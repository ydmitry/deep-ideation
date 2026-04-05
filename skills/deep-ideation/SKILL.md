---
name: deep-ideation
description: "Multi-agent parallel brainstorming at maximum creative depth. Specialists generate high-volume seed ideas; generalist Johns transform them through Disney spirals using an operations toolkit (SCAMPER, TRIZ Contradiction Engine, Six Hats, Reverse Brainstorming, Synectics). Use whenever the user wants to brainstorm with maximum depth, explore a problem from many angles simultaneously, generate a large volume of diverse ideas, or asks for 'deep ideation', 'multi-agent brainstorm', 'parallel brainstorming', 'swarm brainstorm'. Also use when the user says they want 'lots of ideas', 'explore every angle', or 'think about this from every perspective'."
---

# Deep Ideation v7 — Seed, Transform & Converge

Ideas are first-class citizens. The process has two core stages plus convergence:

1. **SEED** — Specialist agents blast out raw idea seeds using their technique. Fast, high-volume, no filtering.
2. **TRANSFORM** — Generalist agents (Johns) pick up batches of seeds and run Disney spirals, applying operations from a shared toolkit. Slower, deliberate, chain-building.
3. **CONVERGE** — Synthesizer scores, Idea Menu (Quick Wins / Core Bets / Moonshots), Session Seed Bank export.

Specialists are seed factories. Johns are idea refineries. Best of both worlds.

---

## Complexity Modes

Choose before starting. Ask the user if unclear.

| Mode | When to Use | Phases Run | Agents | Expected Time |
|------|------------|-----------|--------|--------------|
| **LITE** | Quick problem, 30-min session, low stakes | 1 → 3 → 8 → 10 | Digger + 2 specialists + Synthesizer + Brilliance | Fast |
| **STANDARD** | Default. Most problems. | 1 → 10 (all phases) | Full roster | Normal |
| **DEEP** | High-stakes, complex, multi-stakeholder | 1 → 10 + Historian + 2nd iterative round | Full roster + Historian + Round 2 | Thorough |

**LITE mode shortcuts:**
- Skip ORCHESTRATE, DISTRIBUTE, BUILD, TENSION
- Run only Innovator + Wild Card in SEED phase
- Synthesizer outputs Idea Menu only (no experiments)

**DEEP mode adds:**
- Historian runs after DISCOVER (cross-session transfer)
- Phase 6.5: Hat Evaluation Pass (Six Hats on top 10 built ideas)
- Round 2: Top 5 from Round 1 become new seeds for a focused second run
- Web validation in Synthesizer (WebSearch)

---

## Workspace Isolation

Every session gets its own timestamped directory to prevent cross-contamination:

```bash
# Create session workspace
WORKSPACE="results/$(date +%Y%m%d-%H%M%S)-$(echo "$PROBLEM" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | head -c 30)"
mkdir -p "$WORKSPACE/seeds"
python scripts/idea_db.py init "$WORKSPACE"
```

All agents read from and write to `$WORKSPACE`. The Historian reads from all previous workspace directories.

---

## The TRIZ Contradiction Engine

Built into the Innovator agent. Every Innovator run now produces a **Contradiction Card**:

### 39 Engineering Parameters (adapted for product/business)
```
1. Weight/payload          11. Stress/load             21. Power/throughput
2. Size/footprint          12. Shape/form               22. Energy loss
3. Speed/velocity          13. Stability                23. Resource loss
4. Force/effort            14. Strength/durability      24. Information loss
5. Area/coverage           15. Reliability              25. Time loss
6. Volume/capacity         16. Accuracy/precision       26. Quantity of content
7. Complexity              17. Temperature/affect       27. Productivity
8. Ease of use             18. Visibility               28. Manufacturability
9. Adaptability            19. User engagement          29. Automation level
10. Novelty                20. Defensibility            30. Cost
```

### 40 Inventive Principles (full reference)
```
1. Segmentation            11. Beforehand cushioning    21. Rushing through
2. Taking out              12. Equipotentiality         22. Convert harm to benefit
3. Local quality           13. Inversion                23. Feedback
4. Asymmetry               14. Curvature/spheroidality  24. Intermediary
5. Merging                 15. Dynamization             25. Self-service
6. Universality            16. Partial action           26. Copying
7. Nesting                 17. Another dimension        27. Cheap short-life objects
8. Anti-weight             18. Mechanical vibration     28. Mechanics substitution
9. Preliminary anti-action 19. Periodic action          29. Pneumatics/hydraulics
10. Prior action           20. Continuous useful action  30. Flexible shells
31. Porous materials       36. Phase transitions
32. Color/optical changes  37. Thermal expansion
33. Homogeneity            38. Strong oxidants
34. Discarding/recovering  39. Inert atmosphere
35. Parameter changes      40. Composite materials
```

**Contradiction Card process (in Innovator):**
1. Identify what you want to IMPROVE (improving parameter)
2. Identify what WORSENS as a result (worsening parameter)
3. Name the tension: "Improving [X] worsens [Y]"
4. Select 3-5 relevant principles from the 40 above
5. Apply each principle to generate a seed

---

## Anchored ICE Scoring

Before scoring, calibrate anchors for THIS session. The Synthesizer asks:

```
Impact anchor:    "10 = fully resolves the deepest root cause Digger found"
Confidence anchor: "10 = we have direct evidence (web research, prior session) this works"
Ease anchor:      "10 = can be done today with existing resources in under an hour"
```

These anchors are recorded in the workspace and all ICE scores reference them.

**Formula:** Score = (Impact × Confidence) / (11 - Ease)

---

## How to Write Idea Descriptions

Every idea description — in seeds, transforms, builds, AND the final CSV — must be written like explaining to a colleague over coffee.

**Rules:**
- 2-3 sentences max
- First sentence: what is it? (the mechanism, with a concrete example)
- Second sentence: why does it matter? (the impact)
- NO jargon, NO internal terminology, NO references to how the idea was generated
- Self-contained: a reader with zero context should understand it

**GOOD:** "Every deliverable on Upwork shows a label indicating what percentage was AI versus human effort. Clients see exactly what they're paying for, and freelancers who add more human judgment can charge premium rates."

**BAD:** "AI composition transparency mechanism addressing trust erosion root cause via disclosure tier framework with dynamic fee incentivization."

This rule applies to ALL agents and ALL phases.

---

## Required Idea Columns

Every idea in the CSV must have these columns filled by the agent that creates it:

| Column | What to Write | Example |
|--------|--------------|---------|
| `description` | 2-3 sentences, coffee-talk style | "Companies post tasks stripped of their name. A freelancer sees 'analyze Q3 revenue for a mid-size SaaS company' instead of 'analyze Stripe's Q3 numbers.'" |
| `pros` | 2-3 concrete advantages | "Zero infrastructure cost. Addresses immediate post-layoff demand. Creates premium pricing tier." |
| `cons` | 2-3 honest risks or downsides | "Hard to maintain anonymity for niche industries. Freelancers may resist not knowing who they work for." |
| `requires` | What must exist first | "Anonymization engine. Legal review. 50+ enterprise pilots." |

These help the reader immediately assess each idea. Agents should fill them honestly — cons are as valuable as pros.

---

## Idea Menu Output Format

The Synthesizer's final output uses three buckets:

### Quick Wins
> High Ease (≥7) + decent Confidence (≥6). Low-hanging fruit. Do these first.

### Core Bets
> High Impact (≥8) + reasonable Confidence (≥5). The main strategic bets.

### Moonshots
> Very High Impact (≥9) + High Novelty (≥8) but lower Confidence (≤5). Worth exploring with experiments.

---

## Session Seed Bank

At session end, the Synthesizer exports a **Seed Bank** — a condensed list of the 10-15 most generative seeds from the session (not final ideas, but the raw seeds that produced the most chains). Saved to `$WORKSPACE/seed-bank.md`.

The Historian uses this in future sessions for cross-domain transfer.

Format:
```markdown
# Seed Bank — [session name] — [date]

| # | Seed | Source Agent | Chains Produced | Principle |
|---|------|-------------|----------------|-----------|
| 1 | [seed] | Provocateur | 3 ideas | [transferable mechanism] |
```

---

## Integrated Seed Triage

After SEED phase (Phase 3), before DISTRIBUTE (Phase 4), do a quick triage. Not just dedup — classify:

| Category | Criteria | Action |
|----------|----------|--------|
| **Hot** | Novel mechanism, surprising framing | Give to 2+ Johns |
| **Warm** | Solid but conventional | Assign to best-fit John |
| **Cold** | Interesting but low-energy | Keep, low priority |
| **Discard** | Near-duplicate of another seed | Drop with note |

Hot seeds = 15-20% of total. If you find fewer than 5 hot seeds, the problem brief may be too narrow.

---

## Iterative Rounds (DEEP mode)

After Phase 9 (CONVERGE), offer the user a second round:

```
AskUserQuestion:
  question: "Round 1 produced [N] ideas. Top 5: [list]. Want a focused Round 2?"
  header: "Go Deeper?"
  options:
    - "Yes — focus on [specific direction]"
    - "Yes — explore a direction Round 1 missed"
    - "No — I have enough to work with"
```

**Round 2 flow:**
1. Top 3-5 from Round 1 become new seeds
2. User-specified new direction becomes a new HMW question
3. Run: Innovator + Connector (specialists only)
4. One John (fresh mode, different from Round 1)
5. Synthesizer produces merged output combining Round 1 + Round 2 ideas

---

## The Idea Database

Every idea is recorded as a row in `$WORKSPACE/ideas.csv`. See `references/idea-db.md`.

**Key commands:**
```bash
python scripts/idea_db.py init <workspace>          # start session
python scripts/idea_db.py add_batch <ws> seeds.json # bulk add seeds
python scripts/idea_db.py add_column <ws> ice_score  # dynamic columns
python scripts/idea_db.py top <ws> ice_score --n 5   # query top ideas
python scripts/idea_db.py export_md <ws>             # markdown table
python scripts/idea_db.py multi_filter <ws> --conditions "feasibility>=7,novelty>=8"
```

---

## The Agents

### Seed Phase (parallel, fast)
| Agent | Technique | Target |
|-------|-----------|--------|
| **Provocateur** | Reverse Brainstorming | 10-15 seeds |
| **Innovator** | SCAMPER + TRIZ Contradiction Card | 12-18 seeds |
| **Wild Card** | Crazy 8s + Random Entry + Personas | 12-18 seeds |
| **Connector** | Full Synectics (4 analogy types) | 10-15 seeds |

### Transform Phase (parallel, deliberate)
| Agent | Temperature Zone | Starting Mode |
|-------|-----------------|--------------|
| **John A** | FIRE — push everything wilder | Dreamer-start |
| **John B** | PLASMA — every idea needs a cross-domain mechanism | Realist-start |
| **John C** | ICE — every idea must pass feasibility check | Critic-start |

### Synthesis Phase (sequential)
| Agent | Role |
|-------|------|
| **Brainwriter** | Builds on top 10 Johns ideas; tracks hot/warm/cold seeds |
| **Tension Analyzer** | Maps contradictions; Bridge ops; PMI |
| **Synthesizer** | Hybrids, Anchored ICE scores, Idea Menu, Seed Bank |
| **Brilliance Filter** | Evaluates top ideas against 7 brilliance questions; separates Brilliant (0-3) from Notable (2-4); writes pitch sentences; classifies durability |

### Support Agents
| Agent | When | Role |
|-------|------|------|
| **Historian** | DEEP mode, after DISCOVER | Cross-session knowledge transfer |

---

## The Flow

```
DISCOVER → ORCHESTRATE → SEED → TRIAGE → DISTRIBUTE → TRANSFORM → BUILD → [6.5 HAT EVAL] → TENSION → SYNTHESIZE → CONVERGE → BRILLIANCE
    ↓           ↓          ↓        ↓         ↓            ↓          ↓           ↓              ↓          ↓           ↓            ↓
  Digger     Blue Hat   4 specs  Hot/Warm/  Assign      3 Johns    Brain-    Six Hats on    Groan    Anchored   Idea Menu    Brilliant
  [+Hist.]   set plan   parallel  Cold/Drop  batches     spiral    writer     Top 10 built   Zone     ICE + Menu  + Seed Bank   Ideas
```

*(Phase 6.5 Hat Eval only in STANDARD and DEEP modes)*

---

## Phase-by-Phase

### Phase 1: DISCOVER (non-negotiable)

See `phases/01-discover.md`. Run Digger first.

In DEEP mode: also run Historian after Digger.

```
AskUserQuestion:
  question: "Root causes found: [summary]. HMW questions: [list]. Ready to launch?"
  header: "Confirm"
  options:
    - "Yes, launch the swarm"
    - "Let me adjust the angles"
```

### Phase 2: ORCHESTRATE

See `phases/02-orchestrate.md`. Classify problem, set IFR, plan distribution.

### Phase 3: SEED (parallel, fast)

See `phases/03-seed.md`. Launch 4 specialists in parallel.

### Phase 3.5: INTEGRATED SEED TRIAGE

See `phases/04-distribute.md` (first half). Classify seeds: Hot / Warm / Cold / Discard.

### Phase 4: DISTRIBUTE

See `phases/04-distribute.md` (second half). Assign triage-classified seeds to Johns.

### Phase 5: TRANSFORM (parallel, deliberate)

See `phases/05-transform.md`. Launch 3 Johns with their temperature zone constraints.

### Phase 6: BUILD

See `phases/06-build.md`. Brainwriter reads all Johns, builds on top 10, tracks seed usage.

### Phase 6.5: HAT EVALUATION PASS (STANDARD + DEEP only)

See `phases/06.5-hat-eval.md`. Run Six Thinking Hats on top 10 built ideas before Tension.

### Phase 7: TENSION

See `phases/07-tension.md`. Contradiction mapping, Bridge ops, PMI.

### Phase 8: SYNTHESIZE

See `phases/08-synthesize.md`. Hybrids, Anchored ICE, Idea Menu, web validation, Seed Bank.

### Phase 9: CONVERGE

See `phases/09-converge.md`. Decision tree, experiment design, decide, optional Round 2.

### Phase 10: BRILLIANCE FILTER

See `phases/10-brilliance.md` and `agents/brilliance.md`. Runs in ALL modes (LITE, STANDARD, DEEP) — it's cheap, just a judgment pass on finished work.

Evaluates the Idea Menu through 7 brilliance questions that ICE scoring can't capture. Produces a Brilliance Scorecard, separates Brilliant (0-3) from Notable (2-4) ideas, and writes a one-sentence pitch for each. Output appended to `$WORKSPACE/08-synthesize.md` as the final section the user reads.

---

## Why This Architecture Works

1. **Volume + Quality**: Specialists give 40-60 seeds. Johns transform the best through 3 modes. You get both.
2. **Structural divergence**: Temperature zones prevent Johns from converging even on identical seeds.
3. **Traceability**: Every final idea has a full chain from seed to final form.
4. **TRIZ gives real contradictions**: The Contradiction Card surfaces the actual tension rather than generic ideas.
5. **Anchored ICE prevents score drift**: Scores calibrated to THIS session's root causes are meaningful.
6. **Idea Menu is action-oriented**: Three buckets map directly to "what do I do first?"
7. **Cross-session transfer**: Historian + Seed Bank means each session builds on all previous work.
8. **Brilliance Filter catches what scoring misses**: ICE rewards feasible impact. Brilliance rewards structural insight — parsimony, surprise, inevitability. An idea that scores 6.0 on ICE but resolves the session's core contradiction in a single mechanism is more valuable than a 9.0 that's a well-executed known pattern.

---

## Anti-Patterns

- **Don't skip DISCOVER** — the divergent 5 Whys + HMW is the single most valuable output
- **Don't let Johns generate from scratch** — they transform SEEDS, not start fresh
- **Don't give all Johns the same seeds** — temperature zones + different batches is what produces divergence
- **Don't skip Seed Triage** — hot seeds are the signal; cold seeds might be hidden gems
- **Don't skip Tension Analysis** — the Groan Zone is where the most surprising ideas emerge
- **Don't use generic ICE anchors** — calibrate to the session's specific root causes
- **Don't skip the Brilliance Filter** — it's the last thing the user reads and often surfaces the session's best insight
- **Don't inflate brilliance** — zero Brilliant ideas is a valid output. If nothing is structurally surprising, say so.
