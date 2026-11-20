# Dot de Fernando - ruta Slack

Identidad confirmada por Fernando y comprobada con perfil e historial el
2026-11-19. Es una ruta personal del ecosistema LFP, no un valor por defecto
para cuentas de otros usuarios.

- Workspace: subasteam, ID `T2UQXN92S`, dominio `vmc-subastop.slack.com`.
- Dot actual: nombre real `lfp-sym`, username `lfpsymdot2`, user ID `U0C76BP2YCR`.
- Canal autorizado para pruebas: `bots-room`, ID `C0C5SE8PG6S` (privado).
- Mencion real: `<@U0C76BP2YCR>`.
- `lfp-symdot`, ID `U0C5A0U8FC7`, es una identidad anterior que salio del canal;
  no sustituirla por el Dot actual.

Antes de enviar, consulta el perfil por ID y verifica acceso al canal. La
busqueda por `dot`, `lfp-sym` y `bots-room` devolvio cero resultados aunque
el perfil y el canal eran accesibles por ID. No interpretar esos ceros como
ausencia ni pedir al usuario que vuelva a conectar una cuenta existente.

Primera entrega verificada: `DOT-SKILL-20261119-01`, mensaje
`1795132092.915349`, [hilo](https://vmc-subastop.slack.com/archives/C0C5SE8PG6S/p1795132092915349).
Dot respondio a las 18:48:36 America/Lima, mensaje `1795132116.929169`:
"Recibido: esta mencion si activo a Sym". Queda verificada la activacion por
mencion en este canal. Despues, Sym devolvio el cierre directamente al chat
de origen mediante `send_message_to_thread`, desde su chat
`6afcab13-3100-8191-95e0-403039f6901e`: informo que abrio este chat en M2 y
leyo el skill canonico, SHA-256
`7d70e3992e07d7fe7e912502879172041753d946e176e13c2380b14ace77b3f3`.
El agente de origen cotejo esa huella con su archivo local. Queda probado
el retorno en esta sesion; no acredita acceso universal a cualquier sesion
ni a Claude Code. Revalidar capacidades y autorizacion en cada origen.
No reutilizar ese hilo para encargos nuevos sin relacion.

## Retorno directo obligatorio

Slack es solo transporte de la invocacion. La respuesta de Sym debe llegar
a la sesion donde el usuario lo llamo; no cerrar en Slack ni transcribir el
resultado como sustituto. Enviar siempre app, ID/enlace privado, host e
instruccion humana que Sym pueda verificar leyendo el historial de origen.

En `DOT-SKILL-20261119-02`, el primer intento de retorno fallo antes de
aplicarse. Tras leer la correccion humana en origen, Sym envio el cierre
directamente desde `6afc4cda-5f20-8191-a315-fcd7aa6d90e1` al chat de origen
`01a1f629-560d-7a90-b73f-9b624c2a6447`, host `local`, y se recibio alli.
Son IDs de esa prueba, no destinos para encargos nuevos. La lectura de un
chat de trabajo no garantiza que se pueda continuar con send_message_to_thread:
el chat anterior `6afcab13-3100-8191-95e0-403039f6901e` devolvio
`thread not found` al intentar continuarlo. Usar la ruta Slack para contactar
al Dot real y el ID del origen actual para que el cierre vuelva alli.
