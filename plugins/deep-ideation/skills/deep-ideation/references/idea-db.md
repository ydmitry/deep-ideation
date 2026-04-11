# Idea Database — Usage Guide

Every idea in the session is recorded as a row in a CSV file (`ideas.csv`). This is the single source of truth for all ideas across all agents and phases.

## Setup

At the start of every session, initialize the DB:
```bash
python scripts/idea_db.py init <workspace>
```

This creates `<workspace>/ideas.csv` with built-in columns:
`id, name, description, source_agent, source_seed, chain, tag, phase`

## How Agents Use It

### Specialist Agents (SEED phase)
After generating seeds, save them to the DB:
```bash
# One at a time
python scripts/idea_db.py add <workspace> \
  --name "Smell Marketing" \
  --description "Pump coffee aroma onto sidewalk during peak hours" \
  --source_agent "Wild Card" \
  --tag "BOLD" \
  --phase "seed"

# Or batch from JSON
python scripts/idea_db.py add_batch <workspace> seeds.json
```

Batch JSON format:
```json
[
  {"name": "Smell Marketing", "description": "Pump coffee aroma onto sidewalk", "source_agent": "Wild Card", "tag": "BOLD", "phase": "seed"},
  {"name": "Square Wheels", "description": "What if the product got worse on purpose?", "source_agent": "Provocateur", "source_seed": "", "chain": "PROVOKE → SEED", "tag": "WILD", "phase": "seed"}
]
```

### John Agents (TRANSFORM phase)
When transforming seeds, record the new idea with its chain and temperature zone:
```bash
python scripts/idea_db.py add <workspace> \
  --name "Narrative Loading" \
  --description "Loading screen shows contextual story about your data" \
  --source_agent "John A" \
  --source_seed "3" \
  --chain "SEED #3 [Wild Card: skeleton screens] → BLACK LENS (users distrust loading) → INVERT → COMBINE with #7" \
  --tag "BOLD" \
  --phase "transform"
```

Also add a `temperature_zone` column after initializing:
```bash
python scripts/idea_db.py add_column <workspace> temperature_zone
```

### Brainwriter (BUILD phase)
After Step 1.5 (Seed Usage Report), update seed usage:
```bash
python scripts/idea_db.py add_column <workspace> seed_usage --default "cold"
# Set hot/used/cold for each seed based on usage count
python scripts/idea_db.py set <workspace> 5 seed_usage hot
```

### Adding Evaluation Columns
Any phase can add new columns for scoring or categorization:
```bash
# Add session-derived evaluation criteria (Synthesizer registers; Scorer fills)
python scripts/idea_db.py add_criteria <workspace> \
  --criteria "feasibility,novelty,trust_building,scalability" \
  --composite "total_score"

# Add the menu_bucket column (Scorer assigns qualitative labels)
python scripts/idea_db.py add_column <workspace> menu_bucket --default ""
# Valid values: quick_win / core_bet / moonshot / "" (no bucket)

# Add composite scoring pipeline columns (Phase 8.5 — Scorer sets up; later phases mutate multipliers)
python scripts/idea_db.py add_column <workspace> stress_multiplier --default "1.0"
python scripts/idea_db.py add_column <workspace> brilliance_multiplier --default "1.0"
python scripts/idea_db.py add_column <workspace> composite_score --default ""
python scripts/idea_db.py add_column <workspace> z_score --default ""
python scripts/idea_db.py add_column <workspace> score_notes --default ""
python scripts/idea_db.py add_column <workspace> evidence_ref --default ""

# Add validation columns (for web research)
python scripts/idea_db.py add_column <workspace> validation --default "unvalidated"
python scripts/idea_db.py add_column <workspace> evidence_summary --default ""

# Add TRIZ trade-off resolution column
python scripts/idea_db.py add_column <workspace> triz_status --default ""
# Values: resolves / picks_side / sidesteps

# Add Stress Test columns (Phase 9.5 — STANDARD + DEEP modes)
python scripts/idea_db.py add_column <workspace> stress_rounds --default ""
python scripts/idea_db.py add_column <workspace> stress_attacks --default ""
python scripts/idea_db.py add_column <workspace> stress_results --default ""
python scripts/idea_db.py add_column <workspace> stress_strongest_objection --default ""
python scripts/idea_db.py add_column <workspace> stress_modifications --default ""
```

### Setting Values
```bash
# Set one value
python scripts/idea_db.py set <workspace> 5 total_score 7.4
python scripts/idea_db.py set <workspace> 5 menu_bucket "quick_win"

# Batch update from JSON
python scripts/idea_db.py set_batch <workspace> scores.json
```

Batch JSON (session criteria are the columns the Synthesizer defined):
```json
[
  {"id": 1, "feasibility": "7", "novelty": "4", "trust_building": "6"},
  {"id": 2, "feasibility": "3", "novelty": "9", "trust_building": "8"}
]
```

### Querying
```bash
# Sort by any column
python scripts/idea_db.py sort <workspace> total_score --desc

# Filter by exact value
python scripts/idea_db.py filter <workspace> tag WILD
python scripts/idea_db.py filter <workspace> phase transform
python scripts/idea_db.py filter <workspace> seed_usage hot
python scripts/idea_db.py filter <workspace> menu_bucket quick_win
python scripts/idea_db.py filter <workspace> menu_bucket core_bet
python scripts/idea_db.py filter <workspace> menu_bucket moonshot

# Filter above threshold (numeric)
python scripts/idea_db.py filter_above <workspace> total_score 6

# Top N by column
python scripts/idea_db.py top <workspace> total_score --n 5

# Stats summary
python scripts/idea_db.py stats <workspace>

# Show all (or specific columns)
python scripts/idea_db.py show <workspace> --columns "id,name,tag,total_score,menu_bucket,phase,seed_usage"

# Export as markdown table (for output files)
python scripts/idea_db.py export_md <workspace> \
  --columns "id,name,source_agent,chain,tag,total_score,menu_bucket" \
  --sort total_score --desc
```

### Computing Composite Scores
```bash
# Weighted average with session-derived weights
python scripts/idea_db.py compute <workspace> \
  --criteria "feasibility,novelty,trust_building,scalability" \
  --target "total_score" \
  --formula weighted_avg \
  --weights "feasibility:2,novelty:3,trust_building:4,scalability:2"
```

## When to Use in the Flow

| Phase | What to Record |
|-------|---------------|
| **SEED** | All specialist seeds: name, description, source_agent, tag, phase=seed |
| **TRIAGE** | Update tags; add `triage_category` column (hot/warm/cold/discard) |
| **DISTRIBUTE** | Add `assigned_to` column if tracking John assignments |
| **TRANSFORM** | All John outputs: source_agent, source_seed (ID), chain, tag, phase=transform, temperature_zone |
| **BUILD** | Brainwriter builds: phase=build, chain references parents, seed_usage updates |
| **HAT EVAL** | Add hat evaluation columns per idea (white_note, red_note, black_note, etc.) |
| **TENSION** | Resolution ideas: phase=tension, triz_status for top ideas |
| **SYNTHESIZE** | Hybrids: phase=synthesis, full chains. Register evaluation criteria + composite column. Add validation. NO scoring here — the Scorer applies the criteria in Phase 8.5. |
| **SCORE** (Phase 8.5) | Expanded cohort (all phases: seed, transform, ratchet, bridge, hybrid, build, green_hat). Fill session criteria columns with forced distribution (at least one 1 and one 5 per criterion). Fill `evidence_ref` with upstream citations. Compute `total_score` via weighted_avg. Seed `composite_score` from `total_score`. Compute `z_score`. Add `menu_bucket`. Write `scorer_drop_log.md`. |
| **STRESS-TEST** | Add stress columns (stress_rounds, stress_attacks, stress_results, stress_strongest_objection, stress_modifications). Mutate `stress_multiplier` per idea (asymmetric deltas: −0.15 fatal, +0.08 survived cleanly). Append to `score_notes`. Recompute `composite_score` and `z_score`. |
| **BRILLIANCE** | Mutate `brilliance_multiplier` per evaluated idea (1.20 = BRILLIANT, 1.10 = NOTABLE, 1.00 = —). Append to `score_notes`. Recompute `composite_score` and `z_score`. |
| **CONVERGE** | Sort by `composite_score`. Show `z_score` alongside raw scores. Add proof search columns (proof_verdict). `evidence_ref` and `score_notes` remain inspectable. |

## Session Artifacts

At session end, the workspace contains:
- `ideas.csv` — every idea from every phase with full metadata
- `seed-bank.md` — top generative seeds for future Historian use
- `seeds/<agent>.md` — raw seed outputs per specialist
- `08-synthesize.md` — hybrids, convergent signals, criteria + weights
- `08.5-score.md` — ranked Idea Menu, bucket assignments, appended Brilliance output
- `scorer_drop_log.md` — ideas from the expanded cohort excluded from scoring, with reason codes

The user can:
- Open `ideas.csv` in Excel/Sheets for further analysis
- Filter by phase to see evolution from seeds → transforms → hybrids
- Sort by `composite_score` for the authoritative final ranking (incorporates Scorer + Stress + Brilliance)
- Sort by `z_score` to see which ideas stand furthest above the cohort mean
- Track which seeds produced the best final ideas (via source_seed + chain)
- Share `seed-bank.md` with the Historian for the next session
- Sort by `stress_multiplier` to see which ideas survived adversarial pressure (STANDARD/DEEP only)
- Read `stress_strongest_objection` to understand residual risks on top ideas
- Read `evidence_ref` to trace what upstream work justified each score
- Read `score_notes` for a running log of stress and brilliance verdicts per idea

### Composite Scoring Pipeline

The final ranking is built in three layers, each mutating one column:

| Phase | Column mutated | Effect on composite_score |
|-------|---------------|--------------------------|
| Scorer (8.5) | `total_score` → seeded into `composite_score` | Baseline ranking from session criteria |
| Stress-Tester (9.5) | `stress_multiplier` | Penalizes fatally flawed ideas (down to ×0.50); rewards resilient ones (up to ×1.30) |
| Brilliance (10) | `brilliance_multiplier` | Lifts structurally brilliant ideas (×1.20); leaves ordinary ones at ×1.00 |

`composite_score = total_score × stress_multiplier × brilliance_multiplier`

`z_score` is recomputed after each phase updates its multiplier, so Converge always sees the full distribution.

### Scoring Column Reference

| Column | Type | Set by | Description |
|--------|------|--------|-------------|
| `total_score` | float | Scorer | Weighted average of session criteria |
| `composite_score` | float | Scorer, then updated | total_score × stress_multiplier × brilliance_multiplier |
| `z_score` | float | Scorer, then updated | Per-idea Z-score relative to scored cohort |
| `stress_multiplier` | float | Stress-Tester | Starts at 1.0; asymmetric deltas (−0.15 fatal, +0.08 survived cleanly) |
| `brilliance_multiplier` | float | Brilliance Filter | 1.20 = BRILLIANT, 1.10 = NOTABLE, 1.00 = — |
| `score_notes` | string | Stress-Tester + Brilliance | Running one-line log of verdicts, appended by each phase |
| `evidence_ref` | string | Scorer | Citations of upstream idea-IDs or artifact snippets justifying the scores |
| `menu_bucket` | string | Scorer | quick_win / core_bet / moonshot / "" |

### Stress Test Column Reference

| Column | Type | Description |
|--------|------|-------------|
| `stress_rounds` | int | Number of attack rounds completed (2 in STANDARD, 3 in DEEP) |
| `stress_attacks` | string | Semicolon-separated list of attack types used (e.g., "Market Size;Hidden Assumption") |
| `stress_results` | string | Semicolon-separated list of outcomes per round (survived_cleanly / survived_modified / fatal_wound / no_good_objection) |
| `stress_strongest_objection` | string | The best attack that didn't kill the idea — a residual risk to monitor |
| `stress_modifications` | string | Changes the idea needed to survive attacks, or "None" |
