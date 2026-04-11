# Phase 8: SYNTHESIZE

Launch the Synthesizer. See `agents/synthesizer.md`.

The Synthesizer produces hybrids, convergent signals, and the session-derived evaluation criteria (with weights). It does NOT score ideas — Phase 8.5 (SCORE) does that. Keeping the hybrid-author and the ranker separate prevents self-scoring bias.

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
# Standard run:
python scripts/idea_db.py add_criteria <workspace> \
  --criteria "feasibility,novelty,[session-criteria]" \
  --composite "total_score"

# Corporate / strategic run — always include economics dimensions:
python scripts/idea_db.py add_criteria <workspace> \
  --criteria "feasibility,novelty,segment_viability,pricing_fit,[session-criteria]" \
  --composite "total_score"
```

## Strategic Runs: Economics Criteria

If the run scope is `corporate` or `strategic` (check `$WORKSPACE/02-orchestrate.md`), the Synthesizer **must** include `segment_viability` and `pricing_fit` as explicit evaluation criteria, in addition to the session-derived criteria.

**`segment_viability`** — How well does this idea serve a clearly defined, reachable buyer segment? Does it bet on a segment the team can actually access?

**`pricing_fit`** — Is the implied pricing model coherent with the product mechanics and the buyer's willingness to pay? Does the revenue model hold under realistic take-rates?

For strategic runs, the Synthesizer must also add a **Go-to-Market Summary** section to `$WORKSPACE/08-synthesize.md`:

```
## Go-to-Market Summary (Strategic Run)

For each hybrid and top candidate, summarize:
- **Segment:** [Which buyer segment this idea targets]
- **Pricing model:** [What pricing structure this implies]
- **Sales motion:** [How this reaches buyers — PLG, SLG, channel, viral]
- **Key GTM risk:** [The one thing that could kill adoption before product-market fit]
```

Populate this from the `segment_shift`, `pricing_shift`, `revenue_model`, and `unit_economics_note` columns already filled by the Market Analyst and other specialists in SEED phase.

## Expected Output

Save to `$WORKSPACE/08-synthesize.md`. Includes the hybrid list, the criteria/weights definition, and proof-search material. The authoritative ranking and Idea Menu are produced by Phase 8.5 (SCORE).

## Anti-Patterns
- **Don't score ideas here.** Phase 8.5 applies the criteria. If you score in the Synthesizer, you reintroduce the self-scoring bias the split exists to prevent.
- **Don't generate 48-hour experiments** — they sound actionable but nobody does them. Generate proof search queries instead. A 10-minute web search produces more validation than a hypothetical experiment design.
