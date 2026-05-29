# Reflection Note

### 2026-05-29T09:25:11Z

## Observations

Third-party skill imports need a stricter boundary than first-party Klimkit skills: source attribution, license clarity, and prompt-injection review are part of the import itself, not optional polish.

## Derived Pattern

Mechanical import changes should stay limited to namespacing, metadata validity, self-contained resources, and upstream notes; workflow rewrites belong in a separate proposal so Klim can review the diff against originals.

## Insight

The blocked `roin-orca/simple` request is a useful precedent: Klimkit should prefer creating a clean original skill over redistributing unlicensed or adversarial skill text.

## Next Probe

Before making imported UI/design skills active defaults, audit bundled scripts and reconcile overlapping design guidance so `klimkit-impeccable`, `klimkit-ui-ux-pro-max`, `klimkit-web-design-guidelines`, and `klimkit-agent-browser` give a single coherent workflow.
