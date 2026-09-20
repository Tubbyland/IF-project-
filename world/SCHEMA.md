# World State — Schema

Six kinds of file. Keep them short. A file long enough to skim past is a file
that stops being read.

```
world/
  world.md          setting, tone, what can exist, off-limits content
  player.md         who they are, what they carry, what they can do
  threads.md        what's unresolved
  journal.md        append-only log of sessions
  npcs/<name>.md    one per significant NPC
  places/<name>.md  one per location with persistent state
```

---

## world.md
Written once in session zero, edited rarely. Holds the rules of reality:
setting, era, tone, whether magic or the supernatural exists and what it costs,
and the player's content limits. Everything here is binding. If a later scene
needs it changed, ask the player first.

## player.md
Name, situation, what they want, what they're bad at. Inventory and money as a
plain list. Skills as `name: level — evidence`, where level is one of
`unpracticed / capable / skilled / expert` and evidence is the moment that
earned the last promotion. Reputation as one line per place or faction that
knows them.

## npcs/<name>.md
The load-bearing file. Format:

```
# Torres
Harbourmaster, Kildonan. Late fifties, missing two fingers on the left hand.

stage: cracked
voice: clipped sentences; never says a name twice in one conversation

knows: Sam is looking for the Arden; does NOT know Sam is armed
owes/owed: owes Sam 40 silver
toward Sam: resentful, will not refuse openly
last seen: the customs house, after the fire
```

`knows` is the one to get right — what an NPC knows and doesn't is most of what
makes them feel real. Write the negatives explicitly.

## places/<name>.md
Only for places whose state persists: what's changed, what's hidden there, who
controls it now. Scenery doesn't need a file.

## threads.md
One line each, under `open` or `closed`. A thread is something the player has
reason to expect a resolution to. Closed threads stay in the file — they're the
record of what was actually finished.

## journal.md
Append-only. Five lines per session: when, where the player ended up, what
changed, what's unresolved, and anything you promised that hasn't paid off yet.
Never rewrite past entries.

---

## What doesn't go in these files

Plot you've invented but the player hasn't met. Descriptions. Dialogue.
Anything you'd be content to improvise differently next session. The files exist
to stop the world contradicting itself, not to pre-write it.
