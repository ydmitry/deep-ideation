# Phase 1: DISCOVER (Non-Negotiable)

The Digger runs first, always. Root cause analysis + HMW reframing is the single most valuable output of the entire skill — it determines the quality of everything that follows.

## Step 1: Set Up Workspace

```bash
WORKSPACE="results/$(date +%Y%m%d-%H%M%S)-[slug]"
mkdir -p "$WORKSPACE/seeds"
python scripts/idea_db.py init "$WORKSPACE"
```

Tell the user their session workspace: `Session workspace: $WORKSPACE`

## Step 2: Confirm Complexity Mode

The orchestrator selects the mode before spawning this phase and passes it as input. Use the mode provided. If no mode was passed, default to **LITE**.

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

Save to `$WORKSPACE/01-discover.md`. Return a short summary to the orchestrator containing:

1. **Root causes** (3-4, one sentence each — must arrive at different root causes per angle)
2. **HMW questions** (4-6, each pointing in a different direction)
3. **TRIZ trade-off** ("Improving X worsens Y")
4. **Depth-layered ideas** (surface/mid/root per angle)
5. **Complexity mode** confirmed for this session
6. **`recommended_mode`** — Digger's assessment of the appropriate mode based on problem shape: `LITE` if single-decision with ≤1 contradiction and personal/small-team scope; `STANDARD` if multi-contradiction or corporate/org scope; `DEEP` if high-stakes or complex system. The orchestrator uses this to offer a mid-run downgrade if the problem is simpler than the user selected.

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
