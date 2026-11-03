"""Convenience recipes for measured root-scene authoring through Connector only.

No plist generation, direct package edits, editor GUI automation or hidden installs.
These model setters do not claim inspector-equivalent side effects or atomicity.
"""
from pathlib import Path
import math
import re
import struct
import time

MAIN = 'kTimelineDefaultIdentifier'


def _function_parts(source, name):
    """Recognize the documented function envelope, not arbitrary JavaScript."""
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*', name):
        raise ValueError('Use a JavaScript identifier for the function name.')
    if not isinstance(source, str):
        raise ValueError('Function source must be a string.')
    comments = r'(?:(?:\s+)|(?://[^\r\n]*(?:\r?\n|$))|(?:/\*[\s\S]*?\*/))*'
    match = re.fullmatch(
        r'(?P<header>' + comments + r')(?P<opening>function\s+' + re.escape(name)
        + r'\s*\(\s*hypeDocument\s*,\s*element\s*,\s*event\s*\)\s*\{)'
        + r'(?P<body>[\s\S]*)(?P<closing>\}\s*)', source)
    if not match:
        raise ValueError('Expected a named Hype function with hypeDocument, element, event. '
                         'Inspect custom source instead of replacing its envelope.')
    return match


def fill_function_template(template, native_name, name, body):
    """Fill only a fresh, empty native template; preserve its comments and spacing."""
    parts = _function_parts(template, native_name)
    if not isinstance(body, str) or parts['body'].strip():
        raise ValueError('Expected an empty native template and a string body. No replacement was made.')
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*', name):
        raise ValueError('Use a JavaScript identifier for the function name.')
    opening = re.sub(r'\bfunction\s+' + re.escape(native_name) + r'(?=\s*\()',
                     lambda m: m[0][:-len(native_name)] + name, parts['opening'], count=1)
    # Never reindent JavaScript: whitespace inside template literals is data.
    newline = '\r\n' if '\r\n' in template else '\n'
    if body and not body.startswith(('\n', '\r')):
        body = newline + body
    if body and not body.endswith(('\n', '\r')):
        body += newline
    return parts['header'] + opening + (body or parts['body']) + parts['closing']


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


_COMMENT_MARKERS = {'html': ('<!--',), 'svg': ('<!--',), 'css': ('/*', '*'),
                    'javascript': ('//', '/*', '*')}


def code_readability_issues(source, language):
    """List formatting problems in embedded HTML, SVG, CSS or JavaScript.

    Advisory only: reads no document, changes nothing and validates no syntax.
    An empty list means the layout heuristics passed, not that the code is needed.
    """
    if language not in _COMMENT_MARKERS:
        raise ValueError('Use html, svg, css or javascript.')
    if not isinstance(source, str):
        raise ValueError('Source must be a string.')
    markers = _COMMENT_MARKERS[language]
    lines = [line for line in source.splitlines() if line.strip()]
    comments = [line for line in lines if line.lstrip().startswith(markers) or '<!--' in line or '/*' in line]
    issues = []
    long = [n for n, line in enumerate(source.splitlines(), 1) if len(line) > 120]
    if long:
        issues.append(f'Lines over 120 characters: {long[:10]}. Put one element, rule or statement per line.')
    crowded = []
    for n, line in enumerate(source.splitlines(), 1):
        code = line.strip()
        if language in ('html', 'svg') and code.count('><') >= 2:
            crowded.append(n)
        elif language == 'css' and '{' in code and '}' in code and code.count(';') > 2:
            crowded.append(n)
        elif language == 'javascript' and not code.startswith('for') and code.rstrip(';').count(';') >= 2:
            crowded.append(n)
    if crowded:
        issues.append(f'Several elements, declarations or statements on one line: {crowded[:10]}.')
    if len(lines) > 3 and not any(line.lstrip().startswith(markers) for line in lines[:4]):
        issues.append('Start with a comment that says what the code does and why native Hype features are not enough.')
    if len(lines) > 15 and len(comments) < len(lines) // 15 + 1:
        issues.append('Add comments for the meaningful parts; long code has too few explanations.')
    return issues


class Document:
    def __init__(self, client, path):
        self.client, self.path = client, str(Path(path).absolute())
        self._ref = None
        self._features = None

    def supports(self, feature):
        """Read host features once per Document; a plugin cannot change while pinned."""
        if self._features is None:
            self._features = set(self.client.run('host.capabilities').get('features', []))
        return feature in self._features

    @property
    def ref(self):
        # Native-only recipes acquire their document handle lazily. Named
        # creation, settings and motion do not require the native escape hatch.
        if self._ref is None:
            controller = self.client.invoke({'class': 'NSDocumentController'},
                                            'sharedDocumentController', retain=True)
            ref = self.client.invoke(controller, 'documentForURL:',
                                     {'$url': Path(self.path).as_uri()}, retain=True)
            if not isinstance(ref, dict) or '$ref' not in ref:
                raise ValueError('Open this exact document before using a native recipe.')
            self._ref = ref
        return self._ref

    @classmethod
    def create(cls, client, destination):
        path = Path(destination).absolute()
        if path.exists() or not path.parent.is_dir() or path.suffix != '.hype':
            raise ValueError('Use a new .hype path with an existing writable parent.')
        result = client.run('document.create', destination=str(path), display=True)
        if result.get('created') is not True or result.get('saved') is not True:
            raise ValueError('Creation did not confirm initial save. Preserve state and inspect before continuing.')
        actual = result.get('document')
        if not isinstance(actual, str) or Path(actual).resolve() != path.resolve():
            raise ValueError('Creation returned a different document. Do not retry.')
        return cls(client, actual)

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
        if self.supports("sceneRename"):
            return self.run("scene.rename", scene=scene["id"], name=name)
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
        return self.run('scene.configure', scene=scene['id'], property=property, value=value)

    def edit(self, scene, element, property, value, seconds=0, **guards):
        return self.run('element.edit', scene=scene['id'], symbol=scene['symbol'],
                        timeline=MAIN, element=element, property=property,
                        value=value, seconds=seconds, **guards)

    def elements(self, scene):
        return self.client.page('element.list', 'elements', document=self.path, symbol=scene['symbol'])

    def attributes(self, scene, element, values):
        if self.supports('attributeBatch'):
            # One request: values are converted, checked and committed together.
            # The receipt already carries the full element projection.
            return self.run('element.setAttributes', symbol=scene['symbol'], element=element,
                            attributes=values)['element']
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

    def attributes_many(self, scene, values_by_element):
        """Set attributes of several elements: {element_id: {name: value}}.

        One request on hosts with multiElementAttributeBatch; every value is
        checked before the first commit. Returns per-element rows.
        """
        if self.supports('multiElementAttributeBatch'):
            return self.run('element.setAttributes', symbol=scene['symbol'],
                            elements=dict(values_by_element))['elements']
        return {oid: self.attributes(scene, oid, values) for oid, values in values_by_element.items()}

    def insert(self, scene, kind, values=None):
        """Insert one native element, optionally with attributes, and return its ID."""
        if values and self.supports('insertWithAttributes'):
            # One request: values are checked before insertion, then applied.
            receipt = self.run('editor.action', scene=scene['id'], name='insert.' + kind,
                               elements=[], attributes=dict(values))
            if receipt.get('insertedElements') != [receipt.get('element')] or not receipt.get('element'):
                raise ValueError('Insertion did not add exactly one element. Inspect before continuing.')
            return receipt['element']
        if self.supports('insertedElementIDs'):
            oid = self.insert_id(scene, kind)
        else:
            oid = self.insert_by_inventory(scene, kind)
        if values:
            self.attributes(scene, oid, values)
        return oid

    def insert_id(self, scene, kind):
        receipt = self.run('editor.action', scene=scene['id'], name='insert.' + kind, elements=[])
        fresh = receipt.get('insertedElements')
        if not isinstance(fresh, list) or len(fresh) != 1:
            raise ValueError('Insertion did not add exactly one element. Inspect before continuing.')
        return fresh[0]

    def insert_by_inventory(self, scene, kind):
        before = {e['id'] for e in self.elements(scene)}
        self.run('editor.action', scene=scene['id'], name='insert.' + kind, elements=[])
        fresh = [e for e in self.elements(scene) if e['id'] not in before]
        if len(fresh) != 1:
            raise ValueError('Insertion did not add exactly one element. Inspect before continuing.')
        return fresh[0]['id']

    def element(self, scene, kind, name, x, y, width, height, **values):
        return self.insert(scene, kind, dict(DisplayName=name, Left=x, Top=y, Width=width, Height=height, **values))

    def text(self, scene, name, html, x, y, width, height, size=24, ink='#202020', **values):
        defaults = dict(InnerHTML=html, FontSize=size, FontFamily='Arial', TextColor=color(ink),
                        LineHeight=size*1.2, ExplicitDimensions='YES',
                        PaddingTop=0, PaddingBottom=0, PaddingLeft=0, PaddingRight=0)
        defaults.update(values)
        return self.element(scene, 'text', name, x, y, width, height, **defaults)

    def script(self, name, source):
        """Create a function using Hype's header; accepts the existing full-source API."""
        parts = _function_parts(source, name)  # Validate before native insertion.
        return self.script_body(name, parts['body'], comments=parts['header'])

    def script_body(self, name, body, *, comments=''):
        """Create from a body without throwing away Hype's native template."""
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*', name):
            raise ValueError('Use a JavaScript identifier for the function name.')
        if not isinstance(body, str) or not isinstance(comments, str):
            raise ValueError('Body and comments must be strings.')
        if comments.strip():
            _function_parts(comments + '\nfunction ' + name + '(hypeDocument, element, event) {}', name)
        created = self.run('javascript.add')
        script = created['id']
        template = created['source']
        native = _function_parts(template, created['name'])
        # Keep caller comments too, but do not duplicate a copied native header.
        if comments.strip() and comments.strip() != native['header'].strip():
            body = comments + body
        source = fill_function_template(template, created['name'], name, body)
        self.run('javascript.rename', script=script, value=name)
        self.run('javascript.setSource', script=script, value=source)
        return script

    def replace_script_text(self, script, old, new, *, expected_source):
        """Apply one exact replacement, preserving all other source bytes.

        The read-before-write check is not an atomic editor lock. Avoid concurrent edits.
        """
        if not all(isinstance(v, str) for v in (old, new, expected_source)) or not old:
            raise ValueError('Provide a nonempty exact old text, new text and expected source.')
        rows = [r for r in self.run('javascript.list')['scripts'] if r['id'] == script]
        if len(rows) != 1 or rows[0]['source'] != expected_source:
            raise ValueError('Function changed or is missing. Read it again before editing.')
        if expected_source.count(old) != 1:
            raise ValueError('Replacement must match exactly once; nothing was written.')
        return self.run('javascript.setSource', script=script, value=expected_source.replace(old, new, 1))

    def click(self, scene, element, fields):
        if self.supports('attributeBatch'):
            # The host builds the native HypeAction and refuses a normalized plist.
            return self.attributes(scene, element, {'ActionHandlerOnMouseClick': {'actions': [fields]}})
        # These are native HypeAction values, not edits to a package/plist file.
        a = self.client.invoke({'class': 'HypeAction'}, 'actionWithPlistRepresentation:', fields, retain=True)
        if self.client.invoke(a, 'plistRepresentation') != fields:
            raise ValueError('Native action normalized unexpectedly. Inspect before assigning.')
        self.attributes(scene, element, {'ActionHandlerOnMouseClick': {'actions': [a]}})
        self.client.native('release', handles=[a['$ref']])

    def go(self, scene, button, target, transition=2, duration=.65):
        return self.click(scene, button, dict(type=1, sceneOid=target['sceneContainer'],
                                      transition=transition, duration=duration))

    def run_script(self, scene, element, script):
        return self.click(scene, element, dict(type=4, javascriptOid=script))

    def duration(self, scene, seconds):
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or seconds <= 0:
            raise ValueError('Explicit duration must be a finite positive number.')
        rows = self.run('timeline.list', symbol=scene['symbol'])['timelines']
        main = [row for row in rows if row['id'] == MAIN]
        if len(main) != 1:
            raise ValueError('Expected exactly one Main timeline.')
        return self.run('timeline.setDuration', symbol=scene['symbol'], timeline=MAIN,
                        seconds=seconds, expectedDuration=main[0]['duration'])

    def record(self, scene, element, property, start_value, end_value, end_seconds):
        # The composed API refuses a pre-existing lane and never shortens Main.
        # Return its complete verified receipt, including actual animation rows.
        return self.run('animation.create', scene=scene['id'], symbol=scene['symbol'],
                        timeline=MAIN, element=element, property=property,
                        **{'from': start_value, 'to': end_value, 'seconds': end_seconds})

    def keyframes(self, scene, element, property, frames, expected_animations=None, settle_timeout=None):
        """Record several native keyframes on one Main lane in one request.

        frames: [{'seconds': 0, 'value': 278}, {'seconds': .6, 'value': 230,
        'timingFunction': doc.timing('Ease Out')}, ...]. Without
        expected_animations the current lane is read first; a lane changed in
        between is refused by the host, never overwritten. Times must lie on
        the editor frame grid (multiples of 1/30 s at 30 fps). settle_timeout
        (0 to 10 s, host default 3) bounds each readiness phase.
        """
        if expected_animations is None:
            rows = self.client.page('animation.list', 'animations', document=self.path,
                                    symbol=scene['symbol'], timeline=MAIN)
            expected_animations = [r['id'] for r in rows
                                   if r.get('referenceOid') == element and r.get('identifier') == property]
        extra = {} if settle_timeout is None else {'settleTimeout': settle_timeout}
        return self.run('animation.keyframes', scene=scene['id'], symbol=scene['symbol'],
                        timeline=MAIN, element=element, property=property,
                        keyframes=list(frames), expectedAnimations=list(expected_animations), **extra)

    def timing(self, name):
        """Return the document-local timing-function ID with this exact name."""
        rows = [r for r in self.run('timingFunction.list')['timingFunctions'] if r.get('name') == name]
        if len(rows) != 1:
            raise ValueError('Timing function name must match exactly one entry: ' + repr(name))
        return rows[0]['id']

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
