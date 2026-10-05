---
id: [UUID7]
kind: email
direction: [out | in]
slug: [SLUG DEL CASO]
status: [borrador | enviado | recibido | descartado]
from: [BUZÓN QUE FIRMA, slug de .env]
to: [DESTINATARIO]
subject: [ASUNTO]
written: [YYYY-MM-DD]
sent: [YYYY-MM-DD, de la carpeta Enviados. Vacío mientras sea borrador]
message_id: [EL DEL SERVIDOR, al confirmar]
verbatim: [sí | no, comparado contra el borrador]
answers: [P-1, P-2 — las preguntas de preguntas.md que cubre]
in_reply_to: [MESSAGE-ID AL QUE RESPONDE, si lo hay]
---

# [ASUNTO]

Para [NOMBRE] · [estado y fecha]

## Borrador

[EL TEXTO TAL Y COMO SE ESCRIBIÓ. No se toca después de enviarlo: es lo que se propuso.]

## Lo que salió

[Solo cuando `verbatim: no`. El cuerpo exacto que se leyó de la carpeta de Enviados, con su
fecha y su Message-ID. Si coincide con el borrador, esta sección no existe.]

## Qué cambió al enviarlo

[Solo cuando `verbatim: no`. Las diferencias que importan, en viñetas. Un cambio de saludo no
importa; una pregunta que desapareció o un plazo que se añadió, sí, y entonces se corrige
`answers:` y lo que toque en `preguntas.md`.]
