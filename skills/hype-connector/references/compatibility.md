# Compatibility and interpreting results

## Qualified baseline

The current public guidance targets Connector 0.1.3, app build 15 and plugin build 14, with Tumult Hype 4.1.22 build 786. The app requires macOS 14 or later. Native workflows have been exercised on Apple Silicon and with the Intel executable under Rosetta. This is not physical Intel hardware qualification or a Hype 5 compatibility claim.

The catalog contains 50 service operations. Representative current-build workflows exercised each operation name, including the native escape hatch. That does not establish every property, argument combination, document structure, architecture or editor state. A successful catalog lookup establishes the request shape; runtime capabilities establish that the loaded plugin advertises it; a successful response establishes only that particular invocation's reported result.

Representative demonstrated workflows include:

- Model geometry, whole-element text and sRGB color edits; JavaScript function creation, rename, source update and deletion.
- Native element/scene insertion, duplication and grouping; responsive layout creation; separate scene inspector size, scaling and background changes.
- A width edit isolated to one of two sibling layouts, with both layouts' settings read after save/reopen.
- Main-timeline playhead control, one recorded position lane, easing/start-time edits and a terminal keyframe deletion. These do not establish arbitrary keyframe drag or deletion equivalence.
- PNG import and native image placement; CSS/JavaScript import and head inclusion; RGB JPEG behavior on representative images. Native save/reopen and HTML output were checked for these workflows.
- A recorded position edit followed by named undo and redo, with exposed element/animation state compared and saved/reopened. A separate border-width inspector example also exercised undo/redo.
- CLI, app-backed one-shot commands, MCP and Connector AppleScript workflows, including session selection and native save/reopen.
- Hidden-open template work, loaded-controller inspection and bounded native collection pagination.

The fixed-text-box and fractional-time helper refinements incorporate targeted observations. They do not establish that an independent agent run or every newly composed document passes. Examples should still include their own persistence and browser checks. Exporting valid files does not verify that a button fires, text fits, a transition is correct or a script runs.

## Limits that affect planning

| Area | Practical implication |
| --- | --- |
| Native API | Private editor objects can vary between Hype versions. Use named operations and known native recipes; discover and verify before a new native call. |
| Symbols and groups | Clearing selection does not exit nested editing. Named symbol entry/exit and persistent-symbol creation are not currently provided. Do not confuse model elements with display elements when using a documented native route. |
| Text | `text.set` replaces HTML without promising rich-text range editing or native auto-measurement. Fixed exported text boxes need `ExplicitDimensions:'YES'` as well as dimensions; the helper supplies this measured native flag. Check rendered bounds and scroll extents after the longest dynamic messages. |
| Animation | Named recording is Main-only. `animation.setTiming` is a model edit, not a calibrated drag gesture. Fractional endpoint guards can hit a float32/double boundary mismatch; the helper corrects only identical float32 representations. Do not extrapolate one property lane to all properties or all frame rates. |
| Scene geometry | Only selected-layout scope is supported by named scene settings. Resizing the stage does not proportionally reposition or resize elements. |
| Resources | Named import is bounded to CSS, JavaScript, PNG and RGB JPEG. Resource UUIDs can change after reopening. General resource replacement/deletion is outside the named surface. |
| Export | Named HTML export uses a narrow native writer contract. Export slices, advanced export choices and publishing do not become supported merely by adding guessed request fields. |
| Hidden windows | `display:false` is an opening preference. Editor controllers still need to load and some actions may expose UI. It is not a headless service guarantee. |
| Undo | Optimistic state guards and representative comparisons do not guarantee transactional rollback, dirty-flag restoration or history retention across reopening. |
| Trace | Synchronous notification/KVO observations were demonstrated on controlled objects. They do not enumerate all Hype events, prove absence of side effects or establish later asynchronous behavior. |
| Permissions | Saved folder selection can be reused by app-backed operations. Standalone CLI/MCP uses its launcher's access. No universal promise of prompt-free operation after updates or reboot. |
| Updates | Replacing the plugin on disk requires a new Hype process to load it. Connector does not quit Hype automatically. The current app's automatic update channel is not enabled. |

## Failure handling by category

**Schema or identity refusal:** correct the request only after reading the contract and rediscovering the intended object. Do not treat a wrong ID as an instruction to select another object with the same display name.

**Pending editor readiness:** wait for editor updates and deliberately repeat preparation. This differs from repeating a mutation: the pending response has not established a ready binding or claimed the requested content edit. Re-read the field after readiness.

**Changed expected value, playhead, session or undo state:** stop using stale context. Establish whether another actor or editor action changed it. Fresh discovery/readback is required before a deliberate new mutation.

**Unknown outcome or transport loss after dispatch:** preserve output and document state, inspect the intended effect and exact job when available, and do not retry automatically. Imports, insertion, saves and exports can have completed despite a missing reply.

**Successful mutation:** verify relevant projections, save explicitly, and check reopened state for persistence-sensitive work. For visual deliverables, inspect the actual export and test interactions. Numeric/model agreement alone is not visual equivalence.

## Keep experiments bounded

Work on a fresh copy unless the user requested in-place editing. Pin one intended host/session. Do not take over, close or restart another workflow's Hype instance. Keep the user's installed probes untouched. Report actual deliverables and which interactions were exercised, rather than describing a whole family as universally supported.
