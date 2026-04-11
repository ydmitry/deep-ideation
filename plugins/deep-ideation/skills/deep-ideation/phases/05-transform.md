# Phase 5: TRANSFORM (Parallel, Deliberate)

Launch N Johns simultaneously — the exact count and zones are determined by Phase 4 (DISTRIBUTE). Each reads `agents/john.md` + their seed batch + their temperature zone constraints.

## Launch Instructions

Check `$WORKSPACE/04-distribute.md` for:
- How many Johns to launch (2-5 depending on mode and seed count)
- Which temperature zone each John is assigned
- Whether any John has a budget constraint

Each John gets:
- Their specific seed batch (from Phase 4 — cold seeds injected unlabeled)
- Their starting mode: `[STARTING_MODE]`
- Their temperature zone: `[ICE/FIRE/PLASMA/GHOST/CHAOS/MIRROR]`
- Their second constraint (if assigned): `[axis: value]` — e.g., "budget: $0", "time: this week"
- Operations toolkit: `references/operations.md`
- ICE anchors: `$WORKSPACE/ice-anchors.md`
- The TRIZ trade-off question (from Innovator)

### Reading Your Seed Batch from CSV

Each John reads ONLY its assigned seeds — not the full CSV:

```bash
# First, check the schema to see if assigned_to column exists
python scripts/idea_db.py describe <workspace>

# Check how many seeds total
python scripts/idea_db.py size <workspace>

# Read only YOUR assigned seeds (Phase 4 set assigned_to for each seed)
python scripts/idea_db.py filter <workspace> assigned_to JohnA
# Or for seeds assigned to multiple Johns:
python scripts/idea_db.py filter <workspace> assigned_to JohnAB
```

**LITE mode fallback:** LITE skips Phase 4 (DISTRIBUTE), so the `assigned_to` column won't exist. If `describe` shows no `assigned_to` column, read ALL seeds instead:

```bash
# LITE mode: no assigned_to column — read all seeds
python scripts/idea_db.py filter <workspace> phase seed
```

Use the IDs from this output as your source seeds. Every transformed idea must trace back to one of these seed IDs via the `source_seed` field.

**Special launch order:** MIRROR zone Johns must launch AFTER other Johns have produced Mode 1 output, so they can read it first.

## Temperature Zone Recap (HARD CONSTRAINTS)

**FIRE zone (Dreamer-start):**
- Every idea must be pushed one step wilder before advancing
- Output: 70%+ [BOLD] or [WILD]
- Seeds that stay [SAFE] after transformation are rejected

**PLASMA zone (Realist-start):**
- Every idea must reference a mechanism from a different domain
- Output: 50%+ ideas with explicit cross-domain mechanisms
- Ideas without an external mechanism reference are rejected

**ICE zone (Critic-start):**
- Every idea must pass "could we try this next week?"
- Output: 70%+ [SAFE]
- Ideas scoring below 5/10 on weekly feasibility are inverted, not advanced

**GHOST zone (cold seed specialist):**
- Primary input: all cold seeds from triage
- Apply SCAMPER Reverse and TRIZ Inversion to every seed
- Goal: rescue the hidden gems in what everyone dismissed
- Flag every rescued cold seed as `[COLD SEED RESCUED]`

**CHAOS zone (unconstrained):**
- No zone constraints — follow any chain that seems surprising
- Mix of hot, warm, and cold seeds
- Only rule: don't be boring

**MIRROR zone (disagreement maximizer):**
- Read other Johns' Mode 1 outputs before transforming
- Argue the opposite of every direction they took
- Output must directly contradict at least 60% of other Johns' directions

## Disney Spiral

Each John does three rotations on their seeds:

```
Mode 1 (starting mode) → pick top 3-5 → Mode 2 → pick top 2-3 → Mode 3 → Final Top 5
```

Full operation chains documented. Every idea traces back to its original seed.

## Expected Output

Output scales with John count. Per John: 10-15 ideas.

| John Count | Min Ideas | Max Ideas |
|-----------|-----------|-----------|
| 2 Johns | 20 | 30 |
| 3 Johns | 30 | 45 |
| 4 Johns | 40 | 60 |
| 5 Johns | 50 | 75 |

Each John saves to:
- `$WORKSPACE/05-john-[a/b/c/d/e].md` — full output with chains
- Idea DB via commands below

### Writing to the Idea Database

```bash
# First, discover current schema
python scripts/idea_db.py describe <workspace>

# Add columns for this phase (idempotent — safe if already exists)
python scripts/idea_db.py add_column <workspace> temperature_zone
python scripts/idea_db.py add_column <workspace> second_constraint --default "none"
python scripts/idea_db.py add_column <workspace> triz_status --default ""

# Add all transformed ideas as new rows
# The output will print IDs: 15,16,17,... — use these for set calls below
python scripts/idea_db.py add_batch <workspace> john-[a]-ideas.json
# JSON format: [{"name":"...","description":"...","source_agent":"John A","source_seed":"3","chain":"SEED #3 → ...","tag":"BOLD","phase":"transform"}]

# Set zone + constraint + triz_status on each added idea using returned IDs
python scripts/idea_db.py set <workspace> <id> temperature_zone "FIRE"
python scripts/idea_db.py set <workspace> <id> second_constraint "budget:$0"
python scripts/idea_db.py set <workspace> <id> triz_status "resolves"
```

## TRIZ Trade-Off Engagement

Each John should explicitly answer the trade-off question from the Innovator:
> "Does your best transformed idea RESOLVE the contradiction [X vs Y], PICK A SIDE, or SIDESTEP it?"

Record in the DB using the `triz_status` column: `resolves` / `picks_side` / `sidesteps`

## While Running

Tell the user: "[N] Johns are transforming seeds in parallel using Disney spirals (zones: [list of zones]). Expected: [N×10]-[N×15] transformed ideas."

## Anti-Patterns
- Don't always launch exactly 3 Johns — scale with complexity mode and seed count
- Don't let Johns generate from scratch — every idea must trace to a seed
- Don't ignore the temperature zone constraint — it's what produces structural divergence
- Don't compress the chain — full chain documentation is required for Brainwriter + Synthesizer
- Don't launch MIRROR zone before others have Mode 1 output — it needs something to argue against

## Return

Follow the **Return Contract** in `references/output-rules.md`.
