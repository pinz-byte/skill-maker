# QA BARRIL — AVT.ai + CarMatch.ai
> Fecha: 2026-06-10 · Fuente: pase QA manual de POPs en iPhone (17:23–17:44)
> Builds: AVT.ai v3.0 · 0c81fd5 · 2026-06-09 18:48 UTC — CarMatch.ai v3.0 · 5ed5869 · 2026-06-10 19:20 UTC
> Vehículo de prueba: Ford Bronco Sport 2022 · 33,000 km · placa BZR 671

---

## LECTURA ESTRUCTURAL (antes de los hallazgos)

El pase descubrió un corte E2E, no solo bugs de UI. El flujo
vendedor (AVT) → publicación → comprador (CarMatch/MAX) → match → chat
está roto en el eslabón publicación→deck. Todo lo transaccional río abajo
quedó SIN VERIFICAR.

**Verificación que decide todo (hacer PRIMERO):**
¿Existe la publicación del Bronco (BZR 671) en la base de CarMatch?
- SÍ existe → bug de indexación/caché del deck (y probablemente el mismo
  bug explica el Raptor vendido que reaparece: snapshot stale en ambas
  direcciones).
- NO existe → publicación fantasma: el flujo "Publicando en CarMatch..."
  termina sin persistir, y los hallazgos F7/F8/F9b/F10 son un solo bug.

---

## HALLAZGOS

### P0 — Bloqueantes / integridad transaccional

**F10 · BLOCKER E2E — sin match no hay test** (CarMatch)
El Bronco recién publicado no aparece en el deck de MAX pese a cumplir la
intención declarada ("camioneta Ford 4x4 automática"). Sin él no se puede
generar match → chat comprador-vendedor, ofertas, panel Mensajes del
garage y notificaciones quedan sin probar. Corta el QA del lado
transaccional completo.

**F9a · Vehículo VENDIDO reaparece en el deck** (CarMatch)
Ranger Raptor 2025 figura VENDIDO en AVT Mi Garage y aun así se sirve
como candidato activo en MAX. Un vendido jamás entra al deck. Integridad
del inventario comprometida — espejo invertido de F10 (muestra lo que ya
salió, omite lo que acaba de entrar → huele a índice/caché con lag).

**F7+F8 · Publicación sin confirmación ni cambio de estado** (AVT)
- Loader "Publicando en CarMatch..." genérico, sin brand.
- Al completar: cero mensaje de éxito. Falta "Tu vehículo ha sido
  publicado con éxito en CarMatch" (reusar patrón verde toast+card de
  "Guardado en tu garage") + link al listing.
- El detalle post-publicación sigue diciendo "Listo para publicar ✓" —
  falta estado "Publicado en CarMatch" con badge y acceso al listing.
El usuario no tiene NINGUNA evidencia de que la publicación ocurrió. Si
la verificación inicial da "NO existe", esto es la cara visible del bug
de persistencia.

### P1 — Lógica core degradada

**F1 · Regresión de prellenado inteligente en Mecánica** (AVT, Valuar)
Se dejó de pre-marcar defaults inferidos por marca/modelo/año. Esperado:
Bronco Sport 2022 → Automática + 4x4 (+ Gasolina). Hoy solo Automática
aparece marcada; tracción y combustible vacíos. Debe cubrir TODAS las
marcas y modelos. Verificar en código si "Automática" marcada es resto de
la lógica (degradada) o selección manual (lógica eliminada) — cambia el
diagnóstico.

**F4 · Comparables inconsistentes entre pantallas** (AVT)
La cantidad de vehículos similares en el detalle guardado ≠ pantalla de
valuación para el mismo vehículo. Determinar: ¿snapshot congelado al
guardar vs query live, o filtros distintos por pantalla? El fix depende
de cuál sea.
- Sub-hallazgo 4a: "Rango: Datos insuficientes" con 5 comparables
  listados debajo — contradictorio.
- Sub-hallazgo 4b: comparables muestran coordenadas crudas
  (-13.2987,-72.1378) en vez de ciudad — dato sin formatear.

**F5 · "Recalcular ahora" muerto** (AVT, Más detalles)
Tap sin efecto: ni recálculo, ni loading, ni error. Distinguir:
(a) handler roto, (b) recálculo corre sin feedback y devuelve igual valor,
(c) error silencioso de endpoint. Si es (b), el fix incluye loading +
confirmación visible aunque el valor no cambie.

### P2 — UX / copy

**F3 · CTA duplicado en detalle de vehículo** (AVT)
"Completa el perfil para publicar" aparece 2 veces en la misma vista.
Eliminar el primero, conservar el segundo slot, copy → "Publica en
CarMatch". Decisión pendiente: comportamiento con perfil incompleto
(deshabilitado con hint del gate campos/fotos, o copy intermedio) — si
no, prometemos publicación que el flujo bloquea después.

**F6 · Campo "Precio de venta recomendado" → "Expectativa de venta"** (AVT, sheet publicar)
1. Renombrar a "Expectativa de venta".
2. Peso 1 (⚠️ ambigüedad a confirmar: ¿peso máximo en el motor de
   valuación, o prioridad/orden del campo en el form?).
3. Al editar el precio, feedback en vivo vs valor de mercado
   (US$33,500 vs US$31,790 → "+5.4% sobre mercado"), reusando el patrón
   "% vs AVT" de los comparables.

### P3 — Visual

**F2 · Tag VENDIDO ilegible sobre foto** (AVT, Mi Garage)
El badge verde superior-izquierdo se pierde contra fotos claras/verdes
(confirmado en Raptor y Challenger). Garantizar contraste independiente
de la foto: fondo sólido opaco con padding, scrim detrás, o sacarlo de la
imagen. Nota: ya existe pill "Vendido" abajo-derecha — decidir si el tag
sobre foto se refuerza o se elimina por redundante.

**Colateral CarMatch · Relevancia del matching**
Con intención "Ford", MAX sirvió VW Amarok 2015 / 117k km como
"A considerar". Revisar scoring de relevancia en el mismo pase del deck.

---

## ORDEN DE EJECUCIÓN SUGERIDO

1. **Diagnóstico único:** ¿el Bronco existe en la base de CarMatch?
   (decide si F7/F8/F9/F10 son 1 bug o 2)
2. Fix pipeline publicación→deck + exclusión de vendidos (F10, F9a)
3. Estados de publicación: éxito + badge + link (F7, F8)
4. Re-test E2E: publicar → deck → match → chat (desbloquea el QA cortado)
5. Prellenado Mecánica (F1)
6. Comparables: consistencia + rango + ciudades (F4)
7. Recalcular (F5)
8. CTA + copy CarMatch (F3), Expectativa de venta (F6)
9. Tag VENDIDO (F2) + relevancia matching

## AMBIGÜEDADES A RESOLVER ANTES DEL BUILDER PROMPT

1. F6: significado exacto de "peso 1".
2. F1: ¿"Automática" pre-marcada era prellenado parcial o tap manual?
3. F3: comportamiento del CTA "Publica en CarMatch" con perfil < 100%.
4. F8: confirmar interpretación de "avt publis closed" (sheet se cerró
   sin reflejar estado publicado).
