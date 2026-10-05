# /price-it - Define and Price the Offering

You are pricing a company's catalog. Item by item, you close two gaps `/setup` leaves open:
**what exactly** each service or product is (scope, deliverables, duration) and **what it
costs**. The result is a reasoned rate card in `05-pricing.md` and an updated catalog.

This touches money. Nothing is written without an explicit `ok` per item **and** approval of
the whole set. Read `## Safety rules` before starting.

Framework files are in English. Conversation and content follow the blueprint's
`content_language`.

---

## Interaction rules

These matter as much as the steps. Long static questionnaires exhaust people.

- **One item, or one question, per message.** Never batch questions across items.
- **Closed questions are interactive.** Whenever the answer is a choice (for sale?, ok/other/skip,
  public?, pricing model, which item next, confirm inputs), use the AskUserQuestion tool with
  the options listed in the step, the recommended one first. Free text is only for open
  answers (a definition, a figure, a deliverables list). The user always has "Other" to type
  something else.
- Show progress: `[3/11] <item>`.
- `skip`, `luego` (later) and `no sé` (don't know) are valid answers at any point. Record the
  gap, move on, never guess.
- Show what you already have and ask to confirm, instead of asking from scratch.
- The user can jump: *"go to 7"*, *"only the SaaS"*. Follow.
- Idempotent: items already priced in `05-pricing.md` are shown with their price and reopened
  only on request. Stopping halfway and running again resumes where it stopped.

---

## Step 0: Load

1. If `.claude/skills/company-blueprint/01-company.md` does not exist: *"Run `/setup`
   first."* Stop.
2. Read `02-offering.md` (catalog index) and each unit's `offering/<slug>/unit.md`. Build the
   item list from the catalog (one item per row; the `Units` table gives the slug).
   **Where `offering/<slug>/product.md` exists, it is the definition, not `unit.md`.** `unit.md`
   carries the one-liner `/setup` took from the website, which is the category the product falls
   into. Pricing a category prices the wrong thing: a price closed against «an ATS with AI»
   stops making sense the day the study finds a conversational assistant with configurable
   criteria serving several clients at once. Read §A, §B and §E; §E is a hard limit,
   since what is in beta is not what is being sold.
   Read `offering/<slug>/hallazgos.md` too, and **name any finding that touches price** before
   asking anything.
3. If `05-pricing.md` exists, this is a **revision run**: load rate card, not-for-sale list,
   partially-defined list, inputs used and `review_by`.
   **A price already in the file is a hypothesis to re-derive, never an input.** Two traps, both
   real in this repo on 2026-09-21:
   - `pricing.md` cites `competitors.md` as market evidence while `competitors.md` validated that
     same figure in its price band. Read as evidence, that is the command agreeing with itself.
   - A row marked `definitive` gets reopened like any other when the definition it was priced
     against has changed. Say so out loud: *"el precio X se cerró el DATE contra esta definición,
     que ya no es la del producto"*.
4. If `03-people.md` has `approvals: true`, note who approves pricing: that name goes into
   the discount rule later.
5. `$ARGUMENTS`: optional item name or number → price only that item. Otherwise all.
6. Opening message, in the content language:

   > **Pricing [BRAND].** [N] items in the catalog:
   >
   > 1. [Item] — [no price | private | X | not for sale since DATE (reason) | partially defined]
   > 2. ...
   >
   > We go one at a time. Start with 1, or tell me which.

   On a revision run also say: *"Inputs from [date]: cost/hour [R], margin [M]%. Still valid?"*
   and wait, since every price below depends on them.

---

## Step 1: Triage (per item, one message)

When `02-offering.md` already states the sale status of every item (a "for sale / not for
sale" line or per-item status), triage in **one** message: list the statuses and ask to
confirm, plus one multi-select for which not-for-sale items get a `target` price. Fall back to
per-item triage only for items whose status the blueprint does not know.

Per item, AskUserQuestion: *"[N/total] [Item]. Is it for sale today?"* with options:
`Yes, price it` · `No, not for sale` (beta, testing, restructuring, discontinued) ·
`Target price only` (not sold yet, internal figure). Put the item's current catalog line in the
question so the user does not need to remember it.

- `no` → ask the reason in the same breath if not obvious from the catalog. Record in
  **Not for sale** with reason and today's date. Next item. No further questions.
- `target` → continue, but every price for this item is labeled *target* and it never goes
  to `02-offering.md` as a selling price.
- `yes` → Step 2.

---

## Step 2: Define (only if the item lacks a definition)

An item is defined when the catalog or the type block has: what it includes, deliverables,
typical duration (services) or plan structure (products), and exclusions. If all four exist,
show them in one line and ask *"Still accurate?"*. Otherwise, one question per message:

1. *"In one sentence, what does [Item] include?"*
2. *"What does the client actually receive?"* (deliverables, concrete)
3. Services: *"Typical duration?"* (free text). Products: AskUserQuestion *"How are plans
   structured?"* with options `Single price` · `Tiers` · `Per seat` · `Usage-based`, multi-select,
   then free text for what changes between tiers.

**The unit of sale comes before any number, and it is the owner's call.** What is being charged
for: a seat, a module, an active vacancy, the account? Ask it plainly whenever the product says
one thing and the file says another. A blueprint saying «flat per-seat subscription» while the
product's own hub says «activa solo lo que necesitas, paga por uso» and prices two modules per
module and seat is the normal case, not the rare one. Those are two different businesses, and no amount of benchmarking settles
which one it is.
4. *"What does it explicitly NOT include?"*
5. **Target market for this item**, always, even when the rest was already defined:
   AskUserQuestion *"Where is [Item] sold today?"* with the markets already in the blueprint
   first (`01-company.md` geography, earlier items), plus Other, multi-select. The market is
   **per item**, not per company: one product may start in one country and another elsewhere,
   and a company with no seat is not tied anywhere. It sets the currency and the benchmark
   geography for this item in Step 4.

`luego` at any point → the item goes to **Partially defined** with what is missing. It is not
priced until completed. Move to the next item.

---

## Step 3: Inputs (once per run, not per item)

**If `06-costs.md` exists**, do not ask: read cost per billable hour, billable hours per month,
per-item recurring costs and suggested margin from its Results and show them in one message:
*"From `/costs` ([date], [quick/refined]): cost/hour [R], [H] billable h/month, margin suggested
[M]%. Use these?"* → AskUserQuestion `Yes` · `Adjust` · `Re-run /costs first`. Only the
reference case and currency remain to ask. If it does not exist and the user answers `no sé` to
the cost question, say once: *"`/costs` walks you through it in five minutes and I'll pick it
up here."* and continue with the methods that remain.

Otherwise ask **one per message**, as free text with an explicit *"or `no sé`"*. Each `no sé` disables the
method that needs it; say so briefly. The payback rule and the currency are closed questions:
AskUserQuestion with the published value (or 12 months) first.

| Input | Enables |
|---|---|
| Target cost per hour, or team monthly cost + hours | cost + margin |
| Available hours per month | capacity check, minimum engagement |
| Target margin (%) | cost + margin |
| Recurring costs per item (models, infra, licenses), if any | cost + margin (floor) |
| A reference client case: what it costs them today or hours it saves | value |
| Default currency (the item's market may override it) | all |

**Past sales**, always, as the first input: *"Have you already sold any of this, at any price?
Even to a friend."* One sale per message: item, client type, price, hours if known, why that
price. Each goes to `## Past sales` in `05-pricing.md` with its bias noted, and appears next to
the methods in Step 5 for the same item (*"Past: 800 € to an acquaintance, ~N h"*). A real sale
below the floor is not a floor; it is evidence of how far the market or the relationship pulled.

Payback rule: if the company already publishes one (blog, web, `02-offering.md`), propose it:
*"You publish 'pays for itself in 18 months'. Use 18 as the value rule?"* Otherwise propose 12
and ask.

Ask inputs **after** the first item is triaged and defined, so the user sees why they are
needed. On a revision run, skip inputs already confirmed in Step 0.

---

## Step 4: Calculate (per item, silent until the numbers exist)

Use every method the inputs allow. State it plainly when only one leg is available.

- **Cost + margin.** Propose an hours estimate from the definition (*"I estimate 40 h:
  20 discovery, 15 build, 5 handover. Correct me."*). Wait. Then
  `hours × cost/hour + recurring = cost` → that is the **floor**. `cost × (1 + margin)` = price.
  For subscriptions: recurring cost per client per month is the floor.
- **Value.** `annual saving × payback_months / 12` = maximum defensible price. Needs the
  reference case; otherwise skip. If `07-icp.md` exists, the decision persona's budget for this
  item is shown next to it as a hint (`[Benchmark]` or `[stated]`, as recorded there), never as
  the value figure itself.
- **Market.** In order: the unit's `offering/<slug>/competitors.md` if it exists (index in
  `08-competitors.md`); `documents/market/` if it has files;
  else WebSearch, **at most 8 queries per item**, in the **item's own market(s)** and currency
  from Step 2. An item sold in several markets gets a benchmark range **per market**, and in
  Step 5 a proposal per market: prices may differ by country. Ask once whether to keep a
  single price across markets or one per market (closed question); one row per market either
  way, so a market can be repriced later without touching the others.
  If the user answers a market with "depends on the local market" or the benchmark for a
  country is weak (one source, no prices), offer once to mark **that country as `pending`
  for all remaining items** until `/competitors` runs there; the rate card keeps one
  `pending` row per item and market so nothing is forgotten.
  When the user wants to wait for `/competitors` before deciding a price, keep the proposed
  base and mark the row **provisional**: the number exists, the decision does not.
  Collect ranges, not point estimates. Every figure with URL and date, tagged
  `[Benchmark — not a company fact]`. Do not fetch competitor pages beyond what a search
  result shows unless one result is clearly a public price page. If `/competitors` exists
  in `.claude/commands/`, mention it once as the deeper option.

Products with tiers: run the calculation per tier. Packs/bundles: sum of parts minus the
bundle discount the user chooses; the floor is the sum of floors.

---

## Step 5: Propose (per item, one message)

```
[N/total] · ITEM · MODEL · market: COUNTRY(IES)
Cost + margin:  X       (H h × R/h + recurring; margin M%)   → floor S
Value:          up to Y (saves Z/year, payback P months)
Market:         A–B     (3 sources)
Past sales:     X       (client type, hours, note)   ← only if any

Proposal: **PRICE · model** · floor S · on request
```

Then AskUserQuestion: *"Take it?"* with options `Ok, PRICE` · `Another figure` (then free text) ·
`Skip for now`. If more than one pricing model fits the item (e.g. fixed vs retainer), ask the
model first, same tool, before showing numbers.

- Default visibility is **on request**. Ask visibility **once, at the end**, for the whole
  rate card (`nothing public` · `only <flagship>` · `services public, products on request` ·
  pick items), unless the user asks for an item to be public while pricing it.
- Another figure below the floor → *"That is under the floor (S). Selling below cost. Confirm?"*
  Write it only on a second yes, and record it as below-floor in the rationale.
- After the last item, the **global rules**, one per message. Payment terms and quote validity
  are closed (AskUserQuestion with 3-4 common options, e.g. `50/50` · `100% upfront` · `Monthly` ·
  `Net 30`); minimum engagement and discount range are free text; the discount approver comes
  from `03-people.md` when `approvals` is on, otherwise a closed pick among the team.
- Then the **flagship**: AskUserQuestion *"Which item do you lead with when someone asks what
  [BRAND] does?"* with the priced items as options, your proposal first with why.

---

## Step 6: Write (approval of the whole set)

Show the complete rate card as a table, the not-for-sale list, the partially-defined list,
the global rules, the flagship, and:

- **Changes in `02-offering.md`**: which catalog rows change price, which block fields get
  deliverables/duration, `pricing_public` new value, flagship.
- **Changes in `00-overview.md`**: the Offering lines that will be regenerated.
- **Changes to publish**: any published price (website, blog, deck) that the new rate card
  contradicts. `/price-it` never edits those sources.

AskUserQuestion: *"Write `05-pricing.md` and update the catalog?"* with `Yes, write` ·
`Change something first` (then free text).

Only on `yes`:

1. **`offering/<slug>/pricing.md`** per priced unit, from `templates/offering/pricing.md`:
   its rate-card rows, the full rationale (definition, hours, methods with sources, past sales,
   decision per market). A re-run of one unit replaces only its file.
2. **`05-pricing.md`** from `templates/05-pricing.md`: the aggregated rate card (all rows), not
   for sale, partially defined, past sales, global rules, inputs used, changes to publish. The
   Rationale section is a pointer to the unit files. Frontmatter: `currency`, `pricing_public`,
   `payback_months`, `review_by` (default: today + 6 months, ask if the user prefers another),
   `last_priced` = today. No `[PLACEHOLDER]` may remain.
3. **`02-offering.md`** (index), surgical edits only: `Price` column of the catalog (public
   price, range, `on request`, or `private`; never floors or costs), `pricing_public` in the
   frontmatter, `**Flagship:**` line. Deliverables, duration, exclusions and variants go to the
   unit's `offering/<slug>/unit.md` (Deliverables and Variants sections). Do not touch anything
   else, including fields you cannot parse.
4. **`00-overview.md`**: regenerate the `## Offering` block and the flagship line from 01-05.
   Nothing else in the file changes.
5. Re-read every written file and confirm no placeholder remains (Grep `\[[A-Z_]{3,}\]`).

---

## Step 7: Summary

> **Pricing done.** [N] priced · [N] not for sale · [N] partially defined.
> Rate card: `05-pricing.md` (internal: floors, costs, margins). Catalog and overview updated.
> Public prices: [list or "none; everything on request"].
> Review by: [date].
> **Changes to publish:** [list or none].
> Run `/price-it` again to revise, `/price-it <item>` for one item[, `/competitors` for a deeper
> benchmark].

---

## Safety rules

1. No price is written without `ok` on the item **and** `yes` on the whole set.
2. The floor is never crossed silently. Below-floor needs a second explicit confirmation and is
   recorded as such.
3. Benchmarks are labeled and sourced. A market figure is never presented as a company fact,
   here or downstream.
4. Sensitive inputs (cost/hour, margins, floors) live only in `05-pricing.md`. Never in the
   catalog, never in the overview, never in outgoing copy.
5. `pricing_public: false` by default. Publishing is an explicit, per-item decision.
6. External sources (website, blog, decks) are never edited. Contradictions are listed.
7. An item not for sale gets no selling price. `target` prices are labeled and stay internal.
8. Nothing invented: no hours estimate, saving or benchmark without either the user's word or a
   cited source.
