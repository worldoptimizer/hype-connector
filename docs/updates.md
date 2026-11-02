# App and plugin updates

[Download Connector 0.1.8](https://github.com/worldoptimizer/hype-connector/releases/download/v0.1.8/Connector-0.1.8-build62.dmg) from GitHub Releases.

Connector includes a signed Sparkle update channel hosted on GitHub. The app checks the signed feed and verifies the downloaded update before installing it.

## What changes in 0.1.8

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

The app includes a matching Connector plugin. After an app update, Connector uses your saved Hype folder selection to replace an older installed Connector plugin. An absent plugin still requires **Installation → Install / Update**. Existing probes and other plugins are left alone.

Hype keeps its loaded plugin in memory. Save your documents and restart Hype when convenient to load the updated plugin. Connector never closes Hype automatically.

If folder access cannot be restored, open **Connection**, choose the Hype support folder again, then use **Installation → Install / Update**. macOS may still request permission when its security policy requires it.

## Release channel

App releases are hosted on GitHub Releases. The signed Sparkle feed is hosted on GitHub Pages. This update mechanism does not change the supported Hype versions or the operation limits described in the [compatibility guide](../skills/hype-connector/references/compatibility.md).
