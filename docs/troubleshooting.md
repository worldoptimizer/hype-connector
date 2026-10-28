# Troubleshooting

## Connector cannot find Hype

Open Connector normally, select Hype's existing support folder and confirm that its plugin is installed. If installation happened while Hype was running, save your work and restart Hype to load it. A new plugin on disk does not change an existing process.

With multiple running Hype instances, choose the correct version and document names in Connector. In scripts, use `hosts` and pin both the PID and session. Do not terminate all Hype processes to resolve selection.

## macOS asks for access again

Connector saves the folder selection used by app operations, AppleScript and explicit app MCP mode. If the grant is missing or invalid, choose the folder again in the normal app. A saved folder grant does not grant Hype access to every external document or export directory.

The standalone CLI uses its launching process's access. A terminal, an agent and the Connector app can therefore have different permissions. Try the app command mode when you want to reuse the app's saved selection:

```sh
'/Applications/Connector.app/Contents/MacOS/ConnectorApp' --run-operation '{"op":"document.list"}'
```

A successful version or catalog command reads local information and does not prove that Hype's folder is accessible. Repeatedly restarting Hype will not fix a missing grant. Do not disable macOS protections or remove security attributes to work around access errors.

## An operation is missing

Compare the local `catalog` with the selected host's `capabilities`. The catalog describes the installed app; capabilities describe the plugin loaded in Hype. Update Connector's plugin, then save and restart Hype when convenient.

Connector 0.1.5 targets Hype 4.1.22/build 786 on macOS 14 or later. Other versions or unusual editor contexts may refuse operations. Report the Connector version, Hype version, operation name and sanitized error when seeking help.

## The session changed

Stop the workflow. Hype may have restarted or the selected process may no longer be the same connection. Discover a fresh connection and inspect your working copy before starting another deliberate run. Do not replace the pinned session halfway through a partially completed workflow.

## Inspector preparation is pending or stale

Preparation, reading and setting are separate calls. Preparation can return a pending state while the editor initializes its bindings. Wait for editor updates and inspect the context; deliberately prepare again if appropriate. A preparation receipt does not guarantee that a value is ready to edit.

Use the actual time and value returned by `inspector.get`. A stale `expectedValue`, changed selection, wrong timeline or unavailable field should stop the edit. Missing values are not zero. For the included templates, use one layout with its root symbol active, Main selected and playback stopped. Clearing selection does not exit a nested group or symbol.

## A save or export timed out

An `outcome_unknown` error means the action may have happened. Preserve the reported working-copy path and inspect the document and destination. Do not automatically repeat the save or export. Earlier successful operations remain applied even when a later step fails.

A `save_failed` response may include a native error object, a `job` ID and `mayHaveSideEffects:true`. Preserve these details. If supplied, use `job.get` with that exact native job ID to inspect its result. Release a completed native record with `release:true` only after handling the result. Releasing the record does not reverse filesystem changes.

For example, after replacing the placeholder with a returned native job ID:

```json
{"op":"job.get","job":"RETURNED-NATIVE-JOB-ID"}
```

```json
{"op":"job.get","job":"RETURNED-NATIVE-JOB-ID","release":true}
```

AppleScript's submitted jobs use the separate `job status` command instead. Never substitute an AppleScript app job ID into native `job.get`.

## Output already exists or is not writable

Use a new package path for `document.saveCopy` and a new directory path for `document.exportHTML`. Their parent directories must already exist and be writable by Hype. Keep outputs outside the source and working packages. Choose an accessible external staging parent for large documents.

## Saved values differ from requested values

Read back the result. Hype may quantize the playhead to frames, change text dimensions during layout, normalize colors and image attributes, or change animation duration when its starting time moves. Resource UUIDs can change after reopening a document, so refresh them with `resource.list`.

Model attribute setters and inspector actions serve different purposes. Do not infer inspector side effects or automatic keyframe creation from a model write. Undo history is useful for individual editor actions but is not a rollback guarantee for an entire script.

## An example stops before finishing

The examples deliberately stop on a refusal, incomplete inventory, mismatch or uncertain outcome. They print the preparation or working-copy paths as soon as those exist. Inspect those copies and any output before running again. A new run starts another copy; it does not resume or roll back the earlier run.

Review [example prerequisites](examples.md), including a single root layout, timeline duration and asset limits. Keep all three Python files together because they share helpers.

## An HTML export looks wrong

A successful export confirms native output generation. Inspect the exported page in your browser for appearance, playback and custom JavaScript behavior. Save the editable document explicitly if you want native layout changes after export persisted as well. A save/export receipt is not a visual browser test.

When reporting an issue, use a minimal document you are comfortable sharing. Remove private content, local usernames, credentials and unrelated file paths from logs or screenshots before posting them publicly.
