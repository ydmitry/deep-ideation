---
name: deep-ideation
description: "Multi-agent parallel brainstorming at maximum creative depth. Specialists generate high-volume seed ideas; generalist Johns transform them through Disney spirals using an operations toolkit (SCAMPER, TRIZ Contradiction Engine, Six Hats, Reverse Brainstorming, Synectics). Use whenever the user wants to brainstorm with maximum depth, explore a problem from many angles simultaneously, generate a large volume of diverse ideas, or asks for 'deep ideation', 'multi-agent brainstorm', 'parallel brainstorming', 'swarm brainstorm'. Also use when the user says they want 'lots of ideas', 'explore every angle', or 'think about this from every perspective'."
---

# Deep Ideation v9 — Orchestrator Architecture

You are a lightweight orchestrator. You do NOT read phase files or agent files yourself. You spawn a fresh subagent for each phase — each reads only its own instructions and produces output to the workspace.

## Flags

| Flag | Effect |
|------|--------|
| `--no-checkpoints` | Skip all three user checkpoint gates silently. Log skips to workspace. Use for fully autonomous runs. |

## Complexity Modes

Choose before starting. Ask the user if unclear.

| Mode | When to Use | Phases Run | Specialists | Johns |
|------|------------|-----------|-------------|-------|
| **LITE** | Quick problem, 30-min session | 1 → 3 → 8 → 9 → 10 | Innovator + Wild Card | 2 (FIRE, ICE) |
| **STANDARD** | Default. Most problems. | All phases including 9.5 | All 4 specialists | 3-4 (FIRE, PLASMA, ICE + GHOST if >10 cold) |
| **DEEP** | High-stakes, complex | All phases + Historian + Round 2 | All 4 + Historian | 4-5 (FIRE, PLASMA, ICE, GHOST, MIRROR) |

**LITE skips:** ORCHESTRATE, DISTRIBUTE, BUILD, TENSION, COLLISION MAP, RATCHET, HAT EVAL, STRESS-TEST.
**DEEP adds:** Historian after DISCOVER, full Collision Map (all zones), Ratchet (3 cycles), Hat Eval, Round 2 option.

**Checkpoint behavior by mode:**

| Checkpoint | LITE | STANDARD | DEEP | `--no-checkpoints` |
|-----------|------|----------|------|--------------------|
| Framing Gate (after Phase 1) | Shown, skippable | Required | Required | Skipped silently |
| Taste Check (Phase 5.8) | Skipped | Shown, required | Shown, required | Skipped silently |
| Criteria Gate (after Phase 8a) | Skipped | Required | Required | Skipped silently |

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

Phase 1 runs two agents in sequence, then optionally a third:

1. **Context Scout** (first) — Reads: `agents/context-scout.md`; Input: problem statement, `$WORKSPACE` path; Produces: `$WORKSPACE/00-context.md` with citable facts tagged for confidence and (best-effort) adversarial evidence. Runs in **all modes**. Writes a stub only when the problem is truly ungroundable. Adds ~1–3 min of web-search wall-clock even in LITE mode.
2. **Digger** (second) — Reads: `phases/01-discover.md` + `agents/digger.md` + `$WORKSPACE/00-context.md`. Digger's Step 0 consumes the Scout's output before proposing angles.
3. **Historian** (DEEP mode only, after Digger) — Reads: `agents/historian.md`. → `$WORKSPACE/01-historian.md`. Any historical seeds it surfaces inherit grounding downstream when Phase 3 specialists embed cited facts into their batches.

If Context Scout fails entirely, write a one-line stub to `$WORKSPACE/00-context.md` noting the session is operating on priors, then proceed to Digger normally.

- Digger produces: root causes, HMW questions, TRIZ trade-off, depth-layered ideas, complexity mode → `$WORKSPACE/01-discover.md`
- **Telemetry:** read `context_facts_count` and `adversarial_facts_count` from `$WORKSPACE/00-context.md` header and include in session summary

**Scout vs Synthesize proof searches:** Phase 8 Synthesize performs its own web searches to validate top ideas. The two are complementary, not redundant — Scout's grounding is *broad* (problem-space, run before any ideas exist); Synthesize's is *narrow* (idea-specific, run against concrete candidates). Scout asks "what does reality look like here?"; Synthesize asks "does this specific idea hold up?"

### Framing Gate (orchestrator, between Phase 1 and Phase 2)

**Do NOT spawn a subagent.** The orchestrator reads `$WORKSPACE/01-discover.md` and `$WORKSPACE/00-context.md` (header telemetry), then calls `AskUserQuestion` directly.

**Skip if:** `--no-checkpoints` flag is set. In LITE mode, include "Skip" as an option.

`AskUserQuestion` accepts 2–4 discrete options plus auto-provided "Other" for free-text edits. Keep the options tight — common accept/reject — and route nuanced edits through "Other".

```
AskUserQuestion:
  question: "Root causes found:
    - [Root Cause A]
    - [Root Cause B]
    - [Root Cause C]

    Core contradiction: Improving [X] worsens [Y]

    HMW questions:
    1. [HMW 1]
    2. [HMW 2]
    3. [HMW 3]
    4. [HMW 4]

    [IF context_facts_count < 5:]
    Grounding: Context Scout found [N] cited facts (target was 5). The
    session will proceed on thin grounding. Consider refining the
    problem statement (via 'Other') to name a specific market, domain,
    or benchmark the scout can search for, and we'll rerun it.

    Confirm to launch the swarm, or use 'Other' to edit the framing."
  header: "Confirm Framing"
  multiSelect: false
  options:
    - "Yes, launch the swarm"
    - "I want to edit the framing"   # routes user to 'Other' for free-text edits
```

Parse the response:
- "Yes, launch the swarm" → proceed to Phase 2.
- "Other" / "edit the framing" text → classify the edit:
  - Root cause or HMW rewording → update `$WORKSPACE/01-discover.md`, then proceed.
  - TRIZ contradiction change → update `$WORKSPACE/01-discover.md`, then proceed.
  - New problem statement → re-run Phase 1 (Scout + Digger) with the new statement.
  - Refined problem for better grounding → re-run Context Scout only, update `$WORKSPACE/00-context.md`, then re-present the Framing Gate.

**LITE mode override:** When mode is LITE, treat any "Other" response as Skip and proceed without re-running anything. Log skip reason.

Log checkpoint result to workspace: `Framing Gate: confirmed / edited / reframed / rescouted / skipped`.

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
- Input: problem brief, root causes, HMW questions, IFR, TRIZ trade-off, `$WORKSPACE/00-context.md` path
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

### Phase 5.8: TASTE CHECK (skip in LITE, orchestrator gate)

**Do NOT spawn a subagent.** The orchestrator reads the idea DB and calls `AskUserQuestion` directly. See `phases/05.8-taste-check.md` for the full procedure.

**Skip if:** `--no-checkpoints` is set, OR mode is LITE.

Quick steps:
1. Read top 10 transform-phase ideas by diversity: `python scripts/idea_db.py show <ws> --columns "id,name,description,temperature_zone,tag"`
2. Pick 10 spanning multiple zones and tags.
3. Present via `AskUserQuestion` — user picks any that resonate.
4. Record favorites: `python scripts/idea_db.py add_column <ws> user_favorites --default ""` then `python scripts/idea_db.py mark_favorites <ws> --ids "1,3,7"`
5. Save results to `$WORKSPACE/05.8-taste-check.md`.

Log checkpoint result: `Taste Check: N favorites recorded / no favorites / skipped`.

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

### Phase 8a: CRITERIA (all modes, sequential)

Spawn Agent:
- Reads: `phases/08a-criteria.md` + `agents/synthesizer.md`
- Input: ALL workspace file paths, `$WORKSPACE/ideas.csv`
- Produces: 5-7 evaluation criteria + weights summing to 100% → `$WORKSPACE/criteria.json`
- **Does NOT produce hybrids** — that is Phase 8b's job.

### Criteria Gate (orchestrator, between Phase 8a and Phase 8b)

**Do NOT spawn a subagent.** The orchestrator reads `$WORKSPACE/criteria.json` and calls `AskUserQuestion` directly.

**Skip if:** `--no-checkpoints` is set, OR mode is LITE (proceed straight to Phase 8b using criteria as-is).

`AskUserQuestion` is limited to 2–4 discrete options plus an auto-provided "Other" for free-text input. Use discrete options for the common defaults; rely on "Other" for custom weight/criterion edits.

```
AskUserQuestion:
  question: "Proposed evaluation criteria:
    1. [criterion_name] — [description] (weight: X%)
    2. [criterion_name] — [description] (weight: Y%)
    ...
    Total: 100%

    Accept these as-is, or use 'Other' to describe changes
    (e.g. 'drop novelty', 'feasibility:30,novelty:20,impact:50',
    'add security with weight 15')."
  header: "Evaluation Criteria"
  multiSelect: false
  options:
    - "Accept — use these criteria as-is"
    - "I want to adjust them"   # routes user to 'Other' free-text input
```

If the user picks "Accept", use `criteria.json` as-is. If the user picks "adjust" or types changes via "Other", parse the free-text edit, normalize weights to 100%, and write the confirmed criteria back to `$WORKSPACE/criteria.json`. Then register criteria columns:

```bash
python scripts/idea_db.py add_criteria <workspace> \
  --criteria "feasibility,novelty,[session-criteria]" \
  --composite "total_score"
```

Log checkpoint result: `Criteria Gate: accepted / adjusted / skipped`.

### Phase 8b: HYBRIDIZE (all modes, sequential)

Spawn Agent:
- Reads: `phases/08b-hybridize.md` + `agents/synthesizer.md`
- Input: ALL workspace file paths, `$WORKSPACE/ideas.csv`, **`$WORKSPACE/criteria.json`** (confirmed criteria), `$WORKSPACE/05.8-taste-check.md` (if exists)
- LITE: hybrids + seed bank only (no proof searches). STANDARD/DEEP: full output + web validation.
- Produces: convergent signals, unique gems, hybrids, proof searches, seed bank → `$WORKSPACE/08-synthesize.md` + `$WORKSPACE/seed-bank.md` + Idea DB (hybrid IDs)
- **Does NOT score ideas** — the Scorer (Phase 8.5) applies the criteria.
- **Note on favorites:** Phase 8b does NOT manually boost favorites. The +10% boost is applied mechanically by Phase 8.5's `compute_composite` via the `favorites_multiplier` column (set by Phase 5.8 `mark_favorites`). Phase 8b may *reference* favorites when selecting cross-zone clusters, but the quantitative boost is enforced in the scoring pipeline, not in prompt instructions.

### Phase 8.5: SCORE (all modes, sequential)

Spawn Agent:
- Reads: `phases/08.5-score.md` + `agents/scorer.md`
- Input: `$WORKSPACE/criteria.json` (confirmed criteria + weights), `$WORKSPACE/08-synthesize.md`, `$WORKSPACE/ideas.csv`, `$WORKSPACE/01-discover.md` (root causes), `$WORKSPACE/07-tension.md` (if exists), `$WORKSPACE/05.8-taste-check.md` (if exists)
- Produces: ranked Idea Menu, `total_score`, `composite_score` (= `total_score * stress_multiplier * brilliance_multiplier * favorites_multiplier`), `z_score`, `menu_bucket` filled in ideas.csv → `$WORKSPACE/08.5-score.md`
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
7. **`$WORKSPACE/00-context.md`** is the shared grounding artifact written by the Context Scout in Phase 1. The primary consumers are **Digger** (Phase 1), **Phase 3 specialists**, and **Converge** (Phase 9) — each has explicit instructions on how to weight and cite facts. Other phases may access the file if they need grounding, but no other phase is required to branch on it. Consumers check `context_facts_count` to decide whether grounding is available.
8. **If a subagent fails**, retry once. If it fails again, skip with a note and continue.

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
