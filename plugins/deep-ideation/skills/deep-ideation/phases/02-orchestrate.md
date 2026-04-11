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

## Step 3: Plan Seed Distribution

Decide how to split seeds across Johns:

- **John A (FIRE / Dreamer-start)**: Wild Card seeds + half Connector seeds → wildest material
- **John B (PLASMA / Realist-start)**: Innovator seeds + half Connector seeds → most systematic material
- **John C (ICE / Critic-start)**: Provocateur seeds + random sample from others → most adversarial material

In DEEP mode with Historian results: distribute Historian seeds to the John whose zone best fits the mechanism (check principle type — TRIZ-type → PLASMA, emotional/analogical → FIRE, risk-focused → ICE).

## Step 4: Detect Run Scope

Determine whether this is a **personal** or **corporate / strategic** run.

**Corporate / strategic signals:**
- User mentions go-to-market, pricing, segments, sales motion, market entry, competitive positioning, or business model
- Problem framing involves a company, product, or service targeting customers
- Problem type classified as High-stakes or Ambiguous with business context

**Personal signals:**
- Problem is individual (career, creativity, personal decision, consumer product idea)
- No mention of buyers, segments, pricing, or business mechanics

Save the scope to the orchestration plan: `scope: personal | corporate | strategic`

**If scope = `corporate` or `strategic`:**
- Include the **Market Analyst** specialist in Phase 3 (alongside the existing four specialists)
- The Market Analyst seeds segment choice, pricing model, packaging, sales motion, and competitive positioning
- All specialists are instructed to populate economics columns (`segment_shift`, `pricing_shift`, `revenue_model`, `unit_economics_note`) when relevant — the Market Analyst initializes these columns

**If scope = `personal` or LITE mode:**
- Skip the Market Analyst — go-to-market dimensions are not relevant

## Step 5: Note Complexity Mode Adjustments

**LITE mode:**
- Skip this phase — go straight to SEED with Innovator + Wild Card only
- No Johns — Synthesizer gets seeds directly
- Market Analyst is never included in LITE mode

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
4. **Seed distribution plan** (which seeds go to which John, with temperature zones)
5. **Run scope** (personal / corporate / strategic) and whether Market Analyst is included

See `references/output-rules.md` for mandatory idea description and CSV column rules.
