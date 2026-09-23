# Interactive fiction — typed world state

A persistent single-player interactive fiction game. Claude narrates; the world
lives in `world/` as validated JSON. `CLAUDE.md` holds the game rules.

## Why the store is typed

Claude both narrates the story and records it. Nothing stopped it from
contradicting state it had written itself — a stage that jumped two steps, a
purse that drifted, an edit nobody could audit. So writes are constrained:

- `world/` is **JSON validated against `schema/`**, not prose.
- Changes may only be made as **deltas** drawn from a closed vocabulary
  (`schema/deltas/`). A change outside it is invalid, not merely unusual.
- Every applied delta is appended to `world/log.jsonl` with a content hash and
  the hash of the resulting state.
- A **PreToolUse hook denies direct writes to `world/`**, so the rule is
  enforced rather than remembered.

What this does *not* fix: nothing here checks that Claude's narration matches
the store. Only reading before narrating does that.

## Tools

    bin/render [section]   read state as text (world|player|threads|npcs|places|journal)
    bin/validate           check world/ against the schemas; non-zero on violations
    bin/apply              apply one delta, read as JSON on stdin
    bin/log [-v]           the event log, newest last
    bin/replay             rebuild from world/genesis + log, compare with world/

Apply a change:

    echo '{"kind": "money_change", "amount": -320,
           "reason": "two zhu of musk from Ji Wan"}' | bin/apply

`bin/apply` validates the delta, applies it to a copy of the state, validates
the whole result, and only then commits. On any failure it explains and writes
nothing.

## Layout

    CLAUDE.md          game rules; section 3 is the state protocol
    schema/            one JSON Schema per entity type
    schema/deltas/     one schema per delta kind — the whole vocabulary
    bin/               the tools above; bin/_state.py is the shared library
    world/             current state
    world/genesis/     the snapshot replay starts from
    world/log.jsonl    append-only event log
    world/legacy/      the original markdown, frozen for reference
    tests/             end-to-end tests over the real bin/ tools

## Setup

    pip install -r requirements.txt
    python3 -m unittest discover -s tests
