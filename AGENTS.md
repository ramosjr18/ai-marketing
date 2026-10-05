---
framework_version: 0.1.0
---

# Agent Guidelines: AI Marketing

This workspace holds one company's marketing brain: who the company is, what it sells,
who is behind it, how it speaks, and the workflows that use that knowledge (prospecting,
copy, campaigns).

## Thin-Pointer Design (Single Source of Truth)

To avoid duplication and drift across agent runtimes (Claude Code, Codex, Cursor, Gemini
CLI...), this file points and does not duplicate. All runtimes load from:

1. **Company blueprint** — [CLAUDE.md](CLAUDE.md) (repo rules + one-screen overview) and
   the detail files under [.claude/skills/company-blueprint/](.claude/skills/company-blueprint/)
   (`01-company.md`, `02-offering.md`, `03-people.md`, `04-voice.md`). The populated files
   are gitignored; the templates under `templates/` are what ships.
2. **Workflows** — every slash command under [.claude/commands/](.claude/commands/) is the
   canonical procedure. Do not restate these rules elsewhere.
3. **Source material** — [documents/](documents/) holds raw inputs (decks, product sheets,
   brand assets). Read-only for workflows; only `/setup` and `/setup-update` consume it.

If a blueprint file is missing, the company has not been onboarded: run `/setup`.
