# Phase 6: BUILD

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

## Tell the User

"Brainwriter has finished building on the Johns' outputs:
- [N] hot seeds identified (used by 2+ Johns)
- [N] cross-zone combinations created
- [N] total enhanced ideas"
