# deep-ideation

A Claude skill that runs multiple AI agents in parallel to brainstorm ideas at depth. Agents generate, transform, stress-test, and score ideas — producing a prioritized menu of Quick Wins, Core Bets, and Moonshots.

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
