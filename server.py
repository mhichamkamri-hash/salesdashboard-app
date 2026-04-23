#!/usr/bin/env python3
"""
NETSCOUT Africa — Local Proxy Server (Python)
Usage:
  export ANTHROPIC_API_KEY=sk-ant-...
  python3 server.py
  Open: http://localhost:8080
"""

import os, json, http.server, urllib.request, urllib.error

PORT    = 8080
API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

MIME = {
    '.html': 'text/html',
    '.js':   'application/javascript',
    '.css':  'text/css',
    '.json': 'application/json',
    '.ico':  'image/x-icon',
}

class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        if '/api/claude' in str(args[0] if args else ''):
            status = args[1] if len(args)>1 else '?'
            print(f'  API → {status}')
        elif args and str(args[1] if len(args)>1 else '') not in ('200','304'):
            print(f'  {" ".join(str(a) for a in args)}')

    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-api-key,anthropic-version')

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors()
        self.end_headers()

    def do_POST(self):
        if self.path != '/api/claude':
            self.send_response(404); self.end_headers(); return

        # Check key is set
        if not API_KEY:
            self._json(500, {'error': 'ANTHROPIC_API_KEY not set. Stop server, run: export ANTHROPIC_API_KEY=sk-ant-... then restart.'})
            return

        # Check key format
        if not API_KEY.startswith('sk-ant-'):
            self._json(500, {'error': f'API key looks wrong (got: {API_KEY[:12]}...). It should start with sk-ant-'})
            return

        length = int(self.headers.get('Content-Length', 0))
        body   = self.rfile.read(length)

        try:
            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data    = body,
                method  = 'POST',
                headers = {
                    'Content-Type':      'application/json',
                    'x-api-key':         API_KEY,
                    'anthropic-version': '2023-06-01',
                }
            )
            with urllib.request.urlopen(req) as resp:
                data, status = resp.read(), resp.status

        except urllib.error.HTTPError as e:
            data   = e.read()
            status = e.code
            # Log the actual Anthropic error
            try:
                err = json.loads(data)
                print(f'  Anthropic error {status}: {err.get("error",{}).get("message","unknown")}')
            except:
                print(f'  Anthropic HTTP error: {status}')

        except Exception as e:
            self._json(502, {'error': str(e)}); return

        self._raw(status, data)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/': path = '/index.html'
        fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), path.lstrip('/'))
        if not os.path.isfile(fp):
            self.send_response(404); self.end_headers(); self.wfile.write(b'Not found'); return
        ext  = os.path.splitext(fp)[1]
        with open(fp, 'rb') as f: data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', MIME.get(ext, 'text/plain'))
        self.send_cors()
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status, obj):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_cors()
        self.end_headers()
        self.wfile.write(body)

    def _raw(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_cors()
        self.end_headers()
        self.wfile.write(data)


if __name__ == '__main__':
    print('\n╔══════════════════════════════════════════════╗')
    print('║  NETSCOUT Africa · Sales Intelligence App   ║')
    print('╚══════════════════════════════════════════════╝')
    print(f'\n  App:  http://localhost:{PORT}')
    if API_KEY:
        print(f'  Key:  ✓ {API_KEY[:18]}...')
    else:
        print('  Key:  ✗ NOT SET')
        print('\n  ► Stop this server (Ctrl+C)')
        print('  ► Run: export ANTHROPIC_API_KEY=sk-ant-...')
        print('  ► Then restart: python3 server.py\n')
    print()
    server = http.server.HTTPServer(('', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Server stopped.\n')
