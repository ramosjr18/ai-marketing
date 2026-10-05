# /mailbox - Add, List and Check Outreach Mailboxes

You manage the mailboxes outreach is sent from: add one, list what exists with its real state, or
check that a mailbox still logs in and delivers.

`/set-mail` sets up the **identity** of a person who signs (signature, tone, availability) and
verifies the **domain** end to end. This command is the lighter sibling: a second mailbox on a
domain already verified needs credentials and a login test, not another DNS audit.

Framework files are in English. Conversation follows the blueprint's `content_language`.

---

## Arguments

```
/mailbox add <slug>      give a mailbox a slug, an address and credentials
/mailbox list            every mailbox with its state
/mailbox check [slug]    log in and report; all of them when no slug is given
/mailbox                 same as list
```

The **slug** matches the person in `03-people.md` (`alex`, `sam`) or names a shared mailbox
(`hola`, `ventas`). Lowercase, no spaces. It becomes the variable name, so it never changes once
used: `MAILBOX_<SLUG>_USER`.

---

## How mailboxes are stored

`.env` in the repo root, gitignored. Shared servers once, one block per mailbox:

```
MAIL_SMTP_HOST=…   MAIL_SMTP_PORT=465   MAIL_SMTP_SECURITY=ssl
MAIL_IMAP_HOST=…   MAIL_IMAP_PORT=993
MAIL_TEST_TO=…

MAILBOX_SLUGS=alex,sam
MAILBOX_ALEX_USER=…          # the From: address
MAILBOX_ALEX_LOGIN=…         # only when From: is an alias of another mailbox
MAILBOX_ALEX_PASSWORD=…
```

**An alias is not a mailbox.** `alex@company.com` may be an alias whose real mailbox is
`billing@company.com`: the alias never authenticates, the mailbox does. When login fails with
`AUTHENTICATIONFAILED` while the address plainly works in webmail, this is the first thing to
suspect. Ask which mailbox it belongs to, put that in `_LOGIN`, and check that the server accepts
the alias in `From:` before trusting it — some providers rewrite it, some refuse it.

A mailbox at another provider overrides only what differs:
`MAILBOX_<SLUG>_SMTP_HOST`, `_SMTP_PORT`, `_SMTP_SECURITY`, `_IMAP_HOST`, `_IMAP_PORT`.

**Read `.env` for keys, never echo a value that ends in `_PASSWORD`.** Not in a table, not in a
summary, not in an error message.

---

## `add`

1. **Slug**: from the argument, or ask. Reject one already in `MAILBOX_SLUGS` and offer `check`
   instead. Warn when it matches nobody in `03-people.md`: fine for a shared mailbox, a typo
   otherwise.
2. **Address**: ask. Compare its domain with the ones already configured.
   - **Same domain** → the servers and the domain's verified deliverability are inherited. Say so
     and skip to step 4.
   - **Different domain** → this is a new sending domain. Run the DNS part of `/set-mail` §2 for
     it (MX, single SPF, DMARC, DKIM selectors) before going further, and say plainly that its
     reputation is separate.
3. **Servers**, only for a new domain. Do not ask for what the domain can tell you:

   - Query the provider's autoconfig first:
     `curl -s "http://autoconfig.<domain>/mail/config-v1.1.xml?emailaddress=<address>"`, and the
     `_autodiscover._tcp` SRV record. It returns hostnames, ports and TLS mode authoritatively.
   - **Use the names the certificate is issued for.** A provider's branded alias
     (`mail.provider.com`) often serves the same machine under a certificate for somewhere else
     entirely, and TLS then fails with a hostname mismatch. Read the certificate before deciding:
     `openssl s_client -connect <host>:<port> | openssl x509 -noout -subject -ext subjectAltName`.
   - Probe each port before writing anything, and report what answered.
4. **Password.** Never ask for it in the conversation: what is typed there stays in the session
   transcript. Print the line for the owner to run, with the slug already substituted:

   ```
   cd <repo> && read -rs -p "Contraseña de <address>: " P && \
     sed -i "s|^MAILBOX_<SLUG>_PASSWORD=.*|MAILBOX_<SLUG>_PASSWORD=$P|" .env && unset P && echo " guardada"
   ```

   Ask for an **application password** when the provider offers one. If it does not, say that the
   mailbox password is being stored and that this is worth knowing.
5. **Write** the block into `.env` and add the slug to `MAILBOX_SLUGS`, preserving every other key.
6. **Check it** (below). A mailbox that does not log in is added but reported as broken, never
   silently accepted.
7. **Register it in `cold-cli`** so the engine can send from it:

   ```
   cold-cli account add-smtp <address> \
     --smtp-host <host> --smtp-port <port> \
     --smtp-user <login, when the address is an alias> \
     --smtp-password-ref env:MAILBOX_<SLUG>_PASSWORD \
     --imap-host <host> --imap-port <port> --imap-tls ssl \
     --daily-limit <cap> --env-file .env
   ```

   The password is referenced, not copied: it stays in `.env` alone. Then `cold-cli account verify
   <address>` and report its output.
8. **Note it in `03-people.md`** when the slug is a person: their Outreach block gets the address
   and the daily cap. A shared mailbox gets a line under the same section saying who reads it.

---

## `list`

One table, from `.env` and `cold-cli account list`:

| Slug | Address | Servers | Password | cold-cli | Daily cap |
|---|---|---|---|---|---|
| alex | alex@… | heredados | ✓ configurada | ✓ verificada | 20 |
| hola | hola@… | heredados | **falta** | — | — |

`✓ configurada` means the variable has a value, nothing about whether it is correct. Say that.

---

## `check`

Per mailbox, in this order, reporting each result:

1. **IMAP login** with `_LOGIN` when present, else `_USER`, and folder list. Nothing else.
2. **SMTP login** (`AUTH`), then disconnect. **Never send a message.**
3. **cold-cli** knows the account and `account verify` passes.
4. The domain's deliverability as recorded in `03-people.md`, with its date. Older than 6 months,
   or the record says DKIM failed → say it needs re-checking with `/set-mail`.

A failure is reported with the server's own error. Never retry with a different port or security
setting to make it pass: that hides a wrong setting until the first real send.

---

## Safety rules

1. **A password is never printed, never asked for in the conversation, and never copied into
   `cold-cli`** — it is referenced with `env:`.
2. **`check` never sends.** Test sends are `/set-mail`'s job, and only to `MAIL_TEST_TO`.
3. **A slug is permanent.** It is the variable name; renaming it orphans the credentials.
4. **A new domain is a new domain.** It does not inherit the reputation of another one, and its DNS
   is verified before it is used.
5. **No silent fallbacks.** A port that does not answer is reported, not worked around.
6. **Propose, then write.** `.env` and `03-people.md` change after an explicit yes.
