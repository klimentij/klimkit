#!/usr/bin/env python3
"""Serve Klimkit report HTML from one or more repository roots.

This is a small reference implementation for the klimkit-report-server skill.
It intentionally avoids Klimkit's deprecated runtime service layer.
"""

from __future__ import annotations

import argparse
import html
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote


def find_reports(root: Path) -> list[Path]:
    klimkit = root / ".klimkit"
    if not klimkit.exists():
        return []
    reports = list((klimkit / "reports").glob("**/*.html"))
    for operator_dir in klimkit.iterdir():
        if not operator_dir.is_dir() or operator_dir.name in {"local", "state", "backups", "logs", "tasks", "reports"}:
            continue
        reports.extend((operator_dir / "reports").glob("**/*.html"))
    return sorted({path.resolve() for path in reports if path.is_file()})


class ReportsHandler(SimpleHTTPRequestHandler):
    roots: list[Path] = []
    report_map: dict[str, Path] = {}

    def do_GET(self) -> None:
        if self.path in {"/", "/reports", "/reports/"}:
            self.render_index()
            return
        if self.path.startswith("/reports/r/"):
            key = unquote(self.path.removeprefix("/reports/r/"))
            report = self.report_map.get(key)
            if report is None:
                self.send_error(HTTPStatus.NOT_FOUND, "Report not found")
                return
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(report.read_bytes())
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def render_index(self) -> None:
        self.report_map.clear()
        rows = []
        for root_index, root in enumerate(self.roots):
            for report in find_reports(root):
                key = f"{root_index}/{report.relative_to(root).as_posix()}"
                self.report_map[key] = report
                rows.append(
                    "<li>"
                    f"<a href=\"/reports/r/{quote(key)}\">{html.escape(report.name)}</a>"
                    f" <code>{html.escape(str(report.relative_to(root)))}</code>"
                    "</li>"
                )
        body = "\n".join(rows) or "<li>No reports found.</li>"
        page = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Klimkit Reports</title>
<style>
body {{ font: 16px/1.5 system-ui, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; }}
code {{ color: #445; }}
li {{ margin: 0.5rem 0; }}
</style>
<h1>Klimkit Reports</h1>
<ul>{body}</ul>
</html>
"""
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve .klimkit report HTML files.")
    parser.add_argument("roots", nargs="*", default=["."], help="Repository roots to scan")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    ReportsHandler.roots = [Path(root).expanduser().resolve() for root in args.roots]
    server = ThreadingHTTPServer((args.host, args.port), ReportsHandler)
    print(f"Serving Klimkit reports at http://{args.host}:{args.port}/reports/")
    server.serve_forever()


if __name__ == "__main__":
    main()
