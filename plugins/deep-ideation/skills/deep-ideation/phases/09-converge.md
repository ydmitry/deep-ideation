# Phase 9: CONVERGE

Three-part convergence: Filter → Validate → Decide. Optionally: Round 2.

## Part 1: Decision Tree

Walk the user through a brief decision tree to narrow ideas to the 2-3 that fit their specific situation.

```
AskUserQuestion:
  question: "You have [N] ideas across the Idea Menu. A few questions to find your best fit:

    1. Time horizon: when do you need to see results?
    2. Authority: what can you act on unilaterally vs. needs approval?
    3. Risk appetite: are you optimizing for safety, upside, or balanced?
    4. Existing constraints: what resources do you have available?

    Based on your answers, I'll highlight the most relevant ideas from each Menu bucket."
  header: "Filter"
  options:
    - "Fast results (< 2 weeks) + unilateral + safe"
    - "Medium term (1-3 months) + some approval needed + balanced"
    - "Long game (3+ months) + need buy-in + high upside"
    - "Walk me through the questions one at a time"
```

After responses, apply the filter and present the 2-3 best-fit ideas from the Idea Menu.

## Part 2: Review Proof Search Findings

Present the proof search results (or queries to run) from Phase 8 for the top 2-3 ideas:

For each surviving idea:
- **Market evidence**: what competitors exist, what they charge, how many reviews
- **Demand signals**: what people are searching for, what they say they want
- **Failure evidence**: why similar ideas failed (if found — this is the most valuable data)
- **Verdict**: Market validated / Unvalidated / Counter-evidence found

```
AskUserQuestion:
  question: "Here are your top ideas with proof search findings:

    1. [Idea #1]: [verdict]. [key finding — e.g., '5 competitors found charging €40-80, 200+ reviews']
    2. [Idea #2]: [verdict]. [key finding — e.g., 'no competitors but strong demand signals on Reddit']
    3. [Idea #3]: [verdict]. [key finding — e.g., 'similar product failed in 2023 — reason: distribution']

    What would you like to do?"
  header: "Decision"
  options:
    - "Act on #1 — the evidence is strong"
    - "Research #2 deeper — promising but unvalidated"
    - "Combine a few ideas first, then validate"
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

## Ranking in Converge

Sort by `composite_score` (not `total_score`). This is the single authoritative ranking — it already incorporates the Scorer's weighted average, the Stress-Tester's resilience multiplier, and the Brilliance multiplier. No manual reconciliation of three competing lists is needed.

Show Z-scores alongside raw scores so the user can see where each idea sits relative to the cohort distribution:

```bash
# Primary ranking — sort by composite_score
python scripts/idea_db.py top <workspace> composite_score --n 10

# Export full ranked table with all score dimensions visible
python scripts/idea_db.py export_md <workspace> \
  --columns "id,name,total_score,z_score,stress_multiplier,brilliance_multiplier,composite_score,menu_bucket" \
  --sort composite_score --desc
```

Original per-dimension scores (e.g., `feasibility`, `novelty`) and `evidence_ref` remain in the CSV and are inspectable at any time:

```bash
python scripts/idea_db.py show <workspace> --columns "id,name,feasibility,novelty,[session-criteria],evidence_ref,score_notes"
```

## Recording Decisions in CSV

Before saving, run `describe` to see available columns, then record the user's decisions:

```bash
# Check current schema
python scripts/idea_db.py describe <workspace>

# Add convergence columns
python scripts/idea_db.py add_column <workspace> proof_verdict --default ""
python scripts/idea_db.py add_column <workspace> selected --default "no"
python scripts/idea_db.py add_column <workspace> user_action --default ""

# Record proof search verdicts for top ideas
python scripts/idea_db.py set <workspace> <id> proof_verdict "validated"
python scripts/idea_db.py set <workspace> <id> proof_verdict "unvalidated"
python scripts/idea_db.py set <workspace> <id> proof_verdict "counter-evidence"

# Mark ideas the user selected
python scripts/idea_db.py set <workspace> <id> selected "yes"

# Record what the user wants to do with each selected idea
python scripts/idea_db.py set <workspace> <id> user_action "act_on"
python scripts/idea_db.py set <workspace> <id> user_action "research_deeper"
python scripts/idea_db.py set <workspace> <id> user_action "combine"
python scripts/idea_db.py set <workspace> <id> user_action "saved_for_later"
```

This ensures the Historian in future sessions can see not just which ideas scored well, but which ones the user actually chose to act on.

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
1. **Filtered ideas**: the 2-3 best-fit ideas based on user's constraints
2. **Proof search verdicts**: Market validated / Unvalidated / Counter-evidence per idea
3. **User's decision**: which idea(s) to act on
4. **Round 2 decision** (DEEP mode): whether to run a second round, and if so, the new direction

See `references/output-rules.md` for mandatory idea description and CSV column rules.

## Iterative Rounds (DEEP mode)

See Part 3 above for the full Round 2 flow and user prompts.
