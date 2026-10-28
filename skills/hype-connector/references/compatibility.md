# Compatibility and interpreting results

## Supported version and scope

Connector 0.1.5 requires macOS 14 or later and targets Tumult Hype 4.1.22,
build 786. Representative workflows have been checked on Apple Silicon and
using the Intel executable under Rosetta. Physical Intel hardware and other Hype
versions have not been qualified. Native H.264 movie export and the newer
external-access and composed-editing workflows have been checked on Apple
Silicon; Intel runtime support for those workflows remains unqualified.

Read the selected host's capabilities before using an operation. Updating the
app does not replace a plugin already loaded in Hype. The local catalog describes
request shapes, capabilities describe the loaded plugin's advertised support,
and a successful response describes that particular invocation's result. These
do not qualify every argument, property, document structure or editor state.

Connector 0.1.5 includes these named workflows, subject to the limits below:

- Create a displayed or initially hidden document, save it, save a separate copy,
  and export HTML to a fresh destination. Supported external-access operations
  transfer the client's existing parent permission through temporary bookmarks.
  Broader lazy media/resource reads after an open scope ends remain unqualified.
- Change inspector fields with `element.edit`, selected-layout settings with
  `scene.configure`, and record a new Left, Top or Opacity lane on Main with
  `animation.create`. Read the [reliable editing recipes](reliable-editing.md)
  for required context, receipts and partial-failure handling.
- Set a positive explicit timeline duration with `timeline.setDuration` and a
  fresh expected value. Zero/reset, stale-value and below-content requests are
  refused. Duration shortening and broader numerical precision cases remain
  qualification gaps.
- Export H.264 MP4 from a displayed document without audio. Movie qualification
  covers representative 8, 30 and 60 fps exports, cancellation and observation
  after timeout. Hidden-window export, audio, other codecs and Intel movie
  export remain unqualified.

Other supported operation families include model geometry, whole-element text,
sRGB colors, document JavaScript, native element/scene insertion, responsive
layouts, scene settings, Main-timeline playhead and animation timing, PNG/RGB
JPEG import and CSS/JavaScript resources. Named undo/redo is available for suitable
editor actions. Each family has its own context requirements and limits.

Check saved and reopened state for persistence-sensitive changes. Exporting a
valid file does not establish that text fits, a button fires, a transition looks
right or a script runs. Inspect the actual export and test its interactions.

## Limits that affect planning

| Area | Practical implication |
| --- | --- |
| Native API | Private editor objects can vary between Hype versions. Use named operations and known native recipes; discover and verify before a new native call. |
| Symbols and groups | Clearing selection does not exit nested editing. Named symbol entry/exit and persistent-symbol creation are not currently provided. Do not confuse model elements with display elements when using a documented native route. |
| Text | `text.set` replaces HTML without promising rich-text range editing or native auto-measurement. Fixed exported text boxes need `ExplicitDimensions:'YES'` as well as dimensions; the helper supplies this measured native flag. Check rendered bounds and scroll extents after the longest dynamic messages. |
| Animation | Positive explicit duration uses `timeline.setDuration` when advertised, with fresh `expectedDuration`. Raw zero can mean automatic duration, and zero/reset requests are refused. Named recording is Main-only. `animation.setTiming` is a model edit, not a calibrated drag gesture. Fractional endpoint guards can hit a float32/double boundary mismatch; the helper corrects only identical float32 representations. Do not extrapolate one property lane to all properties or all frame rates. |
| Scene geometry | Only selected-layout scope is supported by named scene settings. Resizing the stage does not proportionally reposition or resize elements. |
| Resources | Named import is bounded to CSS, JavaScript, PNG and RGB JPEG. Resource UUIDs can change after reopening. General resource replacement/deletion is outside the named surface. |
| Export | Named HTML export uses a narrow native writer contract. Native H.264 MP4 export requires advertised support: Hype 4.1.22 build 786, displayed document, no audio, duration up to 30 seconds, integer FPS 1–60, scale 1 and even first-scene dimensions at most 1920 × 1080. Three seconds at 30 fps includes 91 frames. Check advertised support before promising a movie. Export slices, advanced export choices and publishing do not become supported merely by adding guessed request fields. |
| Hidden windows | `display:false` is an opening preference. Editor controllers still need to load and some actions may expose UI. It is not a headless service guarantee. |
| Undo | Optimistic state guards and representative comparisons do not guarantee transactional rollback, dirty-flag restoration or history retention across reopening. |
| Trace | Synchronous notification/KVO observations were demonstrated on controlled objects. They do not enumerate all Hype events, prove absence of side effects or establish later asynchronous behavior. |
| Permissions | Saved folder selection can be reused by app-backed operations. Hosts advertising ephemeral access can receive the client's existing parent access for create/copy/HTML/video and open/save. This grants no new client permission or permanent Hype access; resource import remains separate. Standalone CLI/MCP uses its launcher's access. No universal promise of prompt-free operation after updates or reboot. |
| Updates | Replacing the plugin on disk requires a new Hype process to load it. Connector does not quit Hype automatically. Connector 0.1.5 includes signed automatic updates through GitHub. Version 0.1.3 needs one manual app upgrade. App updates preserve an explicitly selected Hype connection and use the saved folder access to update an older installed plugin. |

## Failure handling by category

**Schema or identity refusal:** correct the request only after reading the contract and rediscovering the intended object. Do not treat a wrong ID as an instruction to select another object with the same display name.

**Pending editor readiness:** wait for editor updates and deliberately repeat preparation. This differs from repeating a mutation: the pending response has not established a ready binding or claimed the requested content edit. Re-read the field after readiness.

**Changed expected value, playhead, session or undo state:** stop using stale context. Establish whether another actor or editor action changed it. Fresh discovery/readback is required before a deliberate new mutation.

**Unknown outcome or transport loss after dispatch:** preserve output and document state, inspect the intended effect and exact job when available, and do not retry automatically. Imports, insertion, saves and exports can have completed despite a missing reply.

**Successful mutation:** verify relevant projections, save explicitly, and check reopened state for persistence-sensitive work. For visual deliverables, inspect the actual export and test interactions. Numeric/model agreement alone is not visual equivalence.

## Keep experiments bounded

Work on a fresh copy unless the user requested in-place editing. Pin one intended host/session. Do not take over, close or restart another workflow's Hype instance. Keep the user's installed probes untouched. Report actual deliverables and which interactions were exercised, rather than describing a whole family as universally supported.
