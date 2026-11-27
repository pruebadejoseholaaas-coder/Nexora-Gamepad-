# Nexora Gamepad

Versión de desarrollo: **0.6.0**.

Convierte uno o varios teléfonos Android en un mando táctil para Windows mediante una conexión de red local.

## Funciones implementadas
- Controles Android horizontales: A/B/X/Y, cruceta, dos sticks, L1/R1, L2/R2, L3/R3, Start y Select.
- Vibración háptica local configurable y recepción de vibración de retorno desde juegos cuando el backend XInput de Windows admite notificaciones.
- Perfiles Android: General, PPSSPP, Acción y Personal, con sensibilidad, zona muerta, diseño Xbox/Nintendo y asignación de botones guardados por separado.
- Editor visual para reasignar 14 controles digitales: A/B/X/Y, cruceta, L1/R1, Select/Start y pulsaciones L3/R3; permite asignaciones repetidas y guarda los cambios por perfil.
- Conexión UDP local con emparejamiento, confirmación, reconexión y detección de pérdida de respuesta.
- Código temporal de emparejamiento de seis dígitos generado por Windows y limitación de intentos incorrectos por IP.
- Aplicación de escritorio para Windows con interfaz gráfica: iniciar/detener, elegir modo XInput automático/teclado/diagnóstico y consultar el código de emparejamiento y las direcciones IP. El cierre ordenado libera los controles.
- Receptor Windows con salida XInput opcional (requiere un controlador virtual compatible instalado) y liberación automática de controles.
- Conexión por Wi-Fi, anclaje USB o Bluetooth PAN.
- Hasta cuatro teléfonos conectados al mismo receptor, compartiendo un mando virtual: los botones se combinan y cada eje usa el movimiento de mayor intensidad.
- Modo teclado opcional para PPSSPP cuando no hay controlador virtual, sin instalar drivers adicionales.
- Compilaciones APK y EXE y pruebas automáticas en GitHub Actions.

## Componentes
- `android/`: aplicación Android.
- `windows/`: receptor Windows ([guía de instalación y uso](windows/README.md)).
- `protocol/`: protocolo local.
- `.github/workflows/`: compilaciones y pruebas.

## Pendiente antes de considerarla terminada
- Integrar y validar un backend XInput moderno opcional. HIDMaestro tiene licencia MIT, pero su instalación implica componentes de controlador y requiere revisar la experiencia de permisos, instalación y desinstalación antes de adoptarlo.
- Validar la interfaz gráfica de Windows y el cierre ordenado en equipos reales.
- Validar la conexión real en Wi-Fi, USB tethering y Bluetooth PAN en distintos equipos.
- Validar controles, reconexión y vibración con teléfonos y juegos reales.

## Seguridad y privacidad
No necesita cuenta, anuncios ni nube. El receptor genera un código temporal de seis dígitos. Hasta cuatro teléfonos pueden emparejarse con el mismo código durante la sesión; cada conexión se identifica por IP y puerto, y se elimina de forma independiente cuando deja de enviar datos y supera el tiempo de espera. Los intentos incorrectos de código se limitan por IP. El código se envía por UDP sin cifrado: es una protección básica para redes domésticas, no seguridad criptográfica. Usa una red de confianza, no compartas el código y no expongas el puerto UDP 26760 a Internet. Autoriza el firewall solo en redes privadas.

## Estado
Versión de desarrollo. La compilación automatizada y las pruebas de código no sustituyen las pruebas reales en teléfono, PC y juegos.

## Licencia
GPL-3.0-or-later. Consulta `LICENSE`.
