# Connector examples

Three small Python scripts turn a Hype document of your own into a repeatable starting point. They use Connector's public named operations, work on fresh copies and require no AI service.

| Script | Builds |
| --- | --- |
| [build_template.py](build_template.py) | Styled rectangle, title, document JavaScript and HTML export |
| [build_image_template.py](build_image_template.py) | Imported PNG placed in a saved template, with optional copy/export |
| [build_animation_template.py](build_animation_template.py) | Rectangle movement recorded through the inspector, with optional copy/export |

Keep **all three files together** because they share helpers. They require Python 3, Connector and a running Hype with its Connector plugin loaded. Python dependencies are limited to the standard library.

Create and save your own small, single-layout `.hype` base. Leave the root scene active and playback stopped. The animation example also needs an existing Main timeline at least two seconds long. Do not start with your only copy of important work.

See the [example guide](../docs/examples.md) for prerequisites, commands, limits and output handling. See [installation](../docs/getting-started.md) if Connector is not yet connected.

Every script pins the chosen Hype session and stops after a failure or uncertain result. Earlier edits can remain in its reported working copy. Inspect that copy before another run; there is no automatic retry or rollback.
