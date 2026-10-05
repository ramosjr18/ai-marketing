# /campaign - One Product, Several Campaigns, Each With a Purpose

You define why a set of messages is going out. A campaign belongs to one sellable unit and has
one objective; a unit has as many campaigns as it has reasons to write.

Framework files are in English; the campaign's content is
in the company's `content_language`.

---

## Arguments

```
/campaign                       list every campaign and its state
/campaign <unit>                create one for that unit
/campaign "<prompt>"            create from a description; work out the unit, ask for the rest
/campaign close <slug>          close it and free the prospects that did not convert
/campaign pause <slug>          stop it without freeing anyone
```

---

## `list`

From `offering/*/campaigns/*/campaign.md` and the tracker:

| Campaign | Unit | Objective | State | Prospects | Written to | Replied |
|---|---|---|---|---|---|---|

Say which units have **no** campaign, and which have more than one `active`. Two active
campaigns on one unit is legal and worth seeing: it is where double-contact comes from.

---

## Creating one

### Step 0: The unit

From the argument, or from the prompt, or ask. It must exist in `02-offering.md`.

Read its `unit.md` and `icp.md`. **A unit that is not for sale gets one question first**: a
campaign for something that cannot be bought is validation, and the owner decides whether that
is what they want.

### Step 1: The objective

**One question, and it is the point of the command.** Not "what do you sell" — the unit already
says that — but what this campaign is trying to make happen.

Offer real options drawn from the unit, as a selector, plus free text:

- for a product with a trial: *que prueben el trial*, *que pidan una demo*
- for a service: *que reserven un diagnóstico*, *que respondan con su caso*
- always: *reactivar a los que no contestaron*, and free text

The objective is not a slogan. It has to be something you can tell whether it happened, because
`/analyze` will ask later. «Que prueben el trial de 30 días» works. «Dar a conocer el producto» does
not, and if that is the answer, say why and ask again.

### Step 2: Who it goes to

The slice of the unit's ICP this campaign is for. Defaults from `icp.md`, and the owner corrects:

- **Market**, when the unit has more than one
- **The slice**: size, sector, the buying signal that qualifies. «Consultoras de selección de
  1-15 reclutadores con 5+ vacantes abiertas» is a slice; «pymes» is not
- **Who is excluded**, if anything: existing clients, a competitor, a segment kept for later

### Step 3: The angle

One or two lines: what this campaign says that the unit's other campaigns do not. It goes into
`/outreach`'s SELLER block and it is what makes two campaigns of the same product read
differently.

If the unit already has campaigns, show their angles. Two campaigns with the same angle are one
campaign with two names, and saying so is more useful than writing the file.

### Step 4: How it goes out

Defaults from `03-people.md`; ask only to confirm:

- **Channel**: email · linkedin · both
- **Cadence**: `email-2` (day 0 and 4) · `linkedin-3`
- **Mailbox**: which sender. When the unit has its own domain, that is the default and say why:
  the sender matching the product is worth more than the corporate domain's history
- **Signer**: from `03-people.md`. Their tone file and their regional variant come with them

### Step 5: The slug

Readable and stable: `<unit>-<who>-<what for>`, e.g. `acme-consultoras-es-trial`. **Never a
date**: a campaign is not the day it was created, and the same name has to work in `cold-cli`,
in the folder and in the tracker.

Reject a slug that already exists under that unit.

### Step 6: Assign the prospects

Show how many rows of `prospects.csv` match the slice and are **free** (`campaign` empty), and
how many match but are **already in another campaign** — listed by name, never moved silently.

Assign only with an explicit yes, writing the slug into their `campaign` column.

> **A prospect is in one active campaign at most.** Moving one means taking it out of the other,
> and the owner has to see that happen. Two campaigns writing to the same person in the same
> week turns attention into a mailing list.

A prospect that was already written to under a closed campaign can come back, and `/outreach`
will require a new angle. Say how many of those there are.

### Step 7: Propose, then write

Show `campaign.md` in full and write it on a yes, along with the `campaign` column changes.

It is born **`draft`**: defined, with its prospects, and not in flight. It becomes `active` when
`/outreach` actually schedules its messages, and nothing else moves it there — a campaign that
calls itself active before anything is scheduled makes the tracker lie about what is running.

Then say the next step: `/outreach <unit> --dry`.

---

## `close`

1. Show what it did: prospects, written to, replies, meetings.
2. **Free** every prospect that did not convert: clear their `campaign` column so they return to
   the pool. Say how many.
3. Anyone in `suppression.csv` stays suppressed. That is per person and closing changes nothing.
4. `status: closed` and the date in `campaign.md`. The folder stays: it is the record of what
   was written and how.

`pause` is the same minus the freeing: nothing goes out, nobody moves.

---

## Safety rules

1. **No objective, no campaign.** It is the reason the command exists; do not fill it with the
   unit's description.
2. **Never assign a prospect silently**, and never move one between campaigns without showing it.
3. **Suppression, sent history and the daily cap are per person or per mailbox**, never per
   campaign. A campaign never gets its own allowance.
4. **Closing frees prospects; it does not erase history.** `events.csv` keeps everything.
5. **Propose, then write**, like everything that touches the blueprint.
