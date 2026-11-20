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

## Evidencia y limite del transporte

Primera entrega: `DOT-SKILL-20261119-01`, mensaje `1795132092.915349`,
[hilo](https://vmc-subastop.slack.com/archives/C0C5SE8PG6S/p1795132092915349).
Dot confirmo que la mencion activo a Sym. Sus retornos con
`send_message_to_thread` llegaron al agente de origen como `functionCallOutput`:
no se mostraron como una intervencion independiente de Sym para el usuario.
La afirmacion historica de "retorno visible comprobado" fue incorrecta.

En `DOT-SKILL-20261119-02` y `-03`, Sym devolvio el texto al agente de origen
desde su chat `6afc4cda-5f20-8191-a315-fcd7aa6d90e1`. Son IDs historicos,
no destinos para nuevos encargos. Continuar el chat de trabajo anterior
`6afcab13-3100-8191-95e0-403039f6901e` fallo con `thread not found`, aunque
se podia leer. Contactar al Dot real por su mencion Slack verificada.

## Contrato vigente: original completo visible en origen

Fernando autorizo que el agente receptor presente aqui la respuesta original
integra de Sym, con su autoria y sin resumirla. No se exige una intervencion
nativa de Sym como participante independiente: esa via no quedo disponible.

Enviar app, ID/enlace privado y host del origen, peticion humana y canal de
retorno al agente. Preferir el mensaje interno dirigido a esa sesion cuando
este disponible; si no, recuperar la respuesta original del hilo del encargo
en Slack. El usuario no tiene que ir a Slack ni copiar mensajes. Ninguna de
esas entregas cierra el encargo hasta que el agente publique el texto completo
bajo "Respuesta de Sym" en el mensaje visible de la sesion de origen.

Conservar autor, texto completo y referencia al encargo; paginar si hace
falta. Los comentarios del agente receptor van fuera y separados. Nunca
sustituir el original por "Sym confirmo que..." ni por un enlace a Slack.
No reutilizar un hilo historico para encargos nuevos sin relacion.
