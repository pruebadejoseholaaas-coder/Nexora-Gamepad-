# Protocolo local

Versión 1: UDP sobre la red Wi-Fi local.

- Puerto del receptor: UDP 26760.
- El teléfono envía paquetes JSON de estado de controles.
- No se envían nombres, archivos, cuentas ni datos personales.
- El receptor debe utilizarse solo dentro de la LAN; no reenvíes el puerto hacia Internet.
- La vibración de retorno se definirá como mensaje independiente después de implementar y verificar la lectura de force feedback en Windows.

Ejemplo de paquete:

```json
{
  "type": "input",
  "version": 1,
  "buttons": ["A"],
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
