# Protocolo Nexora Gamepad

Versión 1: UDP dentro de la red local, puerto 26760.

## Mensajes Android → Windows
- `hello`: solicita conexión.
- `input`: estado completo de botones y ejes.

## Mensajes Windows → Android
- `hello_ack`: confirma el saludo inicial.
- `input_ack`: confirma que el receptor sigue procesando controles.

## Entrada
El paquete `input` contiene:
- `buttons`: nombres de botones activos.
- `axes`: valores normalizados entre -1 y 1 para sticks; los gatillos usan 0 a 1.

Ejemplo:

```json
{
  "type": "input",
  "version": 1,
  "buttons": ["A", "LB"],
  "axes": {
    "leftX": 0.0,
    "leftY": 0.0,
    "rightX": 0.0,
    "rightY": 0.0,
    "leftTrigger": 0.0,
    "rightTrigger": 0.0
  }
}
```

## Seguridad y límites
No envíes datos personales. El protocolo no tiene autenticación criptográfica todavía: úsalo solo en una red local de confianza y nunca reenvíes el puerto hacia Internet.

La vibración de retorno requerirá un canal de eventos independiente y soporte de lectura de force feedback en Windows; todavía no forma parte de esta versión.
