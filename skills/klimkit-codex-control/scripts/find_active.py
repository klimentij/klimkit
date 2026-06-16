#!/usr/bin/env python3
"""
find_active.py — find Codex sessions that are GENUINELY doing work right now.

Why this exists: the app-server's thread/list reports a thread as `active` when
it is merely *loaded in memory*, not when it is actually running a turn. And
`codex exec` agents (source=exec) don't appear in thread/list at all because it
defaults to interactive sources. So the only reliable ground truth for "what is
working right now" is: running `codex exec` processes + rollout files being
written this minute. This script reports both.

Usage:
  python find_active.py [--minutes 5] [--home ~/.codex]
"""
import argparse, datetime, glob, json, os, subprocess


def recent_rollouts(home, minutes):
    base = os.path.join(home, "sessions")
    cutoff = None
    out = []
    for f in glob.glob(os.path.join(base, "**", "*.jsonl"), recursive=True):
        try:
            mt = os.path.getmtime(f)
        except OSError:
            continue
        age_min = (datetime.datetime.now().timestamp() - mt) / 60.0
        if age_min <= minutes:
            out.append((mt, f))
    out.sort()
    return out


def summarize(f):
    meta = {}
    last_user = last_agent = None
    n_agent = 0
    try:
        for line in open(f):
            try:
                d = json.loads(line)
            except Exception:
                continue
            p = d.get("payload", {})
            if d.get("type") == "session_meta":
                meta = p
            elif d.get("type") == "event_msg":
                if p.get("type") == "user_message":
                    last_user = p.get("message", "")
                elif p.get("type") == "agent_message":
                    last_agent = p.get("message", ""); n_agent += 1
    except OSError:
        pass
    return meta, last_user, last_agent, n_agent


def running_exec():
    try:
        out = subprocess.run(["ps", "-eo", "pid,pcpu,etime,cmd"],
                             capture_output=True, text=True).stdout
    except Exception:
        return []
    rows = []
    for line in out.splitlines():
        if " codex " in line and (" exec " in line or "/codex exec" in line) and "grep" not in line:
            rows.append(line.strip())
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=float, default=5)
    ap.add_argument("--home", default=os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex")))
    a = ap.parse_args()

    print(f"== rollouts written in the last {a.minutes:g} min (genuinely active) ==")
    rows = recent_rollouts(a.home, a.minutes)
    if not rows:
        print("  (none)")
    for mt, f in rows:
        meta, lu, la, n = summarize(f)
        when = datetime.datetime.fromtimestamp(mt).strftime("%H:%M:%S")
        sid = os.path.basename(f)
        print(f"\n- {sid[:50]}  (mod {when})")
        print(f"    cwd={meta.get('cwd')}  cli={meta.get('cli_version')}  agent_msgs={n}")
        if lu:
            print(f"    last_user : {lu[:100]}")
        if la:
            print(f"    last_agent: {la[:100]}")

    print("\n== running `codex exec` processes (CPU work in progress) ==")
    procs = running_exec()
    if not procs:
        print("  (none)")
    for line in procs:
        print("  " + line[:200])


if __name__ == "__main__":
    main()
