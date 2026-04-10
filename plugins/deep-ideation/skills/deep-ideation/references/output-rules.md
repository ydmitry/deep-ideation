# Mandatory Output Rules

These rules apply to ALL agents and ALL phases.

## Idea Description Rules

Every idea description — in seeds, transforms, builds, AND the final CSV — must be written like explaining to a colleague over coffee.

- 2-3 sentences max
- First sentence: what is it? (the mechanism, with a concrete example)
- Second sentence: why does it matter? (the impact)
- NO jargon, NO internal terminology, NO references to how the idea was generated
- Self-contained: a reader with zero context should understand it

**Example is mandatory.** "The mechanism" alone is a slogan. The concrete example (who does what, with what, and what happens) is what makes it explainable.

**BAD — procedural, timeline-heavy:**
"Week 1: Run TAM/CAC/churn research on 5 niches. Week 2: Deploy parallel gates on top 2-3. Conviction Score = (Research × 0.4) + (Gate Signals × 0.6). Pick niche > 70%."

**BAD — abstract jargon:**
"AI composition transparency mechanism addressing trust erosion root cause via disclosure tier framework with dynamic fee incentivization."

**GOOD — coffee-talk pitch with concrete example:**
"You stress-test candidate niches before writing a line of code — run €50 ads to 'freelance data analysis for SaaS startups' vs 'freelance data analysis for e-commerce' and pick whichever converts 3x better in a week. You only commit when you're 70% sure, not just hopeful."

If you feel the urge to write "Week 1 / Week 2", a formula, or a step list in `description` — stop. Put that in the `chain` field instead.

## Required CSV Columns

Every idea in the CSV must have these columns filled by the agent that creates it:

| Column | What to Write | Example |
|--------|--------------|---------|
| `description` | 2-3 sentences, coffee-talk style with a concrete example | "Companies post tasks stripped of their name. A freelancer sees 'analyze Q3 revenue for a mid-size SaaS company' instead of 'analyze Stripe's Q3 numbers.'" |
| `pros` | 2-3 concrete advantages, plain English, no acronyms | "Existing users bring their colleagues without you lifting a finger — like how Slack spread through one team and quietly took over a company." |
| `cons` | 2-3 honest risks, plain English, no acronyms | "You'll spend more acquiring each user than they're worth until you hit ~500 active — fine if you're patient, fatal if you need revenue this quarter." |
| `requires` | Concrete things that must exist first | "A list of 50+ paying customers to interview. A simple landing page. Two weeks of unblocked time." |
| `chain` | Full operation lineage (steps, formulas, timelines) | "SEED #3 → COMBINE with #8 → TRIZ Inversion → ..." |

**BAD — jargon-laden pros/cons:**
pros: "TAM expansion via network effects and viral coefficient optimization."
cons: "CAC/LTV ratio deterioration in pre-PMF stage."

**GOOD — coffee-talk pros/cons with examples:**
pros: "Existing users bring their colleagues without you lifting a finger — like how Slack spread through one team and quietly took over a company."
cons: "You'll spend more acquiring each user than they're worth until you hit ~500 active — fine if you're patient, fatal if you need revenue this quarter."

These help the reader immediately assess each idea. Agents should fill them honestly — cons are as valuable as pros.

## Idea Menu Buckets

The Scorer (Phase 8.5) assigns `menu_bucket` per idea based on qualitative judgment, not numeric thresholds. Most ideas get no bucket.

| Bucket | Qualitative definition | Action |
|--------|------------------------|--------|
| **Quick Wins** | Can be started immediately with existing resources; low structural risk | Do these first |
| **Core Bets** | Main strategic plays addressing the session's deepest root cause | Commit to these after stress-testing |
| **Moonshots** | High-novelty, high-upside; requires proof search before commitment | Validate with proof searches first |

Bucket values in the CSV: `quick_win`, `core_bet`, `moonshot`, or empty. A bucket is a recommendation — assign sparingly (3-5 per bucket maximum).

## What NOT to Include in Converge Output

When presenting final selected ideas (Phase 9 CONVERGE), do **not** include:

- Implementation timeline estimates ("6-week MVP", "build in 3 months", "ship in Q2")
- Action plan schedules ("Week 1: do X, Week 2: do Y")
- "90-day success metrics" or "first-action" checklists

These estimates are invented — the agent has no knowledge of team size, stack, prior work, or scope. Presenting them as concrete outputs creates false confidence and wastes the reader's attention. Focus instead on each idea's mechanism, why it fits the problem, and what assumptions need validating. The user decides their own timelines.

## No Scores or Formulas in User-Facing Output

Do not show ICE scores, composite scores, total_score values, or weighted formulas in any text the user reads directly — including the Idea Menu, Converge output, and Brilliance summaries.

Scores are used internally to rank and filter ideas. The output of that ranking is the bucket the idea lands in (Quick Win / Core Bet / Moonshot) and the prose explanation of why. A reader should never have to interpret a number to understand what to do.

**BAD:** "Idea #42: ICE=8.4, composite=7.6 — recommended."
**GOOD:** "This is a Quick Win. It's fast to test and you already have the distribution."

## No Methodology Names in User-Facing Text

Do not mention TRIZ, SCAMPER, Six Thinking Hats, Disney Spiral, temperature zones, Synectics, or any other internal framework name in any text the user reads.

These names are instructions for how agents generate ideas — not explanations of the ideas themselves. Mentioning them adds noise and signals process over substance.

If the mechanism of an idea came from inverting a constraint, just describe the inversion: "What if instead of X, you did the opposite — Y?" The user doesn't need to know what it was called.
