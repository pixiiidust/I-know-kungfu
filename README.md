# I-know-kungfu

Status: early product exploration. This README is intentionally simple and subject to change as the repo evolves.

I-know-kungfu explores how to grow and evolve a user's own knowledge base by importing, adapting, and serving agent-readable knowledge base wikis instead of starting from scratch or relying on noisy web search.

## One-line pitch

Grow your knowledge base with proven wikis your agents can actually use.

## Current product frame

Find useful knowledge base wikis, compare them against what you already know, harmonize overlap, then serve bounded wiki sources to agents through the right entry point.

## Bigger picture

I-know-kungfu is working toward a local-first knowledge distribution system: people and teams can package trusted docs as bounded knowledge base wikis, agents can consume those wikis through standard entry points, and high-quality wikis can later become discoverable, verifiable, and monetizable through a Cookbook/registry.

The current MVP is the first slice of that larger system: prove the trust-to-serve loop locally before adding hosted marketplace, publisher, or monetization mechanics.

## Core idea

A knowledge base wiki is a bounded, source-backed knowledge surface. Each imported wiki should expose enough structure for humans and agents to answer:

- What does this wiki cover?
- What is explicitly out of scope?
- Where did the source material come from?
- How fresh or trustworthy is it?
- Which entry points can an agent use: MCP, `llms.txt`, raw Markdown, or `index.json`?
- When should an agent cite, refuse, or route to another source?

A **Knowledge Pack** is the portable packaging/install format for a knowledge base wiki. The wiki is the conceptual object users grow and serve; the pack is how that wiki moves between local storage, Cookbook listings, and agent harnesses.

## Current MVP direction

The first slice is a local-first Cookbook serving flow, not a hosted marketplace.

The target flow is:

```text
Find useful knowledge base wiki
→ check local fit
→ choose serving entry point
→ harmonize overlap
→ inspect scope / proof / refusal
```

The MVP should prove that a user can inspect a small static registry of knowledge base wikis, compare a candidate wiki against local knowledge, install or route it locally, serve it through agent-readable entry points, and see grounded agent behavior with citations and out-of-scope refusal.

## Repository structure

```text
CONTEXT.md
  Project glossary and domain terms.

docs/PRD.md
  Current PRD for the Cookbook Serving MVP.

docs/adr/
  Lightweight product/domain architecture decisions.

docs/research/
  Early brainstorm and product research notes.

docs/handoff/
  Session handoffs and implementation notes.

prototype/cookbook-serving/
  Throwaway static UI prototype for the Cookbook serving flow.
```

## Prototype

A static UI smell-test currently lives in:

```text
prototype/cookbook-serving/
```

Run it from the repo root:

```bash
python3 -m http.server 4173 --directory prototype/cookbook-serving
```

Then open:

```text
http://127.0.0.1:4173/
```

Available variants:

```text
http://127.0.0.1:4173/?variant=A
http://127.0.0.1:4173/?variant=B
http://127.0.0.1:4173/?variant=C
```

Variant C is the currently preferred direction.

## Local-first principle

Nothing should leave the user's machine unless they explicitly choose to publish, upload, or share a knowledge base wiki. Scanning, compiling, inspecting, installing, and serving should work locally first.

## Not in scope yet

- Hosted marketplace backend
- Accounts or payments
- Public upload moderation
- Hosted RAG or vector database retrieval
- Cloud MCP hosting
- Browser extension
- Automatic third-party wiki trust

## Useful docs

Start here:

- `CONTEXT.md` for shared vocabulary
- `docs/PRD.md` for the current MVP requirements
- `docs/adr/0001-knowledge-base-wiki-is-core-object.md` for the vocabulary decision
- `prototype/cookbook-serving/NOTES.md` for prototype status and run notes
