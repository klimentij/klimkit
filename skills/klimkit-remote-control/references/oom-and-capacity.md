# Why agent hosts die: OOM, and how to size against it

The failure this skill exists to prevent, written from a real post-mortem. Read this before
choosing `--capacity` or telling anyone the setup is durable.

## The incident

A VM with **6 cores, 11 GB RAM and zero swap** ran a research fleet of 13 agents, launched
with `nohup` from a `tmux` pane, alongside an interactive Claude session and several Docker
stacks (two Postgres instances and a PyTorch inference container). Roughly ten minutes in:

```
kernel: tokio-rt-worker invoked oom-killer: ... global_oom
kernel: Out of memory: Killed process 3121330 (dbus-daemon) ... oom_score_adj:200
kernel: Out of memory: Killed process 1167 (systemd) ... oom_score_adj:100
        task_memcg=/user.slice/user-1000.slice/user@1000.service/init.scope
```

The kernel did not kill the fleet. It killed **`user@1000.service`'s own systemd manager**
and dbus. That tore down the entire user slice: tmux, every `nohup`ed fleet member, and the
Remote Control session. Ten agents died mid-work having written nothing. The user manager
came back seven minutes later, on demand, with nothing enabled.

## Why the supervisor was chosen as the victim

systemd sets `OOMScoreAdjust=100` on the per-user manager deliberately, so that user
sessions are sacrificed before system services. Disposable fleet processes ran at the
default `0`. The scoring was therefore exactly inverted against intent: the work that
mattered least was the least likely to be killed.

Three consequences that shape the design:

1. **`Restart=always` on a `--user` unit is a promise the supervisor cannot keep.** It
   cannot restart anything if it is the process being killed. Prefer a system unit under
   PID 1, which cannot be OOM-killed.
2. **What survived was PID 1 supervised.** A `cron` job on the same box kept running
   throughout, because `cron` answers to PID 1, not to the user manager. That contrast is
   the cleanest available proof of the mechanism.
3. **Zero swap converts a spike into a kill.** With swap the kernel reclaims and the box
   goes slow; without it, the OOM killer is the only lever available.

## Diagnosing it on any machine

Do this before believing any other theory of why sessions died:

```bash
journalctl -k --since "7 days ago" | grep -iE "invoked oom-killer|Out of memory: Killed"
```

Read three things from a hit: the `task_memcg=` path names the cgroup that was charged, so
`user@<uid>.service` means the user session tree died; `oom_score_adj:` shows why that
victim was picked; and `constraint=CONSTRAINT_NONE ... global_oom` means the whole machine
ran out, not one cgroup's limit.

Rank the consumers at the moment of the kill from the process table the kernel dumps:

```bash
journalctl -k --since "<time of kill>" --until "<+2min>" \
  | sed -n 's/.*kernel: \[\s*[0-9]\+\]\s\+[0-9]\+\s\+[0-9]\+\s\+[0-9]\+\s\+\([0-9]\+\)\s\+.*\s\([a-zA-Z0-9._:-]\+\)$/\1 \2/p' \
  | sort -rn | head -20 | awk '{printf "%8.1f MB  %s\n", $1*4/1024, $2}'
```

The RSS column is in pages; multiply by 4 KB. If the total is near physical RAM and swap is
zero, the diagnosis is complete — no network theory needed.

The distinguishing signature versus a network timeout: an OOM kills **several unrelated
processes at the same second**, including things that have nothing to do with Claude. A
network timeout exits one process cleanly, roughly ten idle minutes after connectivity
fails, and leaves everything else alive.

## The three defences

### Swap

Any is better than none. 8 GB on an 11 GB box is a reasonable default; `vm.swappiness=10`
keeps it as a safety margin rather than a routine path. Persist it in `/etc/fstab` or it
silently disappears at the next reboot, restoring the original defect.

### One capped parent slice

Put every remote-control instance under a shared slice and bound the **slice**:

```ini
[Slice]
MemoryHigh=6G
MemoryMax=8G
```

`MemoryHigh` throttles and reclaims; `MemoryMax` is the hard wall. With several instances,
a per-instance cap does not bound the machine — it only decides which instance dies first.
Pair it with `OOMPolicy=continue` on the service so that a killed session does not take the
server down with it.

Size the cap so that everything else — Docker, databases, the OS — still fits in what
remains. Total RAM minus resident non-agent workload, then leave headroom.

### Fleets as the preferred victim

Disposable work should be the first thing killed, which is the exact inversion of the
default. Give fleet processes `oom_score_adj=800` and their own capped slice; the installer
ships a `fleet-run` wrapper that does both. Unprivileged processes may always raise their
own score, so even without root, `choom -n 800 -- <cmd>` fixes the victim ordering.

Never `nohup` a fleet from a terminal multiplexer and walk away. That combination is what
turned a recoverable memory spike into a total session loss: the fleet was invisible to any
supervisor and outranked the supervisor for survival.

## Choosing `--capacity`

The flag is a **ceiling, not a reservation** — sessions cost memory only once spawned, so a
high ceiling is not itself dangerous, and the slice cap is what actually protects the box.
But a ceiling you cannot serve is a trap for whoever hits it.

Rough sizing: assume 0.5–1.5 GB per active session under real work. Start from the memory
you are willing to give all agents, divide, and treat the result as the honest concurrent
capacity even if you set the ceiling higher for convenience. On an 11 GB box already
running Docker stacks, that honest number is single digits.

Say both numbers in the handoff — permitted ceiling and expected working set — so nobody
reads `--capacity 64` as a promise of 64 concurrent agents.

Disk is the second ceiling with `--spawn worktree`: one checkout per session.
