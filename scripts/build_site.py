#!/usr/bin/env python3
"""Build the public static site from an explicit set of public files. No upload."""
import argparse
import html
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZipFile, ZIP_DEFLATED

import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ('docs/getting-started.md', 'getting-started', 'Getting started'),
    ('docs/updates.md', 'updates', 'App and plugin updates'),
    ('docs/scripting.md', 'scripting', 'Manual scripting'),
    ('docs/mcp.md', 'mcp', 'MCP & agents'),
    ('docs/applescript.md', 'applescript', 'AppleScript'),
    ('docs/examples.md', 'examples', 'Runnable examples'),
    ('skills/README.md', 'agent-skill', 'Install the skill'),
    ('docs/troubleshooting.md', 'troubleshooting', 'Troubleshooting'),
    ('examples/README.md', 'example-files', 'Example files'),
    ('skills/hype-connector/references/connection-and-delivery.md', 'skill-connection', 'Connection and delivery'),
    ('skills/hype-connector/references/operations.md', 'skill-operations', 'Operation recipes'),
    ('skills/hype-connector/references/compatibility.md', 'skill-compatibility', 'Compatibility and limits'),
    ('skills/hype-connector/references/native-recipes.md', 'skill-native', 'Native authoring recipes'),
    ('skills/hype-connector/references/design-recipes.md', 'skill-design', 'Design recipes'),
]
EXAMPLES = ['build_template.py', 'build_image_template.py', 'build_animation_template.py']
ASSETS = ['style.css', 'site.js', 'connector-mark.svg', 'connector-app-icon.png', 'eiszeit.jpg', 'connector-share-v2.png', 'connector-hero-v1.png', 'connector-brand.css']
SITE_URL = 'https://worldoptimizer.github.io/hype-connector/'
SHARE_IMAGE = SITE_URL + 'assets/connector-share-v2.png'
SHARE_ALT = 'Connector — Automations for Tumult Hype 4, with the Connector chain-link app icon on a warm white background.'


def share_tags():
    return f'''<meta property="og:site_name" content="Connector">
<meta property="og:image" content="{SHARE_IMAGE}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1734">
<meta property="og:image:height" content="907">
<meta property="og:image:alt" content="{SHARE_ALT}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SHARE_IMAGE}">
<meta name="twitter:image:alt" content="{SHARE_ALT}">'''


SKILL_FILES = [
    'SKILL.md',
    'scripts/connector_client.py',
    'scripts/authoring.py',
    'references/operations.md',
    'references/compatibility.md',
    'references/connection-and-delivery.md',
    'references/native-recipes.md',
    'references/design-recipes.md',
]
SKILL_ROOT = ROOT / 'skills/hype-connector'
DEMO_FILES = ['index.html', 'index.hyperesources/Eiszeit-Showcase-hero.jpg', 'index.hyperesources/Eiszeit-Showcase-hero_2x.jpg', 'index.hyperesources/HYPE-786.full.min.js', 'index.hyperesources/HYPE-786.thin.min.js', 'index.hyperesources/PIE.htc', 'index.hyperesources/blank.gif', 'index.hyperesources/index_hype_generated_script.js']


def build(preview=False):
    # Fail before replacing a previous preview if the curated skill is incomplete.
    for relative in SKILL_FILES:
        source = SKILL_ROOT / relative
        if not source.is_file() or any(part.is_symlink() for part in (source, *source.parents)):
            raise RuntimeError('Missing or symlinked public skill file: ' + relative)
    dist = ROOT / 'dist'
    if dist.is_symlink():
        raise RuntimeError('Refusing a symlinked output directory')
    if dist.exists():
        shutil.rmtree(dist)
    for directory in ['assets', 'guides', 'downloads/examples']:
        (dist / directory).mkdir(parents=True, exist_ok=True)
    for asset in ASSETS:
        shutil.copyfile(ROOT / 'site/assets' / asset, dist / 'assets' / asset)
    for relative in DEMO_FILES:
        source = ROOT / 'site/demos/eiszeit' / relative
        if not source.is_file() or any(part.is_symlink() for part in (source, *source.parents)):
            raise RuntimeError('Missing or symlinked demo file: ' + relative)
        destination = dist / 'demos/eiszeit' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    feed = ROOT / 'site/updates/appcast.xml'
    if not feed.is_file() or feed.is_symlink():
        raise RuntimeError('Missing signed update feed')
    (dist / 'updates').mkdir()
    shutil.copyfile(feed, dist / 'updates/appcast.xml')
    banner = ('<div class="preview-banner">Local preview. Nothing has been published.</div>' if preview else '')
    button = '<p class="availability" lang="en">Coming soon</p>'
    homepage = (ROOT / 'site/index.html').read_text().replace('<!--PREVIEW_NOTICE-->', banner).replace('<!--DOWNLOAD_BUTTON-->', button)
    homepage = homepage.replace('<!--SHARE_METADATA-->', share_tags())
    showcase_link = '<a href="demos/eiszeit/index.html">Play the EISZEIT demo</a>'
    homepage = homepage.replace('<!--SHOWCASE_LINK-->', showcase_link)
    (dist / 'index.html').write_text(homepage)
    routes = {str((ROOT / source).resolve()): slug for source, slug, _ in DOCS}

    def rewrite_links(body, source):
        def link(match):
            target = html.unescape(match.group(1))
            if target == 'https://worldoptimizer.github.io/hype-connector/downloads/hype-connector-skill.zip':
                return 'href="../downloads/hype-connector-skill.zip"'
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                return match.group(0)
            resolved = (source.parent / parsed.path).resolve()
            if not resolved.is_relative_to(ROOT):
                raise RuntimeError('Document link escapes the public checkout: ' + target)
            if str(resolved) in routes:
                rewritten = routes[str(resolved)] + '.html'
            elif resolved == ROOT / 'site/demos/eiszeit/index.html':
                rewritten = '../demos/eiszeit/index.html'
            elif resolved.parent == ROOT / 'examples' and resolved.name in EXAMPLES:
                rewritten = '../downloads/examples/' + resolved.name
            elif resolved in {SKILL_ROOT / relative for relative in SKILL_FILES}:
                rewritten = '../downloads/hype-connector/' + resolved.relative_to(SKILL_ROOT).as_posix()
            else:
                raise RuntimeError('Unmapped public document link: ' + target)
            if parsed.fragment:
                rewritten += '#' + parsed.fragment
            return 'href="' + html.escape(rewritten, quote=True) + '"'
        return re.sub(r'href="([^"]+)"', link, body)

    for source_path, slug, title in DOCS:
        source = ROOT / source_path
        content = markdown.markdown(source.read_text(), extensions=['fenced_code', 'tables', 'toc', 'sane_lists'])
        content = rewrite_links(content, source)
        nav = ''.join('<a href="' + other + '.html"' + (' aria-current="page"' if other == slug else '') + '>' + html.escape(label) + '</a>' for path, other, label in DOCS if path != 'examples/README.md')
        document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f5f4f0"><title>{html.escape(title)} — Connector</title><meta name="description" content="{html.escape(title)} with Connector for Tumult Hype 4."><link rel="icon" href="../assets/connector-app-icon.png" type="image/png"><link rel="stylesheet" href="../assets/style.css"><link rel="stylesheet" href="../assets/connector-brand.css"><script src="../assets/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>{banner}
<header class="site-header wrap"><a class="brand" href="../"><img src="../assets/connector-app-icon.png" width="76" height="76" alt="">Connector</a><nav aria-label="Main navigation"><a href="../#examples">Examples</a><a href="getting-started.html">Documentation</a><a href="agent-skill.html">Agent skill</a><a href="../#download">Coming soon</a></nav></header>
<div class="doc-layout wrap"><aside class="doc-sidebar" aria-label="Documentation"><details class="guide-menu" open><summary>Browse guides</summary><label class="sr-only" for="guide-filter">Filter guide titles</label><input id="guide-filter" class="doc-search" type="search" placeholder="Find a guide"><nav aria-label="Guide navigation">{nav}</nav><p class="search-empty" hidden>No matching guide titles.</p></details></aside><main id="main" class="doc-content">{content}<div class="doc-end">Connector 0.1.4 · <a href="https://github.com/worldoptimizer/hype-connector">Project on GitHub</a></div></main></div>
<footer class="footer wrap"><p>By Max Ziebell. Independent software for Tumult Hype.</p><a class="footer-brand" href="../"><img src="../assets/connector-app-icon.png" alt="" width="28" height="28">Connector home</a></footer><div class="copy-status sr-only" aria-live="polite"></div></body></html>'''
        metadata = (f'<meta property="og:title" content="{html.escape(title, quote=True)} — Connector">'
                    f'<meta property="og:description" content="{html.escape(title, quote=True)} with Connector for Tumult Hype 4.">'
                    f'<meta property="og:type" content="article">'
                    f'<meta property="og:url" content="{SITE_URL}guides/{slug}.html">'
                    + share_tags())
        document = document.replace('</head>', metadata + '</head>')
        (dist / 'guides' / (slug + '.html')).write_text(document)
    for filename in EXAMPLES:
        shutil.copyfile(ROOT / 'examples' / filename, dist / 'downloads/examples' / filename)
    with ZipFile(dist / 'downloads/connector-examples.zip', 'w', ZIP_DEFLATED) as archive:
        for filename in EXAMPLES + ['README.md']:
            archive.write(ROOT / 'examples' / filename, 'connector-examples/examples/' + filename)
        for source, _, _ in DOCS:
            if source.startswith('docs/'):
                text = (ROOT / source).read_text()
                text = text.replace('../site/demos/eiszeit/index.html', 'https://worldoptimizer.github.io/hype-connector/demos/eiszeit/index.html')
                text = text.replace('../skills/hype-connector/references/design-recipes.md', 'https://worldoptimizer.github.io/hype-connector/guides/skill-design.html')
                text = text.replace('../skills/hype-connector/references/native-recipes.md', 'https://worldoptimizer.github.io/hype-connector/guides/skill-native.html')
                archive.writestr('connector-examples/' + source, text)
        archive.writestr('connector-examples/README.md', '# Connector examples\n\nStart with [the example guide](docs/examples.md). Keep the three scripts in `examples/` together and run them from that folder. Supply your own Hype base document.\n')
    with ZipFile(dist / 'downloads/hype-connector-skill.zip', 'w', ZIP_DEFLATED) as archive:
        for relative in SKILL_FILES:
            source = SKILL_ROOT / relative
            archive.write(source, 'hype-connector/' + relative)
            downloadable = dist / 'downloads/hype-connector' / relative
            downloadable.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, downloadable)
    (dist / '.nojekyll').write_text('')
    (dist / 'robots.txt').write_text('User-agent: *\n' + ('Disallow: /\n' if preview else 'Allow: /\n'))
    print('Built', len(DOCS), 'guides, the landing page and two downloads in', dist)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true', help='Show local preview status')
    args = parser.parse_args()
    build(args.preview)
