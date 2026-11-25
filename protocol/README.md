# Protocolo Nexora Gamepad

Versión 1: UDP dentro de la red local, puerto 26760.

## Mensajes Android → Windows
- `hello`: solicita emparejamiento; incluye `code` de seis dígitos.
- `input`: estado completo de botones y ejes; incluye el mismo `code`.

## Mensajes Windows → Android
- `hello_ack`: confirma emparejamiento.
- `input_ack`: confirma que el receptor sigue procesando controles.

## Entrada
El paquete `input` contiene:
- `buttons`: botones activos.
- `axes`: sticks normalizados entre -1 y 1; gatillos entre 0 y 1.
- `code`: código temporal de emparejamiento.

Ejemplo:

```json
{
  "type": "input",
  "version": 1,
  "code": "123456",
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
El receptor genera un código aleatorio temporal y autoriza la primera IP que lo presenta hasta reiniciar el servidor. El código se transmite sin cifrado; es una barrera básica para redes locales de confianza, no autenticación criptográfica. No reenvíes el puerto hacia Internet.

La vibración de retorno y los perfiles configurables todavía no forman parte de este protocolo.
