"""End-to-end tests for the world state store.

Each test runs the real bin/ tools as subprocesses against a throwaway copy of
the repository, so what is tested is what is actually used.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="world-test-")
        for part in ("bin", "schema", "world"):
            shutil.copytree(os.path.join(REPO, part), os.path.join(self.dir, part))
        shutil.rmtree(os.path.join(self.dir, "bin", "__pycache__"), ignore_errors=True)
        self.addCleanup(shutil.rmtree, self.dir, True)

    # -- helpers ----------------------------------------------------------
    def tool(self, name, stdin=None, args=()):
        return subprocess.run(
            [os.path.join(self.dir, "bin", name), *args],
            input=stdin, capture_output=True, text=True, cwd=self.dir)

    def apply(self, delta):
        return self.tool("apply", stdin=json.dumps(delta))

    def fingerprint(self):
        """Everything that must not move when a delta is refused."""
        out = {}
        for root, _dirs, files in os.walk(os.path.join(self.dir, "world")):
            for fn in sorted(files):
                p = os.path.join(root, fn)
                with open(p, "rb") as fh:
                    out[os.path.relpath(p, self.dir)] = fh.read()
        return out

    def read(self, *parts):
        with open(os.path.join(self.dir, *parts)) as fh:
            return fh.read()

    # -- tests ------------------------------------------------------------
    def test_fixture_is_valid(self):
        r = self.tool("validate")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_rejects_out_of_vocabulary_delta(self):
        before = self.fingerprint()
        r = self.apply({"kind": "innkeeper_becomes_nice", "npc": "tang"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unknown delta kind", r.stderr)
        self.assertIn("Nothing was written.", r.stderr)
        self.assertIn("relationship_shift", r.stderr)  # lists the vocabulary
        self.assertEqual(before, self.fingerprint())

    def test_rejects_known_kind_with_bad_parameters(self):
        r = self.apply({"kind": "npc_stage_change", "npc": "tang",
                        "to_stage": "furious"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("furious", r.stderr)

    def test_rejects_delta_producing_invalid_state(self):
        """Passes its own kind's schema, but the resulting state is invalid."""
        before = self.fingerprint()
        r = self.apply({"kind": "correction", "path": "player.money",
                        "value": -5, "reason": "test"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("resulting state would be invalid", r.stderr)
        self.assertIn("player.json", r.stderr)
        self.assertEqual(before, self.fingerprint())

    def test_rejects_stage_jump_of_more_than_one(self):
        r = self.apply({"kind": "npc_stage_change", "npc": "pei",
                        "to_stage": "shifting"})  # pei is 'resistant'
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("one step", r.stderr)

    def test_allows_stage_backslide(self):
        r = self.apply({"kind": "npc_stage_change", "npc": "tang",
                        "to_stage": "cracked"})  # tang is 'conflicted'
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_rejected_delta_leaves_state_and_log_untouched(self):
        ok = self.apply({"kind": "money_change", "amount": -40,
                         "reason": "a bowl of gruel and a bad decision"})
        self.assertEqual(ok.returncode, 0, ok.stderr)
        before = self.fingerprint()
        log_before = self.read("world", "log.jsonl")

        for bad in (
            {"kind": "nonsense"},
            {"kind": "money_change", "amount": -999999, "reason": "overdraft"},
            {"kind": "relationship_shift", "npc": "nobody", "toward_player": "x"},
            {"kind": "thread_close", "id": "the-green"},          # no resolution
            {"kind": "knowledge_change", "npc": "tang",
             "add_knows": ["about the musk"],
             "add_not_knows": ["about the musk"]},                 # contradiction
            {"kind": "world_amend", "field": "off_the_table",
             "value": ["x"]},                                      # not approved
        ):
            r = self.apply(bad)
            self.assertNotEqual(r.returncode, 0, "should have refused: %r" % bad)
            self.assertIn("Nothing was written.", r.stderr)

        self.assertEqual(before, self.fingerprint())
        self.assertEqual(log_before, self.read("world", "log.jsonl"))

    def test_replay_reproduces_current_state(self):
        deltas = [
            {"kind": "money_change", "amount": -320,
             "reason": "two zhu of musk from Ji Wan"},
            {"kind": "item_change", "op": "acquire",
             "item": "a folded sack from Tang's gate"},
            {"kind": "npc_stage_change", "npc": "pei", "to_stage": "cracked"},
            {"kind": "knowledge_change", "npc": "pei",
             "add_knows": ["that the old physician came back a second time"]},
            {"kind": "observation_record", "target_type": "place",
             "target_id": "geng-house",
             "observation": "The bronze on the gate has not been polished since autumn."},
            {"kind": "thread_open", "id": "the-grey-jars",
             "summary": "Where were the jars made, and who imports them?"},
            {"kind": "thread_close", "id": "the-side-door",
             "resolution": "It was Pei, coming out to bar the gate for the night."},
            {"kind": "skill_promotion", "skill": "sitting with the frightened",
             "level": "skilled", "evidence": "x"},  # wrong param name; refused
            {"kind": "entity_create", "entity": "npc", "body": {
                "id": "dou", "name": "Dou",
                "description": "Guo Lan's shop master. Tailoring bench, West Market.",
                "stage": "resistant", "voice": "Counts aloud while he talks.",
                "knows": [], "not_knows": ["that Guo Lan takes work outside the shop"],
                "toward_player": "Has never met him."}},
            {"kind": "journal_append", "entry": {
                "date": "Day two, evening", "where": "his own stall, lamp unlit",
                "changed": "He took his own history and found nothing.",
                "unresolved": "The green. The aconite. The house."}},
        ]
        baseline = len([l for l in self.read("world", "log.jsonl").splitlines()
                        if l.strip()])
        applied = 0
        for d in deltas:
            r = self.apply(d)
            if r.returncode == 0:
                applied += 1
        self.assertEqual(applied, len(deltas) - 1)  # the malformed one was refused

        log = [json.loads(l) for l in
               self.read("world", "log.jsonl").splitlines() if l.strip()]
        self.assertEqual(len(log), baseline + applied)
        self.assertEqual([e["seq"] for e in log],
                         list(range(1, baseline + applied + 1)))

        r = self.tool("replay")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("replay matches world/", r.stdout)

    def test_replay_detects_tampering_with_state(self):
        r = self.apply({"kind": "money_change", "amount": -100, "reason": "x"})
        self.assertEqual(r.returncode, 0, r.stderr)
        p = os.path.join(self.dir, "world", "player.json")
        with open(p) as fh:
            body = json.load(fh)
        body["money"] = 999          # edited behind the log's back
        with open(p, "w") as fh:
            json.dump(body, fh, indent=2, sort_keys=True)
        r = self.tool("replay")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("does not match world/", r.stderr)

    def test_every_field_has_a_writer(self):
        """A field no delta kind can write can only go stale."""
        import sys
        sys.path.insert(0, os.path.join(REPO, "bin"))
        import _state
        kinds = set(_state.known_kinds())
        for entity in ("world", "player", "npc", "place", "thread", "journal"):
            props = set(_state.load_schema(entity)["properties"])
            covered = set(_state.WRITERS.get(entity, {})) | _state.FIXED.get(entity, set())
            self.assertEqual(props - covered, set(),
                             "%s fields with no writer and not declared fixed" % entity)
            self.assertEqual(covered - props, set(),
                             "%s writer map names fields the schema lacks" % entity)
            for field, writers in _state.WRITERS.get(entity, {}).items():
                for k in writers:
                    self.assertIn(k, kinds, "%s.%s names unknown kind %s" % (entity, field, k))

    def test_npc_update_keeps_last_seen_and_owes_current(self):
        r = self.apply({"kind": "npc_update", "npc": "guo-lan",
                        "last_seen": "the tailors' lane",
                        "add_owes_owed": ["he owes her for a collar band"]})
        self.assertEqual(r.returncode, 0, r.stderr)
        npc = json.loads(self.read("world", "npcs", "guo-lan.json"))
        self.assertEqual(npc["last_seen"], "the tailors' lane")
        self.assertIn("he owes her for a collar band", npc["owes_owed"])

    def test_update_with_nothing_to_update_is_refused(self):
        r = self.apply({"kind": "npc_update", "npc": "guo-lan"})
        self.assertNotEqual(r.returncode, 0)

    def test_closed_thread_cannot_be_rewritten(self):
        r = self.apply({"kind": "thread_update", "id": "guo-lan-cloth-origin",
                        "summary": "something else"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("closed", r.stderr)

    def test_undetermined_wants_needs_player_approval(self):
        r = self.apply({"kind": "player_update", "wants_undetermined": False})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("promise made to the player", r.stderr)

    def test_render_runs(self):
        r = self.tool("render")
        self.assertEqual(r.returncode, 0, r.stderr)
        for expected in ("WORLD", "PLAYER", "THREADS", "NPCS", "PLACES",
                         "does NOT know", "UNDETERMINED"):
            self.assertIn(expected, r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
