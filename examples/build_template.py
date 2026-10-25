#!/usr/bin/env python3
"""Build a Hype document on a fresh copy using Connector's public JSON operations.
Requires Python 3, a running Connector-enabled Hype instance and a small base document.
Operations are sequential, not a transaction. A failure stops without retry or cleanup.
"""
import argparse
import html
import json
import math
import os
import subprocess
import uuid
from pathlib import Path

ELEMENT_LIMIT = 1000


class ExampleFailure(RuntimeError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(code + ': ' + message)


class Connector:
    def __init__(self, executable, pid):
        self.executable = executable
        self.pid = pid
        self.session = None
        self.failure = None

    def stop(self, code, message):
        self.failure = ExampleFailure(code, message)
        raise self.failure

    def request(self, operation, *, discovery=False, **fields):
        if self.failure is not None:
            raise self.failure
        if not discovery and self.session is None:
            self.stop('host_selection', 'Discover and pin a Connector session before sending operations.')
        command = [self.executable, '--pid', str(self.pid)]
        if self.session is not None:
            command += ['--session', self.session]
        command += ['run', json.dumps({'op': operation, **fields})]
        try:
            result = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True,
                                    text=True, timeout=150)
        except (subprocess.TimeoutExpired, OSError) as error:
            self.stop('outcome_unknown', 'Connector did not return a complete result. Inspect the working copy before retrying. ' + str(error))
        try:
            response = json.loads(result.stdout if result.returncode == 0 else result.stderr)
        except (ValueError, TypeError):
            self.stop('outcome_unknown', 'Connector returned malformed output. Inspect the working copy before retrying.')
        if not isinstance(response, dict) or type(response.get('ok')) is not bool:
            self.stop('outcome_unknown', 'Connector returned an invalid result envelope. Inspect the working copy before retrying.')
        if result.returncode == 0:
            if set(response) != {'ok', 'result'} or response['ok'] is not True or result.stderr.strip():
                self.stop('outcome_unknown', 'Connector returned inconsistent success output. Inspect the working copy before retrying.')
            return response['result']
        if result.returncode != 1:
            self.stop('outcome_unknown', 'Connector returned an unexpected failure exit status. Inspect the working copy before retrying.')
        error = response.get('error')
        if (set(response) != {'ok', 'error'} or response['ok'] is not False or result.stdout.strip()
                or not isinstance(error, dict) or not isinstance(error.get('code'), str) or not error['code']
                or not isinstance(error.get('message'), str)):
            self.stop('outcome_unknown', 'Connector returned inconsistent failure output. Inspect the working copy before retrying.')
        self.stop(error['code'], error['message'] + ' Inspect the working copy before another run.')

    def discover(self):
        if self.session is not None:
            self.stop('host_selection', 'This run already selected a session. Start a new run to choose another host.')
        result = self.request('host.list', discovery=True)
        sessions = result.get('sessions') if isinstance(result, dict) else None
        if not isinstance(sessions, list) or len(sessions) != 1:
            self.stop('host_selection', 'The selected PID must identify exactly one Connector session.')
        selected = sessions[0]
        if (not isinstance(selected, dict) or type(selected.get('pid')) is not int or selected['pid'] != self.pid
                or not isinstance(selected.get('session'), str) or not selected['session'] or '\0' in selected['session']):
            self.stop('host_selection', 'The selected host did not provide a matching PID and session identity.')
        self.session = selected['session']


def identifier(value, label):
    if not isinstance(value, str) or not value or '\0' in value:
        raise ExampleFailure('invalid_result', 'Connector did not return a valid ' + label + '.')
    return value


def inside_existing(path, package):
    """Compare existing ancestor identities, including case aliases on macOS."""
    try:
        identity = package.stat()
    except FileNotFoundError:
        return False  # Let fixture.stage report a missing source.
    for ancestor in (path, *path.parents):
        try:
            observed = ancestor.stat()
        except FileNotFoundError:
            continue
        if (observed.st_dev, observed.st_ino) == (identity.st_dev, identity.st_ino):
            return True
    return False


def observed_geometry(row, element, expected_class, text=None):
    if not isinstance(row, dict) or row.get('id') != element or not isinstance(row.get('attributes'), dict):
        raise ExampleFailure('invalid_result', 'Saved element readback is missing or has the wrong identity. Inspect the working copy.')
    attributes = row['attributes']
    if attributes.get('ClassType') != expected_class or (text is not None and attributes.get('InnerHTML') != text):
        raise ExampleFailure('invalid_result', 'Saved element type or text content differs. Inspect the working copy.')
    actual = {key: attributes.get(key) for key in ('Left', 'Top', 'Width', 'Height')}
    if (any(type(value) not in (int, float) or not math.isfinite(value) for value in actual.values())
            or actual['Width'] <= 0 or actual['Height'] <= 0):
        raise ExampleFailure('invalid_result', 'Saved element geometry must be finite with positive dimensions. Inspect the working copy.')
    return actual


def inventory(client, context, reserve):
    page = client.request('element.list', **context, limit=ELEMENT_LIMIT)
    if (not isinstance(page, dict) or not isinstance(page.get('elements'), list)
            or type(page.get('hasMore')) is not bool or type(page.get('total')) is not int or page['total'] < 0):
        raise ExampleFailure('invalid_result', 'Connector returned an invalid element inventory. Inspect the working copy.')
    rows = page['elements']
    if page['hasMore'] or page['total'] != len(rows) or len(rows) + reserve > ELEMENT_LIMIT:
        raise ExampleFailure('incomplete_inventory', 'Use a base with at most 998 elements and a complete inventory. No insertion was attempted for this check.')
    ids = [identifier(row.get('id') if isinstance(row, dict) else None, 'element ID') for row in rows]
    if len(set(ids)) != len(ids):
        raise ExampleFailure('invalid_result', 'Connector returned duplicate element IDs. Inspect the working copy.')
    return set(ids)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', default='/Applications/Connector.app/Contents/MacOS/connector')
    parser.add_argument('--pid', type=int, required=True, help='Explicit Hype process to control')
    parser.add_argument('--source', type=Path, required=True, help='Base document copied before editing')
    parser.add_argument('--workdir', type=Path, help='Optional staging parent already accessible to Hype')
    parser.add_argument('--export-parent', type=Path, help='Existing writable parent already accessible to Hype')
    parser.add_argument('--title', default='Created with Connector')
    parser.add_argument('--hidden', action='store_true', help='Request display:false when opening the staged copy; later native actions can still show UI')
    args = parser.parse_args(argv)
    if args.pid <= 0 or args.pid > 2_147_483_647:
        parser.error('--pid must be a positive process ID')
    source = Path(os.path.abspath(args.source))
    source_identity = source.resolve(strict=False)
    for destination in (args.workdir, args.export_parent):
        if destination is not None:
            parent = destination.resolve(strict=False)
            if (parent == source_identity or source_identity in parent.parents
                    or inside_existing(parent, source_identity)):
                parser.error('Staging and export parents must be outside the source package')
    client = Connector(args.cli, args.pid)
    client.discover()
    stage = {'source': str(source)}
    if args.workdir:
        stage['destination'] = os.path.abspath(args.workdir)
    staged = client.request('fixture.stage', **stage)
    working = identifier(staged.get('path') if isinstance(staged, dict) else None, 'working-copy path')
    working_path = Path(os.path.abspath(working))
    working_identity = working_path.resolve(strict=False)
    if (not Path(working).is_absolute() or working_identity == source_identity
            or source_identity in working_identity.parents or inside_existing(working_identity, source_identity)):
        raise ExampleFailure('invalid_result', 'Staging did not identify a separate absolute working copy. No document was opened.')
    # Report immediately so partial work remains discoverable after any failure.
    print(json.dumps({'workingCopy': working}), flush=True)
    opened = client.request('document.open', path=working, **({'display': False} if args.hidden else {}))
    if not isinstance(opened, dict) or opened.get('opened') is not True:
        raise ExampleFailure('invalid_result', 'Open did not report completion. Inspect the working copy.')
    scenes = client.request('scene.list', document=working)
    rows = scenes.get('scenes') if isinstance(scenes, dict) else None
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        raise ExampleFailure('invalid_result', 'The working copy has no usable scene. Inspect the copy.')
    scene = identifier(rows[0].get('id'), 'scene ID')
    context = {'document': working, 'symbol': identifier(rows[0].get('symbol'), 'symbol ID')}

    def inserted(name, reserve=1):
        before = inventory(client, context, reserve)
        client.request('editor.action', document=working, scene=scene, name=name)
        after = inventory(client, context, 0)
        new = after - before
        if not before <= after or len(new) != 1:
            raise ExampleFailure('invalid_result', 'The insertion did not produce exactly one fresh ID. Inspect the working copy.')
        return new.pop()

    def attributes(element, values):
        for key, value in values.items():
            client.request('element.setAttribute', **context, element=element, attribute=key, value=value)

    # Reserve both additions before the first insertion, so a full inventory
    # cannot become truncated halfway through the intended example.
    box = inserted('insert.rectangle', reserve=2)
    attributes(box, {'Left': 40, 'Top': 60, 'Width': 360, 'Height': 120,
                     'BackgroundColor': {'$color': [.20, .24, .68, 1], 'space': 'srgb'}})
    label = inserted('insert.text')
    client.request('text.set', **context, element=label, value=html.escape(args.title))
    # Establish text and typography before requesting its final geometry.
    attributes(label, {'FontSize': 24, 'TextColor': {'$color': [1, 1, 1, 1], 'space': 'srgb'}})
    attributes(label, {'Left': 56, 'Top': 92, 'Width': 320, 'Height': 48})
    script = client.request('javascript.add', document=working)
    script_id = identifier(script.get('id') if isinstance(script, dict) else None, 'JavaScript ID')
    function = 'connectorTemplate_' + uuid.uuid4().hex[:8]
    client.request('javascript.rename', document=working, script=script_id, value=function)
    client.request('javascript.setSource', document=working, script=script_id,
                   value='function ' + function + '(hypeDocument, element, event) { return "Created by Connector"; }')
    saved = client.request('document.save', document=working)
    if not isinstance(saved, dict) or saved.get('saved') is not True:
        raise ExampleFailure('invalid_result', 'Save did not report completion. Inspect the working copy before exporting.')
    parent = Path(os.path.abspath(args.export_parent)) if args.export_parent else working_path.parent
    exported = client.request('document.exportHTML', document=working,
                              destination=str(parent / ('connector-export-' + uuid.uuid4().hex[:8])))
    if not isinstance(exported, dict) or exported.get('exported') is not True:
        raise ExampleFailure('invalid_result', 'Export did not report completion. Inspect the working copy and output.')
    index = identifier(exported.get('indexPath'), 'export index path')
    # Export can leave native layout/document changes. This is a distinct final
    # persistence stage after confirmed export, never a retry of a failed call.
    final_saved = client.request('document.save', document=working)
    if not isinstance(final_saved, dict) or final_saved.get('saved') is not True:
        raise ExampleFailure('invalid_result', 'Final save after export did not report completion. Inspect the working copy and existing export.')
    geometry = {}
    for name, element, expected_class, requested, expected_text in (
            ('rectangle', box, 'Rectangle', {'Left': 40, 'Top': 60, 'Width': 360, 'Height': 120}, None),
            ('text', label, 'Text', {'Left': 56, 'Top': 92, 'Width': 320, 'Height': 48}, html.escape(args.title))):
        actual = observed_geometry(client.request('element.get', **context, element=element),
                                   element, expected_class, expected_text)
        geometry[name] = {'requested': requested, 'actual': actual, 'normalized': actual != requested}
    print(json.dumps({'document': working, 'saved': True, 'elements': {'rectangle': box, 'text': label},
                      'script': script_id, 'geometry': geometry, 'indexPath': index}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ExampleFailure as error:
        raise SystemExit(str(error))
