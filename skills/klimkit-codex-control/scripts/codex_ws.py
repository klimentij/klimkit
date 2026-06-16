#!/usr/bin/env python3
"""
codex_ws.py — talk to a running Codex app-server over its WebSocket transport.

This is the ONLY reliable way to drive a Codex session so that turns appear
*live* in every connected client (the Codex desktop app, mobile, other TUIs).
It connects to the SAME app-server instance the desktop is subscribed to, then
speaks the JSON-RPC protocol (initialize -> initialized -> thread/* -> turn/*).

Why a custom WebSocket client and not `codex exec resume`?
  - `codex exec resume` spawns a SEPARATE process. It appends to the rollout
    file on disk but the running app-server never hears about it, so the desktop
    stays stale until the app is restarted.
  - The unix-socket / ws:// transports are WebSocket (HTTP Upgrade + frames),
    NOT raw newline-delimited JSON. Piping raw JSONL (even through
    `codex app-server proxy`) is silently dropped. You MUST do a real WS
    handshake and send each JSON-RPC message as a WS text frame. That is what
    this script does, using only the Python standard library.

Transports:
  - unix socket (default): --sock /path/to/...sock   (auto-discovered if omitted)
  - tcp websocket:         --ws ws://127.0.0.1:4500   (+ --token / --token-file)

Subcommands:
  list      List threads known to the app-server
  send      Resume an existing thread and send a message (appears live)
  new       Start a NEW thread (optionally send a first message)
  read      Read a thread's history (metadata + turns)
  watch     Subscribe to a thread and print live events without sending anything
  interrupt Interrupt the active turn of a thread

Examples:
  python codex_ws.py list
  python codex_ws.py send --thread 019ecf57-...-a -t "Give me a joke about the ocean"
  python codex_ws.py new --cwd /home/me/proj -m gpt-5.5 -t "Summarize README.md"
  python codex_ws.py read --thread 019ecf57-...-a
  python codex_ws.py watch --thread 019ecf57-...-a
"""
import argparse, base64, glob, json, os, socket, struct, sys, threading, time

DEFAULT_HOME = os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))


# --------------------------------------------------------------------------- #
# Socket discovery
# --------------------------------------------------------------------------- #
def discover_sock():
    """Prefer the desktop's socket (so turns show in the desktop app), else the
    managed control socket. Returns a path or None."""
    ctrl = os.path.join(DEFAULT_HOME, "app-server-control")
    desktop = sorted(glob.glob(os.path.join(ctrl, "desktop-ssh-websocket-*.sock")))
    if desktop:
        return desktop[0]
    fallback = os.path.join(ctrl, "app-server-control.sock")
    return fallback if os.path.exists(fallback) else None


# --------------------------------------------------------------------------- #
# Minimal WebSocket client (stdlib only)
# --------------------------------------------------------------------------- #
def _open_transport(sock_path, ws_url):
    if ws_url:
        assert ws_url.startswith(("ws://", "wss://")), "ws_url must start ws://"
        hostport = ws_url.split("://", 1)[1].split("/", 1)[0]
        host, _, port = hostport.partition(":")
        s = socket.create_connection((host, int(port or 80)))
        return s, host
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sock_path)
    return s, "localhost"


def ws_connect(sock_path=None, ws_url=None, token=None):
    s, host = _open_transport(sock_path, ws_url)
    key = base64.b64encode(os.urandom(16)).decode()
    lines = [
        "GET / HTTP/1.1",
        f"Host: {host}",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Sec-WebSocket-Key: {key}",
        "Sec-WebSocket-Version: 13",
    ]
    if token:
        lines.append(f"Authorization: Bearer {token}")
    s.sendall(("\r\n".join(lines) + "\r\n\r\n").encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        d = s.recv(4096)
        if not d:
            raise RuntimeError("server closed during WS handshake; got: %r" % buf)
        buf += d
    header, rest = buf.split(b"\r\n\r\n", 1)
    status = header.split(b"\r\n", 1)[0].decode()
    if "101" not in status:
        raise RuntimeError("WS handshake failed: %s" % status)
    return s, rest


def send_text(s, text):
    payload = text.encode("utf-8")
    out = bytearray([0x80 | 0x1])  # FIN + text opcode
    mask = os.urandom(4)
    n = len(payload)
    if n < 126:
        out.append(0x80 | n)
    elif n < 65536:
        out.append(0x80 | 126); out += struct.pack(">H", n)
    else:
        out.append(0x80 | 127); out += struct.pack(">Q", n)
    out += mask
    out += bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    s.sendall(bytes(out))


def frame_reader(s, initial, on_message, on_close):
    buf = bytearray(initial)

    def recvn(n):
        while len(buf) < n:
            d = s.recv(65536)
            if not d:
                return None
            buf.extend(d)
        out = bytes(buf[:n]); del buf[:n]
        return out

    def loop():
        while True:
            h = recvn(2)
            if h is None:
                on_close(); return
            opcode = h[0] & 0x0F
            masked = h[1] & 0x80
            ln = h[1] & 0x7F
            if ln == 126:
                ln = struct.unpack(">H", recvn(2))[0]
            elif ln == 127:
                ln = struct.unpack(">Q", recvn(8))[0]
            mkey = recvn(4) if masked else None
            payload = recvn(ln) if ln else b""
            if payload is None:
                on_close(); return
            if masked and mkey:
                payload = bytes(b ^ mkey[i % 4] for i, b in enumerate(payload))
            if opcode == 0x1:
                on_message(payload.decode("utf-8", "replace"))
            elif opcode == 0x8:
                on_close(); return
            # 0x9 ping / 0xA pong: ignore (messages are small, single-frame)

    t = threading.Thread(target=loop, daemon=True)
    t.start()
    return t


# --------------------------------------------------------------------------- #
# JSON-RPC session helper
# --------------------------------------------------------------------------- #
class Session:
    def __init__(self, sock_path=None, ws_url=None, token=None, raw=False):
        self.s, rest = ws_connect(sock_path, ws_url, token)
        self.raw = raw
        self.resp = {}
        self.events = []
        self._id = 0
        frame_reader(self.s, rest, self._on_msg, lambda: None)

    def _on_msg(self, line):
        if self.raw:
            print(line, flush=True)
        try:
            m = json.loads(line)
        except Exception:
            return
        if "id" in m and ("result" in m or "error" in m):
            self.resp[m["id"]] = m
        if "method" in m:
            self.events.append(m)

    def _next_id(self):
        self._id += 1
        return self._id

    def call(self, method, params, timeout=30):
        rid = self._next_id()
        send_text(self.s, json.dumps({"method": method, "id": rid, "params": params}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            if rid in self.resp:
                r = self.resp[rid]
                if "error" in r:
                    raise RuntimeError(f"{method} error: {json.dumps(r['error'])}")
                return r["result"]
            time.sleep(0.05)
        raise TimeoutError(f"{method} timed out after {timeout}s")

    def notify(self, method, params=None):
        msg = {"method": method}
        if params is not None:
            msg["params"] = params
        send_text(self.s, json.dumps(msg))

    def initialize(self, name="codex_ws-client"):
        self.call("initialize", {"clientInfo": {
            "name": name, "title": name, "version": "1.0.0"}})
        self.notify("initialized")
        time.sleep(0.2)

    def stream_turn(self, want_reply=True, timeout=180):
        """Wait for the active turn to complete; return the assistant's text.
        Reads the .events buffer that frame_reader fills."""
        agent = []
        seen = 0
        done = [False]
        deadline = time.time() + timeout
        while want_reply and time.time() < deadline and not done[0]:
            while seen < len(self.events):
                ev = self.events[seen]; seen += 1
                meth = ev.get("method")
                if meth == "item/agentMessage/delta":
                    agent.append(ev.get("params", {}).get("delta", ""))
                elif meth == "turn/completed":
                    done[0] = True
                elif meth == "error":
                    sys.stderr.write("server error: %s\n" % json.dumps(ev.get("params", {})))
            time.sleep(0.1)
        return "".join(agent).strip()

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass


def text_input(text):
    # text_elements is optional; omit it for cross-version compatibility.
    return [{"type": "text", "text": text}]


# --------------------------------------------------------------------------- #
# Subcommands
# --------------------------------------------------------------------------- #
def cmd_list(a, sess):
    params = {}
    if a.cwd:
        params["cwd"] = a.cwd
    if a.all_sources:
        # include exec/agent sessions, not just interactive ones
        params["sourceKinds"] = []
    if a.search:
        params["searchTerm"] = a.search
    if a.limit:
        params["limit"] = a.limit
    res = sess.call("thread/list", params)
    rows = res.get("data", res if isinstance(res, list) else [])
    for t in rows:
        st = (t.get("status") or {}).get("type", "?")
        name = t.get("name") or t.get("preview") or ""
        print(f"{t.get('id')}  [{st:7}]  src={t.get('source')}  cwd={t.get('cwd')}  {name[:60]}")
    print(f"\n# {len(rows)} threads  (status 'active' just means LOADED, not running — see troubleshooting.md)",
          file=sys.stderr)


def cmd_send(a, sess):
    sess.call("thread/resume", {"threadId": a.thread})
    sess.call("turn/start", {"threadId": a.thread, "input": text_input(a.text)})
    reply = sess.stream_turn(want_reply=not a.no_wait, timeout=a.timeout)
    if not a.no_wait:
        print(reply or "(no assistant text captured)")


def cmd_new(a, sess):
    params = {"cwd": a.cwd or os.getcwd()}
    if a.model:
        params["model"] = a.model
    if a.sandbox:
        params["sandbox"] = a.sandbox
    if a.approval:
        params["approvalPolicy"] = a.approval
    res = sess.call("thread/start", params)
    tid = (res.get("thread") or {}).get("id") or res.get("threadId")
    print(f"# new thread: {tid}", file=sys.stderr)
    print(tid)
    if a.text:
        sess.call("turn/start", {"threadId": tid, "input": text_input(a.text)})
        reply = sess.stream_turn(want_reply=not a.no_wait, timeout=a.timeout)
        if not a.no_wait:
            print(reply or "(no assistant text captured)")


def cmd_read(a, sess):
    res = sess.call("thread/read", {"threadId": a.thread, "includeTurns": True})
    print(json.dumps(res, indent=2)[: a.max_chars])


def cmd_watch(a, sess):
    # Resume to subscribe, then print events as they arrive (Ctrl-C to stop).
    sess.call("thread/resume", {"threadId": a.thread})
    print(f"# watching {a.thread} — Ctrl-C to stop", file=sys.stderr)
    seen = 0
    try:
        while True:
            while seen < len(sess.events):
                ev = sess.events[seen]; seen += 1
                m = ev.get("method", "")
                if m == "item/agentMessage/delta":
                    sys.stdout.write(ev["params"].get("delta", "")); sys.stdout.flush()
                elif m == "turn/completed":
                    print("\n--- turn/completed ---")
                elif m in ("turn/started", "item/started", "thread/status/changed"):
                    print(f"[{m}]")
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass


def cmd_interrupt(a, sess):
    sess.call("turn/interrupt", {"threadId": a.thread, "turnId": a.turn})
    print("interrupted")


# --------------------------------------------------------------------------- #
def main():
    p = argparse.ArgumentParser(description="Talk to a running Codex app-server over WebSocket.")
    p.add_argument("--sock", help="unix socket path (default: auto-discover desktop socket)")
    p.add_argument("--ws", help="ws://host:port (TCP transport instead of unix socket)")
    p.add_argument("--token", help="bearer token for authenticated ws:// (visible in argv; prefer --token-file)")
    p.add_argument("--token-file", help="file containing a bearer token")
    p.add_argument("--raw", action="store_true", help="print every raw JSON-RPC line received")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list"); s.add_argument("--cwd"); s.add_argument("--search")
    s.add_argument("--limit", type=int); s.add_argument("--all-sources", action="store_true",
        help="include exec/agent sessions (default: interactive only)")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("send"); s.add_argument("--thread", required=True)
    s.add_argument("-t", "--text", required=True); s.add_argument("--timeout", type=int, default=180)
    s.add_argument("--no-wait", action="store_true", help="fire the turn and exit without waiting")
    s.set_defaults(fn=cmd_send)

    s = sub.add_parser("new"); s.add_argument("--cwd"); s.add_argument("-m", "--model")
    s.add_argument("--sandbox", choices=["read-only", "workspace-write", "danger-full-access"])
    s.add_argument("--approval", choices=["untrusted", "on-failure", "on-request", "never"])
    s.add_argument("-t", "--text"); s.add_argument("--timeout", type=int, default=180)
    s.add_argument("--no-wait", action="store_true")
    s.set_defaults(fn=cmd_new)

    s = sub.add_parser("read"); s.add_argument("--thread", required=True)
    s.add_argument("--max-chars", type=int, default=20000); s.set_defaults(fn=cmd_read)

    s = sub.add_parser("watch"); s.add_argument("--thread", required=True); s.set_defaults(fn=cmd_watch)

    s = sub.add_parser("interrupt"); s.add_argument("--thread", required=True)
    s.add_argument("--turn", required=True); s.set_defaults(fn=cmd_interrupt)

    a = p.parse_args()
    token = a.token
    if a.token_file:
        token = open(a.token_file).read().strip()
    sock = a.sock or (None if a.ws else discover_sock())
    if not a.ws and not sock:
        sys.exit("No app-server socket found under ~/.codex/app-server-control/. "
                 "Is the desktop app / app-server running? Pass --sock or --ws.")
    sess = Session(sock_path=sock, ws_url=a.ws, token=token, raw=a.raw)
    try:
        sess.initialize()
        a.fn(a, sess)
    finally:
        sess.close()


if __name__ == "__main__":
    main()
