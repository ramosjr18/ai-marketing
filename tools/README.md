# tools/

Code, only where an agent cannot reach: reading IMAP, parsing, rendering.

## Setup on a new machine

```bash
uv venv                                        # or: python3 -m venv .venv
uv pip install -r tools/requirements.txt
```

`.venv/` is gitignored. On Arch there is no `python-imap-tools` package in the official
repositories, and pip cannot install globally (PEP 668), so a virtualenv is the way.

Scripts read credentials from the repo's `.env`, written by `/set-engine` and `/set-mail`.

## `imap_fetch.py` — leer el buzón, sin tocarlo

Para `/mail-sync` y `/client email confirm`. El agente no sabe hablar IMAP; esto baja los
mensajes nuevos y los imprime en JSON. Todo lo demás (emparejar una respuesta con un prospecto,
clasificarla, decidir qué se contesta) es markdown y lo aprueba una persona.

Dos reglas que no se saltan:

- **No marca nada como leído.** Se baja con PEEK, así que el buzón queda como estaba para quien
  lo abre después.
- **La marca de agua solo avanza con `--commit`.** Una corrida que se cae a mitad de clasificar
  no puede perder mensajes, así que leer y dar por leído son dos pasos.

```bash
tools/imap_fetch.py                        # todos los buzones, desde la última vez
tools/imap_fetch.py --mailbox alex         # uno
tools/imap_fetch.py --days 7               # los últimos 7 días
tools/imap_fetch.py --commit               # guarda la marca de agua
tools/imap_fetch.py --folder sent --to alguien@example.com --days 7
```

`--folder` lee fuera de la bandeja de entrada y **nunca toca el estado**: la marca de agua es de
la bandeja, y buscar en Enviados no debe moverla. Es lo que usa `/client email confirm` para
guardar la versión que salió de verdad.

## `linkedin.py` — canal LinkedIn asistido

Opera sobre **el Chromium que arrancas tú**, con tu sesión ya iniciada. No abre navegadores, no
guarda credenciales de LinkedIn y no toca perfiles que no estén en `prospects.csv`. Los
límites y los topes están escritos en la cabecera del propio fichero.

Arranca Chromium con el puerto de depuración abierto y entra en LinkedIn como cualquier día:

```bash
chromium --remote-debugging-port=9222
```

Luego:

```bash
.venv/bin/python tools/linkedin.py check
.venv/bin/python tools/linkedin.py profile <key|url> --unit acme
.venv/bin/python tools/linkedin.py invite  <key|url> --unit acme --note-file <f> [--send]
.venv/bin/python tools/linkedin.py message <key|url> --unit acme --text-file <f> [--send]
```

**Sin `--send` no pulsa nada**: navega, enseña el texto que enviaría y sale. Los topes diarios
(15 invitaciones · 20 mensajes · 40 perfiles) y la ventana 09:00-17:00 L-V no tienen bandera para
saltárselos. El contador del día vive en `offering/_shared/linkedin-usage.json`.

Se llega a cada perfil **por el buscador de LinkedIn y haciendo clic**, no pegando su URL: la
única navegación directa es abrir el feed al empezar. Del resultado se abre solo el que coincide
con el `linkedin_url` del tracker.

Si un selector no aparece, **para**. Es deliberado: significa que LinkedIn ha cambiado la página,
y lo correcto es arreglar el script, no buscar un botón parecido.

## `explore.py` — recorrer la aplicación, pulsando

Hermano de `peek.py`, con el contrato contrario a propósito. `peek.py` no pulsa nada, así que se
lanza sobre cualquier cosa sin pensarlo; éste **sí pulsa**, y por eso se usa a sabiendas y solo
sobre la aplicación de quien lo pide.

Rellena formularios con `--fill`, para crear datos de prueba y ver el producto funcionando. Lo
que no hace, salvo que se le fuerce: pulsar lo que borra, cancela o da de baja. **`--force`
existe y hay que escribirlo.** Y todo lo que crea lleva el prefijo `ZZ TEST` en el nombre, para
poder encontrarlo y borrarlo después sin dudar de si era real.

Trabaja sobre una pestaña **ya abierta**, la que tiene la sesión. No abre pestañas propias: en
una SPA la sesión se pasa navegando desde dentro, no por URL.

```bash
.venv/bin/python tools/explore.py --url dashboard --map
.venv/bin/python tools/explore.py --url dashboard --click "Abrir Recruitment"
.venv/bin/python tools/explore.py --url recruitment --click "Candidatos" --read
.venv/bin/python tools/explore.py --url recruitment --back
```

## `peek.py` — leer la pestaña que tienes delante

Para `/product`: tú navegas por tu aplicación y el agente mira. **No pulsa nada** — el script no
tiene una sola llamada a `click`, `fill` ni `goto`, y eso es deliberado: la app es producción y
tiene datos de personas reales dentro.

Mismo Chromium que `linkedin.py` (`--remote-debugging-port=9222`):

```bash
.venv/bin/python tools/peek.py            # describe la pestaña activa
.venv/bin/python tools/peek.py --shot     # y guarda una captura en .peek/ (gitignored)
.venv/bin/python tools/peek.py --list     # qué pestañas hay abiertas
```

## `transcribe.py` — la grabación a texto, aquí

Para `/client`: dejas el audio de una llamada y sale un markdown que el agente puede leer. El
modelo corre en esta máquina (faster-whisper sobre CPU) y **la grabación no se sube a ningún
sitio**.

```bash
.venv/bin/python tools/transcribe.py <audio>                        .md al lado del audio
.venv/bin/python tools/transcribe.py <audio> --out clients/x/transcripts/
.venv/bin/python tools/transcribe.py <carpeta>                      lo que no esté transcrito
.venv/bin/python tools/transcribe.py <audio> --model medium         más lento, mejor con cifras
```

Modelos: `tiny` · `base` · `small` (por defecto) · `medium` · `large-v3`. Se descargan la
primera vez a `~/.cache/huggingface`. `small` basta para entender una conversación; sube a
`medium` cuando la llamada vaya llena de números, que es con lo que más se equivoca.

Dos límites que van escritos dentro de cada transcripción y no se quitan: **no distingue quién
habla**, y **se equivoca con las cifras, los nombres propios y las siglas**. Un diagnóstico se
construye sobre números, así que cualquiera que salga de aquí se confirma antes de usarlo.

El audio se decodifica con el **ffmpeg del sistema**, no con PyAV: PyAV 19 cambió la firma de
`open()` y faster-whisper no lo soporta, y no hay rueda de una versión anterior para Python
3.14. Hace falta `ffmpeg` instalado (`sudo pacman -S ffmpeg` en Arch).

## `id7.py` — un identificador por línea

UUID v7: lleva la hora dentro, así que ordenar por nombre es ordenar por cuándo pasó. Nombra las
transcripciones y los resúmenes de `clients/`.

```bash
.venv/bin/python tools/id7.py          # uno
.venv/bin/python tools/id7.py 5        # cinco
```
