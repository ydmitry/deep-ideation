# Phase 8b: HYBRIDIZE

Launch the Synthesizer in full hybrid mode. See `agents/synthesizer.md`.

This is the second half of what was previously Phase 8. It receives the **confirmed** evaluation criteria from `$WORKSPACE/criteria.json` (user-approved in the Criteria Gate checkpoint) and produces all synthesis outputs. It does NOT re-derive criteria — those are already locked.

## What It Receives

All previous phase outputs, plus confirmed criteria:
1. Digger root causes + HMW + TRIZ (`$WORKSPACE/01-discover.md`)
2. John outputs (`$WORKSPACE/05-john-*.md`)
3. Taste Check results (`$WORKSPACE/05.8-taste-check.md`) — if run
4. Brainwriter (`$WORKSPACE/06-build.md`) — if run
5. Hat Eval (`$WORKSPACE/06.5-hat-eval.md`) — if run
6. Tension Analyzer (`$WORKSPACE/07-tension.md`) — if run
7. **`$WORKSPACE/criteria.json`** — confirmed criteria + weights (read this first)
8. `$WORKSPACE/ideas.csv`

## Handling User Favorites

If `$WORKSPACE/05.8-taste-check.md` exists and lists user favorites:

```bash
# Read favorites
python scripts/idea_db.py filter <workspace> user_favorites true
```

When identifying convergent signals and ranking hybrids, apply a **+10% weight boost** to favorites. This is bounded — a favorite that scores poorly on the confirmed criteria can still rank below a non-favorite that scores well.

Do not filter out non-favorites. The boost is additive, not a gate.

## What It Produces

1. **Convergent signals** — ideas multiple Johns independently found (cross-zone clusters = highest confidence)
2. **Unique gems** — ideas only one agent found that deserve attention despite low convergence
3. **5-10 hybrids** — each with full chains from seed → transform → hybrid form, tagged with which criteria they score well on
4. **Web validation** (STANDARD + DEEP) — real-world evidence for 2-3 gut-pick top candidates
5. **Proof search queries** — 3-5 per gut-pick top idea with interpretation guide (+ findings if WebSearch available)
6. **Session Seed Bank** — top 10-15 generative seeds for future Historian use

## Session Seed Bank Export

```bash
python scripts/idea_db.py filter <workspace> seed_usage hot
python scripts/idea_db.py show <workspace> --columns "id,name,description,source_agent,tag"
```

Save to `$WORKSPACE/seed-bank.md`.

## Key Commands

```bash
# Read confirmed criteria
cat $WORKSPACE/criteria.json

# Discover schema — check which columns exist
python scripts/idea_db.py describe <workspace>

# Add hybrid ideas as new rows
python scripts/idea_db.py add_batch <workspace> hybrid-ideas.json
# JSON: [{"name":"...","description":"...","source_agent":"Synthesizer","chain":"Hybrid: #12 + #34 → ...","tag":"BOLD","phase":"synthesis"}]
```

## Expected Output

Save to `$WORKSPACE/08-synthesize.md` (keeping the same output filename for compatibility with downstream phases that reference it). Include the hybrid list, convergent signals, proof-search material, and seed bank summary. The authoritative ranking is produced by Phase 8.5 (SCORE).

## Anti-Patterns

- **Don't re-derive criteria** — they're already confirmed in `criteria.json`; use them as-is
- **Don't score ideas** — Phase 8.5 (SCORE) applies the criteria; Synthesizer generates hybrids
- **Don't generate 48-hour experiments** — generate proof search queries instead
- **Don't hard-filter favorites** — apply the bounded boost, keep all ideas in the pool
