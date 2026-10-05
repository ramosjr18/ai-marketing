---
slug: [SLUG]
unit: [UNIDAD QUE SE BARAJA | sin decidir]
processes: [N]
updated: [YYYY-MM-DD]
status: [en curso | cerrado]
---

# [NOMBRE DEL CASO] — diagnóstico

Método de cuatro pasos (`offering/consultoria-ia/pricing.md`): medir frecuencia, duración,
personas y errores → coste real frente a ahorro → señales de fracaso → por dónde empezar.

**De uno a tres procesos.** Es lo que está vendido, y tres bien medidos valen más que siete
nombrados.

## Cómo leer los números

Cada cifra lleva pegada su procedencia. Sin eso no es un dato, es una suposición con suerte:

- `[dicho por <quién> el <YYYY-MM-DD>]` — salió de una fuente, y está en `fuentes.md`
- `[documento: F-N]` — de un fichero del material
- `[estimado — supuesto: <cuál>]` — lo pusimos nosotros, y la fila está en `preguntas.md`
- `[Inferred from <source> — review before relying on this]` — deducido, no dicho

## Contexto

[QUÉ HACE LA EMPRESA, CUÁNTA GENTE, DÓNDE DUELE. Tres líneas, con procedencia.]

---

## [P1] [NOMBRE DEL PROCESO]

**Qué es:** [EL TRABAJO, EN UNA FRASE, COMO LO DESCRIBEN ELLOS]
**Quién lo hace hoy:** [PERSONA O PAPEL] `[procedencia]`

### 1 · Medida

| | Valor | Procedencia |
|---|---|---|
| Frecuencia | [VECES POR SEMANA / MES] | `[…]` |
| Duración | [TIEMPO POR VEZ] | `[…]` |
| Personas | [CUÁNTAS LO TOCAN] | `[…]` |
| Errores | [CADA CUÁNTO SALE MAL Y QUÉ CUESTA ARREGLARLO] | `[…]` |

### 2 · Coste actual frente a ahorro

| | Cálculo | Resultado |
|---|---|---|
| Coste hoy | [FRECUENCIA × DURACIÓN × COSTE/HORA, ESCRITO] | [X €/mes] |
| Lo que quedaría | [QUÉ SIGUE SIENDO MANUAL Y POR QUÉ] | [Y €/mes] |
| Ahorro | [DIFERENCIA] | [Z €/mes] |

El coste por hora sale de [FUENTE]. Si es un supuesto, aquí se dice.

### 3 · Señales de fracaso

Lo que haría que esto no funcionara, dicho antes y no después:

- [SEÑAL: dato disperso, nadie dueño del proceso, volumen demasiado bajo, excepciones que son la norma…]

### 4 · Veredicto

**[COMPENSA | NO COMPENSA | NO SE PUEDE DECIR TODAVÍA]**

[POR QUÉ, EN DOS LÍNEAS. Si no se puede decir, qué falta — y esa falta es una fila de
`preguntas.md`.]

«No compensa» es una respuesta válida y es la que da valor al resto. Se escribe con el mismo
detalle que un sí.

---

## Por dónde empezar

| Orden | Proceso | Por qué este primero | Qué haría falta |
|---|---|---|---|
| 1 | [P-N] | [ESFUERZO BAJO Y AHORRO CLARO · DESBLOQUEA LOS OTROS · DUELE MÁS] | [LO QUE TENDRÍA QUE PASAR] |

## Lo que no tocaría

[LOS PROCESOS DONDE AUTOMATIZAR NO COMPENSA, Y POR QUÉ. Esta sección no se deja vacía por
quedar bien: si todo compensa, dilo y explica por qué.]

## Qué encajaría de lo que vendemos

Solo unidades con `for_sale: yes`. Nada en beta, nada en testing, nada en reestructuración.

| Proceso | Qué encaja | Por qué | Estado de venta |
|---|---|---|---|
| [P-N] | [UNIDAD] | [EN UNA LÍNEA] | [verificado en `unit.md`] |

## Huecos

[LO QUE NO SE PUDO MEDIR Y POR QUÉ. Cada uno con su fila en `preguntas.md`.]
