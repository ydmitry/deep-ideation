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

## Step 4: Distribute to Johns

Assign triage-classified seeds per the Orchestration Plan:

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

**Hot seed rule:** Every hot seed goes to at least 2 Johns — different temperature zones will produce different transformations of the same hot seed.

### Recording Distribution
```bash
python scripts/idea_db.py add_column <workspace> assigned_to
# Set values: JohnA, JohnB, JohnC, JohnAB, JohnBC, JohnAC, JohnABC
```

---

## Each John's Packet

Every John receives:
1. Their assigned seed batch (with triage categories noted)
2. Problem Brief (problem statement + root causes)
3. HMW questions
4. TRIZ trade-off + the Innovator's trade-off question
5. IFR statement
6. Operations toolkit reference (`references/operations.md`)
7. Their temperature zone constraints
8. ICE anchor calibration (`$WORKSPACE/ice-anchors.md`)

Save distribution plan to `$WORKSPACE/04-distribute.md`.
