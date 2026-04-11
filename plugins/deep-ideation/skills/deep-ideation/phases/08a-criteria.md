# Phase 8a: CRITERIA

Launch the Synthesizer in criteria-only mode. See `agents/synthesizer.md`.

This is the first half of what was previously Phase 8. Its sole job: read the session output, derive evaluation criteria and weights, and write them to `criteria.json`. It does NOT produce hybrids — that is Phase 8b.

The orchestrator reads `criteria.json` after this phase and presents the criteria to the user for confirmation (see SKILL.md Criteria Gate). Phase 8b then uses the confirmed criteria.

## What It Receives

All previous phase outputs:
1. Digger root causes + HMW questions + TRIZ trade-off (`$WORKSPACE/01-discover.md`)
2. John outputs (`$WORKSPACE/05-john-*.md`)
3. Brainwriter enhanced ideas (`$WORKSPACE/06-build.md`) — if run
4. Hat Evaluation (`$WORKSPACE/06.5-hat-eval.md`) — if run
5. Tension Analyzer (`$WORKSPACE/07-tension.md`) — if run
6. `$WORKSPACE/ideas.csv` — to read convergent signals and tags

## What It Produces

**One output only: `$WORKSPACE/criteria.json`**

```json
{
  "criteria": [
    {
      "name": "feasibility",
      "description": "Can this be attempted in the next quarter with existing resources?",
      "weight": 25
    },
    {
      "name": "novelty",
      "description": "Does this open a direction competitors haven't explored?",
      "weight": 20
    },
    {
      "name": "<session-criterion-3>",
      "description": "<derived from the specific tensions and root causes of this session>",
      "weight": 30
    },
    {
      "name": "<session-criterion-4>",
      "description": "...",
      "weight": 15
    },
    {
      "name": "<session-criterion-5>",
      "description": "...",
      "weight": 10
    }
  ],
  "total_weight": 100,
  "composite_column": "total_score"
}
```

## Criteria Design Rules

- 5–7 criteria. Fewer means coarse ranking; more means the weights get meaningless.
- Weights must sum to 100%.
- At least 2 criteria must be session-specific (derived from root causes and tensions, not generic).
- `feasibility` and `novelty` are almost always relevant — include unless the session explicitly rules them out.
- Each criterion name must be a valid Python identifier (no spaces, use underscores).

## Key Commands

```bash
# Discover current schema before reading ideas
python scripts/idea_db.py describe <workspace>

# Check which ideas have high cross-zone agreement (signals for convergent weight)
python scripts/idea_db.py filter <workspace> tag BOLD

# Register criteria columns so Phase 8.5 (SCORE) can fill them
python scripts/idea_db.py add_criteria <workspace> \
  --criteria "feasibility,novelty,[session-criteria]" \
  --composite "total_score"
```

## Anti-Patterns

- **Don't produce hybrids here** — that is Phase 8b's job
- **Don't score ideas** — Phase 8.5 (SCORE) does that
- **Don't invent generic criteria** — at least 2 must trace directly to the session's root causes or tensions
- **Don't let weights drift from 100%** — the orchestrator will renormalize based on user input, but start at exactly 100%
