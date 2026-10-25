# App and plugin updates

**App distribution is paused.** No app releases are currently available, and the signed update feed contains no update offers. Existing installations remain usable. The following describes the previous preview’s update mechanism.

Connector 0.1.4 includes a signed Sparkle update channel hosted on GitHub. The app checks the signed feed and verifies the downloaded update before installing it.

## If you have Connector 0.1.3

Version 0.1.3 did not have a configured update channel. No manual upgrade is currently offered.

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

App downloads have been withdrawn from GitHub Releases. The signed feed remains on GitHub Pages with no release entries, so existing clients are not directed to removed downloads. This update mechanism does not change the supported Hype versions or the operation limits described in the [compatibility guide](../skills/hype-connector/references/compatibility.md).
