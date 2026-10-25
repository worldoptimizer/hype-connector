# Runnable examples

## EISZEIT: a complete campaign

[Play EISZEIT](../site/demos/eiszeit/index.html), a three-scene ice cream campaign built through Connector. Explore the ingredients, switch scenes and choose a flavour in the local giveaway demonstration. No data is collected. The fixed 1200 × 800 composition scales to fit the window.

The original Hype document contains separately editable text, images, controls and animation. The website serves its native HTML export. For building your own complete design, start with the [design recipes](../skills/hype-connector/references/design-recipes.md) and [native authoring recipes](../skills/hype-connector/references/native-recipes.md).

## Small scripting examples

These three Python examples show how to build a repeatable template without an agent. They send Connector's named operations, discover real document IDs and stop after the first failure.

Download or clone this repository, then keep the three scripts together in its [examples directory](../examples/README.md). They use Python 3's standard library and shared helpers from the neighboring scripts. No `pip` packages are needed.

## Prepare your own base

Create a small `.hype` document in Hype and save it as `Base.hype`. Use a single layout, leave its root scene context active and stop playback. The examples copy this package before editing. No bundled Hype document or proprietary fixture is required.

Install Connector and its plugin, then discover the intended Hype process:

```sh
'/Applications/Connector.app/Contents/MacOS/connector' hosts
```

Replace `12345` below with that PID. Each script discovers its session once and pins subsequent calls. Run the commands from the repository's `examples` directory. Replace every `/absolute/...` path with your own existing input or writable output location.

## Basic template

[build_template.py](../examples/build_template.py) adds a colored rectangle, a title and a document JavaScript function. It saves, exports HTML, saves the final editable state and reports requested versus actual element geometry.

```sh
python3 -B build_template.py \
  --pid 12345 \
  --source '/absolute/Base.hype' \
  --title 'A repeatable template'
```

The default CLI path is `/Applications/Connector.app/Contents/MacOS/connector`. Use `--cli` if the app is installed elsewhere. `--workdir` chooses an existing Hype-accessible staging parent, and `--export-parent` chooses an existing export parent. Keep both outside the original package. Use an external volume for large documents.

The base must have a complete inventory with at most 998 elements, leaving room for two additions. The script reads geometry after saving because native text layout may adjust requested dimensions.

`--hidden` explicitly requests `display:false` on opening. Without the flag, the current open operation also defaults to false. Neither choice guarantees every later editor action will remain windowless.

## Image template

[build_image_template.py](../examples/build_image_template.py) copies your base and PNG, imports the copied asset, creates one image, sets its position and dimensions, and saves the working package.

Create the scratch parent yourself before running:

```sh
python3 -B build_image_template.py \
  --pid 12345 \
  --source '/absolute/Base.hype' \
  --png '/absolute/hero.png' \
  --scratch-parent '/absolute/existing-scratch-folder' \
  --left 40 --top 60 \
  --width 320 --height 240
```

The scratch parent must be outside the source package. Use `--workdir` to choose another existing staging parent accessible to Hype. Supply both dimensions or neither; omitting them retains the native dimensions. Position and size use model setters, so they do not imply inspector aspect-ratio behavior.

This example requires exactly one root layout. Its base is limited to 90 MB and 10,000 entries; the PNG is limited to 8 MiB and 16,777,216 pixels. Symlinks and special files are refused. The original document and PNG are preserved because native import receives copies.

Optionally append new output paths with existing, Hype-writable parents:

```sh
--save-copy '/absolute/output/Image-template.hype' \
--export '/absolute/output/Image-template-html'
```

The working document remains open. Optional export follows its explicit save; this example does not save again after export or promise a clean document state afterward.

## Animated template

[build_animation_template.py](../examples/build_animation_template.py) inserts a rectangle and records its Left position through Hype's inspector. Its base needs one layout and an existing Main timeline at least two seconds long. The script does not extend the timeline.

```sh
python3 -B build_animation_template.py \
  --pid 12345 \
  --source '/absolute/Animation-base.hype' \
  --seconds 2
```

It establishes a baseline with recording off, moves to the requested time, reads the inspector value and records a 100-point movement. It checks the new animation rows, restores the original recording mode and saves. Keep playback stopped and the root scene active.

The base may contain at most 999 elements and 30 Main animation rows, leaving room for the additions. Its package limit is 90 MB and 10,000 entries, with no symlinks or special files. Optional `--workdir`, `--save-copy` and `--export` follow the same destination rules as the image example. The working document remains open.

## Read the receipts

All scripts report their working-copy paths. Keep these output lines if a later operation fails. Successful results include identities and output paths you can inspect. The scripts do not automatically retry, roll back or clean up after a failed or uncertain request. A new invocation creates a new copy.

For command options, `--help` does not contact Hype:

```sh
python3 -B build_template.py --help
python3 -B build_image_template.py --help
python3 -B build_animation_template.py --help
```

The examples demonstrate Connector 0.1.3/build 15 with Hype 4.1.22/build 786. Their receipts confirm editing, saving and native export stages; inspect the resulting HTML in a browser to assess visual output and playback.
