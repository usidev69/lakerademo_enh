#!/usr/bin/env python3
"""
Proxy server for Lakera Guard Demo.

Needed because browsers block direct calls to the Lakera API (CORS policy).
This script serves index.html and forwards /proxy/lakera requests to the real API.

API keys can be configured via environment variables or a .env file in the
same directory as this script.  Actual environment variables take precedence
over values in .env.

Supported variables:
  LAKERA_API_KEY        – Lakera Guard API key
  LAKERA_PROJECT_ID     – Lakera project ID (optional)
  LAKERA_ENDPOINT       – Lakera endpoint URL (optional)
  LLM_PROVIDER          – openai | anthropic | gemini | ollama | lmstudio
  LLM_API_KEY           – LLM provider API key
  LLM_MODEL             – model name / ID
  LLM_ENDPOINT          – base URL for ollama / lmstudio (optional)
  LLM_SYSTEM_PROMPT     – system prompt for the LLM (optional)

Usage:
    python3 proxy.py          # listens on port 8080
    python3 proxy.py 9090     # custom port
"""

import http.server
import urllib.request
import urllib.error
import urllib.parse
import json
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
ALLOWED_HOSTS = ('api.lakera.ai', 'us-east-1.api.lakera.ai', 'eu-west-1.api.lakera.ai')

# ── .env loader ──────────────────────────────────────────────────────────────

def _load_env_file(path='.env'):
    """
    Parse a simple KEY=VALUE .env file and populate os.environ for any key
    that is not already set as a real environment variable.
    Supports # comments, blank lines, and single/double-quoted values.
    Does NOT support multi-line values or variable expansion.
    """
    if not os.path.isfile(path):
        return
    loaded = []
    with open(path, encoding='utf-8') as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            # Quoted values: strip quotes and keep as-is (no comment stripping inside quotes)
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            else:
                # Unquoted: strip inline comments (' #' or '\t#' and everything after)
                for sep in (' #', '\t#'):
                    pos = value.find(sep)
                    if pos != -1:
                        value = value[:pos].strip()
                        break
                # Value that is only a comment (e.g. KEY=  # note) → treat as empty
                if value.startswith('#'):
                    value = ''
            if key and key not in os.environ:
                os.environ[key] = value
                loaded.append(key)
    if loaded:
        print(f'  .env  loaded {len(loaded)} variable(s): {", ".join(loaded)}')


def _build_env_config():
    """Return a dict of non-empty env-derived config values for the frontend.

    Guard IN/OUT can each have their own project ID/name.
    LAKERA_PROJECT_ID / LAKERA_PROJECT_NAME act as fallbacks for both if the
    specific IN/OUT variables are not set.
    """
    fallback_id   = os.environ.get('LAKERA_PROJECT_ID', '')
    fallback_name = os.environ.get('LAKERA_PROJECT_NAME', '')
    mapping = {
        'lakeraApiKey':          os.environ.get('LAKERA_API_KEY', ''),
        # Guard IN
        'lakeraInProjectId':     os.environ.get('LAKERA_GUARD_IN_PROJECT_ID',   fallback_id),
        'lakeraInProjectName':   os.environ.get('LAKERA_GUARD_IN_PROJECT_NAME', fallback_name),
        # Guard OUT
        'lakeraOutProjectId':    os.environ.get('LAKERA_GUARD_OUT_PROJECT_ID',  fallback_id),
        'lakeraOutProjectName':  os.environ.get('LAKERA_GUARD_OUT_PROJECT_NAME', fallback_name),
        'lakeraEndpoint':        os.environ.get('LAKERA_ENDPOINT', ''),
        'llmProvider':           os.environ.get('LLM_PROVIDER', ''),
        'llmApiKey':             os.environ.get('LLM_API_KEY', ''),
        'llmModel':              os.environ.get('LLM_MODEL', ''),
        'llmEndpoint':           os.environ.get('LLM_ENDPOINT', ''),
        'llmSystemPrompt':       os.environ.get('LLM_SYSTEM_PROMPT', ''),
    }
    return {k: v for k, v in mapping.items() if v}


# ── HTTP handler ─────────────────────────────────────────────────────────────

class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()}  {fmt % args}")

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?')[0]
        if path in ('/', '/index.html'):
            self._serve_file('index.html', 'text/html; charset=utf-8')
        elif path == '/api/config':
            self._serve_env_config()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.startswith('/proxy/lakera'):
            self._proxy_lakera()
        else:
            self.send_error(404)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _serve_file(self, filename, content_type):
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(data))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404, f'{filename} not found')

    def _serve_env_config(self):
        cfg = _build_env_config()
        body = json.dumps(cfg).encode()
        self.send_response(200)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _proxy_lakera(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        target = params.get('url', ['https://api.lakera.ai/v2/guard'])[0]

        target_host = urllib.parse.urlparse(target).hostname or ''
        if target_host not in ALLOWED_HOSTS:
            self._json_error(403, f'Target host not allowed: {target_host}')
            return

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        auth = self.headers.get('Authorization', '')

        print(f"  → forwarding to {target}")
        print(f"  → Authorization: {auth[:16]}… ({len(auth)} chars)" if auth else "  → Authorization: (empty)")

        req = urllib.request.Request(
            target,
            data=body,
            headers={
                'Content-Type': 'application/json',
                'Authorization': auth,
                'User-Agent': 'lakera-guard-demo/1.0',
                'Accept': 'application/json',
            },
            method='POST',
        )

        try:
            with urllib.request.urlopen(req) as resp:
                resp_body = resp.read()
                self._forward_response(resp.status, resp_body)
        except urllib.error.HTTPError as e:
            resp_body = e.read()
            print(f"  ← Lakera HTTP {e.code}: {resp_body[:200]}")
            self._forward_response(e.code, resp_body)
        except Exception as e:
            self._json_error(502, f'Proxy error: {e}')

    def _forward_response(self, status, body):
        self.send_response(status)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def _json_error(self, status, message):
        body = json.dumps({'error': message}).encode()
        self.send_response(status)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    _load_env_file('.env')

    cfg_preview = _build_env_config()
    if cfg_preview:
        masked = {k: (v[:6] + '…' if 'Key' in k and len(v) > 6 else v)
                  for k, v in cfg_preview.items()}
        print(f'  env   config: {masked}')
    else:
        print('  env   no API keys configured (set vars or create .env)')

    addr = ('', PORT)
    with http.server.HTTPServer(addr, Handler) as httpd:
        print(f'\nLakera Guard Demo  →  http://localhost:{PORT}')
        print(f'Proxy endpoint     →  http://localhost:{PORT}/proxy/lakera')
        print(f'Env config         →  http://localhost:{PORT}/api/config')
        print('Press Ctrl+C to stop.\n')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nStopped.')
