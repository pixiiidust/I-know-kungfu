# Graphify-backed Context Fit demo

This walkthrough proves the adapter path without private local files:

```text
checked-in synthetic Graphify graph
→ Graphify-derived LocalKnowledgeInventory
→ candidate Wiki Contract fit
→ exact overlap / graph evidence / gaps / boundary warnings
→ route recommendation
```

Run it locally:

```bash
python scripts/graphify_fit_demo.py
```

The demo is deterministic and local-only. It reads:

```text
tests/fixtures/graphify/context_fit_graph.json
```

It does **not** run Graphify, install hooks, start MCP/HTTP servers, mutate the
local store, scan private files, or make network calls.

## What the demo shows

### GOOD FIT

Candidate scope:

```text
MCP Server Development
```

Expected behavior:

- exact overlap appears
- graph evidence sources cite the synthetic local source path
- no boundary warning
- route recommendation is `recommended_install`

### POOR FIT

Candidate scope:

```text
Rust compiler internals
```

Expected behavior:

- no exact overlap
- no graph-evidence overlap
- candidate topic remains a gap
- route recommendation stays conservative, usually `findable_only`

### BOUNDARY-RISK FIT

Candidate scope:

```text
Knowledge Pack Routing
Product Case Studies
```

Expected behavior:

- both topics have exact graph-derived local evidence
- the topics belong to different synthetic Graphify communities
- Context Fit emits a bounded-context warning
- recommendation becomes `route_with_care`, not clean install

## Trust boundary

Graphify-backed evidence answers:

```text
"What does my local graph appear to contain, and where are the boundaries?"
```

It does **not** answer:

```text
"Is this candidate official, fresh, trustworthy, or safe to install?"
```

Those decisions remain governed by I-know-kungfu Wiki Contracts, provenance,
freshness, trust state, and install/serve gates.
