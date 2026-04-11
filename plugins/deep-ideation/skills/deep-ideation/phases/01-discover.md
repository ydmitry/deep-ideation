# Phase 1: DISCOVER (Non-Negotiable)

The Digger runs first, always. Root cause analysis + HMW reframing is the single most valuable output of the entire skill — it determines the quality of everything that follows.

## Step 1: Set Up Workspace

```bash
WORKSPACE="results/$(date +%Y%m%d-%H%M%S)-[slug]"
mkdir -p "$WORKSPACE/seeds"
python scripts/idea_db.py init "$WORKSPACE"
```

Tell the user their session workspace: `Session workspace: $WORKSPACE`

## Step 2: Determine Complexity Mode

If the user hasn't specified, ask:

```
AskUserQuestion:
  question: "How deep should we go?
    LITE: Fast. 30 min. Digger + 2 specialists + quick synthesis.
    STANDARD: Full pipeline. 4 specialists + 3 Johns + synthesis. ~90 min.
    DEEP: Maximum. Full pipeline + cross-session history + web validation + optional Round 2."
  header: "Mode"
  options:
    - "LITE — quick exploration"
    - "STANDARD — full session"
    - "DEEP — maximum depth"
```

## Step 3: Run the Digger

See `agents/digger.md`.

The Digger:
1. Proposes angles to the user — waits for confirmation
2. Runs one 5 Whys chain per confirmed angle (divergent — they MUST arrive at different root causes)
3. Runs divergence check — reruns chains if they converged
4. Writes 4-6 HMW questions (each pointing in a different direction)
5. **Identifies the TRIZ trade-off** — the core contradiction for the Innovator
6. Generates depth-layered ideas (surface/mid/root) per angle

Output saved to `$WORKSPACE/01-discover.md`.

## Step 4: Run the Historian (DEEP mode only)

See `agents/historian.md`.

After Digger completes:
```bash
find results -name "ideas.csv" -type f  # scan all previous sessions
```

The Historian resurfaces relevant ideas from previous sessions and adds up to 15 cross-domain seeds to the Problem Brief.

Output saved to `$WORKSPACE/01-historian.md`.

## Step 5: Confirm and Launch

```
AskUserQuestion:
  question: "Root causes found:
    - [Root Cause A in one sentence]
    - [Root Cause B in one sentence]
    - [Root Cause C in one sentence]

    Core contradiction (for TRIZ): Improving [X] worsens [Y]

    HMW questions:
    1. [HMW 1]
    2. [HMW 2]
    3. [HMW 3]
    4. [HMW 4]

    Ready to launch?"
  header: "Confirm"
  options:
    - "Yes, launch the swarm"
    - "Adjust the angles first"
    - "Change the TRIZ contradiction"
```

## Output Requirements

Save to `$WORKSPACE/01-discover.md`. Return a 3-line receipt to the orchestrator per the **Return Contract** in `references/output-rules.md`.

If Historian ran (DEEP mode), also save `$WORKSPACE/01-historian.md` with up to 15 cross-domain seeds.

See `references/output-rules.md` for mandatory idea description and CSV column rules.

## What Gets Distributed to All Agents

After DISCOVER, every agent receives:
- **Problem statement** (one sentence)
- **Root Cause A, B, C** (one sentence each)
- **HMW questions** (4-6, each pointing in a different direction)
- **TRIZ trade-off** ("Improving X worsens Y")
- **IFR** (Ideal Final Result, set in ORCHESTRATE)
- **Historical seeds** (if Historian ran — DEEP mode)

## Anti-Patterns
- **Don't skip DISCOVER** — the divergent 5 Whys + HMW is the single most valuable output of the entire skill
