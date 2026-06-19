# I-know-kungfu Context

This file captures the project glossary only. It should not contain implementation plans or product requirements.

## Glossary

### Knowledge Pack

An installable, inspectable package of curated knowledge that an AI agent can consume through surfaces such as `llms.txt`, raw Markdown, metadata, and MCP tools.

### Human agent-user

A human who uses AI agents and wants trusted context installed into those agents without building custom RAG infrastructure.

### Creator-consumer

The first target user pattern for I-know-kungfu: a person who both has messy source knowledge to curate and wants trusted context to use with agents. Their pain is two-sided: they need to clean/package their own knowledge and then consume it through agent tools.

### Agent consumer

An AI agent acting as a first-class user of Knowledge Packs. It lists, inspects, searches, reads, cites, and refuses based on the pack contract and available sources.

### Pack contract

The explicit metadata and boundaries that tell humans and agents what a Knowledge Pack covers, what it does not cover, how fresh it is, where sources came from, and how it should be installed or served.

### Cookbook

The discovery and recommendation surface for Knowledge Packs. It maps a human or agent task to relevant packs, trust signals, install instructions, and serving options.

### Local knowledge inventory

A user's map of what knowledge they already have before they decide what Knowledge Packs they need. It can include local vault pages, installed packs, source domains, freshness, ownership, and routing boundaries. This is the knowledge equivalent of Odysseus Cookbook scanning hardware before recommending models.

### Knowledge scan

The action that creates or updates a local knowledge inventory. It inspects a user's vault, docs, repos, and installed packs to summarize existing coverage before Cookbook recommends new packs. The scan can run locally first so users can see what would be packaged or shared before choosing whether to upload anything.

### Local pack compilation

The process of converting a user's selected local docs or vault folders into agent-consumable package artifacts such as `llms.txt`, `index.json`, raw Markdown mirrors, metadata, and optionally a local MCP-readable pack. Local compilation does not imply marketplace publication.

### Private draft pack

A Knowledge Pack generated for local/private review before publication. It lets the creator inspect scope, sources, sensitive content risk, metadata, and agent-serving behavior before deciding whether to upload or list the pack.

### Quality marketplace

A marketplace posture where Knowledge Packs are treated as valuable curated knowledge products, not bulk document uploads. Public distribution requires quality, provenance, scope, validation, and trust gates so the marketplace does not become a dumping ground for noisy or low-effort content.

### Distribution pack

A Knowledge Pack published by a product, tool, course, or community to help users discover, set up, and get value from that product or domain. It acts as both useful agent context and a distribution funnel, because agents can recommend and use it when it fits a user's task.

### Public pack trust ladder

The staged path a Knowledge Pack moves through before broad public marketplace distribution: private draft, unlisted share, community pack, verified pack, official pack. Anyone can create private packs, but public listing requires validation. Official product/tool docs packs should be labeled separately from community packs.

### Listing eligibility

The minimum gate for a Knowledge Pack to appear in public Cookbook search. It proves the pack has a clear contract and can be safely inspected, but does not mean Cookbook or agents should actively recommend it.

### Recommendation eligibility

The higher gate for a Knowledge Pack to be actively recommended by Cookbook or agents. It requires stronger quality signals such as evals, freshness policy, usage/task fit, low merge risk, and maintainer reputation or verification.

### Verified Pack

A Knowledge Pack that has passed pack contract verification, source/provenance verification, and behavior verification. Verification means the pack is structurally valid, source-backed, and behaves safely under basic evals; it does not only mean the publisher identity is known.

### Official Pack

A Verified Pack owned, approved, or claimed by the original product, tool, course, community, or source owner. Official status adds source-owner verification on top of normal pack verification.

### Agent harness

An agent runtime, client, or workflow environment that can consume Knowledge Packs through supported surfaces such as MCP, `llms.txt`, raw Markdown, or `index.json`. Examples may include Hermes, Claude Desktop, Cursor, Codex-style coding agents, LangGraph-based agents, and other MCP-capable tools.

### Harness-agnostic pack

A Knowledge Pack that is not tied to one agent runtime. It exposes standard surfaces so different agent harnesses can discover, inspect, search, cite, and route the same knowledge.

### Surface-first integration

An integration strategy where Knowledge Packs support standard consumption surfaces before bespoke client adapters. The v1 surfaces are MCP, `llms.txt`, raw Markdown, and `index.json`; harness-specific setup guides can wrap those surfaces without changing the pack format.

### Optional knowledge scan

A local scan mode the user can choose to run before compiling, installing, or publishing packs. It should help users understand existing coverage and risk, but it should not be mandatory for users who already know their source scope. Users can skip scan and compile directly from explicit include/exclude rules, but public publication still requires enough metadata to pass listing gates.

### Metadata enrichment

The process of deriving missing metadata from weakly structured sources using file paths, filenames, headings, frontmatter when present, links, dates, repeated terms, and optional LLM-assisted labeling. Enriched metadata should be marked as inferred rather than source-declared.

### Source manifest

A machine-readable inventory of source files and inferred/source-declared metadata produced before `llms.txt`. It records what was scanned, what was excluded, what metadata was known or inferred, and where confidence is weak.

### `iknow.yaml`

The structured manual pack configuration file. It lets users skip the optional scan by declaring pack identity, scope, non-scope, sources, include/exclude rules, license, maintainer, and publication intent explicitly.

### Pack contract

The required structured agreement that a Knowledge Pack exposes to humans and agents. It can be produced from a scan, an `iknow.yaml` file, official docs metadata, or manual review, but public listing requires a complete enough contract regardless of how it was produced.

### Reviewable private draft pack

The default output of `iknow compile`. It includes the agent-consumable pack artifacts plus review artifacts such as `sources.json`, `review.md`, and `warnings.json` so the creator can inspect metadata, provenance, sensitivity warnings, and serving behavior before any publish/share decision.

### Local control plane

The local CLI/filesystem layer that scans, compiles, inspects, installs, and serves Knowledge Packs without requiring a hosted backend. It is the first MVP system because it proves value while preserving the local-first trust principle.

### Registry backend

The hosted product layer for public/unlisted pack discovery, publisher accounts, listing gates, recommendation eligibility, trust signals, monetization, and official/verified ownership claims. It should not store private vault contents by default.

### Pack registry database

The database behind the Registry backend. It stores pack listings, metadata, trust state, publication state, ownership, versions, validation results, recommendation signals, and monetization records. It should store package metadata and artifact pointers, not private source knowledge unless the user explicitly uploads/publishes it.

### Endpoint-ready seams

Architecture boundaries that keep local-first modules easy to connect to hosted endpoints later without requiring those endpoints in the first build. Modules should expose clear interfaces for registry search, validation, artifact storage, identity, and publish flows, while the first implementation can use local filesystem or mock adapters.

### Source-local draft storage

The source-adjacent workspace where scans, manifests, and draft pack outputs live while a creator is building or reviewing a pack. Recommended path: `./.kungfu/`. It keeps private draft state close to the source docs and makes it clear the pack is not globally installed yet.

### Global installed pack store

The local user-level store for packs that have been explicitly installed and are available to agent harnesses. Recommended path: `~/.iknow/`. It separates "I am building this pack" from "my agents may use this pack".

### Frontier decision

A decision that must be resolved to build the next useful slice. Decisions beyond the current uncertainty boundary should be noted but not over-designed.

### Cookbook serving prototype

A post-grill UI smell test for the user-facing flow of finding a Knowledge Pack, inspecting its trust/scope, choosing a serving surface, and understanding how an agent would consume it through MCP, `llms.txt`, raw Markdown, or `index.json`. It should be built with `/prototype` after the grill session, not during the current decision pass. The first prototype screen should center on one pack detail / serve flow, with a small sidebar/list of other packs, rather than starting with full marketplace browse.

### Local-first trust principle

Nothing leaves the user's machine unless they explicitly choose to publish, upload, or share a Knowledge Pack. Scanning, compiling, inspecting, and serving should work locally first.

### Context fit check

A pre-install inspection step that compares a candidate Knowledge Pack against the user's local knowledge inventory. It identifies overlap, gaps, conflicts, duplicate concepts, and integration risk before the pack is trusted or installed.

### Knowledge overlap

When a candidate Knowledge Pack covers concepts, sources, or claims that already exist in the user's local knowledge base. Overlap is not automatically bad: it can be duplicate, complementary, fresher, stale, contradictory, or higher provenance.

### Knowledge merge risk

The chance that installing or trusting a Knowledge Pack will pollute, duplicate, contradict, or confuse the user's existing context. The product should surface this risk before installation rather than assuming every relevant pack is safe to add.
