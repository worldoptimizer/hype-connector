# Start automating Hype

[Download Connector 0.1.12](https://github.com/worldoptimizer/hype-connector/releases/download/v0.1.12/Connector-0.1.12-build78.dmg) for macOS.

Connector adds local automation to the Tumult Hype editor. Build repeatable templates with a script, connect an MCP client, or send operations from AppleScript.

The Connector app installs its plugin inside Hype and manages the connection. Your script or agent sends JSON operations to that running editor. Hype remains a desktop application, including for documents opened without an initial window.

## Requirements

- macOS 14 or later.
- Tumult Hype 4. Compatibility is established with **Hype 4.1.22, build 786**. A newer version is not automatically supported simply because it starts.
- Connector 0.1.12 (app build 78, plugin 0.1.7 build 54).
- An internet connection to start the trial or activate a license.
- Python 3 for the optional example scripts. Connector itself does not require Python.

## Guided setup in Connector 0.1.12

1. Move **Connector.app** into **Applications** and open it. The assistant finds Hype automatically. If asked, choose your Hype installation.
2. In **Connect Hype**, click **Continue**. The correct plugin folder opens directly; click **Allow access**. If Hype has not created its folder yet, Continue opens Hype first. Connector installs its plugin after access is confirmed.
3. Follow the same step until Hype connects. Continue opens Hype if needed. If a running Hype needs to load a different plugin, save your documents, quit and reopen Hype. The assistant advances when it connects. With multiple sessions, choose the one to automate.
4. In **Choose your application**, select **Codex**, **Claude Code**, or **CLI or AppleScript**, then click **Continue**. An agent connection installs MCP and the complete skill together. **Back** retains your selection and completed setup work.
5. Click **Finish**. For an agent client, start a new chat and use **Copy first prompt** to check Hype discovery. Add another client later with **Applications → Connect**. The client's normal tool approvals still apply.

The large navigation buttons stay at the bottom of the assistant. The normal sidebar appears after setup. If you already have plugin build 54, updating from 0.1.11 does not require a Hype restart.

Connector preserves customized skills during updates. If **Connect** finds a different copy of the skill, choose **Connect and keep my skill** or **Replace and keep a backup**.

Setup and the first connection check leave the trial unstarted. When you’re ready to edit, open **License** and start the seven-day trial or activate a paid license.

## Legacy manual setup for Connector 0.1.10

1. Download and open the DMG, copy Connector into Applications, then open Connector.
2. Leave the trial unstarted while setting up the connection. When ready to work with documents, open **License** and choose **Start 7-day trial**, or enter your key and choose **Activate license**. A [€29 one-time license](https://license.maxziebell.de/checkout) covers up to two Macs.
3. Choose Hype's existing `Application Support/Hype` folder when Connector asks. This selection lets Connector install its plugin and find running Hype sessions. Keep the selection so the app can restore access later.
4. Install the bundled Connector plugin. If Hype is already open, save your work and restart Hype when convenient to load it. Connector does not quit Hype for you.
5. Leave Hype running. Scripts can create and save a new document with `document.create`; no manually prepared document is required. When editing an existing document, stop playback and leave its root editing context active.
6. Return to Connector. It connects automatically when there is one reachable Hype. With several, choose by version and open document names. The process ID is available in the connection details.

The installer changes Connector's own plugin. Other installed plugins remain in place. Installing a new plugin on disk does not replace the one already loaded in a running Hype process.

CLI, MCP and AppleScript use the same app license. Start or activate it once in Connector before running automation. The trial and activation require a network connection. A valid signed receipt can support offline use for at most 72 hours, with a normal refresh after 24 hours. See [Trial and license](licensing.md) for refresh, recovery and expiry.

For Codex or Claude Code on 0.1.10, configure the [MCP connection](mcp.md) and [install the agent skill](../skills/README.md) separately.

## Check the connection

In Terminal, list available connections:

```sh
'/Applications/Connector.app/Contents/MacOS/connector' hosts
```

Then inspect the running plugin and its documents:

```sh
'/Applications/Connector.app/Contents/MacOS/connector' capabilities
'/Applications/Connector.app/Contents/MacOS/connector' run '{"op":"document.list"}'
```

The terminal needs its own macOS access. If you prefer to reuse Connector's saved folder selection, send the operation through the app executable:

```sh
'/Applications/Connector.app/Contents/MacOS/ConnectorApp' --run-operation '{"op":"document.list"}'
```

This mode runs without opening another Connector window. If access fails, inspect the [support report](troubleshooting.md#local-support-report) first. Select the folder again only if its saved selection is missing or unusable. A version command alone does not test permission to reach Hype.

## Choose a workflow

| Use case | Start here |
| --- | --- |
| Build the same document repeatedly | [Runnable examples](examples.md) |
| Write your own automation | [CLI and scripting](scripting.md) |
| Let Codex or Claude use the editor | [MCP setup](mcp.md) |
| Integrate a Mac automation | [AppleScript](applescript.md) |
| Diagnose connection or editing errors | [Troubleshooting](troubleshooting.md) |

For a multi-step workflow, work on a fresh copy and keep the selected process and session fixed. Discover the IDs you need from that document. Confirm each result before continuing. These are the foundations used by the included examples.

## Updates

Connector includes signed app updates through GitHub. Choose **Connector → Check for Updates…**, or open **Updates** to manage automatic checks and installation. Version 0.1.3 has no configured update channel and requires a manual upgrade. After Connector restarts, it updates an older installed Connector plugin using your saved Hype folder access. Save your work and restart Hype when convenient to load that plugin. See [Updates](updates.md).

The project website is [worldoptimizer.github.io/hype-connector](https://worldoptimizer.github.io/hype-connector/).
