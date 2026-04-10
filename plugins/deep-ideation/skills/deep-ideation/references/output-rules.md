# Mandatory Output Rules

These rules apply to ALL agents and ALL phases.

## Idea Description Rules

Every idea description — in seeds, transforms, builds, AND the final CSV — must be written like explaining to a colleague over coffee.

- 2-3 sentences max
- First sentence: what is it? (the mechanism, with a concrete example)
- Second sentence: why does it matter? (the impact)
- NO jargon, NO internal terminology, NO references to how the idea was generated
- Self-contained: a reader with zero context should understand it

**GOOD:** "Every deliverable on Upwork shows a label indicating what percentage was AI versus human effort. Clients see exactly what they're paying for, and freelancers who add more human judgment can charge premium rates."

**BAD:** "AI composition transparency mechanism addressing trust erosion root cause via disclosure tier framework with dynamic fee incentivization."

## Required CSV Columns

Every idea in the CSV must have these columns filled by the agent that creates it:

| Column | What to Write | Example |
|--------|--------------|---------|
| `description` | 2-3 sentences, coffee-talk style | "Companies post tasks stripped of their name. A freelancer sees 'analyze Q3 revenue for a mid-size SaaS company' instead of 'analyze Stripe's Q3 numbers.'" |
| `pros` | 2-3 concrete advantages | "Zero infrastructure cost. Addresses immediate post-layoff demand. Creates premium pricing tier." |
| `cons` | 2-3 honest risks or downsides | "Hard to maintain anonymity for niche industries. Freelancers may resist not knowing who they work for." |
| `requires` | What must exist first | "Anonymization engine. Legal review. 50+ enterprise pilots." |

These help the reader immediately assess each idea. Agents should fill them honestly — cons are as valuable as pros.

## Idea Menu Buckets

The Scorer (Phase 8.5) assigns `menu_bucket` per idea based on qualitative judgment, not numeric thresholds. Most ideas get no bucket.

| Bucket | Qualitative definition | Action |
|--------|------------------------|--------|
| **Quick Wins** | Can be started immediately with existing resources; low structural risk | Do these first |
| **Core Bets** | Main strategic plays addressing the session's deepest root cause | Commit to these after stress-testing |
| **Moonshots** | High-novelty, high-upside; requires proof search before commitment | Validate with proof searches first |

Bucket values in the CSV: `quick_win`, `core_bet`, `moonshot`, or empty. A bucket is a recommendation — assign sparingly (3-5 per bucket maximum).
