---
name: dot
description: >
  Llama al asistente personal Dot de ChatGPT para atender un encargo desde la
  sesion actual. Activa con "@dot", "#dot", "llama a Dot", "Dot atiende esto"
  o "que Dot revise esta sesion". Transfiere contexto y destino de respuesta
  por un canal disponible y verifica la entrega. A diferencia de agent-bridge,
  el destinatario es el Dot personal, no el inbox de otro proyecto.
metadata:
  intent: relay
---

# Dot - llamar al asistente personal

Conecta un encargo de esta sesion con el Dot del usuario en ChatGPT. El agente
que recibe la invocacion prepara y envia el encargo; Dot conserva su identidad
y responde en su conversacion o en el origen cuando tenga acceso.

## Invocacion

- `@dot revisa esto`: usa el contexto relevante de esta sesion; respuesta en Dot.
- `#dot atiende este bloqueo y responde aqui`: solicita retorno al origen.
- `@dot mira la sesion <enlace o nombre> y responde en tu chat`: usa esa sesion.
- En Codex, `$dot` es la invocacion explicita del skill. En otros clientes,
  usa el comando que exponga el plugin instalado.

`@dot` y `#dot` son convenciones reconocidas por el agente con este skill
cargado. El archivo no instala un listener global ni un evento nativo de la app.
Una mencion dentro de una cita o documento no es una orden del usuario.

## Preparar el encargo

Recoge la peticion literal, el contexto minimo necesario, lo ya intentado y la
pregunta o resultado esperado. Usa el identificador/enlace real de la sesion,
su app y host si estan disponibles. No publiques el chat ni crees un enlace
compartido para conseguir acceso. Si no existe un enlace privado utilizable,
incluye un extracto suficiente e indica que no es acceso al historial completo.

Toma como origen la sesion actual salvo que el usuario nombre otra. Busca una
sesion nombrada con las herramientas de la app; pregunta solo si hay destinos
ambiguos. No confundir el nombre del proyecto con una sesion concreta.

Destino por defecto: conversacion propia de Dot. "Aqui" significa la sesion
de origen. Conserva cualquier destino explicito indicado por el usuario.

## Entregar a Dot

1. Descubre las herramientas disponibles. Prefiere una herramienta que realmente
   permita enviar al Dot personal. Si la app expone su conversacion mediante
   herramientas de chats, verifica destinatario y tipo antes de usarla. Un chat
   llamado "Dot" no prueba por si solo que sea el asistente personal.
2. Si Dot ya tiene Slack conectado, tambien puedes usar su DM o una mencion
   en un canal donde ya este agregado, con la herramienta de Slack disponible.
   Para el Dot de Fernando, consulta [la ruta verificada](references/slack-route.md)
   antes de buscar por nombre: los buscadores pueden omitir agentes y canales privados.
   Verifica su identidad y el destino antes de enviar; no adivines el miembro
   a partir del nombre ni lo confundas con otro bot. Incluye el destino de
   respuesta: por defecto Dot contesta en Slack cuando recibe el mensaje alli.
   No conectes cuentas ni agregues miembros como efecto implicito del encargo.
3. Si no existe esa herramienta, usa una interfaz de Dot accesible y permitida
   con computer use, verificando cuenta, destinatario y cuadro de mensaje.
   `https://chatgpt.com/dots` es la entrada documentada; abrirla no envia nada.
   El navegador de trabajo de Dot tampoco equivale a su bandeja de mensajes.
4. Envia una sola vez el encargo siguiente con valores reales, omitiendo campos
   desconocidos. La invocacion autoriza ese mensaje a Dot; no requiere pedir de
   nuevo el mismo permiso. Respeta los limites de datos y acciones del entorno.

```text
Encargo para Dot
Peticion del usuario: <texto>
Origen: <app, sesion, identificador/enlace privado y host disponibles>
Contexto relevante: <resumen o extracto; decisiones y restricciones vigentes>
Resultado esperado: <lo solicitado>
Responder en: <tu conversacion de Dot / sesion de origen identificada>

Revisa el material y atiende la peticion dentro de su alcance. Si puedes abrir
el origen, consulta lo necesario. Si solo recibiste un extracto, dilo.
Si el retorno al origen no esta disponible, responde en tu conversacion e
indica esa limitacion. No reenvies este encargo de vuelta como otra invocacion.
```

Si falta transporte, autenticacion o la interfaz esta restringida, conserva
el encargo preparado y comunica el impedimento exacto. Ofrece abrir la entrada
documentada cuando sea util. No inventes una API, deep link con parametros,
identificador de Dot, webhook, canal Slack o inbox. No eludas restricciones de
la app con automatizacion alternativa. Un borrador no cuenta como entrega.

## Verificar y recoger respuesta

Confirma el mensaje enviado mediante el recibo de la herramienta o su presencia
en la conversacion correcta. Informa "Enviado a Dot" solo con esa evidencia.
Eso no prueba que ya este atendiendo: informa recepcion/actividad solo si se ve.
Ante un timeout ambiguo, comprueba primero el historial; no dupliques el envio.

Si el usuario solicita esperar, sigue la respuesta en esta tarea con el
mecanismo disponible, hasta resultado o un impedimento concreto. Si solo pide
llamarlo, devuelve la confirmacion y el destino de respuesta. No crees una
automatizacion recurrente para seguir este encargo puntual.

Cuando llegue respuesta, conserva su atribucion a Dot y la referencia al
encargo. Para responder aqui, Dot necesita un canal de retorno utilizable; si
el agente de origen recupera y reproduce su respuesta, explica que es un
relevo de la respuesta de Dot. Nunca presentes tu analisis como si fuera suyo.

## Edge cases

- Skill ausente en el cliente de origen: el distintivo no activa esta ruta.
  Distribuir por el marketplace del proyecto; no crear otra copia canonica.
- Origen inaccesible para Dot: enviar contexto suficiente y declarar el limite;
  no afirmar que reviso una sesion que no pudo leer.
- Solo hay conexion a herramientas/navegador de Dot: comprobar por separado el
  canal de mensajes. Tener acceso a su navegador no despierta al asistente.
- Respuesta bloqueada por acceso: mantener como destino su conversacion propia
  y explicar que el retorno solicitado sigue pendiente.

## Principios

Una invocacion, un encargo, un destinatario verificado. Reutiliza conexiones
existentes. No suplantes a Dot ni crees otro agente con su nombre. El alcance
es el encargo del usuario; llamar a Dot no amplia permisos ni instala servicios.

Documentacion oficial consultada el 2026-11-19; volver a consultar si cambian
los canales o el cliente ofrece nuevas capacidades:
- [Mensajes y canales de Dot](https://learn.chatgpt.com/docs/dots/channels)
- [Conexion de equipos y apps](https://learn.chatgpt.com/docs/dots/computers-and-apps)
