#!/usr/bin/env python3
"""Place one PNG in a fresh Hype copy through Connector's named operations.

Requires a small single-layout .hype base and one explicit running host. Original
inputs are copied first. Operations are sequential, not a transaction. Any failure
stops without retries, host switching, rollback or cleanup calls.
"""
import argparse
import os
import shutil
import stat
import struct
import uuid
from pathlib import Path

from build_template import Connector, ExampleFailure, identifier, inventory

PNG_LIMIT = 8 * 1024 * 1024
PACKAGE_LIMIT = 90_000_000
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


def regular_path(value, *, directory=False, existing=True):
    path = Path(os.path.abspath(value))
    if '\0' in str(path):
        raise ExampleFailure('bad_path', 'Paths must not contain null characters.')
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ExampleFailure('unsafe_path', 'Symlink paths are not accepted: ' + str(part))
    if existing:
        mode = path.stat().st_mode
        if not (stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)):
            raise ExampleFailure('unsafe_path', 'Expected a regular ' + ('directory: ' if directory else 'file: ') + str(path))
    return path


def package_files(source):
    """Inspect only this source package, without following links or special files."""
    files, total = 0, 0
    pending = [source]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                metadata = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(metadata.st_mode):
                    pending.append(Path(entry.path))
                elif stat.S_ISREG(metadata.st_mode):
                    total += metadata.st_size
                else:
                    raise ExampleFailure('unsafe_package', 'Source package contains a symlink or special file: ' + entry.path)
                files += 1
                if files > 10000 or total > PACKAGE_LIMIT:
                    raise ExampleFailure('package_budget', 'Use a base below 90 MB and 10,000 entries for this small example.')


def inside_existing(path, package):
    """Compare existing directory identities, including case aliases and missing leaves."""
    identity = package.stat()
    for ancestor in (path, *path.parents):
        try:
            observed = ancestor.stat()
        except FileNotFoundError:
            continue
        if (observed.st_dev, observed.st_ino) == (identity.st_dev, identity.st_ino):
            return True
    return False


def outside(path, source, label):
    if inside_existing(path, source):
        raise ExampleFailure('unsafe_destination', label + ' must be outside the protected package, including alternate path casing.')


def new_destination(value, source, label):
    path = regular_path(value, existing=False)
    regular_path(path.parent, directory=True)
    outside(path, source, label)
    if path.exists():
        raise ExampleFailure('destination_exists', label + ' must be a new path. Overwrite is not supported by this example.')
    return path


def main(argv=None):
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', default='/Applications/Connector.app/Contents/MacOS/connector')
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--source', type=Path, required=True, help='Small single-layout .hype base, never edited')
    parser.add_argument('--png', type=Path, required=True, help='Original PNG, copied before native import')
    parser.add_argument('--scratch-parent', '--prepare-parent', dest='prepare_parent', type=Path, required=True, help='Existing writable local parent outside the source package')
    parser.add_argument('--workdir', type=Path, help='Optional existing staging parent already accessible to Hype')
    parser.add_argument('--save-copy', type=Path, help='Optional NEW .hype destination already writable by Hype')
    parser.add_argument('--export', type=Path, help='Optional NEW export directory already writable by Hype')
    parser.add_argument('--left', type=int, default=40)
    parser.add_argument('--top', type=int, default=60)
    parser.add_argument('--width', type=int, help='Optional explicit model width, requires --height')
    parser.add_argument('--height', type=int, help='Optional explicit model height, requires --width')
    args = parser.parse_args(argv)
    if not 0 < args.pid <= 2_147_483_647:
        parser.error('--pid must be a positive process ID')
    if (args.width is None) != (args.height is None):
        parser.error('Supply both --width and --height, or neither')
    if any(not 0 <= value <= 100000 for value in (args.left, args.top)) or any(value is not None and not 1 <= value <= 100000 for value in (args.width, args.height)):
        parser.error('Positions must be 0…100000, dimensions 1…100000')
    source = regular_path(args.source, directory=True)
    if source.suffix.lower() != '.hype':
        parser.error('--source must be a .hype package')
    regular_path(source / 'data.plist')
    regular_path(source / 'Resources', directory=True)
    package_files(source)
    asset = regular_path(args.png)
    if asset.suffix.lower() != '.png' or not 0 < asset.stat().st_size <= PNG_LIMIT:
        parser.error('--png must be a nonempty PNG of at most 8 MiB')
    with asset.open('rb') as stream:
        data = stream.read(PNG_LIMIT + 1)
    if len(data) > PNG_LIMIT or len(data) < 24 or data[:8] != PNG_SIGNATURE or data[8:16] != b'\0\0\0\rIHDR':
        parser.error('--png must have a valid bounded PNG header; native import validates decoding')
    width, height = struct.unpack('>II', data[16:24])
    if not width or not height or width * height > 16_777_216:
        parser.error('--png exceeds the 16,777,216 pixel limit')
    prepare_parent = regular_path(args.prepare_parent, directory=True)
    outside(prepare_parent, source, 'Preparation parent')
    stage_fields = {}
    if args.workdir:
        workdir = regular_path(args.workdir, directory=True)
        outside(workdir, source, 'Staging parent')
        stage_fields['destination'] = str(workdir)
    save_copy = new_destination(args.save_copy, source, 'Save-copy destination') if args.save_copy else None
    export = new_destination(args.export, source, 'Export destination') if args.export else None
    if save_copy and save_copy.suffix.lower() != '.hype':
        parser.error('--save-copy must end in .hype')
    if save_copy and export and (save_copy == export or save_copy in export.parents or export in save_copy.parents):
        parser.error('Save-copy and export destinations must be separate')

    client = Connector(args.cli, args.pid)
    client.discover()  # One PID lookup, then every request pins its session ID.
    preparation = prepare_parent / ('connector-image-' + uuid.uuid4().hex[:12])
    preparation.mkdir()
    prepared = preparation / source.name
    # Preserve ordinary metadata where supported. No security attributes are removed.
    shutil.copytree(source, prepared, symlinks=True)
    inputs = prepared / ('ConnectorInputs-' + uuid.uuid4().hex[:12])
    inputs.mkdir()
    name = 'connector-image-' + uuid.uuid4().hex[:12] + '.png'
    shutil.copy2(asset, inputs / name, follow_symlinks=False)
    package_files(prepared)
    regular_path(inputs / name)
    print(json.dumps({'preparedCopy': str(prepared)}), flush=True)
    staged = client.request('fixture.stage', source=str(prepared), **stage_fields)
    working_value = identifier(staged.get('path') if isinstance(staged, dict) else None, 'working-copy path')
    if not Path(working_value).is_absolute():
        raise ExampleFailure('invalid_result', 'Staging must return an absolute working-copy path.')
    working = regular_path(working_value, directory=True)
    outside(working, source, 'Working copy')
    if inside_existing(working, prepared) or inside_existing(working, preparation):
        raise ExampleFailure('invalid_result', 'Staging must return a separate working copy. No document was opened.')
    for destination in (save_copy, export):
        if destination and inside_existing(destination, working):
            raise ExampleFailure('unsafe_destination', 'Output destinations must be outside the staged package.')
    regular_path(working / 'data.plist')
    regular_path(working / 'Resources', directory=True)
    staged_asset = regular_path(working / inputs.name / name)
    with staged_asset.open('rb') as stream:
        if stream.read(PNG_LIMIT + 1) != data:
            raise ExampleFailure('invalid_result', 'Staging changed the copied PNG. No document was opened.')
    print(json.dumps({'workingCopy': str(working), 'session': client.session}), flush=True)
    opened = client.request('document.open', path=str(working), display=True)
    if not isinstance(opened, dict) or opened.get('opened') is not True:
        raise ExampleFailure('invalid_result', 'Open did not report completion. Inspect the reported copy.')
    layouts = client.request('layout.list', document=str(working))
    rows = layouts.get('layouts') if isinstance(layouts, dict) else None
    if not isinstance(rows, list) or len(rows) != 1 or not isinstance(rows[0], dict):
        raise ExampleFailure('unsupported_context', 'Use a base with exactly one root layout for this example.')
    scene = identifier(rows[0].get('id'), 'scene ID')
    context = {'document': str(working), 'symbol': identifier(rows[0].get('symbol'), 'symbol ID')}
    before = inventory(client, context, 1)
    imported = client.request('resource.import', document=str(working), path=str(working / inputs.name / name))
    resource = imported.get('resource') if isinstance(imported, dict) else None
    if (not isinstance(imported, dict) or imported.get('imported') is not True or not isinstance(resource, dict) or resource.get('mimeType') != 'image/png'):
        raise ExampleFailure('invalid_result', 'Import did not identify a PNG. Inspect the copy before another run.')
    resource_id = identifier(resource.get('id'), 'resource ID')
    group_id = identifier(resource.get('group'), 'PNG group ID')
    ready = client.request('scene.settings.prepare', document=str(working), scene=scene,
                           property='width', applyToMatchingLayouts=False)
    if (not isinstance(ready, dict) or any(ready.get(key) is not True for key in ('prepared', 'bindingReady', 'scopeEstablished'))
            or ready.get('scene') != scene or ready.get('affectedLayouts') != [scene] or ready.get('applyToMatchingLayouts') is not False):
        raise ExampleFailure('preparation_pending', 'Scene preparation is incomplete. Inspect the reported copy. This example does not wait or retry preparation.')
    created = client.request('element.createImage', document=str(working), scene=scene, resource=resource_id)
    element = created.get('element') if isinstance(created, dict) else None
    if (not isinstance(created, dict) or created.get('created') is not True or created.get('resource') != resource_id
            or created.get('group') != group_id or not isinstance(element, dict)
            or not isinstance(element.get('attributes'), dict) or element['attributes'].get('ClassType') != 'Image'
            or element['attributes'].get('BackgroundImageResourceGroupOid') != group_id):
        raise ExampleFailure('invalid_result', 'Image creation did not return its resource and group. Inspect the reported copy.')
    element_id = identifier(element.get('id'), 'created element ID')
    after = inventory(client, context, 0)
    if not before <= after or after - before != {element_id}:
        raise ExampleFailure('invalid_result', 'Image creation did not add exactly its returned ID. Inspect the copy.')
    values = {'Left': args.left, 'Top': args.top}
    if args.width is not None:
        values.update(Width=args.width, Height=args.height)
    for attribute, value in values.items():
        client.request('element.setAttribute', **context, element=element_id, attribute=attribute, value=value)
    actual = client.request('element.get', **context, element=element_id)
    attrs = actual.get('attributes') if isinstance(actual, dict) else None
    if (not isinstance(actual, dict) or actual.get('id') != element_id or not isinstance(attrs, dict) or attrs.get('ClassType') != 'Image'
            or attrs.get('BackgroundImageResourceGroupOid') != group_id
            or any(type(attrs.get(key)) not in (int, float) or attrs[key] != value for key, value in values.items())):
        raise ExampleFailure('invalid_result', 'Image model readback differs. Inspect the copy before saving.')
    saved = client.request('document.save', document=str(working))
    if not isinstance(saved, dict) or saved.get('saved') is not True:
        raise ExampleFailure('invalid_result', 'Save did not report completion. Inspect the working copy.')
    result = {'document': str(working), 'saved': True, 'element': element_id, 'resource': resource_id, 'group': group_id}
    if save_copy:
        copied = client.request('document.saveCopy', document=str(working), destination=str(save_copy))
        if not isinstance(copied, dict) or copied.get('saved') is not True:
            raise ExampleFailure('invalid_result', 'Save-copy completion was not confirmed.')
        result['savedCopy'] = str(save_copy)
    if export:
        exported = client.request('document.exportHTML', document=str(working), destination=str(export))
        if not isinstance(exported, dict) or exported.get('exported') is not True:
            raise ExampleFailure('invalid_result', 'Export completion was not confirmed.')
        result['indexPath'] = identifier(exported.get('indexPath'), 'export index path')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ExampleFailure, OSError) as error:
        raise SystemExit(str(error))
