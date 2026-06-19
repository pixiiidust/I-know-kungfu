# I-know-kungfu — Brainstorm Notes

Date: 2026-06-19
Status: early research / pre-PRD

Terminology clarification after PRD refinement: **knowledge base wiki** is the core product object. **Knowledge Pack** is the portable package/install format for a wiki, not the main product noun. Earlier brainstorm sections may use "pack" as shorthand; read them through this distinction.

## Working repo name

`I-know-kungfu`

Inspired by the Matrix fantasy of instantly loading a capability, but applied to AI-agent context rather than human martial arts.

Use as playful repo/prototype name. Avoid Matrix logos/assets/quoted marketing beyond the light inspiration.

## Product thesis

I-know-kungfu helps users grow and evolve their own knowledge base by importing, adapting, and serving bounded knowledge base wikis instead of starting from scratch or relying on noisy web search.

Each imported serving unit is conceptually a wiki: source-backed pages, scope/non-scope, provenance, freshness, and agent-friendly entry points such as MCP, `llms.txt`, raw Markdown, and `index.json`.

A **Knowledge Pack** is the portable packaging/install format for a knowledge base wiki. It is useful implementation language, but not the primary product noun.

## One-line pitch

Grow your knowledge base with proven wikis your agents can actually use.

## Verb-first version

Import proven knowledge base wikis, fit them to what you already know, and serve them to agents as bounded, source-backed context without building custom RAG from scratch.

## Source inspiration

Odysseus Cookbook has a hardware-aware model recommendation/install/serve pattern:

```text
scan hardware → recommend models → download model → serve model
```

I-know-kungfu adapts the shape for knowledge:

```text
scan existing knowledge → understand task → recommend Knowledge Packs → fit-check pack → install/route pack → serve pack through MCP → grounded agent answers
```

The difference:

- Odysseus optimizes around machine fit: “Can this model run on my hardware?”
- I-know-kungfu optimizes around task/context fit: “What knowledge do I already have, what am I missing, and which trusted pack should this human or agent use for this job?”

The analogy is stronger with a scan-first sequence:

```text
Odysseus: hardware scan → model recommendations → download → serve
I-know-kungfu: knowledge scan → pack recommendations → install/route → serve via MCP
```

## Core lock

People want agents to use reliable domain context, but their knowledge is trapped in messy vaults, docs, repos, and half-stale notes.

Existing RAG/upload-docs flows are often:

- hard to package;
- hard to trust;
- hard to install;
- hard to cite;
- hard to keep fresh;
- unclear when out of scope.

## Proposed key

A registry/cookbook of installable Knowledge Packs.

Each pack is a portable, inspectable knowledge artifact with:

- `kb.json` metadata;
- `README.md` overview;
- `llms.txt` compact routing entrypoint;
- `llms-full.txt` full-corpus context;
- `index.json` machine registry;
- raw Markdown pages;
- source/provenance metadata;
- validation/eval metadata;
- MCP serving instructions.

## Product loop

```text
User docs / Obsidian vault / installed packs / research corpus
        ↓
Local knowledge inventory: what do I already have?
        ↓
Cookbook recommends candidate Knowledge Packs
        ↓
Context fit check: overlap, gaps, conflicts, freshness, routing boundaries
        ↓
Human approves install / trust / routing
        ↓
Pack is installed locally
        ↓
MCP server exposes pack search/read tools
        ↓
Agent answers faster with citations and scope checks
```

The sequence should not assume users know what they need before they know what they already have. For creator-consumers, inventory comes before recommendation.

Supply-side publishing has a separate trust sequence:

```text
Creator submits / compiles pack
        ↓
Private draft pack
        ↓
Validation: metadata, provenance, license, scope, leakage checks, evals
        ↓
Staged / unlisted review
        ↓
Marketplace listing only after trust gates pass
```

A first-time publisher should not be immediately served in the public marketplace.

## Marketplace posture

Do not start with payments, accounts, reviews, or public upload moderation.

Start with:

2. local knowledge scan;
3. local compiler;
4. static cookbook registry;
5. context fit check;
6. local install command;
7. MCP serve path;
8. cited answer demo;
9. out-of-scope refusal demo.

Marketplace comes later after trust, provenance, install flow, and quality gates work.

Core trust principle: nothing leaves the user's machine unless they explicitly choose to publish, upload, or share a Knowledge Pack. Scanning, compiling, inspecting, and local MCP serving should work locally first.

Marketplace quality stance: avoid becoming a Scribd-style dumping ground for noisy uploads. Public packs should be curated, scoped, provenance-backed, and validated before distribution. High-quality Knowledge Packs can be monetizable knowledge products, similar to how curated educational knowledge can be monetized by media/learning products.

Distribution angle: product/tool docs can become Knowledge Packs that help users set up and get value from the product. For example, terminal/tooling docs could be packaged for users who want an agent to help them install, configure, troubleshoot, and use that product well. This makes packs both useful context and a discovery funnel.

Public-pack trust ladder:

```text
Private Draft
→ Unlisted Share
→ Community Pack
→ Verified Pack
→ Official Pack
```

Anyone can create private packs. Public marketplace listing requires validation. Official product/tool docs packs should be labeled separately from community packs.

GitHub Marketplace analogy, checked against GitHub Docs on 2026-06-19:

- GitHub separates ordinary repositories from Marketplace app listings. Repositories can be created freely, while Marketplace listings go through draft/submission/review requirements.
- Marketplace listings require customer-facing basics: valid publisher contact, relevant app description, pricing plan, privacy policy, support method, working links, platform integration/value beyond authentication, and listing assets/copy quality.
- Paid Marketplace apps have a higher bar: verified publisher organization, usage threshold, and billing event handling.
- GitHub Marketplace badges distinguish publisher/listing verification signals, but GitHub explicitly says it does not analyze or inspect third-party code; publishers remain responsible for app upkeep.

Implication for I-know-kungfu: use a GitHub-like split between open/private creation and curated public listing, but be stricter than GitHub on pack quality because bad knowledge can directly pollute agent answers. Verification should mean source/provenance/scope/eval quality, not only publisher identity.

Public visibility and recommendation should be separate gates:

```text
Gate A: Listing eligibility
- Can appear in public Cookbook search.
- Requires scope/non-scope, provenance, license, maintainer/contact, support/report link, valid generated artifacts, and sensitivity scan.

Gate B: Recommendation eligibility
- Can be actively recommended by Cookbook or agents.
- Requires eval set, freshness policy, task/use-case fit, no severe overlap/conflict flags, and maintainer reputation or verification.
```

A pack can be findable before it is recommended. This keeps discovery open while protecting users and agents from low-quality or risky context.

Meaning of verification:

```text
Community Pack
= public, contract valid enough to inspect and install with caution.

Verified Pack
= contract valid + source/provenance checked + behavior/eval checks passed.

Official Pack
= Verified Pack owned, approved, or claimed by the original product/tool/source owner.
```

Verification should not mean publisher identity alone. Because packs shape agent answers, verification must include pack contract quality, source/provenance quality, and behavior under basic evals.

## Actors

### Human actors

- Creator — turns vault/docs into a Knowledge Pack.
- Consumer — installs and uses a Knowledge Pack.
- Maintainer — updates and validates a pack.
- Marketplace operator — governs registry quality later.

### Agent actors

- Agent consumer — discovers, searches, reads, cites, and refuses based on installed/public packs.
- Agent curator — helps compile, classify, summarize, and validate source docs.
- Agent installer — recommends or installs the right pack for a task, with human approval.
- Agent evaluator — checks whether answers are grounded in pack sources.

Important correction: the “user” can be an agent, not only a human.

## MVP user stories

### Human consumer

1. As a human, I can browse Cookbook and inspect a Knowledge Pack’s scope, freshness, sources, and install instructions.
2. As a human, I can install one Knowledge Pack locally.
3. As a human, I can connect the installed pack to my agent through MCP.

### Agent consumer

4. As an agent, I can list installed Knowledge Packs.
5. As an agent, I can inspect a pack’s scope/non-scope before using it.
6. As an agent, I can search and read the pack through MCP.
7. As an agent, I can answer with citations from exact KB pages.
8. As an agent, I can refuse or redirect when the pack does not cover the question.

### Creator / curator

9. As a creator, I can compile docs or Obsidian notes into a Knowledge Pack.
10. As an agent curator, I can suggest include/exclude rules and metadata before the creator publishes.
11. As a maintainer, I can validate the pack contract before publication.
12. As a maintainer, I can regenerate the pack when sources change.

## Agent-as-user stories

### Discovery

- As an agent, I want to list available Knowledge Packs so I can decide which context source fits the user’s task.
- As an agent, I want to inspect a pack’s scope, non-scope, freshness, and confidence so I know whether I should rely on it.
- As an agent, I want to search packs by task/domain/tool-use so I can avoid loading irrelevant context.

### Retrieval

- As an agent, I want to search a selected Knowledge Pack through MCP so I can retrieve only relevant pages.
- As an agent, I want to read exact source pages so I can ground my answer in durable knowledge.
- As an agent, I want page metadata, source paths, and updated dates so I can explain freshness/reliability.

### Answering

- As an agent, I want to cite specific KB pages so the human can verify claims.
- As an agent, I want to detect when a question is outside the pack’s scope so I can refuse or ask to use another source.
- As an agent, I want to combine multiple approved packs when a task crosses domains without mixing their source boundaries.

### Installation / routing

- As an agent, I want to recommend the best Knowledge Pack for a task so the human does not have to browse manually.
- As an agent, I want to produce copy-paste install/MCP config instructions so the human can connect the pack quickly.
- As an agent, I want to request approval before installing or trusting a new third-party pack.

### Curation

- As an agent curator, I want to scan a vault/docs folder and propose include/exclude rules so private or low-quality notes are not packaged.
- As an agent curator, I want to classify docs into entities, concepts, syntheses, projects, and references so the pack has useful structure.
- As an agent curator, I want to generate `llms.txt`, `index.json`, and source metadata so other agents can consume the pack predictably.
- As an agent curator, I want to flag missing provenance, stale pages, or weak citations before publication.

### Evaluation

- As an agent evaluator, I want to run test questions against a pack so I can measure whether it answers what it claims to cover.
- As an agent evaluator, I want to check citations against retrieved pages so hallucinated claims are caught.
- As an agent evaluator, I want to test out-of-scope questions so the pack teaches agents when not to answer.

## Story map

```text
DISCOVER
- Browse Cookbook
- Search by task/domain/tool
- Inspect pack contract

TRUST
- See maintainer
- See sources
- See freshness
- See license
- See scope/non-scope
- See eval checks

INSTALL
- Download pack
- Verify package
- Store locally
- Copy MCP config

SERVE
- Start MCP server
- Expose search/read tools
- Connect agent client

USE
- Ask question
- Retrieve cited pages
- Answer grounded in pack
- Refuse out-of-scope

CREATE
- Import docs/vault
- Select include/exclude paths
- Compile pages
- Generate metadata
- Preview
- Publish/register

MAINTAIN
- Regenerate
- Validate
- Changelog
- Report mistake
```

## Suggested MVP demo story

As a creator-consumer with an existing messy knowledge base, I can inspect a first-time agent setup Knowledge Pack from Cookbook, compare it against my current knowledge, see overlap/gaps/conflicts, install it only if it fits, connect it to my agent harness through MCP or another supported surface, and ask a setup/workflow question. The agent answers with citations from the pack instead of guessing.

The first proof pack can use Hermes because it matches the original pain, but the product should be harness-agnostic. Knowledge Packs should work across leading agent harnesses and clients through standard surfaces such as MCP, `llms.txt`, raw Markdown, and `index.json`.

V1 integration principle: surface-first, not harness-specific.

```text
Primary path: MCP clients
Universal fallback: llms.txt
Tool/building-block path: raw Markdown + index.json
```

Ship setup instructions for leading harnesses as wrappers over those surfaces rather than building custom integrations per harness.

Scan principle: optional and local-first.

Users should be able to run a knowledge scan before compiling, installing, or publishing packs, but it should not be mandatory when they already know the source scope. Users can skip scan and compile directly from explicit include/exclude rules. However, public publication still requires enough metadata to pass listing gates.

Recommended weak-metadata pipeline:

```text
raw docs/vault
→ source manifest: paths, filenames, headings, links, dates, known frontmatter, excludes
→ metadata enrichment: inferred domains, topics, sensitivity warnings, confidence
→ user review: approve/rename/exclude weak labels
→ package artifacts: kb.json, index.json, llms.txt, raw Markdown mirror
→ optional MCP serve
```

Do not generate `llms.txt` as the first artifact. Generate a source manifest first, then derive `index.json` and `llms.txt` from reviewed metadata. If sources have weak metadata, label fields as inferred and confidence-scored rather than pretending they were source-declared.

Manual structured path:

Users can skip scan with an explicit `iknow.yaml` pack contract.

```yaml
id: terminal-setup
title: Terminal Setup Pack
scope: Helps users install, configure, troubleshoot, and get value from Terminal.
non_scope:
  - Does not cover unrelated shell scripting.
  - Does not replace official support.
sources:
  - path: docs/
    include: ["**/*.md"]
    exclude: ["drafts/**", "private/**"]
license: CC-BY-4.0
maintainer:
  name: Example Maintainer
publication:
  default_visibility: private_draft
```

```bash
iknow compile --config iknow.yaml
```

Scan is one way to produce a pack contract. `iknow.yaml` is another. Public listing gates still apply either way.

Compile output default: reviewable private draft pack.

```text
.kungfu/packs/<pack-id>/
  kb.json
  index.json
  llms.txt
  raw/
  sources.json
  review.md
  warnings.json
```

`iknow compile` should not default to a minimal publishable artifact. It should default to a private draft with review artifacts so the creator can inspect generated metadata, sensitivity warnings, source provenance, and serving behavior before publish/share decisions.

Next explicit actions:

```bash
iknow inspect <pack-id>
iknow serve <pack-id> --mcp
```

Backend posture:

This is a product, so it eventually needs a backend, but the backend should not be required for the first local proof. Do not plan past the fog of war: resolve only the frontier decisions needed for the next build slice, while keeping module seams endpoint-ready.

Architecture stance:

```text
Build local-first modules now.
Expose clean ports/adapters for hosted endpoints later.
Use filesystem/local adapters first.
Do not bake in assumptions that block registry/API scaling.
```

Frontier decisions resolved/recommended now:

```text
1. Pack contract shape: iknow.yaml → kb.json/index.json/llms.txt.
2. Draft output shape: reviewable private draft pack.
3. Local storage seam: source-local drafts + global installed packs.
4. Serve seam: local MCP over installed packs.
5. Registry seam: interface for search/list/publish/validate, backed by local mock/static registry for now.
```

Local storage recommendation:

```text
./.kungfu/
  scans/
  drafts/
  manifests/

~/.iknow/
  installed/
  registry/
  mcp/
```

Reason: source-local `.kungfu` keeps private draft state close to the docs being packaged; global `~/.iknow` marks packs that have been explicitly installed and are available to agents. This separates "I am building/reviewing this pack" from "my agent can use this pack".

Backend seams to design, not fully build yet:

```text
RegistryClient
- search_packs(query)
- get_pack(id)
- submit_pack_manifest(pack)
- check_listing_eligibility(pack)

ArtifactStore
- put_artifact(pack_version, file)
- get_artifact(pack_version, file)

ValidationService
- validate_contract(pack)
- validate_sources(pack)
- run_eval_set(pack)

IdentityProvider
- current_user()
- current_org()
- claim_official_pack(pack)
```

Local control plane responsibilities:

```text
scan local docs/vaults
compile private draft packs
inspect warnings/provenance
install packs locally
serve through MCP
compare candidate packs against local inventory
```

Registry backend responsibilities later:

```text
public/unlisted pack listings
publisher accounts/orgs
listing eligibility gates
recommendation eligibility gates
verified/official ownership claims
versioning and update metadata
trust/reputation signals
monetization later
```

Database should store metadata and pointers first, not private vault contents by default. Do not design the full DB beyond the current seam needs.

This story proves the product only if it includes a context fit check before install. Installing a prebuilt pack without overlap/conflict awareness can create duplicate or polluted knowledge.

## Prototype shape

After the `/grill-with-docs` frontier decisions are finished, run `/prototype` to build a minimal UI smell test for serving from Cookbook. The prototype question is: "Does the Cookbook serving flow feel understandable before we build the CLI/backend?"

Primary prototype screen: one pack detail / serve flow, with a small sidebar/list of other packs. Do not start with full marketplace browse. The goal is to test the trust → fit → serve moment, not discovery breadth.

Prototype should focus on the user-facing serving flow:

```text
Cookbook pack listing
→ inspect trust/scope/install surfaces
→ compare/fit note if local inventory exists
→ choose serve surface
→ show MCP / llms.txt / raw Markdown setup
→ ask/sample cited answer
```

Prototype fake/prove boundary:

```text
Fake:
- real backend
- real auth
- real payments
- real pack upload
- real MCP process
- real search infrastructure

Prove visually:
- what a pack card shows
- what trust/status looks like
- how a user chooses a serving surface
- how context fit appears
- what “agent can now use this” means
- where citations/out-of-scope behavior appears
```

The `/prototype` output should be UI-only with realistic static data. It is a smell test, not the working CLI/backend.

Do not start the UI prototype until the grill session finishes the frontier decisions.

Build a static web Cookbook plus local CLI installer using existing Pixi Wiki data.

One-weekend scope:

1. Add `/cookbook` page.
2. Define `kb.json` package schema.
3. Package 2 existing KBs.
4. Add install command that copies packs locally.
5. Run existing MCP server against installed packs.
6. Show one grounded query with citation.
7. Show one out-of-scope refusal.

## MVP acceptance criteria

The MVP works if a demo can do this in under 5 minutes:

1. Open Cookbook.
2. Pick a Knowledge Pack.
3. See why it is trustworthy.
4. Install it.
5. Serve it through MCP.
6. Ask a question.
7. Get a cited answer.
8. See an out-of-scope refusal.

## Non-goals for first slice

- payments;
- accounts;
- reviews;
- public upload moderation;
- vector DB;
- hosted RAG;
- full Obsidian sync;
- complex quality scoring;
- browser extension;
- cloud MCP hosting.

## Open questions for /grill-with-docs

1. Who is the first real buyer/user: indie agent builders, students, teams, researchers, or agent tool vendors?
2. Is the first product a local CLI, web cookbook, hosted registry, or compiler?
3. What counts as a valid Knowledge Pack?
4. What minimum provenance is required before a pack can be trusted?
5. What does “less hallucination” mean in measurable MVP terms?
6. Should agent installation ever happen automatically, or always require human approval?
7. What is the first pack domain that best proves value?
8. What does the pack refuse to answer?
9. Is the marketplace for public packs, private/team packs, or both?
10. What is the trust model for third-party packs?
