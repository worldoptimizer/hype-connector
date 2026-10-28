# Connector

**Automations for Tumult Hype 4.**

Connector adds local scripting to the Hype editor. Use a repeatable Python or shell script, AppleScript, or an MCP-connected agent to inspect documents, build content, record animation, save and export.

This repository contains the public website, usage guides, three Python examples and an agent skill. The Connector app and Hype plugin implementations are private and are not included here.

[Download Connector 0.1.6 for macOS](https://github.com/worldoptimizer/hype-connector/releases/download/v0.1.6/Connector-0.1.6-build47.dmg).

[Visit the website](https://worldoptimizer.github.io/hype-connector/) · [Play EISZEIT](https://worldoptimizer.github.io/hype-connector/demos/eiszeit/index.html)

Connector 0.1.6 requires a trial or paid license for automation. Start a **7-day trial without a card**, or [buy a €29 one-time license](https://license.maxziebell.de/checkout) for up to two Macs. CLI, MCP and AppleScript use the same app license. [Recover a key](https://license.maxziebell.de/recover) or read [Licensing](docs/licensing.md). Connector 0.1.5 is a historical release that did not require a license.

## Read the guides

- [Getting started](docs/getting-started.md)
- [Trial and license](docs/licensing.md)
- [Manual scripting](docs/scripting.md)
- [MCP](docs/mcp.md)
- [AppleScript](docs/applescript.md)
- [Runnable examples](docs/examples.md)
- [Install the Codex / Claude Code skill](skills/README.md)
- [Troubleshooting](docs/troubleshooting.md)

The app requires macOS 14 or later and Tumult Hype. Current native compatibility checks cover Hype 4.1.22/build 786 on Apple Silicon and x86_64 under Rosetta. Hype continues to run as a desktop app. Connector includes signed automatic updates through GitHub. See [Updates](docs/updates.md) for details.

## Examples and skill

EISZEIT · Scoop Studio is a three-scene English ice cream campaign built through Connector, with desktop and phone layouts. Serve three orders to unlock a fictional coupon and a short confetti celebration. The native Hype export is included in `site/demos/eiszeit/scene`, with a small “Made with Hype” frame around it. The game stays local, collects no personal data and offers no real discount.

The [examples](examples/README.md) use Python 3's standard library. Keep all three scripts together and supply your own small Hype base document. Each script works on a fresh copy.

The [hype-connector skill](skills/hype-connector/SKILL.md) is a portable instruction file for Codex and Claude Code. It requires a separate Connector installation and an accessible local CLI or configured MCP server. It does not install software or grant permissions.

## Build the website

The website is static. Python and Markdown are build-time dependencies only:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build_site.py --preview
python3 scripts/serve_preview.py --port 8080
```

Use `--output /path/to/preview` to build into a separate local directory. The app download links to the Connector 0.1.6 release on GitHub. Omit `--preview` to build the public website without the local preview banner. The builder copies an explicit set of assets, renders the guides and creates the example and skill ZIPs. It does not upload anything.

## Project

Connector is an independent project by Max Ziebell. Tumult Hype is a product of Tumult Inc. This project is not affiliated with or endorsed by Tumult.
