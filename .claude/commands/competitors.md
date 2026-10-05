# /competitors - Who Else Sells This, to Whom, at What Price

You are mapping the competition for one or more ideal customer profiles: direct competitors
(same offer, same customer) and substitutes (what the customer does today instead of buying).
The result is one `offering/<slug>/competitors.md` per unit (competitor table, **price band per
market** that `/price-it` reads as its market method, positioning gap, objection map, alerts) plus
the index `08-competitors.md`.

The main thread does not search. It scopes, dispatches **one subagent per ICP**, consolidates,
proposes and writes. Framework files are in English. Conversation and content follow the
blueprint's `content_language`.

---

## Arguments

`$ARGUMENTS` decides the scope:

- One or more ICP ids from `07-icp.md`: `/competitors acme` · `/competitors acme otra-unidad`
- A catalog item name: `/competitors Ciberseguridad` → resolved to the ICP that covers it
- A free prompt in quotes: `/competitors "ATS para agencias pequeñas en Portugal"` → an
  **ad-hoc** run, not tied to an ICP; id = slug of the prompt
- Empty → AskUserQuestion, multi-select over the ICPs in `07-icp.md`, those with `pending` or
  `provisional` rows in `05-pricing.md` first

---

## Step 0: Load & scope

1. No `01-company.md` → *"Run `/setup` first."* Stop.
2. No `07-icp.md` and not an ad-hoc prompt → *"Run `/icp` first: competitors without an ICP is
   a list of names."* Stop.
3. Read `07-icp.md` (the blocks for the ICPs in scope), `02-offering.md` (item definitions and
   sale status), `05-pricing.md` if it exists (current price, `pending` and `provisional`
   rows: the priority), `01-company.md` positioning, `04-voice.md` tone and banned words.
4. If `08-competitors.md` exists: list its runs with dates. A unit already run is a
   **revision**: its `competitors.md` is replaced on write. Read the unit's `unit.md` and
   `pricing.md` for the definition and current price.
5. Markets per ICP come from `07-icp.md`. Services: only markets with a country. SaaS products:
   also `global-en` (their competitors are global). A region without countries is asked once.
6. One AskUserQuestion:

   > **Competitors for [BRAND].** Run for: [unit — market(s)], one line per unit. Depth: search
   > + competitor website (home, pricing, about) + reviews + company size. Up to 10 direct + 3
   > substitutes per unit and market. One agent per product or service, in parallel.

   → `Go` · `Change scope` (free text) · `Only price bands (faster: no reviews, no gap)`.

---

## Step 1: Dispatch (one Agent per unit, in parallel)

The unit is **one product, or one service**. An ICP that groups several services (the quick
`services` ICP) is split: one agent per service, each with the shared ICP block plus its own
item definition and price. Bundles (`Paquetes combinados` or equivalent) get no agent: their
price is a sum of parts; say so. Blocks are written per unit (`## services/consultoria-ia —
Consultoría IA`), so a service can be re-run alone later.

Launch every agent in a single message (`subagent_type: general-purpose`). Each prompt
contains, verbatim:

- The ICP block from `07-icp.md` (firmography, pain, triggers, persona, where to find them).
- The item(s): definition from `02-offering.md`, current price or provisional base from
  `05-pricing.md`, sale status.
- The markets, and the language of each.
- The company's positioning quotes (`01-company.md`) and tone (`04-voice.md`), so the gap is
  written against something real.
- The output schema: the `## <icp-id>` block of `templates/08-competitors.md`, filled, in
  `content_language`, headings in English.
- The rules below.

**Agent rules** (paste them):

1. For each market: WebSearch for direct competitors (same offer, same customer) and for
   substitutes (what the ICP does today instead: a spreadsheet, an intern, a generic tool, a
   category leader). Target up to 10 direct + 3 substitutes per market; fewer is fine if the
   market is thin. Say so.
2. For each candidate: WebFetch home, pricing (or plans) and about — at most 3 pages. Then one
   reviews page (G2, Capterra, Google, Trustpilot) if it exists, and the company's LinkedIn
   page or an equivalent for size. Budget: **~30 fetches per unit** in total (~40 for a SaaS
   with a global market). Spend it on pricing pages first, reviews second, size last: in the
   first real run every agent ran out before LinkedIn, and sizes are the least useful column.
   Stop at the budget.
3. **A price without a URL is not a price.** Not published → `—`. Never estimate. Quote the
   plan name and the unit (per seat, per month, per project).
4. Reviews: score, number of reviews, platform. Absent → `—`.
5. Positioning: one quote in their words, from their home page.
6. Compute the price band per market only over competitors with a public price: n, min,
   median, max, and what the band covers (which models).
7. Positioning gap and objection answers are your inference from what you read: tag them
   `[inferred]`. Do not praise or judge the company; describe the gap.
8. Never copy a competitor's copy as a suggestion for the company.
9. Do not record competitor client names.
10. Return the filled block and nothing else. Every URL you used goes in `### Sources` with
    today's date.

Then wait. Do not search yourself while agents run.

---

## Step 2: Consolidate (per ICP, as each agent returns)

- Deduplicate competitors across markets (same company in ES and global → one row, scope
  "ES, global").
- Every price has a URL, or becomes `—` with a note. Recompute the band if a price was dropped.
- Cross the positioning gap with `01-company.md` positioning and `04-voice.md`: if the gap
  suggests a claim the company never makes (`04-voice.md` "Claims we never make"), remove it
  and say so. Any statement about the company that is **not in the blueprint** (an internal
  use, a hosting location, a certification) is tagged `[verify]` inline and listed in the
  block header: agents infer them from the product page; they are not facts yet.
- Mark `partial` if a market returned no competitors with a price, or if the agent hit the
  budget before covering a market.

---

## Step 3: Propose (per ICP, one message)

```
[icp] — [items] · markets: [..]
Direct: N (ES n · PA n · global n) · Substitutes: N
Price band ES: min–median–max (n=..) · PA: .. · global: ..
Gap: [three short lines]
Top objections: [three]
Alerts: [what to watch]
Partial: [what is missing, or none]
```

AskUserQuestion → `Ok` · `Drop or add a competitor` (free text; adding triggers a small
targeted fetch by a fresh agent) · `Re-run this ICP`.

---

## Step 4: Write

After the last ICP, show the set of runs. AskUserQuestion *"Write `08-competitors.md`?"* →
`Yes, write · review in 3 months (Recommended)` · `Yes · 6 months` · `Change something first`.

On yes, per unit: write `offering/<slug>/competitors.md` from
`templates/offering/competitors.md` (one file per unit; a re-run replaces the file). Then update
the index `08-competitors.md` from `templates/08-competitors.md`: one row per unit run (file,
markets, competitors, run date, status), frontmatter `runs`, `last_run`, `review_by`,
consolidation notes. Ad-hoc runs get `offering/_adhoc/<slug>/competitors.md`. No `[PLACEHOLDER]`
may remain (Grep `\[[A-Z_]{3,}\]`). No other blueprint file changes.

---

## Step 5: Summary

> **Competitors done.** [N] ICPs · [N] competitors · bands for [markets].
> `08-competitors.md` (internal). Partial: [list or none].
> **Next:** `/price-it <item>` now has market data for [pending markets / provisional items].
> `/prospects` and outreach can use the objection map. Alerts due: [review_by].

---

## Safety rules

1. Propose-then-write per ICP; nothing written before `Yes, write`.
2. Price = URL + date, or `—`. Reviews = score + n + platform, or `—`.
3. Substitutes always; global market only for SaaS.
4. One agent per product or service with a fetch budget; the main thread never searches.
5. Gaps and objection answers are `[inferred]` hypotheses; nothing from a competitor becomes
   the company's copy.
6. Internal file: no competitor client names; the company's own prices are not written here.
