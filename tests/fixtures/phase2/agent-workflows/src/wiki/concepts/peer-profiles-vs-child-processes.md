# Peer Profiles vs Child Processes

## Definition

Jamie's named crew agents are **peer Hermes profiles by default**, not Pixoid-owned child processes.

Peer profiles have their own identity surface, memory boundary, tool configuration, and route evidence. Child processes or `delegate_task` subagents are temporary workers inside the current session; they can analyze, draft, or review, but they do not prove that a named peer profile executed work.

## Current synthesis

Use the distinction this way:

| Execution shape | Use it for | Do not use it for |
|---|---|---|
| Peer Hermes profile | Named crew execution with profile identity, credentials, memory boundary, route logs, and durable audit requirements. | Fast in-session synthesis when no real profile route is needed. |
| Child/subagent process | Local read-only research, drafting, compatibility review, or linting that Pixoid will synthesize and verify. | Claiming "Tinker/Quill/Boba did this," persistent route proof, profile-specific credentials, or live side effects. |

Pixoid remains the control plane: clarify scope, route work, verify output, and report to Jamie. Named peers may execute bounded work when an agent-capability-route-pattern exists and current authorization allows it.

## Application

Before saying a named peer did work, verify route evidence:

1. requested profile;
2. actual profile;
3. route trigger or handoff;
4. output artifact;
5. verification proof;
6. Pixoid review or closure comment.

If those are absent, describe the work as child-subagent analysis, local synthesis, or Pixoid-authored output.

## Boundaries

- Do not trigger Quill, Boba, Tinker, or recursive worker chains from a concept page or Documentation Hygiene note.
- Do not treat persona wording, a child-agent summary, or a simulated viewpoint as live peer-profile execution.
- Do not route one worker profile directly into another unless an explicit route contract authorizes that chain.
- Do not let profile memories bleed across profiles; use profile-memory-boundaries and runtime-memory-knowledge-routing to choose the correct layer.
- Do not use child agents for durable side effects that require named accountability unless Pixoid verifies the resulting artifact independently.