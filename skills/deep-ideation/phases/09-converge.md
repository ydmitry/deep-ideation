# Phase 9: CONVERGE

Three-part convergence: Filter → Experiment → Decide. Optionally: Round 2.

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

## Part 2: Confirm Experiments

Present the experiment designs from Phase 8 for the top 2-3 ideas:

For each surviving idea:
- **48-hour version**: the stripped-down test
- **Success signal**: specific observable outcome
- **Kill criterion**: riskiest assumption to test first
- **If it works**: next 2-week move

```
AskUserQuestion:
  question: "Here are your top ideas with experiment designs:

    1. [Idea #1]: 48-hr test = [description]. Success = [signal]. Kill = [criterion].
    2. [Idea #2]: 48-hr test = [description]. Success = [signal]. Kill = [criterion].
    3. [Idea #3]: 48-hr test = [description]. Success = [signal]. Kill = [criterion].

    What would you like to do?"
  header: "Decision"
  options:
    - "Run experiment for #1 this week"
    - "Run #1 and #2 in parallel (different assumptions)"
    - "Combine a few ideas first, then experiment"
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
