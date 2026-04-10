# Phase 10: BRILLIANCE FILTER

Launch the Brilliance Filter. See `agents/brilliance.md`.

## When to Run

After Phase 8.5 (SCORE) produces the ranked Idea Menu, and after Phase 9.5 (STRESS-TEST) if it ran. Runs in ALL modes.

Brilliance runs BEFORE CONVERGE so it informs the decision tree — the user should know which ideas are structurally brilliant before choosing what to pursue.

## What It Receives

- Ranked Idea Menu from `$WORKSPACE/08.5-score.md`
- Synthesizer's hybrids and convergent signals from `$WORKSPACE/08-synthesize.md`
- All scored ideas from `$WORKSPACE/ideas.csv`
- Tension analysis from `$WORKSPACE/07-tension.md` (if it exists — checks which ideas resolve real contradictions)
- Digger's root causes from `$WORKSPACE/01-discover.md`

## What It Produces

A `## Brilliance Scorecard` and `## Brilliant Ideas` section appended to `$WORKSPACE/08.5-score.md`.

## Key Distinction

This is a qualitative judgment pass, not another scoring round.

| `total_score` Captures | Brilliance Captures |
|---|---|
| Session-derived criteria (feasibility, novelty, root-cause fit) | Structural elegance (one mechanism, many problems) |
| Weighted rank within the expected solution space | Surprise (obvious in hindsight) |
| — | Inevitability (aligned with structural trends) |
| — | Compounding value (gets better over time) |
| — | Dialectical depth (resolves a real tension) |

`total_score` rewards the best ideas within the expected solution space. Brilliance finds the ideas that reframe the space.

## Selecting Ideas to Evaluate

```bash
# Discover current schema
python scripts/idea_db.py describe <workspace>

# Evaluate top-ranked ideas from the Scorer
python scripts/idea_db.py top <workspace> total_score --n 20
# Focus on the top-scored ideas — typically 10-15 make it to this phase
```

Use the IDs from this output for all brilliance evaluations below.

## Writing to the Idea Database

```bash

# Add brilliance columns
python scripts/idea_db.py add_column <workspace> brilliance_tier --default ""
python scripts/idea_db.py add_column <workspace> brilliance_pitch --default ""

# Set tier and pitch for each evaluated idea using its existing ID
python scripts/idea_db.py set <workspace> <id> brilliance_tier "brilliant"
python scripts/idea_db.py set <workspace> <id> brilliance_pitch "One-sentence pitch here"
# Valid tiers: "brilliant", "notable", "" (not evaluated)
```

## Output Location

Appended to `$WORKSPACE/08.5-score.md` as the final section before CONVERGE. The Brilliant Ideas section should leave the user with the clearest, sharpest ideas from the session — right before they decide what to pursue.

## Anti-Patterns
- **Don't skip the Brilliance Filter** — it's the last thing the user reads and often surfaces the session's best insight
- **Don't inflate brilliance** — zero Brilliant ideas is a valid output. If nothing is structurally surprising, say so.
