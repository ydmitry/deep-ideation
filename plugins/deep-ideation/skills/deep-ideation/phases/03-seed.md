# Phase 3: SEED (Parallel, Fast)

Launch specialist agents simultaneously. Each gets the Problem Brief + HMW questions + TRIZ trade-off.

## Specialists to Launch

### STANDARD / DEEP mode (4 specialists):
- **Provocateur** → `agents/provocateur.md` — reverse brainstorm → invert
- **Innovator** → `agents/innovator.md` — SCAMPER + TRIZ Contradiction Card
- **Wild Card** → `agents/wild-card.md` — Crazy 8s, random stimuli, personas
- **Connector** → `agents/connector.md` — Synectics across 6 domains

### Corporate / Strategic scope (add 1 specialist):
- **Market Analyst** → `agents/market-analyst.md` — segment choice, pricing model, packaging, sales motion, competitive positioning
- Required when `scope = corporate` or `strategic` (set in Phase 2: ORCHESTRATE)
- Runs in parallel with the 4 standard specialists (5 agents total in STANDARD/DEEP)
- Initializes economics columns in the Idea DB: `segment_shift`, `pricing_shift`, `revenue_model`, `unit_economics_note`
- All other specialists should populate these columns when their seeds have clear economic implications

### LITE mode (2 specialists):
- **Innovator** + **Wild Card** only
- Market Analyst is never included in LITE mode

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

| Specialist | Min Seeds | Max Seeds | When Active |
|-----------|-----------|-----------|-------------|
| Provocateur | 10 | 15 | STANDARD/DEEP |
| Innovator | 12 | 18 | All modes |
| Wild Card | 12 | 18 | All modes |
| Connector | 10 | 15 | STANDARD/DEEP |
| Market Analyst | 10 | 15 | Corporate/Strategic scope only |
| **Total (standard)** | **44** | **66** | |
| **Total (strategic)** | **54** | **81** | |

While running, tell the user:
- Standard: "Four specialists are generating raw seed ideas in parallel. Expected: 40-60 seeds."
- Strategic/Corporate: "Five specialists are generating raw seed ideas in parallel, including a Market Analyst for go-to-market dimensions. Expected: 50-75 seeds."

## Anti-Patterns
- Don't let specialists elaborate seeds — one sentence only
- Don't filter seeds before they reach Johns — that's the Triage phase
- Don't give all specialists the same HMW emphasis — let them choose naturally
