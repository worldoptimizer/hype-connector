#!/usr/bin/env python3
"""Record one rectangle's Left animation in a fresh staged Hype copy.

Operations commit separately. Any failure stops without retry or cleanup calls.
"""
import argparse
import json
import math
from pathlib import Path
import struct
import time

from build_template import Connector, ExampleFailure, identifier
from build_image_template import regular_path, package_files, outside, inside_existing, new_destination

MAIN = 'kTimelineDefaultIdentifier'
MAX_ANIMATIONS = 32
SETTLE_SECONDS = .6


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def near(a, b):
    return number(a) and number(b) and math.isclose(a, b, rel_tol=0, abs_tol=1e-6)


def require(condition, message):
    if not condition:
        raise ExampleFailure('invalid_result', message + ' Inspect the reported working copy before another run.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', default='/Applications/Connector.app/Contents/MacOS/connector')
    parser.add_argument('--pid', required=True, type=int)
    parser.add_argument('--source', required=True, type=Path, help='Small single-layout .hype base with Main duration at least two seconds')
    parser.add_argument('--seconds', required=True, type=float, help='Positive recording point within existing Main duration; measured example: 2')
    parser.add_argument('--workdir', type=Path, help='Existing staging parent already accessible to Hype')
    parser.add_argument('--save-copy', type=Path, help='Optional NEW .hype destination already writable by Hype')
    parser.add_argument('--export', type=Path, help='Optional NEW HTML directory already writable by Hype')
    args = parser.parse_args(argv)
    if not 0 < args.pid <= 2_147_483_647:
        parser.error('--pid must be a positive process ID')
    try:
        cursor = struct.unpack('f', struct.pack('f', args.seconds))[0]
    except (OverflowError, struct.error):
        cursor = float('nan')
    if not number(args.seconds) or not number(cursor) or cursor <= 0:
        parser.error('--seconds must be positive and representable by the native float cursor')
    source = regular_path(args.source, directory=True)
    if source.suffix.lower() != '.hype':
        parser.error('--source must be a .hype package')
    regular_path(source / 'data.plist')
    regular_path(source / 'Resources', directory=True)
    package_files(source)  # Shared 90 MB / 10,000-entry, no-link/special-file boundary.
    stage = {'source': str(source)}
    if args.workdir:
        workdir = regular_path(args.workdir, directory=True)
        outside(workdir, source, 'Staging parent')
        stage['destination'] = str(workdir)
    saved_copy = new_destination(args.save_copy, source, 'Save-copy destination') if args.save_copy else None
    exported_to = new_destination(args.export, source, 'Export destination') if args.export else None
    if saved_copy and saved_copy.suffix.lower() != '.hype':
        parser.error('--save-copy must end in .hype')
    if saved_copy and exported_to and (saved_copy == exported_to or saved_copy in exported_to.parents or exported_to in saved_copy.parents):
        parser.error('Save-copy and export destinations must be separate')
    client = Connector(args.cli, args.pid)
    client.discover()
    calls = 1

    def call(op, **fields):
        nonlocal calls
        require(calls < 140, 'Bounded operation budget exhausted.')
        calls += 1
        return client.request(op, **fields)

    required = {'inspector.prepare', 'inspector.get', 'inspector.set', 'animation.list', 'animation.get', 'editor.action', 'layout.list', 'timeline.list'}
    caps = call('host.capabilities')
    require(isinstance(caps, dict) and isinstance(caps.get('operations'), list)
            and all(isinstance(op, str) for op in caps['operations']) and required <= set(caps['operations']), 'Required named operations are unavailable.')
    staged = call('fixture.stage', **stage)
    path = identifier(staged.get('path') if isinstance(staged, dict) else None, 'working-copy path')
    require(Path(path).is_absolute(), 'Staging returned a relative path.')
    working = regular_path(path, directory=True)
    outside(working, source, 'Working copy')
    require(not inside_existing(source, working), 'Staging did not return a separate package.')
    regular_path(working / 'data.plist')
    regular_path(working / 'Resources', directory=True)
    for destination in (saved_copy, exported_to):
        if destination:
            outside(destination, working, 'Output destination')
    print(json.dumps({'workingCopy': str(working), 'session': client.session}), flush=True)
    opened = call('document.open', path=str(working), display=True)
    require(isinstance(opened, dict) and opened.get('opened') is True, 'Open completion was not confirmed.')
    doc = {'document': str(working)}
    layout_result = call('layout.list', **doc)
    layouts = layout_result.get('layouts') if isinstance(layout_result, dict) else None
    require(isinstance(layouts, list) and len(layouts) == 1 and isinstance(layouts[0], dict), 'Use exactly one root layout.')
    scene = identifier(layouts[0].get('id'), 'scene ID')
    symbol = identifier(layouts[0].get('symbol'), 'root symbol ID')
    context = {**doc, 'symbol': symbol}
    timeline_result = call('timeline.list', **context)
    timelines = timeline_result.get('timelines') if isinstance(timeline_result, dict) else None
    require(isinstance(timelines, list) and all(isinstance(row, dict) for row in timelines), 'Malformed timeline inventory.')
    mains = [row for row in timelines if row.get('id') == MAIN]
    require(len(mains) == 1 and number(mains[0].get('duration')) and mains[0]['duration'] >= 2
            and args.seconds <= mains[0]['duration'] and cursor <= mains[0]['duration'], 'Main must already support the requested recording point and at least two seconds.')

    def page(op, key, limit, **fields):
        result = call(op, **context, **fields, limit=limit)
        require(isinstance(result, dict) and isinstance(result.get(key), list)
                and result.get('hasMore') is False and type(result.get('total')) is int
                and result['total'] == len(result[key]) and result.get('nextOffset') == result['total']
                and len(result[key]) <= limit, 'Inventory is incomplete or malformed: ' + op)
        rows = result[key]
        ids = [identifier(row.get('id') if isinstance(row, dict) else None, op + ' ID') for row in rows]
        require(len(ids) == len(set(ids)), 'Inventory contains duplicate identities.')
        return dict(zip(ids, rows))

    def animations():
        rows = page('animation.list', 'animations', MAX_ANIMATIONS, timeline=MAIN)
        result = {}
        for oid in rows:
            detail = call('animation.get', **context, timeline=MAIN, animation=oid)
            require(isinstance(detail, dict) and detail.get('id') == oid and '$ref' not in json.dumps(detail)
                    and number(detail.get('startTime')) and detail['startTime'] >= 0
                    and number(detail.get('duration')) and detail['duration'] >= 0
                    and isinstance(detail.get('referenceOid'), str) and isinstance(detail.get('identifier'), str),
                    'Animation detail identity or shape differs.')
            result[oid] = detail
        return result

    before = page('element.list', 'elements', 1000)
    require(len(before) < 1000, 'No room for one new element in a complete inventory.')
    initial_animations = animations()
    require(len(initial_animations) <= MAX_ANIMATIONS - 2, 'Reserve two animation rows before insertion.')
    receipt = call('editor.action', **doc, scene=scene, name='insert.rectangle', elements=[])
    require(isinstance(receipt, dict) and receipt.get('invoked') is True and receipt.get('action') == 'insert.rectangle'
            and receipt.get('selectionChanged') is True, 'Rectangle insertion receipt differs.')
    after = page('element.list', 'elements', 1000)
    fresh = set(after) - set(before)
    require(set(before) <= set(after) and len(fresh) == 1, 'Insertion did not yield exactly one fresh ID.')
    element = next(iter(fresh))
    attrs = after[element].get('attributes')
    require(isinstance(attrs, dict) and attrs.get('ClassType') == 'Rectangle' and not attrs.get('Parent'), 'Fresh element is not a root rectangle.')
    inspector = {**context, 'scene': scene, 'timeline': MAIN, 'element': element, 'property': 'Left'}

    def inspect(result, seconds):
        require(isinstance(result, dict) and all(result.get(k) == v for k, v in inspector.items() if k != 'document')
                and number(result.get('seconds')) and near(result['seconds'], seconds) and number(result.get('value')), 'Inspector value/context is unavailable or stale.')
        return result

    def prepare(seconds):
        prepared = call('inspector.prepare', **inspector, seconds=seconds)
        require(isinstance(prepared, dict) and prepared.get('prepared') is True and 'value' not in prepared
                and all(prepared.get(k) == v for k, v in inspector.items() if k != 'document')
                and number(prepared.get('seconds')) and near(prepared['seconds'], seconds), 'Inspector preparation is pending or context differs.')
        time.sleep(SETTLE_SECONDS)  # One bounded settle; never polling or a retry.
        return inspect(call('inspector.get', **inspector, seconds=prepared['seconds']), prepared['seconds'])

    def edit(current, value, recording):
        require(number(value), 'Requested Left must remain finite.')
        result = inspect(call('inspector.set', **inspector, seconds=current['seconds'], expectedValue=current['value'], value=value, recording=recording), current['seconds'])
        require(result.get('recordingUsed') is recording and result.get('recordingRestored') is True
                and type(result.get('recordingBefore')) is bool and near(result.get('beforeValue'), current['value'])
                and near(result['value'], value), 'Native edit or recording restoration was not confirmed.')
        return result

    zero = prepare(0)
    baseline = edit(zero, zero['value'] + 40, False)
    unrecorded = animations()
    require(unrecorded == initial_animations, 'Recording-off edit changed animation rows.')
    point = prepare(cursor)
    require(near(point['value'], baseline['value']), 'Fresh rectangle unexpectedly changed before recording.')
    recorded = edit(point, point['value'] + 100, True)
    require(recorded['recordingBefore'] is baseline['recordingBefore'], 'Original recording state changed between edits.')
    all_rows = animations()
    lane = [row for row in all_rows.values() if row.get('referenceOid') == element and row.get('identifier') == 'Left']
    require(len(lane) == 2, 'Expected exactly one transition and one terminal Left point.')
    transition, terminal = sorted(lane, key=lambda row: row['startTime'])
    endpoint = lambda e, v: isinstance(e, dict) and e.get('identifier') == 'Left' and near(e.get('value'), v)
    require(near(transition.get('startTime'), 0) and near(transition.get('duration'), recorded['seconds'])
            and near(terminal.get('startTime'), recorded['seconds']) and near(terminal.get('duration'), 0)
            and endpoint(transition.get('startValue'), baseline['value']) and endpoint(transition.get('endValue'), recorded['value'])
            and endpoint(terminal.get('startValue'), recorded['value']) and terminal.get('endValue', 'missing') is None,
            'Native keyframe endpoints or actual end time differ.')
    lane_ids = {row['id'] for row in lane}
    require(lane_ids.isdisjoint(unrecorded) and {k: v for k, v in all_rows.items() if k not in lane_ids} == unrecorded
            and len(all_rows) == len(unrecorded) + 2, 'Recording changed unrelated animation rows.')
    saved = call('document.save', **doc)
    require(isinstance(saved, dict) and saved.get('saved') is True, 'Save completion was not confirmed.')
    result = {'document': str(working), 'saved': True, 'element': element, 'seconds': recorded['seconds'],
              'baseline': baseline['value'], 'recordedValue': recorded['value'], 'animations': lane,
              'recordingBefore': recorded['recordingBefore'], 'recordingRestored': True}
    if saved_copy:
        copied = call('document.saveCopy', **doc, destination=str(saved_copy))
        require(isinstance(copied, dict) and copied.get('saved') is True, 'Save-copy completion was not confirmed.')
        result['savedCopy'] = str(saved_copy)
    if exported_to:
        exported = call('document.exportHTML', **doc, destination=str(exported_to))
        require(isinstance(exported, dict) and exported.get('exported') is True, 'Export completion was not confirmed.')
        result['indexPath'] = identifier(exported.get('indexPath'), 'export index path')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ExampleFailure, OSError) as error:
        raise SystemExit(str(error))
