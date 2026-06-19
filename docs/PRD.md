# PRD: Cookbook Serving MVP

Date: 2026-06-19
Status: ready for agent implementation planning
Prototype decision: Variant C passed the initial smell test

## Problem Statement

People want agents to use reliable domain context, but their knowledge is trapped in messy vaults, docs, repos, research folders, and half-stale notes.

Existing RAG and upload-docs flows are often hard to package, hard to trust, hard to install, hard to cite, hard to keep fresh, and unclear about when an agent should refuse because a source is out of scope.

I-know-kungfu should turn useful docs and wikis into installable Knowledge Packs so humans and agents can inspect scope, compare local fit, choose the right serving surface, and use trusted context without building custom RAG from scratch.

The first product slice should prove the Cookbook serving flow locally before building a hosted marketplace. The flow must answer:

- What useful wiki or pack should I add?
- Does it fit what I already know?
- Which surface should my agent use: MCP, `llms.txt`, raw Markdown, or `index.json`?
- What overlaps, conflicts, gaps, or boundaries need harmonizing before I trust it?
- Can the agent answer with citations and refuse out-of-scope questions?

## Solution

Build a local-first Cookbook serving MVP that lets a human or agent inspect a small static registry of Knowledge Packs, compare a candidate pack against a local knowledge inventory, install or route the pack locally, serve it through supported agent-readable surfaces, and demonstrate grounded use with citations and out-of-scope refusal.

The prototype direction is Variant C:

```text
Find useful wiki / pack
→ check local fit
→ choose serving surface
→ harmonize overlap
→ inspect scope / proof / refusal
```

This PRD does not ask for a full marketplace. It asks for the smallest working slice that proves the trust-to-serve path:

1. A static Cookbook registry with a few realistic packs.
2. A pack contract format that exposes scope, non-scope, provenance, trust state, freshness, and surfaces.
3. A local install/store path.
4. A serving path over MCP first, with `llms.txt`, raw Markdown, and `index.json` as standard surfaces.
5. A context fit check that surfaces overlap, gaps, conflicts, and route recommendations before install/trust.
6. A demo query that returns a cited answer.
7. A demo query that refuses or redirects when the selected pack is out of scope.

## User Stories

1. As a human consumer, I want to browse a Cookbook of Knowledge Packs, so that I can find useful context without manually hunting through docs.
2. As a human consumer, I want to see whether a pack is Community, Verified, or Official, so that I can understand its trust posture before relying on it.
3. As a human consumer, I want to inspect a pack’s scope, so that I know what questions it can reasonably answer.
4. As a human consumer, I want to inspect a pack’s non-scope, so that I know what questions it should not answer.
5. As a human consumer, I want to see source and provenance metadata, so that I can judge whether the pack is grounded enough to use.
6. As a human consumer, I want to see freshness metadata, so that I can tell whether the pack may be stale.
7. As a human consumer, I want to compare a candidate pack against my local knowledge inventory, so that I do not blindly duplicate or pollute my existing context.
8. As a human consumer, I want to see overlap before installation, so that I can decide whether to merge, route, or skip duplicated concepts.
9. As a human consumer, I want to see gaps the pack fills, so that I can decide whether it adds enough value.
10. As a human consumer, I want to see conflict or boundary warnings, so that I do not route agents to the wrong source.
11. As a human consumer, I want a clear route recommendation, so that I know whether the pack should be installed, used cautiously, or only kept findable.
12. As a human consumer, I want to approve a serving surface explicitly, so that I do not trust an entire pack forever by accident.
13. As a human consumer, I want copyable MCP setup instructions, so that I can connect a pack to an MCP-capable agent quickly.
14. As a human consumer, I want copyable `llms.txt` instructions, so that I can give an agent a compact routing entrypoint.
15. As a human consumer, I want raw Markdown access, so that I can audit the source pages behind an answer.
16. As a human consumer, I want `index.json` access, so that tools can read machine-friendly pack metadata.
17. As a human consumer, I want to install a pack locally, so that my agents can use it without uploading private knowledge.
18. As a human consumer, I want all private scanning and serving to work locally first, so that nothing leaves my machine unless I explicitly publish, upload, or share.
19. As a human consumer, I want to ask a sample question after serving a pack, so that I can see what “agent can now use this” means.
20. As a human consumer, I want the sample answer to cite exact source pages, so that I can verify the answer.
21. As a human consumer, I want the agent to refuse out-of-scope questions, so that the pack does not create false confidence.
22. As a human consumer, I want the install flow to preserve scope boundaries, so that agents do not use a setup pack for unrelated tasks.
23. As a human consumer, I want visible harmonization decisions, so that overlap becomes a review step instead of a hidden side effect.
24. As a human consumer, I want a pack to be findable before it is recommended, so that discovery stays open while active recommendations stay safer.
25. As a human consumer, I want Community packs to be clearly lower-trust than Verified or Official packs, so that I treat them with appropriate caution.
26. As a human consumer, I want Official packs to mean source-owner-approved Verified packs, so that “official” is not confused with generic identity verification.
27. As an agent consumer, I want to list available Knowledge Packs, so that I can decide which context source fits the human’s task.
28. As an agent consumer, I want to inspect a pack contract before using the pack, so that I know scope, non-scope, trust state, freshness, and surfaces.
29. As an agent consumer, I want to search a selected pack through MCP, so that I can retrieve only relevant pages.
30. As an agent consumer, I want to read exact source pages, so that my answer can be grounded in durable knowledge.
31. As an agent consumer, I want page metadata and source paths, so that I can explain freshness and reliability.
32. As an agent consumer, I want to cite exact Markdown paths, so that the human can verify my claims.
33. As an agent consumer, I want to detect when a question is outside the pack’s scope, so that I can refuse or ask to use another source.
34. As an agent consumer, I want to combine multiple approved packs only when their boundaries are clear, so that I do not mix unrelated sources.
35. As an agent installer, I want to recommend a pack for a task only after checking local fit, so that the user does not install risky or duplicative context blindly.
36. As an agent installer, I want to produce copy-paste setup commands, so that the human can approve and connect the pack quickly.
37. As an agent installer, I want to request approval before installing or trusting a third-party pack, so that the human stays in control.
38. As a creator, I want to compile docs or Obsidian notes into a private draft pack, so that I can review what would be exposed before publishing.
39. As a creator, I want source manifests before generated routing files, so that weak metadata is visible before it becomes agent-facing truth.
40. As a creator, I want inferred metadata to be marked as inferred, so that agents and humans do not confuse guesses with source-declared facts.
41. As a creator, I want `iknow.yaml` as a manual pack contract path, so that I can skip scanning when I already know the source scope.
42. As a maintainer, I want validation checks for pack contracts, so that public listings meet a minimum quality bar.
43. As a maintainer, I want provenance checks, so that packs do not cite unknown or unsafe sources.
44. As a maintainer, I want behavior/eval checks, so that Verified packs demonstrate grounded answers and appropriate refusals.
45. As a marketplace operator later, I want listing eligibility separate from recommendation eligibility, so that public discovery does not imply active endorsement.
46. As a marketplace operator later, I want hosted registry seams without requiring the hosted backend now, so that the local-first MVP can grow without being rewritten.
47. As a product builder, I want the first proof to use a small number of existing wiki-like packs, so that the demo proves the flow without creating marketplace sprawl.
48. As a product builder, I want the demo to complete in under five minutes, so that the MVP is understandable in a short walkthrough.
49. As a product builder, I want the UI to stay table/list-first rather than card-pile-first, so that trust, fit, route, and action remain scannable.
50. As a product builder, I want the implementation to keep endpoint-ready seams, so that local adapters can later be swapped for hosted registry, artifact, validation, and identity services.

## Implementation Decisions

- Use the Cookbook serving prototype’s Variant C as the product direction for the first build slice.
- Keep the product frame verb-first: find useful wikis to add to your knowledge base, compare local fit, serve through the right surface, and harmonize diffs when overlap exists.
- Do not frame the product as a prompt library or “loop” system. The useful reference is the community-sharing/listing interface pattern, not the product concept.
- Treat Knowledge Packs as portable, inspectable artifacts for agents and humans.
- Use a pack contract as the central seam for the MVP. The contract should expose identity, scope, non-scope, trust state, freshness, provenance, source manifest, surfaces, and validation state.
- Support a manual structured pack configuration path that can produce the pack contract without requiring a scan.
- Support an optional local knowledge scan path. Scanning helps users understand existing coverage and risk, but it should not be mandatory when users already know the source scope.
- Generate a source manifest before generating `llms.txt`. Do not let weak inferred metadata become routing truth without review.
- Mark inferred metadata as inferred and confidence-scored rather than pretending it was source-declared.
- Make the default compiler output a reviewable private draft pack, not a public listing.
- Include review artifacts in draft output so creators can inspect metadata, provenance, sensitivity warnings, and serving behavior before sharing.
- Separate source-local draft state from globally installed packs. Drafts live near the source being packaged; installed packs live in a global user-level store where agents can use them.
- Use a static/local Cookbook registry for the first MVP. This proves browse, inspect, fit-check, install, serve, answer, and refuse without hosted accounts or public upload moderation.
- Keep the registry seam endpoint-ready. The first adapter can be static/local, but the interface should later support hosted search, listing, publish, validation, and trust states.
- Keep the artifact seam endpoint-ready. The first artifact store can be filesystem/local, but the interface should later support hosted artifact pointers.
- Keep the validation seam endpoint-ready. The first validator can be local checks, but the interface should later support stronger contract, provenance, and eval checks.
- Keep the identity seam conceptual only for the first slice. Official-pack ownership claims are later work.
- Use MCP as the primary interactive serving path for installed packs.
- Use `llms.txt` as the universal compact routing entrypoint, not as the whole source of truth.
- Use raw Markdown as the auditable primitive for source citation.
- Use `index.json` as the machine-readable metadata/index surface.
- Require context fit checking before install/trust in the demo path. The product is not proven if it installs packs without overlap and conflict awareness.
- Represent fit as overlap, gaps filled, conflicts/boundaries, and a route recommendation.
- Represent harmonization as explicit user-visible decisions such as merge as route, install, skip, or do not route.
- Treat Community, Verified, and Official as distinct trust states.
- Define Community as public and contract-valid enough to inspect and install with caution.
- Define Verified as contract-valid, source/provenance checked, and behavior/eval checked.
- Define Official as Verified plus source-owner approval or ownership.
- Separate listing eligibility from recommendation eligibility.
- Build the first demo around one proof pack, with a small supporting registry of two or three packs for comparison.
- Keep the UI clean, minimal, sequenced, and table/list-first. Avoid dashboard clutter and card piles.
- The first MVP should be local-first. Nothing leaves the user’s machine unless they explicitly choose to publish, upload, or share.
- The first MVP should not depend on a hosted backend, account system, payments, reviews, public upload moderation, vector database, hosted RAG, browser extension, or cloud MCP hosting.

The prototype captured the decision-rich flow as:

```text
Find useful wiki / pack
→ check local fit
→ choose serving surface
→ harmonize overlap
→ inspect scope / proof / refusal
```

## Testing Decisions

- Test external behavior at the highest useful seam. Prefer command-level and integration-style tests over testing implementation details.
- The first high-value seam is the pack contract and local control-plane behavior around it.
- Test that a valid manual pack contract can compile into expected pack artifacts.
- Test that a draft pack includes metadata, source manifest, generated routing/index surfaces, review notes, and warnings.
- Test that generated routing surfaces preserve scope and non-scope boundaries.
- Test that inferred metadata is marked as inferred and does not masquerade as source-declared metadata.
- Test that a static/local registry can list packs and return a pack by id.
- Test that trust states are represented distinctly for Community, Verified, and Official packs.
- Test that listing eligibility and recommendation eligibility can diverge.
- Test that a local install copies or registers pack artifacts into the installed-pack store without requiring a hosted backend.
- Test that the local serve path exposes pack search/read behavior through the supported serving seam.
- Test that a sample in-scope query returns an answer with at least one exact source citation.
- Test that a sample out-of-scope query refuses or redirects rather than answering from the wrong pack.
- Test that context fit output includes overlap, gaps, conflicts or boundaries, and route recommendation.
- Test that harmonization decisions are represented as explicit choices rather than hidden mutation.
- Test that local-first privacy is preserved: scan, compile, inspect, install, and serve should not require upload or network access in the first slice.
- Test one demo flow end-to-end: open Cookbook, pick pack, see trust/scope, check local fit, install, serve, ask an in-scope question, get a cited answer, ask an out-of-scope question, get a refusal.
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
- Automatic third-party pack trust without human approval.
- Real public pack monetization.
- Large-scale marketplace browsing.
- Replacing source docs with generated summaries.
- Treating `llms.txt` as the entire knowledge source.
- Building prompt-library or Loop Library semantics into the product concept.

## Further Notes

The static prototype passed the initial smell test with Variant C. That means the next work should move from UI prototype to local control-plane proof, not deeper visual polish unless a concrete implementation question needs it.

The quality bar for the MVP is a short demo that works in under five minutes:

1. Open Cookbook.
2. Pick a Knowledge Pack.
3. See why it is trustworthy.
4. Compare local fit.
5. Install or route it locally.
6. Serve it through MCP or another supported surface.
7. Ask an in-scope question.
8. Get a cited answer.
9. Ask an out-of-scope question.
10. Get a refusal or redirect.

The most important product risk is not search. It is trust routing: installing useful knowledge without polluting the user’s existing context or teaching agents to answer outside the pack’s boundaries.

The implementation should stay endpoint-ready, but the first slice should prove local value before adding hosted registry infrastructure.
