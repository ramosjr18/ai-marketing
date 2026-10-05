# /costs - Know What It Costs to Operate

You are helping a company find out what an hour of its work really costs, so that
`/price-it` has a floor under every price. Many owners have no idea: no accounting, founders
unpaid, subscriptions nobody tracks. This command is built for them. It produces `06-costs.md`,
an internal file `/price-it` reads as its cost inputs.

Framework files are in English. Conversation and content follow the blueprint's
`content_language`. Currency comes from the blueprint (`01-company.md`); confirm it once in
Step 0. Country is per person (Step 1).

---

## Interaction rules

- **Quick first, refine after.** Six coarse questions give a cost per hour in minutes, every
  estimate labeled. Only then offer to refine, block by block.
- **One question per message.** Closed questions through AskUserQuestion, recommended option
  first. Free text only for figures and descriptions.
- **`no sé` is always valid.** It never stops the flow: propose a typical value for this company's
  size, type and country, labeled `[estimate]`, and ask to confirm. Nothing estimated is written
  unconfirmed.
- **Explain the term in one sentence when you introduce it** (employer cost, billable hour,
  utilization, break-even). Never assume the owner knows.
- **Idempotent.** If `06-costs.md` exists, this is a revision: show Results and ask what changed.

---

## Step 0: Load

1. No `01-company.md` → *"Run `/setup` first."* Stop.
2. Read `01-company.md` (type, size, country), `03-people.md` (team), `02-offering.md` (items).
3. If `06-costs.md` exists: show its Results table and `last_costed`; AskUserQuestion *"What
   changed?"* → `People` · `Overhead` · `Recurring per item` · `Hours / week` · `Nothing, just
   review`. Jump to that block, then Step 5.
4. Confirm the currency in one closed question. Country is **per person**, asked in Step 1: it
   is where that person lives and is paid, which drives their salary benchmark and employer
   cost. It is not the company's seat (there may be none) and not the market (that changes per
   product and belongs to `/price-it`).
5. Opening, in the content language:

   > **Costs for [BRAND].** Six quick questions, then a cost per hour. Everything I estimate
   > is marked and you can refine it afterwards. Team from the blueprint: [names]. Start?

---

## Step 1: People (quick)

For each person in `03-people.md`, in order. `[N/total] Name`.

1. AskUserQuestion *"How does [Name] work with the company?"* → `Payroll` · `Freelance /
   invoices` · `Founder, no salary` · `Commission only`. Then *"Where is [Name] based and
   paid?"* — closed, with the countries already seen in the blueprint first, plus Other. This
   is the person's **reference country** for every benchmark below.
2. Cost, by type:
   - **Payroll:** *"Gross salary per month (or per year)?"* → employer cost = gross × the
     person's country employer-cost multiplier (social security and mandatory
     contributions), found by **WebSearch**, one query, source shown, `[estimate]`. Show the
     arithmetic and ask to confirm; offer `Use gross without uplift`.
   - **Freelance:** *"What do they invoice per month, on average?"* That is the cost; no uplift.
   - **Founder, no salary:** explain in one sentence why 0 breaks the floor. Then, in this
     order, never assuming:
     1. *"How much would you want to pay [Name] per month for this work, even if it is not
        paid today?"* A figure → record it as `target draw`, source `stated`.
     2. `no sé`, or they ask for a reference → **WebSearch** the market salary for that role,
        the person's country and a company of this size (2-3 queries: salary portals,
        surveys, job postings with a published range). Show the range with sources and year,
        tagged `[Benchmark]`, propose the midpoint. Never quote a salary from memory.
     3. They insist on 0 → accept it and add the **Warning** line to Results.
   - **Commission only:** fixed cost 0. *"What percentage?"* Record it; `/price-it` subtracts
     it from margin.
   - `no sé` on gross (payroll or freelance) → same WebSearch as above: role, the person's
     country, size; sources and year shown; propose the midpoint `[Benchmark]`. The user
     confirms or corrects before it is recorded.
3. Hours are **not** asked per person here. Step 3 derives them from the week.

---

## Step 2: Overhead (quick)

One closed question: *"Fixed monthly costs besides people: tools, hosting, accountant, office,
ads. Roughly?"* → options built from the company's size and type, e.g. for a 2-3 person studio
with no office: `Under 300` · `300–700 (typical) [estimate]` · `700–1,500` · `I have a bank
statement` · `Let's go category by category`.

- A range → record its midpoint, source `estimate`.
- **Bank statement** → *"Drop the last 3 months (CSV or PDF) in `documents/finance/` and tell
  me."* Then read only recurring charges (same payee, ≥2 months), classify into the six
  categories, and show the table plus an **Unclassified** list: *"'AMZN MKTP 43,90' — what is
  it?"* one at a time. Ignore one-off charges and anything personal; say you did. Source: `bank
  statement`, mode becomes `refined`.
- **Category by category** → Step 2b now.

### Step 2b: Overhead by category (refine)
One category per message, each with 3-5 examples relevant to this company (from its stack in
`01`/`02` when known: *"Tools & SaaS — Google Workspace, GitHub, Vercel, Claude/OpenAI, Notion,
domain..."*). Free text or `no sé` → typical range `[estimate]` to confirm. Categories: Tools &
SaaS · Infrastructure & hosting · Accounting, legal, insurance · Office & workspace ·
Marketing & ads · Other.

---

## Step 3: The week (quick)

Free text: *"Describe a normal week for the people who do client work, in big blocks: how much
goes to clients, to selling, to your own products, to admin. Hours, or halves and quarters."*

Derive per person (or for the team if described together): hours per week → ×4.33 = hours per
month; client-work share = **billable hours**; billable ÷ total = **utilization**. Show the
result in one line, in plain words, and say what it means for the price:

> ~11 h/week on clients out of 45 → ~48 billable h/month (utilization ~25%). Low because you
> invest in your own products: normal for your stage, but the cost per service hour will come
> out high. Correct?

AskUserQuestion `Yes` · `Adjust hours` · `Adjust the split`.

If the user cannot describe it, offer the three profiles: `Mostly clients (~75%)` · `Half clients,
half selling and admin (~50%)` · `Mostly own product, clients now and then (~25%)`.

---

## Step 4: Per-item recurring (quick → refine)

Quick: one closed question *"Does anything you sell carry a cost every time you deliver it or
every month a client stays (API/model usage, hosting per client, licenses, physical goods)?"*
→ `No` · `Yes, some items` · `no sé`.

- `No` → skip. `no sé` → skip and note it in Assumptions.
- `Yes` → one item at a time, only sellable items from `02-offering.md`: per project or per
  client/month, amount, what it is. Quick and coarse is fine; `[estimate]` when guessed.

**For a product that calls models, ask about inference separately, every time.** It is the
component that gets forgotten and the one that moves the margin: AI products average 52 % gross
margin against the 80 % of classic SaaS, and the difference is compute
Ask for the **provider's invoice divided by
active accounts**, not a guess. No invoice yet → `[estimate]`, and every floor built on it is
marked provisional.

Break a product's recurring cost into **infrastructure · inference · support · third parties**
(payment fees, email), not one lump. A single number hides which part grows with usage.

Ecommerce and local businesses: this block is the cost of goods or supplies per sale and it
matters more than cost per hour; say so and spend the questions here.

---

## Step 5: Compute and propose

**A mixed company has two economies, and one cost per hour cannot describe both.** When
`02-offering.md` has both services and products (`blocks: [services, saas]`), compute **two
blocks**. Services consume hours; a product consumes infrastructure, inference and support, and
is costed with its own COGS — [separating software from services COGS is the standard, so both
margins can be read](https://www.dualentry.com/blog/saas-cogs).

Putting the consultancy's absorption rate inside a product's floor is what produced, on
2026-09-21, two defensible floors 16× apart for the same product.

**Support on a product is costed at the cost of whoever provides it, never at the absorption
rate.** An hour of support only displaces a sale if there is demand to displace; below ~40 %
utilization there is not. Say which of the two you used and why.

### Block 1 · Services

One message. Show the arithmetic, not just the results:

```
People            X (N people; K estimated)
Overhead          X (source)
Total / month     X
Billable hours    H (utilization U%)
Cost per hour     X / H = R
Break-even        X revenue / month
Margin suggested  A–B%  [Benchmark: <source, year> for <company type>, <country>]
Sensitivity       utilization ±15 pts → R'  ·  founders at 0 → R''  ·  lower draw → R'''
Estimated inputs  N of M
```

Sensitivity looks the way the business can move: with utilization under 40 % show what
happens if it rises (outreach working); above, what happens if it drops. Always show founders
at 0 when there is a target draw, so the reason for the draw is visible.

### Block 2 · Products, one table per product

```
PRODUCT · per client and month
Infrastructure    X  (hosting, storage)
Inference         X  (provider invoice / active accounts)   ← [estimate] if no invoice
Support           X  (hours × cost of whoever does it)
Third parties     X  (payment fees, email)
─────────────────────────────────────────
COGS / client     X      ← this is the floor
At price P:       gross margin M%
Benchmark         AI product 52% · classic SaaS 80%   [source, year]
```

**Compare each product against its own benchmark.** Measuring an AI product against the 80 % of
classic SaaS makes something normal look broken, and the other way round hides a real problem.

The suggested margin comes from **one WebSearch** on typical margins for this company type and
country (or the sector, for ecommerce), with the source and year shown; if the search gives
nothing usable, write `—` and say no benchmark was found. Explain break-even in one sentence. Then AskUserQuestion *"Good enough for now?"* →
`Write it, I'll refine later (Recommended)` · `Refine people` · `Refine overhead` · `Refine
recurring costs`. Refining loops back to that block (2b for overhead) and returns here.

---

## Step 6: Write

Only after `Write it`. From `templates/06-costs.md` → `.claude/skills/company-blueprint/06-costs.md`.

- `## SaaS unit economics`, one table per product, when there are products: COGS per client
  broken into infrastructure, inference, support and third parties, the gross margin at the
  current price, and the benchmark it was compared against. Mark `[estimate]` per line, not for
  the block: knowing which component is guessed is what makes it fixable.
- Frontmatter: `currency`, `country`, `mode` (`quick` unless any block was refined or a bank
  statement was read), `utilization`, `last_costed` = today, `review_by` = today + 6 months
  (offer to change in the same closed question as the write).
- Every estimated or benchmarked figure keeps its label in the Source column and a row in
  Assumptions with when to revisit.
- Founder at 0 → Warning line in Results.
- Remove rows and sections with no data. No `[PLACEHOLDER]` may remain (Grep `\[[A-Z_]{3,}\]`).
- Do not touch any other blueprint file.

---

## Step 7: Summary

> **Costs done ([quick/refined]).** Cost per billable hour: **R** · billable hours/month: H ·
> break-even: X/month. [N] of [M] inputs are estimates: [list, one line].
> Internal file: `06-costs.md`. Not for clients, not for copy.
> **Next:** run `/price-it`; it picks these up as the floor. Re-run `/costs` when the team,
> tools or your week change, or by [review_by].

---

## Safety rules

1. Nothing is written without the explicit `Write it`. No estimate enters unconfirmed.
2. Every estimate carries `[estimate]` and a source; every external figure `[Benchmark]` with
   URL, country and year. Salaries and employer-cost multipliers are **searched, never
   recalled**: no figure from model memory enters the file. Never present either as a company
   fact.
3. A founder at 0 is never silent: target draw, or a visible Warning.
4. `06-costs.md` is internal. Downstream commands may use the cost per hour as a floor; they
   never quote it, nor any salary or overhead figure.
5. Bank statements: read recurring business charges only; never list personal or one-off items
   in the file; never copy account numbers or balances.
6. Generic across company types: for ecommerce and local, per-item costs lead; for services and
   SaaS, cost per hour and per-client recurring lead. Say which applies.
