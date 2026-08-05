---
name: vmc-listing-copy
description: >
  Escribe y mejora la descripcion comercial de una oferta individual en el
  marketplace VMC Subastas (vmcsubastas.com/oferta/...) -- el texto que ve un
  comprador en la ficha de un vehiculo, maquinaria o activo antes de pujar.
  Cubre Vehicular (liviano/pesado, seminuevo y siniestrado/recuperado) con
  evidencia real de sitio; Materiales, Equipos Diversos y Articulos Diversos
  usan el mismo metodo con menos calibracion verificada. Distinto de
  patel-tone-converter (correos B2B de prospeccion) y copy-deck (copy de
  paginas del ecosistema) -- este es para fichas de producto/activo en
  subasta. Usalo cuando pidan "copy para esta oferta", "descripcion del auto
  en subasta", "ficha de vehiculo para VMC", "mejora esta publicacion de VMC
  Subastas", "texto para vmcsubastas.com/oferta/...", "copy comercial de VMC
  subasta", o peguen datos de un vehiculo/activo (marca, modelo, ano, km,
  condicion) pidiendo convertirlos en ficha de subasta.
---

# VMC Listing Copy -- Fichas de Oferta en Subasta

## Que hace este skill
Convierte los datos de un vehiculo, maquinaria o activo (ficha tecnica, notas de
condicion, o una publicacion ya existente que necesita mejorarse) en el texto
comercial de una oferta individual en vmcsubastas.com: el titulo, el cuerpo
descriptivo, y el ensamblaje correcto de las advertencias legales y el CTA que
corresponden a esa categoria y condicion.

No escribe la pagina completa. La estructura de la ficha (specs en tabla, botones
de "Negocia ahora" / "Adquirir ahora" / registro, documentos SUNARP descargables)
es una plantilla fija de la plataforma -- verificada contra una oferta real
(Buick Skylark 1969, oferta/62978). El trabajo de este skill es el texto libre:
el cuerpo descriptivo, mas la seleccion correcta del bloque legal fijo que le
corresponde. Tratar el titulo como creativo o inventar un CTA nuevo es sobre-alcance.

## Regla que no se negocia: los hechos y la condicion nunca se inventan ni se suavizan
Todo dato en el resultado -- marca, modelo, ano, kilometraje, motor, placa,
ubicacion, y sobre todo el ESTADO del activo -- tiene que venir de lo que el
usuario dio o de la publicacion original que se esta mejorando. Si falta un dato,
preguntalo -- no lo completes por plausibilidad.

Para activos siniestrados o recuperados esta regla es mas estricta, no menos:
la persona que puja va a pagar con un cheque no negociable por algo que se vende
"tal como esta y donde esta", sin garantia mecanica de la plataforma. Redactar el
dano como algo neutro, minimizarlo, o enterrarlo bajo entusiasmo sobre detalles
esteticos es el equivalente de un dato inventado -- es informacion que el
comprador necesita para pujar bien, y omitirla o suavizarla no es copywriting,
es el tipo de reclamo que la plataforma ya blinda contractualmente
("una vez recogido el vehiculo, cualquier reclamo es improcedente" -- confirma
que no hay vuelta atras despues de la puja). Si no tienes el detalle real del
dano, preguntalo antes de escribir "buen estado" o equivalente.

## Flujo de trabajo
### 1. Identifica que te dieron
- **Datos sueltos de un vehiculo/activo** (marca, modelo, ano, km, condicion,
  caracteristicas) sin publicacion previa -- modo generacion, ve al paso 2.
- **Una publicacion ya escrita** (texto plano o un link a vmcsubastas.com/oferta/...)
  que hay que mejorar -- modo conversion: extrae los hechos del original antes de
  tocar una palabra, igual que en generacion, y conserva el 100% de los datos.
- **Ni datos ni publicacion** -- pregunta. No hay ficha de subasta sin hechos reales
  detras.

### 2. Arma el cuerpo descriptivo
Estructura que se ve en fichas reales de la plataforma (ej. oferta/62978): abre
nombrando el atractivo central del activo en una linea, sigue con los elementos
originales/caracteristicas notables, luego los sistemas o componentes que
funcionan (odometro, luces, frenos, etc. si aplica a vehiculos; equivalente
funcional para maquinaria), y cierra sin inflar mas alla de lo verificado.

Ajusta el balance segun condicion:
- **Seminuevo / buen estado real:** el enfoque en caracteristicas originales y
  funcionales es honesto y es lo que ya hace la plataforma -- replicalo.
- **Siniestrado / recuperado:** el dano va primero o muy cerca del inicio, en
  terminos concretos (que se dano, que tan severo, que sigue funcionando) --
  no al final ni disuelto entre adjetivos positivos. Esto no es pesimismo, es
  la razon por la que alguien puja informado en vez de reclamar despues.

### 3. Ensambla el bloque legal fijo -- nunca lo reescribas
Lee `references/disclaimer-library.md` para los bloques verificados contra una
oferta real: pago con cheque de gerencia no negociable, gastos notariales a
cargo del comprador, venta "tal como esta y donde esta", responsabilidad del
comprador de verificar el estado antes de la transferencia, coordinacion de
recojo, papeletas/deudas pendientes a cargo del comprador. Selecciona el bloque
que corresponde a la categoria (vehicular liviano/pesado, materiales, equipos,
articulos) y a si es siniestrado o no -- e insertalo tal cual. Esto es texto
legal, no copy: parafrasearlo "para que suene mejor" es el unico lugar de este
skill donde mejorar el tono es un error, no una mejora.

### 4. Titulo
Sigue el patron verificado: "[Tipo de activo/modelo] [caracteristica clave]
[ano] en Peru | VMC Subastas" para vehiculos (ajusta el patron a la categoria
para no-vehiculos). Esto es SEO/metadata, no el lugar para una linea creativa --
no compitas aqui con el gancho que ya va en el cuerpo.

### 5. Entrega el resultado
```
--- TITULO ---
[titulo]

--- CUERPO ---
[descripcion]

--- BLOQUE LEGAL (categoria: [cual]) ---
[bloque seleccionado de references/disclaimer-library.md, sin editar]
```
Si convertiste una publicacion existente, muestra el original resumido en una
linea antes del resultado, igual que patel-tone-converter.

## Verificacion antes de entregar
1. Cada dato viene del usuario o del original -- nada completado por plausibilidad?
2. Si es siniestrado/recuperado: el dano esta descrito en terminos concretos y
   cerca del inicio, no minimizado ni al final?
3. El bloque legal es el bloque real de `references/disclaimer-library.md`, sin
   parafrasear?
4. El titulo sigue el patron SEO fijo en vez de intentar ser el gancho creativo?

## Edge Cases
- Categorias fuera de Vehicular (Materiales, Equipos Diversos, Articulos
  Diversos): el metodo del paso 2 transfiere, pero `references/disclaimer-library.md`
  solo esta verificado para Vehicular hoy -- confirma con el usuario o marca el
  bloque legal como "sin verificar para esta categoria" en vez de asumir que es
  igual.
- Sin condicion clara (el usuario no dice si es seminuevo o siniestrado):
  pregunta antes de elegir el balance del paso 2 -- no asumas seminuevo por
  default, ese es el sesgo que mas dano hace en este dominio.
