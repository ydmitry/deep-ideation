# Phase 9: CONVERGE

Three-part convergence: Operator Capacity → Filter → Validate → Decide. Optionally: Round 2.

## Part 0: Operator Capacity Check (REQUIRED — runs before any filtering)

Before presenting ideas, establish the operator's execution capacity. The final recommendation is blocked if it exceeds these constraints.

```
AskUserQuestion:
  question: "Before I filter to your best options, I need to understand your execution capacity for the next 30 days:

    1. **People**: How many people are executing on this? (just you, or a team — and if a team, how many?)
    2. **Time**: How many hours per week can you personally dedicate?
    3. **Cash**: What is your available budget to deploy (€/$ rough estimate)?"
  header: "Capacity"
  options:
    - "Solo — ~5 hrs/week — €0 (bootstrap)"
    - "Solo — ~20 hrs/week — <€500"
    - "Small team (2-3) — part-time — €500-5k"
    - "Small team (2-3) — full-time — €5k+"
    - "Let me enter custom numbers"
```

Record the operator constraint:
```bash
python scripts/idea_db.py add_column <workspace> capacity_people --default ""
python scripts/idea_db.py add_column <workspace> capacity_hrs_week --default ""
python scripts/idea_db.py add_column <workspace> capacity_cash --default ""
python scripts/idea_db.py set_session <workspace> capacity_people "[N]"
python scripts/idea_db.py set_session <workspace> capacity_hrs_week "[N]"
python scripts/idea_db.py set_session <workspace> capacity_cash "[amount]"
```

## Part 1: Decision Tree

Walk the user through a brief decision tree to narrow ideas to the best fit for their situation.

```
AskUserQuestion:
  question: "You have [N] ideas across the Idea Menu. A few questions to find your best fit:

    1. Time horizon: when do you need to see results?
    2. Authority: what can you act on unilaterally vs. needs approval?
    3. Risk appetite: are you optimizing for safety, upside, or balanced?

    Based on your answers and your capacity ([N] people, [N] hrs/week, [cash]), I'll highlight your Primary direction and one Backup."
  header: "Filter"
  options:
    - "Fast results (< 2 weeks) + unilateral + safe"
    - "Medium term (1-3 months) + some approval needed + balanced"
    - "Long game (3+ months) + need buy-in + high upside"
    - "Walk me through the questions one at a time"
```

After responses, apply the filter and present exactly **one Primary direction + one Backup** from the Idea Menu. Do not recommend three concurrent initiatives — a solo operator cannot execute them in parallel within 30 days.

## Part 2: Review Proof Search Findings + Capacity Budget

Present the proof search results (or queries to run) from Phase 8 for the Primary and Backup ideas:

For each surviving idea:
- **Market evidence**: what competitors exist, what they charge, how many reviews
- **Demand signals**: what people are searching for, what they say they want
- **Failure evidence**: why similar ideas failed (if found — this is the most valuable data)
- **Verdict**: Market validated / Unvalidated / Counter-evidence found

Then present the **Capacity Budget Table** for the Primary direction. The recommendation is blocked if the Primary exceeds the operator's stated capacity.

```
**Capacity Budget — Primary Direction: [Idea Name]**

| Resource | Required (30 days) | Operator Budget | Fits? |
|----------|-------------------|-----------------|-------|
| Hours/week | [estimate] | [operator input] | ✓/✗ |
| Cash | [estimate] | [operator input] | ✓/✗ |
| People | [estimate] | [operator input] | ✓/✗ |

If any row is ✗: switch Primary and Backup, or flag as over-capacity.
```

```
AskUserQuestion:
  question: "Here are your top directions with proof search findings:

    PRIMARY — [Idea #1]: [verdict]. [key finding]
    Capacity fit: [hours]/wk, [cash], [people] — [FITS / OVER BUDGET]

    BACKUP — [Idea #2]: [verdict]. [key finding]
    Capacity fit: [hours]/wk, [cash], [people] — [FITS / OVER BUDGET]

    What would you like to do?"
  header: "Decision"
  options:
    - "Act on Primary — the evidence is strong and it fits my capacity"
    - "Switch to Backup — Primary is over budget"
    - "Research Primary deeper — promising but unvalidated"
    - "I need to think — save everything"
    - "Start a Round 2 — I want to explore [direction] deeper"
```

## Part 3: Round 2 (DEEP mode or user-requested)

If the user wants to go deeper:

```
AskUserQuestion:
  question: "Round 2 will:
    - Use your Top 3 from Round 1 as seeds
    - Add your new direction as a fresh HMW question
    - Run Innovator + Connector (2 specialists)
    - Run one focused John (choose zone)
    - Synthesizer merges Round 1 + Round 2 into a unified Idea Menu

    What new direction should Round 2 explore?"
  header: "Round 2"
  options:
    - "Go deeper on [top idea from Round 1]"
    - "Explore the angle Round 1 missed: [describe]"
    - "Focus on the TRIZ contradiction we haven't resolved"
    - "Skip Round 2 — I have enough"
```

**Round 2 flow:**
1. Take Top 3-5 from Round 1 as new seeds (phase=round2_seed)
2. Add user's new direction as a HMW question
3. Run: Innovator + Connector only
4. One John (user picks zone, or default PLASMA)
5. Skip Brainwriter + Tension Analyzer (faster)
6. Synthesizer produces merged output

## Recording Decisions in CSV

Before saving, run `describe` to see available columns, then record the user's decisions:

```bash
# Check current schema
python scripts/idea_db.py describe <workspace>

# Add convergence columns
python scripts/idea_db.py add_column <workspace> proof_verdict --default ""
python scripts/idea_db.py add_column <workspace> selected --default "no"
python scripts/idea_db.py add_column <workspace> user_action --default ""
python scripts/idea_db.py add_column <workspace> convergence_role --default ""

# Record proof search verdicts for top ideas
python scripts/idea_db.py set <workspace> <id> proof_verdict "validated"
python scripts/idea_db.py set <workspace> <id> proof_verdict "unvalidated"
python scripts/idea_db.py set <workspace> <id> proof_verdict "counter-evidence"

# Mark Primary and Backup roles
python scripts/idea_db.py set <workspace> <id> convergence_role "primary"
python scripts/idea_db.py set <workspace> <id> convergence_role "backup"

# Mark ideas the user selected
python scripts/idea_db.py set <workspace> <id> selected "yes"

# Record what the user wants to do with each selected idea
python scripts/idea_db.py set <workspace> <id> user_action "act_on"
python scripts/idea_db.py set <workspace> <id> user_action "research_deeper"
python scripts/idea_db.py set <workspace> <id> user_action "combine"
python scripts/idea_db.py set <workspace> <id> user_action "saved_for_later"

# Log capacity_fit telemetry: "fit" if Primary fits operator capacity, "over_budget" if switched
python scripts/idea_db.py telemetry <workspace> capacity_fit "fit"   # or "over_budget"
```

This ensures the Historian in future sessions can see not just which ideas scored well, but which ones the user actually chose to act on — and whether the recommendation fit within their execution reality.

## Saving the Session

Regardless of what the user decides, confirm:

```
AskUserQuestion:
  question: "Your session is complete. Saved:
    - All ideas: $WORKSPACE/ideas.csv
    - Synthesis (hybrids + criteria): $WORKSPACE/08-synthesize.md
    - Ranked Idea Menu + Brilliance: $WORKSPACE/08.5-score.md
    - Seed Bank: $WORKSPACE/seed-bank.md (for future sessions)

    The Idea Menu has [N] Quick Wins, [N] Core Bets, [N] Moonshots.
    Your top pick: [#1 from their decision above]"
  header: "Session Complete"
  options:
    - "Great, I'll act on [choice] today"
    - "Export the top ideas as a summary"
    - "Start a new session on a different problem"
```

## What Gets Saved

- `$WORKSPACE/ideas.csv` — complete session artifact
- `$WORKSPACE/08-synthesize.md` — hybrids, convergent signals, criteria and weights
- `$WORKSPACE/08.5-score.md` — ranked Idea Menu, bucket assignments, appended Brilliance output
- `$WORKSPACE/seed-bank.md` — condensed seeds for Historian

The Historian will scan these files in future sessions.

## Output Requirements

Return a short summary to the orchestrator containing:
1. **Operator capacity**: people, hrs/week, cash
2. **Primary direction**: the single best-fit idea, with proof search verdict and capacity fit status
3. **Backup direction**: the fallback idea, with proof search verdict and capacity fit status
4. **Capacity Budget Table**: estimated hours, cash, and headcount for the Primary direction over 30 days
5. **User's decision**: which direction to act on
6. **Round 2 decision** (DEEP mode): whether to run a second round, and if so, the new direction

See `references/output-rules.md` for mandatory idea description and CSV column rules.

## Iterative Rounds (DEEP mode)

See Part 3 above for the full Round 2 flow and user prompts.
