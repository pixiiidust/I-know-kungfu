# Pixoid: Handoff for `/prototype` — Cookbook Serving UI Smell Test

Date: 2026-06-19
Repo: `pixiiidust/I-know-kungfu`
Status: post-`/grill-with-docs`, ready for `/prototype` session in CLI

## Source artifacts

Read these first:

- `CONTEXT.md` — glossary and locked domain language.
- `docs/research/2026-06-19-brainstorm.md` — full brainstorm and grill decisions.

Do not duplicate or rewrite those docs unless the prototype reveals a concrete correction.

## Suggested skills

Load these before acting:

- `prototype` — required; this is a throwaway UI smell test.
- `domain-modeling` — if new terms emerge from the prototype.
- `verb-first` — if writing visible product copy.
- `claude-design` or `sketch` — if available and useful for fast HTML UI variants.

## Current product frame

`I-know-kungfu` is a local-first system for creating, inspecting, installing, and serving Knowledge Packs for AI agents.

The core promise:

> Install trusted knowledge into AI agents without giving up local control.

Knowledge Packs expose standard surfaces:

- MCP — primary serving path.
- `llms.txt` — universal fallback / agent entrypoint.
- raw Markdown — citation/retrieval corpus.
- `index.json` — machine-readable registry.

The product is harness-agnostic. Hermes can be the first proof context, but the pack should not feel Hermes-only.

## Locked grill decisions

- First user pattern: **creator-consumer** — someone with messy local docs/vaults who also wants trusted agent context.
- Local-first trust principle: nothing leaves the machine unless explicitly published/shared.
- Scan is optional; users can also provide `iknow.yaml` manually.
- `iknow compile` defaults to a reviewable private draft pack.
- Storage seam: `./.kungfu/` for source-local scans/drafts/manifests; `~/.iknow/` for installed packs available to agents.
- Surface-first integration: MCP, `llms.txt`, raw Markdown, `index.json`; avoid custom harness integrations in v1.
- Public marketplace trust ladder: Private Draft → Unlisted Share → Community Pack → Verified Pack → Official Pack.
- Listing eligibility and recommendation eligibility are separate gates.
- Verified Pack means contract + source/provenance + behavior/eval checks, not just publisher identity.
- Endpoint-ready seams are desired, but do not build backend past the fog of war.

## Prototype goal

Build a minimal UI smell test for serving from Cookbook.

Question the prototype must answer:

> Does the Cookbook serving flow feel understandable before we build the CLI/backend?

This is a **UI prototype**, not a backend/CLI implementation.

## Prototype scope

Primary screen:

> One pack detail / serve flow, with a small sidebar/list of other packs.

Do **not** start with full marketplace browsing. The goal is to test the trust → fit → serve moment, not discovery breadth.

Required flow:

```text
Cookbook pack listing/sidebar
→ inspect trust/scope/install surfaces
→ compare/fit note if local inventory exists
→ choose serve surface
→ show MCP / llms.txt / raw Markdown / index.json setup
→ show sample cited answer and out-of-scope behavior
```

## Fake vs prove boundary

Fake:

- real backend
- real auth
- real payments
- real pack upload
- real MCP process
- real search infrastructure

Prove visually:

- what a pack card/detail view shows
- what trust/status looks like
- how a user chooses a serving surface
- how context fit appears
- what “agent can now use this” means
- where citations/out-of-scope behavior appears

## Suggested static data

Use realistic static packs:

1. **Agent Workflow Setup Pack**
   - Status: Verified Pack
   - Fit: overlaps with local Hermes/Pixi Wiki notes; fills harness setup gaps
   - Surfaces: MCP, `llms.txt`, raw Markdown, `index.json`
   - Sample question: “How should I set up a first Hermes agent workflow?”
   - Sample citation: `agent-workflows/wiki/concepts/knowledge-pack-routing.md`

2. **Terminal Setup Pack**
   - Status: Official Pack or Community Pack candidate
   - Fit: helps users install/configure/get value from a tool
   - Shows product-docs-as-distribution-funnel idea

3. **MCP Basics Pack**
   - Status: Community Pack
   - Fit: low overlap, fills protocol background
   - Demonstrates findable but not necessarily recommended

## UI elements to include

For the selected pack detail:

- Pack title, maintainer, status badge: Community / Verified / Official.
- Scope and non-scope.
- Trust panel:
  - provenance
  - license
  - freshness
  - validation/eval status
  - sensitivity status
- Context fit panel:
  - overlap with local inventory
  - gaps filled
  - merge/routing recommendation
- Serve surface selector:
  - MCP
  - `llms.txt`
  - raw Markdown
  - `index.json`
- Setup panel:
  - copyable command/config block
  - “Install locally” / “Serve via MCP” buttons can be fake
- Agent proof panel:
  - sample grounded answer with citation
  - sample out-of-scope refusal

## Visual/tone constraints

Use Jamie’s dark UI preference:

- near-black base
- muted teal
- burgundy `#8b4356`
- pale gold `#fbdc92`
- avoid orange

Keep the copy practical, not hypey.

## Suggested implementation approach

Use `/prototype` UI branch.

Build a throwaway static UI with one command to run. Since this repo is currently docs-only, choose the lightest practical setup:

- Option A: single static HTML/CSS/JS file under `prototype/cookbook-serving/` with a tiny local server command.
- Option B: minimal Vite app if the CLI environment already has Node tooling ready.

Prefer Option A unless there is an obvious project scaffold already present.

The prototype should be clearly marked throwaway.

Suggested path:

```text
prototype/cookbook-serving/
  index.html
  NOTES.md
```

Suggested run command:

```bash
python3 -m http.server 4173 --directory prototype/cookbook-serving
```

## CLI prompt for next session

Copy/paste this into the CLI:

```text
Pixoid: Run /prototype for the I-know-kungfu repo.

Repo: /root/hermes-workspace/I-know-kungfu

Load skills: prototype, domain-modeling, verb-first. Read CONTEXT.md and docs/research/2026-06-19-brainstorm.md first.

Goal: build a throwaway UI smell test for the Cookbook serving flow. The prototype question is: “Does the Cookbook serving flow feel understandable before we build the CLI/backend?”

Use the UI branch of /prototype. Build one primary screen: a Knowledge Pack detail / serve flow with a small sidebar/list of other packs. Do not build full marketplace browse, auth, payments, backend, upload, real MCP, or real search.

The UI must visually prove:
- what a pack detail/card shows
- trust/status badges: Community, Verified, Official
- scope and non-scope
- context fit against local inventory: overlap, gaps, routing recommendation
- serving surface choices: MCP, llms.txt, raw Markdown, index.json
- copyable setup/config blocks
- a sample cited answer
- an out-of-scope refusal example

Use static realistic data for:
- Agent Workflow Setup Pack
- Terminal Setup Pack
- MCP Basics Pack

Use Jamie’s dark UI preference: near-black, muted teal, burgundy #8b4356, pale gold #fbdc92, no orange.

Implementation preference: because the repo is docs-only, create a clearly throwaway static prototype at prototype/cookbook-serving/ with index.html and NOTES.md. Use one command to run, ideally:
python3 -m http.server 4173 --directory prototype/cookbook-serving

After building, run it, inspect it in the browser if available, and report the real verification result. Do not commit unless asked.
```

## Completion criteria for prototype session

The prototype session is complete when:

1. A runnable throwaway UI exists.
2. The run command works.
3. The UI has been inspected, preferably with browser/screenshot verification.
4. The session captures what felt right/wrong in `prototype/cookbook-serving/NOTES.md`.
5. No backend/CLI production work is started.
