# Phase 7: TENSION (Groan Zone)

## Context Intake

Before starting, load these files in full:

| File | What to extract |
|------|----------------|
| `$WORKSPACE/05-john-a.md`, `05-john-b.md`, etc. (all John files) | Full transform outputs |
| `$WORKSPACE/06-build.md` | Enhanced ideas and seed usage report |
| `$WORKSPACE/06.5-hat-eval.md` (if exists) | Hat evaluation insights, invert candidates |
| `$WORKSPACE/05.5-collision-map.md` | Warm zones |
| `$WORKSPACE/01-discover.md` | TRIZ Contradiction Card, root causes |
| `$WORKSPACE/session-state.md` | Open tensions, cohort IDs |

## Output Header

Begin your output file (`$WORKSPACE/07-tension.md`) with:

```
## Upstream References
- `$WORKSPACE/05-john-*.md` — all John outputs (full)
- `$WORKSPACE/06-build.md` — build outputs (full)
- `$WORKSPACE/06.5-hat-eval.md` — hat eval (full, if run)
- `$WORKSPACE/05.5-collision-map.md` — warm zones
- `$WORKSPACE/01-discover.md` — TRIZ card, root causes
- `$WORKSPACE/session-state.md` — open tensions
```

## DB Write Receipt

After `add_batch` (bridge ideas), output as the last line:
```json
{"delta": <N>, "ids": [<bridge_idea_ids>], "updated": []}
```
Then append to `$WORKSPACE/session-state.md`:
```
Phase 7 (TENSION): completed, delta=<N>, ids=[<start>-<end>], upstream=[05-john-*.md, 06-build.md, 01-discover.md]
```

Launch the Tension Analyzer. See `agents/tension-analyzer.md`.

> **Scope:** Hot zones have already been resolved by the Dialectical Ratchet (Phase 5.7).
> The Tension Analyzer focuses on **warm zones** from the Collision Map only.
> Do not re-process hot zone collisions here.

## What It Receives

- All Johns' outputs with temperature zone notes
- Brainwriter's built ideas and cross-zone combinations
- Hat Evaluation Pass results (Phase 6.5) — if run
- Collision Map (`$WORKSPACE/05.5-collision-map.md`) — to identify which tensions are warm (not already resolved)

## What It Produces

1. **3-5 core tensions** — especially cross-zone tensions (FIRE vs ICE are structurally significant)
2. **2-3 Bridge ideas per tension** — ideas that honor both conflicting truths
3. **PMI analysis on top 5-7 ideas** — mining the "Interesting" column for hidden gems
4. **Unspoken trade-offs** — risks embedded in top ideas but not called out
5. **TRIZ trade-off check** — which ideas resolve/pick-side/sidestep the Digger's contradiction
6. **The Deepest Tension** — the single most important contradiction for the Synthesizer

## The Groan Zone Rule

The Groan Zone is uncomfortable. It's where the session feels like it's falling apart — contradictions everywhere, no clear winner. This is correct. Don't rush through it.

The best hybrid ideas come from Bridges that honor BOTH sides of a tension, not from picking a winner.

## Expected Output

- 3-5 tensions with bridges
- 5-7 PMI analyses
- TRIZ trade-off status for each top idea
- 1 named "deepest tension"

Save to `$WORKSPACE/07-tension.md` + add Bridge ideas to DB (phase=tension).

## Key Commands

```bash
# Discover current schema
python scripts/idea_db.py describe <workspace>

# Update TRIZ status on existing ideas (column may already exist from TRANSFORM)
python scripts/idea_db.py add_column <workspace> triz_status --default ""
python scripts/idea_db.py set_batch <workspace> triz-status.json

# Add Bridge ideas as new rows
# The output will print IDs: 75,76,77... — use these for set calls
python scripts/idea_db.py add_batch <workspace> bridge-ideas.json
# JSON format: [{"name":"...","description":"...","source_agent":"Tension Analyzer","chain":"Tension: [X vs Y] → Bridge → ...","tag":"BOLD","phase":"tension"}]

# Check which ideas resolve the core contradiction
python scripts/idea_db.py filter <workspace> triz_status resolves
```

## Anti-Patterns
- **Don't skip Tension Analysis** — the Groan Zone is where the most surprising ideas emerge (warm zones still need bridging)
