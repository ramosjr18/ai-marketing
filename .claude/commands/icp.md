# /icp - Ideal Customer Profile per Product

You are defining who each product or service is for. Not "SMEs": the sector, the size in the
item's own unit, the pain in the customer's words, what makes them buy now, who signs, where
they can be found, and who to avoid. The result is one `icp.md` per unit under `offering/<slug>/` (or one shared file per group
under `offering/_shared/`), with a section per active market, plus the index `07-icp.md`. `/competitors`, `/value-case` and everything
about prospects and copy read it.

Framework files are in English. Conversation and content follow the blueprint's
`content_language`.

---

## Interaction rules

- **One question per message.** Closed questions through AskUserQuestion, recommended option
  first. Free text only for descriptions and names.
- **Propose, then ask.** Whenever the product or the real clients let you draft an answer,
  show the draft labeled `[inferred from product]` and ask to confirm, instead of asking from
  scratch. The owner corrects better than they invent.
- **`no sé`, `ninguno`, `luego` are valid.** `luego` leaves the ICP partial and moves on.
- **Labels everywhere.** `[stated]` only for what a real client or the owner said.
  `[inferred from product]` for deductions. `[Benchmark]` with URL and year for anything found.
- **Idempotent per ICP.** Existing ICPs are shown and reopened only on request.

---

## Step 0: Load & mode

1. No `01-company.md` → *"Run `/setup` first."* Stop.
2. Read `01-company.md` (geography, sectors), `02-offering.md` (catalog, sale status, "for
   whom", features), `05-pricing.md` if it exists (markets per item, past sales).
3. If `07-icp.md` exists: list its ICPs with status; AskUserQuestion *"What do we do?"* →
   `Reopen one` · `Add an ICP` · `Switch to complete mode` · `Just review`. Reopening jumps to
   Step 1 for that ICP.
4. Otherwise AskUserQuestion *"How detailed?"* →
   - `Quick (Recommended)`: one ICP per product, one shared ICP for all services.
   - `Complete`: one ICP per catalog item. Long; can be done later on top of quick.
5. Build the ICP list from the catalog. Items not for sale are included and marked: the ICP
   decides who to show them to. Show the list, numbered, and start with 1.

---

## Step 1: Per ICP, in this order

Header every message with `[N/total] <id> — <items>`.

### 1.1 Markets
If `05-pricing.md` gives markets for the item(s), take them. Otherwise AskUserQuestion
*"Where is this sold or going to be sold first?"*, multi-select, blueprint geography first,
plus Other.

### 1.2 Real clients
*"Who has bought this, or something like it? A friend counts."* One per message, free text:
who or type, sector, size, why they bought (their words), how they found you, price if known.
`ninguno` is valid. Names go in the file only if already public in `02-offering.md`;
otherwise "Client A".

Past sales from `05-pricing.md` that match this item are shown here first for confirmation.

### 1.3 Draft from the product
Draft **Firmography** and **Pain** from what the item does (`02-offering.md`: description,
features, "for whom") and from the real clients. Show both blocks compactly, labeled
`[inferred from product]`. AskUserQuestion *"Does this match?"* → `Yes` · `Adjust` (free text
next) · `Very different, I'll describe it`.

### 1.4 Market search
Per active market **with a country**, **3-5 WebSearch queries**, no output until done. A
market like "global" or "English-speaking" has no measurable segment: skip the search for it,
say so once in the file header, and keep it only as a label in `markets`. If a region is named
without countries (e.g. "Latam"), ask which countries before searching. size of the segment (how
many such companies/listings/studios in that country), how they buy this kind of thing, where
they gather (portals, associations, events), who decides, typical budget. Every figure with
URL and year, tagged `[Benchmark]`. Nothing found → `—`, said plainly. Results feed 1.5-1.8
and the Per-market block; they are never presented as facts about the company or its clients.

### 1.5 Decision persona
Propose role, influencers, what they care about, how they speak, 3-4 objections, budget range
(`[Benchmark]` if found, `[stated]` if a real client gave it, `—` otherwise). AskUserQuestion
`Yes` · `Adjust`.

### 1.6 Triggers
Propose 4-5 events that make this customer buy now. AskUserQuestion, multi-select, plus Other.

### 1.7 Where to find them
Propose channels, search filters/keywords and visible signals, drawn from the search and the
product. AskUserQuestion, multi-select, plus Other. This block is what `/prospects` will run
on: be concrete (a portal name, a LinkedIn title filter, a Google query), not "social media".

### 1.8 Anti-ICP
Propose 3-5 signs of a bad client for this item (too small for the recurring cost, nobody owns
the process, wants it free, needs what the item excludes). Multi-select, plus Other.

`luego` at any sub-step → ICP status `partial`, note what is missing, next ICP. A closed
question left unanswered is asked once more, briefly; unanswered again, it becomes a
`**Missing:**` line and the ICP is `partial`. Never fill it yourself.

---

## Step 2: Propose (per ICP)

One screen: sector · size · pain in one line · top 2 triggers · persona · 3 channels ·
anti-ICP · markets with segment size. Labels visible. AskUserQuestion *"Good?"* → `Ok, next` ·
`Change something`. Iterate until ok.

---

## Step 3: Write

After the last ICP, show the set: ids, items, markets, status. AskUserQuestion *"Write
`07-icp.md`?"* → `Yes, write` · `Change something first`. `review_by`: default today + 6
months, offered in the same question.

On yes: one file per ICP from `templates/offering/icp.md`. An ICP that covers one unit goes
to `offering/<slug>/icp.md`. An ICP shared by several units (quick mode: the services group)
goes to `offering/_shared/<group>-icp.md`, and each covered unit gets a short pointer
`offering/<slug>/icp.md` (frontmatter `shared`, `file`). Then update the index `07-icp.md`
from `templates/07-icp.md`: frontmatter `mode`, `icps` (id, items, markets, status),
`last_icp`, `review_by`, and one row per ICP with its file. Partial ICPs keep a `**Missing:**`
line under their heading. Remove rows and sub-blocks with no data. No `[PLACEHOLDER]` may
remain (Grep `\[[A-Z_]{3,}\]`). No other blueprint file changes.

---

## Step 4: Summary

> **ICPs done ([quick/complete]).** [N] complete · [N] partial. Markets: [list].
> Internal file: `07-icp.md`. Real client names stay internal.
> **Next:** `/competitors` reads these profiles; `/price-it` shows the persona's budget as a
> value hint. Run `/icp` again to add an ICP, complete a partial one, or switch to complete mode.

---

## Safety rules

1. Propose-then-write: nothing is written before `Yes, write`.
2. Labels are mandatory. Only a real client or the owner produces `[stated]`.
3. Client names: public in `02-offering.md`, or anonymous. This file is internal.
4. Search is capped (3-5 queries per ICP and market) and sourced. No source, no figure.
5. Nothing invented about customers: an unconfirmed draft stays a draft with its label.
6. Generic: the "size" unit follows the item (employees, listings, vacancies, projects, orders).
