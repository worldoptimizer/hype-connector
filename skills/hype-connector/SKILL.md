---
name: hype-connector
description: Build, inspect, animate, save and export Tumult Hype documents through Connector. Use for editable multi-scene designs, repeatable templates, buttons, JavaScript interactions, images, inspector edits and automation via CLI or MCP. Requires the separately installed Connector app and Hype plugin.
---

# Hype Connector

Use Connector to operate the desktop editor. This package includes working patterns and optional Python standard-library helpers, not an installer. Hype document creation, changes, saving and export all go through Connector. Do not generate or patch package plists, post-edit an export to disguise an editor limitation, or switch to another Hype tool without the user's authorization.

## Start here

Connector 0.1.6 automation requires an active trial or paid license. If it returns `license_required`, ask the user to start the seven-day trial or activate a key in Connector's **License** section. Do not start their trial merely to test connectivity. License errors do not call for reinstalling Hype or probing private selectors. See [Connection and delivery](references/connection-and-delivery.md#license-status).

1. Discover the intended Hype host. Pin its PID and plugin session throughout the workflow. If several hosts or documents fit, resolve the target before editing. Never silently switch after a restart. Do not quit another workflow's Hype instance.
2. Read runtime capabilities and the current request contract. With MCP use `hype_hosts`, `hype_capabilities`, `connector://operations` and `connector://guide`. With the CLI use `hosts`, `capabilities` and `catalog OPERATION`. An installed app normally contains `/Applications/Connector.app/Contents/MacOS/connector`; honor a supplied executable or test wrapper instead.
3. Prefer the composed editing commands when capabilities list them: `element.edit`, `scene.configure`, `animation.create`. Read [reliable editing](references/reliable-editing.md) for the complete named-only workflow. Use native recipes only for a capability genuinely absent from the named surface, not for basic creation or animation.
4. Verify actual content, save completion, reopened state where needed, and browser behavior. Report what was exercised and any limitations.

## Read the relevant recipes

| Task | Read |
| --- | --- |
| Connect, permissions, CLI/MCP/AppleScript, save/export and jobs | [Connection and delivery](references/connection-and-delivery.md) |
| Create a document, change inspector fields and add native motion | [Reliable editing](references/reliable-editing.md) |
| Build a designed example with scenes, text, buttons and motion | [Design recipes](references/design-recipes.md), then [native recipes](references/native-recipes.md) |
| Inspect/edit existing content, images, layouts, timelines and undo | [Operation families](references/operations.md) |
| Native factories, references, event actions and runtime exploration | [Native recipes](references/native-recipes.md) |
| Supported versions, measured scope and known boundaries | [Compatibility](references/compatibility.md) |

The Connector 0.1.5 procedures require a loaded plugin that advertises them. Do not assume they exist in an older released app, and do not bypass a refusal with private selectors.

Optional Python helpers are [connector_client.py](scripts/connector_client.py) and [authoring.py](scripts/authoring.py). Read their interfaces before importing. They do not start Hype, edit package files, install plugins or download dependencies. A client freezes after a transport/API failure: inspect the outcome before deliberately creating another client. It never retries a mutation automatically.

## Rules that prevent expensive mistakes

- Use explicit absolute paths and discovered IDs. A layout/controller ID, scene-container ID, root-symbol ID, timeline identifier and animation UUID are different identities. Scene navigation uses the **scene-container** ID. Named scene operations use the **layout/controller** ID.
- Read all pages of element/resource/animation lists. Discover insertion results through complete before/after IDs. Resource UUIDs can change on reopen; native references expire with the plugin session. List order does not identify an element’s role. Resolve a target by verified content/attributes, require exactly one match, and keep its document, scene, symbol and element IDs together. Before changing it after reopen, read that target again; never infer “headline” from the first list entry or combine an element ID with another scene’s symbol.
- For an experiment, stage a copy with `fixture.stage` or create a new document using `document.create`. For an explicitly requested in-place edit, keep that scope. Do not set an untitled document's file URL before its first save.
- To preserve an original, create and open the working copy **before** editing. Hype can autosave native changes. Editing the original and calling `saveCopy` afterward does not protect it, and closing with `discard:true` cannot undo an autosave.
- Named `element.setAttribute` requires an existing attribute. Use the documented native attribute factory to introduce a known missing attribute. Model setters do not promise inspector side effects or undo registration.
- `element.edit` and `scene.configure` compose preparation, bounded readiness and one guarded change. `animation.create` starts a fresh Main Left, Top or Opacity lane, refuses an existing lane and never shortens a longer timeline. Partial failures carry completed steps; inspect before continuing. For lower-level inspector changes, use separate prepare, settled read and guarded set with exact context, `expectedValue` and actual quantized `seconds`. At fractional endpoints, use the documented `timeline_guard_seconds` rule only for identical float32 representations across the duration bound; never generally round or silently extend time. Scene size preparation requires `applyToMatchingLayouts:false`. An explicit pending preparation is not readiness.
- Root-level recipes require a root scene/Main context. Clearing selection does not exit a nested symbol. Do not fabricate inspector controllers or load their views to force access.
- Native `LineHeight` is in pixels. Fixed text boxes need `ExplicitDimensions:'YES'` (string) as well as width/height; `Document.text` sets it. Stored dimensions alone do not prove fixed export sizing. Test the longest dynamic messages in the live export and check bounding boxes, scroll extents, wrapping and overlap. Stored JavaScript alone does not attach an event; a button needs a native action binding.
- Preserve Hype's native JavaScript template, including its parameter comments and function wrapper. Prefer `Document.script_body`; `Document.script` also retains the native header. For existing functions, read first and make a narrowly scoped edit, preserving comments. `javascript.setSource` and `setHeadHtml:` replace the entire string, so never treat them as append/body-only operations. See [native recipes](references/native-recipes.md).
- Preserve Hype's positioning transforms on native element nodes. Custom hover/pressed CSS must not replace `transform` or `-webkit-transform`, including through `!important` or keyframes. Avoid `transition:all`, which can animate Hype's own geometry changes. Use shadow/color changes, a tested independent `translate`, or an inner visual child. See the button recipe in [Design recipes](references/design-recipes.md). Hold a pointer down and check position before, during and after release; an ordinary completed click can miss a jump.
- A response with `ok:true` means transport success; inspect the operation's result and any native `NSError` output. A job ID is not completion. Save/export paths must be verified.
- Preview exported HTML through an HTTP server bound to `127.0.0.1` and rooted at that export folder. Choose a free port and record/stop only your server. Use HTTP from the outset because browser tools may reject `file:` URLs. Serving unchanged output is verification, not authoring. Never bypass a browser policy refusal.
- On timeout after dispatch, lost reply or `outcome_unknown`, stop mutations and preserve state. Inspect the exact operation/job before a deliberate next step. Do not repeat insertion, import, save or export automatically.
- Prefer plain native values (`retain:false`). Track runtime references, release only known references from your workflow, and never globally release a shared session. Handles can be reused for the same object.

Operations are sequential, not atomic. `display:false` is a hidden-window preference, not a headless service. Undo is a diagnostic, not general rollback. Standard scripts need no AI service. This skill cannot grant filesystem access or bypass normal macOS permission dialogs.
