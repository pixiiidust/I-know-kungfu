# I-know-kungfu — Brainstorm Notes

Date: 2026-06-19
Status: early research / pre-PRD

## Working repo name

`I-know-kungfu`

Inspired by the Matrix fantasy of instantly loading a capability, but applied to AI-agent context rather than human martial arts.

Use as playful repo/prototype name. Avoid Matrix logos/assets/quoted marketing beyond the light inspiration.

## Product thesis

I-know-kungfu turns Obsidian vaults, raw docs, repos, and research folders into installable Knowledge Packs that agents can load through `llms.txt`, raw Markdown, source metadata, and MCP.

Humans inspect and install trusted packs. Agents search, cite, and respect pack boundaries.

## One-line pitch

Install trusted knowledge into AI agents.

## Verb-first version

Turn messy docs and Obsidian vaults into installable Knowledge Packs so agents can search, cite, and use trusted context without building custom RAG from scratch.

## Source inspiration

Odysseus Cookbook has a hardware-aware model recommendation/install/serve pattern:

```text
scan hardware → recommend models → download model → serve model
```

I-know-kungfu adapts the shape for knowledge:

```text
understand task → recommend Knowledge Packs → install pack → serve pack through MCP → grounded agent answers
```

The difference:

- Odysseus optimizes around machine fit: “Can this model run on my hardware?”
- I-know-kungfu optimizes around task/context fit: “Which trusted knowledge should this human or agent use for this job?”

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
User docs / Obsidian vault / research corpus
        ↓
Compiler / curator
        ↓
Curated Knowledge Pack
        ↓
llms.txt + llms-full.txt + index.json + raw Markdown + metadata
        ↓
Cookbook registry
        ↓
Human or agent discovers the pack
        ↓
Pack is installed locally
        ↓
MCP server exposes pack search/read tools
        ↓
Agent answers faster with citations and scope checks
```

## Marketplace posture

Do not start with payments, accounts, reviews, or public upload moderation.

Start with:

1. package format;
2. local compiler;
3. static cookbook registry;
4. local install command;
5. MCP serve path;
6. cited answer demo;
7. out-of-scope refusal demo.

Marketplace comes later after trust, provenance, install flow, and quality gates work.

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

As an agent user, I can install the “Agent Workflows” Knowledge Pack from Cookbook, connect it to my MCP client, and ask “What is Knowledge Pack Routing?” The agent answers with citations from the pack instead of guessing.

This single story proves the product.

## Prototype shape

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
