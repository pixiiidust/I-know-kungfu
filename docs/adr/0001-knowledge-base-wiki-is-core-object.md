# ADR 0001: Use knowledge base wiki as the core product object

Date: 2026-06-19
Status: accepted

## Context

Early product language centered on "Knowledge Packs." That was useful for discussing portable install artifacts, but it started to drift away from the actual product concept.

The user goal is to help people grow and evolve their own knowledge base without starting from scratch. Users should be able to import or adapt bounded, source-backed wikis with proven value, compare them against existing local knowledge, harmonize overlap, and serve them to agents through agent-friendly entry points.

Each imported serving unit is conceptually a wiki: it has pages, scope, non-scope, source provenance, freshness, and entry points that agents can search, read, cite, and refuse against.

## Decision

Use **knowledge base wiki** as the core product object.

Use **Knowledge Pack** only for the portable packaging/install format of a knowledge base wiki.

Use **Wiki Contract** for the metadata/trust agreement exposed by a wiki.

Use **serving entry point** for MCP, `llms.txt`, raw Markdown, and `index.json`.

## Consequences

- README, PRD, glossary, vault notes, and Pixi Wiki entries should describe the product as growing an agent-usable knowledge base by importing and serving bounded wikis.
- The Cookbook should be framed as discovery and serving for useful knowledge base wikis, not as a generic bundle marketplace.
- The implementation can still produce packages/artifacts, but user-facing copy should not make "pack" the primary noun.
- Future marketplace/monetization language should focus on high-quality, verified, official, or proven wikis.
- Agents should be routed to specific bounded wiki sources instead of generic web search where possible, improving citation quality, token efficiency, and refusal behavior.
