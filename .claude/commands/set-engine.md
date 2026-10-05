# /set-engine - Set Up the Outreach Engine on This Machine

You are preparing the machine that will send outreach: check what is already there, say plainly
what is missing and what installing it means, install it if the owner agrees, pick where the
sequence state lives, and write the configuration.

This runs **before** `/set-mail`. `/set-mail` captures who sends and from which mailbox; this one
sets up the engine underneath. Run it once per machine, not once per campaign.

The architecture it installs is decided once and is not re-opened
here.

---

## The rule that governs this command

**This repo is a prompt framework, not an installed product.** Somebody can clone it on a laptop
that has no Go, no Docker and no Postgres. So:

- **Nothing is installed without saying what it is, who wrote it, under which licence, and how
  much it weighs.** The owner approves or gets the commands to run themselves.
- **Missing infrastructure degrades, it does not block.** No shared Postgres means SQLite, said out
  loud, not an error.
- **Machine configuration never lands in git.** It goes to `.env`; `.env.example` is what ships.

---

## Step 0: Look at the machine

Run these and build one table. Do not install anything yet.

```bash
command -v go && go version
command -v mise && mise ls | grep -i '^go'
command -v cold-cli && cold-cli --version
command -v docker && docker ps --format '{{.Names}}\t{{.Ports}}' | grep 5432
command -v python3 && python3 -c "import imap_tools" 2>&1 | tail -1
```

| Pieza | Para qué | Estado |
|---|---|---|
| Go ≥ 1.25.3 | compilar `cold-cli` | ✓ / falta |
| `cold-cli` | motor de secuencias | ✓ / falta |
| `imap-tools` (Python) | leer el buzón en `/mail-sync` | ✓ / falta |
| Un Postgres ya en la máquina | estado del motor, opcional | ✓ / no hay |
| `mise` | gestor del toolchain | ✓ / no hay |

---

## Step 1: Say what would be installed

For every missing piece, one block, before asking anything:

> **`cold-cli`** — motor de secuencias de correo en frío.
> Autor: `andersmyrmel` · Licencia MIT · ~1,4 MB de código fuente · Go
> Repo: https://github.com/andersmyrmel/cold-cli
> Se compila desde el código, no hay binarios publicados. Guarda su estado en una base tuya y
> envía por el SMTP de tu buzón: no manda tus datos a ningún servicio.
> Comando: `go install github.com/andersmyrmel/cold-cli/cmd/cold-cli@<commit>`

> **Go 1.25.3+** — necesario solo para compilar lo anterior.
> Se instalaría con `mise use -g go@1.27.1`, que es como esta máquina gestiona su toolchain.
> Si no hay `mise`, se dice y se ofrece el paquete del sistema.

> **`imap-tools`** — biblioteca de Python para leer el buzón por IMAP.
> Licencia Apache-2.0 · `pip install --user imap-tools`

**Pinned commit.** `cold-cli` has no tags or releases, so `@latest` tracks its main branch and the
author's next commit would silently change your binary. Install a reviewed commit instead. Current
reference, reviewed 2026-09-21:

```
68a6defb29cc   2026-08-30   feat: support sender template fields
```

**It will probably need patching, and that is the owner's fork, not this repo's.** Upstream sends
HTML only, escapes the signature, and joins paragraphs with `<br>`. For cold outreach that costs
deliverability and renders badly. If the owner wants the behaviour this framework assumes, say so
plainly and leave the work to them:

> `cold-cli` upstream envía solo HTML y escapa la firma. Para outreach hace falta adaptarlo:
> clónalo (`git clone https://github.com/andersmyrmel/cold-cli`), aplica lo que necesites y
> compílalo tú. Tres cambios bastan: enviar `multipart/alternative` en vez de HTML a secas,
> añadir `html_signature` y `text_signature` a los valores por defecto de la secuencia y
> adjuntar cada uno a su parte, y maquetar párrafos con ancho máximo en vez de `<br>`.
> Este repo no distribuye ese fork ni lo mantiene: apunta `COLD_CLI_BIN` al binario que compiles.

Without the patch everything still runs; the emails just go out HTML-only and the plain-text part
carries no signature and no opt-out line. Say that, and let the owner decide.

Then AskUserQuestion:

> **Instalar lo que falta?**
> · `Sí, instálalo` · `Dame los comandos y lo hago yo` · `Cancelar`

On «dame los comandos», print them in one block and stop at Step 3 (configuration can still be
written).

---

## Step 2: Install

Only what is missing, one at a time, reporting each result. If any step fails, stop and show the
real error: do not continue as if it had worked, and do not fall back to another method silently.

After installing `cold-cli`, verify it answers: `cold-cli --help`. If `go install` put it somewhere
outside `PATH` (usually `~/go/bin`), say so and give the line to add, do not edit shell config
files yourself.

---

## Step 3: Where the state lives

Detect, do not ask first:

- **A Postgres is already running** (`docker ps` shows one answering on 5432) → propose using it
  with a database of its own for this repo, named after the repo. Never share a database with
  another project. Show the command before running it, and ask:
  `docker exec <container> psql -U postgres -c "CREATE DATABASE ai_marketing;"`
  Read the password from wherever that instance keeps it, never print it.
  **Direct connection, never a pooler**: `cold-cli tick` uses advisory locks and needs stable
  session semantics.
- **No Postgres, no Docker** → SQLite, and say it:
  > No hay Postgres en esta máquina. Uso SQLite en `~/.cold-cli/data.db`, que es lo que cold-cli
  > trae por defecto. Es un fichero: se copia y se respalda como tal. Si algún día levantas un
  > Postgres, migrar es manual.

Either way, run `cold-cli init` and report what it created.

---

## Step 4: Deliverability check of the engine

`cold-cli doctor` against the company domain from `01-company.md`. Report its output as-is. This is
a check of the domain, not of a mailbox: the mailbox is verified in `/set-mail` with a real
message. Say that difference so nobody thinks the domain passing means the mailbox sends.

---

## Step 5: Write the configuration

Append to `.env` (create if absent, never overwrite keys already there):

```
# --- outreach engine (written by /set-engine) ---
COLD_CLI_BIN=<ruta al binario>   # ~/go/bin/cold-cli, o el que hayas compilado
COLD_CLI_COMMIT=68a6defb29cc
COLD_CLI_STORAGE=postgres|sqlite
COLD_CLI_DATABASE_URL=postgresql://postgres:<pass>@127.0.0.1:5432/ai_marketing   # only if postgres
```

And keep `.env.example` in git with the same keys and no values, so the next person knows what to
fill. If `.env.example` does not exist, create it.

Never print the Postgres password, not even when reading it from the shared `.env`.

---

## Step 6: Summary

> **Motor listo en esta máquina.** cold-cli [versión/commit] · estado en [Postgres `ai_marketing` /
> SQLite `~/.cold-cli/data.db`] · `doctor`: [one line].
> Instalado en esta sesión: [list, or nothing].
> **Siguiente:** `/set-mail` para dar de alta el buzón y verificar que entrega.

---

## Safety rules

1. **Nothing is installed without an explicit yes**, and never without naming the project, its
   author and its licence first.
2. **No silent fallbacks.** A failed install is reported with its error, not worked around.
3. **Missing infrastructure is not an error.** SQLite is a valid answer and is written down as the
   choice it is.
4. **Passwords are never printed**, neither the mailbox's nor the shared infrastructure's.
5. **Shell configuration and DNS are not edited by this command.** It says what to change.
6. **Nothing is sent here.** No campaign, no test message: this command only prepares the machine.
