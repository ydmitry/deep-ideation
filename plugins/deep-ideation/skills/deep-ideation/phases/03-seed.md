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

Each seed is: **one name + one sentence**. Tagged [SAFE/BOLD/WILD]. No elaboration.

The Innovator additionally produces:
- A filled-out TRIZ Contradiction Card
- A trade-off question for the Johns

## Expected Output

| Specialist | Min Seeds | Max Seeds |
|-----------|-----------|-----------|
| Provocateur | 10 | 15 |
| Innovator | 12 | 18 |
| Wild Card | 12 | 18 |
| Connector | 10 | 15 |
| **Total** | **44** | **66** |

While running, tell the user: "Four specialists are generating raw seed ideas in parallel. Expected: 40-60 seeds."

## Anti-Patterns
- Don't let specialists elaborate seeds — one sentence only
- Don't filter seeds before they reach Johns — that's the Triage phase
- Don't give all specialists the same HMW emphasis — let them choose naturally
