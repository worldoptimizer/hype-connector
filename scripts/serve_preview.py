#!/usr/bin/env python3
"""Serve a local design preview, optionally with an explicitly selected DMG."""
import argparse
import functools
import json
import shutil
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--download', type=Path, help='Optional local notarized DMG to offer through the preview download button')
    args = parser.parse_args()
    artifact = args.download.resolve(strict=True) if args.download else None
    if artifact and (not artifact.is_file() or artifact.suffix != '.dmg'):
        parser.error('--download must be a regular DMG file')

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if urlsplit(self.path).path == '/downloads/Connector-0.1.4-build21.dmg':
                if not artifact:
                    self.send_error(503, 'No local app download selected for this design preview')
                    return
                self.send_response(200)
                self.send_header('Content-Type', 'application/x-apple-diskimage')
                self.send_header('Content-Length', str(artifact.stat().st_size))
                self.send_header('Content-Disposition', 'attachment; filename="Connector-0.1.4-build21.dmg"')
                self.end_headers()
                with artifact.open('rb') as stream:
                    shutil.copyfileobj(stream, self.wfile)
                return
            super().do_GET()

    server = ThreadingHTTPServer(('127.0.0.1', args.port), functools.partial(Handler, directory=str(ROOT / 'dist')))
    print(json.dumps({'url': f'http://127.0.0.1:{server.server_port}/', 'downloadAvailable': artifact is not None}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
