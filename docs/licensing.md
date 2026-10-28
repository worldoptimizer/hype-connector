# Trial and license

Connector 0.1.6 requires a trial or paid license for automation. This release includes app build 47 and plugin build 38. Connector 0.1.5 is a historical release that did not require a license.

## Start the seven-day trial

Open Connector’s **License** section and choose **Start 7-day trial** while connected to the internet. The trial starts only when you explicitly choose it. No card is required, and it does not turn into a purchase or subscription.

The seven-day trial includes the automation features. CLI, MCP and AppleScript use the same app license, so you do not need separate keys for each workflow.

## Buy and activate

[Buy a license for €29](https://license.maxziebell.de/checkout). This is a one-time purchase for up to two Macs, with no subscription.

After purchase, copy your license key into Connector’s **License** section and choose **Activate license**. Activation requires an internet connection. Activate the same key on your second Mac when needed. Connector stores the key in that Mac’s Keychain.

If you replace a Mac or reach the activation limit, contact [license@maxziebell.de](mailto:license@maxziebell.de). Do not delete Keychain data to reset activation.

## Refresh and offline use

Connector normally tries to refresh its signed access receipt after 24 hours. A valid receipt permits offline access until its original expiry, at most 72 hours after it was issued. Starting a trial or activating a key always requires a network connection.

A temporary network or service failure does not extend a receipt or the seven-day trial. Once the receipt expires, connect to the internet and choose **Refresh status** in **License**. A revoked license or invalid receipt is refused. Keep the Mac’s date and time correct.

Your Hype documents remain yours and can still be opened and edited normally in Hype after the trial ends or a receipt expires.

## Recover a key or get help

[Recover your license key](https://license.maxziebell.de/recover) using the email address entered at checkout. For purchase, activation or recovery questions, email [license@maxziebell.de](mailto:license@maxziebell.de). Keep license keys out of public issues, screenshots and logs.

## Licensing data

Starting a trial, activating a license or refreshing access sends this installation’s random ID to the licensing service. Paid activation and refresh also send your license key. The service verifies paid status with Stripe and stores your purchase email encrypted to deliver and recover your key. No Hype documents are sent to the licensing server.

## What is included in the public repository?

The public repository contains the website, guides, examples and agent skill. The Connector app and Hype plugin source code remain private. Downloads are distributed through [GitHub Releases](https://github.com/worldoptimizer/hype-connector/releases).
