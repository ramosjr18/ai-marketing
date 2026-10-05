#!/usr/bin/env python3
"""Read new messages from the outreach mailboxes and print them as JSON.

Code lives here because an agent cannot speak IMAP. Everything downstream —
matching a reply to a prospect, classifying it, deciding what to write — is
`/mail-sync`'s job, in markdown, with a human approving.

    tools/imap_fetch.py                      every mailbox, since the last run
    tools/imap_fetch.py --mailbox alex       one mailbox
    tools/imap_fetch.py --since 2026-09-01   ignore the saved state
    tools/imap_fetch.py --days 7             last 7 days
    tools/imap_fetch.py --commit             save the new high-water mark
    tools/imap_fetch.py --folder sent --to someone@example.com --days 7
                                             look in Sent instead, to confirm what actually left

Two rules it will not break:

- **Nothing is marked as read.** Messages are fetched with PEEK, so the mailbox
  looks untouched to the person who owns it.
- **The high-water mark only moves with `--commit`.** A run that crashes while
  the agent is halfway through classifying must not lose messages, so reading
  and acknowledging are separate steps.

`--folder` reads somewhere other than the inbox, and **never touches the state**:
the watermark belongs to the inbox, and a search through Sent must not move it.
That is what `/client email confirm` uses to store the version that really went
out, instead of asking somebody to remember whether they edited it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE = REPO / ".claude/skills/company-blueprint/offering/_shared/mail-sync-state.json"
BODY_CHARS = 4000

# A reply that no human typed. Worth knowing before anyone reads it as interest.
# RFC 3834: "auto-replied" is an answer to your message; "auto-generated" is a
# newsletter or a notification, which is a different thing entirely. And
# X-Auto-Response-Suppress means the opposite of an auto-reply: it asks not to
# receive one. Conflating the three marks every newsletter as a reply.
AUTO_HEADERS = ("x-autoreply", "x-autorespond")
AUTO_SUBJECT = re.compile(
    r"\b(out of (the )?office|automatic reply|respuesta autom|fuera de la oficina|"
    r"ausencia|vacation|abwesenheit|réponse automatique)\b", re.I)
# no-reply@ is not a bounce, it is just a mailbox that does not read answers.
BOUNCE_FROM = re.compile(r"^(mailer-daemon|postmaster)@", re.I)
BOUNCE_SUBJECT = re.compile(
    r"(undeliverable|delivery (status notification|has failed|failure)|returned mail|"
    r"mail delivery failed|no se pudo entregar|devuelto)", re.I)
# Address a DSN says it failed for.
DSN_FINAL = re.compile(r"^Final-Recipient:\s*rfc822;\s*(\S+)", re.I | re.M)
DSN_STATUS = re.compile(r"^Status:\s*([245]\.\d+\.\d+)", re.I | re.M)


def load_env(path: Path = REPO / ".env") -> dict[str, str]:
    if not path.exists():
        sys.exit(f"no hay {path}. Corre /set-engine y /set-mail primero.")
    env = {}
    for line in path.read_text().splitlines():
        line = line.rstrip("\n")
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        env[k.strip()] = v
    return env


def mailboxes(env: dict[str, str], only: str | None) -> list[dict]:
    slugs = [s.strip() for s in env.get("MAILBOX_SLUGS", "").split(",") if s.strip()]
    if only:
        if only not in slugs:
            sys.exit(f"buzón '{only}' no está en MAILBOX_SLUGS ({', '.join(slugs) or 'vacío'})")
        slugs = [only]
    out = []
    for slug in slugs:
        u = slug.upper()
        addr = env.get(f"MAILBOX_{u}_USER", "").strip()
        pwd = env.get(f"MAILBOX_{u}_PASSWORD", "")
        if not addr or not pwd:
            out.append({"slug": slug, "address": addr, "skipped": "sin credenciales"})
            continue
        out.append({
            "slug": slug,
            "address": addr,
            # An alias never authenticates; the mailbox behind it does.
            "login": env.get(f"MAILBOX_{u}_LOGIN", addr).strip(),
            "password": pwd,
            "host": env.get(f"MAILBOX_{u}_IMAP_HOST", env.get("MAIL_IMAP_HOST", "")).strip(),
            "port": int(env.get(f"MAILBOX_{u}_IMAP_PORT", env.get("MAIL_IMAP_PORT", "993"))),
        })
    return out


def read_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def addr_of(value) -> tuple[str, str]:
    """(name, address) from whatever imap_tools hands back."""
    if not value:
        return "", ""
    pairs = getaddresses([value if isinstance(value, str) else str(value)])
    for name, addr in pairs:
        if addr:
            return name, addr.lower()
    return "", ""


def classify_shape(msg, headers: dict) -> dict:
    """What KIND of message this is. Never what it means: that is the agent's call."""
    _, frm = addr_of(msg.from_)
    subject = msg.subject or ""
    submitted = headers.get("auto-submitted", "").strip().lower()
    auto_reply = (
        submitted.startswith("auto-replied")
        or any(h in headers for h in AUTO_HEADERS)
        or bool(AUTO_SUBJECT.search(subject))
    )
    # "no" means a human sent it, whatever else the headers say.
    if submitted == "no":
        auto_reply = False
    bounce = bool(BOUNCE_FROM.match(frm) or BOUNCE_SUBJECT.search(subject))
    shape = {
        "auto_reply": auto_reply,
        # Machine-sent but not a reply: newsletters, alerts, receipts.
        "automated": bool(submitted) and submitted != "no",
        "bounce": bounce,
    }
    if bounce:
        raw = (msg.text or "") + "\n" + (msg.html or "")
        final = DSN_FINAL.search(raw)
        status = DSN_STATUS.search(raw)
        if final:
            shape["bounce_address"] = final.group(1).strip("<>").lower()
        if status:
            code = status.group(1)
            shape["bounce_status"] = code
            # 5.x.x is permanent: the address is dead. 4.x.x is worth retrying.
            shape["bounce_permanent"] = code.startswith("5")
    return shape


SENT_NAMES = ("sent", "enviados", "sent items", "sent mail", "elementos enviados",
              "correo enviado", "gesendet")


def pick_folder(box, wanted: str) -> str:
    """The folder whose name was asked for. 'sent' resolves by the \\Sent special-use
    flag first, and only then by name: providers spell it in their own language."""
    folders = list(box.folder.list())
    if wanted.lower() != "sent":
        for f in folders:
            if f.name.lower() == wanted.lower():
                return f.name
        return wanted  # let the server complain, with its own error
    for f in folders:
        if "\\Sent" in (f.flags or ()):
            return f.name
    for f in folders:
        if f.name.lower().split("/")[-1].split(".")[-1] in SENT_NAMES:
            return f.name
    raise LookupError(
        "no encuentro la carpeta de Enviados. Carpetas: "
        + ", ".join(f.name for f in folders))


def fetch(mb_cfg: dict, since: date, seen_uid: int, folder: str | None = None,
          to: str | None = None, subject: str | None = None) -> dict:
    from imap_tools import AND, MailBox

    out = {"slug": mb_cfg["slug"], "address": mb_cfg["address"], "messages": [],
           "max_uid": seen_uid, "error": None, "folder": folder or "INBOX"}
    try:
        with MailBox(mb_cfg["host"], port=mb_cfg["port"]).login(
                mb_cfg["login"], mb_cfg["password"]) as box:
            if folder:
                name = pick_folder(box, folder)
                out["folder"] = name
                box.folder.set(name)
            criteria = {"date_gte": since}
            if to:
                criteria["to"] = to
            if subject:
                criteria["subject"] = subject
            for msg in box.fetch(AND(**criteria), mark_seen=False, bulk=True):
                uid = int(msg.uid or 0)
                if uid <= seen_uid:
                    continue
                headers = {k.lower(): " ".join(v) for k, v in (msg.headers or {}).items()}
                name, frm = addr_of(msg.from_)
                refs = [r for r in re.findall(r"<([^>]+)>", headers.get("references", ""))]
                in_reply = re.findall(r"<([^>]+)>", headers.get("in-reply-to", ""))
                body = (msg.text or msg.html or "").strip()
                out["messages"].append({
                    "uid": uid,
                    "mailbox": mb_cfg["slug"],
                    "date": msg.date.isoformat() if msg.date else None,
                    "from_name": name,
                    "from": frm,
                    "from_domain": frm.split("@")[-1] if "@" in frm else "",
                    "to": [a for _, a in getaddresses(list(msg.to or []))],
                    "cc": [a for _, a in getaddresses(list(msg.cc or []))],
                    "subject": msg.subject or "",
                    "message_id": (headers.get("message-id", "").strip("<> ") or None),
                    "in_reply_to": in_reply[0] if in_reply else None,
                    "references": refs,
                    "body": body[:BODY_CHARS],
                    "body_truncated": len(body) > BODY_CHARS,
                    **classify_shape(msg, headers),
                })
                out["max_uid"] = max(out["max_uid"], uid)
    except Exception as exc:  # reported, never swallowed
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mailbox", help="slug; default: every mailbox in MAILBOX_SLUGS")
    ap.add_argument("--since", help="YYYY-MM-DD; overrides the saved state")
    ap.add_argument("--days", type=int, help="last N days")
    ap.add_argument("--commit", action="store_true", help="save the new high-water mark")
    ap.add_argument("--folder", help="carpeta a leer; 'sent' la resuelve sola. Por defecto INBOX")
    ap.add_argument("--to", help="solo mensajes dirigidos a esta dirección")
    ap.add_argument("--subject", help="solo mensajes cuyo asunto contenga este texto")
    args = ap.parse_args()

    if args.folder and args.commit:
        sys.exit("--commit no se usa fuera de la bandeja: la marca de agua es del INBOX.")

    env = load_env()
    state = read_state()
    boxes = mailboxes(env, args.mailbox)
    if not boxes:
        sys.exit("MAILBOX_SLUGS está vacío: no hay buzones configurados.")

    result = {"fetched_at": datetime.now().astimezone().isoformat(), "mailboxes": []}
    new_state = dict(state)
    for cfg in boxes:
        if cfg.get("skipped"):
            result["mailboxes"].append({"slug": cfg["slug"], "address": cfg["address"],
                                        "skipped": cfg["skipped"], "messages": []})
            continue
        prev = state.get(cfg["slug"], {})
        if args.since:
            since = date.fromisoformat(args.since)
        elif args.days:
            since = date.today() - timedelta(days=args.days)
        elif prev.get("last_date"):
            since = date.fromisoformat(prev["last_date"])
        else:
            since = date.today() - timedelta(days=30)
        watermark = 0 if (args.since or args.days or args.folder) else int(prev.get("last_uid", 0))
        got = fetch(cfg, since, watermark, folder=args.folder, to=args.to, subject=args.subject)
        got["since"] = since.isoformat()
        result["mailboxes"].append(got)
        if not got["error"] and not args.folder:
            new_state[cfg["slug"]] = {"last_uid": got["max_uid"],
                                      "last_date": date.today().isoformat(),
                                      "last_run": result["fetched_at"]}

    result["total"] = sum(len(m.get("messages", [])) for m in result["mailboxes"])
    result["committed"] = bool(args.commit)
    if args.commit:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(new_state, indent=2) + "\n")

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 1 if any(m.get("error") for m in result["mailboxes"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
