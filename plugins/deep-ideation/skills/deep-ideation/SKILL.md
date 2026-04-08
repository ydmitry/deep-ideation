---
name: deep-ideation
description: "Multi-agent parallel brainstorming at maximum creative depth. Specialists generate high-volume seed ideas; generalist Johns transform them through Disney spirals using an operations toolkit (SCAMPER, TRIZ Contradiction Engine, Six Hats, Reverse Brainstorming, Synectics). Use whenever the user wants to brainstorm with maximum depth, explore a problem from many angles simultaneously, generate a large volume of diverse ideas, or asks for 'deep ideation', 'multi-agent brainstorm', 'parallel brainstorming', 'swarm brainstorm'. Also use when the user says they want 'lots of ideas', 'explore every angle', or 'think about this from every perspective'."
---

# Deep Ideation v8 — Orchestrator Architecture

You are a lightweight orchestrator. You do NOT read phase files or agent files yourself. You spawn a fresh subagent for each phase — each reads only its own instructions and produces output to the workspace.

## Complexity Modes

Choose before starting. Ask the user if unclear.

| Mode | When to Use | Phases Run | Specialists | Johns |
|------|------------|-----------|-------------|-------|
| **LITE** | Quick problem, 30-min session | 1 → 3 → 8 → 9 → 10 | Innovator + Wild Card | 2 (FIRE, ICE) |
| **STANDARD** | Default. Most problems. | All phases including 9.5 | All 4 specialists | 3-4 (FIRE, PLASMA, ICE + GHOST if >10 cold) |
| **DEEP** | High-stakes, complex | All phases + Historian + Round 2 | All 4 + Historian | 4-5 (FIRE, PLASMA, ICE, GHOST, MIRROR) |

**LITE skips:** ORCHESTRATE, DISTRIBUTE, BUILD, TENSION, COLLISION MAP, RATCHET, HAT EVAL, STRESS-TEST.
**DEEP adds:** Historian after DISCOVER, full Collision Map (all zones), Ratchet (3 cycles), Hat Eval, Round 2 option.

## Workspace Setup

```bash
WORKSPACE="results/$(date +%Y%m%d-%H%M%S)-$(echo "$PROBLEM" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | head -c 30)"
mkdir -p "$WORKSPACE/seeds"
python scripts/idea_db.py init "$WORKSPACE"
```

## Mandatory Output Standards

Every subagent prompt must include `references/output-rules.md` in its file list. This file contains:
- Idea description rules (coffee-talk, 2-3 sentences, no jargon)
- Required CSV columns (`description`, `pros`, `cons`, `requires`)
- Idea Menu bucket definitions (Quick Wins / Core Bets / Moonshots)

## Phase Orchestration

For each phase: spawn an Agent, pass it the files to read, the input from prior phases, and the problem statement. Collect the summary it returns. Pass file PATHS (not full content) between phases. Pass short summaries (2-5 sentences) for context.

### Phase 1: DISCOVER (all modes, sequential)

Spawn Agent:
- Reads: `phases/01-discover.md` + `agents/digger.md`
- Input: problem statement, user's preferred angles (if any)
- If DEEP: spawn a second Agent reading `agents/historian.md` after Digger completes
- Produces: root causes, HMW questions, TRIZ trade-off → `$WORKSPACE/01-discover.md`
- After: present root causes + HMW to user for confirmation before proceeding

### Phase 2: ORCHESTRATE (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/02-orchestrate.md`
- Input: discover summary, workspace path
- Produces: problem type, IFR, ICE anchors, distribution plan → `$WORKSPACE/02-orchestrate.md` + `$WORKSPACE/ice-anchors.md`

### Phase 3: SEED (all modes, parallel)

Spawn 2-4 Agents simultaneously:
- Each reads: `phases/03-seed.md` + `agents/<specialist>.md`
- LITE: Innovator + Wild Card (2 agents)
- STANDARD/DEEP: Provocateur + Innovator + Wild Card + Connector (4 agents)
- Input: problem brief, root causes, HMW questions, IFR, TRIZ trade-off
- Each produces: 10-18 seeds → `$WORKSPACE/seeds/<agent-name>.md` + Idea DB

### Phase 4: DISTRIBUTE (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/04-distribute.md`
- Input: all seed file paths, mode, orchestration plan
- Produces: triage results, John assignments → `$WORKSPACE/04-distribute.md`

### Phase 5: TRANSFORM (all modes, parallel)

Spawn 2-5 John Agents simultaneously:
- Each reads: `phases/05-transform.md` + `agents/john.md`
- Input per John: seed batch, temperature zone, starting mode, second constraint (if any), ICE anchors, TRIZ trade-off, `references/operations.md`
- LITE: 2 Johns (FIRE, ICE). STANDARD: 3-4. DEEP: 4-5 (MIRROR runs after others).
- Each produces: 10-15 transformed ideas → `$WORKSPACE/05-john-[a-e].md` + Idea DB

### Phase 5.5: COLLISION MAP (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/05.5-collision-map.md` + `agents/collision-map.md`
- Input: all John output paths, ICE anchors, TRIZ card
- STANDARD: cap at 2 hot zones. DEEP: all zones (max 3).
- Produces: HOT/WARM/COLD zone classification + routing plan → `$WORKSPACE/05.5-collision-map.md`

### Phase 5.7: RATCHET (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/05.7-ratchet.md` + `agents/dialectical-ratchet.md`
- Input: hot zone details from collision map, TRIZ card, ICE anchors
- STANDARD: 2 cycles/zone. DEEP: 3 cycles + full TRIZ.
- Produces: synthesis per hot zone → `$WORKSPACE/05.7-ratchet.md` + Idea DB

### Phase 6: BUILD (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/06-build.md` + `agents/brainwriter.md`
- Input: all John output paths, ratchet syntheses path, hat eval path (if run)
- Produces: 20-30 enhanced ideas + cross-zone combos → `$WORKSPACE/06-build.md` + Idea DB

### Phase 6.5: HAT EVAL (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/06.5-hat-eval.md`
- Input: top 10 ideas from build phase
- Produces: six-hat analysis + invert candidates + combination suggestions → `$WORKSPACE/06.5-hat-eval.md`

### Phase 7: TENSION (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/07-tension.md` + `agents/tension-analyzer.md`
- Input: John outputs, brainwriter ideas, hat eval (if run), collision map warm zones, TRIZ card
- Produces: 3-5 tensions + bridges + PMI + deepest tension → `$WORKSPACE/07-tension.md` + Idea DB

### Phase 8: SYNTHESIZE (all modes, sequential)

Spawn Agent:
- Reads: `phases/08-synthesize.md` + `agents/synthesizer.md`
- Input: ALL workspace file paths, `$WORKSPACE/ideas.csv`
- LITE: Idea Menu only (no proof searches). STANDARD/DEEP: full output + web validation.
- Produces: Idea Menu + proof searches + seed bank → `$WORKSPACE/08-synthesize.md` + `$WORKSPACE/seed-bank.md`

### Phase 9.5: STRESS-TEST (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/09.5-stress-test.md` + `agents/stress-tester.md`
- Input: Idea Menu, ideas.csv, tension analysis, root causes
- STANDARD: top 5, 2 rounds. DEEP: top 8, 3 rounds.
- Produces: confidence adjustments → `$WORKSPACE/09.5-stress-test.md` + updated ideas.csv

### Phase 10: BRILLIANCE (all modes, sequential)

Spawn Agent:
- Reads: `phases/10-brilliance.md` + `agents/brilliance.md`
- Input: Idea Menu, ideas.csv, tensions, stress results (if run), root causes
- Produces: Brilliance Scorecard → appended to `$WORKSPACE/08-synthesize.md`

### Phase 9: CONVERGE (all modes, sequential — runs last)

Spawn Agent:
- Reads: `phases/09-converge.md`
- Input: complete Idea Menu + stress results + brilliance output, all workspace paths
- Produces: filtered 2-3 best-fit ideas, proof search verdicts, user decision
- In DEEP: offers Round 2 option

## Inter-Phase Data Rules

1. **Pass file paths, not content.** Subagents read workspace files directly.
2. **Pass short summaries** (2-5 sentences) between phases for context.
3. **Problem statement** goes to every subagent.
4. **Mandatory output standards** (above) go to every subagent.
5. **`$WORKSPACE` path** goes to every subagent — they use it for all `idea_db.py` commands.
6. **`references/idea-db.md`** path goes to every subagent that writes or reads ideas (Phases 3-10). The CSV is the shared state — agents read and write `$WORKSPACE/ideas.csv` via `python scripts/idea_db.py` commands documented in each phase/agent file.
7. **If a subagent fails**, retry once. If it fails again, skip with a note and continue.

## The Idea Database

Every idea is tracked in `$WORKSPACE/ideas.csv`. See `references/idea-db.md` for commands. Key:
```bash
python scripts/idea_db.py init <ws>                    # create empty DB
python scripts/idea_db.py describe <ws>                # show current schema: columns, types, fill rates
python scripts/idea_db.py add_batch <ws> seeds.json    # bulk add
python scripts/idea_db.py top <ws> ice_score --n 5     # query top
python scripts/idea_db.py export_md <ws>               # markdown export
```

**Every subagent should run `describe` first** to discover which columns exist from prior phases before reading or writing the CSV.
