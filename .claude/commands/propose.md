# /propose - Write What You Send Them, in the Right Register

You turn a diagnosis into something a client reads. **Which document that is depends on who
they are**: a friend in the first round does not get a rate card, and an inbound lead who asked
for a quote does not get a vague note.

Framework files are in English; the proposal is in
the blueprint's `content_language`.

---

## Arguments

```
/propose <slug>            pick the type and write it
/propose <slug> <type>     nota · diagnostico · proyecto · programa
/propose                   every case and what has been sent to it
```

---

## Step 0: Load

`clients/<slug>/caso.md`, `diagnostico.md`, `preguntas.md`, the summaries' "what was promised"
section, and `proposals/` to see what already went out.

Then: `04-voice.md`, `03-people.md` (who signs, and whether `approvals: true`), the unit's
`unit.md` (deliverables and **excludes**), and the rate card — `05-pricing.md` plus the unit's
`pricing.md`.

**`pricing.md` is internal.** Floors, hourly costs and margins never appear in a client
document. You read it to know the price; you copy only the price.

---

## Step 1: Which type

Four, and they are a closed set. Propose one from `relation` and from where the case stands, say
why, and let the owner change it.

| Type | Who it is for | Money | Ends in |
|---|---|---|---|
| **nota** | Someone close or a referral, first round | **No.** Its absence is a decision, written down | A conversation, with a date |
| **diagnostico** | Someone who already wants it looked at properly | Yes, the rate card price | Accepting the diagnosis |
| **proyecto** | After the diagnosis, with the numbers in hand | Yes, the band from the rate card | A start date |
| **programa** | The three-months-free deal, as offered to the five consultancies | No price, **but there is a deal** | Who joins and when |

The type changes over time: a normal case starts at `nota` and ends at `proyecto`. Each proposal
keeps its own date in `proposals/YYYY-MM-DD-<type>.md`, so the second does not quietly
contradict the first. Read the previous one before writing the next.

If something is needed that is not on this list, it gets added to the plan first. It is not
improvised in a conversation.

---

## Step 2: The gates

Run them before writing a line. Each failure is reported, never worked around.

| Gate | Rule |
|---|---|
| **Price blocked** | A row in `preguntas.md` blocking `precio` and unanswered → no price. Write what is missing instead, and say it out loud |
| **Unconfirmed figure** | A figure marked doubtful in a summary, or `[estimado]` in the diagnosis, may not carry a price. Confirm it or leave the price out |
| **nota carries no price** | Not a number, not a band, not "around". Check the finished text |
| **No invented terms** | No new price, no discount, no payment plan, no deadline that is not in the rate card or in `unit.md` |
| **What was promised binds** | The proposal may not contradict what was said on a call. Where it has to, say so explicitly and change it on purpose |
| **For sale only** | `for_sale: yes` in `unit.md`. Beta is beta |
| **Approvals** | `approvals: true` in `03-people.md` → pricing, public copy or a new client goes to the person named there before it goes out |

---

## Step 3: Write it

From `.claude/templates/client/propuesta.<type>.md`. Voice is `04-voice.md` and it is not
negotiable: short sentences, one idea per line, `tú` to the reader, real numbers, no empty
adjectives. Banned words are banned — revolucionario, líder, el mejor, ilimitado, mágico,
disrupción, 10x garantizado — and no em-dashes.

Signature from `03-people.md` and `signatures/`, in the variant of whoever signs.

### The nota, in more detail

It is the one that goes wrong most easily, because being friendly is cheap and being useful is
not. It carries:

- **The diagnosis figures**, with their provenance. Leaving the price out is not the same as
  talking without numbers.
- **The scope, in writing.** This is the uncomfortable line and the one that has to be there:
  *this is me looking at it and telling you what I see, not building it*. With someone close,
  whatever is not written down gets assumed, and three weeks later you are doing three times the
  work for free.
- **What happens if they want to go on**: not a price, just that the next thing is a real
  diagnosis and that is where numbers come in. The money then has somewhere to arrive instead of
  appearing out of nowhere.

**The price is omitted, never lowered.** If they ask what it costs, they get the rate card. A
discount for a friend is not a command's decision.

---

## Step 4: Show it, then write it

Show the document **in full** — it is going to a person outside the company. Alongside it, say:
the type and why, where each figure came from, what was deliberately left out, and anything that
was promised on a call that this touches.

On an explicit yes: write `proposals/YYYY-MM-DD-<type>.md`, add it to `proposals:` in `caso.md`,
move `status`, and update `updated`.

**Nothing is sent.** No mail, no draft, no calendar invite. The proposal leaves by the usual
channel, by hand, because what reaches a client is decided by a person.

---

## Safety rules

1. **The price comes from the rate card or it does not exist.** No new price, no discount, no
   band invented for the occasion.
2. **The floor, the hourly cost and the margin never leave `pricing.md`.**
3. **No price on top of an unconfirmed figure.** Say what is missing.
4. **A nota has no price**, and that is a recorded decision, not an oversight.
5. **A free programme still has a written deal**: what you give, what you ask for, for how long,
   and what happens when it ends.
6. **What was said out loud binds what gets written.**
7. **Voice is law**, banned words included.
8. **This command does not send.** It shows, it writes on a yes, and it stops there.
