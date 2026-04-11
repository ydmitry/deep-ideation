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

## Step 3: Run the Context Scout

**Context Scout** (`agents/context-scout.md`) runs first in all modes (LITE/STANDARD/DEEP).

- The scout identifies the evidence types that matter for this problem, gathers citable facts with epistemic tags, and makes a **best-effort** search for adversarial evidence (counter-evidence, documented failures, regulatory pushback, critical reviews). Adversarial evidence is often unavailable — survivorship bias means most failures aren't documented, and the scout is told not to fabricate to meet a quota.
- Output saved to `$WORKSPACE/00-context.md`.
- The scout writes a stub **only** when the problem is genuinely ungroundable (rare).
- Expect ~1–3 minutes of wall-clock time even in LITE mode (3–5 web searches).

The Digger in Step 4 reads `$WORKSPACE/00-context.md` at its own Step 0 before proposing angles.

## Step 4: Run the Digger

See `agents/digger.md`.

The Digger:
1. Proposes angles to the user — waits for confirmation
2. Runs one 5 Whys chain per confirmed angle (divergent — they MUST arrive at different root causes)
3. Runs divergence check — reruns chains if they converged
4. Writes 4-6 HMW questions (each pointing in a different direction)
5. **Identifies the TRIZ trade-off** — the core contradiction for the Innovator
6. Generates depth-layered ideas (surface/mid/root) per angle

Output saved to `$WORKSPACE/01-discover.md`.

## Step 5: Run the Historian (DEEP mode only)

See `agents/historian.md`.

After Digger completes:
```bash
find results -name "ideas.csv" -type f  # scan all previous sessions
```

The Historian resurfaces relevant ideas from previous sessions and adds up to 15 cross-domain seeds to the Problem Brief.

Output saved to `$WORKSPACE/01-historian.md`.

## Step 6: Confirm and Launch

If `context_facts_count < 5` (below the scout's 5-fact floor), include a **thin-grounding warning** in the confirmation so the user can decide whether to proceed or refine the problem statement. The floor is aspirational — we can't force the scout to invent facts — but the user deserves visibility into how grounded the session actually is.

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

    [IF context_facts_count < 5:]
    Grounding: Scout found [N] cited facts (target was 5). The session
    will proceed on thin grounding — [N] real anchors and priors for the
    rest. If you'd like stronger grounding, refine the problem statement
    to name a specific market, domain, or benchmark the scout can search
    for, and we'll rerun the scout.

    Ready to launch?"
  header: "Confirm"
  options:
    - "Yes, launch the swarm"
    - "Adjust the angles first"
    - "Change the TRIZ contradiction"
    - "Refine the problem and rerun the scout"
```

## Output Requirements

Save to `$WORKSPACE/01-discover.md`. Return a short summary to the orchestrator containing:

1. **Root causes** (3-4, one sentence each — must arrive at different root causes per angle)
2. **HMW questions** (4-6, each pointing in a different direction)
3. **TRIZ trade-off** ("Improving X worsens Y")
4. **Depth-layered ideas** (surface/mid/root per angle)
5. **Complexity mode** selected by the user
6. **Context telemetry** — `context_facts_count` and `adversarial_facts_count` from `$WORKSPACE/00-context.md` header

If Historian ran (DEEP mode), also save `$WORKSPACE/01-historian.md` with up to 15 cross-domain seeds.

See `references/output-rules.md` for mandatory idea description and CSV column rules.

## What Gets Distributed to All Agents

After DISCOVER, every agent receives:
- **Problem statement** (one sentence)
- **Root Cause A, B, C** (one sentence each)
- **HMW questions** (4-6, each pointing in a different direction)
- **TRIZ trade-off** ("Improving X worsens Y")
- **IFR** (Ideal Final Result, set in ORCHESTRATE)
- **`$WORKSPACE/00-context.md`** path — citable facts with epistemic tags (passed to every downstream agent; stub only when the problem is ungroundable)
- **Historical seeds** (if Historian ran — DEEP mode)

## Anti-Patterns
- **Don't skip DISCOVER** — the divergent 5 Whys + HMW is the single most valuable output of the entire skill
