# Phase 10: BRILLIANCE FILTER

Launch the Brilliance Filter. See `agents/brilliance.md`.

## When to Run

After Phase 9 (CONVERGE) or after Phase 8 (SYNTHESIZE) in LITE mode. Runs in ALL modes.

This is the final output step — it appends the Brilliant Ideas section to the session deliverable.

## What It Receives

- Full Idea Menu from `$WORKSPACE/08-synthesize.md`
- All scored ideas from `$WORKSPACE/ideas.csv`
- Tension analysis from `$WORKSPACE/07-tension.md` (if it exists — checks which ideas resolve real contradictions)
- Digger's root causes from `$WORKSPACE/01-discover.md`

## What It Produces

A `## Brilliance Scorecard` and `## Brilliant Ideas` section appended to `$WORKSPACE/08-synthesize.md`.

## Key Distinction

This is a qualitative judgment pass, not another scoring round.

| ICE Captures | Brilliance Captures |
|---|---|
| Impact (how much it helps) | Structural elegance (one mechanism, many problems) |
| Confidence (evidence it works) | Surprise (obvious in hindsight) |
| Ease (how hard to implement) | Inevitability (aligned with structural trends) |
| — | Compounding value (gets better over time) |
| — | Dialectical depth (resolves a real tension) |

ICE rewards the best ideas within the expected solution space. Brilliance finds the ideas that reframe the space.

## Output Location

Appended to `$WORKSPACE/08-synthesize.md` as the final section. The Brilliant Ideas section is the last thing the user reads.
