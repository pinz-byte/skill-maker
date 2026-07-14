---
name: patel-tone-converter
description: >
  Convierte correos y mensajes ya escritos (para ejecutivos, generacion de leads, ventas B2B)
  al tono persuasivo y la estructura de conversion aprendida de la metodologia de email
  marketing de Neil Patel / NP Digital  -  nunca copiando su texto, solo su metodo (gancho de
  contraste, ritmo skimmable, urgencia dosificada, P.D. como segunda oferta). Pensado en
  primer lugar para las iniciativas de VMC Subastas / Echo Chamber (correos a ejecutivos y
  leads de subastas), pero usable para reescribir cualquier mensaje de venta o prospeccion
  que necesite mas gancho y menos tono corporativo plano. Usalo siempre que el usuario pida
  "convierte este correo", "dale el tono de Neil Patel", "reescribe esto con mas gancho",
  "hazlo mas vendedor", "esto suena muy plano, mejoralo", "aplica la metodologia de Patel a
  este mensaje", "correo para ejecutivos", "mensaje de prospeccion/lead-gen", o pegue un
  borrador de email/mensaje pidiendo que se mejore  -  incluso si no menciona a Neil Patel
  explicitamente.
---
# Conversor de Tono  -  Metodologia Patel
## Que hace este skill
Su trabajo principal es CONVERTIR: toma un correo, mensaje o borrador que el usuario ya
escribio (o los hechos sueltos de una oferta/propuesta) y lo reescribe aplicando la
estructura y el tono persuasivo que se audito de 212 correos reales de Neil Patel / NP
Digital  -  sin copiar ni una frase de su texto real, solo el metodo.

Piensa en esto como un tone-transfer, no como un generador desde cero: el valor esta en
tomar contenido plano, corporativo o desordenado que ya existe (una propuesta de venta, un
correo de prospeccion a un ejecutivo, un mensaje de seguimiento de lead) y reestructurarlo
para que enganche, se lea en skim, y cierre con una oferta clara  -  conservando el 100% de
los hechos, la oferta y los datos originales.

**Regla que no se negocia:** conviertes tono y estructura, nunca inventas hechos. Todo dato,
cifra, nombre de cliente, oferta o fecha que aparezca en el resultado debe venir del
borrador o brief original del usuario. Si el borrador original es ambiguo o le faltan datos
clave (a quien va dirigido, cual es la oferta exacta, hay una fecha limite real), preguntalo
en vez de inventarlo  -  un mensaje persuasivo con un dato falso es peor que uno sin convertir.

**Segunda regla que no se negocia (validada en produccion, VMC Subastas  -  2026-07-03):**
"mas estructura Patel" no es el objetivo  -  "mas humano" lo es. En el primer test real de
este skill, la conversion aplico el metodo de forma naive a un borrador que ya era bueno
(gancho de contraste natural, frases cortas, CTA directo) y el resultado fue RECHAZADO por
el cliente final con el motivo exacto: "son palabras y construcciones AI en lugar de
humanas." El error fue anadir pulido que el original no necesitaba: partir en lineas
demasiado uniformes, agregar un P.D. de segunda oferta donde no habia uno, convertir la
antitesis natural del original en una formula. Si el borrador original YA suena a un
operador humano escribiendo rapido  -  ritmo irregular, sin cortesia corporativa que
eliminar, sin estructura que arreglar  -  la conversion correcta puede ser casi nula. No
agregues estructura NP por reflejo. Ver "Voz de operador humano" en el paso 4.

## Flujo de trabajo
### 1. Identifica que te dieron
- **Si el usuario pego un correo/mensaje ya escrito**  este es el modo principal:
	conversion. Ve al paso 2.
- **Si el usuario solo dio hechos sueltos** (oferta, audiencia, objetivo, sin un borrador
	previo)  modo generacion. Usa los mismos patrones de `references/patterns.md` pero
	construyelo desde cero con esos hechos.
- **Si el usuario no dio nada de contenido real** (ni borrador ni hechos)  pregunta antes
	de escribir. No inventes la oferta, el producto o la audiencia.

### 2. Modo conversion  -  extrae antes de reescribir
Antes de tocar una palabra, separa el borrador original en:
- **Hechos y oferta** (lo que NO puede cambiar: precio, producto, nombre, fecha, cifra).
- **Objetivo** (busca una respuesta, una llamada agendada, un registro, cerrar una venta?).
- **Audiencia** (a quien le habla?  -  para VMC Subastas / Echo Chamber, normalmente
	ejecutivos y leads de un proceso de subasta; ver `references/executive_audience.md` para
	como calibrar el registro cuando la audiencia es ejecutiva).

Todo lo demas (estructura de parrafos, gancho de apertura, orden de las ideas, longitud,
CTA, P.D.) se reescribe libremente segun el patron que mejor calce.

### 3. Elige el patron que mejor sirve al objetivo del mensaje original
No fuerces un patron que no calce  -  lee `references/patterns.md` para la anatomia completa
de los 9 y elige segun lo que el mensaje original ya intentaba lograr:

| Si el mensaje original busca... | Conviertelo al patron |
|---|---|
| Presentar una idea/propuesta y generar interes | A  -  Pregunta Incomoda |
| Invitar a una reunion, demo o evento | B  -  Invitacion a Webinar |
| Cerrar algo con fecha limite real | C  -  Urgencia de Cierre |
| Anunciar un hito o relanzamiento | D  -  Historia de Origen |
| Comentar una novedad del sector para abrir conversacion | E  -  Cambio de Paradigma |
| Anunciar una oferta/promocion concreta | F  -  Regalo con Mecanica Clara |
| Usar un resultado o caso real como prueba | G  -  Prueba con Caso y Estadistica |
| Dar seguimiento periodico sin vender directo | H  -  Resumen Mensual de Industria |
| Reactivar un lead frio sin urgencia falsa | I  -  Manejo de Objecion Social |

Muchos correos de prospeccion ejecutiva y lead-gen calzan naturalmente en A (abrir con una
tension/pregunta incomoda), G (si hay un resultado real que mostrar) o I (si es seguimiento
a un lead que ya conoce la propuesta y no ha respondido).

### 4. Aplica las micro-reglas al reescribir
- **Gancho de contraste** ("la mayoria de [audiencia ejecutiva] asume X  -  no es asi") en vez
	de la apertura corporativa tipica ("Espero que este correo le encuentre bien...").
	Elimina cualquier apertura de cortesia generica del original  -  no aporta nada y es lo
	primero que un ejecutivo salta al leer en skim.
- **Frases de una sola idea**, parrafos de 1-2 lineas. Si el borrador original tiene parrafos
	largos y densos (tipico de correos corporativos), esa es la conversion mas importante que
	vas a hacer.
- **El P.D. es una segunda oferta**, no un resumen. Si el borrador original termina con un
	cierre plano ("Quedo atento a sus comentarios"), reemplazalo por un CTA claro + un P.D. que
	ofrezca algo distinto (una reformulacion mas directa, una alternativa de bajo compromiso).
- **Saludo con nombre solo si hay urgencia real** (patron C)  -  en el resto, abre directo con
	el gancho. Si el original abre con "Estimado [nombre]," y no es un correo de cierre con
	fecha limite, quitalo y empieza con el gancho.
- **Urgencia necesita una fecha/hora real.** Si quieres convertir el cierre a un patron C
	pero el original no da una fecha limite real, no la inventes  -  conserva un cierre sin
	urgencia artificial (patron A o I) o pregunta si existe una fecha real que no se menciono.
- **Un asunto que entrega lo que promete**  -  ver formulas en `references/patterns.md`.

### 4b. Voz de operador humano  -  el filtro final, siempre
Antes de entregar, lee el resultado en voz alta y preguntate: esto suena a un operador
real escribiendo rapido, o a una plantilla de marketing bien portada? Si suena a plantilla,
sobreconvertiste. Reglas concretas:
- **Ritmo irregular, no uniforme.** Frases de largo desigual  -  algunas de 4 palabras, otras
	de 20  -  es lo humano. Partir todo en lineas de 1-2 ideas parejas es el tic mas delatador
	de "esto lo escribio una IA aplicando una formula".
- **Cero trios y cero antitesis de manual.** "No es X: es Y" funciona UNA vez si ya estaba
	en el original o surge natural  -  convertirlo en un recurso que se repite entre correos de
	la misma secuencia (FLOTA, GG, CFO todos con su propio "no es X: es Y") es exactamente el
	patron que se detecta como IA. Si tres correos de la misma secuencia comparten la misma
	arquitectura retorica, reescribe al menos dos para que diverjan.
- **Cero P.S./P.D. por reflejo.** El P.D. como "segunda oferta de menor friccion" es una
	tecnica valida DEL CORPUS DE NEWSLETTER (one-to-many), no una regla universal para
	outreach ejecutivo 1:1. Si el original no tenia cierre adicional y el mensaje ya cierra
	bien sin el, no le agregues uno  -  un P.D. anadido donde no hacia falta es puro "andamiaje
	de embudo" y se nota.
- **CTA como pregunta humana, no como boton.** "Te armo el numero con tu flota?" es
	operador real. "[RESERVA TU LUGAR AHORA ]" o cualquier CTA en mayusculas/corchetes es
	marketing-mode  -  evitalo salvo que el canal literalmente sea un email HTML con boton real
	y el usuario lo haya pedido asi.
- **Si el borrador original ya es bueno, la conversion correcta puede ser minima.** No hay
	obligacion de tocar cada linea. Menos pulido, no mas, es la direccion por defecto para
	outreach ejecutivo 1:1  -  reserva la reestructuracion pesada (patron completo, P.D.,
	reordenamiento) para borradores que de verdad llegan planos o corporativos.

### 5. Si la audiencia es ejecutiva (VMC Subastas / Echo Chamber u otro contexto B2B)
Lee `references/executive_audience.md` antes de reescribir  -  calibra registro, longitud y
nivel de formalidad para una audiencia ejecutiva sin perder el gancho de contraste que hace
funcionar el metodo. Ejecutivos leen menos tiempo, no mas formalidad  -  la formalidad
corporativa plana es precisamente lo que el metodo de Patel reemplaza.

### 6. Entrega el resultado
Muestra siempre AMBAS versiones cuando conviertas un mensaje existente, en este orden:
```
--- ORIGINAL (resumen de 1 linea de que intentaba lograr) ---

--- CONVERTIDO (patron usado: [letra y nombre]) ---

ASUNTO: [linea de asunto]

[Cuerpo reescrito]

[Cierre]

P.D. [si aplica al patron elegido]
```

Si conviertes varios mensajes de una secuencia, procesalos uno por uno y senala si el orden
o el angulo de alguno deberia cambiar para que la secuencia completa siga el arco de
cadencia de `references/patterns.md` (educa  refuerza con prueba  cierra con urgencia
real, del mas largo al mas corto).

## Verificacion antes de entregar
1. Cada dato/cifra/nombre/fecha en la version convertida viene del original o del brief del
	usuario? Si inventaste algo para "sonar mejor", quitalo y pregunta.
2. Alguna frase se parece sospechosamente a una linea real de Neil Patel/NP Digital?
	Reescribela  -  el objetivo es el metodo, no su copy.
3. El asunto entrega lo que promete el cuerpo?
4. El tono ejecutivo se mantiene (ver `references/executive_audience.md`) sin volver a caer
	en la cortesia corporativa plana que estabas reemplazando?
