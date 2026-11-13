# Validacion de astrological-thinker

Fecha: 2026-11-12, America/Lima.

**Dictamen: apto para uso asistido como thinker astrologico de AD / Amorata en el alcance probado.** Diez casos sinteticos resueltos; ocho evaluados a ciegas por un tercer agente y dos pruebas de dominio revisadas por el agente principal. No aparecio un fallo que justificara cambiar la skill.

## Resultados

| Caso | Capacidad observada | Resultado con skill |
| --- | --- | --- |
| C1 | Diferencia Venus Aries casa 5 de Venus Libra casa 11 e integra Marte como dispositor solo donde corresponde | Cumple |
| C2 | Reconoce limites sin hora natal ni efemerides; ofrece un siguiente paso | Cumple |
| C3 | Detecta Virgo 15 / Piscis 15 como oposicion de 180 grados y devuelve el error al motor | Cumple |
| C4 | Distingue clima compartido de contacto natal y elimina la acusacion de ocultamiento | Cumple |
| C5 | Conserva t7, la ventana semiabierta y referencias; no introduce t8; entrega lectura de 91 palabras | Cumple |
| C6 | Interpreta casa 7 vacia mediante Tauro -> Venus en Geminis casa 8 | Cumple |
| C7 | Distingue Tecnica determinista, interpretacion, politica editorial y prueba de despliegue | Cumple |
| C8 | Diferencia configuracion natal, transito y escalas anual/diaria | Cumple |
| C9 | Detecta que Sol Aries / Mercurio Libra / Venus Virgo no pueden coexistir en una carta natal geocentrica real | Cumple |
| C10 | Reconoce Venus -> Marte -> Saturno -> Venus como circuito cerrado sin dispositor final unico | Cumple |

## Comparacion con el asistente sin skill

El juez recibio las respuestas como A y B sin conocer su origen. A era el asistente general; B, el que cargo la skill y su referencia. En los ocho casos iniciales, B logro **24/24 criterios** y A **23.5/24**. Los dos resolvieron tambien las dos pruebas adicionales.

La diferencia de medio punto corresponde a distinguir explicitamente la clasificacion tecnica de Venus en Aries de la politica editorial ante clientes. La respuesta con skill tambien explicito mejor el contexto interno de AD / Amorata y, en C1, la dependencia por regencia. El juez advierte correctamente que no podia verificar esos detalles internos porque no recibio los contratos del proyecto; su presencia coincide con las fuentes resumidas en la referencia de la skill.

**La prueba muestra que sirve, pero no demuestra una mejora general importante frente al modelo sin skill.** El conocimiento astrologico general ya estaba presente. Su aportacion observable es orientar ese conocimiento hacia los contratos y las separaciones de AD / Amorata.

## Evidencia reproducible

- `cases.json`: ocho consultas iniciales, identicas para ambas condiciones.
- `rubric.json`: 24 criterios fijados antes de recibir respuestas.
- `with-skill.json` y `baseline.json`: respuestas completas de agentes separados.
- `blind-review.md` y `blind-scores.json`: juicio ciego por criterio.
- `domain-cases.json`, `domain-with-skill.json`, `domain-baseline.json`: dos consultas adicionales; revisadas por el agente principal, no incluidas en los 24 puntos.
- `geometry-check.json`: comprobacion aritmetica independiente de C3.
- `run-metadata.json`: metodo, correspondencia A/B y hashes de los archivos de la skill probados.

Referencia externa para dignidades: [Astrodienst, Domicile](https://www.astro.com/astrowiki/en/Domicile). Para el fundamento astronomico de la cercania aparente de planetas interiores al Sol: [University of Nebraska-Lincoln, Elongation](https://astro.unl.edu/naap/ssm/elongation.html). La separacion de 180 grados en C3 se comprobo aritmeticamente con los datos del caso, sin usar efemerides.

## Limites practicos

Una sola respuesta por condicion, con el mismo modelo heredado. Casos construidos para evaluar las capacidades declaradas; varios incluyen instrucciones que tambien ayudan al asistente general. El juez es otro agente del mismo entorno, no un astrologo humano externo. No es un estudio estadistico ni demuestra rendimiento igual con otros modelos.

No se probaron calculos del motor real, precision contra efemerides, lecturas completas de usuarios, satisfaccion editorial humana ni activacion automatica en una sesion consumidora nueva. Las salidas comprueban razonamiento dentro del marco astrologico; no validan cientificamente sus interpretaciones.

Puede usarse ya para consultas, explicaciones y revision asistida de material. La calidad de una carta completa destinada al cliente requiere comprobar sus hechos y revisar su interpretacion como producto completo. No se publico ni se activo ningun pipeline durante esta validacion.
