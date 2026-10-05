# /prospects - Find Real Companies That Match One Unit's ICP

You are building a prospect list for one sellable unit: real companies, a named contact when
public, a **verified buying signal with its URL**, a public contact email or none, and 3-5
observed facts to write from. The result is rows in `offering/<slug>/prospects.csv` plus a run
log in `offering/<slug>/prospects-runs.md`. `/outreach` reads the rows; `/analyze` reads what
happened to them.

The method is a two-phase discovery: a free web search over the ICP's five axes returns
candidates; then one verifier per candidate looks for public evidence of the signal. A
candidate without evidence and URL is discarded. The main thread does not search: it scopes,
dispatches, consolidates, proposes and writes. Framework files are in English. Conversation
and content follow the blueprint's `content_language`.

---

## Arguments

`/prospects <unit> [market] [n]`

- `unit`: a slug under `offering/` (`acme`, `consultoria-ia`) or a catalog item name.
- `market`: a country code from the unit's `icp.md` (`ES`, `PA`). Default: the first market
  with a country. `global` is not a market here: no country, no prospects.
- `n`: candidates to look for. Default **20**, hard cap **20** per run.
- Empty → AskUserQuestion over the units that have an `icp.md`, flagship first.

---

## Step 0: Load & scope

1. No `01-company.md` → *"Run `/setup` first."* Stop.
2. No `offering/<slug>/icp.md` (or the `_shared/` file it points to) → *"Run `/icp <unit>`
   first: prospects without an ICP are a list of names."* Stop.
3. Read: the unit's `unit.md` (what it is, sale status, markets), its ICP (firmography, pain
   in their words, triggers, persona, **Where to find them**, anti-ICP, the market block),
   `03-people.md` only to know who signs (nothing else is needed yet).
4. Read `offering/<slug>/prospects.csv` if it exists (companies and keys already there) and
   `offering/_shared/suppression.csv` if it exists (emails and domains never to contact).
   Read `offering/<slug>/prospects-runs.md` if it exists: companies discarded in earlier runs
   are excluded too.
5. If the unit is not for sale (`unit.md` says beta, testing, restructuring), say so once and
   ask whether to continue: prospects for something that cannot be sold are for validation,
   and the row gets `notes: validation only`.

---

## Step 1: ICP FINAL

Build the five axes from the ICP file. Do not ask what the file already answers.

- **Sector / vertical**: from firmography.
- **Geography**: the market argument, narrowed by the ICP's market block if it names regions
  or cities.
- **Size**: in the ICP's own unit (employees, locations, listings, hires per year).
- **Contact role**: from the persona block (who signs, who feels the pain).
- **Buying signal**: from **Visible signals** and **Triggers**. This is the axis that cannot
  be missing: without it the search is demographic and the emails have no hook.

The **Where to find them** channels and keywords are hints for the researcher (where such
companies show up), never a list of portals to enumerate.

Show it exactly like this, in `content_language`:

```
ICP FINAL · <unit> · <market>
- Sector: ...
- Geografía: ...
- Tamaño: ...
- Cargo objetivo: ...
- Señal de compra: ...   ← qué evidencia pública buscar (vacantes, reseñas, posts, su web)
- Pistas: ... (canales y keywords del ICP)
- Excluir: N empresas ya en el tracker o descartadas antes
```

AskUserQuestion → `Go` · `Change something` (free text; rebuild and show again) · `Stop`.
If the ICP has no observable signal, the question is instead *"Which public signal should
we look for?"* with 2-3 proposals typical of the vertical, labeled `[inferred from product]`.

---

## Step 2: Candidates (one Agent)

One `general-purpose` agent with WebSearch. Its prompt contains the ICP FINAL, `n`, the
exclusion list, and this, verbatim:

> You are researching prospects for **[unit]**, sold by [company] to [ICP one-liner]. Find
> [n] real companies that match the DEMOGRAPHIC axes of this profile:
>
> [ICP FINAL]
>
> Demographic axes are sector, geography, size and contact role. Match those. The buying
> signal will be verified per candidate in a second pass, so here be generous on signal and
> strict on reality: a plausible reason is enough, quoted proof is not needed yet.
>
> Use the hints as places where such companies are visible (job boards, directories,
> associations, LinkedIn), but the result is companies, not listings.
>
> Return ONLY a JSON array, one object per company:
> `company` (official name) · `website` (https URL) · `role` (likely contact role) ·
> `contact_name` (only when found with reasonable confidence; else "") · `linkedin_url`
> (company or person page if it appeared in results; else "") · `email` (only if public in
> what you read; never invent one; else "") · `signal` (one sentence: why they plausibly have
> the pain; will be verified) · `source_url` (where you found the company).
>
> Rules: no preamble, no fence, no prose after the array. Return fewer real companies rather
> than pad. Never invent a company. Skip these, already known: [exclusion list]. Skip anything
> that matches the anti-ICP: [anti-ICP lines].

Parse the array. Drop entries whose `website` does not resolve to a domain. Drop exact
duplicates and companies in the exclusion list the agent missed.

---

## Step 3: Verify (one Agent per candidate, 10 at a time)

Launch verifiers in waves of **10**, each `general-purpose`, all in one message per wave.
Each prompt carries one candidate, the signal axis, the market, and the three tasks below.

**Task A · signal** (verbatim):

> You are verifying ONE candidate against ONE buying-signal hypothesis.
> Company: [company] · Website: [website] · Country/region: [market]
> Signal to verify: [signal axis from ICP FINAL]
>
> Search the public web for evidence that this company, or someone clearly speaking for it,
> plausibly exhibits this signal. ANY one of these counts:
>   A) A review or rating (Google Maps, Trustpilot, Glassdoor) mentioning any aspect of the pain.
>   B) A job posting. A generic admin / back-office posting IS evidence when the signal is
>      about manual work: it means the function is staffed by people. Quote title + one duty.
>   C) A LinkedIn post or article by an employee, founder or manager touching the workflow.
>   D) A forum, community or sector-press thread describing their operations.
>   E) Their own About / Careers / Press / Blog page revealing the operational profile.
>
> verified=true with ONE concrete artefact and a real URL (a job posting for a manual role is
> "medium"). verified=true "low" when circumstantial but real. verified=false ONLY when after an
> honest search you found NO public artefact at all. Positive reviews do not disprove the pain.
>
> Return: `verified` true|false · `evidence` (1-2 sentences, direct quote allowed, original
> language; "" if false) · `source_url` (the exact page hosting the evidence, not the homepage
> unless it is literally there; "" if false) · `confidence` high|medium|low · `notes` (one
> sentence on why this confidence; mandatory when true).
> NEVER invent quotes, postings or URLs. A modest real signal with a working URL beats a
> perfect-sounding one with a fabricated source.

**Task B · public email** (verbatim):

> Find the company's public contact email. Procedure, in order:
> 1. WebFetch the homepage. Collect `mailto:` links first, then plain-text emails.
> 2. Follow the REAL footer or menu links whose text matches: contacto, contact, aviso legal,
>    legal, privacidad, privacy, quiénes somos, nosotros, about, oficinas, dónde estamos.
>    Spanish companies must publish a contact email in their aviso legal.
> 3. Only then try known slugs: /contacto /contact /aviso-legal /legal /privacidad
>    /politica-de-privacidad /quienes-somos /nosotros. At most 8 pages in total.
> 4. Discard: sentry, wixpress, example., yourdomain, image or asset extensions, schema.org,
>    w3.org, googleapis; local part shorter than 2; TLD longer than 12.
> 5. Rank: same domain as the website +100 · role mailbox (info, contacto, hola,
>    administracion, comercial, ventas, rrhh, talento, seleccion...) +40 · gmail/hotmail/
>    outlook/yahoo −10 · shorter wins ties.
> Return `email` (best one or ""), `email_source` (URL of the page where it appears, or ""),
> and `email_status`: `public` (found) · `none` (pages read, nothing published) ·
> `unsearchable` (could not access the site: blocked, down, JS-only). Never report `none`
> when you could not read the pages. Never deduce an address from a name pattern.

**Task C · findings** (verbatim):

> From the pages you already read, write 3-5 short factual bullets about this company that a
> salesperson could reference: what they do and for whom, visible tools or stack, open
> vacancies (count and titles), locations, anything dated. Each bullet ends with its URL.
> Observed facts only; no scores, no judgments, no advice. Also return `linkedin_url` if a
> public company or person page appeared, else "".

Each verifier returns one JSON object with all fields. Then wait; do not search yourself.

---

## Step 4: Consolidate

1. **Drop unverified.** `verified=false` → discarded, listed in the run log with "no public
   evidence". The verifier's `evidence`, `source_url` and `confidence` replace the phase-1
   signal.
2. **Key**: slug of `email` → else `<company>-<contact_name>` → else `<company>`; lowercase,
   `[a-z0-9.-]`, hyphens collapsed, max 80 chars. Same rule for everything already in the CSV.
3. **Dedup** against the tracker by key and by normalized company name; against
   `suppression.csv` by email and by domain. Suppressed → discarded, reason "suppressed".
4. **MX check** on public emails, from the main thread:
   `dig +short MX <domain>` (fallback `nslookup -type=mx <domain>`). Empty answer → keep the
   address but set `email_status=none` and `notes: publicado pero el dominio no tiene MX`.
5. **Channel**: `email` when `email_status=public`; otherwise `linkedin` when `linkedin_url`
   exists; otherwise `none` (the row still enters: the signal is verified, the route is
   missing and `/outreach` will say so).
6. Mark the run `partial` if the researcher returned fewer than `n`, or a wave failed.

---

## Step 5: Propose

One message, a table in `content_language`:

```
Prospects · <unit> · <market> · <date>
Candidates N · verified N · discarded N (no evidence n · duplicate n · suppressed n · anti-ICP n)

| # | Company | Contact · role | Email / LinkedIn | Signal (confidence) | Evidence URL |
| 1 | ... | ... | hola@... (public) | 6 vacantes abiertas (high) | https://... |
| 2 | ... | ... | LinkedIn | ... (medium) | https://... |

Discarded: company · reason (one line each)
Partial: what is missing, or none
```

AskUserQuestion → `Add all N rows` · `Pick rows` (free text: numbers to keep or drop) ·
`Re-run with changes` (free text; back to Step 1) · `Discard the run`.

---

## Step 6: Write

Nothing is written before the answer above. Then:

1. `offering/<slug>/prospects.csv`: if missing, create it from
   `templates/offering/prospects.csv` (header only). Append one row per approved prospect,
   `status=lead`, `source=prospects`, `cadence=none`, `next_touch_on=""`, `added_on` and
   `updated_on` today. Write with Python's `csv` module (a one-liner via Bash) so quotes and
   commas inside `findings` and `evidence` stay valid. Never rewrite existing rows.
2. `offering/_shared/events.csv`: if missing, create from `templates/offering/_shared/events.csv`.
   One `added` event per row written (`by=agent`).
3. `offering/<slug>/prospects-runs.md`: if missing, create from
   `templates/offering/prospects-runs.md`. Append a `## <date> · <market> · n=<n>` block
   with the ICP FINAL used, counts, the discarded companies with reasons (they are excluded
   next time), and `partial` notes.
4. No other blueprint file changes. No `[PLACEHOLDER]` may remain in what you wrote.

---

## Step 7: Summary

> **Prospects done.** <unit> · <market>: N rows added (n by email, n by LinkedIn, n without
> route). Discarded N. File: `offering/<slug>/prospects.csv`. Run log updated.
> **Next:** `/set-mail` if `03-people` outreach is still pending; then `/outreach <unit>`.

---

## Campaigns

A new row goes into the pool with **`campaign` empty**. This command never puts anyone into a
campaign, not even when the unit has exactly one active: a discovery run that quietly adds people
to a campaign already in flight is how twenty becomes thirty-five with nobody looking.

Assigning is `/campaign`'s job, and it shows who moves. Say how many free rows the unit now has.

---

## Safety rules

1. **No evidence, no row.** A verified signal means a real URL a person can open.
2. **Public emails only.** Never deduce, never probe SMTP. `none` and `unsearchable` are
   different answers and are never merged.
3. **Never invent a company, a person, a quote or a URL.** Fewer rows beat fake rows.
4. **The main thread never searches.** One researcher, then verifiers in waves of 10.
5. **Propose-then-write.** Rows enter the CSV only after `Add` or `Pick`. Existing rows are
   never edited here; `/outreach log` owns status changes.
6. **Suppression is final.** An email or domain in `suppression.csv` is never proposed.
7. **Internal.** Client names from `02-offering.md` proof, costs and floors never appear in a
   prospect's notes.
