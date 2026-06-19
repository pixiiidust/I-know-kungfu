# I-know-kungfu Context

This file captures project glossary only. It should not contain implementation plans, requirements, or roadmap notes.

## Glossary

### Knowledge base wiki

The core product object in I-know-kungfu: a bounded, source-backed wiki that a human can inspect and an AI agent can search, read, cite, and refuse against. It is the knowledge surface users grow, adapt, and serve over time.

### Agent-readable wiki

A knowledge base wiki with explicit agent entry points such as MCP, `llms.txt`, raw Markdown, and `index.json`.

### Knowledge Pack

The portable packaging and installation format for a knowledge base wiki. A Knowledge Pack moves a wiki between local storage, Cookbook listings, and agent harnesses; it is not the core conceptual object.

### Wiki Contract

The explicit agreement a knowledge base wiki exposes to humans and agents: identity, scope, non-scope, provenance, freshness, license, trust state, available entry points, and validation state. A Wiki Contract can be produced from a scan, an `iknow.yaml` file, official docs metadata, or manual review.

### Cookbook

The discovery and serving surface for knowledge base wikis. It helps humans and agents find useful wikis, inspect trust and scope, check local fit, choose a serving entry point, and understand proof/refusal behavior.

### Creator-consumer

The first target user pattern for I-know-kungfu: a person who has messy local source knowledge to organize and also wants trusted context served into agents.

### Human agent-user

A human who uses AI agents and wants trusted context installed or routed into those agents without building custom RAG infrastructure.

### Agent consumer

An AI agent acting as a first-class user of knowledge base wikis. It lists, inspects, searches, reads, cites, and refuses based on Wiki Contracts and available sources.

### Local knowledge inventory

A local map of what knowledge the user already has before deciding what wikis they need. It may include vault pages, docs folders, installed wikis, source domains, freshness, ownership, and routing boundaries.

### Knowledge scan

An optional local action that creates or updates a Local Knowledge Inventory by inspecting a user's vault, docs, repos, and installed wikis. It helps users see existing coverage and risk before installing, compiling, or publishing wikis.

### Source manifest

A machine-readable inventory of source files and source-declared or inferred metadata. It records what was scanned, what was excluded, where metadata came from, and where confidence is weak.

### Metadata enrichment

The process of deriving missing metadata from weakly structured sources using paths, filenames, headings, frontmatter, links, dates, repeated terms, and optional LLM-assisted labeling. Enriched metadata must be marked as inferred rather than source-declared.

### `iknow.yaml`

The structured manual Wiki Contract configuration file. It lets users skip the optional scan by declaring wiki identity, scope, non-scope, sources, include/exclude rules, license, maintainer, and publication intent.

### Local wiki compilation

The process of converting selected local docs or vault folders into a reviewable private draft knowledge base wiki. Local wiki compilation does not imply marketplace publication.

### Reviewable private draft wiki

The default output of local wiki compilation. It includes agent-consumable artifacts plus review artifacts such as source metadata, warnings, and review notes so the creator can inspect scope, provenance, sensitivity risk, and serving behavior before any share/publish decision.

### Local-first trust principle

Nothing leaves the user's machine unless they explicitly choose to publish, upload, or share a knowledge base wiki. Scanning, compiling, inspecting, installing, and serving should work locally first.

### Context fit check

A pre-install or pre-route comparison between a candidate knowledge base wiki and the user's Local Knowledge Inventory. It surfaces overlap, gaps, conflicts, boundaries, and route recommendations before the wiki is trusted.

### Knowledge overlap

When a candidate knowledge base wiki covers concepts, sources, or claims that already exist in the user's local knowledge. Overlap can be duplicate, complementary, fresher, stale, contradictory, or higher provenance.

### Knowledge merge risk

The chance that installing, routing, or trusting a knowledge base wiki will pollute, duplicate, contradict, or confuse the user's existing context.

### Harmonization

The explicit decision step for handling overlap between local knowledge and a candidate wiki. Examples include install, skip, route only for a bounded use case, prefer local source, prefer wiki source, or keep both with clear boundaries.

### Serving entry point

A way an agent or tool can consume a knowledge base wiki. V1 entry points are MCP, `llms.txt`, raw Markdown, and `index.json`.

### Agent harness

An agent runtime, client, or workflow environment that can consume knowledge base wikis through supported serving entry points. Examples include Hermes, Claude Desktop, Cursor, Codex-style coding agents, LangGraph-based agents, and other MCP-capable tools.

### Harness-agnostic wiki

A knowledge base wiki that is not tied to one agent runtime. It exposes standard serving entry points so different agent harnesses can discover, inspect, search, cite, and route the same knowledge.

### Surface-first integration

An integration strategy where knowledge base wikis support standard serving entry points before bespoke client adapters. Harness-specific setup guides can wrap those entry points without changing the Wiki Contract.

### Quality marketplace

A marketplace posture where knowledge base wikis are treated as curated knowledge products, not bulk document uploads. Public distribution requires quality, provenance, scope, validation, and trust gates.

### Distribution wiki

A knowledge base wiki published by a product, tool, course, or community to help users discover, set up, and get value from that product or domain. It acts as useful agent context and as a distribution funnel.

### Public wiki trust ladder

The staged path a knowledge base wiki moves through before broad public marketplace distribution: Private Draft, Unlisted Share, Community Wiki, Verified Wiki, Official Wiki.

### Listing eligibility

The minimum gate for a knowledge base wiki to appear in public Cookbook search. It proves the wiki has a clear enough contract to inspect safely, but does not mean Cookbook or agents should actively recommend it.

### Recommendation eligibility

The higher gate for a knowledge base wiki to be actively recommended by Cookbook or agents. It requires stronger quality signals such as evals, freshness policy, task fit, low merge risk, and maintainer reputation or verification.

### Community Wiki

A public wiki that is contract-valid enough to inspect and install with caution, but has not passed the stronger Verified Wiki bar.

### Verified Wiki

A knowledge base wiki that has passed Wiki Contract verification, source/provenance verification, and behavior verification. Verification means the wiki is structurally valid, source-backed, and behaves safely under basic evals; it is not merely publisher identity.

### Official Wiki

A Verified Wiki owned, approved, or claimed by the original product, tool, course, community, or source owner.

### Local control plane

The local CLI/filesystem layer that scans, compiles, inspects, installs, and serves knowledge base wikis without requiring a hosted backend.

### Registry backend

The hosted product layer for public/unlisted wiki discovery, publisher accounts, listing gates, recommendation eligibility, trust signals, monetization, and official/verified ownership claims. It should not store private vault contents by default.

### Wiki registry database

The database behind the Registry backend. It stores wiki metadata, artifact pointers, trust state, publication state, ownership, versions, validation results, recommendation signals, and monetization records; it should not store private source knowledge unless the user explicitly publishes it.

### Endpoint-ready seam

An architecture seam that keeps a local-first module easy to connect to hosted endpoints later. The first adapter can be local/static/filesystem-backed while the interface remains ready for hosted registry, artifact, validation, identity, and publish adapters.

### Source-local draft storage

The source-adjacent workspace where scans, manifests, and draft wiki outputs live while a creator is building or reviewing a wiki. Recommended path: `./.kungfu/`.

### Global installed wiki store

The local user-level store for wikis that have been explicitly installed and are available to agent harnesses. Recommended path: `~/.iknow/`.

### Cookbook serving prototype

A UI smell test for the user-facing flow of finding a knowledge base wiki, inspecting trust and scope, checking local fit, choosing a serving entry point, and understanding how an agent would consume it.

### Variant C

The accepted initial prototype direction: find useful knowledge base wiki, check local fit, choose serving entry point, harmonize overlap, then inspect scope, proof, and refusal.

### Frontier decision

A decision that must be resolved to build the next useful slice. Decisions beyond the current uncertainty boundary should be noted but not over-designed.
