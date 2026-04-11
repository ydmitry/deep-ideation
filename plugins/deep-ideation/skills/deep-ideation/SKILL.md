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

**Every subagent also receives** (in addition to the files listed per phase):
- `references/output-rules.md` — mandatory idea description and CSV column rules
- `references/idea-db.md` — CSV database API (for phases that write/read ideas: 3-10)
- `$WORKSPACE` path — for all file reads/writes and `idea_db.py` commands
- Problem statement (one sentence)

### Phase 1: DISCOVER (all modes, sequential)

Spawn Agent:
- Reads: `phases/01-discover.md` + `agents/digger.md`
- Input: problem statement, user's preferred angles (if any)
- If DEEP: spawn a second Agent reading `agents/historian.md` after Digger completes
- Produces: root causes, HMW questions, TRIZ trade-off, depth-layered ideas, complexity mode → `$WORKSPACE/01-discover.md`
- After: present root causes + HMW to user for confirmation before proceeding

### Phase 2: ORCHESTRATE (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/02-orchestrate.md` + `$WORKSPACE/01-discover.md`
- Input: discover summary (root causes, HMW questions, TRIZ trade-off)
- Produces: problem type, specialist emphasis, IFR, distribution plan → `$WORKSPACE/02-orchestrate.md`

### Phase 3: SEED (all modes, parallel)

Spawn 2-4 Agents simultaneously:
- Each reads: `phases/03-seed.md` + `agents/<specialist>.md`
- LITE: Innovator + Wild Card (2 agents)
- STANDARD/DEEP: Provocateur + Innovator + Wild Card + Connector (4 agents)
- Input: problem brief, root causes, HMW questions, IFR, TRIZ trade-off
- If DEEP: also pass `$WORKSPACE/01-historian.md` (historical seeds)
- Each produces: 10-18 seeds → `$WORKSPACE/seeds/<agent-name>.md` + Idea DB (IDs returned)

### Phase 4: DISTRIBUTE (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/04-distribute.md` + `$WORKSPACE/02-orchestrate.md`
- Input: all seed file paths, mode, problem brief, root causes, HMW questions, IFR, TRIZ trade-off
- Also pass: `references/operations.md` path (included in John packets)
- Produces: triage results (Hot/Warm/Cold/Discard counts), John lineup, distribution plan → `$WORKSPACE/04-distribute.md`

### Phase 5: TRANSFORM (all modes, parallel)

Spawn 2-5 John Agents simultaneously:
- Each reads: `phases/05-transform.md` + `agents/john.md` + `references/operations.md`
- Input per John: **assigned_to value** (e.g. "JohnA"), temperature zone, starting mode, second constraint (if any), TRIZ trade-off
- Each John filters its seeds with: `idea_db.py filter <ws> assigned_to JohnA`
- **LITE fallback:** LITE skips DISTRIBUTE, so `assigned_to` doesn't exist — Johns read all seeds via `filter <ws> phase seed`
- LITE: 2 Johns (FIRE, ICE). STANDARD: 3-4. DEEP: 4-5 (MIRROR runs after others).
- Each produces: 10-15 transformed ideas → `$WORKSPACE/05-john-[a-e].md` + Idea DB (IDs returned)

### Phase 5.5: COLLISION MAP (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/05.5-collision-map.md` + `agents/collision-map.md`
- Input: all John output paths (`$WORKSPACE/05-john-*.md`), `$WORKSPACE/01-discover.md` (TRIZ card + root causes)
- STANDARD: cap at 2 hot zones. DEEP: all zones (max 3).
- Produces: HOT/WARM/COLD zone classification + routing plan → `$WORKSPACE/05.5-collision-map.md`

### Phase 5.7: RATCHET (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/05.7-ratchet.md` + `agents/dialectical-ratchet.md`
- Input: `$WORKSPACE/05.5-collision-map.md` (hot zone details), `$WORKSPACE/01-discover.md` (TRIZ card)
- STANDARD: 2 cycles/zone. DEEP: 3 cycles + full TRIZ.
- Produces: synthesis per hot zone → `$WORKSPACE/05.7-ratchet.md` + Idea DB (IDs returned)

### Phase 6: BUILD (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/06-build.md` + `agents/brainwriter.md`
- Input: all John output paths, `$WORKSPACE/05.7-ratchet.md` (ratchet syntheses)
- Produces: 20-30 enhanced ideas + cross-zone combos + seed usage report → `$WORKSPACE/06-build.md` + Idea DB (IDs returned)

### Phase 6.5: HAT EVAL (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/06.5-hat-eval.md` + `$WORKSPACE/06-build.md`
- Input: top 10 ideas from build phase, `$WORKSPACE/ideas.csv`
- Produces: six-hat analysis, invert candidates, combination suggestions, gut-check ranking, Green Hat seeds (if any) → `$WORKSPACE/06.5-hat-eval.md` + Idea DB (Green Hat seed IDs if any)

### Phase 7: TENSION (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/07-tension.md` + `agents/tension-analyzer.md`
- Input: all John output paths, `$WORKSPACE/06-build.md`, `$WORKSPACE/06.5-hat-eval.md` (if run), `$WORKSPACE/05.5-collision-map.md` (warm zones), `$WORKSPACE/01-discover.md` (TRIZ card)
- Produces: 3-5 tensions + bridges + PMI + deepest tension → `$WORKSPACE/07-tension.md` + Idea DB (bridge idea IDs)

### Phase 8: SYNTHESIZE (all modes, sequential)

Spawn Agent:
- Reads: `phases/08-synthesize.md` + `agents/synthesizer.md`
- Input: ALL workspace file paths, `$WORKSPACE/ideas.csv`
- LITE: hybrids + criteria only (no proof searches). STANDARD/DEEP: full output + web validation.
- Produces: convergent signals, unique gems, hybrids, **evaluation criteria + weights (for Phase 8.5 to apply)**, proof searches, seed bank, qualitative roadmap → `$WORKSPACE/08-synthesize.md` + `$WORKSPACE/seed-bank.md` + Idea DB (hybrid IDs)
- **Does NOT score ideas** — the Scorer (Phase 8.5) applies the criteria.

### Phase 8.5: SCORE (all modes, sequential)

Spawn Agent:
- Reads: `phases/08.5-score.md` + `agents/scorer.md`
- Input: `$WORKSPACE/08-synthesize.md` (criteria + weights), `$WORKSPACE/ideas.csv`, `$WORKSPACE/01-discover.md` (root causes), `$WORKSPACE/07-tension.md` (if exists)
- Produces: ranked Idea Menu, `total_score` and `menu_bucket` (quick_win/core_bet/moonshot/empty) filled in ideas.csv → `$WORKSPACE/08.5-score.md`
- Separation rationale: the agent that generates hybrids (Synthesizer) is different from the agent that ranks them (Scorer). This removes self-scoring bias.

### Phase 9.5: STRESS-TEST (skip in LITE, sequential)

Spawn Agent:
- Reads: `phases/09.5-stress-test.md` + `agents/stress-tester.md`
- Input: `$WORKSPACE/08.5-score.md` (ranked Idea Menu), `$WORKSPACE/ideas.csv`, `$WORKSPACE/07-tension.md` (if exists), `$WORKSPACE/01-discover.md` (root causes)
- STANDARD: top 5 by `total_score`, 2 rounds. DEEP: top 8, 3 rounds.
- Produces: confidence adjustments → `$WORKSPACE/09.5-stress-test.md` + updated ideas.csv

### Phase 10: BRILLIANCE (all modes, sequential)

Spawn Agent:
- Reads: `phases/10-brilliance.md` + `agents/brilliance.md`
- Input: `$WORKSPACE/08.5-score.md` (ranked Idea Menu), `$WORKSPACE/08-synthesize.md` (hybrids + convergent signals), `$WORKSPACE/ideas.csv`, `$WORKSPACE/07-tension.md` (if exists), `$WORKSPACE/01-discover.md` (root causes)
- Produces: Brilliance Scorecard + tier classifications → appended to `$WORKSPACE/08.5-score.md` + updated ideas.csv (brilliance_tier, brilliance_pitch)

### Phase 9: CONVERGE (all modes, sequential — runs last)

Spawn Agent:
- Reads: `phases/09-converge.md`
- Input: `$WORKSPACE/08.5-score.md` (ranked Idea Menu + brilliance), `$WORKSPACE/08-synthesize.md` (hybrids + proof searches), `$WORKSPACE/09.5-stress-test.md` (if run), `$WORKSPACE/ideas.csv`, all workspace paths
- Produces: filtered 2-3 best-fit ideas, proof search verdicts, user decision, Round 2 decision (DEEP) → `$WORKSPACE/09-converge.md` + updated ideas.csv (selected, proof_verdict, user_action)

## Parallel Splitting

When a phase has many ideas to process (50+), the orchestrator can split work across parallel agents using `size` and `slice`:

```bash
# 1. Check how many ideas need processing
python scripts/idea_db.py size $WORKSPACE
# → SIZE: 150, BY_PHASE: seed=44,transform=106

# 2. Split into N agents by ID range
python scripts/idea_db.py slice $WORKSPACE --ids 1-50     # → Agent 1
python scripts/idea_db.py slice $WORKSPACE --ids 51-100    # → Agent 2
python scripts/idea_db.py slice $WORKSPACE --ids 101-150   # → Agent 3

# Or filter by phase first, then split
python scripts/idea_db.py slice $WORKSPACE --phase transform --ids 45-90
```

Pass the `--ids` range to each parallel agent. The agent uses `slice` to read only its batch, processes those ideas, and writes results back using the IDs from the slice output.

**When to split:** Consider parallel agents when a single phase would process 50+ ideas (e.g., scoring 150 ideas in SYNTHESIZE, or running hat eval on many build outputs in DEEP mode).

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
python scripts/idea_db.py top <ws> total_score --n 5   # query top
python scripts/idea_db.py export_md <ws>               # markdown export
```

**Every subagent should run `describe` first** to discover which columns exist from prior phases before reading or writing the CSV.

## Session Telemetry

Track token usage and wall-clock time for every subagent call and append to `$WORKSPACE/telemetry.jsonl`. This powers the Session Cost footer in Phase 9.

**After each Agent call, append one JSON line:**
```json
{"phase": "03-seed:innovator", "tokens": 12400, "duration_ms": 18200, "mode": "STANDARD"}
```

- `phase` — phase ID + agent name (e.g. `"05-transform:john-a"`, `"08-synthesize"`)
- `tokens` — total tokens consumed by that subagent (input + output)
- `duration_ms` — wall-clock milliseconds from spawn to result
- `mode` — `"LITE"`, `"STANDARD"`, or `"DEEP"`

**Bash append pattern:**
```bash
echo '{"phase":"<phase>","tokens":<n>,"duration_ms":<ms>,"mode":"<MODE>"}' >> "$WORKSPACE/telemetry.jsonl"
```

**Historical averages for comparison** (used by Phase 9 cost footer):

| Mode | Typical tokens | Typical duration |
|------|---------------|-----------------|
| LITE | ~200k | ~8 min |
| STANDARD | ~1.1M | ~40 min |
| DEEP | ~2.5M | ~90 min |

Phase 9 reads `telemetry.jsonl` to compute totals and compare against these baselines.
