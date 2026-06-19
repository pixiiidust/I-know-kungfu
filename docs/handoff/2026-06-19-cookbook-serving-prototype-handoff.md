# Pixoid: Handoff — Cookbook Serving Prototype

Date: 2026-06-19
Repo: `/root/hermes-workspace/I-know-kungfu`
Status: throwaway prototype in progress, not committed

## What changed

Created and iterated a static UI smell-test prototype at:

```text
prototype/cookbook-serving/
  index.html
  NOTES.md
```

Run command from repo root:

```bash
python3 -m http.server 4173 --directory prototype/cookbook-serving
```

Open locally on the machine running the server:

```text
http://127.0.0.1:4173/
```

If viewing from a local desktop while the server runs on a VPS, use an SSH tunnel from the desktop:

```bash
ssh -N -L 4173:127.0.0.1:4173 root@<vps-host>
```

Then open:

```text
http://127.0.0.1:4173/
```

## Prototype question

Does the Cookbook serving flow feel understandable before building the CLI/backend?

## Current chosen direction

Jamie likes Variant C best.

Default behavior now uses Variant C when no `?variant=` is provided:

```text
http://127.0.0.1:4173/
http://127.0.0.1:4173/?variant=C
```

Other variants remain available for comparison:

```text
http://127.0.0.1:4173/?variant=A
http://127.0.0.1:4173/?variant=B
```

Variant C direction:

```text
Find useful wiki/pack
→ check local fit
→ choose serving surface
→ harmonize diffs when overlap exists
→ show scope/proof/refusal below
```

## Important copy correction

Do not frame I-know-kungfu as “like Loop Library prompts.”

The useful comparison to Forward Future Loop Library is the community-sharing/listing interface pattern, not the product concept.

Use this product frame instead:

> Find useful wikis to add to your knowledge base, compare local fit, serve through the right surface, and harmonize diffs when the new pack overlaps with what you already know.

Current UI lead copy:

> Find useful wikis to add to your knowledge base, compare local fit, serve through the right surface, and harmonize diffs when the new pack overlaps with what you already know.

## Visual direction

Jamie asked to use the same light/dark color scheme as:

```text
https://signals.forwardfuture.ai/loop-library/
```

Sampled colors now used:

Light mode:

```text
background: #faf8f7
text:       #101010
surface:    #ffffff
accent:     #ff5033
muted:      #5f666b
```

Dark mode:

```text
background: #101010
surface:    #1b1b1a
text:       #faf8f7
accent:     #ff5033
muted:      #a8aaa4
```

Jamie also prefers:

- clean minimal UI;
- intuitive sequenced flow;
- table/list layout, not card piles;
- sans-serif semi-bold typography;
- avoid oversized/heavy bold headings.

## Scope boundary

This remains a throwaway UI prototype.

Fake:

- backend;
- auth;
- payments;
- upload;
- real MCP process;
- real local inventory scan;
- real install/copy actions;
- real search infrastructure.

Visually prove:

- pack/wiki listing and detail shape;
- trust/status badges: Community, Verified, Official;
- scope and non-scope;
- local context fit: overlap, gaps, routing recommendation;
- serving surfaces: MCP, `llms.txt`, raw Markdown, `index.json`;
- copyable setup/config blocks;
- sample cited answer;
- out-of-scope refusal;
- harmonize/integrate diffs concept when overlap exists.

## Static data currently included

- Agent Workflow Setup Pack — Verified.
- Terminal Setup Pack — Official.
- MCP Basics Pack — Community.

These are placeholder static data. Future iteration can rename/reframe them as “wiki packs” more explicitly if needed.

## Verification done

- Prototype server was running on port 4173.
- Browser loaded `http://127.0.0.1:4173/?variant=A` successfully during iteration.
- A/B/C variant switcher worked.
- Fresh reload verified light mode default.
- Dark mode toggle verified.
- Computed colors matched the Forward Future palette after update:
  - light bg `rgb(250, 248, 247)`;
  - light text `rgb(16, 16, 16)`;
  - light table `rgb(255, 255, 255)`;
  - accent `rgb(255, 80, 51)`;
  - dark bg `rgb(16, 16, 16)`;
  - dark table `rgb(27, 27, 26)`.
- Browser visual checks showed no obvious layout breakage.

## Current git state

No commit was made.

Expected git status:

```text
?? prototype/
?? docs/handoff/2026-06-19-cookbook-serving-prototype-handoff.md
```

Depending on timing, `prototype/cookbook-serving/index.html` and `prototype/cookbook-serving/NOTES.md` may appear under untracked `prototype/`.

## Suggested skills for next session

Load:

- `prototype` — UI branch, because this is a throwaway UI smell test.
- `verb-first` — for product copy cleanup.
- `domain-modeling` — only if new domain terms need to be captured in `CONTEXT.md`.
- `handoff` — only if continuing into another session.

## Short handoff prompt for a fresh session

```text
Pixoid: Continue the I-know-kungfu Cookbook serving UI prototype.

Repo: /root/hermes-workspace/I-know-kungfu

First read this handoff doc:
docs/handoff/2026-06-19-cookbook-serving-prototype-handoff.md

Then inspect live state with git status and read:
- CONTEXT.md
- docs/research/2026-06-19-brainstorm.md
- prototype/cookbook-serving/NOTES.md
- prototype/cookbook-serving/index.html

Load skills: prototype, verb-first. Use domain-modeling only if new terms need to be captured.

Continue from Variant C as the preferred direction. Keep the Forward Future Loop Library color scheme, but do not copy its “loop prompt” product framing. The product frame is: find useful wikis to add to your knowledge base, compare local fit, serve through the right surface, and harmonize diffs when overlap exists.

Do not build backend/auth/payments/upload/real MCP/search. This is still a static throwaway UI smell test. Do not commit unless Jamie asks.

Run and verify with:
python3 -m http.server 4173 --directory prototype/cookbook-serving

Report what changed and what browser/HTTP verification returned.
```
