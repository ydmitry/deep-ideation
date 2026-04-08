# deep-ideation

A Claude plugin that runs multiple AI agents in parallel to brainstorm ideas at depth. Agents generate, transform, stress-test, and score ideas — producing a prioritized shortlist of the most promising ideas.

## Setup

### Claude Desktop

Works in both **Chat** and **Cowork** modes — the plugin installs once and is available everywhere.

**In Chat mode:**

1. Click **Customize** in the left sidebar
2. Open the **Directory** and select the **Plugins** tab
3. Switch to the **Personal** tab, click **"+"** → **Add marketplace**
4. Enter `ydmitry/deep-ideation` and click **Sync**

**In Cowork mode:**

1. Click **Customize** in the left sidebar
2. Next to **Personal plugins**, click **"+"** → **Add marketplace**
3. Enter `ydmitry/deep-ideation` and click **Sync**

**Upload manually:**

1. Go to [github.com/ydmitry/deep-ideation](https://github.com/ydmitry/deep-ideation) → green **Code** button → **Download ZIP**
2. Rename the file from `.zip` to `.plugin`
3. In the same plugin menu above, choose **Upload plugin** instead and select the file

### Claude Code (CLI)

```shell
/plugin marketplace add ydmitry/deep-ideation
/plugin install deep-ideation@ydmitry-deep-ideation
```

Or from a local clone:

```bash
git clone https://github.com/ydmitry/deep-ideation.git ~/deep-ideation
claude --plugin-dir ~/deep-ideation
```

## Usage

Ask Claude to brainstorm using deep ideation, or invoke the skill directly:

```
/deep-ideation
```

Claude will ask for your problem statement and complexity mode, then orchestrate the full brainstorming pipeline.

## Requirements

- Python 3 (for the idea database script)
