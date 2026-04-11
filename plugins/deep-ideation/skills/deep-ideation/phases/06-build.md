# Phase 6: BUILD

## Context Intake

Before starting, load these files in full:

| File | What to extract |
|------|----------------|
| `$WORKSPACE/05-john-a.md`, `05-john-b.md`, etc. (all John files) | Full transform outputs |
| `$WORKSPACE/05.7-ratchet.md` | Ratchet syntheses per hot zone |
| `$WORKSPACE/session-state.md` | Cohort IDs, open tensions |

## Output Header

Begin your output file (`$WORKSPACE/06-build.md`) with:

```
## Upstream References
- `$WORKSPACE/05-john-*.md` — all John outputs (full)
- `$WORKSPACE/05.7-ratchet.md` — ratchet syntheses (full)
- `$WORKSPACE/session-state.md` — cohort IDs, open tensions
```

## DB Write Receipt

After `add_batch`, output as the last line:
```json
{"delta": <N>, "ids": [<id1>, ...], "updated": [<seed_ids_with_usage_updated>]}
```
Then append to `$WORKSPACE/session-state.md`:
```
Phase 6 (BUILD): completed, delta=<N>, ids=[<start>-<end>], upstream=[05-john-*.md, 05.7-ratchet.md]
```

Launch the Brainwriter. See `agents/brainwriter.md`.

## What the Brainwriter Does

1. **Reads all three Johns' complete outputs** including chains and temperature zone compliance
   — and **Ratchet syntheses** from `$WORKSPACE/05.7-ratchet.md` as **pre-resolved ideas**
   (build on them; do not re-debate them)
2. **Generates seed usage report** — classifies every seed as hot/used/cold in the DB
3. **Picks top 10 ideas** — favoring cross-zone diversity and hot seed lineage
4. **Applies 2-3 operations to each** — Combine, Modify, Deepen, TRIZ Transform, Substitute
5. **Creates cross-zone combinations** — FIRE + ICE, PLASMA + FIRE, etc.
6. **Resurrects wild cold seeds** — attempts combinations with hot ideas

## Expected Output

- Seed usage report (hot/used/cold classification)
- 20-30 enhanced ideas with full operation chains
- At least 5 cross-zone combinations explicitly labeled

Save to `$WORKSPACE/06-build.md` + Idea DB (phase=build).

## Key Commands

```bash
# Discover current schema
python scripts/idea_db.py describe <workspace>

# After Brainwriter completes seed usage report:
python scripts/idea_db.py add_column <workspace> seed_usage --default "cold"
python scripts/idea_db.py set_batch <workspace> seed-usage.json

# Add enhanced ideas as new rows — use add_batch for new ideas
# The output will print IDs: 60,61,62... — use these for set calls
python scripts/idea_db.py add_batch <workspace> build-ideas.json
# JSON format: [{"name":"...","description":"...","source_agent":"Brainwriter","source_seed":"12","chain":"John A #12 → COMBINE with John C #8 → ...","tag":"BOLD","phase":"build"}]

# Stats to show user
python scripts/idea_db.py stats <workspace>
python scripts/idea_db.py filter <workspace> seed_usage hot
```

## Description Discipline (Mandatory)

When writing the `description` field for any idea:
- Write a pitch, not a procedure
- If you're writing "Step 1 / Step 2" or "Week 1 / Week 2" — you're in the wrong field
- Put formulas, timelines, and mechanism details in `chain`
- Re-read your description aloud: if it sounds like a spec doc, rewrite it
- No jargon: TAM, CAC, OODA, TRIZ, ICE, and similar terms do not belong in `description`

## Tell the User

"Brainwriter has finished building on the Johns' outputs:
- [N] hot seeds identified (used by 2+ Johns)
- [N] cross-zone combinations created
- [N] total enhanced ideas"
