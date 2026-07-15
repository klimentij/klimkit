# docs/work — how features actually got made

Most of the thinking behind a feature — the original ask, the requirements someone spelled
out in chat, the dead ends, the review findings, the run results — normally evaporates
into chat histories and private notes. This folder keeps it. Each piece of work gets one
folder that reads like a story: what the human asked, what the agent did, what they decided
together, and why. Anyone (human or agent) can open a work folder months later and follow
the exact trajectory that produced the code — or dive into just one phase of it when
debugging, reviewing, or designing something similar.

The folder names double as a simple semantic index: numbers give order, dates give time,
slugs say what happened. Skimming the tree *is* discovering the history.

```
docs/work/
└── 042-140126-rate-limiter/            # one piece of work; number-date-slug
    ├── LOG.md                          # start here: one entry per phase, links down
    ├── 001-140126-proposal/            # a phase = one logical human+agent iteration
    │   ├── LOG.md                      #   what happened here: timestamped entries with a
    │   │                               #   one-liner, who drove (human / joint / agent-only),
    │   │                               #   and links to the exact files
    │   └── 001-original-ask-chat-thread.md       # artifacts: plain numbered files
    ├── 002-150126-research-and-grilling/
    ├── 003-180126-pr-build/
    └── 004-200126-critical-review/
        ├── LOG.md
        ├── 001-review-prompts.md       # the human's messages, verbatim — the most
        │                               #   valuable artifact of all
        ├── 002-gap-analysis.md
        └── 003-explainer.html          # reports are self-contained single-file HTMLs,
                                        #   numbered like any other artifact
```

**How it works day to day.** Notes are written live, while the work happens — the agent
records each human message verbatim into a fitting note and logs every meaningful beat in
the phase `LOG.md`. There is no after-the-fact transcript parsing; the notes *are* the
record. A new logical iteration (design, grilling, build, review…) opens a new phase
folder; a few short related turns share one.

**What stays out.** Raw transcripts, build artifacts, regenerable renders, and asset
folders never enter git — distilled prose, verbatim human prompts, and self-contained
HTMLs only (soft budget ≈300 KB per work folder). Screenshots are tracked only when they
are irreproducible evidence.

**Heavier artifacts — three tiers.** Default: one self-contained file. If an artifact
genuinely can't be one file, make it a numbered folder (`007-proof-bundle/` with an
`index.html` or `README.md` entry point) — unambiguous inside a phase, budget still
applies. Everything heavy and moment-useful but audit-irrelevant (screen recordings,
large images, exports, HTML-with-dependencies) goes in a `.local/` folder — gitignored,
machine-local, allowed to vanish. Notes may point into `.local/`, but must stay
comprehensible without it; if something heavy matters beyond the moment, link where it
lives externally instead of committing it.

**Viewing for the human driver.** HTML artifacts are not just files: by default the agent
also deploys them through its harness's native hosted surface — the Claude Code Artifact
tool or Codex Sites — which are authentication-protected (private to the author or
workspace-only). Never enable public link sharing unless the human explicitly asks. The
deployed URL goes in the phase `LOG.md` next to the file link; the git-tracked HTML stays
the source of truth.

**Where things graduate.** Decisions become ADRs, durable research goes to
`docs/research/`, final reports to `docs/reports/` — the work folder is the workshop and
stays behind as history. If you're reading to learn: open the work `LOG.md`, pick a phase,
and only then open files. Don't bulk-read the tree; it's built so you never have to.

**Always two layers.** Artifacts never sit directly in a work folder: a work folder
contains only its `LOG.md` and phase folders, and files live inside phases. Even a
single-sitting piece of work gets one phase folder — a flat work folder goes wide and
unreadable as artifacts accumulate. (Folders migrated from an earlier layout carry a
migration note in their `LOG.md`; authorship recovered from the old file names lives in
the phase LOGs.)
