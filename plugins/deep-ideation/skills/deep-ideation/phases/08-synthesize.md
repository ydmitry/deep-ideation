# Phase 8: SYNTHESIZE

Launch the Synthesizer. See `agents/synthesizer.md`.

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
4. **ICE anchor calibration** — for this session's specific root causes
5. **Scoring** — all ideas scored on session-derived criteria
6. **Idea Menu** — Quick Wins / Core Bets / Moonshots
7. **Web validation** (STANDARD + DEEP) — real-world evidence for top ideas
8. **Proof search queries** — 3-5 queries per top idea with interpretation guide (+ actual findings if WebSearch available)
9. **Session Seed Bank** — top generative seeds for future Historian use
10. **Phased roadmap**

## Idea Menu Structure

### Quick Wins
> Ease ≥7 AND Confidence ≥6
> These are the safe, fast, high-confidence moves. Do these first.

### Core Bets
> Impact ≥8 AND Confidence ≥5
> The main strategic plays. These might take time but are worth committing to.

### Moonshots
> Impact ≥9 AND Novelty ≥8 (confidence may be lower)
> Long shots worth validating with proof searches. Don't commit without evidence.

## Session Seed Bank Export

After scoring, identify the 10-15 most generative seeds:
```bash
python scripts/idea_db.py filter <workspace> seed_usage hot
python scripts/idea_db.py show <workspace> --columns "id,name,description,source_agent,tag"
```

Save condensed seed bank to `$WORKSPACE/seed-bank.md`.

## Key Commands

```bash
# Score all ideas
python scripts/idea_db.py set_batch <workspace> scores.json

# Compute composite
python scripts/idea_db.py compute <workspace> \
  --criteria "feasibility,novelty,[session-criteria]" \
  --target "total_score" \
  --formula weighted_avg

# Build Idea Menu
python scripts/idea_db.py multi_filter <workspace> --conditions "ease>=7,confidence>=6"
python scripts/idea_db.py multi_filter <workspace> --conditions "impact>=8,confidence>=5"
python scripts/idea_db.py multi_filter <workspace> --conditions "impact>=9,novelty>=8"

# Export full table
python scripts/idea_db.py export_md <workspace> \
  --columns "id,name,source_agent,temperature_zone,triz_status,ice_score,total_score" \
  --sort total_score --desc
```

## Expected Output

Save to `$WORKSPACE/08-synthesize.md`. This is the primary deliverable.

The Idea Menu is the most action-oriented output — format it clearly for the user.

## Anti-Patterns
- **Don't generate 48-hour experiments** — they sound actionable but nobody does them. Generate proof search queries instead. A 10-minute web search produces more validation than a hypothetical experiment design.
