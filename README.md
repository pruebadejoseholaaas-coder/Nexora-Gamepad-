# Nexora Gamepad

Versión de desarrollo: **0.5.0**.

Convierte uno o varios teléfonos Android en un mando táctil para Windows mediante una conexión de red local.

## Funciones en desarrollo
- Controles Android horizontales: A/B/X/Y, cruceta, dos sticks, L1/R1, L2/R2, L3/R3, Start y Select.
- Vibración háptica local configurable.
- Ajustes guardados de sensibilidad y zona muerta de los sticks, independientes por perfil.
- Perfiles Android: General, PPSSPP, Acción y Personal, con sensibilidad, zona muerta, diseño Xbox/Nintendo y asignación de botones guardados por separado.
- Conexión UDP local con emparejamiento, confirmación, reconexión y detección de pérdida de respuesta.
- Código de emparejamiento de seis dígitos generado por Windows.
- Receptor Windows con salida XInput opcional (requiere un controlador virtual compatible ya instalado) y liberación automática de controles.
- Conexión por Wi-Fi, anclaje USB o Bluetooth PAN.
- Hasta cuatro teléfonos conectados al mismo receptor, compartiendo un mando virtual: los botones se combinan y cada eje usa el movimiento de mayor intensidad.
- Modo teclado opcional para PPSSPP cuando no hay controlador virtual, sin instalar drivers adicionales.
- Compilaciones APK y EXE en GitHub Actions.

## Componentes
- `android/`: aplicación Android.
- `windows/`: receptor Windows.
- `protocol/`: protocolo local.
- `.github/workflows/`: compilaciones y pruebas.

## Pendiente
- Editor visual para reasignar cada botón a una tecla o acción configurable por juego.
- Reenvío de vibración del juego desde Windows a los teléfonos emparejados cuando el backend XInput instalado admite notificaciones de vibración (compilado y cubierto por pruebas; falta validación física).
- Un backend de mando virtual para Windows que no dependa de ViGEmBus, cuyo proyecto original está archivado.
- Pruebas adicionales de interoperabilidad entre Wi-Fi, USB tethering y Bluetooth PAN.
- Pruebas reales en hardware.

## Seguridad y privacidad
No necesita cuenta, anuncios ni nube. El receptor genera un código temporal de seis dígitos. Hasta cuatro direcciones IP pueden emparejarse con el mismo código durante la sesión; se eliminan automáticamente cuando dejan de enviar datos y superan el tiempo de espera. El código se envía por UDP sin cifrado: es una protección básica para redes domésticas, no seguridad criptográfica. Usa una red Wi-Fi de confianza, no compartas el código y no expongas el puerto UDP 26760 a Internet. Autoriza el firewall solo en redes privadas.

## Estado
Versión de desarrollo. La compilación automatizada no sustituye pruebas reales en teléfono y PC.

## Licencia
GPL-3.0-or-later. Consulta `LICENSE`.
