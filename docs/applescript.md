# AppleScript

Connector supplies an AppleScript dictionary and forwards JSON operations to Hype. These examples address **Connector**; they do not require Hype to provide its own AppleScript commands.

Connector 0.1.6 automation uses the same [trial or paid app license](licensing.md). Start or activate it in Connector’s **License** section first.

Complete [installation](getting-started.md) and choose the Hype folder in Connector first. macOS may also ask whether your scripting app is allowed to control Connector. You can inspect Connector's dictionary in Script Editor.

## Discover a connection

```applescript
tell application "Connector"
    set responseJSON to perform operation "{\"op\":\"host.list\"}"
end tell
return responseJSON
```

The response is JSON text. Inspect or parse it to obtain the intended connection's PID and session. Use both for a multi-step workflow:

```applescript
tell application "Connector"
    set responseJSON to perform operation "{\"op\":\"document.list\"}" host pid 12345 host session "SESSION-FROM-DISCOVERY"
end tell
return responseJSON
```

Replace the placeholders with discovered values. Without selectors, an ordinary app launch chooses the sole available Hype each time a request executes. Keeping selectors fixed prevents the script from changing targets if another Hype starts or the editor restarts.

## Queue a longer operation

Use `submit operation` for a save or other operation that may take time:

```applescript
tell application "Connector"
    set jobID to submit operation "{\"op\":\"document.save\",\"document\":\"/absolute/working-copy.hype\"}" host pid 12345 host session "SESSION-FROM-DISCOVERY"
    set statusJSON to job status jobID
end tell
return {jobID, statusJSON}
```

This snippet submits the save and reads its status once. A returned job ID is **not** confirmation that the save reached disk. Keep the job ID and query its status again while pending:

```applescript
tell application "Connector"
    set statusJSON to job status "JOB-ID-FROM-SUBMISSION"
end tell
return statusJSON
```

Parse the JSON, wait for completion and check the operation's result. Only after the job is finished and its result has been handled, release its record:

```applescript
tell application "Connector"
    set releasedJSON to job status "COMPLETED-JOB-ID" releasing true
end tell
return releasedJSON
```

Use a JSON parser for result handling rather than searching the text for words such as `true` or `saved`. These app job IDs belong to the running Connector app. They are separate from native job IDs inspected by the named `job.get` operation. Connector refuses a normal quit while an app-owned job or helper is active.

## Build on the shared operations

The JSON inside `perform operation` or `submit operation` follows the same contracts as the [CLI](scripting.md). Use absolute document paths and IDs discovered from the selected document. For generated requests, serialize JSON correctly before passing it as AppleScript text, especially when values contain quotes or backslashes.

Stage a copy, discover its layouts and elements, apply one change at a time, then save explicitly. A timeout or `outcome_unknown` result requires inspection before another decision. Submitting the same mutation again is not a safe way to check whether the first one succeeded.
