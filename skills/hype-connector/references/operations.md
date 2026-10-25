# Operation families and reliable workflows

Use this reference to choose an operation, then read its current `catalog` contract or MCP `connector://operations` schema. Field names below are literal. Values such as document paths and IDs must come from this workflow. Check the running host's capabilities as well as the local catalog.

## Identity and discovery

Keep the selected host's process and plugin-session identities fixed for a multi-step workflow. They are transport selectors, not fields inside named operation JSON. A host restart invalidates runtime references and requires fresh discovery.

| Discover | Required operation fields beyond `op` | What the identity means |
| --- | --- | --- |
| `document.list` | None | Absolute open document paths |
| `scene.list` | `document` | Scene/layout controller IDs |
| `layout.list` | `document` | Layout IDs, owning `sceneContainer`, root `symbol` |
| `symbol.list` | `document` | Document-local symbol identities |
| `element.list` | `document`, `symbol` | Elements owned by that symbol |
| `timeline.list` | `document`, `symbol` | Timeline identifiers, names and durations |
| `animation.list` | `document`, `symbol`, `timeline` | Animation UUIDs, start times and durations |
| `timingFunction.list` | `document` | Document-local easing identities |
| `resource.list` | `document` | Current-open resource UUIDs and native names |
| `resourceGroup.list` | `document` | Groups and their current resource membership |
| `javascript.list` | `document` | Document function identities and source |

`scene` in mutation requests means a layout/controller ID, not a scene-container ID. Do not substitute a display name, root-symbol ID or ordinal. Multiple layouts may belong to the same scene container. Discover their relationship explicitly.

`element.list`, `animation.list` and `resource.list` accept `offset` and `limit`. Their arrays are named `elements`, `animations` and `resources`. Each page also reports `total`, `nextOffset` and `hasMore`. Start at zero, append the rows, and follow `nextOffset` until `hasMore:false`. The default page size is 100 and the maximum is 1000. Do not mutate the collection while paging it. For creation, take complete before and after inventories and compare IDs; one page is insufficient to identify a newly added object in a large document.

Resource UUIDs can change after close/reopen. Re-list before using them again. Native collection `map` and `find` are a separate interface: `map` projects a getter named by `name`; `find` uses `where` and separate `scanLimit` and result `limit`. Follow `nextOffset` even when a `find` page contains no matches. A scan page can end before the match. Release only runtime references acquired by your own workflow. Prefer `retain:false` for native scalar reads.

## Documents, persistence and export

- `fixture.stage`: `source`, optional `destination`. Creates a unique copy of a `.hype` or `.hypetemplate` package and returns the path. Rejects symlinks and special files. Use that returned copy for experimentation rather than editing the source. The default staging parent has a 100 MB budget; an explicit destination permits up to 2 GB. Existing files are not overwritten.
- `document.open`: absolute `path`, optional `display` and `wait`. Defaults to `display:false`, `wait:true`. Use `wait:false` only when you will track the returned native job to completion.
- `document.save`: `document`. Wait for its completion result. A returned job ID alone is insufficient.
- `document.saveCopy`: `document`, `destination`, optional `overwrite`. Use a fresh destination by default. The open document's URL remains unchanged; reopen the saved copy explicitly when checking it.
- `document.exportHTML`: `document`, `destination`. Destination must not exist and its parent must already be writable. Success verifies the native index result plus actual HTML and generated JavaScript files. It does not establish browser rendering, runtime interaction or JavaScript correctness.
- `document.close`: `document`, optional `discard`. Do not supply `discard:true` unless discarding changes is intended and authorized.
- `job.get`: `job`, optional `release:true`. Inspect the completed result first. Release deletes the job's diagnostic record, not its filesystem effects. These are native jobs, distinct from the Connector app's AppleScript job IDs.

After successful export, Hype can have further native layout or metadata changes. If the editable document should preserve that final state, save it separately. Treat the native `edited` flag as an observation, not a checksum: an inspector edit can change exposed content while that flag remains false.

Save errors can include a plain native error, job identity and `mayHaveSideEffects:true`. Preserve partial output and inspect the exact job and document. `outcome_unknown`, a timeout after dispatch, or a lost response is not permission to retry. First inspect whether the requested effect already happened. A confirmed open followed by a job-release failure does not mean the document failed to open.

## Element insertion, selection and model values

`editor.action` requires `document`, `scene`, `name`; optional `elements` is an array of existing IDs in that scene's currently displayed symbol. Supported names:

- `insert.rectangle`, `insert.ellipse`, `insert.text`, `insert.button`, `insert.texturedButton`, `insert.htmlWidget`, `insert.polygon`
- `selection.duplicate`, `selection.group`
- `scene.create`, `scene.duplicate`, `scene.duplicateWithoutAnimations`, `scene.delete`

The operation changes scene/selection and invokes an editor action. Its response confirms invocation, not a new object ID. Discover the result through complete before/after inventories. After scene actions, refresh scene/layout/symbol relationships. After grouping, re-read element relationships instead of assuming children are still in the same displayed context.

An empty `elements` array clears selection; it does not leave a nested group or symbol editing context. Root-level insertion requires a root context. The current named surface has no `symbol.enter` or `symbol.exit` operation. Do not invent those calls or assume a symbol definition ID identifies one particular instance. Use a documented, verified native recipe if the task requires additional navigation.

`element.get` requires `document`, `symbol`, `element` and returns current attributes. `element.setAttribute` takes those fields plus `attribute` and `value`. It copies and sets an existing model attribute. An absent attribute can yield `attribute_not_found`; do not repeatedly submit guessed attribute names. Read the available attributes, use an editor action that introduces the intended attribute, or use a separately documented native construction recipe.

`text.set` requires the same identity fields plus a string `value`. It writes complete `InnerHTML`; an empty string deliberately clears it. It can introduce that text attribute, but does not promise native text measurement, a selected character range, or editor-style line-break normalization. Read actual width, height, font size and line height after changing copy. Rich-text range selection remains outside this named operation. For fixed text geometry, also establish native `ExplicitDimensions:'YES'` (a string); `Width`/`Height` alone can leave exported text auto-sized. `Document.text` sets this flag. If it is missing, use the known native attribute factory rather than expecting `element.setAttribute` to introduce it. The [native text recipe](native-recipes.md#fixed-text-boxes-and-dynamic-messages) explains wrapping and required runtime checks after the longest dynamic message.

Colors use `{"$color":[0.2,0.4,0.6,1],"space":"srgb"}`. Components are numbers from 0 to 1. Unsupported spaces remain opaque. Do not reinterpret an opaque object as a usable CSS value.

## Inspector edits: prepare, read, change

Use this path when the change should follow the editor's inspector binding rather than only a model setter. Each request requires `document`, `scene`, `symbol`, `timeline`, `element`, `property`.

1. `inspector.prepare`, optionally with `seconds`, selects the requested editor context and inspector pane. The symbol must already be displayed in that scene.
2. Allow editor updates, then call `inspector.get`. It returns the presented `value` and actual `seconds`. Optionally pass `seconds` to guard the expected playhead.
3. Call `inspector.set` with the same identity fields, the exact read `expectedValue`, returned `seconds`, and new `value`. At a fractional timeline endpoint, use the narrowly bounded [float32 time guard](native-recipes.md#fractional-endpoint-guards-on-current-plugins) for get/set when the returned native cursor exceeds the double duration only by its float32 representation; do not generally round or relax time guards. Optional `recording:true` records on Main; default is false.
4. Read affected element and animation projections. Save explicitly.

Preparation is not a settled-value promise. Keep these as separate requests so Hype can update its bindings. A disabled/unavailable binding is refused rather than becoming zero. A changed context, time or value requires a new read. Never reuse stale `expectedValue` after unrelated operations.

Supported inspector properties:

| Family | Properties | Value constraints |
| --- | --- | --- |
| Geometry | `Left`, `Top`, `Width` | Finite numbers; width nonnegative |
| Appearance | `Opacity`, `BackgroundColor`, `BorderWidth` | Opacity 0–1; sRGB color; border width nonnegative |
| Transform | `ScaleX`, `RotationAngleZ`, `SkewX` | Finite numbers; current scale-ratio constraint remains in effect |
| Text | `LetterSpacing`, `TextColor`, `FontSize`, `LineHeight`, `TextAlignment` | Finite numbers or sRGB color; font size positive integer; alignment `left`, `center`, `right`, `justify` |

A successful set reports `beforeValue`, resulting native `value`, `recordingBefore`, `recordingUsed`, `recordingRestored:true`. Native normalization can differ from the requested value. Original recording mode is restored, but the operation does not save. A failure after the native setter begins is an unknown outcome.

## Scene dimensions, background and responsive layouts

`scene.settings.prepare`, `.get`, `.set` take `document`, `scene`, `property`. Set additionally requires `expectedValue` and `value`. Properties are `width`, `height`, `backgroundColor`, `scaleWidth`, `scaleHeight`, `widthPercent`, `heightPercent`.

For every size/scale request, explicitly include `applyToMatchingLayouts:false`. Preparation establishes and persists that selected-layout scope. The background operation stays local and preserves the existing scope flag.

- Ready preparation reports `prepared:true`, `bindingReady:true`, `scopeEstablished:true`.
- Pending preparation reports all three false and may include `animationReady:false`. Allow editor updates and deliberately prepare again. No content edit or established scope is implied by pending status.
- Read a settled value before set. Do not set merely because the pane was selected.
- Dimensions are positive integers up to 100000. Percentages are greater than zero and at most 1000, with `100` meaning 100 percent. Turn on the corresponding scale flag before changing its percentage.
- Background requires an sRGB color with alpha exactly 1.
- Resizing does not scale existing element geometry. A single-layout scene's breakpoint may change with its dimensions.

`layout.add` requires `document`, source `scene`, nonempty `name`, positive numeric `width`, `height`. It creates a responsive sibling through the scene container and returns the new IDs in `layouts`. The source must be at its root symbol with only Main available and playback stopped. Refresh layout relationships and prepare the chosen new layout before subsequent inspector/image work.

## Images and library resources

`resource.import` requires only `document` and absolute `path`. Hype must already have filesystem access to the input. Connector does not obtain a grant or show a chooser for that path.

Supported imports: CSS, JavaScript, PNG and RGB JPEG, at most 8 MiB each. Text must be nonempty UTF-8 without NULs. Images must decode completely, match their extension and have at most 16777216 pixels. JPEG must decode as RGB, so grayscale/CMYK files are refused. Symlinks, aliases, special files, duplicate names and sources already inside the selected document's Resources folder are refused. These are Connector policy limits, not Hype's general limits.

Success returns `imported:true`, the actual `resource` row, `grouping:"native"`, and `changedGroups`. Do not manufacture a group for CSS/JavaScript when the returned group is null. `resourceGroup.rename` takes `document`, `group`, nonempty `name`; re-read actual filenames afterward. `resource.setHeadIncluded` takes `document`, `resource`, Boolean `included` and applies to CSS/JavaScript. Save separately.

To place an image:

1. Import it and retain the returned current-open resource ID, or discover an existing PNG/JPEG resource.
2. Prepare its root scene with `scene.settings.prepare`, `property:"width"`, `applyToMatchingLayouts:false`. Wait for readiness, including its animation controller.
3. Call `element.createImage` with `document`, `scene`, `resource`. Main must be selected and playback stopped. This call neither imports nor silently switches context.
4. Use the returned `element` projection, inspect native dimensions, and place it through supported attributes or inspector operations.
5. Save, reopen when persistence matters, and refresh the resource list before editing resources again.

Pixel size need not equal scene size: native density interpretation can produce a half-size logical image and 1x/2x export derivatives. `OriginalWidth`/`OriginalHeight` may normalize from a unit string to a number after save/reopen. Compare meaning, not JSON representation alone. Export bytes need not match the original JPEG. Referencing an image can change native `canRemove` to false. The named surface does not currently provide general resource replacement or deletion.

Import may update source metadata even if its contents stay the same. Post-dispatch failures have unknown outcomes; inspect resources and groups rather than retrying the import.

## Timelines and animation

`playhead.get` takes `document`, `scene` and optional expected `timeline`; Main is the default. The expected timeline must already be current; this operation does not switch timelines. `playhead.seek` adds `seconds` and requires playback stopped. Use the actual frame-quantized returned time in later guards, with only the documented float32 endpoint representation correction where needed. Named seek is bounded by the existing timeline duration; inspect that duration before planning a recorded point. Do not assume a newly created timeline is long enough.

`animation.get` takes `document`, `symbol`, `timeline`, `animation`. Use it after listing to inspect the property, element, easing and endpoint attribute values. A missing endpoint is null; an existing attribute with an empty value remains an attribute object containing `value:null`.

For new recorded motion, establish the baseline through the inspector at the initial time, prepare/read at the desired point, then set with `recording:true` on Main. Inspect the full resulting animation lane, save and read after reopening. Do not assume a particular number of rows or a synthesized UUID.

`animation.setTiming` takes the same context and animation identity, plus at least one of `startTime` or `timingFunction`. Discover an easing ID with `timingFunction.list`. Both inputs are validated before either edit. Moving start time through this model operation can also change duration to preserve the old end time. Re-read; this is not a guaranteed equivalent of dragging a keyframe in Hype.

`animation.delete` additionally requires `scene`. It selects the requested timeline/keyframe and invokes the editor deletion action. The scene must already display the requested symbol with playback stopped. Read surviving animation rows and endpoints: deletion can merge durations or update a baseline.

## JavaScript functions

`javascript.add` needs `document` and returns the new function's ID, name and source. `javascript.rename` and `javascript.setSource` take `document`, `script`, `value`; `javascript.delete` takes `document`, `script`. Renaming requires a JavaScript identifier matching `[A-Za-z_$][A-Za-z0-9_$]*`. Source must be a string and an explicit empty string clears it. Merely storing a function does not attach it to an event, execute it, or validate browser behavior. Follow a documented action-binding recipe for invocation, then test the exported interaction.

## Undo and synchronous diagnostics

`document.undoState` takes `document` and returns the exact state for `document.undo` or `document.redo` as `expectedState`. Copy the entire object unchanged, including Boolean flags and nullable counts. The state includes document/context, playhead, recording, action names, history eligibility, grouping and edited status. A stale state is refused.

The current root scene/Main context must already be initialized, playback stopped, no save pending and undo registration enabled. Undo allows grouping level zero, or the automatic event group at level one with `groupsByEvent:true`. Redo requires level zero. Do not close manual groups or enable registration to force the operation through. Read resulting model/animation state and save separately if wanted.

Undo is an extra diagnostic, not an atomic rollback or byte-for-byte restoration guarantee. Model setters need not register undo. Empty groups affect counts; names and counts do not uniquely identify an action. Do not use undo as cleanup after an uncertain mutation.

The native interface additionally supports explicit synchronous `call`/`set` undo wrapping and bounded notification/KVO tracing. Trace observations cover only the request's synchronous execution, not later run-loop work, asynchronous save or browser events. A missing trace event is not proof of no side effect. Loaded controller inspection can expose existing window/inspector objects; inactive panes or lazy popovers can be absent. Do not treat an absent object as a license to invent a selector or force-create a controller.
