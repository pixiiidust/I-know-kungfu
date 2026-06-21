# ADR 0002: Graphify is an optional Context Fit evidence adapter

Status: accepted
Date: 2026-06-21

## Context

I-know-kungfu needs a better fitting stage: users should be able to compare a
candidate Wiki Contract against what their local workspace already appears to
contain.

Graphify is useful for this because it can turn a local folder into graph-shaped
evidence: concepts, source files, communities, relationship hints, and weak
bridges between local areas.

But Graphify is not the product's source of truth. I-know-kungfu's source of
truth remains the Wiki Contract and the local install/serve gates.

## Decision

Graphify is allowed as an **optional read-only local inventory / Context Fit evidence adapter**.

In plain terms: Graphify is an optional read-only local inventory / Context Fit evidence adapter, not a product authority.

Allowed role:

```text
local files or synthetic fixture graph
→ Graphify-style graph.json
→ Graphify-derived LocalKnowledgeInventory
→ Context Fit evidence: exact overlap, graph evidence, gaps, source hints,
  bounded-context warnings, route recommendation
```

Graphify evidence may help answer:

```text
What does my local graph appear to contain?
Where might this candidate overlap?
Where are likely gaps?
Does the candidate cross local bounded contexts?
```

Graphify evidence must not answer:

```text
Is this wiki official?
Is it verified?
Is its provenance acceptable?
Is it fresh enough?
Should it be installed automatically?
Can an agent answer from it without the Wiki Contract?
```

## Explicit non-goals for this phase

Do **not** add these by default:

- Graphify install hooks
- committed `graphify-out/` artifacts
- Graphify MCP server dependency
- Graphify HTTP server dependency
- Graphify-generated wiki as the canonical serving layer
- Graphify as trust/provenance/freshness authority
- Graphify as install authority
- Graphify as a required dependency for basic `iknow` usage
- network scans or private local scans in the browser prototype

The current implementation reads a local Graphify-style JSON artifact only when
the user explicitly passes it:

```bash
iknow fit <wiki-id> --inventory-graph graphify-out/graph.json
```

The checked-in demo uses synthetic data:

```bash
python scripts/graphify_fit_demo.py
```

## Private data handling

Graph-derived source paths are evidence hints, not public provenance.

Adapter expectations:

- keep Graphify input local and read-only
- avoid absolute path leakage in public/demo output
- redact machine/user prefixes such as `/home/<user>/`, `/Users/<user>/`,
  `/root/`, and drive-letter prefixes before displaying source hints
- do not commit real private `graphify-out/` output by default
- use synthetic fixtures for public demos and tests
- do not send local graph contents to a remote model as part of the v1 adapter

## Current implementation

Current supported path:

```text
Graphify-style graph.json adapter
```

Implemented pieces:

- synthetic graph fixtures under `tests/fixtures/graphify/`
- `iknow.inventory.graphify` adapter
- `iknow fit --inventory-graph <path>`
- fit output separation:
  - exact overlap
  - related graph evidence
  - gaps
  - evidence sources
  - boundary warnings
  - recommendation
- static Cookbook UI demo data rendering Graphify-backed fit fields
- deterministic walkthrough in `docs/demo/graphify-backed-context-fit.md`

## Future upgrade paths, not implemented now

These are named seams, not current scope:

1. **Graphify `graph.json` adapter v2**
   - richer source-cluster summaries
   - stronger path redaction policy
   - better utility/noise suppression

2. **Graphify MCP adapter**
   - optional local MCP client read path
   - no required server dependency
   - only after local JSON adapter proves useful

3. **Graphify-generated wiki adapter**
   - treat generated wiki pages as local evidence summaries
   - not canonical knowledge-base serving
   - still subordinate to Wiki Contracts

## Consequences

Positive:

- Context Fit becomes more grounded in local evidence.
- Users can see overlap, gaps, and boundary risk before install.
- The product keeps its local-first posture.

Trade-offs:

- Graph evidence is approximate and must be labeled as evidence.
- Token/label overlap can create weak false positives.
- The adapter needs conservative copy and tests to avoid trust overclaims.

Quality bar:

- basic I-know-kungfu commands work without Graphify installed
- Graphify-backed fit is opt-in
- tests use synthetic checked-in graph data
- docs and UI keep saying: Graphify helps fit, Wiki Contracts govern trust
