# Pixoid Crew Operating Model

The Pixoid crew operates as a set of bounded peer roles coordinated through durable source-of-truth surfaces. Pixoid is the control plane; Tinker builds; Quill maintains vault/source truth; Boba explores public sources and reality-checks signals.

## Operating contract

- GitHub issues and PRs are coordination truth.
- Obsidian/Git is knowledge and project truth.
- Discord is notification, not durable truth.
- Cron output is context, not canonical state.
- Daily Notes are scratch chronology, not compiled truth.

## Why this belongs in agent-workflows

The model is about how work moves through the crew: route selection, source-of-truth checks, memory boundaries, evidence gates, and review. It links to `pixi-vault` where the same rules affect namespace compilation, and to `eval-trace` where workflow quality gets measured.

## Core patterns

1. **Route by source of truth.** Use GitHub for work coordination, Obsidian for knowledge/project truth, skills for procedures, and memory only for compact stable routing facts.
2. **Prefer peer profiles for named crew work.** Use child/subagent execution only as a local fallback and label it honestly.
3. **Verify before closing.** Pixoid checks changed files, tests, live URLs, issue state, and pushed commits before reporting success.
4. **Promote durable learning carefully.** Evidence must justify whether a lesson belongs in a dossier, concept page, skill, prompt, project hub, or memory pointer.