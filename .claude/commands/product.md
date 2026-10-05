# /product - One Unit in Depth, From Sales and Marketing

You learn what a product actually is, past the category it falls into. `unit.md` holds the short
card `/setup` wrote from the website; this is the long answer that everything else writes from.

Framework files are in English; the study is in the company's
`content_language`.

---

## Arguments

```
/product <unit>              study it, or carry on where it was left
/product <unit> <section>    go straight to one section: que-es · capacidades · como-se-cuenta
                             · comparan · demostrable · desajustes
/product                     list what each unit has studied and what is missing
```

---

## Step 0: Load, and say what is missing

Read `offering/<unit>/unit.md`, then `product.md` if it exists (else create it from
`templates/product.md`), then `hallazgos.md` (else `templates/offering/hallazgos.md`).

**Say how many findings are still `sin confirmar`, and name the worst one.** They are the point
of having studied the product: nobody goes looking for a file, so this is where they surface.

Show the state in one table: each section, `pendiente` / `en curso` / `hecho`, with the date and
the source it came from. That table **is** the resume point.

Then read, without asking: `documents/products/*` for this unit, `04-voice.md`, and `icp.md` if
it exists (their pain is half of what makes a capability worth naming).

---

## Step 1: How do we work today

**This is the first question every time, and the owner drives.** The flow is not linear on
purpose: they pick the sources, in any combination, and they can skip the interview entirely.

AskUserQuestion, multi-select, plus free text:

| Source | What it gives | What you must say about it |
|---|---|---|
| **Entrevista** | What only they know: why each thing exists, what clients ask for | One question per message, always with a draft to correct rather than a blank page |
| **`documents/products/`** | Deck, screenshots, a recorded demo | You read and propose; they correct. Say what you could not get from it |
| **Recorrer la app** | The product as a new user sees it | **They navigate, you look.** See Step 2 |
| **La web pública** | **Contrast only, never a source.** | It is what says "ATS con IA" and what got this wrong |

Then ask which section to work on, offering the first `pendiente` as the default.

Never run the whole questionnaire because it is there. A section studied well beats six half
answered, and the file keeps the rest for next time.

---

## Step 2: Walking the app

Two tools, two contracts. **Ask which one applies before starting**, because the answer depends
on whose data is in there.

| | `tools/peek.py` | `tools/explore.py` |
|---|---|---|
| What it does | Reads the tab. No click, no fill, no goto | Clicks, fills forms, walks routes |
| Use it on | Anything, including production with other people's data | An account the owner says can be written to |
| Who navigates | **The owner.** You read what they put in front of you | You do |

Default to `peek.py`. Reach for `explore.py` only when the owner has said this is a test account
and reading the screens is not enough to answer the section — which is usually section E, where
the question is whether the thing works, not whether the screen exists.

```bash
.venv/bin/python tools/peek.py --url <part of the url>      # read their tab
.venv/bin/python tools/explore.py --url <…> --map           # what can be clicked
.venv/bin/python tools/explore.py --url <…> --click "<text>" --read
```

`explore.py` refuses anything that sounds like deleting or cancelling unless `--force` is
written out. Leave it that way.

Then do the thing only you can do here: **describe the screen without knowing what it is for**,
and ask about what you cannot work out. That confusion is the same one a prospect has, and it is
worth more than a confident summary.

**Never copy real data out of the app.** Candidate names, client names, emails: none of it
enters the blueprint. You are describing what the product does, not what it contains.

**Prefer using the product over reading it.** Four screens of empty lists say less than one
real request to the thing: what it gives back is what proves the capability.
Where the product offers a way to do the thing, do the thing.

---

## Step 3: The sections

Work one at a time. Each ends with a proposal shown in full and written on a yes.

### A · Qué es y qué no es

The one that matters most, and the reason this command exists.

- **The category they put you in**: the word a stranger reaches for ("ATS", "CRM", "gestoría")
- **Why it falls short**: what the category does not cover and the product does
- **What it is instead**, in the owner's words

Push here. "It is more than an ATS" is not an answer yet; ask what it does that makes the word
wrong, and keep asking until there is something a stranger could repeat.

### B · Capacidades

Per capability, the thing that is almost never written down: **what work a person stops doing.**

> Not «scoring de candidatos 0-100 por IA».
> But «nadie lee sesenta CV para quedarse con seis, y los seis salen comparables entre sí».

For each one: what it does · what stops being done by hand · who notices · and whether it is
live, in beta, or planned. **The last field is a hard limit on what any email may promise.**

### C · Cómo se cuenta

Three different texts, and today one is used for all three:

| Length | For | Test |
|---|---|---|
| One line | A subject, a bio, a hallway | A stranger repeats it without looking |
| Three lines | An email, the top of the home | Says what it is, for whom, and what changes |
| A demo | A call | The order in which you show it, and what you show first |

Written in the brand's voice, banned words included.

### D · Contra qué lo comparan

What the buyer puts next to it: a competitor, a spreadsheet, a person, doing nothing. For each:
what they get there, what they do not, and **why the product is not that**. Never a claim that
`competitors.md` does not back.

### E · Qué se puede demostrar hoy

What can be shown working, and what cannot. Split plainly: live · beta · planned · not built.

This is the ceiling for `/outreach`, the website and any creative. «Beta es Beta» is a brand
rule, and this section is where it is enforced.

### F · Qué no cuadra fuera

The study wins over the website. Findings go to
**`hallazgos.md`**, one block each, not into `product.md`: that file describes the product,
this one lists what is wrong with it, and the two rot at different speeds.

- **The site says less than the product does** → a marketing task
- **The site promises more than the product does** → the urgent one. That reaches customers
- **What the product should do and does not** → this comes out on its own when you study a
  product to sell it

**Write each one so somebody else can reproduce it**: the exact screen, what was seen without
interpreting it, the steps, who it hurts, and **the concrete question the reviewer has to
answer**. A finding nobody can reproduce is a complaint.

Say plainly when something might be your own fault — a click that failed through automation is
not the same as a broken form, and marking that difference is what makes the list trustworthy.

This section is an output, not a footnote. Report it at the end of the run, out loud.

---

## Step 4: Propose, then write

Per section: show it in full, say which source each piece came from, and write on an explicit
yes. Update the state table and the date.

Say what it changes downstream: `/outreach` writes from `product.md` once section A or B exists,
and stops writing the website's one-liner.

---

## Safety rules

1. **Never invent a capability.** If the interview, the material and the screen do not say it,
   it does not exist. `[Inferred from <source> — review before relying on this]` for anything
   worked out rather than sourced.
2. **Read before you drive.** `peek.py` by default; `explore.py` only on an account the owner
   has said is safe to write to, and never to delete anything.
3. **No real data leaves the app.** No candidate, client or contact from inside the product.
   Findings describe the behaviour, never the records it happened on.
4. **The website is contrast, never a source.** It is what got this wrong in the first place.
5. **What is not live cannot be promised.** Section E is a hard ceiling for every other command.
6. **One section well beats six half done.** Stop when the answers get thin and say so.
