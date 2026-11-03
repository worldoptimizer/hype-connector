# Hype Connector skill

A standalone skill for Codex and Claude Code that teaches an agent to build and inspect editable Hype documents through Connector. It includes connection and save/export guidance, operation recipes, native authoring recipes, design patterns, and known compatibility limits.

[Download the complete skill](https://worldoptimizer.github.io/hype-connector/downloads/hype-connector-skill.zip). The ZIP includes the instructions, six reference guides and two optional Python helpers. Keep the entire `hype-connector` folder together: the main instruction file loads references and helpers when needed.

## Guided installation in Connector 0.1.11

Connector 0.1.11 bundles this complete skill. After Hype setup, choose **Applications → Connect** beside **Codex** or **Claude Code**. This configures MCP and installs the skill together. A compatible Codex desktop installation supplies its own CLI; a separate terminal installation is not required. You can add the other client later from Applications.

Start a new chat after connecting. “Configured” confirms the saved connection, not that your agent has made a successful Hype call. Use **Copy first prompt** to check `hype_hosts` without starting a trial. Normal client tool approvals still apply.

Later app launches update unchanged skills managed by Connector. Locally edited skills are preserved. When connecting with a different existing skill, choose **Connect and keep my skill**, or **Replace and keep a backup**. Other MCP entries are preserved; an existing conflicting `hype-connector` connection needs review in the client's settings.

Use the manual instructions below with Connector 0.1.10 or clients not covered by guided setup. Install Connector and its Hype plugin first. Configure MCP through **Automation → MCP configuration**, or give your agent the app's bundled CLI path. The standalone skill is independent of Skillset. Skip the manual copy if guided setup already installed it.

## What is included

- [Connection and delivery](hype-connector/references/connection-and-delivery.md): selecting one Hype session, permissions, first save, save copies, export completion, MCP and AppleScript.
- [Reliable editing](hype-connector/references/reliable-editing.md): complete workflows using documented editing commands.
- [Operation recipes](hype-connector/references/operations.md): named editor workflows and the context each request needs.
- [Native authoring recipes](hype-connector/references/native-recipes.md): measured Connector native calls for authoring beyond named operations.
- [Design recipes](hype-connector/references/design-recipes.md): composing complete, editable scenes and interactions.
- [Compatibility and limits](hype-connector/references/compatibility.md): what has been established and where an agent must inspect results.
- [Connector client](hype-connector/scripts/connector_client.py) and [authoring helper](hype-connector/scripts/authoring.py): optional Python wrappers using the standard library. Keep them together in `scripts/`; no `pip` packages are needed. They send requests through Connector and do not replace Hype with a separate document writer.

The instructions describe both named operations and explicitly enabled native access. Use the current plugin's capabilities and the supplied recipes; the skill does not make every possible native selector a supported operation.

## Manual installation: Codex

Extract the ZIP. In Terminal, change to the directory containing the extracted `hype-connector` folder, then copy the whole folder's contents:

```sh
mkdir -p "$HOME/.agents/skills/hype-connector"
cp -R hype-connector/. "$HOME/.agents/skills/hype-connector/"
```

Start a new Codex chat and invoke `$hype-connector`, or request a Connector task matching its description.

## Manual installation: Claude Code

From the directory containing the extracted `hype-connector` folder:

```sh
mkdir -p "$HOME/.claude/skills/hype-connector"
cp -R hype-connector/. "$HOME/.claude/skills/hype-connector/"
```

Start a new Claude Code session and invoke `/hype-connector`, or describe a matching Connector task.

## Install from the repository

From the downloaded or cloned repository root, use `skills/hype-connector/.` as the copy source instead of `hype-connector/.`. The destination stays the same. Choose either the ZIP or repository installation method.

Copying updates files of the same name in that skill folder. For a clean replacement, preserve any personal additions, remove only the previous `hype-connector` skill folder, then copy the new complete folder. Do not update only `SKILL.md`; its recipes and Python helpers belong to the same version. To uninstall, remove only this skill folder. These manual copy steps do not run automatically. Guided setup in 0.1.11 manages its own installed copy as described above.

## Try it

Start with inspection:

> Use the hype-connector skill to list open Hype documents and summarize the scenes, elements and animations in my selected document. Inspect only.

For a complete authoring task:

> Use Connector to build a new three-scene Hype demo for a coffee brand. Include an image, navigation buttons with different scene transitions, an ingredients scene and an interactive tasting selection. Keep the text, images and controls editable in Hype. Save the Hype package and export HTML to new output paths. Read back the structure and check the exported interactions. Use only Connector for Hype authoring.

Give the agent an accessible output folder and any source assets it should use. A skill provides instructions, not additional permissions. The ordinary scripts also work without an AI service.
