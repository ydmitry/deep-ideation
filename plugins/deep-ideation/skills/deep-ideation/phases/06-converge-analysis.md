# Phase 6: CONVERGENCE ANALYSIS

**Runs in:** STANDARD mode as a single collapsed phase. Skip in LITE. In DEEP mode, use separate phases 05.5, 05.7, 06.5, and 07 instead.

This phase folds four formerly separate steps — Collision Map, Dialectical Ratchet, Hat Evaluation, and Tension Analysis — into a single subagent pass over a shared idea cohort. Each prior step would have re-loaded and re-ranked the same ~20 ideas independently; this phase does them in sequence with no redundant re-processing.

## When It Runs

After Phase 5 (TRANSFORM) — all Johns have finished.
Before Phase 6 (BUILD, `06-build.md`) — ratchet syntheses and tension bridges feed into the Brainwriter.

## What It Receives

- All Johns' complete output paths (`$WORKSPACE/05-john-*.md`)
- TRIZ Contradiction Card and root causes from `$WORKSPACE/01-discover.md`
- `$WORKSPACE/ideas.csv` (transform-phase ideas)

## What It Does (four sub-steps, one agent)

### Sub-step 1 — Collision Map

Classify every sub-problem across John outputs into HOT / WARM / COLD zones (cap at 2 hot zones for STANDARD).

Output: zone table + hot zone details (Side A, Side B, core question, TRIZ connection).

### Sub-step 2 — Dialectical Ratchet (one cycle per hot zone)

For each hot zone: thesis → antithesis → synthesis. One cycle only in STANDARD (not three). If synthesis is "a bit of both," run one more cycle max, then flag UNRESOLVED.

Add ratchet syntheses to Idea DB as new rows (phase=ratchet).

```bash
python scripts/idea_db.py add_column <workspace> ratchet_cycle --default ""
python scripts/idea_db.py add_batch <workspace> ratchet-syntheses.json
# JSON: [{"name":"...","description":"...","source_agent":"Ratchet","chain":"Zone: [X] — Thesis→Antithesis→Synthesis","tag":"BOLD","phase":"ratchet"}]
```

**Deduplication:** ideas already in the DB are referenced by their existing ID, not re-added. Run `describe` to check what already exists.

### Sub-step 3 — Hat Pass (condensed)

Apply six hats to the top 10 ideas from Phase 5 (and ratchet syntheses). One bullet per hat is enough — do not write paragraphs.

Focus on:
- **Black Hat**: identify invert candidates
- **Green Hat**: surface combination suggestions
- **Red Hat**: gut-check ordering (becomes divergence signal for the convergence probe)

Record per idea:
```bash
python scripts/idea_db.py add_column <workspace> hat_red --default ""
python scripts/idea_db.py add_column <workspace> hat_black_invert --default "no"
python scripts/idea_db.py set <workspace> <id> hat_red "exciting"
python scripts/idea_db.py set <workspace> <id> hat_black_invert "yes"
```

If Green Hat surfaces new seeds, add them to DB (phase=hat_eval).

### Sub-step 4 — Tension Log

Focus only on **warm zones** from sub-step 1. (Hot zones are resolved by the Ratchet above.)

For each warm zone: identify 1-2 bridge ideas that honor both sides. Add bridges to DB (phase=tension).

Also produce:
- PMI on top 5 ideas
- TRIZ trade-off status per idea
- One named "deepest tension" for the Synthesizer

```bash
python scripts/idea_db.py add_column <workspace> triz_status --default ""
python scripts/idea_db.py set_batch <workspace> triz-status.json
python scripts/idea_db.py add_batch <workspace> bridge-ideas.json
# JSON: [{"name":"...","description":"...","source_agent":"Tension Analyzer","chain":"Tension: [X vs Y] → Bridge","tag":"BOLD","phase":"tension"}]
```

## Convergence Variance

After sub-step 3 (Hat Pass), compute and record a **disagreement variance** value:

- Count ideas where FIRE John and ICE John diverged sharply in Red Hat gut score (scale: 1-5, variance = std dev across Johns)
- Record `convergence_variance: <float>` in the phase output

This value feeds the convergence-probe condition for conditional Stress-Test skip.

## What It Produces

Save to `$WORKSPACE/06-converge-analysis.md` with four labeled sections:

```markdown
## Collision Map
[zone table]

## Ratchet Syntheses
[per hot zone: thesis / antithesis / synthesis]

## Hat Pass Summary
[per-idea bullet table: RED | BLACK_INVERT | GREEN combos]

## Tension Log
[tensions + bridges + PMI + deepest tension]

## Convergence Variance
convergence_variance: <float>
surviving_candidates: <N>
```

Also write a `phase_status` row to telemetry:
```
phase: 06-converge-analysis | mode: STANDARD | status: completed | candidates: <N> | convergence_variance: <float>
```

## Observability

Write one line to `$WORKSPACE/telemetry.md` (create if absent):
```
06-converge-analysis | STANDARD | completed | surviving=<N> | variance=<float>
```

## Tell the User

"Convergence Analysis complete:
- [N] HOT zones ratcheted ([N] strong syntheses, [N] UNRESOLVED)
- [N] WARM zones logged → [N] bridge ideas added
- [N] invert candidates flagged by Black Hat
- Convergence variance: [float] ([high/low] disagreement)"

## Deduplication Rule

Any idea that was already added to the DB in a prior sub-step is referenced by its existing ID in subsequent sub-steps. Do NOT re-add. Check with:
```bash
python scripts/idea_db.py filter <workspace> phase ratchet
python scripts/idea_db.py filter <workspace> phase tension
```

## Anti-Patterns
- **Don't re-debate hot zones in the Tension Log** — the Ratchet already resolved them
- **Don't write paragraphs per hat** — one bullet is enough; the Synthesizer does the deep work
- **Don't compromise in the Ratchet** — if the synthesis is just "a bit of both," run one more cycle, not five
