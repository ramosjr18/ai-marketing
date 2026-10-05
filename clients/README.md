# clients/

Un caso por carpeta: lo que el cliente te contó, lo que se midió, y lo que se le mandó.
Todo gitignored menos este fichero. Dentro hay personas con nombre y apellido.

Lo abre `/client`, lo estudia `/diagnose`, lo escribe `/propose`.

```
clients/<slug>/
  caso.md              la ficha: identidad, estado, qué unidad se baraja, siguiente paso
  empresa.md           el dosier: quiénes son, con fuente y fecha en cada línea
  antecedentes.md      qué hicieron antes con terceros, y qué abandonaron
  reputacion.md        qué se dice de ellos fuera
  como-trabajan.md     cómo deciden, cómo compran, qué valoran
  personas.md          quién es quién, y quién firma de verdad
  material/            lo crudo: audio, PDFs, capturas, hilos de correo
  transcripts/         <uuid7>.md — una conversación cada uno
  summaries/           <uuid7>.md — el problema, lo hablado, lo prometido, de un transcript
  emails/              <uuid7>.md — lo que le mandas y lo que contesta
  fuentes.md           inventario de todo lo anterior: qué es, de cuándo, quién habla
  diagnostico.md       procesos medidos, coste, ahorro, go/no-go
  preguntas.md         lo que falta saber antes de poner un precio
  proposals/           YYYY-MM-DD-<tipo>.md, una por cada cosa que le mandas
```

Carpetas en inglés como en el resto del repo, documentos en español porque son contenido.

Los cinco ficheros del dosier los escribe `/client research <slug>`, y se rehacen cuando aparece
material nuevo. `caso.md` se queda corto a propósito: es la ficha, no el dosier. Misma razón por
la que `unit.md` y `product.md` son dos ficheros en el blueprint.

## Por qué UUID v7

Las transcripciones y sus resúmenes se nombran con un **UUID v7**: lleva la hora dentro, así
que ordenar por nombre es ordenar por cuándo pasó, y dos conversaciones del mismo día no
chocan. El resumen apunta a su transcripción por ese identificador, y `fuentes.md` los lista
con fecha y una línea de qué son, que es como los encuentra una persona.

```bash
.venv/bin/python tools/id7.py          # uno
```

Las propuestas no: esas se llaman `YYYY-MM-DD-<tipo>.md` porque se mandan fuera y hay que
reconocerlas de un vistazo.

## Los correos de un caso no son outreach

`/outreach` es frío, va por campaña, lo manda el motor y deja rastro en `prospects.csv` y
`events.csv`. Un correo de caso lo escribe una persona, lo manda una persona y **no toca el
tracker**.

Lo que se guarda es lo que salió de verdad, no lo que se redactó: `/client email <slug> confirm`
lee tu carpeta de Enviados y compara. Si el texto cambió por el camino, el borrador se queda y
debajo va el cuerpo real. Un correo que no aparece en Enviados **no se marca como enviado**.

## El slug es una etiqueta, no una clave

Un caso puede nacer sin saber de quién es: `2026-10-02-consultora-bcn` vale. La identidad vive
en el frontmatter de `caso.md`, en un solo sitio, y **nada de fuera apunta hacia dentro de un
caso** — el enlace va al revés: `caso.md` guarda la clave del prospecto, no `prospects.csv` la
del caso.

Por eso renombrar es gratis: `/client rename <viejo> <nuevo>`. Y si dos carpetas resultan ser la
misma empresa, `/client merge <de> <a>`.

## Qué se puede dejar en `material/`

| Formato | Cómo se lee |
|---|---|
| `.md` `.txt` | tal cual |
| `.vtt` `.srt` | transcripción con marcas de tiempo; se limpia al leer |
| `.pdf` | `pdftotext` |
| `.png` `.jpg` | como imagen |
| `.csv` `.xlsx` | tabla |
| `.m4a` `.mp3` `.wav` `.ogg` | `tools/transcribe.py`, whisper en local. La grabación no sale de tu máquina |

Lo demás se lista y se salta.

## Dos cosas que no son negociables

- **Grabar una llamada es decisión de quien la graba.** Lo que entra aquí se obtuvo con el
  consentimiento de quien habla. Ningún comando puede comprobarlo; queda escrito.
- **Esto no viaja.** No entra en git, y en `/export` cuenta como datos de terceros: se pregunta,
  y por defecto no sale.
