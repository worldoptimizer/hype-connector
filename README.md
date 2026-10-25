# Connector

**Automations for Tumult Hype 4.**

Connector adds local scripting to the Hype editor. Use a repeatable Python or shell script, AppleScript, or an MCP-connected agent to inspect documents, build content, record animation, save and export.

This repository contains the public website, usage guides, three Python examples and a small independent agent skill. The signed and notarized macOS app is available from [GitHub Releases](https://github.com/worldoptimizer/hype-connector/releases/latest).

[Visit the website](https://worldoptimizer.github.io/hype-connector/) · [Play EISZEIT](https://worldoptimizer.github.io/hype-connector/demos/eiszeit/index.html)

## Read the guides

- [Getting started](docs/getting-started.md)
- [Manual scripting](docs/scripting.md)
- [MCP](docs/mcp.md)
- [AppleScript](docs/applescript.md)
- [Runnable examples](docs/examples.md)
- [Install the Codex / Claude Code skill](skills/README.md)
- [Troubleshooting](docs/troubleshooting.md)

The app requires macOS 14 or later and Tumult Hype. Current native compatibility checks cover Hype 4.1.22/build 786 on Apple Silicon and x86_64 under Rosetta. Hype continues to run as a desktop app. Version 0.1.4 enables signed automatic updates through GitHub Releases. If you have 0.1.3, install 0.1.4 once to enable the update channel. See [Updates](docs/updates.md) for settings and plugin behavior.

## Examples and skill

EISZEIT is a three-scene ice cream campaign built through Connector, with native Hype transitions and an interactive flavour choice. Its exported demo is included in `site/demos/eiszeit`. The fixed 1200 × 800 composition scales to fit the window. The giveaway is a local demonstration and collects no data.

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

To enable the preview's app-download button, pass `--download /absolute/path/Connector.dmg` to the preview server. Without a selected DMG, that route explains that the local download is unavailable. Omit `--preview` only when preparing a reviewed publication with its release asset available. The builder copies an explicit set of assets, renders the guides and creates the example and skill ZIPs. It does not upload anything.

## Project

Connector is an independent project by Max Ziebell. Tumult Hype is a product of Tumult Inc. This project is not affiliated with or endorsed by Tumult.
