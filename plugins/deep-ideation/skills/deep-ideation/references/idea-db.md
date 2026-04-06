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
# Add Anchored ICE columns
python scripts/idea_db.py add_column <workspace> impact
python scripts/idea_db.py add_column <workspace> confidence
python scripts/idea_db.py add_column <workspace> ease
python scripts/idea_db.py add_column <workspace> ice_score

# Add session-derived evaluation criteria
python scripts/idea_db.py add_criteria <workspace> \
  --criteria "feasibility,novelty,trust_building,scalability" \
  --composite "total_score"

# Add validation columns (for web research)
python scripts/idea_db.py add_column <workspace> validation --default "unvalidated"
python scripts/idea_db.py add_column <workspace> evidence_summary --default ""

# Add TRIZ trade-off resolution column
python scripts/idea_db.py add_column <workspace> triz_status --default ""
# Values: resolves / picks_side / sidesteps

# Add Stress Test columns (Phase 9.5 — STANDARD + DEEP modes)
python scripts/idea_db.py add_column <workspace> confidence_raw --default "5.0"
python scripts/idea_db.py add_column <workspace> confidence_adjusted
python scripts/idea_db.py add_column <workspace> stress_rounds
python scripts/idea_db.py add_column <workspace> stress_attacks
python scripts/idea_db.py add_column <workspace> stress_results
python scripts/idea_db.py add_column <workspace> stress_strongest_objection
python scripts/idea_db.py add_column <workspace> stress_modifications
```

### Setting Values
```bash
# Set one value
python scripts/idea_db.py set <workspace> 5 ice_score 18.0

# Batch update from JSON
python scripts/idea_db.py set_batch <workspace> scores.json
```

Batch JSON:
```json
[
  {"id": 1, "impact": "9", "confidence": "7", "ease": "6", "ice_score": "12.6"},
  {"id": 2, "impact": "8", "confidence": "8", "ease": "4", "ice_score": "9.1"}
]
```

### Querying
```bash
# Sort by any column
python scripts/idea_db.py sort <workspace> ice_score --desc

# Filter by exact value
python scripts/idea_db.py filter <workspace> tag WILD
python scripts/idea_db.py filter <workspace> phase transform
python scripts/idea_db.py filter <workspace> seed_usage hot

# Filter above threshold (numeric)
python scripts/idea_db.py filter_above <workspace> ice_score 15

# Top N by column
python scripts/idea_db.py top <workspace> ice_score --n 5

# Multi-condition filter (Idea Menu queries)
python scripts/idea_db.py multi_filter <workspace> \
  --conditions "ease>=7,confidence>=6"   # Quick Wins
python scripts/idea_db.py multi_filter <workspace> \
  --conditions "impact>=8,confidence>=5"  # Core Bets
python scripts/idea_db.py multi_filter <workspace> \
  --conditions "impact>=9,novelty>=8"     # Moonshots

# Stats summary
python scripts/idea_db.py stats <workspace>

# Show all (or specific columns)
python scripts/idea_db.py show <workspace> --columns "id,name,tag,ice_score,phase,seed_usage"

# Export as markdown table (for output files)
python scripts/idea_db.py export_md <workspace> \
  --columns "id,name,source_agent,chain,tag,ice_score,total_score" \
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

# ICE formula
python scripts/idea_db.py compute <workspace> \
  --criteria "impact,confidence,ease" \
  --target "ice_score" \
  --formula ice
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
| **SYNTHESIZE** | Hybrids: phase=synthesis, full chains. ICE calibration. Add evaluation criteria. Score all. Add validation. |
| **CONVERGE** | Add experiment columns (48hr_version, success_signal, kill_criterion) |
| **STRESS-TEST** | Add stress columns (confidence_raw, confidence_adjusted, stress_rounds, stress_attacks, stress_results, stress_strongest_objection, stress_modifications). `confidence_adjusted` is the authoritative battle-test confidence for each idea. |

## Session Artifacts

At session end, the workspace contains:
- `ideas.csv` — every idea from every phase with full metadata
- `seed-bank.md` — top generative seeds for future Historian use
- `ice-anchors.md` — calibration anchors for this session's scores
- `seeds/<agent>.md` — raw seed outputs per specialist

The user can:
- Open `ideas.csv` in Excel/Sheets for further analysis
- Filter by phase to see evolution from seeds → transforms → hybrids
- Sort by any score column
- Track which seeds produced the best final ideas (via source_seed + chain)
- Share `seed-bank.md` with the Historian for the next session
- Sort by `confidence_adjusted` to see which ideas survived stress testing (STANDARD/DEEP only)
- Read `stress_strongest_objection` to understand residual risks on top ideas

### Stress Test Column Reference

| Column | Type | Description |
|--------|------|-------------|
| `confidence_raw` | float | Always 5.0 — neutral starting point before any stress testing |
| `confidence_adjusted` | float | 5.0 ± round scores. Range 1.0–9.0. Scores ≥7 = battle-tested. |
| `stress_rounds` | int | Number of attack rounds completed (2 in STANDARD, 3 in DEEP) |
| `stress_attacks` | string | Semicolon-separated list of attack types used (e.g., "Market Size;Hidden Assumption") |
| `stress_results` | string | Semicolon-separated list of outcomes per round (survived_cleanly / survived_modified / fatal_wound / no_good_objection) |
| `stress_strongest_objection` | string | The best attack that didn't kill the idea — a residual risk to monitor |
| `stress_modifications` | string | Changes the idea needed to survive attacks, or "None" |
