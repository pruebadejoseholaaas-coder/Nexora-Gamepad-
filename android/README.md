# Nexora Gamepad para Android

Aplicación Android horizontal para controlar un mando virtual en Windows.

## Controles
- Stick izquierdo y derecho analógicos.
- Cruceta y botones A/B/X/Y.
- L1/R1, L2/R2, L3/R3, Start y Select.
- Vibración háptica local con interruptor.

## Conexión
1. Ejecuta Nexora Gamepad en Windows.
2. Comprueba que ambos dispositivos estén en la misma red Wi-Fi.
3. Introduce en Android la dirección IPv4 local del PC.
4. Pulsa **CONECTAR** y espera el indicador verde.

La app utiliza UDP en el puerto 26760 y confirma la conexión mediante mensajes de respuesta. Si el PC deja de responder, la app muestra el estado de reconexión.

## Compatibilidad
Android 8.0 o posterior. La interfaz y el protocolo están en desarrollo; deben probarse en dispositivos reales antes de considerarse estables.

La vibración incluida es la respuesta háptica local al tocar los controles. La vibración de retorno generada por el juego en Windows todavía no está implementada.
