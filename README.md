# deep-ideation

Multi-agent parallel brainstorming skill for Claude. Specialist agents generate 40-60 seed ideas using SCAMPER, TRIZ, Reverse Brainstorming, and Synectics. Generalist agents ("Johns") then transform those seeds through Disney Creative Strategy spirals in parallel, each constrained to a different temperature zone (FIRE/PLASMA/ICE/GHOST/CHAOS/MIRROR) to prevent convergence. Final output is a scored Idea Menu of Quick Wins, Core Bets, and Moonshots with stress-tested confidence scores.

## Complexity Modes

| Mode | Use case | Time |
|------|----------|------|
| **LITE** | Quick exploration, low stakes | ~30 min |
| **STANDARD** | Most problems (default) | ~90 min |
| **DEEP** | High-stakes, complex problems | Thorough |

## Setup

### Claude Code

```bash
claude install-plugin ydmitry/deep-ideation
```

Or manually:

```bash
git clone https://github.com/ydmitry/deep-ideation.git
cd deep-ideation
claude plugin link .
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "plugins": [
    {
      "name": "deep-ideation",
      "source": "/path/to/deep-ideation"
    }
  ]
}
```

### Claude Cowork

Search for **deep-ideation** in the plugin marketplace and install it.

## Usage

```
/deep-ideation
```

Claude will ask for your problem statement and complexity mode, then orchestrate the full brainstorming pipeline.

## Requirements

- Python 3 (for the idea database script)
