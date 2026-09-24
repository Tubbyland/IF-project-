"""Shared state machinery for the world/ store.

The store is a directory of JSON files. Every change goes through apply_delta,
which is pure: it takes a state dict and a delta and returns a new state dict.
Nothing here writes to disk except commit().
"""
import copy
import hashlib
import json
import os
import sys

try:
    import jsonschema
except ImportError:  # pragma: no cover - environment problem, not a state problem
    sys.stderr.write(
        "jsonschema is not installed. Run: pip install -r requirements.txt\n")
    raise SystemExit(2)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD = os.path.join(ROOT, "world")
GENESIS = os.path.join(WORLD, "genesis")
SCHEMA = os.path.join(ROOT, "schema")
LOG = os.path.join(WORLD, "log.jsonl")

COLLECTIONS = {"npcs": "npc", "places": "place", "threads": "thread"}
SINGLETONS = {"world": "world", "player": "player", "journal": "journal"}

STAGES = ["resistant", "cracked", "conflicted", "shifting", "changed"]
LEVELS = ["unpracticed", "capable", "skilled", "expert"]


class DeltaError(Exception):
    """A delta that cannot be applied. Carries a message meant to be read."""


# ---------------------------------------------------------------- schemas

def load_schema(name):
    with open(os.path.join(SCHEMA, name + ".schema.json")) as f:
        return json.load(f)


def load_delta_schema(kind):
    path = os.path.join(SCHEMA, "deltas", kind + ".schema.json")
    if not os.path.exists(path):
        raise DeltaError(
            "unknown delta kind %r.\nThe vocabulary is closed. Known kinds:\n  %s"
            % (kind, "\n  ".join(known_kinds())))
    with open(path) as f:
        return json.load(f)


def known_kinds():
    d = os.path.join(SCHEMA, "deltas")
    return sorted(f[:-len(".schema.json")] for f in os.listdir(d)
                  if f.endswith(".schema.json"))


# ---------------------------------------------------------------- load/save

def _read(path):
    with open(path) as f:
        return json.load(f)


def load_state(base=WORLD):
    state = {}
    for name in SINGLETONS:
        path = os.path.join(base, name + ".json")
        state[name] = _read(path) if os.path.exists(path) else None
    for coll in COLLECTIONS:
        state[coll] = {}
        d = os.path.join(base, coll)
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                if fn.endswith(".json"):
                    state[coll][fn[:-5]] = _read(os.path.join(d, fn))
    return state


def _write_atomic(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def save_state(state, base=WORLD):
    """Write the whole state out. Used for genesis snapshots and by commit()."""
    for name in SINGLETONS:
        if state.get(name) is not None:
            _write_atomic(os.path.join(base, name + ".json"), state[name])
    for coll in COLLECTIONS:
        d = os.path.join(base, coll)
        os.makedirs(d, exist_ok=True)
        wanted = set(state.get(coll, {}))
        for fn in os.listdir(d):
            if fn.endswith(".json") and fn[:-5] not in wanted:
                os.remove(os.path.join(d, fn))
        for eid, body in state.get(coll, {}).items():
            _write_atomic(os.path.join(d, eid + ".json"), body)


# ---------------------------------------------------------------- hashing

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def sha(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def state_hash(state):
    return sha(state)


# ---------------------------------------------------------------- validation

def _schema_errors(obj, schema, label):
    v = jsonschema.Draft202012Validator(schema)
    out = []
    for e in sorted(v.iter_errors(obj), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in e.path) or "(root)"
        out.append("%s: %s: %s" % (label, loc, e.message))
    return out


def validate_state(state):
    """Return a list of readable violations. Empty list means valid."""
    errors = []
    for name, schema_name in SINGLETONS.items():
        body = state.get(name)
        if body is None:
            errors.append("%s.json: missing" % name)
            continue
        errors += _schema_errors(body, load_schema(schema_name), name + ".json")
    for coll, schema_name in COLLECTIONS.items():
        schema = load_schema(schema_name)
        for eid, body in sorted(state.get(coll, {}).items()):
            label = "%s/%s.json" % (coll, eid)
            errors += _schema_errors(body, schema, label)
            if body.get("id") != eid:
                errors.append("%s: id %r does not match filename %r"
                              % (label, body.get("id"), eid))

    # cross-entity rules the schemas cannot express
    for tid, t in sorted(state.get("threads", {}).items()):
        if t.get("state") == "closed" and not t.get("resolution"):
            errors.append("threads/%s.json: closed thread has no resolution" % tid)
    player = state.get("player") or {}
    seen = set()
    for s in player.get("skills", []):
        n = s.get("name")
        if n in seen:
            errors.append("player.json: duplicate skill %r" % n)
        seen.add(n)
    return errors


# ---------------------------------------------------------------- paths

def get_path(state, path):
    cur = state
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise DeltaError("path %r does not exist (stopped at %r)" % (path, part))
        cur = cur[part]
    return cur


def set_path(state, path, value):
    parts = path.split(".")
    cur = state
    for part in parts[:-1]:
        if not isinstance(cur, dict) or part not in cur:
            raise DeltaError("path %r does not exist (stopped at %r)" % (path, part))
        cur = cur[part]
    if not isinstance(cur, dict) or parts[-1] not in cur:
        raise DeltaError("path %r does not exist (no key %r)" % (path, parts[-1]))
    cur[parts[-1]] = value


def _require(state, coll, eid):
    if eid not in state.get(coll, {}):
        raise DeltaError("no %s with id %r. Known: %s"
                         % (coll[:-1], eid,
                            ", ".join(sorted(state.get(coll, {}))) or "(none)"))
    return state[coll][eid]


def _append_unique(lst, value):
    if value not in lst:
        lst.append(value)


# ---------------------------------------------------------------- appliers

def _a_relationship_shift(st, d):
    _require(st, "npcs", d["npc"])["toward_player"] = d["toward_player"]


def _a_money_change(st, d):
    new = st["player"]["money"] + d["amount"]
    if new < 0:
        raise DeltaError("money would go to %d; the player has %d"
                         % (new, st["player"]["money"]))
    st["player"]["money"] = new


def _a_item_change(st, d):
    carrying = st["player"].setdefault("carrying", [])
    if d["op"] == "acquire":
        _append_unique(carrying, d["item"])
    else:
        if d["item"] not in carrying:
            raise DeltaError("the player is not carrying %r" % d["item"])
        carrying.remove(d["item"])


def _a_promise(st, d):
    npc = _require(st, "npcs", d["npc"])
    promises = npc.setdefault("promises", [])
    for p in promises:
        if p["what"] == d["what"]:
            p["state"] = d["op"]
            if "by" in d:
                p["by"] = d["by"]
            return
    if d["op"] != "made":
        raise DeltaError("no promise %r on %s to mark %s"
                         % (d["what"], d["npc"], d["op"]))
    entry = {"what": d["what"], "state": "made"}
    if "by" in d:
        entry["by"] = d["by"]
    promises.append(entry)


def _a_place_change(st, d):
    place = _require(st, "places", d["place"])
    _append_unique(place.setdefault("changed", []), d["changed"])


def _a_thread_open(st, d):
    if d["id"] in st["threads"]:
        raise DeltaError("thread %r already exists" % d["id"])
    st["threads"][d["id"]] = {"id": d["id"], "summary": d["summary"],
                              "state": "open"}


def _a_thread_close(st, d):
    t = _require(st, "threads", d["id"])
    if t["state"] == "closed":
        raise DeltaError("thread %r is already closed" % d["id"])
    t["state"] = "closed"
    t["resolution"] = d["resolution"]


def _a_skill_promotion(st, d):
    skills = st["player"].setdefault("skills", [])
    target = d["to_level"]
    for s in skills:
        if s["name"] == d["skill"]:
            gap = LEVELS.index(target) - LEVELS.index(s["level"])
            if gap != 1:
                raise DeltaError(
                    "%r is %s; promotion must be exactly one level (next is %s), "
                    "got %s" % (d["skill"], s["level"],
                                LEVELS[LEVELS.index(s["level"]) + 1]
                                if s["level"] != LEVELS[-1] else "(none)", target))
            s["level"] = target
            s["evidence"] = d["evidence"]
            return
    if target != "unpracticed":
        raise DeltaError(
            "no skill %r. A new skill enters at 'unpracticed'; got %r"
            % (d["skill"], target))
    skills.append({"name": d["skill"], "level": target,
                   "evidence": d["evidence"]})


def _a_npc_stage_change(st, d):
    npc = _require(st, "npcs", d["npc"])
    gap = STAGES.index(d["to_stage"]) - STAGES.index(npc["stage"])
    if abs(gap) != 1:
        raise DeltaError(
            "%s is %r; a stage change moves one step in either direction, "
            "not %r. One scene moves an NPC at most one stage."
            % (d["npc"], npc["stage"], d["to_stage"]))
    npc["stage"] = d["to_stage"]


def _a_entity_create(st, d):
    coll = {"npc": "npcs", "place": "places", "thread": "threads"}[d["entity"]]
    body = d["body"]
    eid = body.get("id")
    if not eid:
        raise DeltaError("body has no id")
    if eid in st[coll]:
        raise DeltaError("%s %r already exists" % (d["entity"], eid))
    errs = _schema_errors(body, load_schema(d["entity"]), "body")
    if errs:
        raise DeltaError("body does not match the %s schema:\n  %s"
                         % (d["entity"], "\n  ".join(errs)))
    st[coll][eid] = body


def _a_knowledge_change(st, d):
    npc = _require(st, "npcs", d["npc"])
    for field, add, rem in (("knows", "add_knows", "remove_knows"),
                            ("not_knows", "add_not_knows", "remove_not_knows")):
        lst = npc.setdefault(field, [])
        for item in d.get(add, []):
            _append_unique(lst, item)
        for item in d.get(rem, []):
            if item not in lst:
                raise DeltaError("%s has no %s entry %r" % (d["npc"], field, item))
            lst.remove(item)
    overlap = set(npc.get("knows", [])) & set(npc.get("not_knows", []))
    if overlap:
        raise DeltaError("%s would both know and not know: %s"
                         % (d["npc"], ", ".join(sorted(overlap))))


def _a_observation_record(st, d):
    t = d["target_type"]
    if t == "player":
        target = st["player"]
    else:
        if "target_id" not in d:
            raise DeltaError("target_type %r needs a target_id" % t)
        target = _require(st, t + "s", d["target_id"])
    _append_unique(target.setdefault("observed_not_explained", []),
                   d["observation"])


def _a_journal_append(st, d):
    st["journal"].setdefault("entries", []).append(d["entry"])


BINDING_WORLD_FIELDS = {"what_can_exist", "off_the_table"}


def _a_world_amend(st, d):
    if d["field"] in BINDING_WORLD_FIELDS and not d.get("player_approved"):
        raise DeltaError(
            "%r is binding. CLAUDE.md: if a later scene needs it changed, ask the "
            "player first. Set player_approved true only after they have said so."
            % d["field"])
    st["world"][d["field"]] = d["value"]


def _edit_list(lst, add, remove, label):
    for item in add or []:
        _append_unique(lst, item)
    for item in remove or []:
        if item not in lst:
            raise DeltaError("%s has no entry %r" % (label, item))
        lst.remove(item)


def _a_npc_update(st, d):
    npc = _require(st, "npcs", d["npc"])
    for f in ("last_seen", "description", "voice"):
        if f in d:
            npc[f] = d[f]
    _edit_list(npc.setdefault("owes_owed", []), d.get("add_owes_owed"),
               d.get("remove_owes_owed"), "%s owes_owed" % d["npc"])


def _a_place_update(st, d):
    place = _require(st, "places", d["place"])
    for f in ("controlled_by", "description"):
        if f in d:
            place[f] = d[f]
    _edit_list(place.setdefault("hidden", []), d.get("add_hidden"),
               d.get("remove_hidden"), "%s hidden" % d["place"])


def _a_thread_update(st, d):
    t = _require(st, "threads", d["id"])
    if t["state"] == "closed":
        raise DeltaError("thread %r is closed. Closed threads are the record of what "
                         "was finished and are not rewritten." % d["id"])
    t["summary"] = d["summary"]


def _a_player_update(st, d):
    p = st["player"]
    if "wants_undetermined" in d and d["wants_undetermined"] != p["wants"]["undetermined"]:
        if not d.get("player_approved"):
            raise DeltaError(
                "wants.undetermined was a promise made to the player in session zero. "
                "Change it only after the player has said so, with player_approved true.")
        p["wants"]["undetermined"] = d["wants_undetermined"]
    if "wants_text" in d:
        p["wants"]["text"] = d["wants_text"]
    for f in ("situation", "bad_at", "money_note"):
        if f in d:
            p[f] = d[f]
    _edit_list(p.setdefault("known_by", []), d.get("add_known_by"),
               d.get("remove_known_by"), "player known_by")


def _a_correction(st, d):
    set_path(st, d["path"], d["value"])


APPLIERS = {
    "relationship_shift": _a_relationship_shift,
    "money_change": _a_money_change,
    "item_change": _a_item_change,
    "promise": _a_promise,
    "place_change": _a_place_change,
    "thread_open": _a_thread_open,
    "thread_close": _a_thread_close,
    "skill_promotion": _a_skill_promotion,
    "npc_stage_change": _a_npc_stage_change,
    "entity_create": _a_entity_create,
    "knowledge_change": _a_knowledge_change,
    "observation_record": _a_observation_record,
    "journal_append": _a_journal_append,
    "world_amend": _a_world_amend,
    "correction": _a_correction,
    "npc_update": _a_npc_update,
    "place_update": _a_place_update,
    "thread_update": _a_thread_update,
    "player_update": _a_player_update,
}

# Every field of every entity must be writable by some delta kind, or be declared
# fixed. A field nothing can write is a field that can only go stale.
# `correction` is deliberately not counted: it is for errors, not for keeping current.
WRITERS = {
    "world":  {f: ["world_amend"] for f in (
        "setting", "era", "scale", "tone", "what_can_exist", "established_frame",
        "off_the_table", "play_style")},
    "player": {"situation": ["player_update"], "bad_at": ["player_update"],
               "money_note": ["player_update"], "wants": ["player_update"],
               "known_by": ["player_update"], "money": ["money_change"],
               "carrying": ["item_change"], "skills": ["skill_promotion"],
               "observed_not_explained": ["observation_record"]},
    "npc":    {"stage": ["npc_stage_change"], "knows": ["knowledge_change"],
               "not_knows": ["knowledge_change"], "toward_player": ["relationship_shift"],
               "promises": ["promise"], "observed_not_explained": ["observation_record"],
               "last_seen": ["npc_update"], "owes_owed": ["npc_update"],
               "description": ["npc_update"], "voice": ["npc_update"]},
    "place":  {"changed": ["place_change"], "observed_not_explained": ["observation_record"],
               "controlled_by": ["place_update"], "description": ["place_update"],
               "hidden": ["place_update"]},
    "thread": {"summary": ["thread_update"], "state": ["thread_close"],
               "resolution": ["thread_close"]},
    "journal": {"entries": ["journal_append"]},
}
FIXED = {"player": {"name"}, "npc": {"id", "name"}, "place": {"id", "name"},
         "thread": {"id"}}


def apply_delta(state, delta):
    """Pure. Returns a new state. Raises DeltaError with a readable message."""
    if not isinstance(delta, dict):
        raise DeltaError("a delta must be a JSON object")
    kind = delta.get("kind")
    if not kind:
        raise DeltaError("a delta must have a 'kind'. Known kinds:\n  %s"
                         % "\n  ".join(known_kinds()))
    schema = load_delta_schema(kind)
    errs = _schema_errors(delta, schema, kind)
    if errs:
        raise DeltaError("delta does not match the %s schema:\n  %s"
                         % (kind, "\n  ".join(errs)))
    if kind not in APPLIERS:
        raise DeltaError("no applier for kind %r" % kind)
    new = copy.deepcopy(state)
    APPLIERS[kind](new, delta)
    return new


# ---------------------------------------------------------------- log

def read_log():
    if not os.path.exists(LOG):
        return []
    entries = []
    with open(LOG) as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise DeltaError("log line %d is not valid JSON: %s" % (n, e))
    return entries


def commit(new_state, delta, log_entries):
    """Write state and append to the log, or leave everything as it was."""
    touched = []
    for name in SINGLETONS:
        touched.append(os.path.join(WORLD, name + ".json"))
    for coll in COLLECTIONS:
        d = os.path.join(WORLD, coll)
        if os.path.isdir(d):
            touched += [os.path.join(d, f) for f in os.listdir(d)
                        if f.endswith(".json")]
        for eid in new_state.get(coll, {}):
            touched.append(os.path.join(d, eid + ".json"))
    backup = {}
    for p in set(touched):
        backup[p] = open(p, "rb").read() if os.path.exists(p) else None

    entry = {
        "seq": len(log_entries) + 1,
        "kind": delta["kind"],
        "delta": delta,
        "delta_hash": sha(delta),
        "state_hash": state_hash(new_state),
    }
    log_backup = open(LOG, "rb").read() if os.path.exists(LOG) else None
    try:
        save_state(new_state)
        with open(LOG, "a") as f:
            f.write(canonical(entry) + "\n")
    except Exception:
        for p, data in backup.items():
            if data is None:
                if os.path.exists(p):
                    os.remove(p)
            else:
                with open(p, "wb") as f:
                    f.write(data)
        if log_backup is None:
            if os.path.exists(LOG):
                os.remove(LOG)
        else:
            with open(LOG, "wb") as f:
                f.write(log_backup)
        raise
    return entry
