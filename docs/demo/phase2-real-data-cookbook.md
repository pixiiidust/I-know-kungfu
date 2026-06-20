# Phase 2 real-data Cookbook walkthrough

Run the local-first real-data demo:

```bash
python scripts/phase2_real_data_demo.py
```

The command uses the Phase 2 packaged wiki fixtures under
`tests/fixtures/phase2/` and writes only to a temporary local directory.
It requires no auth, no upload, no hosted backend, no network call, no vector DB,
and no cloud MCP process.

## What it proves

The walkthrough prints the product path end to end:

```text
inspect real package contract
→ compare fit against local inventory
→ export generated Cookbook registry data
→ install/route into a temp local store
→ serve/search/read installed Markdown
→ produce a cited answer
→ refuse an out-of-scope question
```

## Real packages used

- `agent-workflows` — draft/private wiki covering Pixoid/Tinker/Quill/Boba,
  route governance, memory boundaries, handoffs, Knowledge Pack Routing,
  agent entrypoint meshes, and reliability practices.
- `ai-native-product-surfaces` — community/restricted wiki covering AI-native
  product/application surfaces, product demos, PM case studies, and related
  product-language frameworks.

## Expected success markers

A successful run includes these strings:

```text
Phase 2 real-data Cookbook productization demo
Package:      agent-workflows
Recommendation:
Exported 2 wiki(s)
Installed wiki 'agent-workflows'
CITED ANSWER
OUT-OF-SCOPE REFUSAL
Phase 2 real-data demo completed successfully.
```

## Boundary

This is still local/static Phase 2 productization. It intentionally does not add
accounts, uploads, payments, moderation, hosted RAG/vector DB, cloud MCP hosting,
or marketplace backend behavior.
