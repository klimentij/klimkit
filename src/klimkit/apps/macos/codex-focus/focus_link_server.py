#!/usr/bin/env python3
import html
import http.server
import socketserver
import sys
import urllib.parse
from typing import Optional

HOST = "127.0.0.1"
PORT = 43123


def _build_deep_link(query: str) -> Optional[str]:
    params = urllib.parse.parse_qs(query, keep_blank_values=False)
    if "target" in params and params["target"]:
        return "codexfocus://open?target=" + urllib.parse.quote(params["target"][0], safe="")
    if "url" in params and params["url"]:
        return "codexfocus://open?url=" + urllib.parse.quote(params["url"][0], safe="")
    return None


class FocusLinkHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path not in ("/", "/open"):
            self.send_error(404, "Not Found")
            return

        deep_link = _build_deep_link(parsed.query)
        escaped_link = html.escape(deep_link or "", quote=True)
        open_button = ""
        guidance = "<p>Missing <code>url=</code> or <code>target=</code> query parameter.</p>"
        redirect_script = ""

        if deep_link is not None:
            open_button = f'<a href="{escaped_link}">Open Codex Focus</a>'
            guidance = "<p>If it does not open automatically, click the button below.</p>"
            redirect_script = f"<script>window.location.replace({deep_link!r});</script>"

        body = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Opening Codex Focus…</title>
    <style>
      body {{
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 0;
        padding: 32px 20px;
        background: #111;
        color: #f5f5f5;
      }}
      main {{
        max-width: 520px;
        margin: 0 auto;
      }}
      a {{
        display: inline-block;
        margin-top: 16px;
        padding: 12px 16px;
        border-radius: 10px;
        background: #0a84ff;
        color: white;
        text-decoration: none;
        font-weight: 600;
      }}
      p {{
        line-height: 1.5;
      }}
      code {{
        word-break: break-all;
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>Opening Codex Focus…</h1>
      {guidance}
      {open_button}
      <p><code>{escaped_link}</code></p>
    </main>
    {redirect_script}
  </body>
</html>
"""
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> int:
    with socketserver.TCPServer((HOST, PORT), FocusLinkHandler) as server:
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
