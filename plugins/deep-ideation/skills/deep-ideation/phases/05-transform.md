# Phase 5: TRANSFORM (Parallel, Deliberate)

Launch 3 Johns simultaneously. Each reads `agents/john.md` + their seed batch + their temperature zone constraints.

## Launch Instructions

Each John gets:
- Their specific seed batch (from Phase 4)
- Their starting mode: `[STARTING_MODE]`
- Their temperature zone: `[ICE/FIRE/PLASMA]`
- Operations toolkit: `references/operations.md`
- ICE anchors: `$WORKSPACE/ice-anchors.md`
- The TRIZ trade-off question (from Innovator)

## Temperature Zone Recap (HARD CONSTRAINTS)

**John A — FIRE zone (Dreamer-start):**
- Every idea must be pushed one step wilder before advancing
- Output: 70%+ [BOLD] or [WILD]
- Seeds that stay [SAFE] after transformation are rejected

**John B — PLASMA zone (Realist-start):**
- Every idea must reference a mechanism from a different domain
- Output: 50%+ ideas with explicit cross-domain mechanisms
- Ideas without an external mechanism reference are rejected

**John C — ICE zone (Critic-start):**
- Every idea must pass "could we try this next week?"
- Output: 70%+ [SAFE]
- Ideas scoring below 5/10 on weekly feasibility are inverted, not advanced

## Disney Spiral

Each John does three rotations on their seeds:

```
Mode 1 (starting mode) → pick top 3-5 → Mode 2 → pick top 2-3 → Mode 3 → Final Top 5
```

Full operation chains documented. Every idea traces back to its original seed.

## Expected Output

| Agent | Min Ideas | Max Ideas |
|-------|-----------|-----------|
| John A (FIRE) | 10 | 15 |
| John B (PLASMA) | 10 | 15 |
| John C (ICE) | 10 | 15 |
| **Total** | **30** | **45** |

Each John saves to:
- `$WORKSPACE/05-john-[a/b/c].md` — full output with chains
- Idea DB: `phase=transform, temperature_zone=[ICE/FIRE/PLASMA]`

## TRIZ Trade-Off Engagement

Each John should explicitly answer the trade-off question from the Innovator:
> "Does your best transformed idea RESOLVE the contradiction [X vs Y], PICK A SIDE, or SIDESTEP it?"

Record in the DB: `triz_status = resolves / picks_side / sidesteps`

## While Running

Tell the user: "Three Johns are transforming seeds in parallel using Disney spirals (temperature zones: FIRE/PLASMA/ICE). Expected: 30-45 transformed ideas."

## Anti-Patterns
- Don't let Johns generate from scratch — every idea must trace to a seed
- Don't ignore the temperature zone constraint — it's what produces structural divergence
- Don't compress the chain — full chain documentation is required for Brainwriter + Synthesizer
