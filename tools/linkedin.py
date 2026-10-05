#!/usr/bin/env python3
"""Assisted LinkedIn channel: drives the Chromium that already holds the session.

What matters:

  - Attaches over CDP to a Chromium the person starts. It opens no browser and touches no
    credentials.
  - Only profiles already in prospects.csv, reached through LinkedIn's own search and a click,
    never by pasting the URL: navigating straight there is a signature. Of the results it
    accepts only the one matching the tracker's linkedin_url.
  - Without --send it writes nothing on LinkedIn: it navigates, says what it would do, exits.
  - Random pauses and daily caps. A fixed interval is the signature this avoids.
  - On anything unexpected it stops. Never an approximate click.

Usage:
    .venv/bin/python tools/linkedin.py check
    .venv/bin/python tools/linkedin.py profile <url|key> --unit acme
    .venv/bin/python tools/linkedin.py invite  <url|key> --unit acme --note-file <f> [--send]
    .venv/bin/python tools/linkedin.py message <url|key> --unit acme --text-file <f> [--send]
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parent.parent
BLUEPRINT = REPO / ".claude" / "skills" / "company-blueprint"
OFFERING = BLUEPRINT / "offering"
SHARED = OFFERING / "_shared"
USAGE = SHARED / "linkedin-usage.json"
EVENTS = SHARED / "events.csv"
SUPPRESSION = SHARED / "suppression.csv"

TZ = ZoneInfo("Europe/Madrid")

# Daily caps. There is no flag to skip them.
CAPS = {"invite": 15, "message": 20, "profile": 40}
WINDOW = (9, 17)          # hora local, inclusive-exclusive
WORKDAYS = range(0, 5)    # lunes a viernes
PAUSE_ACTION = (5.0, 20.0)
PAUSE_PROFILE = (30.0, 90.0)

NOTE_MAX = 250            # límite de LinkedIn para la nota de invitación


class Stop(Exception):
    """Algo no es como se esperaba. Se para y se cuenta, no se improvisa."""


# ----------------------------------------------------------------------- environment

def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    path = REPO / ".env"
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env


def cdp_url(env: dict[str, str]) -> str:
    return env.get("LINKEDIN_CDP_URL", "http://127.0.0.1:9222")


# ----------------------------------------------------------------------------- pacing

def now() -> datetime:
    return datetime.now(TZ)


def check_window() -> None:
    t = now()
    if t.weekday() not in WORKDAYS:
        raise Stop(f"fuera de ventana: hoy es {t:%A}, la ventana es lunes a viernes")
    if not (WINDOW[0] <= t.hour < WINDOW[1]):
        raise Stop(
            f"fuera de ventana: son las {t:%H:%M} y la ventana es "
            f"{WINDOW[0]:02d}:00-{WINDOW[1]:02d}:00 Europe/Madrid"
        )


def read_usage() -> dict[str, int]:
    today = date.today().isoformat()
    if USAGE.exists():
        data = json.loads(USAGE.read_text())
        if data.get("date") == today:
            return {k: int(v) for k, v in data.get("counts", {}).items()}
    return {}


def bump_usage(kind: str) -> int:
    counts = read_usage()
    counts[kind] = counts.get(kind, 0) + 1
    USAGE.parent.mkdir(parents=True, exist_ok=True)
    USAGE.write_text(json.dumps({"date": date.today().isoformat(), "counts": counts}, indent=2))
    return counts[kind]


def check_cap(kind: str) -> None:
    used = read_usage().get(kind, 0)
    cap = CAPS[kind]
    if used >= cap:
        raise Stop(f"tope diario alcanzado para '{kind}': {used}/{cap}. Mañana.")


def pause(span: tuple[float, float], why: str) -> None:
    secs = random.uniform(*span)
    print(f"  · pausa {secs:.1f}s ({why})", flush=True)
    time.sleep(secs)


# --------------------------------------------------------------------------- tracker

@dataclass
class Prospect:
    key: str
    campaign: str
    company: str
    contact_name: str
    linkedin_url: str
    status: str
    row: dict


def prospects_path(unit: str) -> Path:
    p = OFFERING / unit / "prospects.csv"
    if not p.exists():
        raise Stop(f"no existe {p.relative_to(REPO)}")
    return p


def load_prospect(unit: str, ref: str) -> Prospect:
    """ref es una key del CSV o una URL de LinkedIn que esté en él."""
    ref_n = ref.rstrip("/").lower()
    with prospects_path(unit).open() as fh:
        for row in csv.DictReader(fh):
            url = (row.get("linkedin_url") or "").rstrip("/").lower()
            if row["key"].lower() == ref_n or (url and url == ref_n):
                return Prospect(
                    key=row["key"],
                    campaign=(row.get("campaign") or "").strip(),
                    company=row.get("company", ""),
                    contact_name=row.get("contact_name", ""),
                    linkedin_url=(row.get("linkedin_url") or "").strip(),
                    status=row.get("status", ""),
                    row=row,
                )
    raise Stop(
        f"'{ref}' no está en {prospects_path(unit).relative_to(REPO)}. "
        "Solo se opera sobre perfiles del tracker."
    )


def is_suppressed(key: str, email: str) -> bool:
    if not SUPPRESSION.exists():
        return False
    with SUPPRESSION.open() as fh:
        for row in csv.DictReader(fh):
            hit = row.get("key", "") == key or (email and row.get("email", "") == email)
            if hit and row.get("reason", "") != "reactivated":
                return True
    return False


EVENT_COLS = ["ts", "unit", "campaign", "key", "type", "channel", "touch", "summary", "by"]


def log_event(unit: str, campaign: str, key: str, etype: str,
              touch: str, summary: str) -> None:
    """Append to events.csv with the columns it actually has.

    The schema is documented in `templates/offering/README-outreach.md`. Writing a row of a
    different width does not fail loudly: it quietly shifts every field of that row, and the
    tracker lies from then on. So the header is checked, not assumed.
    """
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    if EVENTS.exists():
        with EVENTS.open() as fh:
            header = (fh.readline().strip().split(",") if fh else [])
        if header and header != EVENT_COLS:
            raise Stop(
                f"events.csv tiene otras columnas de las que espero.\n"
                f"  fichero: {','.join(header)}\n"
                f"  espero : {','.join(EVENT_COLS)}\n"
                "  No escribo: una fila de otro ancho desplaza los campos y el tracker miente."
            )
    else:
        with EVENTS.open("w", newline="") as fh:
            csv.writer(fh).writerow(EVENT_COLS)
    with EVENTS.open("a", newline="") as fh:
        csv.writer(fh).writerow([
            now().isoformat(timespec="seconds"), unit, campaign, key, etype,
            "linkedin", touch, summary, "linkedin.py",
        ])


# --------------------------------------------------------------------------- browser

def attach(env: dict[str, str]):
    """Devuelve (playwright, page) sobre una pestaña NUEVA del Chromium de la persona.

    Nunca se reutiliza una pestaña suya: navegarla le movería el sitio donde está. Y nunca se
    llama a browser.close(), que sobre una conexión CDP es una forma de tocar su navegador; se
    cierra la pestaña propia y se suelta la conexión.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise Stop("falta playwright: uv pip install -r tools/requirements.txt")

    url = cdp_url(env)
    pw = sync_playwright().start()
    try:
        browser = pw.chromium.connect_over_cdp(url)
    except Exception as exc:
        pw.stop()
        raise Stop(
            f"no hay Chromium escuchando en {url}.\n"
            "  Arráncalo tú con: chromium --remote-debugging-port=9222\n"
            f"  ({type(exc).__name__}: {exc})"
        )

    if not browser.contexts:
        pw.stop()
        raise Stop("Chromium responde pero no tiene ningún contexto abierto")

    ctx = browser.contexts[0]
    if not any(c["name"] == "li_at" for c in ctx.cookies("https://www.linkedin.com")):
        pw.stop()
        raise Stop(
            "el perfil de Chromium no tiene sesión de LinkedIn (falta la cookie 'li_at').\n"
            "  Entra en LinkedIn en ese mismo navegador y vuelve a lanzarlo."
        )
    return pw, ctx.new_page()


def detach(pw, page) -> None:
    try:
        page.close()
    except Exception:
        pass
    pw.stop()


HOME = "https://www.linkedin.com/feed/"


def open_home(page) -> None:
    """La única navegación por URL de todo el script: abrir LinkedIn.

    A partir de aquí se llega a todo haciendo clic, como lo haría una persona. Entrar
    pegando la URL de un perfil es una firma tan reconocible como un intervalo fijo.
    """
    page.goto(HOME, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1500)


def normalize(url: str) -> str:
    u = (url or "").strip().lower().split("?")[0].rstrip("/")
    for prefix in ("https://", "http://", "www.", "es.", "uk.", "fr.", "de."):
        if u.startswith(prefix):
            u = u[len(prefix):]
    return u


def search_and_open(page, prospect: "Prospect") -> None:
    """Llega al perfil por el buscador de LinkedIn, no pegando su URL.

    El resultado se acepta solo si su enlace coincide con el `linkedin_url` del tracker. Si no
    aparece, se para: no se pagina, no se prueba otro nombre y no se abre un perfil parecido.
    """
    target = normalize(prospect.linkedin_url)
    if not target:
        raise Stop(f"{prospect.key} no tiene linkedin_url en el tracker")

    box = page.locator(
        "input.search-global-typeahead__input, "
        "input[placeholder*='Buscar'], input[placeholder*='Search']"
    ).first
    if not box.count():
        raise Stop("no encuentro el buscador de LinkedIn. La página ha cambiado: se para aquí.")

    query = " ".join(x for x in (prospect.contact_name, prospect.company) if x).strip()
    box.click()
    pause(PAUSE_ACTION, "antes de teclear la búsqueda")
    box.type(query, delay=random.randint(60, 140))
    pause(PAUSE_ACTION, "revisar lo tecleado")
    box.press("Enter")
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    page.wait_for_timeout(2500)
    guard_interstitial(page)

    links = page.locator("a[href*='/in/']")
    for i in range(min(links.count(), 30)):
        href = links.nth(i).get_attribute("href") or ""
        if normalize(href) == target:
            pause(PAUSE_ACTION, "antes de abrir el resultado")
            links.nth(i).click()
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            if normalize(page.url) != target:
                raise Stop(
                    f"el clic ha llevado a {page.url} y esperaba {prospect.linkedin_url}. Se para."
                )
            return

    raise Stop(
        f"'{query}' no devuelve el perfil esperado ({prospect.linkedin_url}) en la primera "
        "página de resultados. No se pagina ni se abre otro parecido: revísalo a mano."
    )


def assert_logged_in(page) -> str:
    """Para si LinkedIn ha devuelto un muro. La sesión ya se comprobó por cookie en attach()."""
    for wall in ("/login", "/checkpoint", "/authwall", "/uas/"):
        if wall in page.url:
            raise Stop(f"LinkedIn ha devuelto un muro: {page.url}")
    me = page.locator("img.global-nav__me-photo, .global-nav__me").first
    try:
        me.wait_for(state="attached", timeout=6000)
        return (me.get_attribute("alt") or "").strip() or "sesión iniciada"
    except Exception:
        return "sesión iniciada"


def read_profile(page, prospect: "Prospect") -> dict:
    open_home(page)
    assert_logged_in(page)
    search_and_open(page, prospect)
    if "/404" in page.url or "unavailable" in page.url:
        raise Stop(f"el perfil no existe o no es accesible: {prospect.linkedin_url}")

    def text(sel: str) -> str:
        loc = page.locator(sel).first
        try:
            loc.wait_for(state="attached", timeout=5000)
            return (loc.inner_text() or "").strip().split("\n")[0]
        except Exception:
            return ""

    name = text("main h1")
    headline = text("main .text-body-medium")
    body = page.content()
    state = "desconocido"
    if "Pendiente" in body or "Pending" in body:
        state = "invitación pendiente"
    elif page.locator("button:has-text('Mensaje'), button:has-text('Message')").count():
        state = "conectado o se puede mensajear"
    elif page.locator("button:has-text('Conectar'), button:has-text('Connect')").count():
        state = "sin conexión, se puede invitar"
    return {"url": page.url, "name": name, "headline": headline, "state": state}


def click_one(page, selector: str, what: str):
    loc = page.locator(selector).first
    if not loc.count():
        raise Stop(
            f"no encuentro {what} ({selector}). La página ha cambiado: "
            "se para aquí, no se hace clic a ciegas."
        )
    loc.click()
    return loc


def guard_interstitial(page) -> None:
    body = page.content().lower()
    for marker in ("captcha", "verifica que eres", "verify you", "unusual activity",
                   "has alcanzado el límite", "you've reached the", "weekly invitation limit"):
        if marker in body:
            raise Stop(
                f"LinkedIn ha mostrado un aviso ('{marker}'). Se para y no se reintenta hoy."
            )


# --------------------------------------------------------------------------- actions

def do_invite(page, note: str, send: bool) -> str:
    if len(note) > NOTE_MAX:
        raise Stop(f"la nota tiene {len(note)} caracteres y el máximo es {NOTE_MAX}")
    if not send:
        return "dry: no se pulsa nada"

    click_one(page, "button:has-text('Conectar'), button:has-text('Connect')", "el botón Conectar")
    pause(PAUSE_ACTION, "abrir el diálogo")
    guard_interstitial(page)

    click_one(page,
              "button:has-text('Añadir nota'), button:has-text('Add a note')",
              "el botón Añadir nota")
    pause(PAUSE_ACTION, "escribir la nota")

    box = page.locator("textarea#custom-message, textarea[name='message']").first
    if not box.count():
        raise Stop("no encuentro el cuadro de la nota")
    box.fill(note)
    pause(PAUSE_ACTION, "revisar antes de enviar")
    guard_interstitial(page)

    click_one(page, "button:has-text('Enviar'), button:has-text('Send')", "el botón Enviar")
    page.wait_for_timeout(2500)
    guard_interstitial(page)
    return "invitación enviada"


def do_message(page, text: str, send: bool) -> str:
    if not send:
        return "dry: no se pulsa nada"

    click_one(page, "button:has-text('Mensaje'), button:has-text('Message')", "el botón Mensaje")
    pause(PAUSE_ACTION, "abrir la conversación")
    guard_interstitial(page)

    box = page.locator("div.msg-form__contenteditable[contenteditable='true']").first
    if not box.count():
        raise Stop("no encuentro el cuadro de mensaje")
    box.click()
    box.type(text, delay=random.randint(18, 45))
    pause(PAUSE_ACTION, "revisar antes de enviar")
    guard_interstitial(page)

    click_one(page, "button.msg-form__send-button", "el botón de enviar mensaje")
    page.wait_for_timeout(2500)
    guard_interstitial(page)
    return "mensaje enviado"


# ------------------------------------------------------------------------ subcommands

def cmd_check(args, env) -> int:
    pw, page = attach(env)
    try:
        open_home(page)
        who = assert_logged_in(page)
        used = read_usage()
        print(f"Chromium  : {cdp_url(env)}  ok")
        print(f"Sesión    : {who}")
        print(f"Hoy       : " + " · ".join(
            f"{k} {used.get(k, 0)}/{CAPS[k]}" for k in CAPS))
        t = now()
        inside = t.weekday() in WORKDAYS and WINDOW[0] <= t.hour < WINDOW[1]
        print(f"Ventana   : {t:%a %H:%M} — {'dentro' if inside else 'FUERA'}")
        return 0
    finally:
        detach(pw, page)


def _prepare(args, env):
    p = load_prospect(args.unit, args.ref)
    if not p.linkedin_url:
        raise Stop(f"{p.key} no tiene linkedin_url en el tracker")
    if is_suppressed(p.key, p.row.get("email", "")):
        raise Stop(f"{p.key} está en suppression.csv. No se abre.")
    return p


def cmd_profile(args, env) -> int:
    check_window()
    check_cap("profile")
    p = _prepare(args, env)
    pw, page = attach(env)
    try:
        info = read_profile(page, p)
        bump_usage("profile")
        print(f"{p.key}  ({p.company})")
        print(f"  nombre : {info['name']}")
        print(f"  titular: {info['headline']}")
        print(f"  estado : {info['state']}")
        print(f"  url    : {info['url']}")
        return 0
    finally:
        detach(pw, page)


def _act(args, env, kind: str, body: str, runner) -> int:
    check_window()
    check_cap(kind)
    check_cap("profile")
    p = _prepare(args, env)
    if not p.campaign:
        raise Stop(
            f"{p.key} no está en ninguna campaña (columna 'campaign' vacía).\n"
            "  Una campaña dice para qué se escribe: /campaign <unit>."
        )
    touch = _touch_from(getattr(args, "note_file", None) or getattr(args, "text_file", ""))

    print(f"{p.key}  ({p.company} · {p.contact_name})")
    print(f"  acción : {kind}{'' if args.send else '  [DRY: no se envía nada]'}")
    print(f"  texto  : {len(body)} caracteres")
    for line in body.splitlines():
        print(f"    | {line}")

    pw, page = attach(env)
    try:
        info = read_profile(page, p)
        bump_usage("profile")
        print(f"  perfil : {info['name']} — {info['state']}")

        if kind == "invite" and "pendiente" in info["state"]:
            print("  nada que hacer: la invitación ya está pendiente")
            log_event(args.unit, p.campaign, p.key, "note", touch,
                      "invitación ya pendiente, no se repite")
            return 0

        pause(PAUSE_ACTION, "antes de actuar")
        result = runner(page, body, args.send)
        print(f"  → {result}")

        if args.send:
            n = bump_usage(kind)
            log_event(args.unit, p.campaign, p.key, "sent", touch, result)
            print(f"  registrado en events.csv · {kind} {n}/{CAPS[kind]} hoy")
            pause(PAUSE_PROFILE, "antes del siguiente perfil")
        return 0
    finally:
        detach(pw, page)


def _touch_from(path: str) -> str:
    """linkedin-2.md -> "2". El nombre del borrador lleva el número de toque."""
    m = re.search(r"linkedin-(\d+)", str(path))
    return m.group(1) if m else ""


def cmd_invite(args, env) -> int:
    return _act(args, env, "invite", Path(args.note_file).read_text().strip(), do_invite)


def cmd_message(args, env) -> int:
    return _act(args, env, "message", Path(args.text_file).read_text().strip(), do_message)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="engancha con Chromium y dice qué ve")

    def with_target(p):
        p.add_argument("ref", help="key del tracker o URL de LinkedIn que esté en él")
        p.add_argument("--unit", required=True, help="slug de la unidad (acme, ...)")
        return p

    with_target(sub.add_parser("profile", help="abre un perfil y describe su estado"))

    p_inv = with_target(sub.add_parser("invite", help="invitación con nota"))
    p_inv.add_argument("--note-file", required=True)
    p_inv.add_argument("--send", action="store_true", help="sin esto no se pulsa nada")

    p_msg = with_target(sub.add_parser("message", help="mensaje a un contacto"))
    p_msg.add_argument("--text-file", required=True)
    p_msg.add_argument("--send", action="store_true", help="sin esto no se pulsa nada")

    args = ap.parse_args()
    env = load_env()
    fn = {"check": cmd_check, "profile": cmd_profile,
          "invite": cmd_invite, "message": cmd_message}[args.cmd]
    try:
        return fn(args, env)
    except Stop as exc:
        print(f"PARADO: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
