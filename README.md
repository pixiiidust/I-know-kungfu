# I-know-kungfu

Status: early product exploration. This README is intentionally simple and subject to change as the repo evolves.

I-know-kungfu explores how to turn messy docs, Obsidian vaults, repos, and research folders into installable Knowledge Packs that AI agents can inspect, search, cite, and use without custom RAG setup.

## One-line pitch

Install trusted knowledge into AI agents.

## Current product frame

Find useful wikis or packs to add to your knowledge base, compare local fit, serve them through the right surface, and harmonize diffs when the new pack overlaps with what you already know.

## Core idea

Knowledge Packs are portable, inspectable packages of curated knowledge. A pack should expose enough structure for humans and agents to answer:

- What does this pack cover?
- What is explicitly out of scope?
- Where did the source material come from?
- How fresh or trustworthy is it?
- Which surfaces can an agent use: MCP, `llms.txt`, raw Markdown, or `index.json`?
- When should an agent cite, refuse, or route to another source?

## Current MVP direction

The first slice is a local-first Cookbook serving flow, not a hosted marketplace.

The target flow is:

```text
Find useful wiki / pack
→ check local fit
→ choose serving surface
→ harmonize overlap
→ inspect scope / proof / refusal
```

The MVP should prove that a user can inspect a small static registry of Knowledge Packs, compare a candidate pack against local knowledge, install or route it locally, serve it through agent-readable surfaces, and see grounded agent behavior with citations and out-of-scope refusal.

## Repository structure

```text
CONTEXT.md
  Project glossary and domain terms.

docs/PRD.md
  Current PRD for the Cookbook Serving MVP.

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

Nothing should leave the user's machine unless they explicitly choose to publish, upload, or share a Knowledge Pack. Scanning, compiling, inspecting, installing, and serving should work locally first.

## Not in scope yet

- Hosted marketplace backend
- Accounts or payments
- Public upload moderation
- Hosted RAG or vector database retrieval
- Cloud MCP hosting
- Browser extension
- Automatic third-party pack trust

## Useful docs

Start here:

- `CONTEXT.md` for shared vocabulary
- `docs/PRD.md` for the current MVP requirements
- `prototype/cookbook-serving/NOTES.md` for prototype status and run notes
