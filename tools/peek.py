#!/usr/bin/env python3
"""Read the active tab of the owner's Chromium. Touches nothing.

Used by `/product`: the owner browses their own application and the agent looks. That
application is production with real people's data in it, so this script **clicks nothing**.
There is not one call to click, fill, type or press in this file, and there will not be.

It does navigate by URL with --open, in a tab of its own that it opens and closes. Navigating
asks for a page; clicking runs an action. That distinction is what makes this safe on
production.

Attaches over CDP to a Chromium the owner starts:

    chromium --remote-debugging-port=9222

Usage:
    .venv/bin/python tools/peek.py                 describe the active tab
    .venv/bin/python tools/peek.py --shot          and save a screenshot
    .venv/bin/python tools/peek.py --list          list open tabs
    .venv/bin/python tools/peek.py --tab 0         one tab, by index from --list
    .venv/bin/python tools/peek.py --url panel     the first whose URL contains that text
    .venv/bin/python tools/peek.py --links         the page's links, to know where to go next
    .venv/bin/python tools/peek.py --open URL      open it in its own tab, read it, close it
    .venv/bin/python tools/peek.py --max-chars N   trim the text (default 6000)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHOTS = REPO / ".peek"


def load_cdp_url() -> str:
    env_file = REPO / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("LINKEDIN_CDP_URL="):
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
        sys.exit(
            f"no hay Chromium escuchando en {url}.\n"
            "  Arráncalo tú con: chromium --remote-debugging-port=9222\n"
            f"  ({type(exc).__name__}: {exc})"
        )
    if not browser.contexts:
        pw.stop()
        sys.exit("Chromium responde pero no tiene ningún contexto abierto")
    return pw, browser.contexts[0]


def active_page(ctx):
    """La pestaña que la persona tiene delante.

    Playwright no expone "la activa", así que se toma la última que no esté oculta. Con una
    sola pestaña visible, que es el caso normal cuando alguien enseña algo, coincide.
    """
    pages = [p for p in ctx.pages if not p.is_closed()]
    if not pages:
        sys.exit("no hay ninguna pestaña abierta")
    for p in reversed(pages):
        try:
            if p.evaluate("document.visibilityState") == "visible":
                return p
        except Exception:
            continue
    return pages[-1]


def report(page, args) -> int:
    print(f"URL    : {page.url}")
    print(f"Título : {page.title()}")

    if args.links:
        links = page.evaluate("""() => [...document.querySelectorAll('a[href]')]
            .map(a => [a.innerText.trim().split('\\n')[0].slice(0, 60), a.href])
            .filter(([t, h]) => h && !h.startsWith('javascript'))""")
        seen = set()
        for text_, href in links:
            if href not in seen:
                seen.add(href)
                print(f"  {text_ or '(sin texto)':<42} {href}")
        print(f"\n{len(seen)} enlaces únicos")
        return 0

    text = page.evaluate("() => document.body ? document.body.innerText : ''") or ""
    text = "\n".join(line.rstrip() for line in text.splitlines() if line.strip())
    if len(text) > args.max_chars:
        text = text[:args.max_chars] + f"\n… (recortado en {args.max_chars} caracteres)"
    print(f"\n--- texto visible ---\n{text}")

    if args.shot:
        SHOTS.mkdir(exist_ok=True)
        path = SHOTS / f"peek-{datetime.now():%Y%m%d-%H%M%S}.png"
        page.screenshot(path=str(path), full_page=False)
        print(f"\ncaptura: {path.relative_to(REPO)}")
    return 0


def pick(ctx, args):
    """La página a leer. --open abre una pestaña PROPIA; el resto son suyas, no se tocan."""
    if args.open:
        page = ctx.new_page()
        page.goto(args.open, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)
        return page, True

    pages = [p for p in ctx.pages if not p.is_closed()]
    if args.tab is not None:
        if not 0 <= args.tab < len(pages):
            sys.exit(f"no hay pestaña {args.tab}: hay {len(pages)}. Mira --list")
        return pages[args.tab], False
    if args.url:
        page = next((p for p in pages if args.url.lower() in p.url.lower()), None)
        if page is None:
            sys.exit(f"ninguna pestaña con '{args.url}' en la URL. Mira --list")
        return page, False
    return active_page(ctx), False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shot", action="store_true", help="guarda una captura en .peek/")
    ap.add_argument("--tab", type=int, help="índice de pestaña, de --list")
    ap.add_argument("--url", help="primera pestaña cuya URL contenga este texto")
    ap.add_argument("--open", help="URL a abrir en una pestaña propia, leer y cerrar")
    ap.add_argument("--links", action="store_true", help="lista los enlaces de la página")
    ap.add_argument("--list", action="store_true", help="lista las pestañas y sale")
    ap.add_argument("--max-chars", type=int, default=6000)
    args = ap.parse_args()

    pw, ctx = attach(load_cdp_url())
    mine = None
    try:
        if args.list:
            for i, p in enumerate(ctx.pages):
                if not p.is_closed():
                    print(f"  [{i}] {p.title()[:60]:<62} {p.url}")
            return 0
        page, mine_flag = pick(ctx, args)
        mine = page if mine_flag else None
        return report(page, args)
    finally:
        if mine is not None:
            try:
                mine.close()
            except Exception:
                pass
        pw.stop()


if __name__ == "__main__":
    sys.exit(main())
