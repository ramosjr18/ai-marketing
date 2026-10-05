# /export - Move the Knowledge Without Moving the Keys

You package what this repo knows about the company so it can be carried somewhere else: another
machine, or another person who is about to start from an empty clone.

Framework files are in English; the `README.md` you write goes
in the company's `content_language`.

---

## Why this exists

**The blueprint is gitignored.** Whoever clones the repo tomorrow gets the framework and **none
of the company knowledge**. They would run `/setup` and build a different blueprint: another
voice, other prices, another ICP. Two people working the same company from two truths.

---

## Arguments

```
/export                  ask both questions
/export <unit>           only what belongs to one sellable unit, plus the company files it needs
```

---

## Step 1: Two questions, neither with a default

### 1a · Who is it for

AskUserQuestion, and **this one is a security boundary, not a preference**:

| Answer | What changes |
|---|---|
| **For me** — another machine, a backup | Same rules. A backup that leaks is a leak |
| **For someone else** — a teammate starting from zero | Third-party data and internal figures are asked for separately and default to no |

Neither answer lets a credential travel in the clear. **No answer, no export.** Do not guess it
from context.

### 1b · How much

AskUserQuestion, multi-select, with what each layer drags:

| Layer | What it carries |
|---|---|
| **Identidad** | `00`-`04`: who they are, what they sell, who signs, how they speak |
| **Comercial** | `05`-`08` and `offering/<unit>/{unit,icp,competitors,pricing,product,hallazgos}.md` |
| **Interno** | `06-costs.md`, and the floors and margins inside `05-pricing.md`. **Ask separately** |
| **Outreach** | `prospects.csv`, `events.csv`, `prospects-runs.md`, campaigns, rendered emails. **Ask separately, and say out loud that these are real named people with real addresses** |
| **Casos de cliente** | `clients/<slug>/`: transcripts, summaries, diagnoses, proposals. **Ask separately, and say out loud that these are recordings of real conversations with named people.** Default no |
| **Todo** | every layer above, still minus the keys. **Client cases are never swept in by "todo"** — they are only ever included when asked for by name |

`suppression.csv` is not on the list because it is not optional. See Step 3.

---

## Step 2: Credentials travel encrypted, and separately

`.env` **may** go, by the owner's decision, under three conditions that are not negotiable:

1. **Real encryption.** `zip -e` is ZipCrypto, broken since the nineties by a known-plaintext
   attack, and a `.env` is the ideal target because its shape is predictable. Use AES-256:

   ```bash
   7z a -p -mhe=on credenciales-<empresa>-<fecha>.7z .env
   ```

   `-mhe=on` encrypts the file names too. **Never pass the password on the command line**: `-p`
   with no value prompts for it, so it stays out of the shell history. The owner types it; you
   never see it, never store it, never write it into the README.
2. **A separate file from the knowledge folder.** The blueprint stays readable without
   decrypting anything, and the only thing behind a password is a 2 KB file whose purpose is
   obvious. One password protecting a voice guide and a mailbox password protects neither well.
3. **The password goes by a different channel than the file.** Say it out loud: sending both
   over WhatsApp encrypts nothing. Put that sentence in the README.

Still never, at any scope, for anyone:

- **`~/.cold-cli/data.db`** — every lead ever loaded, with addresses, plus send history.
  `/set-engine` and `/mailbox` rebuild it from `.env` in minutes
- **`.peek/`** — screenshots of a live application with other people's data in them
- **`offering/_shared/linkedin-usage.json`** — the day's send counters. State of *this* machine,
  not knowledge. Carrying it would tell the receiver's tool that it had already sent today
- Anything under `documents/` the owner did not name
- Anything under `clients/` the owner did not name, case by case. A recording of somebody's
  conversation does not travel because a scope was ticked

**Formats travel unchanged**: Markdown, CSV, HTML, TXT, YAML, exactly as
they sit in the repo. No conversion to JSON or anything else. The receiver drops each file into
the same path and it works; the files read without tooling; and `diff` against their copy says
something legible. Converting would create a second version of the truth, which is what the
export exists to prevent.

---

## Step 3: The suppression list always travels

**No conditions.** `offering/_shared/suppression.csv` goes into every export, even when the
chosen scope has nothing to do with outreach, even when third-party data was declined.

A suppression list is not commercial information: it is the list of people who must not be
written to. Handing over the repo without it hands over the ability to write to them again.
When it is empty, it still goes, with its header, so the file exists before anyone writes a
line.

---

## Step 4: Write it

**An uncompressed folder**, dated, **outside the repo** (default: `~/`,
ask if unsure). Uncompressed because it reads without opening anything, diffs against the other
person's repo, and Claude Code can read it in place:

```
export-<empresa>-<YYYY-MM-DD>/
  README.md
  blueprint/          the files, keeping their paths
  MANIFIESTO.txt      one line per file: path, bytes, sha256
credenciales-<empresa>-<YYYY-MM-DD>.7z     next to it, only if credentials were included
```

Copy files, never rewrite them. The only file you author is `README.md`.

**`README.md` is half the work.** An export without instructions is a folder somebody opens, does
not understand, and rebuilds by hand. It says, in the company's language:

1. **What this is and what date it is from**, in the first line. Prices, ICPs and prospect lists
   go stale
2. **Which layers are inside**, and **which were left out and why** — not just a list of files
3. **What the receiver has to supply themselves**: their `.env`, their mailbox, their DKIM,
   their signature, their tone file, their regional variant of Spanish. Name the files
4. **Where each file goes**, with the exact paths
5. **What to run next**, in order
6. **How to open the credentials file**, when there is one, and that **the password comes by
   another route**. Never the password itself
7. **That this is a snapshot, not a sync.** Once both sides edit, they diverge; there is no
   merge, and two `prospects.csv` edited in parallel cannot be joined. Say it plainly instead of
   letting the word "sincronizado" promise it

---

## Step 5: Report

Show the folder path, the layer list, what was excluded and why, the file count and total size,
and the one line that matters most: **what the receiver must do first.**

---

## Safety rules

1. **Credentials never travel in the clear.** `.env` goes only inside a separate AES-256
   archive whose password the owner types and you never see, store or write down. The engine
   database and `.peek/` do not travel at all, at any scope, for anyone.
2. **The audience question has no default.** If it was not answered, nothing is written.
3. **Third-party data is named out loud.** Before including prospects, say how many real people
   and companies that is. A commission collaborator is not automatically entitled to them.
4. **`suppression.csv` always travels.**
5. **Costs, floors and margins are internal.** They leave only on an explicit yes, for that
   export, said once and not inferred from a previous run.
6. **Copy, never edit.** An export that reformats the blueprint is a second version of the
   truth.
7. **The `README.md` says what is missing**, not only what is there. The gaps are what the
   receiver has to act on.
