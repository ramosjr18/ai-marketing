# /outreach - Write and Schedule the Touches for One Unit

You turn verified prospects into a real campaign: **one email written whole per prospect** from
the evidence `/prospects` found, every message shown rendered before anything is scheduled, and
nothing sent until the owner says so.

Not a template with a variable. The body adapts to each prospect, and the sequence file is only
a shell that carries the per-lead content.

The engine is `cold-cli`, set up by `/set-engine`. This command does not send: it
writes, schedules and hands over. `cold-cli tick` sends, and the owner runs it.

Framework files are in English. Emails are written in the market's language (`content_language`,
or the market block of the ICP).

---

## Arguments

```
/outreach <unit>              every eligible prospect, written in batches of 5
/outreach <unit> --limit 5    only the first N
/outreach <unit> --dry        write the files and render, create nothing
/outreach <unit> --linkedin   the LinkedIn cadence instead of email
```

---

## Step 0: The gate

Everything stops here if something is missing. In order, reporting each check:

| Check | Where | If it fails |
|---|---|---|
| Sending identity complete | `03-people.md` Outreach block: address, signature, availability | run `/set-mail` |
| Deliverability verified | same block: SPF, DKIM, DMARC with a date | run `/set-mail`; if DKIM fails, say it and ask before continuing |
| Engine ready | `cold-cli account list` shows the account `active` | run `/set-engine`, then `/mailbox` |
| Daily cap | `03-people.md`, and today's `sent` events | schedule only what fits; say how many were left out |
| Voice | `04-voice.md` banned words and vetoed claims | never optional |
| Signer's variant | `03-people.md`: the signer's regional variant of Spanish | stop and ask; never infer it |
| A campaign | `offering/<unit>/campaigns/*/campaign.md`, `status` `draft` or `active` | run `/campaign <unit>` first. One usable → use it and say so. Several → ask. **Never pick one yourself**. `paused` or `closed` → stop and say which |

Then load: the unit's `unit.md` (what is sold, price status), its `icp.md` (pain in their words,
objections), `prospects.csv`, `_shared/suppression.csv`, `events.csv`.

**Eligible prospect**: **`campaign` is this campaign's slug**, `status` is `lead`, `channel` is
`email`, `email_status` is `public`, has a `signal_evidence` with a `signal_url`, is not in
`suppression.csv` by address or domain, and has no `sent` event already. Anything else is listed
as excluded, with the reason, and left alone.

Prospects of the unit that match the campaign's slice but sit in the pool with `campaign` empty
are **not** written to. Say how many there are and that `/campaign` assigns them: a run that
quietly widens its own audience is how people get written to twice.

A prospect with a `sent` event **from an earlier campaign** needs a new angle, not a resend.
Name them and say what they already received.

A unit whose `unit.md` says it is not for sale gets one question before anything else: writing to
prospects about something that cannot be bought is validation, not sales, and the owner decides.

---

## Step 1: Load the three blocks

Two are loaded once per run, the third per prospect. They are the **only** sources: a fact that
is in none of them does not exist.

**SELLER** — from `offering/<slug>/product.md` when it exists, else `unit.md`, plus
`03-people.md` and `01-company.md`.

**Prefer `product.md`.** `unit.md` carries the one-liner `/setup` took from the website, which is
the category the product falls into, not what it is: writing from it produces emails that pitch
the category. When `product.md` has section A or B, write from those, and never promise a
capability its section E does not mark `live`.

```
Campaña: <slug> · Objetivo: <de campaign.md, literal>
Ángulo: <de campaign.md — qué dice esta campaña que no dicen las otras de esta unidad>
Empresa: <nombre> · <una frase de qué hace>
Quien firma: <nombre>, <cargo>
Qué vendes: <de product.md §A: qué es, y qué NO es aunque lo parezca; si no hay, la frase de unit.md>
Capacidades: <de product.md §B: el trabajo que cada una elimina, solo las `live`>
A quién: <ICP en una línea>
Resultado: <de unit.md, solo lo escrito>
Precio: <lo que diga unit.md; «on request» si es eso lo que dice>
Estado de venta: <en producción / beta / no se vende>
Tono personal: <las reglas de tone/<slug>.md, literales; si no existe, «aplica la VOZ»>
Nunca escribe: <de 03-people>
Disponibilidad: <de 03-people>
```

**PROSPECT** — that row of the CSV, verbatim, `findings` and `notes` included in full.

> `findings` and `notes` are **the channel**. Anything any command writes there reaches the
> writing without touching this one. That is how a future enrichment step gets into the email
> for free.

**VOICE** — `04-voice.md`: the five rules, the banned words, the vetoed claims, **and the
signer's regional variant of Spanish**, declared in their `03-people.md` block.

The variant is not cosmetic and it is not corrected to suit the reader: what a person signs goes
out in their own Spanish. The second-person plural is where it shows — `ustedes` or `vosotros` —
so decide it from the signer, never from the prospect's country. A signer with no declared
variant is a gate failure, not something to guess.

---

## Step 2: Write each email in full

**One email per prospect, written whole.** Not a template with a variable: the body adapts to
this prospect, not just its first line. Two prospects with different signals get different
middles, not the same paragraph with a different opening.

Write from the SELLER block: never invent what the sender does, sells, charges or has done.
Write about the PROSPECT block: never import a fact about another company.

**Rules of evidence**, they outrank style:

1. **Never state that something is missing, broken or absent** unless the PROSPECT block says so.
   Not measured is not the same as not there.
2. **No number that is not in the blocks.** Not counted by eye, not estimated.
3. **What was observed is said as an observation**, with its source. What is deduced is asked as
   a question, never asserted.
   **The pain is always deduced.** The tracker proves they have 26 vacancies; it does not prove
   those vacancies hurt. So the vacancy count is stated flat, and what it costs them is owned as
   ours: *«veo que tienen 26 procesos abiertos. Creemos que esto ayuda justo ahí, en X y en
   Y»*. Never *«a ese volumen cada minuto se multiplica»*, which asserts their experience from
   the outside and is the fastest way to sound like someone who has never done their job.
4. **Never invent** a prior conversation, a mutual contact or a client name.

**Touch 1** (day 0), **90-140 words, or up to 160 when the campaign's offer has to be stated
in full** — terms, what is asked in return, why it is limited. In that case the offer *is* the
message and cutting it to fit a number makes the email vaguer, not shorter. A founding-member
offer written in full lands around 145 words and that is fine. Everything else still gets cut
before the offer does.

- Open with the verified signal as an observation, never a diagnosis of what they do wrong.
  «Vi que tienen siete procesos abiertos a la vez» reads as attention; «su selección es un caos»
  is an insult and a claim you cannot make. (The regional variant of that example follows
  whoever signs.)
- One idea per paragraph, blank line between them. **Never hand-wrap a line**: a paragraph is one
  line, and the renderer decides the width. Mixing wrapped and unwrapped paragraphs is what made
  one stretch across the whole window on 2026-09-21.
- One or two lines on what this unit does for a company like theirs, **attributed**: «creemos
  que», «lo que suele ayudar». Not a diagnosis of what is happening inside their office.
- **No meta-commentary about the email itself.** «No te voy a decir que…», «te escribo porque…»,
  «seré breve». It spends the reader's attention on the writer instead of on them.
- A line that gives permission to say no. It is in the brand's voice and it works.
- Close with **one** easy question. No link.
- End with a short sign-off, no name: the signature is appended.

**Touch 2** (day 4, last), 40-70 words:

- **One new angle** that was not in touch 1. Never repeat the hook.
- No second ask for the call. Close politely, leave the door open.
- Same sign-off rule.

**Subject 1**: under 50 characters, no emoji, no clickbait, something a person would open.
**Subject 2**: empty, so it threads as `Re:`.

No contact name is not a problem here: the email opens another way, because you are writing it.

---

## Step 3: The files

The campaign already exists and already has a name: **use its slug**, in the folder, in the
files and in `cold-cli`. Do not generate one from the date. Everything goes to
`offering/<unit>/campaigns/<slug>/`, next to the `campaign.md` that defines it.

`sequence.yml` is a shell; the content travels per lead:

**Check where the opt-out line lives before writing the sequence.** It must appear exactly
once, in both the text and the HTML part. Some signature files already carry it as their last
line, below the legal notice. When they do, the sequence must **not** append it again, or it
goes out twice.

```yaml
name: <campaign slug>
defaults:
  from_name: <quien firma>
  text_signature: |
    --
    <signatures/<slug>.txt>
    <the opt-out line, ONLY if the .txt does not already end with it>
  html_signature: |
    <signatures/<slug>.html, indented; no comments in that file>
    <the same, ONLY if the .html does not already carry it>
steps:
  - step: 1
    delay: 0
    subject: "{{subject_1}}"
    body: "{{body_1}}"
  - step: 2
    delay: 4
    subject: ""
    body: "{{body_2}}"
```

`leads.csv`: `email,first_name,company,subject_1,body_1,body_2`. Written with Python's `csv`
module, because bodies carry commas, quotes and newlines.

Both go to `offering/<unit>/campaigns/<campaign slug>/`, gitignored with the blueprint.

The opt-out line goes in **both** parts: whoever reads the plain text has to be able to
unsubscribe too. Whether it comes from the signature file or from the sequence, grep the
rendered output for it before showing anything: **zero is a legal problem and two is sloppy.**

---

## Step 4: Render and show

```bash
cold-cli campaign create --name <name> --sequence <path>/sequence.yml \
  --leads <path>/leads.csv --accounts <address> --env-file .env
cold-cli campaign preview <name> --env-file .env
```

Then, **for every lead, not a sample**:

```bash
cold-cli campaign preview <name> --render --lead <email> --env-file .env
```

Show each rendered email in full, **in batches of five**. Reviewing twenty at once is where
attention runs out, and the review is where the value of this command is. A campaign is created
as a **draft**: nothing is scheduled until it is activated, so this is safe.

Check before showing, and report anything found:

Per email:

- A `{{placeholder}}` that did not resolve. `--render` warns about stripped placeholders; treat
  any warning as a blocker, not a note.
- A banned word from `04-voice.md`, or an em-dash.
- A claim backed by neither block.
- A signal used as a diagnosis instead of an observation.

Per batch, and this is the one that replaces reading twenty hooks in a row:

- **Two interchangeable emails are a failure.** If swapping the company name in one makes it work
  for the other, neither was written for its prospect. Both get rewritten.
- **The same opening sentence twice** is the early symptom of that.

---

## Step 5: Approve

AskUserQuestion → `Activar la campaña` · `Cambiar algún correo` (free text; rewrite that hook and
render again) · `Dejarla en borrador` · `Borrarla`.

**Every correction the owner makes here is kept**, verbatim: what you wrote, what they changed it
to, and for which prospect. They are the input of Step 5b. Do not ask about them yet — asking
mid-review breaks the review, which is the part that matters.

On activate:

```bash
cold-cli campaign activate <name> --env-file .env
```

Say plainly what happens next: the campaign is scheduled, and **nothing leaves until `cold-cli
tick` runs**, which is the owner's call. Give the command.

---

## Step 5b: What the corrections taught you

This runs **by itself**, at the end of every run where the owner changed something. It is not a
command they have to remember: a tone that depends on someone remembering to record it never
gets recorded. Rules and method: `/adjust-tone`.

Take the corrections kept in Step 5 and look across them, not one by one:

- **A change made once** is probably about that prospect. Note it, propose nothing.
- **A change made three or more times in the batch** is a rule. The count is the evidence, and it
  goes into the observation: "corregido en 6 de 20".
- **The same word or construction removed every time it appeared** is a rule even at two, and it
  may belong in `04-voice.md` rather than in the person's file.

Then, **once, in one message**, propose what you learned: the rule, personal or brand, what it
merges with or contradicts, and the verbatim examples behind it. Follow `/adjust-tone` Steps 2 to
5 for the wording, the 10-rule cap and the conflict handling.

**Nothing is written without a yes.** Automatic means it is proposed without being asked for, not
that the blueprint changes on its own: that rule does not bend for convenience.

If the owner changed nothing, say nothing. Silence is information: the tone held.

---

## Step 6: Record

Only after activating:

- `prospects.csv`: `cadence=email-2`, `next_touch_on` = the first send date. **`status` stays
  `lead`**: it becomes `contacted` when a touch actually goes out, not when it is scheduled.
- `campaign.md`: `status: active`. A campaign is born `draft` — defined but not in flight — and
  becomes `active` here, when its messages are actually scheduled. Nothing else moves it.
- `events.csv`: one `draft_created` per prospect, with the campaign name, `by=agent`.
- Save the rendered emails under the campaign folder, so what was written can be read back.

> **Registrar el envío es un paso aparte.** `cold-cli tick` sends; `/mail-sync` and the owner
> record it. A tracker that says "enviado" about something that never left is worse than an empty
> one: the cadence, the follow-ups and the numbers are all computed from it.

---

## Step 7: Summary

> **Campaña `<name>` lista.** N prospectos · 2 toques (días 0 y 4) · tope N/día.
> Excluidos: [reasons and counts].
> No ha salido nada todavía. Para enviar lo que toque hoy: `cold-cli tick --env-file .env`
> **Después:** `/mail-sync` para traer las respuestas.

---

## `--linkedin`

No engine and no scheduling. Produce, per prospect, the invitation note (under 250 characters,
who you are and the verified signal, no pitch), the day-0 message (max 60 words, ending in one
easy question, no links) and the day-7 close (max 40 words). Save them as
`drafts/<key>/linkedin-{1,2,3}.md`, write `cadence=linkedin-3` and `next_touch_on`, and **show
them all** before anything happens — same rule as email, not a sample.

Once approved, the touches are executed one at a time through `tools/linkedin.py`, which drives
the Chromium the owner already has open and logged in. Design and limits:
`tools/linkedin.py`. What this command must respect:

- **Never run it with `--send` on your own initiative.** Print the command for each prospect and
  let the owner decide. Without `--send` the tool navigates and shows what it would do.
- **One prospect per call.** No loops over the tracker: the pauses and the daily caps exist to
  keep the rhythm irregular, and a loop defeats them.
- **The tool writes the event**, because it is what performed the click. Do not also write it.
- **If it stops, it stops.** A missing selector, a captcha or a limit notice means the page
  changed or LinkedIn is pushing back. Report the message as-is; never retry, never look for a
  similar button.

```
.venv/bin/python tools/linkedin.py invite <key> --unit <unit> --note-file <path>          # dry
.venv/bin/python tools/linkedin.py invite <key> --unit <unit> --note-file <path> --send   # real
```

A prospect with no `linkedin_url`, or one in `suppression.csv`, is not opened at all.

---

## Safety rules

1. **Nothing is sent here.** Not one message, not even to the test address.
2. **The gate is not negotiable.** No verified identity, no campaign.
3. **Every email is shown rendered before approval.** Not a sample: all of them.
4. **Three blocks only**: SELLER from the blueprint, PROSPECT from the tracker, VOICE from
   `04-voice.md`. A fact from anywhere else is invented.
5. **Suppression wins.** An address or domain in `suppression.csv` never enters a campaign.
6. **Scheduled is not sent.** `status` stays `lead` until a touch actually goes out.
7. **An unresolved placeholder is a blocker**, never a cosmetic problem.
8. **The opt-out line goes in both the text and the HTML signature.** A reader of the plain-text
   part has to be able to unsubscribe too.
9. **Nothing internal leaves**: no costs, no floors, no margins, no client names from the catalog.
