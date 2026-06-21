# I-know-kungfu

Grow your knowledge base with proven wikis your agents can actually use.

I-know-kungfu helps users import, adapt, and serve bounded knowledge base wikis instead of starting from scratch or relying on noisy web search. Each wiki is source-backed, scoped, and exposed through agent-readable entry points such as MCP, `llms.txt`, raw Markdown, and `index.json`.

The result: agents can search a specific trusted source, cite exact pages, refuse out-of-scope questions, and waste fewer tokens wandering the open web.

## Try the UI prototype

Open the Cookbook serving prototype:

```text
https://pixiiidust.github.io/I-know-kungfu/
```

The prototype shows the preferred flow:

```text
find wiki → check fit → choose entry point → harmonize overlap → inspect proof/refusal
```

## What this repo contains

This repo currently implements a local-first MVP control plane for the Cookbook wiki serving flow.

It can:

- list candidate wikis from a static Cookbook registry
- inspect a Wiki Contract for scope, non-scope, provenance, trust, freshness, and entry points
- compare a candidate wiki against a local knowledge inventory
- compile Markdown sources plus `iknow.yaml` into a reviewable draft wiki
- install approved draft wikis into a local store
- search and read installed wikis through an agent-facing serving seam
- validate listing and recommendation eligibility locally
- demonstrate in-scope citation and out-of-scope refusal

## Core concepts

### Knowledge base wiki

The main product object. A bounded, source-backed wiki that humans can inspect and agents can search, read, cite, and refuse against.

### Knowledge Pack

The portable package/install format for a knowledge base wiki. The wiki is the thing users grow and agents use; the pack is how that wiki moves between local storage, Cookbook listings, and agent harnesses.

### Cookbook

The discovery and serving surface. It helps a user find useful wikis, compare fit against local knowledge, choose an entry point, and decide how to harmonize overlap.

### Context fit

A local comparison between a candidate wiki and what the user already knows. It surfaces overlap, gaps, conflicts, boundaries, and a route recommendation before install.

## Install locally

Requires Python 3.11+.

```bash
pip install -e ".[dev]"
```

Check the CLI:

```bash
iknow --help
iknow --version
```

## Run the end-to-end demo

The original MVP demo uses bundled fixtures only. No network access is required.

```bash
python scripts/demo.py
```

You should see the full local flow:

```text
Cookbook list
→ inspect Agent Workflow Setup Wiki
→ check local fit
→ compile a draft wiki
→ install it into a temp local store
→ search an in-scope query
→ refuse an out-of-scope query
→ read a cited source document
```

## Run the Phase 2 real-data demo

The real-data Cookbook walkthrough uses the Phase 2 packaged wiki fixtures and generated registry data:

```bash
python scripts/phase2_real_data_demo.py
```

It proves:

```text
inspect real package → fit check → export registry → install/route → serve/search/read → cited answer → refusal
```

Details: [`docs/demo/phase2-real-data-cookbook.md`](docs/demo/phase2-real-data-cookbook.md)

Phase 2 boundary: [`docs/roadmap/phase2-real-data-productization.md`](docs/roadmap/phase2-real-data-productization.md)

## CLI quick reference

```bash
# Find candidate wikis
iknow cookbook list

# Inspect scope, trust, freshness, and entry points
iknow cookbook inspect agent_workflow_setup

# Compare against local inventory
iknow fit agent_workflow_setup

# Compile a private draft wiki
iknow compile --config tests/fixtures/issue6/iknow.yaml

# Install the compiled draft locally
iknow install test-wiki \
  --draft-dir tests/fixtures/issue6/.kungfu/drafts/test-wiki

# List installed wikis
iknow list

# Search in-scope content
iknow serve search test-wiki testing

# Refuse an out-of-scope query
iknow serve search test-wiki deployment

# Read an exact source document
iknow serve read test-wiki getting-started.md
```

## Project structure

```text
src/iknow/
  cli.py              CLI entry point
  contracts/          Wiki Contract parsing and validation
  registry/           Static Cookbook registry
  inventory/          Local knowledge inventory
  fit/                Context fit comparison
  harmonization/      Explicit install/route/merge decisions
  compiler/           Draft wiki compiler
  store/              Installed wiki store
  serving/            Search/read serving seam
  validation/         Listing and recommendation gates

prototype/cookbook-serving/
  Static UI prototype deployed to GitHub Pages

docs/
  PRD, ADRs, research notes, and handoffs
```

## Run tests

```bash
python -m pytest -q
```

Current verification target:

```text
327 passed
```

## Local-first principle

Scanning, compiling, inspecting, installing, and serving should work locally first. Nothing should leave the user's machine unless they explicitly choose to publish, upload, or share a wiki.

## Not in scope yet

- hosted marketplace backend
- accounts or payments
- public upload moderation
- hosted RAG or vector database retrieval
- cloud MCP hosting
- browser extension
- automatic third-party wiki trust

## Documentation

Start with:

- [`CONTEXT.md`](CONTEXT.md) — glossary and domain terms
- [`docs/PRD.md`](docs/PRD.md) — current MVP requirements
- [`docs/roadmap/phase2-real-data-productization.md`](docs/roadmap/phase2-real-data-productization.md) — Phase 2 boundary and issue sequence
- [`docs/adr/0001-knowledge-base-wiki-is-core-object.md`](docs/adr/0001-knowledge-base-wiki-is-core-object.md) — vocabulary decision
- [`docs/adr/0002-graphify-context-fit-adapter.md`](docs/adr/0002-graphify-context-fit-adapter.md) — Graphify adapter boundary decision
- [`prototype/cookbook-serving/NOTES.md`](prototype/cookbook-serving/NOTES.md) — prototype notes
