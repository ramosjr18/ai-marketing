# documents/

Raw source material for `/setup` and `/setup-update`. Everything here is gitignored
except this file: drop real material freely.

| Folder | Put here | Used for |
|---|---|---|
| `web/` | Exports or screenshots of the website, if it cannot be fetched (login, SPA, 403) | `01-company`, `02-offering`, `04-voice` |
| `decks/` | Pitch deck, sales presentations, investor memos | `01-company`, `02-offering` |
| `products/` | Product sheets, one-pagers, catalog, price lists, feature matrices | `02-offering` |
| `people/` | CVs, bios, LinkedIn exports, headshots of owners and team | `03-people` |
| `brand/` | Logo files, brand manual, color palette, font files | `04-voice` (visual block) |
| `content/` | Posts, emails, newsletters, landing copy already published | `04-voice` (tone, vocabulary) |

Formats: `.md`, `.txt`, `.pdf` (read with `pdftotext`), `.png`/`.jpg` (read as images),
`.csv`. Anything else is listed but skipped.

Reading order during setup: `web/ → decks/ → products/ → people/ → brand/ → content/`.
When two documents disagree, `/setup` asks you which one is right; it never picks.
