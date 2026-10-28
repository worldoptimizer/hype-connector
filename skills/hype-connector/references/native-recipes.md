# Native authoring recipes

These recipes bridge gaps in named operations using observed Hype 4.1.22 object contracts. They operate through Connector; they do not read or write a document's plist. Runtime selectors are private and version-sensitive. Read capabilities first and stop on an unexpected result. See [compatibility](compatibility.md).

## Use the small client

Add this skill's `scripts` directory to Python's module search path. Supply the executable and PID obtained from the environment or host discovery, not a guessed process. A provided ownership-checking executable wrapper is used exactly like the normal CLI.

```python
import sys
sys.path.insert(0, str(skill_directory / 'scripts'))
from connector_client import Connector
from authoring import Document, color, MAIN

c = Connector(connector_executable, selected_pid)
host = c.discover()                 # pins this host's plugin session
capabilities = c.command('capabilities')
contract = c.command('catalog', 'editor.action')
```

`run(op, **fields)` calls a named operation. `native(op, **fields)` sends a raw query. `invoke(target, selector, *args, retain=False)` returns the native `value` and checks error out-parameters. `page(op, key, **fields)` exhausts a named collection with advancing offsets. Errors stop this client; it does not automatically retry or replace the session. Keep a workflow log and save discovered IDs when developing a longer script.

To inspect after a failure, deliberately create a fresh client with the **same PID and session** and make only the necessary diagnostic reads first. Do not restart the failed builder or silently select another host. Named creation releases its completed job record after confirmed success; a release failure does not mean the save failed.

## Create and open a real editable document

Use an existing Hype-writable parent and a new `.hype` destination:

```python
doc = Document.create(c, new_document_path)
scenes = doc.layouts()
home = scenes[0]
doc.name_scene(home, 'Start')
details = doc.add_scene('Details')
```

`Document.create` uses `document.create` and verifies both `created:true` and `saved:true`, including the returned path. It leaves that named document open. It never closes and reopens an untitled copy or sets `fileURL` manually. Read capabilities first; a missing operation requires a compatible app/plugin, not an improvised first-save sequence.

Document handles are acquired lazily only when a native-only helper needs one. Named creation, scene settings and recording need no native handle. For a template, use `fixture.stage` and `document.open`, then `Document(c, returned_path)`.

Every scene in `layout.list` has an `id` for its controller/layout, `sceneContainer` for navigation and `symbol` for root content. `name_scene` names the scene container. Responsive layout names are separate.

## Create native elements and attributes

```python
title = doc.text(home, 'Headline', 'A new scene', 64, 80, 800, 100,
                 size=64, ink='#182821', FontWeight='700')
panel = doc.element(home, 'rectangle', 'Panel', 64, 240, 700, 300,
                    BackgroundColor=color('#D8E8B8'))
doc.attributes(home, panel, {'Left': 90, 'Opacity': .9})
```

The helper inserts through `editor.action`, exhausts before/after inventories and requires exactly one new element. It finds the native object through the scene's current root symbol and `allElements`, using native `find` on the known getter `oid`. A nested symbol mismatch is refused.

To introduce or batch-set known attributes, use `HypeAttribute.attributeWithName:objectValue:` for each name and value, then `HypeElement.setAttributes:` with those returned attribute objects. The factory accepts names; success alone does not prove Hype uses an invented attribute. Use demonstrated names, read back and inspect export. `setAttributes:` returning false can mean no change. Mark the document changed with `updateChangeCount:0` and save explicitly.

Useful measured names include geometry `Left`, `Top`, `Width`, `Height`, `Opacity`, `RotationAngleZ`; text `InnerHTML`, `FontSize`, `FontFamily`, `FontWeight`, `LineHeight`, `LetterSpacing`, `TextAlign`, `TextColor`, `ExplicitDimensions`, `WhiteSpace`; styling `BackgroundColor`, `PaddingTop`, `PaddingRight`, `PaddingBottom`, `PaddingLeft`, `BorderWidthTop`, `BorderWidthRight`, `BorderWidthBottom`, `BorderWidthLeft`; and `DisplayName`, `DomID`, `AltText`. Inspector property `TextAlignment` and model attribute `TextAlign` are different spellings.

Colors use `{"$color":[r,g,b,a],"space":"srgb"}`. `color('#RRGGBB')` and `color('#RRGGBBAA')` produce that marker. Text `LineHeight` is a pixel value, for example 30 for 24px text, **not** 1.25. Geometry can be content-box geometry with border and padding added; check actual export dimensions.

## Fixed text boxes and dynamic messages

For a text box with explicit width and height, set the native attribute `ExplicitDimensions` to the **string** `'YES'` as well as `Width` and `Height`. `Document.text` includes this default. If constructing text with `Document.element(..., 'text', ...)` or changing an existing element through the attribute factory, include it explicitly:

```python
doc.attributes(scene, text_id, {
    'Width': 420, 'Height': 105, 'ExplicitDimensions': 'YES',
    'LineHeight': 30,
})
```

Native `Width` and `Height` values alone do not prove the exported text has fixed dimensions. An observed text element without `ExplicitDimensions` exported without CSS width/height and with `white-space: nowrap`; a longer runtime confirmation expanded beyond its intended box. A native Width inspector edit established `ExplicitDimensions:'YES'`, after which the export used the fixed dimensions and wrapping. `Display:'block'` alone and `WhiteSpace:'normal'` alone did not establish that fixed-box behavior.

The observed native default for `HypeAttributeWhiteSpace.defaultObjectValue` is `pre-wrap`. Do not override it as a substitute for fixed dimensions. The model flag is a measured private attribute, not an asserted GUI checkbox. Hype's public documentation describes automatic text sizing and says that manual resizing fixes an element's size. [Tumult Hype text documentation](https://tumult.com/hype/documentation/v4/#text)

A fixed box still needs enough height. It does not shrink text, guarantee that a long unbroken token wraps, or prevent clipping. After export, trigger the longest real dynamic message and inspect the live element's bounding box, computed width/height and `white-space`, and `scrollWidth`/`clientWidth` plus `scrollHeight`/`clientHeight`. Inspect surrounding controls and the scene boundary as well. Compare bounding boxes with allowance for scale, padding and borders. Native readback and an initial screenshot cannot replace these interaction-state checks.

## Attach native button actions

```python
button = doc.element(home, 'button', 'Details button', 64, 600, 250, 50,
                     InnerHTML='See details', FontSize=22, LineHeight=28)
doc.go(home, button, details, transition=2, duration=.65)
```

The helper creates `HypeAction.actionWithPlistRepresentation:` with a plain dictionary, checks `plistRepresentation`, and sets the known `ActionHandlerOnMouseClick` attribute to `{"actions":[ACTION_REF]}`. The selector's name refers to native serialization; no plist file is edited. Plain action dictionaries alone do not replace the required HypeAction objects.

Navigation dictionary: `{"type":1,"sceneOid":TARGET_SCENE_CONTAINER,"transition":2,"duration":0.65}`. JavaScript dictionary: `{"type":4,"javascriptOid":FUNCTION_ID}`. The function must belong to this document. These bindings persist through native save/export.

| Transition value | Meaning | Verification |
| --- | --- | --- |
| 1 | Instant | Identified in editor contract |
| 2 | Crossfade | Export interaction exercised |
| 3 | Swap | Identified in editor contract |
| 4 | Push left to right | Export interaction exercised |
| 5 | Push right to left | Export interaction exercised |
| 6 | Push bottom to top | Identified in editor contract |
| 7 | Push top to bottom | Identified in editor contract |
| 8 | Page turn | Export interaction exercised |

## Document JavaScript and head content

Use Hype's own function template. `javascript.add` already returns the native source, including the two comments explaining `element` and `event`. These comments are ordinary editable source, not a separate header file. Do not discard them by writing a bare function over the whole source.

Prefer the body-only helper, which fills the empty template returned by Hype and keeps its header and signature:

```python
script_id = doc.script_body('showMessage', "\tconsole.log('Hello from Hype');")
doc.run_script(scene, button_id, script_id)
```

The existing `doc.script(name, source)` helper still accepts a complete named function with `(hypeDocument, element, event)` and now retains the native header too. Additional supplied comments are retained inside the function. Neither helper rewrites JavaScript body whitespace, which can be meaningful inside template literals. A nonempty or unexpected native template stops the operation; inspect the already-created function before any retry. These helpers are not JavaScript syntax validators.

For an existing function, read `javascript.list` first. Preserve its comments, wrapper and unrelated code, including user changes. The helper below replaces exactly one occurrence and refuses a changed source or an ambiguous match:

```python
row = next(r for r in doc.run('javascript.list')['scripts'] if r['id'] == script_id)
doc.replace_script_text(script_id, "'Hello from Hype'", "'Welcome back'",
                        expected_source=row['source'])
```

This is a read-before-write check, not an atomic editor lock. Avoid concurrent edits. `javascript.setSource` remains an explicit full-source replacement at the low level; it does not merge or protect comments by itself.

Use `DomID:'choice-result'` on an output element, then `hypeDocument.getElementById('choice-result')` in the function. Storing source does not attach a click event. A navigation action and a JavaScript action are separate; deliberately construct a multiple-action array if both are intended.

Document head HTML is separate from function source. Read `headHtml` even for a new document and preserve the returned content. Add or update only your own clearly delimited block, keeping existing comments, script/style tags and user formatting. Exact document selector `setHeadHtml:` replaces the full head string, followed by `doc.dirty()` and save. Inspect again before writing if another editor may have changed it. Native element attributes should provide the main design. Do not replace the export with hand-authored HTML. External scripts/styles can instead use named resource import and head inclusion.

## Record simple native motion

```python
receipt = doc.record(home, panel, 'Top', 270, 240, 1.0)
```

`Document.record` now calls `animation.create`. It returns the complete workflow receipt, including the verified animation projections, instead of the legacy bare row list. It accepts a new Left, Top or Opacity lane on Main, refuses an existing lane, preserves a longer timeline and checks native recording restoration. Read [reliable editing](reliable-editing.md) for contracts and partial-failure handling. It does not use private duration selectors. A non-frame-aligned endpoint is refused and may leave an earlier duration extension, reported in completed steps.

`Document.duration` uses `timeline.setDuration` with a freshly read expected duration. This explicitly requested duration operation can shorten a timeline when the named API permits it; `Document.record` never does so. `Document.setting` delegates to `scene.configure`, and `Document.edit` delegates to `element.edit`.

`MAIN` is `kTimelineDefaultIdentifier`. Frame quantization is authoritative. Read actual returned times and animation rows, save and test playback. Do not promise arbitrary properties are recordable merely because geometry was exercised.

### Fractional endpoint guards on current plugins

The native cursor uses float32 while the current plugin's duration bound is compared as a double. At a timeline end of `1.1`, preparation can return `1.100000023841858`. Passing that exact number back can produce `time_range` even though it identifies the same native cursor position.

`timeline_guard_seconds(actual, duration)` handles only this representation mismatch. It returns `actual` unchanged when it is within duration. If it is above duration, it substitutes duration **only when both numbers have identical float32 bytes**; otherwise it raises an error. Both values must be finite and nonnegative. `Document.time_guard(scene, actual)` reads the current Main duration before applying that rule, for callers of the low-level inspector API. The composed `animation.create` handles this internally.

For an explicit inspector workflow on Main, use `seconds=doc.time_guard(scene, returned_seconds)` with both `inspector.get` and `inspector.set`. Keep the actual returned cursor in diagnostics. This does not move the playhead, lengthen the timeline, relax context matching or round to another frame. Do not replace it with a broad epsilon, general decimal rounding or an automatic retry after a failed mutation. For another timeline, discover that timeline's actual duration and apply the same pure helper deliberately. This compatibility rule is not a claim that every fractional endpoint or frame rate has been qualified.

## Native introspection without dumping everything

Raw requests below go through `c.native` or CLI `native`, not named `run`:

- `members`: `target`, `kind:"method"` or `"property"`, `search`, `scope:"instance"`, `inherited:true`, `offset`, `limit`. A class target is `{"class":"HypeElement"}`. Advance member offset by returned member count while `hasMore`; this operation has no `nextOffset`. Runtime KVO subclasses may require inherited members.
- `map`: an acquired collection `target`, known getter `name`, `offset`, `limit`. Returns plain `items`, `scanned`, `nextOffset`, `hasMore` without retaining every element.
- `find`: collection `target`, `where:{"oid":ID}` or another known getter, `offset`, `limit`, `scanLimit`. Follow offsets even after an empty scan page. Matching `items` are retained references.
- `controllers`: exact document `target`. Returns loaded window/inspector objects, controls and actions, plus errors/truncation. It may load views through getters. Inactive popovers can be absent. Never invent or allocate inspector controllers to fill that gap.

`call` uses `target`, `selector`, positional `args` and `retain`. Prefer `retain:false` for strings, numbers, dictionaries and projections; unsupported objects become opaque markers. Use `retain:true` when you need a callable object reference. `$url` accepts a properly encoded file URL. `$literal` wraps a dictionary that would otherwise be interpreted as a bridge marker. `$out:"NSError"` occupies a known error-pointer argument; inspect both return value and `out`, which is indexed by argument position.

Handles belong to one session and the same object can return the same handle. The table is bounded at 8192. Release only references you know your workflow no longer needs, never all references in a shared session. The helper releases newly created detached attribute/action objects after assignment, while keeping document/context references alive. Plain conversion is bounded; a truncated collection is not a complete inventory.

These helpers target bounded example documents, not unlimited batch creation. Context and collection handles remain retained for the workflow. Long-running services should explicitly track their own references, handle shared references correctly and release finished work; do not assume a Python object going out of scope releases a native handle.

For diagnostics, a native synchronous call can include `undo:{"document":DOC_REF}` and explicit `trace` notification names or KVO target/keyPath pairs. These observe one request only, not async save or later browser events. A balanced undo group does not cause a model setter to register an action. Prefer the named guarded undo workflow described in [operation families](operations.md).
