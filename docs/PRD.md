# PRD: Cookbook Wiki Serving MVP

Date: 2026-06-19
Status: implemented for Phase 1; Phase 2 real-data productization in progress
Prototype decision: Variant C was the historical smell-test direction; Variant A is now the chosen UI surface for Phase 2.

## Problem Statement

People want agents to use reliable domain context, but their knowledge is trapped in messy vaults, docs, repos, research folders, half-stale notes, and scattered external sources.

Existing RAG, upload-docs, and web-search flows are often hard to trust, hard to cite, hard to keep fresh, wasteful with tokens, and unclear about when an agent should refuse because a source is out of scope.

I-know-kungfu should help users grow and evolve their own knowledge base by importing, adapting, and serving bounded knowledge base wikis instead of reinventing knowledge from scratch. A candidate wiki should be source-backed, scoped, proven enough to trust, and exposed through agent-friendly entry points.

This PRD covers the first slice of a larger local-first knowledge distribution system: prove that a wiki can be discovered, fitted to existing local knowledge, harmonized, served, cited, and refused against before expanding into hosted registry, publisher, verification, and monetization workflows.

The first product slice should prove the Cookbook wiki serving flow locally before building a hosted marketplace. The flow must answer:

- What useful knowledge base wiki should I add?
- Does it fit what I already know?
- Which entry point should my agent use: MCP, `llms.txt`, raw Markdown, or `index.json`?
- What overlaps, conflicts, gaps, or boundaries need harmonizing before I trust it?
- Can the agent answer with citations and refuse out-of-scope questions?

## Solution

Build a local-first Cookbook wiki serving MVP that lets a human or agent inspect a small static registry of knowledge base wikis, compare a candidate wiki against a local knowledge inventory, install or route the wiki locally, serve it through supported agent-readable entry points, and demonstrate grounded use with citations and out-of-scope refusal.

The original prototype smell-test direction was Variant C:

```text
Find useful knowledge base wiki
→ check local fit
→ choose serving entry point
→ harmonize overlap
→ inspect scope / proof / refusal
```

This PRD does not ask for a full marketplace. It defines the durable substrate that later marketplace work depends on: Wiki Contract, Context Fit, Harmonization, Installed Wiki Store, and Serving seams. It asks for the smallest working slice that proves the trust-to-serve path:

1. A static Cookbook registry with a few realistic knowledge base wikis.
2. A Wiki Contract format that exposes scope, non-scope, provenance, trust state, freshness, and entry points.
3. A local install/store path.
4. A serving path over MCP first, with `llms.txt`, raw Markdown, and `index.json` as standard entry points.
5. A context fit check that shows overlap, gaps, conflicts, and route recommendations before install/trust.
6. A demo query that returns a cited answer.
7. A demo query that refuses or redirects when the selected wiki is out of scope.

A **Knowledge Pack** is the portable packaging/install format for one of these wikis. It is useful implementation language, but the product concept should stay centered on knowledge base wikis.

## User Stories

1. As a human consumer, I want to browse a Cookbook of knowledge base wikis, so that I can find useful context without manually hunting through docs.
2. As a human consumer, I want to see whether a wiki is Community, Verified, or Official, so that I can understand its trust posture before relying on it.
3. As a human consumer, I want to inspect a wiki’s scope, so that I know what questions it can reasonably answer.
4. As a human consumer, I want to inspect a wiki’s non-scope, so that I know what questions it should not answer.
5. As a human consumer, I want to see source and provenance metadata, so that I can judge whether the wiki is grounded enough to use.
6. As a human consumer, I want to see freshness metadata, so that I can tell whether the wiki may be stale.
7. As a human consumer, I want to compare a candidate wiki against my local knowledge inventory, so that I do not blindly duplicate or pollute my existing context.
8. As a human consumer, I want to see overlap before installation, so that I can decide whether to merge, route, or skip duplicated concepts.
9. As a human consumer, I want to see gaps the wiki fills, so that I can decide whether it adds enough value.
10. As a human consumer, I want to see conflict or boundary warnings, so that I do not route agents to the wrong source.
11. As a human consumer, I want a clear route recommendation, so that I know whether the wiki should be installed, used cautiously, or only kept findable.
12. As a human consumer, I want to approve a serving entry point explicitly, so that I do not trust an entire wiki forever by accident.
13. As a human consumer, I want copyable MCP setup instructions, so that I can connect a wiki to an MCP-capable agent quickly.
14. As a human consumer, I want copyable `llms.txt` instructions, so that I can give an agent a compact routing entrypoint.
15. As a human consumer, I want raw Markdown access, so that I can audit the source pages behind an answer.
16. As a human consumer, I want `index.json` access, so that tools can read machine-friendly wiki metadata.
17. As a human consumer, I want to install a wiki locally, so that my agents can use it without uploading private knowledge.
18. As a human consumer, I want all private scanning and serving to work locally first, so that nothing leaves my machine unless I explicitly publish, upload, or share.
19. As a human consumer, I want to ask a sample question after serving a wiki, so that I can see what “agent can now use this” means.
20. As a human consumer, I want the sample answer to cite exact source pages, so that I can verify the answer.
21. As a human consumer, I want the agent to refuse out-of-scope questions, so that the wiki does not create false confidence.
22. As a human consumer, I want the install flow to preserve scope boundaries, so that agents do not use a setup wiki for unrelated tasks.
23. As a human consumer, I want visible harmonization decisions, so that overlap becomes a review step instead of a hidden side effect.
24. As a human consumer, I want a wiki to be findable before it is recommended, so that discovery stays open while active recommendations stay safer.
25. As a human consumer, I want Community wikis to be clearly lower-trust than Verified or Official wikis, so that I treat them with appropriate caution.
26. As a human consumer, I want Official wikis to mean source-owner-approved Verified wikis, so that “official” is not confused with generic identity verification.
27. As an agent consumer, I want to list available knowledge base wikis, so that I can decide which context source fits the human’s task.
28. As an agent consumer, I want to inspect a Wiki Contract before using the wiki, so that I know scope, non-scope, trust state, freshness, and entry points.
29. As an agent consumer, I want to search a selected wiki through MCP, so that I can retrieve only relevant pages.
30. As an agent consumer, I want to read exact source pages, so that my answer can be grounded in durable knowledge.
31. As an agent consumer, I want page metadata and source paths, so that I can explain freshness and reliability.
32. As an agent consumer, I want to cite exact Markdown paths, so that the human can verify my claims.
33. As an agent consumer, I want to detect when a question is outside the wiki’s scope, so that I can refuse or ask to use another source.
34. As an agent consumer, I want to combine multiple approved wikis only when their boundaries are clear, so that I do not mix unrelated sources.
35. As an agent installer, I want to recommend a wiki for a task only after checking local fit, so that the user does not install risky or duplicative context blindly.
36. As an agent installer, I want to produce copy-paste setup commands, so that the human can approve and connect the wiki quickly.
37. As an agent installer, I want to request approval before installing or trusting a third-party wiki, so that the human stays in control.
38. As a creator, I want to compile docs or Obsidian notes into a private draft wiki, so that I can review what would be exposed before publishing.
39. As a creator, I want source manifests before generated routing files, so that weak metadata is visible before it becomes agent-facing truth.
40. As a creator, I want inferred metadata to be marked as inferred, so that agents and humans do not confuse guesses with source-declared facts.
41. As a creator, I want `iknow.yaml` as a manual Wiki Contract path, so that I can skip scanning when I already know the source scope.
42. As a maintainer, I want validation checks for Wiki Contracts, so that public listings meet a minimum quality bar.
43. As a maintainer, I want provenance checks, so that wikis do not cite unknown or unsafe sources.
44. As a maintainer, I want behavior/eval checks, so that Verified wikis demonstrate grounded answers and appropriate refusals.
45. As a marketplace operator later, I want listing eligibility separate from recommendation eligibility, so that public discovery does not imply active endorsement.
46. As a marketplace operator later, I want hosted registry seams without requiring the hosted backend now, so that the local-first MVP can grow without being rewritten.
47. As a product builder, I want the first proof to use a small number of existing knowledge base wikis, so that the demo proves the flow without creating marketplace sprawl.
48. As a product builder, I want the demo to complete in under five minutes, so that the MVP is understandable in a short walkthrough.
49. As a product builder, I want the UI to stay table/list-first rather than card-pile-first, so that trust, fit, route, and action remain scannable.
50. As a product builder, I want the implementation to keep endpoint-ready seams, so that local adapters can later be swapped for hosted registry, artifact, validation, and identity services.

## Implementation Decisions

- Preserve the product direction from the prototype: find a useful knowledge base wiki, check local fit, choose serving entry point, harmonize overlap, then inspect scope, proof, and refusal. Use Variant A as the chosen UI surface for Phase 2; older Variant C wording is historical.
- Keep the product frame verb-first: find useful wikis to add to a knowledge base, compare local fit, serve through the right entry point, and harmonize diffs when overlap exists.
- Do not frame the product as a prompt library or Loop Library system. The useful reference is the community-sharing/listing pattern, not the product concept.

### Highest useful seam

- Put the first build slice around the **Wiki Contract**. It is the highest useful seam because humans, agents, the Cookbook UI, the compiler, the installer, validators, and future registry endpoints all need the same contract.
- Treat the Wiki Contract as the central interface for the MVP. Its interface includes identity, scope, non-scope, provenance, freshness, license, trust state, available serving entry points, source manifest references, validation state, and warnings.
- Keep the Wiki Contract deep: callers should not need to know whether the contract came from a scan, `iknow.yaml`, official docs metadata, or manual review.

### Local control-plane modules

- Build the **Wiki Contract module** first. Its interface should validate and expose the contract while hiding parsing, defaults, inferred metadata handling, and warning generation.
- Build the **Draft Wiki Compiler module** behind a small interface: compile selected sources plus a Wiki Contract into a Reviewable Private Draft Wiki. Its implementation can handle raw Markdown mirroring, source manifests, `index.json`, `llms.txt`, warnings, and review notes.
- Build the **Local Inventory module** as a separate module from compilation. Its interface should produce a Local Knowledge Inventory; its implementation can use an optional scan now and richer source analysis later.
- Build the **Context Fit module** at the seam between candidate Wiki Contract and Local Knowledge Inventory. Its interface should return overlap, gaps, boundary/conflict warnings, merge risk, and a route recommendation.
- Build the **Harmonization module** as explicit decision state, not hidden mutation. Its interface should represent choices such as install, skip, route-only, prefer-local, prefer-wiki, or keep-both-with-boundaries.
- Build the **Installed Wiki Store module** as the seam between draft wikis and agent-available wikis. Its first adapter should use the local filesystem; future adapters can register installs with a hosted registry without changing callers.
- Build the **Serving module** over installed wikis. Its interface should expose list, summarize, search, and read behavior for agent harnesses. The first serving adapter should be MCP; `llms.txt`, raw Markdown, and `index.json` remain standard entry points rather than bespoke harness integrations.
- Build the **Static Cookbook Registry module** for the first Cookbook slice. Its interface should list wikis and fetch wiki details. Its first adapter can be static/local; future adapters can call a Registry backend.
- Build the **Validation module** as an endpoint-ready seam. Its first adapter can perform local contract/provenance/entry point checks; later adapters can add hosted listing eligibility, recommendation eligibility, and eval checks.

### Endpoint-ready seams

- Keep these seams adapter-backed from the start: Registry, Artifact Store, Validation, Identity, Installed Wiki Store, and Serving.
- Use local/static/filesystem adapters first. Do not build hosted accounts, backend auth, payments, public upload, vector search, or cloud MCP in this PRD.
- Design the interfaces so hosted endpoints can replace local adapters later without changing the Wiki Contract or the Cookbook serving flow.
- Keep identity conceptual in the first slice. Official Wiki ownership claims are later work.

### Storage and artifact decisions

- Separate source-local draft state from globally installed wikis. Drafts live near the source being packaged; installed wikis live in a global user-level store where agents can use them.
- Use `./.kungfu/` for source-local scans, manifests, and drafts.
- Use `~/.iknow/` for installed wikis, local registry configuration, and MCP-serving state.
- Make the default compiler output a Reviewable Private Draft Wiki, not a public listing.
- Include review artifacts in draft output so creators can inspect metadata, provenance, sensitivity warnings, and serving behavior before sharing.
- Generate a Source Manifest before generating `llms.txt`. Do not let weak inferred metadata become routing truth without review.
- Mark inferred metadata as inferred and confidence-scored rather than source-declared.

### Trust and marketplace decisions

- Treat Community Wiki, Verified Wiki, and Official Wiki as distinct trust states.
- Define Community Wiki as public and contract-valid enough to inspect and install with caution.
- Define Verified Wiki as contract-valid, source/provenance checked, and behavior/eval checked.
- Define Official Wiki as Verified plus source-owner approval or ownership.
- Separate Listing Eligibility from Recommendation Eligibility.
- Keep the first registry static/local. This proves browse, inspect, fit-check, install, serve, answer, and refuse without hosted accounts or public upload moderation.

### Serving and UI decisions

- Use MCP as the primary interactive serving path for installed wikis.
- Use `llms.txt` as the universal compact routing entrypoint, not as the whole source of truth.
- Use raw Markdown as the auditable primitive for source citation.
- Use `index.json` as the machine-readable metadata/index entry point.
- Require Context Fit checking before install or trust in the demo path. The product is not proven if it installs wikis without overlap and conflict awareness.
- Represent fit as overlap, gaps filled, boundary/conflict warnings, merge risk, and route recommendation.
- Keep the UI clean, minimal, sequenced, and table/list-first. Avoid dashboard clutter and card piles.
- Build the first demo around one proof wiki, with a small supporting registry of two or three wikis for comparison.

The prototype captured the decision-rich flow as:

```text
Find useful knowledge base wiki
→ check local fit
→ choose serving entry point
→ harmonize overlap
→ inspect scope / proof / refusal
```

## Testing Decisions

- Test external behavior at the highest useful seam. Prefer command-level and integration-style tests over implementation-detail tests.
- Treat the Wiki Contract as the first test surface. Tests should prove that callers can validate and consume a contract without knowing whether it came from `iknow.yaml`, a scan, or static registry data.
- Test the Draft Compiler through its public interface: a valid contract plus selected sources produces a Reviewable Private Draft Wiki with expected artifacts and review outputs.
- Test that generated routing entry points preserve scope and non-scope boundaries.
- Test that inferred metadata is marked as inferred and does not masquerade as source-declared metadata.
- Test the Static Registry through its interface: it can list wikis, return a wiki by id, and preserve Community, Verified, and Official trust states.
- Test that Listing Eligibility and Recommendation Eligibility can diverge.
- Test the Local Inventory and Context Fit seam with realistic inventories: output must include overlap, gaps, boundary/conflict warnings, merge risk, and a route recommendation.
- Test Harmonization as explicit decision state. Installing, skipping, route-only use, prefer-local, prefer-wiki, and keep-both-with-boundaries should be visible decisions, not hidden side effects.
- Test the Installed Wiki Store through its interface: installing a draft registers or copies wiki artifacts into the installed-wiki store without requiring network access.
- Test the Serving module through its interface: installed wikis can be listed, summarized, searched, and read by an agent-facing adapter.
- Test the MCP adapter at the serving seam rather than testing internal file layout directly.
- Test that a sample in-scope query returns an answer with at least one exact source citation.
- Test that a sample out-of-scope query refuses or redirects rather than answering from the wrong wiki.
- Test local-first privacy as behavior: scan, compile, inspect, install, and serve do not require upload, auth, or hosted network access in the first slice.
- Test one end-to-end demo flow: open Cookbook, pick wiki, see trust/scope, check local fit, choose harmonization, install or route locally, serve, ask an in-scope question, get a cited answer, ask an out-of-scope question, get a refusal.
- Do not test visual styling as production behavior yet. The static prototype already served as the initial UI smell test.
- Do not test hosted marketplace behavior, accounts, payments, public upload moderation, cloud MCP, or vector retrieval in this PRD.

## Out of Scope

- Hosted marketplace backend.
- User accounts.
- Payments.
- Reviews.
- Public upload moderation.
- Public publisher onboarding.
- Official ownership claim workflow.
- Complex quality scoring.
- Hosted RAG.
- Vector database retrieval.
- Browser extension.
- Cloud MCP hosting.
- Full Obsidian sync.
- Automatic third-party wiki trust without human approval.
- Real public wiki monetization.
- Large-scale marketplace browsing.
- Replacing source docs with generated summaries.
- Treating `llms.txt` as the entire knowledge source.
- Building prompt-library or Loop Library semantics into the product concept.

## Further Notes

The static prototype passed the initial smell test with Variant C. That means the next work should move from UI prototype to local control-plane proof, not deeper visual polish unless a concrete implementation question needs it.

The quality bar for the MVP is a short demo that works in under five minutes:

1. Open Cookbook.
2. Pick a knowledge base wiki.
3. See why it is trustworthy.
4. Compare local fit.
5. Install or route it locally.
6. Serve it through MCP or another supported entry point.
7. Ask an in-scope question.
8. Get a cited answer.
9. Ask an out-of-scope question.
10. Get a refusal or redirect.

The most important product risk is not search. It is trust routing: installing useful knowledge without polluting the user’s existing context or teaching agents to answer outside the wiki’s boundaries.

The implementation should stay endpoint-ready, but the first slice should prove local value before adding hosted registry infrastructure.
