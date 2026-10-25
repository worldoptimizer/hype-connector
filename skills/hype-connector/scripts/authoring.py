"""Convenience recipes for measured root-scene authoring through Connector only.

No plist generation, direct package edits, editor GUI automation or hidden installs.
These model setters do not claim inspector-equivalent side effects or atomicity.
"""
from pathlib import Path
import math
import struct
import time

MAIN = 'kTimelineDefaultIdentifier'


def timeline_guard_seconds(actual, duration):
    """Preserve native float cursor identity at old-plugin double range bounds."""
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
               and math.isfinite(v) and v >= 0 for v in (actual, duration)):
        raise ValueError('Time and duration must be finite nonnegative numbers.')
    if actual <= duration:
        return actual
    # Native timeCursor is float32; old plugins compare duration as double first.
    # Clamp only an identical float32 value, never a nearby different frame/time.
    if struct.pack('f', actual) == struct.pack('f', duration):
        return duration
    raise ValueError('Returned cursor lies beyond the actual timeline duration.')


def color(hex_value):
    value = hex_value.lstrip('#')
    if len(value) not in (6, 8):
        raise ValueError('Use six RGB or eight RGBA hexadecimal digits.')
    parts = [int(value[i:i+2], 16)/255 for i in range(0, len(value), 2)]
    return {'$color': parts if len(parts) == 4 else parts + [1], 'space': 'srgb'}


class Document:
    def __init__(self, client, path):
        self.client, self.path = client, str(Path(path).absolute())
        controller = client.invoke({'class': 'NSDocumentController'}, 'sharedDocumentController', retain=True)
        self.ref = client.invoke(controller, 'documentForURL:', {'$url': Path(self.path).as_uri()}, retain=True)
        if not isinstance(self.ref, dict) or '$ref' not in self.ref:
            raise ValueError('Open this exact document before constructing Document.')

    @classmethod
    def create(cls, client, destination):
        path = Path(destination).absolute()
        if path.exists() or not path.parent.is_dir() or path.suffix != '.hype':
            raise ValueError('Use a new .hype path with an existing Hype-writable parent.')
        controller = client.invoke({'class': 'NSDocumentController'}, 'sharedDocumentController', retain=True)
        ref = client.invoke(controller, 'openUntitledDocumentAndDisplay:error:', True,
                            {'$out': 'NSError'}, retain=True)
        if not isinstance(ref, dict) or '$ref' not in ref:
            raise ValueError('Native document creation did not return a document handle.')
        saved = client.native('save', target=ref, to=str(path), type='com.tumult.hype.document', timeout=120)
        if saved.get('saved') is not True:
            raise ValueError('Initial save did not confirm completion. Preserve the untitled document.')
        # Failure to release this diagnostic record does not undo the confirmed save.
        # The client stops on failure; inspect the existing output instead of recreating it.
        if saved.get('job'):
            client.run('job.get', job=saved['job'], release=True)
        # Save To creates a copy and leaves the untitled document URL unset.
        # It is safe to close the just-created blank document only after this confirmed save.
        client.invoke(ref, 'close')
        client.run('document.open', path=str(path), display=True)
        return cls(client, path)

    def run(self, op, **fields):
        return self.client.run(op, document=self.path, **fields)

    def layouts(self):
        return self.run('layout.list')['layouts']

    def scene_ref(self, scene):
        return self.client.invoke(self.ref, 'sceneWithOid:', scene['id'], retain=True)

    def symbol_ref(self, scene):
        ref = self.client.invoke(self.scene_ref(scene), 'currentSymbol', retain=True)
        if self.client.invoke(ref, 'oid') != scene['symbol']:
            raise ValueError('Scene is displaying a different/nested symbol. Restore root context deliberately.')
        return ref

    def element_ref(self, scene, element):
        collection = self.client.invoke(self.symbol_ref(scene), 'allElements', retain=True)
        offset = 0
        while True:
            r = self.client.native('find', target=collection, where={'oid': element},
                                   offset=offset, limit=1, scanLimit=1000)
            if r['items']:
                return r['items'][0]
            if not r['hasMore']:
                raise ValueError('Element ID not found in the selected symbol.')
            if r['nextOffset'] <= offset:
                raise ValueError('Native find did not advance.')
            offset = r['nextOffset']

    def name_scene(self, scene, name):
        self.client.invoke(self.ref, 'setCurrentScene:', self.scene_ref(scene))
        container = self.client.invoke(self.ref, 'currentSceneContainer', retain=True)
        self.client.invoke(container, 'setName:', name)
        self.dirty()

    def add_scene(self, name):
        before = self.layouts()
        self.run('editor.action', scene=before[-1]['id'], name='scene.create', elements=[])
        fresh = [s for s in self.layouts() if s['id'] not in {x['id'] for x in before}]
        if len(fresh) != 1:
            raise ValueError('Scene creation did not add exactly one root layout; inspect before continuing.')
        self.name_scene(fresh[0], name)
        return fresh[0]

    def prepare_scene(self, scene, property='width'):
        q = dict(scene=scene['id'], property=property, applyToMatchingLayouts=False)
        r = self.run('scene.settings.prepare', **q)
        # A single deliberate follow-up is allowed only for an explicit pending preparation.
        if r.get('prepared') is not True:
            time.sleep(.6)
            r = self.run('scene.settings.prepare', **q)
        if not all(r.get(k) is True for k in ('prepared', 'bindingReady', 'scopeEstablished')):
            raise ValueError('Scene binding remains pending. No value was set.')
        time.sleep(.2)
        return q

    def setting(self, scene, property, value):
        q = self.prepare_scene(scene, property)
        current = self.run('scene.settings.get', **q)
        return self.run('scene.settings.set', **q, expectedValue=current['value'], value=value)

    def elements(self, scene):
        return self.client.page('element.list', 'elements', document=self.path, symbol=scene['symbol'])

    def attributes(self, scene, element, values):
        ref = self.element_ref(scene, element)
        attributes = [self.client.invoke({'class': 'HypeAttribute'}, 'attributeWithName:objectValue:',
                      key, value, retain=True) for key, value in values.items()]
        if any(not isinstance(a, dict) or '$ref' not in a for a in attributes):
            raise ValueError('Unknown attribute factory result; no attribute batch was committed.')
        self.client.invoke(ref, 'setAttributes:', attributes)
        self.dirty()
        # Detached attributes were constructed by this recipe, not borrowed controller objects.
        self.client.native('release', handles=[a['$ref'] for a in attributes])
        return self.run('element.get', symbol=scene['symbol'], element=element)

    def element(self, scene, kind, name, x, y, width, height, **values):
        before = {e['id'] for e in self.elements(scene)}
        self.run('editor.action', scene=scene['id'], name='insert.' + kind, elements=[])
        fresh = [e for e in self.elements(scene) if e['id'] not in before]
        if len(fresh) != 1:
            raise ValueError('Insertion did not add exactly one element. Inspect before continuing.')
        oid = fresh[0]['id']
        self.attributes(scene, oid, dict(DisplayName=name, Left=x, Top=y, Width=width, Height=height, **values))
        return oid

    def text(self, scene, name, html, x, y, width, height, size=24, ink='#202020', **values):
        defaults = dict(InnerHTML=html, FontSize=size, FontFamily='Arial', TextColor=color(ink),
                        LineHeight=size*1.2, ExplicitDimensions='YES',
                        PaddingTop=0, PaddingBottom=0, PaddingLeft=0, PaddingRight=0)
        defaults.update(values)
        return self.element(scene, 'text', name, x, y, width, height, **defaults)

    def script(self, name, source):
        script = self.run('javascript.add')['id']
        self.run('javascript.rename', script=script, value=name)
        self.run('javascript.setSource', script=script, value=source)
        return script

    def click(self, scene, element, fields):
        # These are native HypeAction values, not edits to a package/plist file.
        a = self.client.invoke({'class': 'HypeAction'}, 'actionWithPlistRepresentation:', fields, retain=True)
        if self.client.invoke(a, 'plistRepresentation') != fields:
            raise ValueError('Native action normalized unexpectedly. Inspect before assigning.')
        self.attributes(scene, element, {'ActionHandlerOnMouseClick': {'actions': [a]}})
        self.client.native('release', handles=[a['$ref']])

    def go(self, scene, button, target, transition=2, duration=.65):
        self.click(scene, button, dict(type=1, sceneOid=target['sceneContainer'],
                                      transition=transition, duration=duration))

    def run_script(self, scene, element, script):
        self.click(scene, element, dict(type=4, javascriptOid=script))

    def duration(self, scene, seconds):
        if seconds < 0:
            raise ValueError('Duration must be nonnegative.')
        timelines = self.client.invoke(self.symbol_ref(scene), 'timelines', retain=True)
        r = self.client.native('find', target=timelines, where={'identifier': MAIN}, limit=1, scanLimit=1000)
        if len(r['items']) != 1:
            raise ValueError('Main timeline not found.')
        self.client.invoke(r['items'][0], 'setUserDefinedDuration:', seconds)
        self.dirty()
        return self.run('timeline.list', symbol=scene['symbol'])

    def record(self, scene, element, property, start_value, end_value, end_seconds):
        # For a newly created, unanimated element on Main; do not use as a general retiming tool.
        self.duration(scene, end_seconds)
        q = dict(scene=scene['id'], symbol=scene['symbol'], element=element, timeline=MAIN, property=property)
        for seconds, value, recording in [(0, start_value, False), (end_seconds, end_value, True)]:
            prepared = self.run('inspector.prepare', **q, seconds=seconds)
            if prepared.get('prepared') is not True:
                raise ValueError('Inspector preparation did not complete.')
            actual = prepared['seconds']
            time.sleep(.6)
            current = self.run('inspector.get', **q, seconds=self.time_guard(scene, actual))
            result = self.run('inspector.set', **q, seconds=self.time_guard(scene, current['seconds']),
                              expectedValue=current['value'], value=value, recording=recording)
            if result.get('recordingRestored') is not True:
                raise ValueError('Recording restoration was not confirmed.')
        self.run('playhead.seek', scene=scene['id'], timeline=MAIN, seconds=0)
        return self.client.page('animation.list', 'animations', document=self.path,
                                symbol=scene['symbol'], timeline=MAIN)

    def time_guard(self, scene, seconds):
        rows = self.run('timeline.list', symbol=scene['symbol'])['timelines']
        main = [row for row in rows if row['id'] == MAIN]
        if len(main) != 1:
            raise ValueError('Expected exactly one Main timeline.')
        return timeline_guard_seconds(seconds, main[0]['duration'])

    def dirty(self):
        self.client.invoke(self.ref, 'updateChangeCount:', 0)  # NSChangeDone

    def save(self):
        result = self.run('document.save')
        if result.get('saved') is not True:
            raise ValueError('Save completion was not confirmed.')
        return result

    def export(self, destination):
        result = self.run('document.exportHTML', destination=str(Path(destination).absolute()))
        if result.get('exported') is not True:
            raise ValueError('Export completion was not confirmed.')
        return result
