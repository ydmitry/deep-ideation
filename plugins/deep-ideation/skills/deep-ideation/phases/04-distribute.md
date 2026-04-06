# Phase 4: INTEGRATE SEED TRIAGE + DISTRIBUTE

Two steps: first classify seeds (Triage), then assign them to Johns (Distribute).

---

## Step 1: Read All Seeds

```bash
python scripts/idea_db.py filter <workspace> phase seed
python scripts/idea_db.py stats <workspace>
```

---

## Step 2: Integrated Seed Triage

Not just dedup — classify every seed into one of four categories. This determines distribution priority.

### Triage Categories

| Category | Criteria | Distribution |
|----------|----------|--------------|
| **Hot** | Novel mechanism, surprising framing, crosses domain boundaries, addresses TRIZ trade-off | Give to 2+ Johns |
| **Warm** | Solid idea, conventional framing but valuable direction | Assign to best-fit John |
| **Cold** | Interesting but low-energy, needs a lot of development | Keep, low priority — Wild Card cold seeds get special treatment |
| **Discard** | Near-duplicate of another seed (note the duplicate pair) | Drop, log reason |

### What Makes a Seed "Hot"

A hot seed is one that:
1. Addresses an angle that other seeds miss (unique framing)
2. Contains a transferable mechanism (not surface-level)
3. Directly attacks the TRIZ trade-off
4. Connects two domains nobody else connected
5. Would surprise the user

You should find 5-15 hot seeds per session. If fewer than 5, the problem brief may be too narrow.

### Triage Process

Add a triage column:
```bash
python scripts/idea_db.py add_column <workspace> triage_category --default "warm"
# Set hot/cold/discard for each non-warm seed
python scripts/idea_db.py set <workspace> 7 triage_category hot
python scripts/idea_db.py set <workspace> 23 triage_category discard
```

### Wild Card Cold Seeds

Wild Card cold seeds (too weird for quick classification) get a special flag. The Brainwriter looks at these specifically in Phase 6.

---

## Step 3: Quick Dedup

After triage, remove seeds classified as "discard" and note the duplicate:
- `DISCARD seed #X (duplicate of #Y — [shared concept])`

Do NOT merge seeds that are similar but not identical — they may produce different chains.

---

## Step 4: Determine John Count and Types

Before distributing, decide how many Johns to launch and which temperature zones to use. This scales with complexity mode AND seed count.

### John Count by Mode

| Mode | John Count | Temperature Zones |
|------|-----------|-------------------|
| **LITE** | 2 Johns | FIRE, ICE |
| **STANDARD** | 3-4 Johns | FIRE, PLASMA, ICE + GHOST (if >10 cold seeds) |
| **DEEP** | 4-5 Johns | FIRE, PLASMA, ICE, GHOST, MIRROR |

### John Count by Seed Volume (overrides mode minimum, never reduces below mode minimum)

| Seed Count | Johns |
|-----------|-------|
| <20 seeds | 2 |
| 20-50 seeds | 3 |
| 50+ seeds | 4-5 |

**Multiple Johns of same type:** Allowed. If hot seeds are plentiful, launch 2 FIRE Johns each receiving half the hot seed batch — they'll diverge because seeds differ.

### Budget Constraints (optional second axis)

The Orchestrator may assign budget constraints. If so, pair them with temperature zones:
- Record as `[ZONE] + [$BUDGET]` in the distribution plan
- Example: "John A: FIRE + $0", "John B: PLASMA + $5K"
- If no budget constraint assigned, omit from packets

---

## Step 5: Distribute Seeds to Johns

Assign triage-classified seeds per the Orchestration Plan and John lineup:

**John A (FIRE / Dreamer-start):**
- All Wild Card seeds (hot + warm)
- Half of Connector seeds (favor fantasy + personal analogy seeds)
- Hot seeds from any specialist (hot seeds go to 2+ Johns)
- Historical seeds with emotional/creative mechanisms (DEEP mode)

**John B (PLASMA / Realist-start):**
- All Innovator seeds (hot + warm)
- Half of Connector seeds (favor direct + symbolic analogy seeds)
- Hot seeds from any specialist
- Historical seeds with TRIZ-type mechanisms (DEEP mode)

**John C (ICE / Critic-start):**
- All Provocateur seeds (hot + warm)
- A random sample from other specialists
- Hot seeds from any specialist (hot seeds go to 2+ Johns)
- Historical seeds with risk-inversion mechanisms (DEEP mode)

**John D (GHOST / cold seed specialist) — STANDARD+ when >10 cold seeds, always in DEEP:**
- ALL cold seeds as primary input
- 2-3 hot seeds for contrast (to cross-pollinate with cold seeds)
- No warm seeds — this John exists solely for cold seed rescue

**John E (MIRROR) — DEEP mode only:**
- Same hot seed set as John A
- Must read other Johns' outputs before transforming (runs slightly after others)
- Goal: maximum disagreement for the Collision Map

**Hot seed rule:** Every hot seed goes to at least 2 Johns — different temperature zones produce different transformations of the same hot seed.

### Cold Seed Injection

During distribution, sneak 2-3 random Cold seeds into EACH regular John's batch alongside their hot/warm seeds. Do NOT label them as cold in the packet — let Johns transform them without prejudice. This gives cold seeds a second chance through every temperature zone.

Exception: If a GHOST John exists, GHOST gets all cold seeds. Only inject 2-3 cold seeds into non-GHOST Johns' packets when GHOST is NOT present.

### Recording Distribution
```bash
python scripts/idea_db.py add_column <workspace> assigned_to
# Set values: JohnA, JohnB, JohnC, JohnD, JohnE, JohnAB, JohnBC, JohnAC, JohnABC, etc.
python scripts/idea_db.py add_column <workspace> john_zone
# Set zone: FIRE, PLASMA, ICE, GHOST, CHAOS, MIRROR
python scripts/idea_db.py add_column <workspace> john_budget
# Set budget: $0, $5K, $50K+, none
```

---

## Each John's Packet

Every John receives:
1. Their assigned seed batch (triage categories NOT shown — cold seeds injected without label)
2. Problem Brief (problem statement + root causes)
3. HMW questions
4. TRIZ trade-off + the Innovator's trade-off question
5. IFR statement
6. Operations toolkit reference (`references/operations.md`)
7. Their temperature zone constraints
8. Their budget constraint (if assigned)
9. ICE anchor calibration (`$WORKSPACE/ice-anchors.md`)

Save distribution plan to `$WORKSPACE/04-distribute.md`. Include: John count, zones assigned, budget constraints if any, seed counts per John.
