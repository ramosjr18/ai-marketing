# /calendar-sync - The Calendar as a View of the Outreach

You mirror what the engine has scheduled onto the signer's Google Calendar, so a month view answers
"what are we doing this week" without opening a database. You reconcile, you never invent, and
the calendar never decides anything.

Framework files are in English. Event titles and descriptions follow the blueprint's
`content_language`.

---

## Arguments

```
/calendar-sync                  reconcile the window: 7 days back, 30 days forward
/calendar-sync --days 60        a wider window forward
/calendar-sync --dry            say what would change, change nothing
/calendar-sync <unit>           only that unit's sends
```

---

## Step 0: What the engine says

```bash
cold-cli campaign list --json
sqlite3 ~/.cold-cli/data.db "SELECT s.id, s.status, s.send_at, s.sent_at, s.step_number,
  l.email, l.company, c.name FROM scheduled_sends s
  JOIN leads l ON l.id = s.lead_id JOIN campaigns c ON c.id = s.campaign_id
  WHERE s.send_at BETWEEN ? AND ?;"
```

LinkedIn touches are not in the engine: they live in `offering/<slug>/prospects.csv`, rows with
`channel=linkedin` and a `next_touch_on` inside the window.

**The engine and the tracker are the source. The calendar is the reflection.** If they disagree,
the calendar is rewritten. Never the other way round, and nothing here ever changes a send.

---

## Step 1: What the calendar already has

```
list_events(calendarId: <the outreach calendar>, startTime, endTime, fullText: "cold-cli:send:")
```

Every event this command creates carries its identity on the first line of the description:

```
cold-cli:send:42
acme · consultoras-es-arranque · toque 2
hola@ejemplo.es
```

For LinkedIn, the marker is `linkedin:<unit>:<key>:<touch>`; search it the same way. An event
without a marker was put there by a person: **never touch it**.

---

## Step 2: The difference

| In the engine | Its event | What you do |
|---|---|---|
| `pending`, no event | — | create |
| `pending`, event at another time | engine rebalanced | move |
| `sent`, delivered | exists | title gets `✓` in front |
| `sent`, then bounced | exists | title gets `✗` and the description says it never arrived. A row that says `sent` and a mailbox that says 550 are both true, and the calendar shows the second |
| `skipped` (replied, bounced, unsubscribed) | exists | **delete**. What will not happen is not shown |
| nothing | event with a marker | delete: leftover from a closed campaign |

Idempotent by construction: run it twice in a row and the second run changes nothing. If it
does, the marker is wrong and that is the bug to fix.

---

## Step 3: The event

```
summary            → <Company> · t<N>              ("✓ → " once it has gone out)
start/end          send_at, 5 minutes
availability       AVAILABILITY_FREE
attendees          none
notificationLevel  NONE
overrideReminders  []
colorId            one fixed colour for outreach, never the one meetings use
description        the marker block from Step 1
```

A touch whose prospect has since replied keeps its `✓` and gains one line in the
description: `contestó, cadencia detenida`. It happened; the calendar says what happened.

`t1`/`t2` and not `toque 1`: the month view truncates, and what has to survive the cut is the
company name.

LinkedIn touches carry the hour the tracker does not have: `next_touch_on` is a date, so they go
at **10:00**, inside the channel's 09:00-17:00 window, and the
description says the hour is indicative.

---

## Step 4: Propose, then write

Show the difference grouped by day, then `AskUserQuestion`:

```
Calendario · 23/09 · ventana 16/09 → 23/10

LUN 28  crear 17 eventos · toque 2 · acme consultoras ES
        09:00 → Empresa Uno · 09:01 → Empresa Dos · … (17)
MAR 22  marcar ✓ 20 envíos ya salidos
        borrar 2: AMG Human y AddYou rebotaron

Sin tocar: 0 eventos ajenos en la ventana.
```

`Aplicar` · `Elegir` · `No aplicar`. With `--dry` you stop here.

Creating events is one call each: twenty sends are twenty calls. Say how many you are about to
make before you make them.

---

## Step 5: Summary

> **Calendario al día.** N creados · M movidos · K marcados ✓ · J borrados.
> Reflejo del motor a las <hora>. **Vuelve a correrlo después de `/mail-sync`**: entre sesiones
> el calendario no se entera de nada.

---

## Safety rules

1. **No attendees, ever.** An outreach event with a guest emails the prospect. Only `/answer`
   creates events with guests, and only inside an approved reply.
2. **`AVAILABILITY_FREE` always.** Seventeen sends that block Monday morning make `/answer`
   believe there is no free slot, and no meeting gets proposed.
3. **An event without a marker is somebody's appointment.** Read it, never write it, never
   delete it.
4. **The calendar never changes a send.** Deleting an event cancels nothing; the engine does not
   read this.
5. **Nothing in a title or description that is not already in the tracker.** No prices, no
   signals, no notes about a person. A calendar is the easiest thing to show on a screen by
   accident.
6. **The reflection goes stale between sessions**, because the connector only exists inside one.
   Say so in the summary rather than pretending the calendar is live.
