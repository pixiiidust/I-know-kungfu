# Pixoid: Handoff — I-know-kungfu PRD + Domain Model Refinement

Date: 2026-06-19
Repo: `/root/hermes-workspace/I-know-kungfu`
Status: Variant C prototype accepted as initial smell-test direction; PRD/README/prototype committed and pushed.

## Current durable state

Latest pushed repo commit at handoff time:

```text
5883b251d0c697a6e618752aaf4467c9d8a92d2c
```

GitHub issue:

```text
https://github.com/pixiiidust/I-know-kungfu/issues/1
```

Main artifacts:

```text
README.md
CONTEXT.md
docs/PRD.md
docs/research/2026-06-19-brainstorm.md
docs/handoff/2026-06-19-cookbook-serving-prototype-handoff.md
prototype/cookbook-serving/index.html
prototype/cookbook-serving/NOTES.md
```

## Accepted prototype direction

Jamie said Variant C passes the initial smell test for now.

Variant C sequence:

```text
Find useful wiki / pack
→ check local fit
→ choose serving surface
→ harmonize overlap
→ inspect scope / proof / refusal
```

Product frame to preserve:

> Find useful wikis to add to your knowledge base, compare local fit, serve through the right surface, and harmonize diffs when overlap exists.

Do not reframe it as a Loop Library/prompt-library product. The Forward Future Loop Library reference was visual/community-listing pattern only.

## Next-session goal

Use `/domain-modeling` and `/codebase-design` to improve:

```text
CONTEXT.md
docs/PRD.md
```

Primary work:

1. Sharpen the ubiquitous language in `CONTEXT.md`.
2. Remove duplicates/overlaps in glossary terms.
3. Check whether the PRD uses the glossary consistently.
4. Improve the PRD’s implementation decisions using deep-module language:
   - Module
   - Interface
   - Seam
   - Adapter
   - Depth
   - Locality
   - Leverage
5. Clarify the highest useful seams for the first build slice, without over-designing the hosted marketplace.
6. Keep the first slice local-first and endpoint-ready.

Potential follow-up:

- Run another `/grill-with-docs` session after domain model + codebase design pass to pressure-test what remains unclear.

## Suggested skills

Load:

- `domain-modeling`
- `codebase-design`
- `grill-with-docs` only after the first pass if Jamie asks to pressure-test
- `github-operations` if committing/pushing

Optional if touching product copy:

- `verb-first`

## Important boundaries

Do not build backend/auth/payments/public upload/real marketplace/vector DB/hosted RAG/cloud MCP in this pass.

Do not expand beyond PRD/context improvement unless Jamie asks.

Do not rewrite the accepted prototype direction unless a concrete contradiction appears.

## Vault / Pixi Wiki state

This project has been added as a new project under the `ai-native-product-surfaces` namespace in Pixi Wiki.

Relevant vault/public handles:

```text
/root/ObsidianVault/Projects/I-know-kungfu/Index.md
/root/ObsidianVault/wikis/ai-native-product-surfaces/wiki/entities/i-know-kungfu.md
https://pixiiidust.github.io/pixi-wiki/wiki/ai-native-product-surfaces/wiki/entities/i-know-kungfu.md.html
```

## Short handoff prompt

```text
Pixoid: Continue I-know-kungfu PRD/domain refinement.
Repo: /root/hermes-workspace/I-know-kungfu
First read: docs/handoff/2026-06-19-prd-context-modeling-handoff.md
Then inspect live state. Use /domain-modeling + /codebase-design to improve CONTEXT.md and docs/PRD.md. Keep Variant C as accepted prototype direction. After that, we may run /grill-with-docs on the revised docs.
```
