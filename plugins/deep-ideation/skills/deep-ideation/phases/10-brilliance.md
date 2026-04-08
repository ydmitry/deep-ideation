# Phase 10: BRILLIANCE FILTER

Launch the Brilliance Filter. See `agents/brilliance.md`.

## When to Run

After Phase 8 (SYNTHESIZE) produces the Idea Menu. Runs in ALL modes.

Brilliance runs BEFORE CONVERGE so it informs the decision tree — the user should know which ideas are structurally brilliant before choosing what to pursue.

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

## Writing to the Idea Database

```bash
# Discover current schema
python scripts/idea_db.py describe <workspace>

# Add brilliance columns
python scripts/idea_db.py add_column <workspace> brilliance_tier --default ""
python scripts/idea_db.py add_column <workspace> brilliance_pitch --default ""

# Set tier and pitch for each evaluated idea using its existing ID
python scripts/idea_db.py set <workspace> <id> brilliance_tier "brilliant"
python scripts/idea_db.py set <workspace> <id> brilliance_pitch "One-sentence pitch here"
# Valid tiers: "brilliant", "notable", "" (not evaluated)
```

## Output Location

Appended to `$WORKSPACE/08-synthesize.md` as the final section before CONVERGE. The Brilliant Ideas section should leave the user with the clearest, sharpest ideas from the session — right before they decide what to pursue.

## Anti-Patterns
- **Don't skip the Brilliance Filter** — it's the last thing the user reads and often surfaces the session's best insight
- **Don't inflate brilliance** — zero Brilliant ideas is a valid output. If nothing is structurally surprising, say so.
