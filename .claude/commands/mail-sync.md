# /mail-sync - Bring the Mailbox Into the Tracker

You read what arrived in the outreach mailboxes, work out which prospect each message belongs to,
say what kind of answer it is, and **propose** the changes to the tracker. You never reply, and you
never write to a file before the owner says yes.

This is the command that keeps `prospects.csv` honest. Without it the tracker only knows what was
sent, which is the half that flatters us.

Framework files are in English. Conversation and content follow the blueprint's `content_language`.

---

## Arguments

```
/mail-sync                  everything new since the last run
/mail-sync --days 7         last 7 days, ignoring the saved mark
/mail-sync <unit>           only prospects of that unit
/mail-sync --dry            read and report, propose nothing
```

---

## Step 0: Read the mailbox

```bash
.venv/bin/python tools/imap_fetch.py            # add --days N when asked for a window
```

It prints JSON and **marks nothing as read**. Do not move the high-water mark yet: `--commit` comes
at the end, after the owner approves, so an interrupted run re-reads instead of losing messages.

No `.venv` → `tools/README.md`. A mailbox reporting `skipped: sin credenciales` is named in the
summary, not silently ignored. An `error` is shown with the server's own words.

Then load `offering/*/prospects.csv`, `offering/_shared/events.csv` and `suppression.csv`.

---

## Step 1: Match each message to a prospect

In this order, because the cheap signal is also the weakest:

1. **Ask the engine.** `cold-cli log --json` and `cold-cli campaign status <name>` already say
   which lead replied: `cold-cli` matches the reply to its own send by thread, and it is the one
   holding the `Message-ID` it generated. This repo never sees that id, so **do not try to match
   by thread from `events.csv`** — it does not record one. Trust the engine here.
2. **Address.** `from` equals a prospect's `email`. This is what catches replies the engine did
   not associate, and what works for mailboxes not driven by a campaign.
3. **Domain.** `from_domain` matches a prospect's website or email domain. A colleague answering
   for the person you wrote to is normal and this catches it. Say the match was by domain, and
   which prospect you are guessing.
4. **No match** → leave it alone. It is not outreach, it is the owner's mail.

Never match on the person's name, and never on subject alone: "Re: propuesta" is not evidence.

---

## Step 2: Say what kind of answer it is

The reader already flags the mechanical shapes: `bounce`, `auto_reply`, `automated`. Respect them.
An `auto_reply` is **not** a reply: the prospect has not read anything, so the cadence must keep
going and the status must not change.

For everything else, read the body and pick one:

| Class | What it looks like | What follows |
|---|---|---|
| `interested` | wants to talk, asks for a call, says send more | status `replied`, cadence stops |
| `question` | asks something before deciding: price, how it works, security | status `replied`, cadence stops |
| `not_now` | interesting but not this quarter, ask me in N months | status `replied`, cadence stops, note when to return |
| `not_interested` | a clear no | status `lost`, cadence stops |
| `unsubscribe` | asks to stop: BAJA, no me escribas, remove me | **suppression first**, status `do_not_contact` |
| `referral` | not me, talk to X | status `replied`, and the new contact is proposed as a row |
| `bounce` | the reader said so | permanent (5.x.x) → `email_status=bounced` and suppress; temporary (4.x.x) → note it, change nothing |
| `unclear` | you cannot tell | propose nothing, show it to the owner and ask |

**A reply that names a date and a time is checked against the calendar.** Read the signer's
calendar through the Google Calendar connector and say, on the same line, whether
an event already exists for it. **Never create it here**: an invitation reaches the prospect, and
this command does not send. Creating it is `/answer`'s job, inside an approved reply. A meeting
that was agreed in writing and sits in nobody's calendar is the most expensive thing this command
can let through.

**An unsubscribe outranks everything else in the same message.** Somebody who writes "me interesa
pero quítame de la lista" is asking to be removed, and that is what happens.

Quote the sentence that decided the class. One line, verbatim, from their message. If you cannot
quote it, the class is `unclear`.

---

## Step 3: Propose

One message. Grouped by what it changes, not by mailbox:

```
Mail-sync · <date> · <N> mensajes nuevos, <M> emparejados

RESPUESTAS
  <company> · <person>
    "<quoted sentence>"
    → interested · lead → replied · cadencia detenida
    → propone jueves 24/09 12:00 · SIN EVENTO en el calendario
    (uid 412, emparejado por hilo)

BAJAS
  <company> — "quítame de la lista" → suppression.csv + do_not_contact

REBOTES
  <address> — 5.1.1 permanente → email_status=bounced + suppression

SIN CLASIFICAR (necesito que mires)
  <from> — "<subject>"

NO ES OUTREACH (sin tocar)
  4 mensajes: boletines y notificaciones
```

AskUserQuestion → `Aplicar todo` · `Elegir cuáles` (free text) · `No aplicar nada`.

---

## Step 4: Write

Only what was approved, in this order so an interruption cannot leave a suppression unrecorded:

1. `offering/_shared/suppression.csv` — unsubscribes and permanent bounces. **Append only**; a
   removal is a new row with `reason=reactivated`, never a deletion.
2. `offering/<slug>/prospects.csv` — `status`, `email_status`, `next_touch_on` (empty when the
   cadence stops), `updated_on`.
3. `offering/_shared/events.csv` — one `reply` or `bounce` row per message, with the uid and the
   classification in the summary, `by=agent`.
4. `cold-cli` — cancel the pending cadence for whoever replied:
   `cold-cli lead cancel <email>` where available, otherwise report which campaign to stop and
   let the owner do it. Never leave a stopped prospect with touches queued.
5. `tools/imap_fetch.py --commit` — move the high-water mark. **Last**, and only now.

Write CSVs with Python's `csv` module: bodies contain commas, quotes and newlines.

---

## Step 5: Summary

> **Mail-sync hecho.** N mensajes · M emparejados · respuestas: interesados A, preguntas B,
> noes C · bajas D · rebotes E.
> Sin clasificar: F (pendientes de que los mires).
> **Siguiente:** [who is waiting for an answer, by name].

Answering is not this command's job. Say who is waiting; the owner decides what goes back.

---

## Safety rules

1. **Never reply, never forward, never send.** This command only reads.
2. **Never mark as read**, never move or delete a message. The mailbox belongs to a person.
3. **An unsubscribe is written before anything else** and is permanent.
4. **An auto-reply is not a reply.** Nothing changes and the cadence continues.
5. **No quote, no class.** Guessing what someone meant is how a "no" becomes a follow-up.
6. **The high-water mark moves last**, after the writes are approved and done.
7. **Propose, then write.** Including suppressions: the owner sees them, then they happen.
8. **A message that matches nobody stays untouched.** Personal mail is not tracker material.
