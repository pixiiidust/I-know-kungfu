# Knowledge Pack Routing

**Knowledge Pack Routing** is Jamie's markdown-first pattern for telling agents where durable truth lives before they start work.

It does not try to put every fact into one file. A pack is a map to truth: it states scope, freshness, source paths, fallback rules, and ownership so the agent can route itself to GitHub issues, Obsidian notes, skills, session search, or live tools.

## Why it exists

Without routing, agents waste context on archaeology, treat stale notes as current, or build infrastructure before proving retrieval failure. KPR makes the first step explicit: load the right compact contract, then follow canonical source links.

## Operating rule

A useful pack answers five questions quickly:

- What does this pack cover?
- What does it explicitly not cover?
- How fresh is it?
- Where are the canonical source paths?
- What should the agent do if the answer is missing, stale, or out of scope?

## Product judgment

KPR deliberately keeps MCP/RAG/search deferred until a concrete eval shows markdown routing cannot answer important questions. That turns retrieval infrastructure into a response to evidence, not a default reflex.

## Related pages

- [[agent-entrypoint-mesh]]
- [[static-retrieval-evals]]
- [[runtime-memory-knowledge-routing]]
- [[../entities/hermes-mission-control|Hermes Mission Control]]