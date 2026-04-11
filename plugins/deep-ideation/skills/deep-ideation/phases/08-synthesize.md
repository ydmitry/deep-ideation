# Phase 8: SYNTHESIZE

Launch the Synthesizer. See `agents/synthesizer.md`.

The Synthesizer produces hybrids, convergent signals, and the session-derived evaluation criteria (with weights). It does NOT score ideas — Phase 8.5 (SCORE) does that. Keeping the hybrid-author and the ranker separate prevents self-scoring bias.

## Context Intake

Before starting, load these files in full:

| File | What to extract |
|------|----------------|
| `$WORKSPACE/01-discover.md` | Root causes, HMW questions, TRIZ card |
| `$WORKSPACE/05-john-*.md` (all John files) | Full transform outputs and chains |
| `$WORKSPACE/06-build.md` | Enhanced ideas, seed usage report |
| `$WORKSPACE/06.5-hat-eval.md` (if exists) | Hat evaluation, combination suggestions |
| `$WORKSPACE/07-tension.md` | Tensions, bridges, PMI insights |
| `$WORKSPACE/ideas.csv` (via `idea_db.py describe` + `show`) | Current DB state |
| `$WORKSPACE/session-state.md` | Open tensions, cohort IDs from all prior phases |

## Output Header

Begin your output file (`$WORKSPACE/08-synthesize.md`) with:

```
## Upstream References
- `$WORKSPACE/01-discover.md` — root causes, TRIZ card (full)
- `$WORKSPACE/05-john-*.md` — all John outputs (full)
- `$WORKSPACE/06-build.md` — build outputs (full)
- `$WORKSPACE/06.5-hat-eval.md` — hat eval (full, if run)
- `$WORKSPACE/07-tension.md` — tensions and bridges (full)
- DB ideas: #1-#<max> (full schema via describe)
- `$WORKSPACE/session-state.md` — accumulated tensions and cohort IDs
```

## DB Write Receipt

After `add_batch` (hybrid ideas), output as the last line:
```json
{"delta": <N>, "ids": [<hybrid_ids>], "updated": []}
```
Then append to `$WORKSPACE/session-state.md`:
```
Phase 8 (SYNTHESIZE): completed, delta=<N>, ids=[<start>-<end>], upstream=[all prior phases]
```

## What It Receives

All previous phase outputs:
1. Digger root causes + HMW questions + TRIZ trade-off
2. John A, B, C outputs with full chains + temperature zones
3. Brainwriter enhanced ideas + seed usage report
4. Hat Evaluation Pass (if run)
5. Tension Analyzer contradictions + bridges + PMI insights

## What It Produces

1. **Convergent signals** — ideas multiple Johns independently found (cross-zone clusters = highest confidence)
2. **Unique gems** — ideas only one agent found
3. **5-10 hybrids** with full chains from seed to final form
4. **Evaluation criteria and weights** — session-derived, for Phase 8.5 to apply
5. **Web validation** (STANDARD + DEEP) — real-world evidence for 2-3 gut-pick top candidates
6. **Proof search queries** — 3-5 queries per gut-pick top idea with interpretation guide (+ actual findings if WebSearch available)
7. **Session Seed Bank** — top generative seeds for future Historian use
8. **Phased roadmap** — qualitative ordering (no time estimates)

## Session Seed Bank Export

Identify the 10-15 most generative seeds:
```bash
python scripts/idea_db.py filter <workspace> seed_usage hot
python scripts/idea_db.py show <workspace> --columns "id,name,description,source_agent,tag"
```

Save condensed seed bank to `$WORKSPACE/seed-bank.md`.

## Key Commands

```bash
# Discover current schema — check which columns exist from prior phases
python scripts/idea_db.py describe <workspace>

# Add hybrid ideas as new rows
# The output will print IDs: 80,81,82... — use these for set calls
python scripts/idea_db.py add_batch <workspace> hybrid-ideas.json
# JSON format: [{"name":"...","description":"...","source_agent":"Synthesizer","chain":"Hybrid: #12 + #34 → ...","tag":"BOLD","phase":"synthesis"}]

# Register the session's evaluation criteria and composite column (Phase 8.5 will fill them)
python scripts/idea_db.py add_criteria <workspace> \
  --criteria "feasibility,novelty,[session-criteria]" \
  --composite "total_score"
```

## Expected Output

Save to `$WORKSPACE/08-synthesize.md`. Includes the hybrid list, the criteria/weights definition, and proof-search material. The authoritative ranking and Idea Menu are produced by Phase 8.5 (SCORE).

## Anti-Patterns
- **Don't score ideas here.** Phase 8.5 applies the criteria. If you score in the Synthesizer, you reintroduce the self-scoring bias the split exists to prevent.
- **Don't generate 48-hour experiments** — they sound actionable but nobody does them. Generate proof search queries instead. A 10-minute web search produces more validation than a hypothetical experiment design.
