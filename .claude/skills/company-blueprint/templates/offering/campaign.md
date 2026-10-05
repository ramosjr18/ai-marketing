---
slug: [CAMPAIGN_SLUG]
unit: [UNIT_SLUG]
status: draft
market: [MARKET]
channel: [email|linkedin|both]
cadence: [email-2|linkedin-3]
mailbox: [SENDING_ADDRESS]
signer: [PERSON_SLUG]
created: [YYYY-MM-DD]
closed: [YYYY-MM-DD or empty]
---

# [CAMPAIGN_NAME]

**Objetivo:** [WHAT_THIS_CAMPAIGN_IS_TRYING_TO_MAKE_HAPPEN]

Tiene que poder comprobarse si pasó o no. «Que prueben el trial de 30 días» sirve; «dar a
conocer el producto» no, y `/analyze` no podrá decir nada de ello.

## A quién

- **Porción del ICP:** [THE_SLICE — tamaño, sector, señal de compra que califica]
- **Excluidos:** [WHO_IS_LEFT_OUT_AND_WHY, or «nadie»]

## Ángulo

[ONE_OR_TWO_LINES: qué dice esta campaña que no dicen las otras de la misma unidad]

## Estado

| Dato | Valor |
|---|---|
| Prospectos asignados | [N] |
| Escritos | [N] |
| Respuestas | [N] |

Los prospectos de esta campaña son las filas de `../../prospects.csv` con `campaign` igual a
este slug. Al cerrarla, los que no convirtieron se liberan y vuelven al pozo; la supresión y el
historial de envíos son de la persona y no se tocan.
