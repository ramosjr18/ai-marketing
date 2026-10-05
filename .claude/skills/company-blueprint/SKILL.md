---
name: company-blueprint
description: >
  The company's single source of truth for marketing: who the company is, what it sells,
  who is behind it, and how it speaks. Load this whenever a task needs a company fact,
  a product or price, a person's role or signature, or the brand voice. Triggers on:
  company, our product, our services, pricing, who we are, founder, owner, team, brand
  voice, tone, banned words, logo, colors, empresa, nuestro producto, servicios, precios,
  socios, equipo, voz de marca, tono.
allowed-tools: Read, Glob, Grep
framework_version: 0.1.0
---

# Company Blueprint

Company-level files `00`-`08` plus one folder per sellable unit under `offering/<slug>/`
(`unit.md`, `icp.md`, `competitors.md`, `pricing.md`). `02`, `05`, `07`, `08` are indexes over
those folders. All populated files are gitignored; `templates/` (including
`templates/offering/`) is what ships. `00-overview.md` is already in context
through `CLAUDE.md`. Load the others one at a time, only the one the task needs.

| Need | File |
|---|---|
| Identity, URL, market, positioning, where a fact came from | `01-company.md` |
| Catalog, proof, flagship, list of units | `02-offering.md` (index) |
| One unit in depth: definition, deliverables, type block, variants | `offering/<slug>/unit.md` |
| What the unit really is past its category, capability by capability, and what can be demonstrated today | `offering/<slug>/product.md` (written by `/product`) |
| What was found wrong with the product or the website, waiting for someone to confirm it | `offering/<slug>/hallazgos.md` |
| One unit's customers · competitors · price rationale | `offering/<slug>/icp.md` · `competitors.md` · `pricing.md` (shared ICPs under `offering/_shared/`) |
| Who does what, who signs outreach, bios, who approves | `03-people.md` |
| Tone, vocabulary, banned words, examples, logo, colors, fonts | `04-voice.md` |
| How one signer writes, and why each rule is there | `tone/<slug>.md` (corrected by `/adjust-tone`) |
| Why a set of messages is going out: objective, slice, angle | `offering/<unit>/campaigns/<slug>/campaign.md` |
| Aggregated rate card, floors, what is public, pricing rules (exists after `/price-it`) | `05-pricing.md` |
| Cost per hour, capacity, overhead, break-even (exists after `/costs`) — **internal, never quote** | `06-costs.md` |
| Which ICPs exist and where (exists after `/icp`) | `07-icp.md` (index) |
| Which competitor runs exist and where (exists after `/competitors`) | `08-competitors.md` (index) |
| One unit's prospects, their status and what was sent (exists after `/prospects`) — **internal** | `offering/<slug>/prospects.csv` · `prospects-runs.md` · `drafts/`; company-wide `offering/_shared/events.csv` · `suppression.csv` (see `templates/offering/README-outreach.md`) |

## Rules when reading

1. **Missing file = not onboarded.** If `01-company.md` does not exist, stop and tell the
   user to run `/setup`. Do not fill the gap from the website or from memory.
2. **Flags gate blocks.** Each file's frontmatter has `sections:`. A block whose flag is
   `false` is absent: do not quote it, do not ask for it. Check the flag before using
   outreach signatures, bios, approvals or visual identity.
3. **`private` is an answer.** A price marked `private` means "do not state a number".
   Say pricing is on request. Prices come only from `05-pricing.md` (or the catalog in
   `02-offering.md`, which mirrors its public part). Never quote a floor, a cost or a margin:
   those lines are internal. No `05-pricing.md` means no prices exist yet: point to `/price-it`.
4. **Inference stays labeled.** Anything under `Patterns observed` or tagged `[Inferred
   from ...]` is a hypothesis. Use it, but never present it to the outside as a company
   statement.
5. **Sources travel with facts.** When you reuse a metric, client name or testimonial from
   `## Proof`, keep the ability to point at its source if asked.
6. **Never write here.** These files change only through `/setup`, `/setup-update`,
   `/price-it` (`05-pricing.md` and the price fields of `02-offering.md`), `/costs`
   (`06-costs.md`), `/icp` (`07-icp.md`), `/competitors` (`08-competitors.md`), `/prospects`
   (`prospects.csv`, `prospects-runs.md`, `events.csv`) and `/outreach` (`drafts/`, status
   fields, `events.csv`, `suppression.csv`).
   If a fact looks stale, say so and point to `/setup-update`.

## Templates

`templates/` holds the placeholder versions, tracked in git. `/setup` copies and fills
them. `templates/offering/` holds the per-unit files; `02-offering.<type>.md` list the fields
each company-type block should carry inside a unit's `unit.md`.
