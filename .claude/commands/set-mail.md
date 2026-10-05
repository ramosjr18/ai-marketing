# /set-mail - Outreach Sending Identity

You are setting up **who sends the outreach, from where, and whether that address can actually
deliver**. The result is the `## Outreach` block of `03-people.md` filled in, plus a `.env` with
the mailbox credentials. Nothing is sent from here and no campaign is created.

This is the command that unblocks `/outreach` and `/mail-sync`. The architecture it assumes
(SMTP from the mailbox itself, `cold-cli` as the engine, IMAP as a hard requirement) is decided in
`/set-engine` and is **not** re-opened here: this command captures identity and
verifies deliverability, nothing else.

Framework files are in English. Conversation and content follow the blueprint's `content_language`.

---

## Arguments

`/set-mail [person]` — the person whose sending identity is being set up. Default: the
decision-maker in `03-people.md`. With several people who sign, ask which one.

---

## Interaction rules

- **One question per message.** Closed questions through AskUserQuestion, recommended option first.
  Free text only for addresses, hosts, signatures and descriptions.
- **`no sé`, `luego`, `skip` are valid.** A skipped field stays `pendiente` and the summary says
  which ones block sending.
- **Never print a password.** Not in a question, not in an answer, not in the summary, not in a
  proposed file. It goes straight into `.env` and is referred to as «configurada».
- **Idempotent.** A field already filled in is shown and only changed on request.

---

## Step 0: Load & check

1. No `01-company.md` → *"Run `/setup` first."* Stop.
2. Read `03-people.md`: the person who signs, the `outreach` flag in the frontmatter, and what the
   Outreach block already has. If the flag is `false`, ask whether to enable it.
3. Read `04-voice.md`: banned words and tone, so the signature and the personal tone do not
   contradict the brand voice.
4. Read `01-company.md` for the domain(s) the company owns.
5. If a `.env` already exists in the repo root, read only the **keys** present, never the values.

---

## Step 1: The sending address

AskUserQuestion, built from what you know:

> **¿Desde qué dirección sale el outreach de [person]?**
> · `[existing address from 03-people or 01-company]` — ya existe, arranca hoy
> · `Otra del dominio` — free text
> · `Un subdominio de envío` (`algo@mail.<dominio>`) — aísla la reputación, requiere alta y DNS

Then, in one message each:

- LinkedIn profile URL of the person who signs (or `skip`).
- Whether any other mailbox will be used in rotation later (just noted, not configured now).

---

## Step 2: Verify the domain can deliver

**This step is what makes the command worth running.** Do it before asking for credentials: if the
domain cannot deliver, the rest is wasted effort.

1. Query the live DNS yourself and show the result as a table:

   ```bash
   dig +short MX <domain>
   dig +short TXT <domain>            # SPF
   dig +short TXT _dmarc.<domain>
   ```

   For a sending subdomain, query it too. Report, per record: present / absent / what it says.

2. **SPF**: exactly one TXT record starting `v=spf1` per name. Two invalidate each other
   (RFC 7208 §4.5). If there are two, stop and say so: it is the single most common breakage.

3. **DMARC**: read `p=`, `sp=`, `adkim=` and `aspf=`. Explain in one line what the current policy
   does. If `adkim=s`, warn explicitly: the DKIM signature's `d=` must match the From: domain
   exactly, so a provider that signs with its own domain will fail DMARC even with valid DKIM.

4. **DKIM**: it cannot be found by querying the domain alone — the selector is unknown. Try the
   common ones (`default`, `dkim`, `s1`, `s2`, `selector1`, `google`, `mail`) and report which
   answered. Then verify the real one end to end:

   **Open the browser yourself, do not ask the owner to navigate.** Run the platform's opener
   (`xdg-open` on Linux, `open` on macOS) on `https://www.mail-tester.com` and report that it is
   open. If it cannot be opened, say so and give the URL to open by hand.

   Then guide, one short step at a time, waiting for the owner between them:

   > 1. Te he abierto mail-tester. Copia la dirección que te muestra en grande y pégamela.
   > 2. Escríbele **desde [address]** con asunto y cuerpo normales, dos o tres frases reales.
   >    Un mensaje vacío puntúa peor y falsea el resultado.
   > 3. Vuelve a la pestaña, pulsa «Then check your score» y pásame la URL del resultado.

   Holding the address the owner pastes lets you check it looks like a mail-tester address before
   they send anything to it. The result URL has the shape `https://www.mail-tester.com/test-XXXXX`;
   if the owner pastes only the code, build the URL yourself.

   Fetch that URL and report: SPF pass/fail, DKIM pass/fail **and its `d=`**, DMARC pass/fail,
   whether the From: aligns, and any blacklist hit. Then state plainly whether this mailbox can
   send or not.

5. If DKIM does not align under `adkim=s`, present the two ways out and let the owner choose:
   ask the provider to sign with the domain, or relax the DMARC record to `adkim=r`. **Do not edit
   any DNS record**: this repo does not touch DNS, it reports what to change.

Record the outcome verbatim (date, what passed, what failed). That line is what `/outreach` reads
before generating anything.

---

## Step 3: SMTP and IMAP

Explain in one line why IMAP is needed: without it nothing can be known about replies, and
`/mail-sync` and the auto-stop of the sequence both depend on it.

Ask, in one message each:
- SMTP host and port (typical: 587 with STARTTLS, or 465 with SSL).
- IMAP host and port (typical: 993).
- Whether the provider offers **application passwords**. If it does, ask for one to be created for
  this use. If it does not, say plainly that the mailbox password will be used and that this is a
  risk worth noting.

Then write `.env` in the repo root (already covered by `.gitignore`), creating it if absent and
**preserving any keys already there**:

```
MAIL_SMTP_HOST=…   MAIL_SMTP_PORT=…   MAIL_SMTP_SECURITY=ssl|starttls
MAIL_IMAP_HOST=…   MAIL_IMAP_PORT=…
MAIL_TEST_TO=<test address>

MAILBOX_SLUGS=<slug>
MAILBOX_<SLUG>_USER=<address>
MAILBOX_<SLUG>_PASSWORD=
```

Servers are shared by every mailbox; each mailbox only declares its own address and password, so
a second one is a two-line block. Adding, listing and checking them afterwards is `/mailbox`.

**Never ask for the password in the conversation**: what is typed there stays in the session
transcript. Print the line for the owner to run instead, slug already substituted:

```
cd <repo> && read -rs -p "Contraseña de <address>: " P && \
  sed -i "s|^MAILBOX_<SLUG>_PASSWORD=.*|MAILBOX_<SLUG>_PASSWORD=$P|" .env && unset P && echo " guardada"
```

Never echo it. Never put it in `03-people.md`.

Verify the credentials work before moving on: a single IMAP login and folder list, nothing else.
Use the repo's virtualenv (`.venv/bin/python`); if it is missing, point at `tools/README.md`
rather than failing silently.

---

## Step 4: Voice of the person

One question per message, each with a draft to correct rather than a blank page. Drafts come from
`04-voice.md` and from any real email in `documents/content/`, labeled
`[inferred from <source>]`:

1. **Signature.** Three files per person under `signatures/` (gitignored, generated from
   `templates/signature.html` which ships):

   | File | Used for |
   |---|---|
   | `<slug>.html` | outreach: no confidentiality notice |
   | `<slug>-full.html` | day-to-day mail: same plus the notice |
   | `<slug>.txt` | plain-text part of every message |

   If the person already has a signature they like, **take theirs** and fill the template from it
   instead of proposing a new one. Then check the two things that break real signatures:

   - **Every image URL must be public.** Fetch it and look at what comes back, do not trust a
     `200`: a webmail's internal image endpoint answers `200` with a JSON session error, and the
     recipient sees a broken box while the sender sees the logo fine. If it is not public, find a
     public one on the company domain (try `/<name>.png`, the site's header, the press kit) and
     say what you changed.
   - **The confidentiality notice comes out for outreach.** Claiming confidentiality on a message
     nobody asked for reads badly and adds weight. It stays in the `-full` version.

   **Strip every HTML comment from the populated files**, with a real parser or a multiline
   regex, never by dropping lines that open or close one: a comment spanning several lines
   leaves its middle behind, and that middle is inlined into the body and reaches the
   recipient as visible text above the signature. What the comment was explaining goes into
   `signatures/README.md` instead.

   Show the result rendered as text and say which URL each image now points to.
2. **Regional variant of Spanish**: which Spanish this person writes. **Ask, never infer it**
   from their name or from the prospect's country. What they sign goes out in their own variant
   even when the reader is from somewhere else, and the second-person plural is the tell:
   `ustedes` or `vosotros`. Write it into their block and say plainly how it will read to the
   other market. This is the exception to the brand register recorded in `04-voice.md`.
3. **Personal tone**: how this person writes, beyond the brand voice. Ask for a **real message
   they wrote**, not a description: people describe themselves worse than they write. Distil it
   into rules and save them to `tone/<slug>.md`, from `templates/tone.md`, recording the sample
   verbatim as the first observation. `03-people.md` only points at that file.
   Say plainly what the sample does **not** cover: a reply to a warm contact tells you little
   about a cold open. From there it is `/adjust-tone` that improves it, one real correction at a
   time.
4. **What they would never write**: phrases, claims, greetings they refuse. Adds to the banned list
   in `04-voice.md`, never replaces it.
5. **Availability for calls**: time slots, booking link if any, and what the brand promises about
   response time. A booking link is optional: proposing a short call and letting them reply is a
   valid CTA, and on a first cold email it asks less of someone who does not know you yet.

---

## Step 5: Limits

AskUserQuestion for each, with these defaults:

- **Daily cap** for this mailbox: `20 las dos primeras semanas, luego 40` (recommended) · other.
- **Sending window**: working hours in the recipient's timezone (recommended) · any time.
- **Test address**: where test sends go. Never a prospect.

---

## Step 6: Propose, then write

Show the complete `## Outreach` block, filled, in `content_language`, with the password shown only
as «configurada en `.env`». AskUserQuestion → `Write it` · `Change something` (free text) ·
`Leave it as a draft`.

On yes, write into `03-people.md`:

```markdown
## Outreach
Who sends messages to prospects and how they sound.

### [Person]
- **Sends from:** [address] · SMTP [host:port] · IMAP [host:port] · credenciales en `.env`
- **LinkedIn:** [url]
- **Deliverability (verified [date]):** SPF [pass/fail] · DKIM [pass/fail, d=…] · DMARC
  [pass/fail, policy] · [mail-tester URL]
- **Daily cap:** [n] · **Window:** [hours]
- **Test address:** [address]
- **Signature:** `signatures/<slug>.html` (outreach) · `signatures/<slug>-full.html` (día a día) ·
  `signatures/<slug>.txt` (texto plano). [what was corrected, if anything]
- **Personal tone:** [text]
- **Would never write:** [text]. Banned words and vetoed claims from `04-voice.md` still apply
- **Availability for calls:** [text]
```

Set `outreach: true` in the frontmatter and update `last_setup`. Do not touch any other block. No
`[PLACEHOLDER]` may remain (Grep `\[[A-Z_]{3,}\]`).

---

## Step 7: Summary

> **Identidad de envío lista.** [address] · entregabilidad: [one line].
> `.env` escrito · `03-people.md` actualizado.
> **Bloquea el envío:** [pending fields, or none].
> **Siguiente:** `/outreach <unit>` ya tiene con qué firmar. `/mail-sync` ya tiene buzón que leer.

---

## Safety rules

1. **The password never leaves `.env`.** Not printed, not summarised, not written to the blueprint,
   not passed as a command-line argument where it would land in shell history.
2. **Deliverability is verified, not assumed.** The DNS is queried live and the DKIM is confirmed
   with a real message. «Debería funcionar» is not an answer this command accepts.
3. **This command does not touch DNS.** It reports which record to change and who changes it.
4. **Propose, then write.** The Outreach block is shown in full and approved before writing.
5. **Nothing is sent to a prospect.** The only address this command writes to is the test one.
6. **A failed check is recorded, not hidden.** If DKIM does not align, the block says so, and
   `/outreach` refuses to generate until it is fixed or explicitly waived.
