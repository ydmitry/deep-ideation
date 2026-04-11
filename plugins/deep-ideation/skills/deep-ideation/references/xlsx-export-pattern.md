# xlsx Export Pattern — Ideation Scorecard

This document describes how to hand off a completed deep-ideation session to the `anthropic-skills:xlsx` skill as a re-weightable scorecard spreadsheet.

## When to Use

After Phase 9 (CONVERGE) the user has a ranked Idea Menu in `$WORKSPACE/ideas.csv`. This export produces a live spreadsheet where the user can adjust criterion weights and see scores recalculate — without re-running the session.

## Source Artifact

`$WORKSPACE/ideas.csv` — the idea database written throughout the session.

Key columns used for the scorecard:

| CSV column | Scorecard column | Notes |
|---|---|---|
| `id` | ID | Idea identifier |
| `description` | Idea | Coffee-talk description (2-3 sentences) |
| `phase` | Source Phase | seed / transform / hybrid |
| `menu_bucket` | Bucket | quick_win / core_bet / moonshot |
| `total_score` | Score | Numeric, from Phase 8.5 |
| `pros` | Pros | Comma-separated |
| `cons` | Cons / Risks | Comma-separated |
| `requires` | Dependencies | What's needed to act |
| `selected` | Selected | yes / no (from Phase 9) |
| `user_action` | Next Action | act_on / research_deeper / combine / saved_for_later |
| `brilliance_tier` | Brilliance | Tier 1–3 or blank |
| `brilliance_pitch` | Pitch | One-line pitch from Brilliance agent |

## Scorecard Sheet Layout

The xlsx skill should produce two sheets:

### Sheet 1 — Ranked Idea Menu

Columns (left to right): **ID · Idea · Bucket · Score · Pros · Cons/Risks · Dependencies · Selected · Next Action · Brilliance**

Sort order: `total_score` descending within each bucket group (Quick Wins → Core Bets → Moonshots → empty).

Conditional formatting:
- `menu_bucket = quick_win` → row fill **light green**
- `menu_bucket = core_bet` → row fill **light blue**
- `menu_bucket = moonshot` → row fill **light purple**
- `selected = yes` → bold text

### Sheet 2 — Weight Adjuster

A live re-weighting panel. The Synthesizer (Phase 8) writes the criteria and their default weights to `$WORKSPACE/08-synthesize.md`. Extract those criteria and create:

| Column A | Column B |
|---|---|
| Criterion name | Weight (editable, 0–10) |

Below the weight table, a formula section recomputes a `weighted_score` for each idea using the updated weights and ranks the Idea Menu live.

**Formula pattern (Excel / Google Sheets):**
```
weighted_score = SUM(criterion_score_1 * weight_1, criterion_score_2 * weight_2, ...) / SUM(weights)
```

If per-criterion scores are not available in the CSV (only `total_score` is), create one editable row per criterion for the user to manually adjust weights and observe rank shifts — the point is giving them the interactive surface, not replicating the exact Phase 8.5 math.

## Invocation

When the user chooses "Export to xlsx" at the end of Phase 9, the orchestrator calls the `anthropic-skills:xlsx` skill with:

1. The path to `$WORKSPACE/ideas.csv`
2. The path to this file (`references/xlsx-export-pattern.md`) as the layout spec
3. The path to `$WORKSPACE/08-synthesize.md` for extracting evaluation criteria and weights

The xlsx skill reads the CSV, applies the sheet layout above, and produces a `.xlsx` file saved to `$WORKSPACE/ideation-scorecard.xlsx`.

## What the xlsx Skill Should Recognize

When the xlsx skill receives a CSV with columns matching the ideation schema (`id`, `description`, `menu_bucket`, `total_score`, `brilliance_tier`), it should apply this scorecard template automatically rather than a generic table layout.

Trigger signal: CSV has **both** `menu_bucket` and `total_score` columns → use the Ranked Idea Menu + Weight Adjuster layout above.
