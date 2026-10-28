# Connection, documents and delivery

Use this reference for choosing a transport, creating/opening a document, saving, exporting and resolving completion. Connector 0.1.5 targets Hype 4.1.22 build 786 on macOS 14 or later. Named creation, duration, video and external-access workflows require their advertised capabilities. Read [compatibility.md](compatibility.md) for architecture coverage and concrete limits. Check the running plugin's capabilities; a newer installed app does not replace a plugin already loaded in Hype.

## Connect once, keep the identity

A normal installation contains two executables:

- `/Applications/Connector.app/Contents/MacOS/connector`: standalone CLI.
- `/Applications/Connector.app/Contents/MacOS/ConnectorApp`: app, app-backed one-shot commands and MCP.

Use the actual installed location if different. Open Connector normally to select Hype's support folder and install the plugin. If installation changed a running Hype's plugin, Hype must restart before that new version loads. Do not restart an editor with someone else's work as a side effect of discovery.

### License status

Connector 0.1.6 requires an active seven-day trial or paid license. The app, CLI, MCP and AppleScript share that license. `connector license status` inspects the local status. The trial begins only when explicitly started, so obtain the user's intent before `connector license trial` or the app's **Start 7-day trial** action. Activation and the first trial start need internet access. Enter keys in the app or via `connector license activate -` on stdin, never command-line arguments, logs or public messages.

On `license_expired`, use **Refresh status** or `connector license refresh` while online. A valid signed receipt supports at most 72 hours offline. `trial_expired` requires a paid license, and `license_revoked` requires resolving the purchase with support. Do not delete Keychain entries, reset installation IDs, downgrade or switch transports to work around these errors. These are licensing outcomes, not a reason to mutate a Hype document or reinstall its plugin.

### Discover the host

```sh
'/Applications/Connector.app/Contents/MacOS/connector' hosts --details
'/Applications/Connector.app/Contents/MacOS/connector' catalog
'/Applications/Connector.app/Contents/MacOS/connector' catalog document.exportHTML
```

`hosts` returns `result.sessions`, including each `pid` and `session`. Details include version and documents where reachable. With one connection, interactive use can auto-select it. For a multi-step script, select the intended host and retain **both** identities for every request. PID alone can be reused after a restart. All IDs in this reference are placeholders.

```sh
'/Applications/Connector.app/Contents/MacOS/connector' \
  --pid 12345 --session 'DISCOVERED-SESSION' capabilities
'/Applications/Connector.app/Contents/MacOS/connector' \
  --pid 12345 --session 'DISCOVERED-SESSION' run '{"op":"document.list"}'
```

Selectors precede the CLI command. `catalog` reads local request schemas without contacting Hype; `capabilities` reads the selected loaded plugin. `version` succeeding does not establish filesystem permission or a live connection.

Native object references and document-local IDs are distinct. Keep all references within their original session. After reopen, rediscover object references and resource IDs. Pinning is target selection, not a license to operate on every document in that process. Follow any workspace-specific host ownership checks supplied by the user.

## JSON transport and permissions

The standalone CLI accepts one object as `run JSON`, `run @FILE` or `run -` with JSON on stdin. For native bridge requests, `native JSON` wraps that raw request as `native.query`. Alternatively send the full wrapper with `run`:

```json
{"op":"native.query","request":{"op":"roots"}}
```

Success is exit status 0 plus `{"ok":true,"result":...}` on stdout. Failure is status 1 plus `{"ok":false,"error":...}` on stderr. Parse the envelope and operation-specific completion fields. For subprocess calls use an argument array and a JSON serializer, rather than shell interpolation. Keep stderr available even when the process fails.

The standalone CLI inherits its launcher's access. The app-backed mode reuses the folder selection saved by Connector:

```sh
'/Applications/Connector.app/Contents/MacOS/ConnectorApp' \
  --hype-pid 12345 --hype-session 'DISCOVERED-SESSION' \
  --run-operation - < operation.json
```

Its selectors must be paired. Add `--allow-native` when the input operation is `native.query`. App mode accepts inline JSON or stdin, not `@FILE`. Input is UTF-8, at most 64 KiB, and stdin must reach EOF within ten seconds before dispatch. This explicit mode does not open another app window. Prefer bounded requests to enormous text or source payloads.

If saved access is unavailable, open the normal Connector app and select the folder again. Its saved grant covers the selected support folder, not every source image, document or export directory that Hype might access. A successful Terminal read does not establish that Hype can read the same file. On hosts advertising `ephemeralDestinationAccess`, supported create/copy/HTML/video operations transfer a fresh temporary bookmark for the existing destination parent. `ephemeralDocumentAccess` adds external `document.open` and in-place `document.save`. The client must already hold the required parent access; these transfers do not grant new client permission or permanent Hype access. Export and Save To destination access remains active through native completion or terminal job observation, including work beyond a timeout. Hosts advertising `documentLifetimeAccess` keep the source-parent access acquired by create, open or in-place save for the lifetime of that exact open document, so deferred native reads between requests remain permitted. Closing the document releases its lease; pending operations keep their own access until completion. This access is not persisted across Hype launches. Older hosts provide only operation-lifetime access. Read-only parents may be opened but cannot be writable destinations. Older hosts retain their original sandbox requirements. `resource.import` is outside these transfers, so use an asset location Hype can already read. Do not fix a missing grant by repeated Hype launches or by disabling macOS protections.

`recipe FILE` executes a fixed `steps` array sequentially, stops on the first failure, and pins the host before its first host operation. It is neither a transaction nor an ID-substitution language. Use a short Python or other script when later requests depend on returned IDs.

## Start from a document or a new native document

For an existing base, stage it through Connector:

```json
{"op":"fixture.stage","source":"/absolute/Base.hype"}
```

Use the returned `path`; it is a fresh package copy. Optional `destination` is an existing accessible staging **parent**, useful for large work on an external volume. Staging rejects symlinks and special files and preserves file dates.

```json
{"op":"document.open","path":"/absolute/returned-copy.hype","display":false}
```

By default, `document.open` waits for its native job and returns `opened:true`. `wait:false` returns a job receipt instead, which requires polling. `display:false` suppresses the initial window. This is a hidden desktop editor, not a headless rendering service: inspector initialization or subsequent editor operations can show UI.

For a new project, prefer the named `document.create` operation when the loaded
host advertises it:

```json
{"op":"document.create","destination":"/absolute/output/New.hype","display":true,"timeout":120}
```

Use a fresh absolute `.hype` path under an existing accessible parent. The
operation creates a native untitled document, performs initial Save As and
verifies the assigned document URL, completed job and package contents. Require
`created:true` and `saved:true`, then discover its contexts directly. Hidden
creation with `display:false` is supported; movie export separately requires a
displayed document. A failure can preserve an untitled document or partial
package. Inspect the returned job and `preservedDocuments` instead of retrying
or closing it as cleanup. A timeout does not cancel native work.

If `document.create` is absent, read the documented legacy native creation
recipe in [native-recipes.md](native-recipes.md) before proceeding. Do not guess
selectors, call `setFileURL:` as a substitute for initial save, or substitute the
fire-and-forget `saveDocument:` selector for completion-aware save.

Discover layouts using `layout.list`, then elements and timelines for the returned root symbol. Use each layout/controller ID where a named operation requests `scene`; it differs from the scene-container ID. Native scene transitions use the scene-container identity described in the native recipes. Follow `nextOffset` while `hasMore` for named inventories. Invented IDs or partially read inventories make later mutations unreliable.

## Save, export, reopen

For an already named open document:

```json
{"op":"document.save","document":"/absolute/Working.hype"}
```

Require `saved:true` before closing or moving on. This operation uses the native completion callback with a fixed 120-second wait budget. For raw model calls that bypass Hype's editor change tracking, mark the document changed as described in the native recipe before saving. A method returning successfully is not evidence that a save occurred.

For a separate editable deliverable:

```json
{"op":"document.saveCopy","document":"/absolute/Working.hype","destination":"/absolute/output/Result.hype"}
```

This does not change the source document's URL and may leave it edited. The destination must be new unless deliberately using `overwrite:true`; do not enable overwrite to conceal a partially completed prior attempt. Parent directories must already exist and have the access required by the loaded host. New ephemeral-access hosts transfer the client's existing parent access as described above.

If the original must stay unchanged, save it, create the copy **before the first revision**, and open that copy as the editing target. Rediscover its IDs. Hype may autosave changes even without an explicit `document.save`; a later `saveCopy` or close with `discard:true` cannot restore the original. For persistence checks compare authored content through fresh inventories, and distinguish native metadata/thumbnail rewrites from content changes.

```json
{"op":"document.exportHTML","document":"/absolute/Working.hype","destination":"/absolute/output/Result-html"}
```

Export uses the document's current native export options with HTML enabled and enclosing-folder disabled. Its named API does not expose arbitrary export slices. The destination must be fresh, with no symlink components. Require `exported:true` and use the returned `indexPath`, rather than guessing the HTML filename. Completion verifies HTML, generated JavaScript, referenced runtimes and a restorable plist when requested. Default wait is 120 seconds. Export may update native layout or metadata: save explicitly afterward if those changes belong in the editable deliverable.

For a native movie, check `document.exportVideo` in host capabilities before
editing or promising delivery:

```json
{"op":"document.exportVideo","document":"/absolute/Working.hype","destination":"/absolute/output/Result.mp4","duration":3,"framesPerSecond":30}
```

The current adapter is restricted to Hype 4.1.22 build 786, H.264 MP4 without
audio, positive duration up to 30 seconds, integer FPS 1–60 (default 30), and
`scale:1`. The document must be displayed without an existing sheet. Its first
scene needs even integer dimensions at most 1920 × 1080. Native progress runs
without a Save dialog or simulated keys. Require a successful envelope with
`writerStatus:2`, `nativeSheetResponse:1`, `containerVerified:true`, positive
`capturedFrames` and the intended output `path`. Completion checks native
cleanup/sheet completion, writer completion and container structure,
then delivers without replacing an existing destination. Partial output is
preserved. Independent decoding and visual checks remain necessary for the
specific deliverable.

The default wait is 120 seconds, with optional `timeout` 1–300. A timeout means
unknown outcome, not cancellation. Inspect the exact export job with `job.get`;
keep its document open while `nativePending` is true. To request cancellation,
use `document.cancelVideo` with the exact `document` and export `job`, then poll
for terminal state. A finalizing writer may refuse cancellation. Never export
again to resolve an uncertain response. Capture includes the endpoint frame:
three seconds at 30 fps produces 91 frames, about 3.033 seconds encoded. Receipts
separate `requestedDuration` and `capturedFrames`.

Inspect the exported page in a browser for layout, scene navigation, animation, custom JavaScript, and usable controls. This checks the native export; it is not an opportunity to rebuild the design in a replacement HTML page. When the user requires Connector-only authoring, keep document changes and export generation in Connector. Generated files can be copied unchanged for delivery.

Serve that unchanged export folder on loopback HTTP before opening it in a browser. For example, run `python3 -m http.server 8770 --bind 127.0.0.1 --directory '/absolute/output/Result-html'` using an available port, then open its `http://127.0.0.1:8770/index.html`. Track that server's process and stop only your server after verification. Browser tools may disallow `file:` URLs. Use HTTP from the start, do not disable security or try alternate routes after a policy refusal. Inspect computed text color/font size and visible bounds after all edits, as well as motion at multiple times; an inspector receipt alone does not establish the final appearance.

```json
{"op":"document.close","document":"/absolute/Working.hype"}
```

Close refuses unsaved changes by default. `discard:true` is an explicit decision to lose changes, not a save workaround. Reopen a saved output and read its scene/element/resource inventories when the task calls for a reusable editable document. Native saves may normalize colors, dimensions and representations; resource UUIDs can change on reopen.

For a `.hype.zip` delivery, include exactly one top-level `.hype` package. Put README files outside that ZIP. After extraction, `data.plist` and `Resources` must be directly inside the package, rather than under an accidental extra `.hype` wrapper.

## Jobs and uncertain outcomes

The host's native jobs and the Connector app's AppleScript jobs are separate namespaces. Keep each receipt and poll using its corresponding interface.

Native job inspection:

```json
{"op":"job.get","job":"RETURNED-NATIVE-JOB-ID"}
```

Native states are `running`, `completed` or `failed`. Inspect the job's result/error. A returned job ID alone is not completion. After handling a completed/failed record, release it with the same request plus `"release":true`. Releasing records neither rolls back changes nor releases arbitrary retained native handles.

`document.open` normally waits and releases its job automatically. `document.save` and `document.saveCopy` normally return completion and attempt to release the completed job. Errors such as `save_failed` may include a job ID, native error details and `mayHaveSideEffects:true`; keep these details and inspect the specific job. Partial output on failure is preserved.

On transport timeout or `outcome_unknown`, stop dependent mutations. The request may have executed. Inspect the identified job, document inventory and output before deciding what to do next. Do not automatically repeat insertion, import, save or export, and do not delete the working copy to “reset” an unknown outcome. Earlier steps remain committed. A changed session requires fresh discovery and inspection, not silent repinning halfway through a build.

## MCP

Run a local stdio server directly, preserving stdin/stdout:

```json
{
  "mcpServers": {
    "hype-connector": {
      "command": "/Applications/Connector.app/Contents/MacOS/ConnectorApp",
      "args": ["--mcp-stdio", "--allow-native"]
    }
  }
}
```

This illustrates the `mcpServers` config format; clients may express the same command and arguments differently. Omit `--allow-native` for workflows needing only named operations. Never launch stdio MCP through `open -a`. Standalone `connector mcp --allow-native` is the alternative using its launcher's access. App MCP reuses saved folder access and does not open a background permission chooser.

- `hype_hosts`: discover sessions.
- `hype_capabilities`: check selected loaded plugin.
- `hype_query`: named reads only.
- `hype_apply`: named mutations through a `request` object.
- `hype_document_create`: direct `destination`, optional `display` and `timeout`.
- `hype_timeline_set_duration`: direct `document`, `symbol`, `timeline`, positive `seconds` and fresh `expectedDuration`.
- `hype_document_export_video`: direct `document`, `destination`, `duration`, optional `framesPerSecond` and `timeout`.
- `hype_native`: raw native bridge request, exposed only with `--allow-native`.

Read `connector://guide` and `connector://operations` for the current request contracts. `hype_query` and `hype_apply` arguments wrap the operation:

```json
{"pid":12345,"session":"DISCOVERED-SESSION","request":{"op":"document.list"}}
```

The three dedicated mutation tools take their fields directly without `op` or a `request` wrapper, plus optional `pid` and `session`. Tool presence alone does not establish support in the selected loaded plugin. Use `hype_apply` for `document.cancelVideo`.

For `hype_native`, `request` is the **raw** native object, such as `{"op":"roots"}`, without another `native.query` wrapper. The query/apply tools reject `native.query`; use the enabled native tool explicitly. Native getters can initialize state, so native tools are not classified as inherently read-only.

For a fixed server target, add paired `--hype-pid` and `--hype-session` to the app's launch arguments. Conflicting per-tool selectors are refused. After a restart, refresh fixed launch selectors deliberately.

## AppleScript

Address **Connector**, which supplies the dictionary, rather than assuming Hype supplies equivalent scripting commands. macOS may require the scripting application to be allowed to control Connector.

```applescript
tell application "Connector"
    set responseJSON to perform operation "{\"op\":\"host.list\"}"
end tell
return responseJSON
```

Parse the JSON envelope, choose the discovered connection, then pin subsequent calls:

```applescript
tell application "Connector"
    set responseJSON to perform operation "{\"op\":\"document.list\"}" host pid 12345 host session "DISCOVERED-SESSION"
end tell
return responseJSON
```

For long work, submit once and poll the app-owned record:

```applescript
tell application "Connector"
    set jobID to submit operation "{\"op\":\"document.save\",\"document\":\"/absolute/Working.hype\"}" host pid 12345 host session "DISCOVERED-SESSION"
    set statusJSON to job status jobID
end tell
return {jobID, statusJSON}
```

This polls only once. Continue reading `job status jobID` while its parsed state is `running`. `completed` includes a `response` operation envelope; verify its success and `saved:true`. `failed` may include a failed response or an error. Release only after handling the result with `job status jobID releasing true`. These records belong to the running app; do not send their IDs to native `job.get`. Connector refuses a normal quit while app-owned jobs/helpers are active.

Generate JSON with a serializer and parse responses as JSON; substring searches for `true` or `saved` do not establish success. The named operation contracts are identical across CLI, MCP and AppleScript.

## Movie window preparation

When capabilities advertise `videoExport.preparesDocumentWindow`, a named video
export prepares the requested document window and selects its tab if necessary.
Do not add a close/reopen workaround. Existing sheets remain untouched and cause
`document_busy`. The operation converts captured images into tagged sRGB buffers
for the native H.264 writer (BT.709 primaries/matrix, sRGB transfer). It composites
alpha over black. Verify the completed movie independently; compression is lossy.

## Playhead after opening a document

Use `playhead.seek` with the document, layout/controller scene ID, expected Main timeline and requested seconds. It prepares the requested scene when its editor has not loaded, waits for a stable cursor, then performs one guarded seek. No manual inspector preparation is required. This may change the active scene. `playhead.get` stays read-only and may return `editor_not_ready` or `inspector_controller_not_ready` before the target editor has loaded. Unknown outcomes are not replayed automatically.
