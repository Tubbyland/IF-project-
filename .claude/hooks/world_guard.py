#!/usr/bin/env python3
"""Guard world/ so state changes can only happen through bin/apply.

PreToolUse   - denies Write/Edit/NotebookEdit against world/ state files.
PostToolUse  - runs bin/validate after anything touches world/, and reports
               violations back into Claude's context (exit 2).

world/legacy/ is exempt: it is the frozen markdown kept for reference.
"""
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORLD = os.path.join(REPO, "world")
LEGACY = os.path.join(WORLD, "legacy")

DENY_REASON = """\
world/ is not writable directly. State changes go through the delta vocabulary:

    echo '{"kind": "...", ...}' | bin/apply

bin/apply validates the delta against its kind's schema, validates the resulting
state, and only then writes — and appends it to world/log.jsonl so the change is
auditable and replayable. Writing the file by hand skips all of that.

  bin/render          read current state
  ls schema/deltas/   the delta kinds that exist
  bin/log             what has changed so far

If no delta kind fits what needs recording, say so and propose one rather than
editing the file. (world/legacy/ is exempt — it is frozen reference markdown.)"""


def target_paths(tool_input):
    out = []
    for key in ("file_path", "notebook_path", "path"):
        v = tool_input.get(key)
        if isinstance(v, str) and v:
            out.append(v)
    return out


def is_guarded(path):
    ap = os.path.abspath(os.path.join(REPO, path))
    if not (ap == WORLD or ap.startswith(WORLD + os.sep)):
        return False
    if ap == LEGACY or ap.startswith(LEGACY + os.sep):
        return False
    return True


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never break the session over a malformed payload

    event = payload.get("hook_event_name", "")
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}

    if event == "PreToolUse":
        if tool in ("Write", "Edit", "NotebookEdit"):
            hit = [p for p in target_paths(tool_input) if is_guarded(p)]
            if hit:
                print(json.dumps({"hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": DENY_REASON,
                }}))
        return 0

    if event == "PostToolUse":
        touched = any(is_guarded(p) for p in target_paths(tool_input))
        if tool == "Bash":
            cmd = tool_input.get("command", "")
            touched = touched or "world/" in cmd
        if not touched:
            return 0
        r = subprocess.run([sys.executable, os.path.join(REPO, "bin", "validate")],
                           capture_output=True, text=True, cwd=REPO)
        if r.returncode != 0:
            sys.stderr.write(
                "world/ FAILED VALIDATION after this write.\n"
                + (r.stderr or r.stdout) +
                "\nThe store is now inconsistent. Restore it "
                "(git checkout -- world/) and make the change with bin/apply.\n")
            return 2
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
