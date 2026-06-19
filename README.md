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

---

## Install & run

```bash
# Editable install (local dev)
pip install -e ".[dev]"

# Run the CLI
iknow --help
iknow --version
```

## Run tests

```bash
# With dev extras installed
python -m pytest tests/ -v
```

## Demo: Variant C end-to-end CLI flow

Run the full demo with no network access (uses bundled fixtures only):

```bash
# One command to exercise the whole pipeline
python scripts/demo.py
```

Or step through each phase interactively:

```bash
# 1. Find wiki — list available wikis in the Cookbook registry
iknow cookbook list

# 2. Inspect scope & entry points for a specific wiki
iknow cookbook inspect agent_workflow_setup

# 3. Check local fit — compare against default local inventory
iknow fit agent_workflow_setup

# 4. Compile a private draft from iknow.yaml and Markdown sources
iknow compile --config tests/fixtures/issue6/iknow.yaml

# 5. Install the compiled draft into the global store
iknow install test-wiki \
  --draft-dir tests/fixtures/issue6/.kungfu/drafts/test-wiki

# 6. List installed wikis
iknow list

# 7. Serve — search inside the installed wiki (in-scope → proof)
iknow serve search test-wiki testing

# 8. Serve — search inside the installed wiki (out-of-scope → refusal)
iknow serve search test-wiki deployment

# 9. Serve — read a document with a citation path
iknow serve read test-wiki getting-started.md
```

The demo preserves the **Variant C** order:

```
find wiki → check fit → choose entry point → harmonize → inspect proof/refusal
```

## Module seams (local control plane)

The control plane is organized as a standard `src/iknow/` Python package.
Each sub-module corresponds to one **seam** named in the PRD.
All v1 adapters are local-only — no hosted backend, auth, payments,
vector DB, or cloud MCP.

| Module             | Seam / responsibility                                  | v1 adapter (local-only)                     |
|--------------------|--------------------------------------------------------|---------------------------------------------|
| `contracts`        | Wiki Contract — validate & expose identity, scope, trust, provenance, freshness, entry points | Static files / YAML on disk |
| `registry`         | Static Cookbook Registry — list wikis, fetch details   | Bundled or user-placed JSON/YAML             |
| `inventory`        | Local Knowledge Inventory — what the user already knows | Optional filesystem scan + manual fallback   |
| `fit`              | Context Fit — compare wiki vs inventory: overlap, gaps, conflicts, route recommendation | Heuristic local analysis |
| `harmonization`    | Harmonization — explicit decision state (install, skip, route-only, prefer-local, prefer-wiki, keep-both) | Filesystem-tracked decisions |
| `compiler`         | Draft Wiki Compiler — sources + contract → Reviewable Private Draft Wiki | Local filesystem read/write |
| `store`            | Installed Wiki Store — register drafts as agent-available | Local filesystem (`~/.iknow/`) |
| `serving`          | Serving — list, summarize, search, read installed wikis | Local MCP server |
| `validation`       | Validation — contract, provenance, entry-point checks   | Local static checks |

### Endpoint-ready seams

Registry, store, serving, validation, and identity are designed with
adapter interfaces so that hosted backends can replace local adapters
later without changing the Wiki Contract or the serving flow.

### Identity & trust states

Identity is conceptual in v1. Trust states (Community, Verified, Official)
are tracked in the Wiki Contract but ownership claims require later work.

### Storage convention

| Path          | Purpose                                      |
|---------------|----------------------------------------------|
| `./.kungfu/`  | Source-local scans, manifests, drafts        |
| `~/.iknow/`   | Installed wikis, registry config, MCP state  |

### What is NOT introduced

- Hosted backend
- User accounts or payments
- Public upload moderation
- Vector database or RAG service
- Cloud MCP hosting
- Browser extension
