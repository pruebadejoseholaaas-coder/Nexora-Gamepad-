# Nexora Gamepad

Convierte un teléfono Android en un mando táctil para Windows mediante la red Wi-Fi local.

## Funciones en desarrollo
- Controles Android horizontales: A/B/X/Y, cruceta, dos sticks, L1/R1, L2/R2, L3/R3, Start y Select.
- Vibración háptica local configurable.
- Ajustes guardados de sensibilidad y zona muerta de los sticks.
- Conexión UDP con saludo, confirmación y detección de pérdida de respuesta.
- Código de emparejamiento de seis dígitos generado por Windows.
- Receptor Windows con mapeo a XInput y liberación automática de controles.
- Conexión por Wi-Fi, anclaje USB o Bluetooth PAN.
- Hasta cuatro teléfonos conectados al mismo receptor, compartiendo un mando virtual.
- Modo teclado opcional para PPSSPP cuando no hay controlador virtual.
- Compilaciones APK y EXE en GitHub Actions.

## Componentes
- `android/`: aplicación Android.
- `windows/`: receptor Windows.
- `protocol/`: protocolo local.
- `.github/workflows/`: compilaciones y pruebas.

## Pendiente
- Perfiles configurables dentro de Android y asignación visual de botones para otros juegos.
- Vibración de retorno desde el juego de Windows al teléfono.
- Mejoras adicionales al protocolo y pruebas de interoperabilidad.
- Pruebas reales en hardware.

## Seguridad y privacidad
No necesita cuenta, anuncios ni nube. El receptor genera un código temporal de seis dígitos. El primer teléfono que lo presenta queda emparejado hasta reiniciar el receptor. El código se envía por UDP sin cifrado: es una protección básica para redes domésticas, no seguridad criptográfica. Usa una red Wi-Fi de confianza, no compartas el código y no expongas el puerto UDP 26760 a Internet. Autoriza el firewall solo en redes privadas.

## Estado
Versión de desarrollo. La compilación automatizada no sustituye pruebas reales en teléfono y PC.

## Licencia
GPL-3.0-or-later. Consulta `LICENSE`.
