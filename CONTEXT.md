# I-know-kungfu Context

This file captures project glossary only. It should not contain implementation plans, requirements, or roadmap notes.

## Glossary

### Knowledge Pack

An installable, inspectable package of curated knowledge for humans and AI agents. A Knowledge Pack exposes a Pack Contract and agent-readable surfaces such as MCP, `llms.txt`, raw Markdown, and `index.json`.

### Pack Contract

The explicit agreement a Knowledge Pack exposes to humans and agents: identity, scope, non-scope, provenance, freshness, license, trust state, available surfaces, and validation state. A Pack Contract can be produced from a scan, an `iknow.yaml` file, official docs metadata, or manual review.

### Cookbook

The discovery and serving surface for Knowledge Packs. It helps humans and agents find useful packs, inspect trust and scope, check local fit, choose a serving surface, and understand proof/refusal behavior.

### Creator-consumer

The first target user pattern for I-know-kungfu: a person who has messy local source knowledge to organize and also wants trusted context served into agents.

### Human agent-user

A human who uses AI agents and wants trusted context installed or routed into those agents without building custom RAG infrastructure.

### Agent consumer

An AI agent acting as a first-class user of Knowledge Packs. It lists, inspects, searches, reads, cites, and refuses based on Pack Contracts and available sources.

### Local knowledge inventory

A local map of what knowledge the user already has before deciding what packs they need. It may include vault pages, docs folders, installed packs, source domains, freshness, ownership, and routing boundaries.

### Knowledge scan

An optional local action that creates or updates a Local Knowledge Inventory by inspecting a user's vault, docs, repos, and installed packs. It helps users see existing coverage and risk before installing, compiling, or publishing packs.

### Source manifest

A machine-readable inventory of source files and source-declared or inferred metadata. It records what was scanned, what was excluded, where metadata came from, and where confidence is weak.

### Metadata enrichment

The process of deriving missing metadata from weakly structured sources using paths, filenames, headings, frontmatter, links, dates, repeated terms, and optional LLM-assisted labeling. Enriched metadata must be marked as inferred rather than source-declared.

### `iknow.yaml`

The structured manual Pack Contract configuration file. It lets users skip the optional scan by declaring pack identity, scope, non-scope, sources, include/exclude rules, license, maintainer, and publication intent.

### Local pack compilation

The process of converting selected local docs or vault folders into a reviewable private draft Knowledge Pack. Local pack compilation does not imply marketplace publication.

### Reviewable private draft pack

The default output of local pack compilation. It includes agent-consumable artifacts plus review artifacts such as source metadata, warnings, and review notes so the creator can inspect scope, provenance, sensitivity risk, and serving behavior before any share/publish decision.

### Local-first trust principle

Nothing leaves the user's machine unless they explicitly choose to publish, upload, or share a Knowledge Pack. Scanning, compiling, inspecting, installing, and serving should work locally first.

### Context fit check

A pre-install or pre-route comparison between a candidate Knowledge Pack and the user's Local Knowledge Inventory. It surfaces overlap, gaps, conflicts, boundaries, and route recommendations before the pack is trusted.

### Knowledge overlap

When a candidate Knowledge Pack covers concepts, sources, or claims that already exist in the user's local knowledge. Overlap can be duplicate, complementary, fresher, stale, contradictory, or higher provenance.

### Knowledge merge risk

The chance that installing, routing, or trusting a Knowledge Pack will pollute, duplicate, contradict, or confuse the user's existing context.

### Harmonization

The explicit decision step for handling overlap between local knowledge and a candidate pack. Examples include install, skip, route only for a bounded use case, prefer local source, prefer pack source, or keep both with clear boundaries.

### Serving surface

A way an agent or tool can consume a Knowledge Pack. V1 serving surfaces are MCP, `llms.txt`, raw Markdown, and `index.json`.

### Agent harness

An agent runtime, client, or workflow environment that can consume Knowledge Packs through supported serving surfaces. Examples include Hermes, Claude Desktop, Cursor, Codex-style coding agents, LangGraph-based agents, and other MCP-capable tools.

### Harness-agnostic pack

A Knowledge Pack that is not tied to one agent runtime. It exposes standard serving surfaces so different agent harnesses can discover, inspect, search, cite, and route the same knowledge.

### Surface-first integration

An integration strategy where Knowledge Packs support standard serving surfaces before bespoke client adapters. Harness-specific setup guides can wrap those surfaces without changing the Pack Contract.

### Quality marketplace

A marketplace posture where Knowledge Packs are treated as curated knowledge products, not bulk document uploads. Public distribution requires quality, provenance, scope, validation, and trust gates.

### Distribution pack

A Knowledge Pack published by a product, tool, course, or community to help users discover, set up, and get value from that product or domain. It acts as useful agent context and as a distribution funnel.

### Public pack trust ladder

The staged path a Knowledge Pack moves through before broad public marketplace distribution: Private Draft, Unlisted Share, Community Pack, Verified Pack, Official Pack.

### Listing eligibility

The minimum gate for a Knowledge Pack to appear in public Cookbook search. It proves the pack has a clear enough contract to inspect safely, but does not mean Cookbook or agents should actively recommend it.

### Recommendation eligibility

The higher gate for a Knowledge Pack to be actively recommended by Cookbook or agents. It requires stronger quality signals such as evals, freshness policy, task fit, low merge risk, and maintainer reputation or verification.

### Community Pack

A public pack that is contract-valid enough to inspect and install with caution, but has not passed the stronger Verified Pack bar.

### Verified Pack

A Knowledge Pack that has passed Pack Contract verification, source/provenance verification, and behavior verification. Verification means the pack is structurally valid, source-backed, and behaves safely under basic evals; it is not merely publisher identity.

### Official Pack

A Verified Pack owned, approved, or claimed by the original product, tool, course, community, or source owner.

### Local control plane

The local CLI/filesystem layer that scans, compiles, inspects, installs, and serves Knowledge Packs without requiring a hosted backend.

### Registry backend

The hosted product layer for public/unlisted pack discovery, publisher accounts, listing gates, recommendation eligibility, trust signals, monetization, and official/verified ownership claims. It should not store private vault contents by default.

### Pack registry database

The database behind the Registry backend. It stores package metadata, artifact pointers, trust state, publication state, ownership, versions, validation results, recommendation signals, and monetization records; it should not store private source knowledge unless the user explicitly publishes it.

### Endpoint-ready seam

An architecture seam that keeps a local-first module easy to connect to hosted endpoints later. The first adapter can be local/static/filesystem-backed while the interface remains ready for hosted registry, artifact, validation, identity, and publish adapters.

### Source-local draft storage

The source-adjacent workspace where scans, manifests, and draft pack outputs live while a creator is building or reviewing a pack. Recommended path: `./.kungfu/`.

### Global installed pack store

The local user-level store for packs that have been explicitly installed and are available to agent harnesses. Recommended path: `~/.iknow/`.

### Cookbook serving prototype

A UI smell test for the user-facing flow of finding a Knowledge Pack, inspecting trust and scope, checking local fit, choosing a serving surface, and understanding how an agent would consume it.

### Variant C

The accepted initial prototype direction: find useful wiki or pack, check local fit, choose serving surface, harmonize overlap, then inspect scope, proof, and refusal.

### Frontier decision

A decision that must be resolved to build the next useful slice. Decisions beyond the current uncertainty boundary should be noted but not over-designed.
