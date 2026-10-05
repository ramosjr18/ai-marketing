# /import - Receive What Another Repo Knew, Without Overwriting What This One Knows

You take a folder written by `/export` and land it in this repo. The other half of the pair:
`/export` copies out, this one copies in, and neither of them merges.

Framework files are in English; anything you write for the owner goes in the company's
`content_language`.

---

## Why this exists

A fresh clone has the framework and **no company knowledge**. Without this, the receiver reads
the export by hand and retypes it, or runs `/setup` and builds a second, different truth.

And the opposite case, which is the dangerous one: a repo that **already** has a blueprint. Then
an import is not a load, it is a collision. Every file in the package has a counterpart here,
each one may be newer or older, and copying the folder over the top silently destroys work. This
command exists mostly to refuse to do that.

---

## Arguments

```
/import <path>           the export folder
/import                  ask for the path
/import <path> --dry     say what would happen, write nothing
```

---

## Step 1: Read the package before trusting it

Do not copy anything yet.

1. **It must look like an export**: a `README.md`, a `blueprint/` folder and a `MANIFIESTO.txt`.
   Anything else is not one. Say so and stop.
2. **Check `MANIFIESTO.txt`**: recompute the sha256 of every file and compare. Report mismatches
   by name. A file that does not match its hash **does not get imported**, not even when the
   owner insists: the package is broken and the fix is to ask for it again, not to land half of
   it.
3. **Read the package `README.md`** and say its date out loud. Prices, ICPs and prospect lists go
   stale; a nine-month-old export is a historical document, not a blueprint.
4. **Check it is the same company.** Compare `01-company.md` in the package with
   `00-overview.md` here, if there is one. Different company name, different website, different
   market → **stop**. One company per repo. Say which two names you are looking at and let the
   owner decide; never guess that it is a rename.

---

## Step 2: Say what is going to happen, file by file

Build one table before writing anything. This is the whole command; the copying is the easy
part.

| State | Meaning | Default |
|---|---|---|
| **Nuevo** | the path does not exist here | import |
| **Idéntico** | same sha256 | skip, do not touch the mtime |
| **Distinto** | exists here and differs | **ask**, showing the diff |
| **Solo aquí** | this repo has it, the package does not | leave it. An export is a snapshot, not a deletion order |

For every **Distinto**, show a real diff (`diff -u`), not a byte count. Say which side is newer
by the dates inside the files, not by filesystem mtime, which a copy destroys. Then AskUserQuestion
per file, or per group when the owner wants to go faster:

> `Traer la del paquete` · `Conservar la mía` · `Ver el diff entero` · `Dejarla aparte`

«Dejarla aparte» writes the incoming version next to the current one as
`<name>.import-<YYYY-MM-DD>.md` and changes nothing. That is the honest answer when neither
version is clearly right, and it is the right default to offer on a file the owner has been
editing.

With `--dry`, print the table and stop here.

---

## Step 3: The three files that are not files

Ordinary blueprint files are copies. These three are not, and getting them wrong is the reason
this command is careful.

### `suppression.csv` — union, never replacement

**It is merged, and the merge only ever grows.** One row per address, keyed by `email`. On a
collision keep the **oldest** `suppressed_at`: the moment someone asked not to be written to is
the moment it happened, not the moment their row reached this machine.

Never replace this file. Never drop a row because the incoming package lacks it. An import that
shrinks the suppression list has just given this repo permission to write to someone who said
no, and nothing in the output would show it. Report the count: *«bajas: 34 aquí + 12 del paquete
→ 41 (5 ya estaban)»*.

### `prospects.csv` — joined only when one side is empty

Two prospect trackers edited in parallel **cannot be joined** and this command will not pretend
otherwise. Each row carries status, touch dates and per-prospect history that belong to the
machine that sent the emails.

- **No `prospects.csv` here** → import it whole.
- **There is one, and the keys do not overlap** → append the new rows, report how many.
- **The keys overlap** → **stop on the overlapping rows.** List them (key, status here, status
  there) and ask what to do, one by one or in bulk. Never pick the "more advanced" status
  automatically: `lost` after `replied` is information, not a regression.

Same rule for `events.csv`, which is append-only: append what is not already there, keyed by
whatever makes the row unique, and never rewrite an existing line.

### `.env` — never written by this command

If the package came with a `credenciales-*.7z`, **do not open it as part of the import**. Tell
the owner it is there, give them the line to extract it themselves, and say the password comes
by a different route than the file:

```bash
7z x credenciales-<empresa>-<fecha>.7z
```

Then they merge the keys into their own `.env` by hand, or run `/set-engine`, `/set-mail` and
`/mailbox`, which is usually faster and always safer. **A mailbox password that arrives by
import and is never typed by its owner is a credential nobody is responsible for.**

Never write, append to, or overwrite `.env` from a package. Never print its contents.

---

## Step 4: Land it

Copy approved files to their paths, **keeping the layout**: `blueprint/` maps onto
`.claude/skills/company-blueprint/`, `clients/` onto `clients/`. Create directories as needed.
**Copy, never reformat.** A file that gets rewritten on the way in is a second version of the
truth, which is what the pair exists to prevent.

Things that are not imported even when present in the folder, because they are the state of
another machine and not knowledge:

- `~/.cold-cli/data.db` or any engine database. `/set-engine` rebuilds it
- `.peek/`
- `offering/_shared/linkedin-usage.json` — another machine's daily counters. Importing it would
  tell this machine it had already sent today, or that it had not
- Anything that was not in `MANIFIESTO.txt`

---

## Step 5: Report, and say what is missing

Show what landed, what was kept, what was left aside and under which name. Then the part that
matters, in the company's language:

1. **The date of the package**, again. It is the shelf life of everything just imported
2. **What this machine still has to supply**: its own `.env`, mailbox, DKIM, signature,
   `tone/<slug>.md`, regional variant. Name the files that are still absent after the import
3. **What to run next**, in order. Usually `/set-engine` → `/set-mail` → `/mailbox`, then
   `/mail-sync` before anything is sent
4. **That this was a snapshot, not a sync.** From now on both repos diverge, and the next import
   will collide with whatever gets edited here today

Finish by reading `00-overview.md` and confirming in one line which company this repo now holds.

---

## Safety rules

1. **Nothing is overwritten without the owner seeing the diff.** No silent copies, no "newer
   wins", no bulk approval that was not asked for in those words.
2. **A hash that does not match does not get imported.** Not even on insistence.
3. **`suppression.csv` only grows.** If the merge would ever produce fewer rows than this repo
   already has, that is a bug: stop and say so.
4. **Overlapping prospects stop the import of those rows**, and only those. The rest of the
   package still lands.
5. **`.env` is never written here**, and credentials are never printed, stored or echoed.
6. **A different company stops everything.** One company per repo.
7. **Copy, never reformat**, and never delete what this repo has and the package lacks.
