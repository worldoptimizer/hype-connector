# CLI and scripting

Connector accepts the same JSON operation objects through its CLI, app command mode, MCP and AppleScript. Use a script for a repeatable workflow that discovers IDs, makes edits and checks their results. No AI service is required.

## Discover and pin a connection

```sh
'/Applications/Connector.app/Contents/MacOS/connector' hosts
'/Applications/Connector.app/Contents/MacOS/connector' catalog
```

`hosts` returns running connections, including `pid` and `session`. `catalog` is local documentation. To inspect an individual request contract:

```sh
'/Applications/Connector.app/Contents/MacOS/connector' catalog element.setAttribute
```

Use the actual PID and session from discovery for every subsequent call. Put selectors before the command:

```sh
'/Applications/Connector.app/Contents/MacOS/connector' \
  --pid 12345 --session 'SESSION-FROM-DISCOVERY' \
  capabilities
```

The values above are placeholders. `capabilities` describes the plugin loaded by that Hype process. Its supported operations can differ from the installed app's catalog until Hype restarts. A pinned session prevents a workflow from silently continuing on a restarted editor.

## Request and response format

Pass one JSON object directly, through a file or through standard input:

```sh
'/Applications/Connector.app/Contents/MacOS/connector' \
  --pid 12345 --session 'SESSION-FROM-DISCOVERY' \
  run '{"op":"document.list"}'
```

```sh
'/Applications/Connector.app/Contents/MacOS/connector' \
  --pid 12345 --session 'SESSION-FROM-DISCOVERY' run @operation.json
```

```sh
'/Applications/Connector.app/Contents/MacOS/connector' \
  --pid 12345 --session 'SESSION-FROM-DISCOVERY' run - < operation.json
```

A successful command writes `{"ok":true,"result":...}` to stdout. A failed command exits with status 1 and writes `{"ok":false,"error":...}` to stderr. Check both the process status and JSON envelope. Do not treat a successfully launched process as a completed edit.

For subprocesses, pass arguments as an array and serialize JSON with your language's JSON library. This avoids shell quoting problems in text, filenames and JavaScript source. The [Python examples](examples.md) implement this pattern.

## Build a working copy

Send these as separate operations, filling later values from earlier responses:

```json
{"op":"fixture.stage","source":"/absolute/Base.hype"}
```

The staging response returns `path`, a fresh copy. Use that exact path:

```json
{"op":"document.open","path":"/absolute/returned-copy.hype","display":false}
```

Confirm `opened:true` before continuing. `display:false` suppresses the initial document window; subsequent editor actions can still display UI. Staging rejects symlinks and special files. An optional `destination` selects an existing staging parent already accessible to Hype, useful for large documents on an external volume.

```json
{"op":"layout.list","document":"/absolute/returned-copy.hype"}
```

Use the returned layout ID as `scene` where required and its root symbol ID as `symbol`. A layout/controller ID is different from its scene-container ID. IDs belong to this document; never invent them or reuse them from another package.

```json
{"op":"element.list","document":"/absolute/returned-copy.hype","symbol":"DISCOVERED-SYMBOL-ID","offset":0,"limit":100}
```

For paginated lists, follow `nextOffset` while `hasMore` is true. Insertion scripts need complete before/after inventories to identify the new element reliably.

## Editing building blocks

| Task | Named operations |
| --- | --- |
| Documents and files | `document.list`, `document.open`, `document.save`, `document.saveCopy`, `document.exportHTML`, `document.close` |
| Scenes and layouts | `scene.list`, `layout.list`, `layout.add`, `symbol.list`, `scene.settings.prepare/get/set` |
| Elements and text | `element.list`, `element.get`, `element.setAttribute`, `text.set`, `element.createImage`, `editor.action` |
| Timeline and animation | `timeline.list`, `playhead.get/seek`, `animation.list/get/setTiming/delete`, `timingFunction.list` |
| Inspector and recording | `inspector.prepare`, `inspector.get`, `inspector.set` |
| Assets | `resource.import`, `resource.list`, `resourceGroup.list` and the resource-group operations in the catalog |
| Document JavaScript | `javascript.list/add/rename/setSource/delete` |
| Undo and jobs | `document.undoState`, `document.undo`, `document.redo`, `job.get` |

Slash notation in the table abbreviates separate operation names; send a single exact `op` value. Use `catalog OPERATION` for required fields and supported values.

For a fixed model value:

```json
{
  "op":"element.setAttribute",
  "document":"/absolute/returned-copy.hype",
  "symbol":"DISCOVERED-SYMBOL-ID",
  "element":"DISCOVERED-ELEMENT-ID",
  "attribute":"Width",
  "value":320
}
```

Read the same element with `element.get` afterward. Model setters do not automatically reproduce inspector adjustments, recording behavior or undo grouping. Colors use an explicit object such as `{"$color":[0.2,0.24,0.68,1],"space":"srgb"}`. `text.set` accepts HTML, so escape plain text before sending it. It does not select rich-text ranges.

`editor.action` provides named editor actions, including insertion, duplication and grouping. These change editor context and selection. Root insertion requires the scene already to be in its root editing context; clearing element selection does not leave a nested group or symbol.

## Use the inspector for recording

1. Call `inspector.prepare` with the exact document, scene, symbol, timeline, element, property and desired time.
2. Allow the editor to settle, then call `inspector.get`. Use its actual `seconds` and presented `value`.
3. Send `inspector.set` with that value as `expectedValue`, the actual time, and your new `value`. Set `recording:true` when deliberately recording an animation on Main.
4. Check the receipt, then read the relevant element and animation details.

A prepared context can still be pending. A changed context or presented value is refused. Playhead time can be rounded to a native frame boundary. Use the returned time instead of assuming the requested time was retained. The [animation example](examples.md#animated-template) shows a complete baseline-then-record workflow.

Scene settings use the same prepare/read/set pattern. Dimensions and scaling require explicit `applyToMatchingLayouts:false`. This keeps the edit scoped to the selected layout. Preparation establishes that scope, so it is itself an intentional editor operation.

## Save and export

```json
{"op":"document.save","document":"/absolute/returned-copy.hype"}
```

Wait for `saved:true`. To write another editable package without changing the open document's URL:

```json
{"op":"document.saveCopy","document":"/absolute/returned-copy.hype","destination":"/absolute/output/Result.hype"}
```

For HTML:

```json
{"op":"document.exportHTML","document":"/absolute/returned-copy.hype","destination":"/absolute/output/Result-html"}
```

Use new destinations with existing parents that Hype can write. Export completion returns `exported:true` and the actual `indexPath`. Export can leave further layout or metadata changes in the editable document. If these need persisting, perform a separate explicit save after confirmed export. Open the resulting HTML in your browser to check its appearance and behavior.

After reopening a package, refresh resource IDs. Native save and layout can normalize colors, dimensions and attribute representation. Compare saved values rather than assuming every input survives unchanged.

## Recipes and app command mode

`recipe FILE` runs a fixed `steps` array sequentially and stops on the first error. It is not a transaction and does not substitute IDs from earlier results. Use Python or another language when the next request depends on a returned ID.

To reuse the folder access saved by the app:

```sh
'/Applications/Connector.app/Contents/MacOS/ConnectorApp' \
  --hype-pid 12345 --hype-session 'SESSION-FROM-DISCOVERY' \
  --run-operation - < operation.json
```

This mode accepts one UTF-8 JSON operation, up to 64 KiB. Input must reach EOF within ten seconds before dispatch. It does not accept `@FILE` or recipes. The standalone CLI uses the access of its own launching process.

## Failures and undo

Each operation commits separately. An `outcome_unknown` response or transport timeout means a mutation may have happened. Stop, preserve the working copy and inspect the affected state before another deliberate action. Never automatically repeat insert, import, save or export after uncertainty.

Undo is available for suitable editor actions through `document.undoState`, then `document.undo` with the complete returned object as `expectedState`. Read a fresh state before redo. These operations require a prepared root scene on the stopped Main timeline. They do not create a transaction around your script. Model setters may register no undo action, so confirm affected values and save separately.

See [troubleshooting](troubleshooting.md) for jobs, permissions and partial results.
