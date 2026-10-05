# /diagnose - Measure One to Three Processes and Say Whether It Pays

You take what a case knows and turn it into the thing actually being sold: a measured answer to
whether automating something is worth it. **Including when the answer is no.**

`/client` brings the material in. This reads it, applies the four-step method the rate card is
built on, and writes `diagnostico.md` and `preguntas.md`.

Framework files are in English; the diagnosis is in the
blueprint's `content_language`.

---

## Arguments

```
/diagnose <slug>              work on the case, or carry on where it was left
/diagnose <slug> <process>    straight to one process
/diagnose                     every case, what it has measured and what is missing
```

---

## Step 0: Load, and say what you are missing

Read, in this order: `clients/<slug>/caso.md`, `fuentes.md`, every `summaries/*.md`, then
`diagnostico.md` and `preguntas.md` if they exist. Go to a transcript when a figure needs
checking; do not read them all for the sake of it, the summaries point at the minutes.

Then the company side: `02-offering.md`, the `unit.md` of whatever is on the table, and
`offering/consultoria-ia/pricing.md` for the method.

Show a table of the processes already measured, their state, and **the unanswered questions that
block a price**. That table is the resume point.

---

## Step 1: Which processes

One to three. That is what the service is, and three measured properly beat seven named.

Propose them from the summaries, with the sentence that justifies each one and its minute. The
owner picks. A process nobody described in detail is a candidate for `preguntas.md`, not for
measuring.

---

## Step 2: The four steps, per process

Straight out of `offering/consultoria-ia/pricing.md`. Each one, in order:

### 1 · Measure

Frequency, duration, people, errors. From their data, never from a sector average.

**Every figure carries where it came from:**

| Tag | When |
|---|---|
| `[dicho por <who> el <date>]` | It was said, and it is in `fuentes.md` |
| `[documento: <id>]` | It is in a file in `material/` |
| `[estimado — supuesto: <which>]` | We put it there. It also gets a row in `preguntas.md` |
| `[Inferred from <source> — review before relying on this]` | Worked out, not said |

An untagged number is a bug, not a detail.

### 2 · Cost today against saving

Write the arithmetic out, not just the result: frequency × duration × hourly cost. Where the
hourly cost comes from, and whether it is theirs or an assumption.

Then the part people skip: **what stays manual anyway.** A saving that assumes the whole process
disappears is a saving that will not happen.

### 3 · Failure signals

What would make this not work, said before starting and not afterwards: scattered data, nobody
owning the process, too little volume, exceptions that are actually the rule, a person whose job
this is.

### 4 · Verdict

`compensa` · `no compensa` · `no se puede decir todavía`, each with two lines of why.

**"No compensa" is a good outcome.** It is literally the company's first line: *no te vendemos
IA, te decimos si te compensa*. A command that always finds something to automate turns the
diagnosis into a sales form and throws away the only thing that makes it different. Write a no
with the same care as a yes.

"Can't say yet" is honest too, as long as it names what is missing, and what is missing becomes
a question.

---

## Step 3: Where to start, and what you would not touch

Order the processes that pay off, and say why that one first: low effort and clear saving, it
unblocks the others, or it simply hurts most.

Then **what you would not touch**, which is the section that makes the rest credible. It is
never left empty to look good.

---

## Step 4: What of ours would fit

Only units with `for_sale: yes` in their `unit.md`. Nothing in beta, nothing in testing, nothing
being restructured. Check the file, do not trust your memory of it.

If what fits is something we do not sell, say so plainly: that is a finding about the offering,
and it is worth more than a forced fit.

No price here. Pricing is `/propose`.

---

## Step 5: `preguntas.md`

Every hole becomes a row: the question as you would ask it, what changes depending on the
answer, and **what it blocks** — `precio`, `alcance`, `go/no-go`, or `nada`.

While a row blocking `precio` is unanswered, `/propose` will not write a price. That is the
mechanism, and it only works if the rows are honest.

Assumptions go in their own table with what happens if they are wrong. **An assumption is not
promoted to a fact because a week went by.**

---

## Step 6: Propose, then write

Show the diagnosis in full, process by process, saying where each figure came from. Write on an
explicit yes. Update `caso.md`: `status`, `updated`, the next step.

Report out loud: the verdict per process, how many figures are still `[estimado]`, and which
questions block a price.

---

## Safety rules

1. **A figure that was not said does not exist.** Nothing gets rounded into being true because
   it sounds plausible. This is the rule the whole thing rests on: an invented number ends up in
   a quote, and the quote reaches a client.
2. **Every number carries its provenance**, in the file, not in your head.
3. **An assumption stays an assumption** until somebody answers the question.
4. **"No compensa" is a valid answer**, written with its reasons.
5. **Only what is for sale gets proposed.** `for_sale: yes`, checked in the file.
6. **Nothing from here goes into the blueprint.** Client names, their people, their numbers:
   they stay in `clients/`.
7. **Propose, then write.**
