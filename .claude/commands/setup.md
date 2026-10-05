# /setup - Company Blueprint Onboarding

You are onboarding a company into the AI Marketing framework. Your goal is to build the
**company blueprint**: five files under `.claude/skills/company-blueprint/` that every other
workflow reads. You gather from three sources (website, `documents/`, interview), and they
are not exclusive: read everything that exists, interview only for what is missing.

Framework files are in English. Blueprint **content** is written in the company's
`content_language`, chosen in Step 4.

Follow the steps in order. Do not write any file before Step 6.

## Interaction rules

Same as every command in this repo:

- **Closed questions go through AskUserQuestion**, options listed in the step, recommended one
  first. Free text only for open answers (a name, a URL, a description, a list). The user
  always has "Other".
- **One section per message.** Up to four closed questions from the same section can share
  one AskUserQuestion call; never mix sections.
- **Propose, then ask.** Whatever the website or `documents/` already answered is shown and
  confirmed (`Yes` · `Adjust`), never asked from scratch.
- `skip`, `luego` and `no sé` are valid at any point; a skipped question is asked once more
  with the reason, then recorded as a gap. Never guess.

---

## Step 0: State check & welcome

**Existing blueprint.** Glob `.claude/skills/company-blueprint/0*.md`. If any populated
file exists (not under `templates/`):

- Without `--force` in `$ARGUMENTS`: read `last_setup` from `01-company.md` and stop with:

  > A blueprint already exists (last setup: [DATE]). Use `/setup-update` to revise it, or
  > `/setup --force` to discard it and start over.

- With `--force`: list the populated files and AskUserQuestion *"Discard these and start
  over?"* → `Yes, discard` · `No, keep them`. Only on yes continue; the files are overwritten
  in Step 6, not now.

**Inventory.** Glob `documents/**/*` (ignore `.gitkeep` and `README.md`). Count files per
subfolder: `web/`, `decks/`, `products/`, `people/`, `brand/`, `content/`.

**Welcome.** One message:

> **Welcome to the AI Marketing setup.**
>
> I'll build your company blueprint: who you are, what you sell, who is behind it, and how
> the brand speaks. Every other command in this repo reads from it.
>
> I found in `documents/`: [per subfolder, e.g. "1 deck, 3 product sheets, nothing in
> brand/" — or "nothing yet. If you have decks, product sheets, bios or brand assets, drop
> them in `documents/` (see `documents/README.md`) and tell me when; or we go by interview."]
>
Then AskUserQuestion *"Does the company have a website?"* → `Yes, I'll paste the URL`
(free text follows) · `No website` · `Let me add documents first` (wait, then re-run the
inventory). Only the URL itself is free text.

---

## Step 1: Sources

### 1a. Website (if a URL was given)

Fetch with WebFetch, read-only, one pass, **at most 12 pages**. Order:

1. Home page. Extract navigation links.
2. `/sitemap.xml` if it exists, to pick pages instead of guessing paths.
3. About / team / company page.
4. Products, services, pricing, plans, catalog pages. Follow one level into individual
   product pages if the catalog has fewer than 8 items; otherwise read the catalog page only.
5. Contact page (addresses, hours, phone).
6. Two or three blog posts or news items, most recent first: these are **voice** samples,
   not facts.
7. Legal / imprint page for legal name, tax ID and founding entity if present.

While fetching, note the source URL next to every fact you extract.

If the site returns 403, a login wall, or a shell with no content (SPA rendered client
side), stop fetching and say:

> I can't read [URL] ([reason]). Export the key pages as PDF or text into `documents/web/`
> and tell me, or we cover the website by interview.

Do not retry in a loop. Do not use any other channel to reach the site.

### 1b. Documents

Read every file in `documents/`, in this order: `web/ → decks/ → products/ → people/ →
brand/ → content/`. PDFs through `pdftotext <file> -`; images with Read (logos, headshots,
brand boards); `.md`, `.txt`, `.csv` directly. List unsupported formats and skip them.

What to pull from each:

- **`web/`**: same as the website pass.
- **`decks/`**: mission, market, positioning, offering, team slide, traction numbers.
- **`products/`**: catalog, features, prices, deliverables, process, specs.
- **`people/`**: names, roles, bios, credentials, contact, photos.
- **`brand/`**: logo variants, palette (hex), fonts, usage rules. Read images.
- **`content/`**: tone, register (tú/usted), recurring vocabulary, sentence patterns,
  CTAs. Sample at least 3 pieces if available.

### 1c. Material outside the repo

The user may point at files elsewhere on disk (a brand guide in another repo, a deck on
the desktop) or paste screenshots. Sources must live inside `documents/` so the blueprint's
paths resolve and `/setup-update` can re-read them:

- For a path: AskUserQuestion *"Copy it into `documents/<folder>/`?"* → `Yes, copy` ·
  `No, skip it`; copy on yes, then read it from its new location and cite the `documents/`
  path. Never cite a path outside the repo.
- For a pasted screenshot: use it as a source, cite it as *"screenshot provided by the user
  on YYYY-MM-DD"*, and suggest saving the original into `documents/`.

### 1d. No sources at all

If there is no URL and `documents/` is empty, say so and go straight to Step 4 in full
interview mode. Steps 2 and 3 are skipped.

---

## Step 2: Extract

No intermediate output. Build the working model in context, organised by target file:

- **Company** (`01`): identity, web & presence, what we do, market, positioning quotes.
- **Offering** (`02`): catalog rows, flagship, proof, and the fields of the type block(s).
- **People** (`03`): team table; anything usable for outreach, bios, approvals.
- **Voice** (`04`): languages, register, tone adjectives, vocabulary, verbatim examples,
  observed patterns; visual: logos, colors, fonts.

Every fact carries its source (URL or `documents/` path). Distinguish **stated** (the
company says it) from **inferred** (you deduce it). Inferred items will be labeled
`[Inferred from <source> — review before relying on this]` in the files.

Propose a `company_type` from: `saas`, `services`, `ecommerce`, `local`, `mixed`. Keep
the one-line justification for Step 4.

---

## Step 3: Cross-reference

Compare website against documents, and documents against each other. Look for:

- Different prices or plans for the same product
- Different names for the same product or service
- Different number of founders/partners, or different roles for the same person
- Different founding year, legal name, or location
- Claims in a deck that the website no longer makes (or vice versa)

If there are conflicts, resolve them one AskUserQuestion at a time (up to four conflicts per
call): the question states the conflict, the options are the versions found (`Website says A`
· `Deck says B` · `Neither, I'll type it`). Format of each question:

```
## Cross-reference issues

Tell me which version is right for each.

1. **Price — [PRODUCT]:**
   Website ([URL]) says: [A]
   Deck ([file]) says: [B]

2. ...
```

If none: state `No cross-reference issues found.` and continue.

---

## Step 4: Interview for gaps

A conversation, not a form. Ask only what Steps 1-3 did not answer. Where you extracted
something, show it and ask for confirmation instead of asking from scratch. Group
questions per section; two to four per message.

### 4.1 Type & language (one AskUserQuestion, two questions)
- `company_type`: *"From what I read, this is a [type] company because [reason]. Right?"* →
  the proposed type first, then the others (`saas` · `services` · `ecommerce` · `local` ·
  `mixed`). For `mixed`, a second multi-select: which blocks apply.
- `content_language`: *"Language for the blueprint content?"* → the market's language first,
  then English, then Other.

### 4.2 Company (`01`)
Whatever is missing from: legal name, brand, founded, HQ, size, social profiles, B2B/B2C,
geography, sectors served, one-sentence value proposition. Closed where the answer is a
choice (`B2B` · `B2C` · `Both`; brand spelling variants found on the site; the value
proposition sentences found, as options), free text for names and URLs. If positioning was
only inferred, read it back → `Yes, that's us` · `Adjust`.

### 4.3 Offering (`02`)
- Complete the catalog: *"I have [N] products/services: [list]. Anything missing or
  discontinued?"*
- Pricing: AskUserQuestion *"Is pricing public?"* → `No, all private` · `Partly` · `Yes,
  published`. Set `pricing_public` to `false` / `partial` / `true`; ranges, if any, as free text.
- The fields of the type block(s) that are still empty. Ask for the most useful ones first
  (plans, deliverables, categories, hours); leave the rest blank rather than asking twenty
  questions.
- A question the user skips or answers with something else is asked **once more**, briefly,
  saying why it matters. If it is skipped again, record the gap (`—` or "pendiente") and
  list it under **Gaps left open** in Step 5 and Step 7. Never fill it with a guess.
- Proof: for clients or figures found on the site, AskUserQuestion *"Can I cite these
  publicly?"* → `Yes, all` · `Only on the website, don't cite` · `Some` (then free text).
  Anything else: *"Any numbers, clients or testimonials I can use publicly?"* as free text.

### 4.4 People (`03`)
- Team: names, roles, participation (owner %, partner, employee, freelance), what each
  one owns. Who is the decision-maker the agent should ask when a workflow needs a human.
- Team: participation and relationship are closed (`Owner` · `Partner` · `Employee` ·
  `Freelance` · `Commission only`); names and responsibilities are free text. Decision-maker:
  closed pick among the team.
- Then the **three flags**, as one AskUserQuestion with three yes/no questions:
  - *"Will anyone send outreach (emails, LinkedIn DMs) from this repo?"* → `outreach`.
    If yes: for each sender, sending address, LinkedIn, signature, personal tone, what
    they'd never write, availability for calls.
  - *"Do you want bios for content (posts, about page, press)?"* → `bios`. If yes: short
    and long bio per person, story, highlights, photo path, public links. If a CV or
    LinkedIn export exists in `documents/people/`, draft from it and ask for corrections.
  - *"Should workflows check who approves pricing changes, public copy, and new
    clients before acting?"* → `approvals`. If yes, fill the approvals table row by row;
    `anyone` means no gate.
- A `false` flag means the block is removed from the file in Step 6, not left empty.

### 4.5 Voice (`04`)
- If you have website copy or `content/` samples: present the extracted tone, register,
  vocabulary and observed patterns, with two verbatim "this is us" examples →
  AskUserQuestion `Yes, that's us` · `Adjust` (free text).
- If you have nothing: register is closed (`tú` · `usted` · `both by context`, or the
  language's equivalent); adjectives, own words, banned words and the two example sentences
  are free text, one prompt each.
- Banned words and claims never made: propose a list from the market's usual hype
  (multi-select, plus Other), then *"Any claims you never make?"* with common options
  (`"the best" / "#1"` · `guarantees of results` · `naming competitors` · `metrics without
  data`) multi-select.
- `voice` is `true` unless the user explicitly picks `Skip voice for now`.

### 4.6 Visual (`04`)
- If `documents/brand/` had material: present logo files found, colors, fonts. Confirm.
- If the website was readable but `brand/` is empty, you may propose colors observed on
  the site, labeled as inferred; ask for the real hex values.
- If nothing: AskUserQuestion *"Visual identity?"* → `I have a logo / colors, I'll give
  paths and hex` (free text follows) · `Skip for now, visual: false`.

---

## Step 5: Propose

Show the complete blueprint in summary **before writing anything**. Per file, what it will
contain, with `[inferred]` marks and the final flag values:

```
## Blueprint proposal

**01-company.md** — [BRAND], [type], [HQ], founded [YEAR]. Market: [B2B/B2C], [geo].
Value proposition: "[sentence]". Positioning: 2 quotes + 1 inferred note. Sources: [N] URLs, [N] documents.

**02-offering.md** — [N] catalog rows, flagship [X]. Blocks: [saas]. Pricing: [public/partial/private].
Proof: [N] items with sources.

**03-people.md** — [N] people. Decision-maker: [NAME]. Flags: outreach=[..] bios=[..] approvals=[..].
[If outreach: senders: ...] [If approvals: N rules]

**04-voice.md** — [language], [register]. Tone: [adj] / not [adj]. Banned: [N] words.
Examples: [N] verbatim. Patterns observed: [N] (inferred). Flags: voice=[..] visual=[..].
[If visual: logo variants [N], colors [N], fonts.]

**00-overview.md** — generated from the four above.

Gaps left open: [e.g. "no proof items", "pricing private", "no brand assets"].

```

Then AskUserQuestion *"Write these files?"* → `Yes, write` · `Change something first` (free
text). Iterate until yes. Do not write on a partial answer.

---

## Step 6: Write

Templates live in `.claude/skills/company-blueprint/templates/`. Targets live one level
up, in `.claude/skills/company-blueprint/`.

1. **`01-company.md`**: copy the template, fill every placeholder, set frontmatter
   (`company_type`, `content_language`, `sources`, `last_setup` = today). Fill the
   `## Sources read` table with every URL and file actually read.
2. **`02-offering.md`** (index): copy the base template; fill the catalog (one row per
   product or service), Proof, Flagship, sale status, and the `## Units` table (slug + folder
   per row). Set `blocks:` and `pricing_public:` in the frontmatter.
   Then, **one folder per unit**: `offering/<slug>/unit.md` from
   `templates/offering/unit.md`, keeping only the block for the unit's type (`services`,
   `saas`, `ecommerce`, `local`; the `02-offering.<type>.md` templates list the fields each
   block should carry). Slug = kebab-case of the item name, stable from now on. Units not for
   sale get a folder too. `icp.md`, `pricing.md` and `competitors.md` are created later by
   their commands; leave them absent.
3. **`03-people.md`**: copy, fill the team table and decision-maker. For each flag set to
   `false`, **delete its block entirely** (heading included). Remove the
   `[sections.x]` markers from the headings that remain.
4. **`04-voice.md`**: same rule for `voice` and `visual`. Everything under `Patterns
   observed` keeps the inferred label.
5. **`00-overview.md`**: generate from the four files. One screen. Do not add facts that
   are not in 01-04.

Rules while writing:

- A populated file **never contains a `[PLACEHOLDER]`**. A field with no data is removed,
  or written as `—` inside a table row that has other data.
- Content in `content_language`; headings and frontmatter keys stay in English.
- Sources next to facts: a URL or a `documents/` path, as the templates show.
- Write with the Write tool, whole file at a time. These files are gitignored; nothing
  here reaches git.
- After writing, Glob the five files and confirm each exists and has no `[` `]` placeholder
  left (Grep for `\[[A-Z_]{3,}\]`). Fix before reporting.

---

## Step 7: Summary

> **Setup complete.**
>
> - `00-overview.md` — one-screen summary, loaded in every session through `CLAUDE.md`
> - `01-company.md` — identity, market, positioning, sources
> - `02-offering.md` — [N] products/services, [type] block(s), pricing [public/partial/private]
> - `03-people.md` — [N] people · outreach=[..] bios=[..] approvals=[..]
> - `04-voice.md` — voice=[..] visual=[..]
>
> **Left open:** [gaps from Step 5, or "nothing"].
>
> **Privacy:** these files hold real company and personal data and are gitignored. They live
> only in this working copy; back them up outside git if you need to.
>
> **Next:** when the offering, team or brand changes, run `/setup-update`. Every other
> command now reads from this blueprint.

---

## Design principles

- Three sources, one pass, no exclusive paths: read what exists, interview the rest.
- Propose-then-write: the user sees the whole blueprint before a single file is written.
- Nothing invented: a fact without a source or an answer does not go in. Empty beats plausible.
- Inference is labeled, and stays a hypothesis.
- Flags decide what exists. A block set to `false` is removed, so downstream workflows
  never read half-filled sections.
- The website is read once, read-only, with a page cap. No scraping, no login, no retries.
- The populated blueprint is gitignored; the templates are the product.

---

## Signature (written with `03-people.md`)

For each person who signs outreach, fill `templates/signature.html` into
`signatures/<person-slug>.html` using the company data already gathered: name, role, company,
phone, email, website, brand colour from `04-voice.md`, and a **public** logo URL on the company's
own domain. Also write the `.txt` plain-text version.

Never point the logo at a webmail's internal image endpoint: it needs a session and reaches the
recipient broken. If no public logo URL is known, leave `[LOGO_URL]` and say so — `/set-mail`
resolves it.
