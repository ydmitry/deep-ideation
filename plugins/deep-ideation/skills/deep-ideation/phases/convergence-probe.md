# Convergence Probe

A lightweight checkpoint that compares the current top-3 ranked ideas to the top-3 from the prior probe. When the top-3 is stable across two consecutive probes, the orchestrator surfaces an early-exit option to the user.

**Runs in:** STANDARD and DEEP modes only. Skip in LITE.

**Probe insertion points** (orchestrator runs this after each of these phases):
- After Phase 6 (BUILD) → Probe 1
- After Phase 8 (SYNTHESIZE) → Probe 2
- After Phase 8.5 (SCORE) → Probe 3

## What the Orchestrator Does (not the subagent)

The orchestrator maintains a running `previous_top3` list across probes. After each target phase completes:

1. Spawn one Agent:
   - Reads: `agents/convergence-checker.md`
   - Input: `$WORKSPACE/ideas.csv` path, `$WORKSPACE` path, probe number, previous top-3 IDs (or empty for Probe 1)
   - Produces: `PROBE_RESULT probe=<N> converged=<true/false> top3=[ID,ID,ID]`

2. Parse the `PROBE_RESULT`:
   - Update `previous_top3` with the returned IDs
   - If `converged: false` → continue to next phase normally

3. **If `converged: true` on two consecutive probes:**
   - Surface an `AskUserQuestion` to the user:

```
The top 3 ideas have been stable for the last two checkpoints:
  1. [Idea Name] — [one-sentence description]
  2. [Idea Name] — [one-sentence description]
  3. [Idea Name] — [one-sentence description]

Would you like to:
  A) Exit now and go straight to CONVERGE with these 3 ideas
  B) Continue the full pipeline (remaining phases: [list])
```

   - If user chooses **A**: pass top-3 IDs directly to Phase 9 (CONVERGE), skip remaining phases, write `phase_status` telemetry for each skipped phase.
   - If user chooses **B**: continue pipeline normally. Do not ask again even if the top-3 stays the same.

## Telemetry for Skipped Phases

When the user exits early, write one line per skipped phase to `$WORKSPACE/telemetry.md`:
```
<phase-name> | STANDARD | skipped | reason=early_exit_convergence
```

## Anti-Patterns
- **Don't offer early exit after only one stable probe** — two consecutive stable probes are required
- **Don't block pipeline progress** — if the probe agent fails, skip it with a note and continue
- **Don't ask again after the user declines** — one offer per run only
