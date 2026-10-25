# Building a complete example

Plan a small, coherent composition before sending calls. Native Hype text, shapes, image elements and buttons remain editable. Use a few repeated helper functions for typography and buttons. Keep body text readable, avoid decorative labels with no purpose, and give the layout enough space for its actual copy. A collection of default rectangles is an API smoke test, not a finished design.

Read [native recipes](native-recipes.md) and the two Python helpers first. They supply connection handling, first save, scene insertion, native attributes, action binding and short motion. Use [operation families](operations.md) for named import, layouts and inspector contracts.

## Compose several scenes

```python
# c is a discovered, pinned Connector client. Paths are chosen by the caller.
doc = Document.create(c, output_hype)
start = doc.layouts()[0]
doc.name_scene(start, 'Start')
story = doc.add_scene('Story')
participate = doc.add_scene('Participate')
for scene in (start, story, participate):
    doc.setting(scene, 'width', 1200)
    doc.setting(scene, 'height', 800)
    doc.setting(scene, 'backgroundColor', color('#F3EAD5'))

borderless = {'BorderWidth'+side: 0 for side in ('Top','Right','Bottom','Left')}
def text(scene, name, content, x, y, w, h, size=26, **extra):
    return doc.text(scene, name, content, x, y, w, h, size=size,
                    ink='#18372B', **extra)
def button(scene, name, label, x, y, w=260):
    return doc.element(scene, 'button', name, x, y, w, 58,
        InnerHTML=label, FontFamily='Arial', FontSize=22, FontWeight='700',
        LineHeight=58, TextAlign='center', TextColor=color('#F3EAD5'),
        BackgroundColor=color('#18372B'),
        PaddingTop=0, PaddingBottom=0, PaddingLeft=0, PaddingRight=0,
        **borderless)

text(start, 'Title', 'Something worth<br>staying for.', 64, 140, 820, 210,
     size=76, FontWeight='700', LetterSpacing=-3)
to_story = button(start, 'Story navigation', 'Read the story', 64, 590)
to_action = button(start, 'Participate navigation', 'Take part', 350, 590)
doc.go(start, to_story, story, transition=5)
doc.go(start, to_action, participate, transition=2)
back = button(story, 'Return', 'Back', 64, 680, 160)
doc.go(story, back, start, transition=4)
# Fill story and participate with real content, then add a return route there too.
```

This demonstrates composition syntax, not a mandatory design style. Scene names can be changed without changing their IDs. Native buttons can have default border, padding and state appearance; set intended values and check hover/click visually. Text boxes need enough height for all lines and native `ExplicitDimensions:'YES'` when width/height are intended to stay fixed. `Document.text` supplies it; direct text construction must supply it deliberately. Width/height model values alone are insufficient to establish export sizing. Use explicit pixel line height, and avoid typography that depends on fonts absent from the export viewer.

## Button styling without breaking Hype positioning

For native buttons, first consider Hype's own normal/hover/pressed state styling and native animations through the discovered Connector interface. Use those when they express the requested behavior and keep it editable in Hype. Custom head CSS is an additional option, not a required replacement for native button states.

Hype can position a native element with an inline `transform: matrix(...)` or translation. A rule such as `:active { transform: translateY(5px) !important; }` replaces that entire positioning transform. The button can jump toward the scene origin while pressed and return after release. This affects hover rules, CSS animations and JavaScript assignments too. Do not overwrite `transform` or `-webkit-transform` on the Hype-managed node for a decorative effect. Use Hype's native timeline/runtime APIs for intended scene movement. Do not add a CSS `top`/`left` offset assuming Hype's position is stored there.

For a raised button, assign a known `DomID`, set explicit native dimensions (for example 280 × 68), zero all four native padding values, and set `ExplicitDimensions:'YES'`. Add styling through the Hype document head before export. This example targets only the chosen buttons:

```css
[id^="demo-button-"] {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-sizing: border-box !important;
  padding: 0 !important;
  line-height: 1.15 !important;
  text-align: center;
  border-radius: 18px;
  background-image: linear-gradient(rgba(255,255,255,.25), rgba(0,0,0,.06));
  box-shadow: 0 6px 0 rgba(70,35,20,.22), inset 0 2px 0 rgba(255,255,255,.4);
  transition: box-shadow .12s, filter .12s;
}
[id^="demo-button-"]:active {
  box-shadow: 0 2px 0 rgba(70,35,20,.22), inset 0 2px 3px rgba(70,35,20,.12);
}
@supports (translate: 0 3px) {
  [id^="demo-button-"]:active { translate: 0 3px; }
}
@media (prefers-reduced-motion: reduce) {
  [id^="demo-button-"] { transition: none; }
  [id^="demo-button-"]:active { translate: none; }
}
```

Independent CSS `translate` composes with the existing transform instead of replacing it. Use it only when that property is not already used by the document, and verify scaled/rotated layouts in the target browser. Shadow/color changes alone are the simplest fallback. An inner visual child is another option when it does not disturb the native action target. Use explicit transition properties, not `transition:all`, which can animate Hype's own position changes.

Verify the actual label center and outer button bounds after export. Native padding can enlarge the box beyond its nominal height. Leave space for the shadow and pressed travel between controls. For a stationary button, record its bounding box and computed transform, hold the pointer down, then release: the Hype transform should remain intact, with only the intended small local offset during the press. Repeat keyboard activation and a narrow layout. A screenshot taken after `click()` finishes does not prove that the pressed state stayed in place.

## Image placement

Provide an existing, readable PNG or RGB JPEG within Connector's limits. Asset creation is separate from Hype authoring and must follow the user's tool constraints. Do not silently substitute another Hype exporter or package editor.

```python
resource = doc.run('resource.import', path=str(image_path))['resource']
doc.prepare_scene(start)
image = doc.run('element.createImage', scene=start['id'], resource=resource['id'])['element']
doc.attributes(start, image['id'], {
    'DisplayName': 'Hero image', 'AltText': 'Describe the image',
    'Left': 760, 'Top': 0, 'Width': 440, 'Height': 800,
})
```

Do not stretch a photograph accidentally. Choose a matching crop or preserve its aspect ratio. Resource density can change logical dimensions; read placement values. Save/reopen and refresh resource UUIDs before further resource work. Import is not repeat-safe; do not rerun it into the same document after an uncertain outcome.

## Small local interactions

Create an output text element with an explicit `DomID`, and a complete function through `doc.script`:

```javascript
function chooseOption(hypeDocument, element, event) {
  var output = hypeDocument.getElementById('choice-result');
  if (output) output.textContent = 'You chose ' + element.textContent.trim() + '.';
}
```

Attach the returned function ID using `doc.run_script(scene, button_id, script_id)`. Build the result text as a fixed box with `ExplicitDimensions:'YES'`. Exercise the longest confirmation or error text the interaction can produce, including repeated choices. Check the runtime bounding box and horizontal/vertical scroll extents after the text changes. Increase the native box or revise the composition if the text overlaps, clips or escapes its intended region; an initially short placeholder is not a sufficient check. For a demo with no service, make clear that submission/purchase is simulated and keep the interaction local. Native mouse actions do not automatically establish keyboard accessibility. If needed, add keyboard/focus handling through the document's head content or Hype functions and verify it in the export. Do not claim accessibility from button-shaped text alone.

## Motion and responsive behavior

For a new decorative element, `doc.record(scene, element, 'Top', start_y, end_y, 1.0)` records native position motion on Main. Use a common duration for multiple helper calls. Fractional endpoints use the documented float32 guard in `Document.record`, which preserves the same native cursor identity. Inspect returned rows, and test the actual export. Scene transitions and timeline motion are separate features. Do not make every piece move; animate where it helps attention or orientation.

A fixed 1200×800 stage is not a responsive layout by itself. Named scene scaling can scale its container but does not automatically reflow element geometry. For real alternate layouts, use `layout.add` with discovered IDs and prepare each layout independently. If using head CSS for surrounding viewport behavior, apply it in Hype before export and test narrow as well as desktop viewports. Report a fixed-stage limitation honestly when no alternate layout was built.

## Finish and prove the result

1. Read complete scene, element, JavaScript and animation lists. Check names, action targets and actual geometry. Do not infer a successful insertion from a command count.
2. `doc.save()` must confirm completion. `doc.export(new_export_directory)` needs a new path with an existing Hype-writable parent. Save again if export changed native state you want persisted.
3. For a persistence check, close only your saved working document, reopen the exact path, rediscover IDs/handles and read the meaningful projections. Never reuse resource UUIDs or handles after the relevant lifetime ends.
4. Serve the unchanged export locally and inspect each scene at its intended size. Test every navigation route, each local interaction, motion and browser errors. Hold styled buttons down to inspect their active state before releasing, then verify keyboard activation. For text and dynamic feedback, measure live bounding boxes and `scrollWidth`/`clientWidth` plus `scrollHeight`/`clientHeight` after the longest messages. Check computed wrapping, clipping, neighboring controls and scene edges. Account for transforms, borders and padding. Take screenshots of the actual interaction states, not an independent mockup.
5. Deliver the editable `.hype`, native HTML export, reproducible builder script, small README and screenshots. A `.hype.zip` must contain exactly one top-level `.hype` package, with `data.plist` and `Resources` directly inside that package. Keep README and screenshots outside that ZIP. Verify extraction structure.

A script is reproducible when it discovers new IDs and accepts paths/host selection. Hardcoded transient object references are not a recipe. Write generated assets and build outputs to the user's requested location; never edit the skill installation to store one example's state.
