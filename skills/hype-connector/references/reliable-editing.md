# Reliable named editing

The client commands `element.edit`, `scene.configure` and `animation.create`
compose existing named operations. They use no private selector fallback. A
current local catalog describes their request shapes, while the selected host's
`host.capabilities` exposes each in `operations` and `clientOperations` only when
its native prerequisites are available. Representative checks on Connector 0.1.5 cover scene size/background, position/width,
Left/Top/Opacity animation, duration preservation and save/reopen on arm64 Hype
4.1.22. An independent agent completed multi-scene authoring and revision plus
HTML and H.264 export using the skill and documentation. This does not qualify
every composed property, architecture or document structure.

| Command | Required native capabilities | Fields beyond `op` |
| --- | --- | --- |
| `element.edit` | `scene.settings.prepare`, `inspector.prepare`, `inspector.get`, `inspector.set` | `document`, `scene`, `symbol`, `timeline`, `element`, `property`, `value`; optional `seconds` (0), `expectedValue` |
| `scene.configure` | `scene.settings.prepare`, `scene.settings.get`, `scene.settings.set` | `document`, `scene`, `property`, `value`; optional `expectedValue`, `applyToMatchingLayouts:false` |
| `animation.create` | `scene.settings.prepare`, Inspector prepare/get/set, `timeline.list`, `timeline.setDuration`, `animation.list`, `animation.get` | `document`, `scene`, `symbol`, `timeline`, `element`, `property` (`Left`, `Top`, `Opacity`), numeric `from`/`to`, positive `seconds` |

`element.edit` and `animation.create` require `inspectorGuardedPreparation`;
their names are omitted from capabilities on older plugins. Use these composed
commands directly after rediscovery on reopen. They handle activation and the
requested cursor; a separate manual seek or close/reopen cycle is not required.

All accept optional `settleTimeout` 0–10 seconds, default 3, per readiness phase.
After successful inspector preparation, cursor/readiness observation gets its own
full budget. Native pane loading does not consume the subsequent quiet interval.
Only documented pending scene preparation and unavailable inspector reads are
polled. Only an explicit pre-dispatch `editor_not_ready` from inspector preparation
can activate the requested root layout via `scene.settings.prepare` (width,
`applyToMatchingLayouts:false`) before preparing again. This does not set width,
but changes the pane and persists selected-layout scope. Activation is reported
as `<prepare-step>.activateLayout`. It does not enter or exit nested symbols.
This is not an overall operation budget. An explicit pre-dispatch `inspector_controller_not_ready` waits for the document inspector within the same budget and retries preparation without layout activation. No controller is constructed or forced open. Mutations, changed contexts and
unknown outcomes are never automatically retried. MCP uses `hype_apply` with the
operation inside `request`; there are no dedicated composed-edit tools.

```json
{"op":"element.edit","document":"/absolute/New.hype","scene":"layout-id","symbol":"symbol-id","timeline":"kTimelineDefaultIdentifier","element":"element-id","property":"Top","value":80}
```

```json
{"op":"scene.configure","document":"/absolute/New.hype","scene":"layout-id","property":"width","applyToMatchingLayouts":false,"value":640}
```

```json
{"op":"animation.create","document":"/absolute/New.hype","scene":"layout-id","symbol":"symbol-id","timeline":"kTimelineDefaultIdentifier","element":"element-id","property":"Left","from":40,"to":300,"seconds":3}
```

Preparation first activates only changed context, then observes exact-target
readiness before one guarded seek to the requested time. Loading targets require
a stable cursor for 200 ms within `settleTimeout`; already-current targets retain
strict cursor guards. This avoids rescheduling Hype’s saved-cursor restoration.
It is not a native loading-complete flag: later context drift still refuses the
edit, and property writes are never retried. Readiness and guarded preparation
receipts remain available for diagnosis.

`element.edit` prepares and reads the inspector, then sets with a fresh native
expected-value guard and recording disabled. An optional caller `expectedValue`
must also match the settled value exactly. It supports the inspector properties
listed in [operations.md](operations.md#inspector-edits-prepare-read-change).
`LineHeight` requests use pixel numbers. The adapter also recognizes Hype's
presented CSS pixel string for that field, returning its numeric pixel value;
other units and selection markers remain refusals.
`scene.configure` edits one scene setting and establishes selected-layout scope
for size/scale. It does not scale element geometry or enable a scale flag before
a percentage edit. Establish that flag separately.

`animation.create` requires a previously empty target element/property lane,
distinct numeric endpoints and Main. Supported properties are `Left`, `Top` and
`Opacity`, with their existing inspector type/range rules. Other properties yield
`unsupported_property` before dispatch. This is a restriction of the composed
single-lane writer. `element.edit` and lower-level inspector operations retain
their documented property families. Aggregate fields can produce multiple native
lanes and are outside this procedure.
It grows duration only if needed and verifies the endpoint before changing the
baseline. The endpoint must match the native Float32 time on the editor's frame
grid. Arbitrary subframe times are refused, rather than silently shifted. It
records from zero and verifies the resulting transition plus terminal native row.
It never replaces existing animation or shortens duration.

Use a root/Main/stopped context for new authoring. The requested symbol must
already be displayed; these commands do not enter/exit nested symbols. Duration
extension inherits the duration command's context restrictions. Previous
selection, pane, playhead and duration are not restored. Native recording mode
restoration is verified.

## Receipts and recovery

### Text insertion and appearance

Use `editor.action` with `name:"insert.text"`. The current adapter returns the
new `element` and `textEditingFinished:true`: it finishes only the text-edit
session that this insertion opened. An existing active text edit is refused
before insertion. Do not replace this with a raw factory or manually end an
unrelated edit. Temporary text-editor values can differ from the saved element.

Set content with `text.set`, then use composed `element.edit` for typography
and geometry. New text can lack an `ExplicitDimensions` attribute, so do not
attempt to write that missing attribute through `element.setAttribute`. Establish
the box through the native width inspector first, then inspect `element.get`
for its resulting dimensions and `ExplicitDimensions:"YES"` marker. Set the
existing `Height` attribute only after that sizing step. Include enough height
for every line and native padding. Check the final projection and exported appearance after
the full sequence, not only each inspector's immediate response. Set explicit
font size and text color for readable contrast. `LineHeight` is a pixel number.

For example, after discovering `scene`, `symbol`, Main timeline and the inserted
text ID, use `text.set` for the copy, `element.edit` for `FontSize:32`,
`TextColor` with an sRGB marker, and `LineHeight:40`. For two lines choose a box
height that fits both lines plus padding. Validate the result after selecting a
different element and after save/reopen, when temporary text-edit state can no
longer hide a stale model value.

### Completion and partial failure

These are sequential procedures, without atomicity, rollback, an exclusive editor
lock or automatic save. Success returns `workflow`, `context`, `completedSteps`
and keyed `receipts`. Element/scene edits add the final setter `result`.
Animation creation adds full native `animations`, `animationIDs`,
`requestedSeconds`, actual `seconds`, `fromValue` and `toValue`.

Failure preserves `failedStep`, `completedSteps`, `receipts`, `context`,
`mayHaveSideEffects`, `contextPreparationAttempted` and
`contentMutationAttempted`, alongside the original error. A later refusal can
follow earlier content changes, for example a duration extension before an
endpoint alignment failure. Preserve the envelope, inspect the completed steps
and fresh element/timeline/animation state, then decide on one deliberate next
action. Do not repeat the whole procedure, clear partial content or use undo as
failure cleanup. Save explicitly after the intended state is verified.

## Create, discover, edit, animate, save and export

This example uses only the small `Connector` transport client in
`skills/hype-connector/scripts/connector_client.py`, not `authoring.Document` or
the native bridge. It creates a fresh displayed document, identifies an inserted
rectangle through complete inventories, edits its position and creates motion.
Capture stdout/stderr as the run receipt. Pass the actual skill `scripts` directory, CLI path, selected owned PID and fresh
absolute document/HTML paths. Output parents must already be accessible. Follow
workspace host-ownership rules before running it. No host is launched or adopted.

```python
# python3 named_rectangle.py SKILL_SCRIPTS CLI PID /output/New.hype /output/HTML
import json
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from connector_client import Connector

cli, pid, document, html = sys.argv[2:]
assert Path(document).is_absolute() and Path(html).is_absolute()
assert not Path(document).exists() and not Path(html).exists()
c = Connector(cli, int(pid))
c.discover()  # Pins the exact discovered session for this selected PID.

def run(op, **fields):
    result = c.run(op, **fields)
    print(json.dumps({'op': op, 'result': result}), flush=True)
    return result

required = {
    'document.create', 'layout.list', 'scene.list', 'element.list',
    'timeline.list', 'editor.action', 'element.edit', 'animation.create',
    'document.save', 'document.exportHTML',
}
assert required <= set(run('host.capabilities')['operations'])
created = run('document.create', destination=document, display=True)
assert created['created'] is True and created['saved'] is True
assert created['document'] == document
layouts = run('layout.list', document=document)['layouts']
scenes = run('scene.list', document=document)['scenes']
assert len(layouts) == len(scenes) == 1
layout, scene = layouts[0], scenes[0]
assert scene['id'] == layout['id'] and scene['symbol'] == layout['symbol']
timelines = run('timeline.list', document=document,
                  symbol=layout['symbol'])['timelines']
assert len(timelines) == 1
timeline = timelines[0]['id']
assert timeline == 'kTimelineDefaultIdentifier'

def elements():
    return c.page('element.list', 'elements', document=document,
                  symbol=layout['symbol'])

before = elements()
run('editor.action', document=document, scene=layout['id'],
      name='insert.rectangle', elements=[])
after = elements()
added = {r['id'] for r in after} - {r['id'] for r in before}
assert len(added) == 1 and len(after) == len(before) + 1
context = dict(document=document, scene=layout['id'], symbol=layout['symbol'],
               timeline=timeline, element=added.pop())
edit = run('element.edit', **context, property='Top', value=80)
motion = run('animation.create', **context, property='Left',
               **{'from': 40, 'to': 300, 'seconds': 3})
assert motion['seconds'] == 3 and len(motion['animations']) == 2
saved = run('document.save', document=document)
assert saved['saved'] is True
export = run('document.exportHTML', document=document, destination=html)
assert export['exported'] is True
print(json.dumps({'edit': edit, 'motion': motion, 'export': export}, indent=2))
```

The client stops on its first failed/uncertain response and retains the error
object; inspect its full receipt before using a fresh client for recovery. Keep
successful receipts with the deliverable. Check the actual exported page for
movement and layout, and reopen the saved package with fresh IDs when persistence
verification is required. Export can cause further native metadata/layout changes;
save separately if that resulting editable state belongs in the deliverable.
