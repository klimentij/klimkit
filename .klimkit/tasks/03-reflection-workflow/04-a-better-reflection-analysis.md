# Better Reflection Format Analysis

## Context

Human task: `.klimkit/tasks/03-reflection-workflow/03-h-better-refrection.md`.

Current artifact reviewed: `.klimkit/reflection.md`, especially the first entry for
`2026-05-11 - 03-reflection-workflow`.

This note is analysis only. It proposes formats and rewrites, but does not change
the shared harness instructions yet.

## Short Take

The current reflection is valuable, but it is too long for an append-only file that
should stay useful after dozens of tasks. It correctly found a real process gap
and made a useful cross-task connection, but the format reads like an essay. That
makes it expensive to scan and easy for future entries to become proof summaries
instead of synthesis.

I would keep the file append-only, but make it more like a timestamped log than a
task-indexed report. The entry should not be "one record per task". It should be
one reflection session whenever the agent has enough evidence to connect multiple
tasks, logs, memories, current work, and recent failures into a higher-level
pattern. The filename can stay `.klimkit/reflection.md` for compatibility unless
Klim wants a migration later.

Recommended format: short, source-grounded, and explicitly split into facts,
connections, risks, and reconsideration. Detailed evidence belongs in task proof
notes; the ledger should capture what became newly obvious only after comparing
the current task with memory, log, and past tasks.

## What Worked In The Current Reflection

- It made a useful distinction between memory, log, and reflection:
  memory stores durable preferences, log stores actions, and reflection stores
  cross-task synthesis.
- It spotted a real workflow issue: the implementation proof note was missing or
  not obvious before final review.
- It connected the reflection workflow to a broader Klimkit pattern: the repo is
  building a proof-contract system around checklists, task notes, QA reports, and
  final reviewers.
- It correctly treats a fresh-context subagent as useful. The value comes from
  different context shape, not just another pass by the same parent agent.

## What Should Change

- The source-read summary is too heavy. A future reader usually needs source
  boundaries, not a full inventory of every file.
- "Non-Obvious Synthesis" is the core section, but it is buried under a lot of
  process narration.
- Risks and follow-ups are useful, but they should be sharper and more action-like.
- The format does not force the writer to separate evidence from inference.
- There is no explicit "reconsideration" field, even though the harness requires
  the parent agent to reconsider before final reviewers.

## Naming Options

| Name | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| Reflection | Familiar, already used, broad enough | Sounds soft and can invite diary-like writing | Keep as filename only |
| Synthesis Ledger | Says this is append-only and connective | Slightly formal | Recommended |
| Insight Ledger | Short and readable | "Insight" can become vague | Good alternative |
| Pattern Ledger | Pushes reusable patterns | Less good for task-specific contradictions | Good for stricter variant |
| Learning Ledger | Human and durable | Can drift into motivational prose | Maybe |
| Cross-Task Synthesis | Very explicit | Clunky as a repeated name | Good section title |
| Signals Ledger | Compact and analytical | Less obvious to new agents | Maybe for expert mode |
| Reflection Log | Simple, timestamped, task-independent | "Reflection" can still sound vague | Strong if sections are strict |

Recommendation: use "Synthesis Ledger" in agent instructions and UI/docs language,
while keeping `.klimkit/reflection.md` unless a migration is worth it.

## Success Criteria For A Better Format

- It captures non-obvious connections, not chronology.
- It is append-only and still useful after many entries.
- It is grounded in named sources without duplicating the proof note.
- It separates fact, inference, risk, and action.
- It produces a reconsideration result before final reviewers.
- It is bounded enough that a subagent can generate it consistently.

## Format Approaches

### 1. Current Essay Reflection

Shape:

```markdown
Task Reference
Source-Read Summary
Non-Obvious Synthesis
Risks Or Contradictions
Candidate Memory/Log/Task Follow-Ups
```

Pros:

- Good for first adoption because it gives the writer room to think.
- Captures nuance and source boundaries.
- Easy to write when the task is complex.

Cons:

- Too long for a ledger.
- Repeats task proof content.
- Hard to scan across many entries.
- Does not force fact versus inference separation.

Best use: temporary exploratory format while the reflection practice is still
being designed.

### 2. Compressed Synthesis Ledger

Shape:

```markdown
Signal
Sources
Connections
Risks / Contradictions
Follow-Ups
Reconsideration
```

Pros:

- Compact and readable.
- Preserves the most valuable parts of the current format.
- Easy to require before final reviewers.
- Keeps detailed evidence in task notes.

Cons:

- May still become generic if "connections" is not enforced as the core section.
- Needs a soft word budget or bullet limit.

Best use: default harness format.

Recommended constraint: 300-500 words, 2-4 connection bullets, 1-3 risks, 1-3
follow-ups.

### 3. Fact / Inference / Bet Format

Shape:

```markdown
Facts
Inferences
Bets
Risks
Actions
```

Pros:

- Very clear epistemic hygiene.
- Makes unsupported claims obvious.
- Good for tasks where the agent might overfit to a story.

Cons:

- Slightly clinical.
- Can under-emphasize novel cross-task connections unless "Inferences" is written well.

Best use: high-risk workflow, architecture, release, or policy changes.

### 4. Connection Graph Format

Shape:

```markdown
Nodes
Edges
New Connection
Contradiction
Next Probe
```

Pros:

- Best at the user's stated goal: finding unobvious connections.
- Compact when written well.
- Forces relationship thinking instead of summary writing.

Cons:

- Less natural for simple tasks.
- Some agents may produce decorative graph language without useful conclusions.

Best use: periodic repo-wide synthesis, not every implementation task.

### 5. Decision-Delta Format

Shape:

```markdown
Before Reflection
After Reflection
Changed Work
Changed Final Response
Remaining Risk
```

Pros:

- Directly matches the pre-final-review gate.
- Makes "did reflection matter?" visible.
- Prevents reflection from becoming detached from the actual task.

Cons:

- Less useful as long-term memory unless it also records the pattern discovered.

Best use: final pre-review reflection note for implementation work.

### 6. Pattern Cards

Shape:

```markdown
Pattern
Context
Observed In
Why It Matters
Anti-Pattern
Next Experiment
```

Pros:

- Excellent for reusable learning.
- Scans well across months.
- Turns repeated task noise into named patterns.

Cons:

- Too abstract if every task forces a pattern.
- Can miss one-off risks and contradictions.

Best use: when a reflection discovers a reusable operating principle.

### 7. Two-Tier Format

Shape:

```markdown
.klimkit/reflection.md
  Short synthesis ledger entry

.klimkit/tasks/<feature>/<nn>-a-reflection-deep-note.md
  Optional detailed source read, excerpts, and reasoning
```

Pros:

- Keeps the global ledger clean.
- Still allows deep reflection when needed.
- Matches the existing split between proof notes and durable memory.

Cons:

- More files.
- Needs clear rule for when the deep note is worth it.

Best use: recommended if Klim wants creativity and novelty without making the
global file unreadable.

### 8. Timestamped Cross-Task Reflection Log

Shape:

```markdown
### 2026-05-14T09:55:00Z

**Observations:** One sentence with grounded signals across current work, task history, log, memory, and recent artifacts.
**Derived Pattern:** One sentence naming the reusable pattern or pressure.
**Insight:** One sentence stating the non-obvious connection, bet, or reframing.
**Next Probe:** One sentence with the next thing to test, watch, or encode.
```

Pros:

- Matches the user's desire for a log-like, task-independent reflection file.
- Full timestamps make it naturally append-only and chronological.
- The entry is higher-level than a task proof note.
- The fixed four-line shape limits drift and keeps scanning cheap.
- It can still reference tasks when useful without being organized by task.

Cons:

- A very compressed format can hide source boundaries unless the observation
  sentence is disciplined.
- Some complex synthesis may need an optional task-local deep note.

Best use: default global reflection format.

Recommended rule: one reflection session may mention multiple tasks and should
only be written when there is a cross-task observation, not merely because a task
finished.

Optional stricter variant:

```markdown
### 2026-05-14T09:55:00Z

**Observed:** ...
**Pattern:** ...
**Insight:** ...
**Probe:** ...
```

Optional more analytical variant:

```markdown
### 2026-05-14T09:55:00Z

**Signals:** ...
**Pattern:** ...
**Tension:** ...
**Bet:** ...
```

For Klimkit, I prefer the four-label version:

```markdown
**Observations**
**Derived Pattern**
**Insight**
**Next Probe**
```

It is plain enough that agents will follow it, but it still pushes them beyond
summary into synthesis.

## Recommended Standard

Use a two-tier system with a timestamped global reflection log:

- `.klimkit/reflection.md` is an append-only, timestamped cross-task reflection log.
- Entries are reflection sessions, not task records.
- Most entries are four short lines.
- If a task needs deeper thinking, write the deep version in the task folder and
  link it from the ledger.
- The parent agent must read the ledger entry and record whether it changed the
  implementation, proof, or final response before starting final reviewers.

Recommended ledger template:

```markdown
### YYYY-MM-DDTHH:MM:SSZ

**Observations:** One sentence with concrete cross-task signals.
**Derived Pattern:** One sentence naming the reusable pattern.
**Insight:** One sentence with the non-obvious connection or reframing.
**Next Probe:** One sentence with the next thing to test, watch, or encode.
```

Ultra-compact variant for small tasks:

```markdown
### YYYY-MM-DDTHH:MM:SSZ

**Observed:** ...
**Pattern:** ...
**Insight:** ...
**Probe:** ...
```

## Rewritten Current Reflection: Version A, Very Compressed

```markdown
### 2026-05-11 - 03-reflection-workflow

**Signal:** Reflection is becoming the missing layer between task proof and final review: it captures cross-task learning that memory, log, and proof notes do not.

**Sources:** Current reflection-workflow task, memory/log, Klimkipedia reflection pattern, representative tasks from `01-tui-ux-multi-harness-more` and `02-better-wf-and-tabs`, and the pack changes. Binary screenshots were noted as evidence, not read as text.

**Connections:** Klimkit has been converging on a proof-contract pipeline: task notes -> checklists -> proof reports -> final reviewers -> synthesis. Memory stores durable rules; log records actions; reflection stores patterns and contradictions. A fresh-context reflector is useful because synthesis quality depends on context shape, not just more parent-agent attention.

**Risks / Contradictions:** Reflection can become proof slop if it repeats evidence instead of extracting connections. The task also needed a clear proof note before final reviewers.

**Follow-Ups:** Keep the ledger short, append-only, and source-grounded. Put detailed validation in task proof. Require explicit reconsideration before final reviewers.

**Reconsideration:** Add or verify implementation proof before final review.
```

## Rewritten Current Reflection: Version B, Fact Based

```markdown
### 2026-05-11 - 03-reflection-workflow

**Facts**
- Klimkipedia already uses a reflection file to capture synthesis separate from memory and log.
- Klimkit already uses task notes, acceptance checklists, proof artifacts, browser QA, and final reviewers.
- The proposed harness change places reflection after verification and before final reviewers.
- The new `reflector` agent is intended to read current task context plus wider `.klimkit/tasks/` history.

**Inferences**
- Reflection is valuable only if it records patterns and contradictions that are not already present in proof notes.
- Fresh-context synthesis reduces the chance that a long parent-agent session misses process gaps.
- The strongest existing Klimkit pattern is a proof-contract spine: each workflow stage reduces ambiguity before the next one.

**Risks**
- Long reflections will become unreadable and duplicate proof.
- A reflector without an explicit reconsideration field may produce an artifact that does not affect the final result.

**Actions**
- Keep `.klimkit/reflection.md` append-only and concise.
- Record detailed validation in task proof notes.
- Before final reviewers, state whether reflection changed the implementation, proof, or final response.
```

## Rewritten Current Reflection: Version C, Connection Graph

```markdown
### 2026-05-11 - 03-reflection-workflow

**Nodes**
- Memory: durable preferences and rules.
- Log: timestamped actions.
- Task notes: scoped plans, checklists, proof, and QA evidence.
- Final reviewers: independent completion gate.
- Reflection: cross-task synthesis and contradiction capture.

**Edges**
- Memory -> Checklists: durable rules become blocking acceptance criteria.
- Log -> Proof: action history helps validate what was actually changed.
- Task proof -> Final reviewers: reviewers receive evidence instead of trust.
- Reflection -> Final reviewers: synthesis catches gaps before the final claim.
- Past tasks -> Current task: repeated workflow pain becomes a pack-level rule.

**New Connection**
The reflection step is not another review. It is the only step optimized for discovering relationships between tasks after implementation has created new evidence.

**Contradiction**
The current reflection format is long enough that it may weaken the ledger it is meant to improve.

**Next Probe**
Try a shorter Synthesis Ledger entry plus optional deep task-local reflection notes.
```

## Rewritten Current Reflection: Version D, Decision Delta

```markdown
### 2026-05-11 - 03-reflection-workflow

**Before Reflection**
The change looked like a straightforward harness addition: add a `reflector` agent, require it before final reviewers, and update pack validation.

**After Reflection**
The change is better understood as another layer in Klimkit's proof-contract system. The important behavior is not the extra file. It is forcing a fresh-context synthesis pass that compares the current task with memory, log, and previous task history.

**Changed Work**
The task should include clear proof that the reflection gate was implemented, projected, and validated. The proof note matters because the reflection itself identified that gap.

**Changed Final Response**
The final response should mention the reflection gate as a reconsideration step, not just as a new agent.

**Remaining Risk**
If entries remain essay-length, the ledger will stop being useful after a few tasks.
```

## Rewritten Current Reflection: Version E, Pattern Card

```markdown
### 2026-05-11 - Pattern: Proof Contract Spine

**Context**
Klimkit keeps adding mechanisms that convert vague completion claims into reviewable evidence.

**Observed In**
Memory/log files, task checklists, browser proof reports, final reviewers, release proof notes, and now the reflection workflow.

**Pattern**
Each stage should reduce ambiguity for the next stage:
task request -> checklist -> implementation -> proof -> synthesis -> final reviewers -> user report.

**Why It Matters**
Long agent sessions lose global shape. A short synthesis ledger preserves non-obvious connections and contradictions without turning them into permanent preferences.

**Anti-Pattern**
Reflection as a long proof recap. That duplicates evidence and makes the global file hard to scan.

**Next Experiment**
Use a concise Synthesis Ledger entry by default, with optional task-local deep notes only when the task produces a genuinely reusable pattern.
```

## Rewritten Current Reflection: Version F, Timestamped Cross-Task Log

```markdown
### 2026-05-11T10:32:51Z

**Observations:** Across Klimkit tasks, memory/log, proof reports, final reviewers, and the Klimkipedia source pattern, the repo is repeatedly converting vague agent completion claims into reviewable artifacts.
**Derived Pattern:** The emerging system is a proof-contract pipeline: checklist -> implementation -> verification -> proof -> synthesis -> final review -> user report.
**Insight:** Reflection should not be a task recap; it should be the task-independent step that notices when multiple artifacts imply a reusable pattern, contradiction, or missing gate.
**Next Probe:** Keep the global ledger to four timestamped lines per session, and move detailed source inventories or evidence into task-local notes.
```

Even more compressed:

```markdown
### 2026-05-11T10:32:51Z

**Observed:** Klimkit keeps adding artifacts that make agent claims independently checkable across tasks.
**Pattern:** Checklist, proof, reflection, and final review are one proof-contract pipeline.
**Insight:** Reflection is valuable only when it extracts cross-task synthesis, not when it repeats task evidence.
**Probe:** Use four timestamped lines globally; put details in task notes.
```

## Final Recommendation

Adopt the **Timestamped Cross-Task Reflection Log** as the default and allow
optional task-local deep notes when a reflection session needs more evidence.

Best default entry:

```markdown
### YYYY-MM-DDTHH:MM:SSZ

**Observations:** ...
**Derived Pattern:** ...
**Insight:** ...
**Next Probe:** ...
```

Best file policy:

- Keep `.klimkit/reflection.md` as the append-only ledger.
- Call the practice "Reflection Log" or "Synthesis Ledger" in pack docs and agent prompts.
- Use full timestamps, not task titles, as the primary entry key.
- Do not require one entry per task.
- Write an entry only when there is a higher-level cross-task signal.
- Keep global entries to four short sections by default.
- Put long source inventories and detailed evidence in task-local proof notes.
- Require the parent agent to state what changed after reading the ledger entry.

---

Klim: Great, I like this. I want you to update the related subagents and workflow instructions in Skills Agent MD or wherever it's mentioned. And the agent, of course, if the agent sees the older versions of reflection, it should redo it to the newer version of reflection. I mean, the newer format. And also, um, maybe keep a list of default sections like observations, derived pattern, and so on, but maybe keep three or four of them required and maybe up to ten sections when needed. Maybe some reflections are wider, some of them are deeper, some of them are more creative, and so on. I don't want an idea to be cut off just because there is a missing section of a reflection session. Go do it and let me know when all the files are updated so I can review the new hardness pack. 