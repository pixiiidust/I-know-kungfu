# Cookbook Serving Prototype Notes

Status: throwaway UI smell test. Do not promote directly to production.

## Prototype question

Does the Cookbook serving flow feel understandable before we build the CLI/backend?

## Run command

```bash
python3 -m http.server 4173 --directory prototype/cookbook-serving
```

Then open:

```text
http://127.0.0.1:4173/
```

## What is fake

- Real backend.
- Real auth, payments, upload, or marketplace browse.
- Real MCP process.
- Real local inventory scan.
- Real package install/copy actions.
- Real search infrastructure.

## What this prototype should visually prove

- What a knowledge base wiki detail view shows.
- How Community, Verified, and Official trust badges read in the flow.
- How scope and non-scope are exposed before use.
- How a candidate wiki compares against local inventory: overlap, gaps, and routing recommendation.
- How the user chooses a serving entry point: MCP, `llms.txt`, raw Markdown, or `index.json`.
- How copyable setup/config blocks appear.
- Where a sample cited answer appears.
- Where an out-of-scope refusal appears.

## Synthetic demo data included

- Agent Workflow Setup Wiki — Verified, high-confidence route.
- Terminal Setup Wiki — Official, narrow source-owned route.
- MCP Basics Wiki — Community, findable but review first.
- Local Model Serving Wiki — Community, quarantined due to mixed provenance.

The prototype also fakes a local inventory scan: 428 notes, 7 installed wikis, and overlap/gap/confidence/risk fields for each pack.

## Interactions now wired

- Search filters packs by name, maintainer, route, summary, and topic keywords.
- Trust chips filter by All / Community / Verified / Official.
- Selecting a pack updates fit, setup commands, harmonize diffs, scope/non-scope, cited answer, and refusal copy.
- Surface buttons update the copyable setup block for MCP, `llms.txt`, raw Markdown, or `index.json`.
- Copy buttons show a small toast after writing setup text to the clipboard.

## Visual direction

Adapted the dense editorial/database feel Jamie pointed to from Forward Future Loop Library:

- light mode default with off-white background, black text, white table surface, and red-orange accent;
- dark mode toggle with near-black background, off-white text, dark table surface, and the same red-orange accent;
- sharp rectangular controls;
- thin rules instead of soft cards;
- uppercase metadata labels;
- compact table/list records;
- semi-bold sans-serif headings instead of heavy oversized display type.

## Current smell-test read

Jamie chose Variant A as the surface to solidify first. The prototype now removes the A/B/C switcher and defaults to the single Library flow:

```text
Hero
→ selected wiki setup panel
→ four-step flow rail
→ searchable/filterable wiki rows
→ detail / serve / proof
```

The selected-wiki setup panel uses a light surface instead of the red-orange accent background. The accent now acts as a small inset marker so the container does not clash with the text/code block.

Product-copy correction from Jamie: this is not about Loop Library-style prompts. The relevant similarity is the community-sharing/listing approach. The actual product frame is finding useful knowledge base wikis to add to your own knowledge base, comparing local fit, serving through a chosen entry point, and harmonizing/integrating diffs when the new wiki overlaps with existing knowledge.

Light mode is the default; top nav includes a Dark toggle for checking the dark palette. Typography was softened after Jamie feedback: smaller headings, sans-serif semibold weights, cleaner spacing, and less oversized bold display type.

Forward Future Loop Library design cues used:

- same light/dark color scheme sampled from the live page:
  - light bg `#faf8f7`, ink `#101010`, surface `#ffffff`, accent `#ff5033`, muted gray `#5f666b`;
  - dark bg `#101010`, surface `#1b1b1a`, ink `#faf8f7`, accent `#ff5033`, muted gray `#a8aaa4`;
- one wide content rail;
- large editorial hero;
- oversized accent callout block;
- dense table/list rows instead of separate cards;
- tiny uppercase monospace metadata;
- sharp rectangular controls;
- thin horizontal rules;
- muted body copy with strong title scan anchors;
- small consistent action buttons.

Current design direction: continue from Variant A as the chosen surface. Older Variant C references are historical smell-test context only; do not restore the A/B/C switcher unless Jamie explicitly asks for alternate surfaces again. Keep the Forward Future light/dark color scheme, but avoid copying product language about loops/prompts.
