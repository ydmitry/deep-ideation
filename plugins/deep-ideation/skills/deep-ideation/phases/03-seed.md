# Phase 3: SEED (Parallel, Fast)

Launch specialist agents simultaneously. Each gets the Problem Brief + HMW questions + TRIZ trade-off.

## Specialists to Launch

### STANDARD / DEEP mode (4 specialists):
- **Provocateur** → `agents/provocateur.md` — reverse brainstorm → invert
- **Innovator** → `agents/innovator.md` — SCAMPER + TRIZ Contradiction Card
- **Wild Card** → `agents/wild-card.md` — Crazy 8s, random stimuli, personas
- **Connector** → `agents/connector.md` — Synectics across 6 domains

### LITE mode (2 specialists):
- **Innovator** + **Wild Card** only

## What Each Specialist Receives

Every specialist gets:
1. Problem statement (one sentence)
2. All root causes (from Digger)
3. All HMW questions (from Digger)
4. **TRIZ trade-off** (from Digger) — especially important for Innovator
5. IFR statement (from Orchestrate)
6. Historical seeds (DEEP mode, from Historian)

## What Each Specialist Produces

Each saves output to:
- `$WORKSPACE/seeds/<agent-name>.md` — human-readable seed list
- Idea DB:
```bash
python scripts/idea_db.py describe <workspace>
python scripts/idea_db.py add_batch <workspace> <agent>-seeds.json
# The output will print IDs: 1,2,3... — pass these to the orchestrator for downstream use
```

Each seed is: **one name + one sentence**. Tagged [SAFE/BOLD/WILD/BASELINE]. No elaboration.

The Innovator additionally produces:
- A filled-out TRIZ Contradiction Card
- A trade-off question for the Johns

## Expected Output

| Specialist | Min Seeds | Max Seeds | Required [BASELINE] |
|-----------|-----------|-----------|---------------------|
| Provocateur | 10 | 15 | 1 |
| Innovator | 12 | 18 | 1 |
| Wild Card | 12 | 18 | 1 |
| Connector | 10 | 15 | 1 |
| **Total** | **44** | **66** | **4** |

While running, tell the user: "Four specialists are generating raw seed ideas in parallel. Expected: 40-60 seeds (including 4 baseline anchors)."

## Concreteness Floor

After seeds are collected and before they are written to the Idea DB, apply the Concreteness Floor. Every seed must be able to answer all five questions — or it is flagged:

1. **Day 1 action** — What does the operator actually do on day 1?
2. **Money flow** — In which direction does money move, and what is the rough split (%)?
3. **Product surface** — Which specific product surface is touched (name it)?
4. **Smallest pilot** — What is the smallest runnable pilot (shippable this week)?
5. **Ownership** — Who owns this on the org chart?

Seeds that pass all five: recorded normally.
Seeds that fail one or more: flagged `mechanism_density=low` in the JSON before `add_batch`. They are **not discarded** — they are downweighted by the Scorer (Phase 8.5).

```bash
# After add_batch, set mechanism_density for flagged seeds
python scripts/idea_db.py add_column <workspace> mechanism_density --default "ok"
python scripts/idea_db.py set <workspace> <id> mechanism_density "low"

# Log telemetry
python scripts/idea_db.py telemetry <workspace> mechanism_density_rejects <count>
python scripts/idea_db.py telemetry <workspace> baseline_count <count>
```

## Anti-Patterns
- Don't let specialists elaborate seeds — one sentence only
- Don't filter seeds before they reach Johns — that's the Triage phase
- Don't give all specialists the same HMW emphasis — let them choose naturally
- Don't skip the Concreteness Floor — vague seeds that survive to Converge become unimplementable recommendations
- Don't omit the [BASELINE] seed from any specialist batch — without it, the Scorer has no reality anchor and the ranking becomes a cleverness contest
