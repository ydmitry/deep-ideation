# Phase 2: ORCHESTRATE

Analyze problem type, set the Ideal Final Result, plan seed distribution, and assign temperature zones.

## Step 1: Classify Problem Type

| Problem Type | Provocateur | Innovator | Wild Card | Connector |
|-------------|-------------|-----------|-----------|-----------|
| Novel/creative | Medium | Low | HIGH | HIGH |
| Technical/product | Medium | HIGH | Medium | Medium |
| Stuck/stagnant | HIGH | Medium | HIGH | Medium |
| High-stakes | HIGH | HIGH | Low | Medium |
| Ambiguous | Medium | Medium | HIGH | HIGH |

Adjust specialist emphasis based on classification. The dominant type determines which agent gets the most seeds distributed to Johns.

## Step 2: Set the Ideal Final Result (TRIZ IFR)

Complete this sentence: "Ideally, the problem solves itself — [describe the perfect outcome with no constraints]."

The IFR is a directional anchor, not a deliverable. Johns use it to check whether their transformed ideas move toward or away from the ideal.

## Step 3: Calibrate ICE Anchors (in advance)

Set the Anchored ICE calibration based on Digger's outputs. Save to `$WORKSPACE/ice-anchors.md`:

```markdown
# ICE Anchors — [Session Name]

Impact anchor:
  10 = fully resolves [deepest root cause]
  5  = addresses one angle partially
  1  = cosmetic improvement only

Confidence anchor:
  10 = direct evidence (case study, prior session data, web validation)
  5  = reasonable assumption, no direct evidence
  1  = pure speculation

Ease anchor:
  10 = done today with existing resources (< 1 hour)
  5  = 1-2 week sprint with current team
  1  = months of work + new capabilities
```

## Step 4: Plan Seed Distribution

Decide how to split seeds across Johns:

- **John A (FIRE / Dreamer-start)**: Wild Card seeds + half Connector seeds → wildest material
- **John B (PLASMA / Realist-start)**: Innovator seeds + half Connector seeds → most systematic material
- **John C (ICE / Critic-start)**: Provocateur seeds + random sample from others → most adversarial material

In DEEP mode with Historian results: distribute Historian seeds to the John whose zone best fits the mechanism (check principle type — TRIZ-type → PLASMA, emotional/analogical → FIRE, risk-focused → ICE).

## Step 5: Note Complexity Mode Adjustments

**LITE mode:**
- Skip this phase — go straight to SEED with Innovator + Wild Card only
- No Johns — Synthesizer gets seeds directly

**STANDARD mode:**
- Run all 4 specialists, all 3 Johns
- Skip Phase 6.5 (Hat Eval) only if user wants faster results

**DEEP mode:**
- Run all phases including Phase 6.5
- Queue Round 2 decision after Phase 9

## Output Requirements

Save orchestration plan to `$WORKSPACE/02-orchestrate.md`. Return a short summary to the orchestrator containing:

1. **Problem type** classification (Novel/Technical/Stuck/High-stakes/Ambiguous)
2. **Specialist emphasis** (which agents get priority based on problem type)
3. **IFR statement** ("Ideally, the problem solves itself — [perfect outcome]")
4. **ICE anchor calibration** saved to `$WORKSPACE/ice-anchors.md`
5. **Seed distribution plan** (which seeds go to which John, with temperature zones)

See `references/output-rules.md` for mandatory idea description and CSV column rules.

## Anti-Patterns
- **Don't use generic ICE anchors** — calibrate to the session's specific root causes
