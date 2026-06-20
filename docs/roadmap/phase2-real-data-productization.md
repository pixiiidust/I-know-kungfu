# Phase 2: Real-data Cookbook productization

Status: active local/static productization phase.

Phase 2 moves I-know-kungfu from a convincing static UI/CLI smell test to a
real-data local proof. The frontier is not the hosted marketplace. The frontier
is: can real packaged wikis generate the Cookbook registry, render in the chosen
UI surface, and run the local inspect → fit → install/serve → cite/refuse path?

## Phase 2 proves

- Two real example knowledge base wikis can be packaged from source docs.
- Each package exposes a concrete contract: scope, non-scope, provenance,
  freshness, trust/publication posture, and entry points.
- Generated static Cookbook registry data can be exported from those package
  artifacts instead of being hand-maintained inside the prototype UI.
- The Cookbook UI consumes generated registry data through the chosen Variant A
  surface.
- A local command can demonstrate the real-data path end to end:

```text
inspect real package
→ fit check against local inventory
→ export generated registry
→ install/route into a local store
→ serve/search/read installed sources
→ produce a cited answer
→ refuse an out-of-scope query
```

Run it with:

```bash
python scripts/phase2_real_data_demo.py
```

Detailed walkthrough: [`docs/demo/phase2-real-data-cookbook.md`](../demo/phase2-real-data-cookbook.md)

## UI surface decision

Variant A is the chosen surface for this phase.

Older references to Variant C describe the historical smell-test direction from
the pre-Phase-2 prototype. They should not be treated as instructions to restore
the A/B/C switcher or rebuild alternate surfaces.

## Deferred until a later phase

Do not build these in Phase 2 unless Jamie explicitly opens a new scope:

- hosted marketplace backend
- publisher accounts or auth
- public uploads
- payments or monetization
- public upload moderation
- official ownership/claim workflows
- hosted registry write APIs
- vector database retrieval or hosted RAG
- cloud MCP hosting
- browser extension
- automatic third-party wiki trust

Keep the seams endpoint-ready, but keep implementation local/static.

## Issue sequence

Parent:

- [#11 — Phase 2: Real-data Cookbook productization](https://github.com/pixiiidust/I-know-kungfu/issues/11)

Children:

- [#12 — Package the first real knowledge base wiki from existing source docs](https://github.com/pixiiidust/I-know-kungfu/issues/12)
- [#13 — Package a second real wiki to exercise trust and fit differences](https://github.com/pixiiidust/I-know-kungfu/issues/13)
- [#14 — Export static Cookbook registry data from real wiki contracts](https://github.com/pixiiidust/I-know-kungfu/issues/14)
- [#15 — Wire the Variant A Cookbook UI to generated registry data](https://github.com/pixiiidust/I-know-kungfu/issues/15)
- [#16 — Add a real-data end-to-end demo walkthrough](https://github.com/pixiiidust/I-know-kungfu/issues/16)
- [#17 — Document Phase 2 boundaries and deferred backend work](https://github.com/pixiiidust/I-know-kungfu/issues/17)
