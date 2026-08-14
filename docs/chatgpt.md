# ChatGPT

Ponytail works in ChatGPT as a skill-first adapter.

ChatGPT and Codex can both use reusable Skills. Ponytail keeps the portable behavior in `skills/`; ChatGPT should consume those skills directly instead of adding a second copy of the ruleset.

## Build uploadable skills

ChatGPT skill uploads are stricter than several CLI hosts: the upload bundle should keep only portable Skill frontmatter and include ChatGPT UI metadata. Build all six upload-ready archives from the canonical `skills/` tree with:

```bash
python3 scripts/build-chatgpt-skills.py
```

This writes one archive per skill under `dist/chatgpt/<skill>/skill.zip`.

The builder intentionally does not mutate the canonical skills. It:

- keeps `name` and `description` in `SKILL.md` frontmatter;
- strips host-specific frontmatter such as `argument-hint` and `license` from the ChatGPT copy;
- adds `agents/openai.yaml` with a display name;
- preserves any bundled references, scripts, and assets;
- verifies the required files and the 25 MiB upload limit.

## Install

In ChatGPT web or desktop, open **Plugins** → **Skills** and upload whichever generated `skill.zip` archives you want:

- `dist/chatgpt/ponytail/skill.zip`
- `dist/chatgpt/ponytail-review/skill.zip`
- `dist/chatgpt/ponytail-audit/skill.zip`
- `dist/chatgpt/ponytail-debt/skill.zip`
- `dist/chatgpt/ponytail-gain/skill.zip`
- `dist/chatgpt/ponytail-help/skill.zip`

A workspace plugin can package the same skills without an app dependency; do not add an MCP server just to carry instructions.

Personal Skills are installed separately on ChatGPT surfaces. Installing Ponytail in Codex does not automatically install the personal Skill in ChatGPT.

## Invoke

ChatGPT may auto-select an installed Ponytail skill when its description matches the task. Explicit invocation is also useful when you want deterministic activation:

```text
@ponytail full
@ponytail ultra
@ponytail-review
```

Use `lite`, `full`, or `ultra` in the prompt to choose intensity. `full` remains the default defined by the core skill.

## Lifecycle behavior

ChatGPT does not expose Ponytail's Codex lifecycle-hook contract to uploaded Skills. In particular, do not assume that these Codex events run in ChatGPT:

- `SessionStart`
- `UserPromptSubmit`
- `SubagentStart`

That means the ChatGPT adapter is intentionally **skill-tier**, not hook-tier:

- no shell hook runs on every user prompt;
- no hook-backed `PONYTAIL_DEFAULT_MODE` state injection;
- no hook-backed subagent injection;
- no Ponytail statusline integration.

The installed `ponytail` Skill still carries the core behavior and its activation language. Mode changes such as `@ponytail ultra` are conversation instructions, not a persisted hook-state file. Start a new chat or explicitly select a mode when deterministic state matters.

## Adapter rule

Keep this adapter thin. The source of truth remains `skills/`. If ChatGPT gains a lifecycle API equivalent to the Codex hook events, add a host adapter that calls the existing shared hook/instruction machinery rather than forking the ruleset.
