#!/usr/bin/env python3
"""Walk an application the way a person would: click, look, go back.

Sibling of `peek.py`, with a deliberately different contract. `peek.py` clicks nothing, so it
can be pointed at anything without thinking. This one does click, so it is used knowingly and
only on the application of whoever asks.

It also fills forms (`--fill`), to create test data and see the product working. What it does
not do, unless forced: press anything that deletes, cancels or unsubscribes. Exploring is not
destroying, and this runs on production with real people's data inside. `--force` exists and
has to be typed.

Hygiene rule: **everything created from here is prefixed `ZZ TEST`** in its name, so it can be
found and deleted later without wondering whether it was real.

Works on a tab that is ALREADY open (the owner's, which is the one holding the session). It
opens no tabs of its own: in a SPA the session travels by navigating from inside, not by URL.

Usage:
    .venv/bin/python tools/explore.py --url dashboard --map
    .venv/bin/python tools/explore.py --url dashboard --click "Open Recruitment"
    .venv/bin/python tools/explore.py --url recruitment --click "Candidates" --read
    .venv/bin/python tools/explore.py --url recruitment --back
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHOTS = REPO / ".peek"

# Nothing that sounds destructive gets clicked without --force.
PELIGRO = re.compile(
    r"\b(elimin|borrar|delete|remove|descartar|archivar|cancelar|darse de baja|"
    r"unsubscribe|desactivar|vaciar|restablecer|reset|revocar|expulsar)\w*",
    re.IGNORECASE,
)


def load_cdp_url() -> str:
    env = REPO / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("LINKEDIN_CDP_URL="):
                return line.split("=", 1)[1].strip()
    return "http://127.0.0.1:9222"


def attach(url: str):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("falta playwright: uv pip install -r tools/requirements.txt")
    pw = sync_playwright().start()
    try:
        browser = pw.chromium.connect_over_cdp(url)
    except Exception as exc:
        pw.stop()
        sys.exit(f"no hay Chromium en {url} ({type(exc).__name__}: {exc})")
    if not browser.contexts:
        pw.stop()
        sys.exit("Chromium sin contexto abierto")
    return pw, browser.contexts[0]


def find_page(ctx, needle: str | None):
    pages = [p for p in ctx.pages if not p.is_closed()]
    if not pages:
        sys.exit("no hay pestañas abiertas")
    if not needle:
        return pages[-1]
    page = next((p for p in pages if needle.lower() in p.url.lower()), None)
    if page is None:
        opts = "\n".join(f"    {p.url}" for p in pages)
        sys.exit(f"ninguna pestaña con '{needle}'. Abiertas:\n{opts}")
    return page


def show_map(page) -> None:
    """Lo que se puede pulsar en esta pantalla, que es por dónde se puede seguir."""
    items = page.evaluate("""() => {
        const sel = 'a[href], button, [role=button], [role=tab], [role=menuitem], summary';
        return [...document.querySelectorAll(sel)]
            .filter(e => e.offsetParent !== null)
            .map(e => [(e.innerText || e.getAttribute('aria-label') || '').trim()
                        .split('\\n')[0].slice(0, 55),
                       e.tagName.toLowerCase(),
                       e.getAttribute('href') || '',
                       !!(e.disabled || e.getAttribute('aria-disabled') === 'true')])
            .filter(([t]) => t);
    }""")
    seen, out = set(), []
    for text, tag, href, dis in items:
        if text.lower() in seen:
            continue
        seen.add(text.lower())
        flag = "  [!]" if PELIGRO.search(text) else ""
        flag += "  DESHABILITADO" if dis else ""
        out.append(f"  {text:<57} {tag:<8}{href[:40]}{flag}")
    print("\n--- se puede pulsar ---")
    print("\n".join(out) if out else "  (nada clicable visible)")
    print("\n[!] = no se pulsa sin --force")


def show_form(page) -> None:
    """Los campos que se pueden rellenar aquí, con cómo llamarlos en --fill."""
    items = page.evaluate("""() => [...document.querySelectorAll('input, textarea, select')]
        .filter(e => e.offsetParent !== null && e.type !== 'hidden')
        .map(e => {
            const lab = e.labels && e.labels[0] ? e.labels[0].innerText.trim() : '';
            return [lab, e.placeholder || '', e.name || '', e.id || '', e.tagName.toLowerCase(),
                    e.type || ''];
        })""")
    print("\n--- campos ---")
    if not items:
        print("  (ninguno visible)")
        return
    for lab, ph, name, eid, tag, typ in items:
        como = lab or ph or name or eid or "(sin nombre)"
        print(f"  {como:<40} {tag}/{typ:<10} name={name or '-'} id={eid or '-'}")


def read(page, max_chars: int) -> None:
    text = page.evaluate("() => document.body ? document.body.innerText : ''") or ""
    text = "\n".join(l.rstrip() for l in text.splitlines() if l.strip())
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n… (recortado en {max_chars})"
    print(f"\n--- texto visible ---\n{text}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="parte de la URL de la pestaña sobre la que trabajar")
    ap.add_argument("--click", help="texto visible del elemento a pulsar")
    ap.add_argument("--nth", type=int, default=0, help="cuál, si el texto aparece varias veces")
    ap.add_argument("--last", action="store_true",
                    help="el último que coincida. En un modal, el botón de enviar suele serlo")
    ap.add_argument("--go", help="ruta o URL, navegando la MISMA pestaña (conserva la sesión)")
    ap.add_argument("--back", action="store_true", help="volver atrás")
    ap.add_argument("--map", action="store_true", help="qué se puede pulsar aquí")
    ap.add_argument("--form", action="store_true", help="los campos rellenables de la pantalla")
    ap.add_argument("--fill", action="append", default=[], metavar="CAMPO=VALOR",
                    help="rellena un campo por su etiqueta, placeholder o name. Repetible")
    ap.add_argument("--select", action="append", default=[], metavar="CAMPO=OPCIÓN",
                    help="elige una opción de un desplegable, por su texto. Repetible")
    ap.add_argument("--read", action="store_true", help="texto visible tras la acción")
    ap.add_argument("--press", help="tecla a pulsar tras rellenar, p. ej. Enter")
    ap.add_argument("--wait", type=int, default=0, help="segundos a esperar antes de leer")
    ap.add_argument("--shot", action="store_true")
    ap.add_argument("--force", action="store_true", help="pulsar aunque suene a destructivo")
    ap.add_argument("--hard", action="store_true",
                    help="forzar el clic si el elemento no es alcanzable (modales, viewport)")
    ap.add_argument("--max-chars", type=int, default=5000)
    args = ap.parse_args()

    pw, ctx = attach(load_cdp_url())
    try:
        page = find_page(ctx, args.url)

        for pair in args.fill:
            if "=" not in pair:
                sys.exit(f"--fill espera CAMPO=VALOR, recibí '{pair}'")
            campo, valor = pair.split("=", 1)
            target = None
            for finder in (lambda: page.get_by_label(campo, exact=False),
                           lambda: page.get_by_placeholder(campo),
                           lambda: page.locator(f"[name='{campo}']"),
                           lambda: page.locator(f"#{campo}")):
                try:
                    loc = finder().first
                    if loc.count():
                        target = loc
                        break
                except Exception:
                    continue
            if target is None:
                sys.exit(f"no encuentro el campo '{campo}'. Lanza --form para ver cuáles hay")
            target.fill(valor)
            print(f"«{campo}» = {valor}")
        for pair in args.select:
            if "=" not in pair:
                sys.exit(f"--select espera CAMPO=OPCIÓN, recibí '{pair}'")
            campo, valor = pair.split("=", 1)
            loc = None
            for finder in (lambda: page.get_by_label(campo, exact=False),
                           lambda: page.locator(f"#{campo}"),
                           lambda: page.locator(f"select[name='{campo}']")):
                try:
                    cand = finder().first
                    if cand.count():
                        loc = cand
                        break
                except Exception:
                    continue
            if loc is None:
                sys.exit(f"no encuentro el desplegable '{campo}'. Lanza --form")
            loc.select_option(label=valor)
            print(f"«{campo}» → {valor}")

        if args.press and args.fill:
            campo = args.fill[-1].split("=", 1)[0]
            for finder in (lambda: page.get_by_label(campo, exact=False),
                           lambda: page.get_by_placeholder(campo)):
                try:
                    loc = finder().first
                    if loc.count():
                        loc.press(args.press)
                        print(f"tecla {args.press}")
                        break
                except Exception:
                    continue

        if args.fill or args.select:
            page.wait_for_timeout(800)
        if args.wait:
            print(f"esperando {args.wait}s…", flush=True)
            page.wait_for_timeout(args.wait * 1000)

        if args.go:
            dest = args.go if args.go.startswith("http") else (
                page.url.split("/")[0] + "//" + page.url.split("/")[2] + "/" + args.go.lstrip("/"))
            page.goto(dest, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2500)
            print(f"→ {page.url}")

        elif args.click:
            if PELIGRO.search(args.click) and not args.force:
                sys.exit(
                    f"'{args.click}' suena a destructivo y esto corre sobre producción.\n"
                    "  Si de verdad toca, repite con --force."
                )
            # Role first: a button is more precise than any matching text. Searching by
            # text hits the modal's title instead of its submit button.
            pick_one = (lambda l: l.last) if args.last else (lambda l: l.nth(args.nth))
            loc = pick_one(page.get_by_role("button", name=args.click, exact=False))
            if not loc.count():
                loc = pick_one(page.get_by_text(args.click, exact=False))
            if not loc.count():
                sys.exit(f"no encuentro '{args.click}'. Lanza --map para ver qué hay")
            before = page.url
            try:
                loc.scroll_into_view_if_needed(timeout=4000)
            except Exception:
                pass
            try:
                loc.click(timeout=8000)
            except Exception as exc:
                if not args.hard:
                    sys.exit(
                        f"no pude pulsar «{args.click}»: {str(exc).splitlines()[0]}\n"
                        "  Suele ser un modal o el viewport. Repite con --hard, o usa --go."
                    )
                loc.click(force=True, timeout=8000)
                print("  (clic forzado: --hard)")
            page.wait_for_timeout(3000)
            print(f"clic en «{args.click}»")
            if page.url != before:
                print(f"  {before}\n  → {page.url}")

        elif args.back:
            page.go_back()
            page.wait_for_timeout(2500)
            print(f"atrás → {page.url}")

        print(f"URL    : {page.url}")
        print(f"Título : {page.title()}")
        if args.map:
            show_map(page)
        if args.form:
            show_form(page)
        if args.read or not (args.map or args.form or args.click or args.back or args.go or args.fill or args.select) or args.press:
            read(page, args.max_chars)
        if args.shot:
            SHOTS.mkdir(exist_ok=True)
            path = SHOTS / f"explore-{datetime.now():%H%M%S}.png"
            page.screenshot(path=str(path))
            print(f"\ncaptura: {path.relative_to(REPO)}")
        return 0
    finally:
        pw.stop()


if __name__ == "__main__":
    sys.exit(main())
