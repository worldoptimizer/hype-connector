# Connect an MCP client

Connector lets an MCP-capable client discover Hype documents, inspect their content and make explicit editor changes. It communicates locally over standard input/output. It does not expose a public network service.

Connector 0.1.6 automation uses the same [trial or paid app license](licensing.md). Start or activate it in Connector’s **License** section first.

First complete [installation](getting-started.md), select Hype's folder in Connector and load the plugin in Hype. Keep a small disposable document available for your first session.

## Server configuration

In Connector, use **Automation → MCP configuration** and copy the generated configuration into your client's MCP settings. The app provides its actual installed executable path. A standard installation uses:

```json
{
  "mcpServers": {
    "hype-connector": {
      "command": "/Applications/Connector.app/Contents/MacOS/ConnectorApp",
      "args": ["--mcp-stdio"]
    }
  }
}
```

This is the command/arguments configuration for clients using the `mcpServers` format. If your client uses another format, add a local stdio server with the same executable and arguments. Codex and Claude Code can use this local server. Their settings interfaces and configuration formats may differ.

Run the executable directly. Launching it through `open -a` does not preserve MCP's standard input/output connection. This explicit MCP mode opens no Connector window. The normal Connector app may stay open alongside it.

App MCP reuses Connector's saved folder selection. If it reports missing or invalid access, open the normal app and choose the folder again. It does not open a background permission chooser. The alternative standalone `connector mcp` mode uses its launcher's access rather than that saved selection.

## Tools and discovery

| Tool | Purpose |
| --- | --- |
| `hype_hosts` | Discover running Hype connections |
| `hype_capabilities` | Read the selected plugin's available operations |
| `hype_query` | Send a named read operation |
| `hype_apply` | Send a named mutation |
| `hype_document_create` | Create and initially save a new document |
| `hype_timeline_set_duration` | Set a timeline duration with a current-value guard |
| `hype_document_export_video` | Request a native video export |

Start with discovery and capabilities. For a multi-step workflow, include the selected `pid` and `session` on every call. Read the available MCP resources `connector://guide` and `connector://operations` for request instructions and schemas.

Example `hype_query` arguments, after discovering real values:

```json
{
  "pid":12345,
  "session":"SESSION-FROM-DISCOVERY",
  "request":{
    "op":"element.list",
    "document":"/absolute/working-copy.hype",
    "symbol":"DISCOVERED-SYMBOL-ID",
    "offset":0,
    "limit":100
  }
}
```

Use `hype_apply` with the same wrapper for named write operations, including `element.edit`, `scene.configure` and `animation.create`. The dedicated mutation tools take operation fields directly, without `op` or a `request` wrapper. Their presence does not replace the loaded host capability check. See the [scripting guide](scripting.md) for the creation and editing contracts. Read tools refuse writes. Follow pagination and inspect successful results before constructing the next request.

For a server fixed to one discovered connection, append both `--hype-pid`, the PID string, and `--hype-session`, the session string, to the launch arguments. Conflicting tool selectors are refused. Refresh this configuration deliberately after Hype restarts; do not silently switch a workflow to another process.

## A useful first request

Give your agent a clear source, output and editing scope:

> Use Connector to inspect my open Hype documents. Show me which document you will use. Work on a fresh copy of my chosen base, add a title and a rectangle, save the copy and export HTML to a new directory. Read back the result. Stop and report the working-copy path if an operation has an uncertain outcome.

Once you have a repeatable sequence, turn it into a normal script. The same JSON operations work without an agent. See [examples](examples.md) and [scripting](scripting.md).

## Keep the workflow predictable

- Select and pin one connection, then discover document-local IDs.
- Work on a fresh copy unless the user explicitly requests an in-place edit.
- Use the named operation catalog and check the loaded plugin's capabilities.
- Distinguish model changes from inspector actions. Prepare and read inspector state before setting it.
- Save explicitly, confirm completion and inspect the exported result.
- Stop after uncertain outcomes. Do not retry a mutation merely because a tool timed out.

The basic setup exposes named operations. It does not need open native invocation. Large JSON payloads can also hit operating-system argument limits before the MCP frame limit, so keep individual requests bounded.

The small companion skill in this repository teaches this workflow to compatible agents. Installing a skill does not install the app, grant folder access or configure an MCP server automatically.
