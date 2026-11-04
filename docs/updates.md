# App and plugin updates

[Download Connector 0.1.12](https://github.com/worldoptimizer/hype-connector/releases/download/v0.1.12/Connector-0.1.12-build78.dmg) from GitHub Releases.

Connector includes a signed Sparkle update channel hosted on GitHub. The app checks the signed feed and verifies the downloaded update before installing it.

## What changes in 0.1.12

Connector 0.1.12 includes app build 78 and the unchanged Hype plugin **0.1.7 build 54**.

- A compact three-step assistant replaces the setup settings page: connect Hype, choose your application, finish.
- Large Back and Continue buttons stay at the bottom. Each step has one primary action.
- The folder permission dialog opens directly in Hype's plugin folder. Continue opens Hype first only if it still needs to create the folder.
- Updated setup instructions and bundled agent skill guidance.

Updating from 0.1.11 does not require restarting Hype when it already runs plugin build 54. Existing connections are kept. Setup does not start the trial.

## What changed in 0.1.11

Connector 0.1.11 includes app build 69 and the unchanged Hype plugin **0.1.7 build 54**. It adds guided Hype setup and **Applications → Connect** for Codex and Claude Code. Connecting installs MCP and the complete skill together; another client can be added later. Setup does not start the trial.

On launch, Connector checks the plugin installation and skills it manages. It updates unchanged managed skills, keeps customized copies and offers a backup when you explicitly replace one. The guided and manual Install / Update buttons preserve a newer installed plugin. Setup indicates when Hype still needs to load the installed plugin; save and restart Hype yourself when needed. App-only updates do not require restarting an already current Hype plugin.

After updating from 0.1.10, connect Codex or Claude Code from **Applications** to set up the bundled skill. Start a new client chat after connecting.

## What changed in 0.1.10

Connector 0.1.10 includes app build 65 and Hype plugin **0.1.7 build 54**. App and plugin version numbers are independent.

- Newly created or updated JavaScript functions show their source immediately in Hype's editor. They can be edited without reopening the document.
- `element.get` and `element.list` return action data with target references, including `javascriptOid`, instead of opaque `HypeAction` placeholders.
- `scene.rename` renames a scene using its layout/controller ID. `scene.list` now exposes `sceneName`, `layoutName` and `sceneContainer`; its existing `name` field remains the layout name for compatibility.
- MCP `resources/templates/list` returns an empty list instead of “Method not found”. The guide and operation catalog remain ordinary MCP resources. Read the installed skill files through the local filesystem.
- The updated agent skill and Python authoring helper use the new scene rename command when the loaded plugin supports it.

After updating Connector, **save your work and restart Hype** to load plugin build 54. Reconnect your MCP client so it uses the updated app, and [update the installed skill](../skills/README.md). In 0.1.10, updating the app alone does not replace a skill previously copied into Codex or Claude.

The fixes were checked in Hype 4.1.22 with a separate scene, native animations, JavaScript functions and button actions, including saving and reopening the document while preserving the original scene.

## What changed in 0.1.9

Connector 0.1.9 includes app build 64 and the unchanged plugin 0.1.6 build 53.

- Normal use of the saved Hype folder selection no longer requires a writable settings directory or lock file.
- Removed unnecessary ownership and exact file-permission restrictions. macOS access permissions still apply.
- Fixed renewal of older saved selections and simultaneous bookmark refreshes.
- Added a [local support report](troubleshooting.md#local-support-report) that includes component versions and access diagnostics without personal paths, document names or license information.

Restart Connector and reconnect your MCP client after updating, so they use the updated executable. If Hype already reports plugin build 53, this app-only update does not require restarting Hype. App and plugin versions are separate and do not need to match.

## What changed in 0.1.8

Connector 0.1.8 includes app build 62 and plugin build 53.

- Fix a folder-access issue that could prevent saving in Documents or its subfolders, even when manual saving in Hype worked. The correction also applies to opening, creating and exporting documents.
- Report destination-access refusals before an operation starts with `started: false` and `mayHaveSideEffects: false`.

After updating Connector, save your work and restart Hype to load the corrected plugin. No scripting changes are needed.

## What changed in 0.1.7

Connector 0.1.7 includes app build 56 and plugin build 47.

- Set attributes on one element or reflow several elements in one request, with validation before the first commit and per-attribute readback.
- Insert native elements with initial attributes and use the returned element IDs directly. Text and both button variants finish their own inserted text editor before the next operation.
- Record several native keyframes with easing and holds, or append after an existing lane, with an explicit guard against changed animation IDs.
- Reduce connection-discovery work and clean up ended-session manifests. Prepare fresh cloned layouts whose native selection is initially empty.
- Use the updated authoring helper and skill for batch reflow, insertion receipts and keyframe workflows.

Read the [scripting guide](scripting.md) for batch limits, frame-grid requirements and failure receipts. Batches and keyframe workflows are sequential, so earlier edits can remain if a later step fails. Inspect state after an unknown outcome before making another deliberate change.

After updating the plugin, save your documents and restart Hype when convenient. Each running Hype instance keeps its previously loaded plugin until it restarts. The selected host's capabilities describe the features actually available.

## Licensing introduced in 0.1.6

Connector 0.1.6 includes app build 47 and plugin build 38. Automation now requires a trial or paid license. Connector 0.1.5 is a historical release that did not require a license.

After updating, open **License** and explicitly start the seven-day trial without a card, or activate a paid key. A [€29 one-time license](https://license.maxziebell.de/checkout) covers up to two Macs and all app, CLI, MCP and AppleScript automation. Your Hype documents remain editable in Hype after a trial or license receipt expires. See [Trial and license](licensing.md).

## If you have Connector 0.1.3

Version 0.1.3 did not have a configured update channel. Download the current DMG, quit Connector after active work finishes, and replace the app in Applications.

## Choose how to update

Open **Updates** in Connector, or choose **Connector → Check for Updates…** from the menu.

- Automatic update checks are enabled by default. You can turn them off.
- Automatic downloading and installation is optional. Enable it in Updates if you want Sparkle to handle updates when possible.
- Manual checks show the available version and release notes before installation.

Connector postpones an update restart while an automation is running. An explicitly selected Hype connection stays selected across the update restart. If that session disappears, Connector does not silently switch to another Hype instance.

## The Hype plugin

The app includes a matching Connector plugin. After an app update, Connector uses your saved Hype folder selection to replace an older installed Connector plugin. Connector 0.1.11 installs it during first-time Setup. If the plugin is removed after setup, use **Installation → Install / Update**. Connector 0.1.10 also uses that button for its first installation. Existing probes and other plugins are left alone.

Hype keeps its loaded plugin in memory. Save your documents and restart Hype when convenient to load the updated plugin. Connector never closes Hype automatically.

If access fails, inspect the [support report](troubleshooting.md#local-support-report) before selecting the folder again. If the saved selection is missing or unusable, restore it in **Connection** (or **Setup** in Connector 0.1.11), then finish plugin installation. macOS may still request permission when its security policy requires it.

## Release channel

App releases are hosted on GitHub Releases. The signed Sparkle feed is hosted on GitHub Pages. This update mechanism does not change the supported Hype versions or the operation limits described in the [compatibility guide](../skills/hype-connector/references/compatibility.md).
