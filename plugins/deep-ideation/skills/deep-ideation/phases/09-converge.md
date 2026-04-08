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

## Saving the Session

Regardless of what the user decides, confirm:

```
AskUserQuestion:
  question: "Your session is complete. Saved:
    - All ideas: $WORKSPACE/ideas.csv
    - Idea Menu: $WORKSPACE/08-synthesize.md
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
- `$WORKSPACE/08-synthesize.md` — full synthesis with Idea Menu
- `$WORKSPACE/seed-bank.md` — condensed seeds for Historian
- `$WORKSPACE/ice-anchors.md` — scoring calibration for reference

The Historian will scan these files in future sessions.

## Output Requirements

Return a short summary to the orchestrator containing:
1. **Filtered ideas**: the 2-3 best-fit ideas based on user's constraints
2. **Proof search verdicts**: Market validated / Unvalidated / Counter-evidence per idea
3. **User's decision**: which idea(s) to act on
4. **Round 2 decision** (DEEP mode): whether to run a second round, and if so, the new direction

### Mandatory Idea Description Rules

Every idea description — in all phases — must follow these rules:
- 2-3 sentences max. First sentence: what is it (mechanism + concrete example). Second: why it matters (impact).
- NO jargon, NO internal terminology. Self-contained: zero context needed.
- Every idea in the CSV must have: `description` (coffee-talk), `pros` (2-3 advantages), `cons` (2-3 risks), `requires` (what must exist first).

## Iterative Rounds (DEEP mode)

After convergence, offer the user a second round:

**Round 2 flow:**
1. Top 3-5 from Round 1 become new seeds (phase=round2_seed)
2. User-specified new direction becomes a new HMW question
3. Run: Innovator + Connector (specialists only)
4. One John (user picks zone, or default PLASMA)
5. Skip Brainwriter + Tension Analyzer (faster)
6. Synthesizer produces merged output combining Round 1 + Round 2 ideas
