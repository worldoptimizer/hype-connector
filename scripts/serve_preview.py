#!/usr/bin/env python3
"""Serve a local website preview. App downloads use the public release link."""
import argparse
import functools
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), functools.partial(SimpleHTTPRequestHandler, directory=str(ROOT / 'dist')))
    print(json.dumps({'url': f'http://127.0.0.1:{server.server_port}/'}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
