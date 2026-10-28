# Start automating Hype

[Download Connector 0.1.6](https://github.com/worldoptimizer/hype-connector/releases/download/v0.1.6/Connector-0.1.6-build47.dmg) for macOS.

Connector adds local automation to the Tumult Hype editor. Build repeatable templates with a script, connect an MCP client, or send operations from AppleScript.

The Connector app installs its plugin inside Hype and manages the connection. Your script or agent sends JSON operations to that running editor. Hype remains a desktop application, including for documents opened without an initial window.

## Requirements

- macOS 14 or later.
- Tumult Hype 4. Compatibility is established with **Hype 4.1.22, build 786**. A newer version is not automatically supported simply because it starts.
- Connector 0.1.6 (app build 47, plugin build 38).
- An internet connection to start the trial or activate a license.
- Python 3 for the optional example scripts. Connector itself does not require Python.

## Install and connect

1. Download and open the DMG, copy Connector into Applications, then open Connector.
2. Open **License**. Choose **Start 7-day trial** to begin without a card, or enter your paid license key and choose **Activate license**. The trial starts only when you choose it. A [€29 one-time license](https://license.maxziebell.de/checkout) covers up to two Macs.
3. Choose Hype's existing `Application Support/Hype` folder when Connector asks. This selection lets Connector install its plugin and find running Hype sessions. Keep the selection so the app can restore access later.
4. Install the bundled Connector plugin. If Hype is already open, save your work and restart Hype when convenient to load it. Connector does not quit Hype for you.
5. Leave Hype running. Scripts can create and save a new document with `document.create`; no manually prepared document is required. When editing an existing document, stop playback and leave its root editing context active.
6. Return to Connector. It connects automatically when there is one reachable Hype. With several, choose by version and open document names. The process ID is available in the connection details.

The installer changes Connector's own plugin. Other installed plugins remain in place. Installing a new plugin on disk does not replace the one already loaded in a running Hype process.

CLI, MCP and AppleScript use the same app license. Start or activate it once in Connector before running automation. The trial and activation require a network connection. A valid signed receipt can support offline use for at most 72 hours, with a normal refresh after 24 hours. See [Trial and license](licensing.md) for refresh, recovery and expiry.

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

This mode runs without opening another Connector window. If access is missing, open the normal app and choose the folder again. A version command alone does not test permission to reach Hype.

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
