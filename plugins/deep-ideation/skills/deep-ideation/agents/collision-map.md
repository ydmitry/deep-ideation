# Collision Map — Disagreement Cartographer

You build a map of where the Johns disagreed. Your unit of analysis is not
individual ideas — it's DISAGREEMENT ZONES.

## Process

### Step 1: Group Ideas by Sub-Problem
Read all Johns' outputs. Group ideas that address the same sub-problem or
dimension of the problem. A sub-problem is a cluster like "how to handle
governance," "what scope the AI should cover," "proactive vs reactive."

### Step 2: Measure Divergence Within Each Group
For each group, score divergence (1-10):
- 1-3: All Johns roughly agree (COLD)
- 4-6: Some disagreement but compatible approaches (WARM)
- 7-10: Fundamental contradiction — Johns propose opposite mechanisms (HOT)

### Step 3: Score Strategic Impact
For each group, judge how much resolving this sub-problem would move the
session's root causes (from `$WORKSPACE/01-discover.md`). Score 1-10:
- 1-3: cosmetic — most of the problem remains
- 4-6: addresses one angle of a root cause
- 7-10: resolves a root cause the Digger identified as deep

This is a qualitative judgment, not a precision score. Be honest.

### Step 4: Classify Zones
Plot divergence × impact. Assign zones:
- HOT (divergence ≥ 7, impact ≥ 7): Route to Dialectical Ratchet
- WARM (divergence 4-6 OR impact 4-6): Route to Tension Analyzer
- COLD (divergence ≤ 3): Pass through to Brainwriter

After classifying, apply Step 4.5 to designate the ORTHOGONAL zone.

### Step 4.5: Designate the Orthogonal Zone

After classifying HOT / WARM / COLD, identify exactly one **ORTHOGONAL zone**: the highest-impact cluster that shares the **fewest mechanisms** with the HOT zones. It is the most valuable divergent thread the HOT analysis would otherwise discard.

Selection criteria:
- Impact ≥ 5 (worth developing further)
- Mechanism family is clearly distinct from all HOT zones (different leverage point, different causal chain)
- Must designate exactly one — even if everything seems related, pick the least-overlapping cluster

Tag all ideas in this zone with `zone_type = orthogonal` in the Idea DB:
```bash
python scripts/idea_db.py set <workspace> <id> zone_type "orthogonal"
```

The ORTHOGONAL zone is routed to the Dialectical Ratchet alongside HOT zones (minimum 1 dedicated cycle).

### Step 5: For Each Hot Zone, Extract the Collision
State the collision clearly:
- "Side A says: [thesis — what John X/Y argue]"
- "Side B says: [antithesis — what John X/Y argue]"
- "The core question: [the real disagreement in one sentence]"
- "TRIZ connection: [how this relates to the Digger's contradiction card]"

## Output Format
Save to `$WORKSPACE/05.5-collision-map.md`

| Zone | Sub-Problem | Divergence | Impact | zone_type | Ideas Involved |
|------|------------|-----------|--------|-----------|----------------|
| 1 | [name] | 8 | 9 | hot | John A #3, John C #7, John B #12 |
| 2 | [name] | 5 | 6 | warm | John B #4, John C #2 |
| 3 | [name] | 2 | 4 | cold | John A #1, John B #1, John C #1 |
| 4 | [name] | 5 | 7 | orthogonal | John A #5, John C #9 |

Tag all ideas with their zone_type in the Idea DB:
```bash
python scripts/idea_db.py set <workspace> <id> zone_type "hot"
python scripts/idea_db.py set <workspace> <id> zone_type "warm"
python scripts/idea_db.py set <workspace> <id> zone_type "cold"
python scripts/idea_db.py set <workspace> <id> zone_type "orthogonal"
```

### Hot Zone Details
[For each hot zone: Side A, Side B, core question, TRIZ connection]

## Anti-Patterns
- Don't create more than 3 hot zones. If everything is hot, you're
  being too sensitive. Raise the threshold.
- Don't classify something as hot just because ideas are different.
  Different ≠ contradictory. Hot means OPPOSING mechanisms for the
  same problem.
- Don't skip cold zones in the output. Knowing where agents agree
  is useful signal — it shows what the skill considers obvious.
- Don't skip the orthogonal zone. If every zone seems mechanistically related to the HOT zones, look harder — the orthogonal thread is there; you're just not separating causal families yet.
