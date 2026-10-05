# /client - Open a Client Case and Bring Its Material In

You hold what a client told you: a recording, a transcript, a PDF, a thread, a name scribbled
after a call. This command turns that into a case anyone can pick up later, and leaves it ready
for `/diagnose`.

The rest of the repo looks inward. This is the only place where somebody else's company lives.

Framework files are in English; everything written into
a case is in the blueprint's `content_language`.

---

## Arguments

```
/client                          list the cases and where each one stands
/client <anything>               a transcript, an audio file, a PDF, a URL, a name, a sentence
/client <slug>                   re-read a case: new material in, inventory out
/client rename <old> <new>       the case was called something else, or turned out to be someone else
/client merge <from> <into>      two folders, one company
/client research <slug>          study the company itself: who they are, what they did before,
                                 what is said about them, how they like things done, who decides
/client email <slug>             draft a message to them. Shows it, never sends it
/client email <slug> confirm     read the Sent folder and store what actually went out
/client email <slug> pull        bring their reply in
```

**There is no single way in, and that is the point.** A case starts from whatever you happen to
have. The first job of this command is working out what you were handed.

---

## Step 0: What did you get

Do not ask before looking. Work it out, say what you concluded, and only ask when it is
genuinely ambiguous.

| What came in | What you do |
|---|---|
| Path to `.m4a` `.mp3` `.wav` `.ogg` `.opus` `.mp4` | Transcribe it (Step 2), then summarise |
| Path to `.vtt` `.srt` `.txt` `.md` that reads like a conversation | It is a transcript: Step 2 |
| Transcript **pasted into the message** | Same, written to `transcripts/<uuid7>.md` yourself |
| Path to a `.pdf`, a deck, a spreadsheet, an image | Material, not a conversation: it lands in `material/` |
| A URL | Their website or a job board. Read it, record it as a source |
| A company or person's name | No material yet. Open the case and say what is missing |
| A key from `prospects.csv` | The prospect is becoming a case. Carry over what the tracker knows |
| Nothing | `list` |

A free sentence (`/client mira esta transcripción de la llamada con X`) is normal input: read it
for the path, the name, and what they want out of it.

---

## Step 1: The case

Load `clients/<slug>/caso.md` when the slug is known. Otherwise work out which case this belongs
to from what you just read, propose it, and ask only if two are plausible.

**A new case does not need a client.** Material arrives before identity: a conversation at an
event, a PDF with no letterhead, a call with someone who has not said yet which company they
speak for. Open it anyway:

- Slug when the name is known: the company, lowercased, no accents (`acme-sl` → `acme`).
- Slug when it is not: `YYYY-MM-DD-<the clue you have>` (`2026-10-02-consultora-bcn`).

Create from `.claude/templates/client/caso.md` and fill what you can. Ask for the rest **only
when it changes what gets written**, one question at a time:

| Field | Why it matters |
|---|---|
| `relation` | `conocido` · `referido` · `frio` · `entrante`. Decides the proposal type later, and whether money appears in the first round |
| `unit` | Which unit is on the table, if any. Only ones with `for_sale: yes` |
| `prospect_key` | The row in `prospects.csv`, when there is one. **The case points at the tracker; the tracker never points here** |

That last rule is what makes `rename` free. Nothing outside a case may reference its folder.

---

## Step 2: Material in

### Audio

```bash
.venv/bin/python tools/transcribe.py <audio> --out clients/<slug>/transcripts/
```

Runs on this machine; the recording does not leave it. Default model is `small`; use `--model
medium` when the conversation is full of figures, because that is what a small model gets wrong.
It writes `transcripts/<uuid7>.md` with frontmatter and the automatic-transcription warning
inside. Leave that warning there.

### A transcript you already have

Write it to `transcripts/<uuid7>.md` from `.claude/templates/client/transcript.md`, keeping the
original text intact. Get the id with:

```bash
.venv/bin/python tools/id7.py
```

**Never edit the words.** Fix nothing, tidy nothing, cut nothing. The transcript is the record;
everything you think it means goes in the summary.

### Everything else

Into `material/`, read in place: `.pdf` with `pdftotext`, images as images, `.csv` as a table.
A mail thread can come from the tracker, and their website from `tools/peek.py --open <url>`.

---

## Step 3: The summary, which is the actual work

One summary per transcript, `summaries/<uuid7>.md`, from
`.claude/templates/client/resumen.md`. Its own id, pointing back at the transcript's.

Five things come out of a conversation, and they are not equally easy:

1. **The problem in one sentence**, in their words. If the call never got there, write that it
   never got there. That is a finding, not a blank to fill in.
2. **What was discussed**, by topic, each with the minute it happened at.
3. **Figures that were said**, literally, with the minute and whether they are clearly audible.
   A machine transcript mishears numbers, and numbers are the whole point of a diagnosis.
4. **What was proposed or promised**, by either side. This is the one that binds: a written
   proposal may not contradict what was said out loud on a call.
5. **Commitments and what was left hanging.** The loose ends become rows in `preguntas.md`.

Everything carries `[mm:ss]`. A summary nobody can trace back is an opinion.

**Say nothing the transcript does not.** No reading between lines, no filling a gap with what
usually happens. What you work out rather than hear is labelled `[Inferred from <source> —
review before relying on this]`, and it is the exception.

---

## Step 4: `fuentes.md`

The inventory: every transcript, summary and file, with what it is, its date, who speaks, and
one line on what it gives. Plus the quotes worth keeping, and **what is missing** — the gaps that
stop you from measuring anything, which become `preguntas.md`.

This is how a person finds their way around a folder full of UUIDs.

---

## Step 5: Report, then hand over

Show, in this order: what came in, what the case now knows, the problem in one sentence, what
was promised out loud, and what is missing to be able to measure.

Update `caso.md`: `status`, `updated`, the next step, and the Historial line.

Then say what comes next, which is almost always `/diagnose <slug>`.

---

## `research` — the dossier on the company

The case knows what they want. This is about **who they are**, and it is a different job: it
reads widely, it writes five files, and it is re-run whenever new material shows up.

Separated from `caso.md` for the same reason `product.md` is separated from `unit.md`: the card
has to stay short, and a dossier never stops growing. One file, one job.

| File | What it answers |
|---|---|
| `empresa.md` | Who they are: legal identity, what they do, where, how the group is built, which systems they run |
| `antecedentes.md` | What they did before with outsiders: projects, suppliers, what they dropped |
| `reputacion.md` | What is said about them: press, reviews, awards, what they brag about and what they avoid |
| `como-trabajan.md` | How they decide, how they buy, what they value, what annoys them, how they speak |
| `personas.md` | Who is who, and who actually signs |

### How it runs

Fan out, one search per axis, the way `/competitors` does. Each finding comes back with its URL
and the date it was read, or it does not come back at all.

Start from what the case already holds — the transcripts and the summaries say more about how
they work than any website — and only then go outside: their own site in every language they
publish, their legal notice, their careers and press pages, their shop, the registry, their
suppliers' case studies, trade press, reviews.

**Check the domain you were given before concluding anything from it.** A domain that fails to
load may be a redirect with no certificate rather than a company with no website: follow the
`http` redirect before writing that they have no site. That happened on the first real run.

### Rules that are not negotiable

1. **Source and date on every line.** No source, no line. Anything worked out rather than read
   is labelled `[Inferred from <source> — review before relying on this]`.
2. **Public and identifiable sources only.** No anonymous screenshots, no gossip, no scraping
   behind a login.
3. **People appear by professional role only.** What they do and who they report to, when it is
   published. Nothing personal, nothing about anyone who has no part in this.
4. **Contradictions stay visible.** Two sources disagreeing get both versions with both dates.
   Nothing is averaged, and the nicer number is not the one that wins.
5. **What is deduced is never quoted back to them.** `04-voice.md` is explicit: what we worked
   out from their guts decides what we do, and never appears in a message. Here it is written
   down to decide with; out there it stays unsaid.
6. **Say what was not looked at.** Every file ends with what is still unread. A dossier with
   holes is normal; one that hides them is not.

---

## `email` — the correspondence of a case

A case needs letters: asking for the access that unblocks a diagnosis, sending a note, answering
a question. They live in `emails/<uuid7>.md`, one per message, in and out.

**This is not outreach.** `/outreach` is cold, belongs to a campaign, is sent by the engine and
leaves its trail in `prospects.csv` and `events.csv`. A case letter is written by hand, sent by
a person, and **never touches the tracker**. Do not mix the two.

### `email <slug>` — draft

Content comes from the case: usually the open rows of `preguntas.md`, in the order that matters,
and never all of them because a list of nine questions does not get answered. Voice is
`04-voice.md`, signature and regional variant from `03-people.md` and `tone/<slug>.md`, and the
sending mailbox is one of `MAILBOX_SLUGS` in `.env` — ask which when it is not obvious.

What the type of case allows applies here too: with `relation: conocido`, in the first round,
**no price**. And nothing that `/propose` would gate is smuggled into a letter.

Write it from `.claude/templates/client/email.md` with `status: borrador`, show it in full, and
stop. **This command does not send.** No SMTP, no `cold-cli`, no draft in the mail client. The
person sends it, because what reaches a client is a person's decision.

### `email <slug> confirm` — what actually went out

The text that leaves is often not the text that was written: a line gets rewritten in the mail
client on the way out. So the version that counts is read back from the server, not remembered.

```bash
.venv/bin/python tools/imap_fetch.py --mailbox <slug> --folder sent \
  --to <address> --subject "<part of it>" --days 14
```

Then, in the email's file: `sent`, the real `message_id`, and `verbatim: sí` when the body
matches the draft. When it does not, keep the draft where it is, add **Lo que salió** with the
body the server returned, and list what changed. A question that disappeared on the way out is
not a detail: `answers:` and `preguntas.md` have to be corrected, or the case will think it
asked something it never asked.

**If the message is not in Sent, it is not marked as sent.** Say so. Maybe it went from another
mailbox, maybe the provider does not keep a copy, maybe it was never sent. Any of those is worth
knowing, and none of them is fixed by assuming.

### `email <slug> pull` — their reply

Same tool against the inbox, matched by `in_reply_to` or by address. It lands as
`emails/<uuid7>.md` with `direction: in`, and then the real work: every answer that resolves a
row in `preguntas.md` moves there as `respondida [date]`, with the quote going into
`fuentes.md`. That is what unblocks `/diagnose`.

`/mail-sync` does not do this: it matches messages against `prospects.csv`, and a case may well
have no prospect at all.

---

## `rename` and `merge`
**rename** — the name changed, or it turned out to be the parent group and not the subsidiary
(Talent Areté and talent wins, in this repo's own history). Move the folder, update `slug` and
`client` in `caso.md`, add a Historial line with the date and the reason. Nothing else: no
reference outside the case points in.

**merge** — two folders, one company. Move `material/`, `transcripts/` and `summaries/` across
(the UUIDs do not collide, that is why they are UUIDs), append the source's `fuentes.md` to the
target's, redo the diagnosis instead of stitching two, and leave `MOVIDO-A.md` in the old folder
with the destination and the date. **Never delete the old folder.**

Both show the plan and run on an explicit yes.

---

## Safety rules

1. **Real people are in here.** `clients/**` is gitignored, stays local, counts as third-party
   data in `/export`, and no name from it enters the blueprint.
2. **Recording a call is the recorder's decision.** The repo assumes consent was given. No
   command can check that, which is exactly why it is written down.
3. **The transcript is never edited.** Interpretation lives in the summary, with timestamps.
4. **Nothing is invented.** A figure that was not said does not exist. Anything deduced is
   labelled, and anything missing goes to `preguntas.md` instead of being guessed.
5. **A figure heard by a machine is a figure to confirm.** Mark the doubtful ones in the summary;
   `/propose` refuses to price on an unconfirmed number.
6. **Only what is for sale gets floated.** Check `for_sale` in the unit's `unit.md` before
   putting any product in front of a client. Beta is beta.
7. **No command here sends anything.** A letter is drafted, shown, and sent by a person. The
   copy that counts is read back from the Sent folder, never assumed.
8. **A case letter is not outreach.** It never enters `prospects.csv`, `events.csv` or a
   `cold-cli` campaign.
9. **Propose, then write.** Every file is shown before it is created, including the summary.
