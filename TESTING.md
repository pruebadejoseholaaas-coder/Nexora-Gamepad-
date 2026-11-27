# Primera prueba de Nexora Gamepad

Esta guía sirve para realizar una primera prueba controlada. Que GitHub Actions compile los archivos y supere las pruebas automáticas no sustituye la comprobación en un teléfono, una PC y un juego reales.

## 1. Descargar los dos programas

1. Abre la pestaña **Actions** del repositorio.
2. Entra en la ejecución más reciente que aparezca con resultado verde y que corresponda al código que quieres probar.
3. En **Artifacts**, descarga:
   - `Nexora-Gamepad-Android`: contiene el APK.
   - `Nexora-Gamepad-Windows`: contiene el EXE.
4. Extrae ambos ZIP. No necesitas instalar Python ni Android Studio.

## 2. Preparar Windows

1. Ejecuta `NexoraGamepad.exe`.
2. Para la primera prueba con PPSSPP, selecciona **Teclado (ideal para PPSSPP)**.
3. Pulsa **Iniciar receptor**.
4. Si Windows Firewall pregunta, permite la conexión solo en una red privada y de confianza.
5. Espera a que aparezcan el código de seis dígitos y las direcciones IPv4.
6. Conserva abierta la ventana de Nexora.

El modo Teclado no instala controladores y envía teclas a la ventana que esté en primer plano. El modo Automático intenta usar un mando virtual XInput si hay un controlador compatible instalado; Nexora no instala ese controlador por su cuenta.

## 3. Primera conexión por Wi-Fi

1. Conecta el teléfono y la PC a la misma red Wi-Fi.
2. Instala y abre el APK en Android.
3. En Nexora Android, selecciona **WI-FI**.
4. Escribe la IPv4 de Windows que corresponde a esa red Wi-Fi y el código de seis dígitos que aparece en la ventana de Windows.
5. Pulsa **CONECTAR** y espera el estado **CONECTADO**.
6. Abre PPSSPP en Windows y déjalo en primer plano.
7. Configura las teclas de PPSSPP según la tabla de [windows/PPSSPP.md](windows/PPSSPP.md).

Prueba primero A/B/X/Y, cruceta, L1/R1, Start/Select y después los sticks y gatillos. Mantén PPSSPP en primer plano durante el modo Teclado.

## 4. Comprobar desconexión y reconexión

1. Pulsa **DESCONECTAR** en Android.
2. Comprueba que el receptor deja de recibir controles.
3. Vuelve a conectar usando el mismo código mientras el receptor siga iniciado.
4. Pulsa **Detener** en Windows al terminar.

El receptor libera las teclas y botones al perder la conexión o cerrarse. Si el teléfono no conecta, comprueba primero la IPv4, el código, la red compartida y el permiso del Firewall para redes privadas.

## 5. Probar USB y Bluetooth por separado

Haz estas pruebas después de que Wi-Fi funcione. No son conexiones USB HID ni Bluetooth HID/RFCOMM: usan anclaje de red.

### USB

1. Conecta el teléfono a la PC con un cable que permita datos.
2. Activa **Anclaje USB** en los ajustes de Android.
3. En Windows, identifica la IPv4 del adaptador Ethernet/RNDIS creado por el teléfono.
4. En Android, selecciona **USB** e introduce esa IPv4 y el código de Nexora.
5. Pulsa **CONECTAR**.

### Bluetooth

1. Empareja el teléfono y la PC desde sus ajustes Bluetooth.
2. Activa **Anclaje Bluetooth** en Android y conecta Windows a la red PAN del teléfono.
3. Identifica la IPv4 del adaptador de red Bluetooth en Windows.
4. En Android, selecciona **BLUETOOTH** e introduce esa IPv4 y el código.
5. Pulsa **CONECTAR**.

Algunos Android no muestran la interfaz de anclaje en sus APIs de red. Nexora intenta usar la ruta de red del sistema como alternativa. Si no conecta, revisa el adaptador y la IPv4; el resultado depende también del fabricante y de la versión de Android.

## 6. Varias funciones y límites actuales

- Hasta cuatro teléfonos pueden emparejarse con el mismo receptor. Comparten un solo mando: los botones se combinan y los sticks se mezclan. No son cuatro mandos independientes.
- La vibración local del teléfono se puede activar o desactivar desde Android.
- La vibración de retorno desde el juego requiere modo XInput y un controlador virtual compatible que admita notificaciones de vibración. No funciona en modo Teclado ni Diagnóstico.
- Los perfiles y la asignación de botones se guardan localmente en Android.
- Wi-Fi, USB y Bluetooth PAN usan UDP local sin cifrado. Usa una red de confianza, no compartas el código y nunca expongas el puerto 26760 a Internet.

## 7. Qué anotar si algo falla

Indica el modo usado (Wi-Fi, USB o Bluetooth), el texto exacto del estado que muestra Android, si Windows muestra el teléfono emparejado y qué control estabas probando. No publiques tu código de emparejamiento ni direcciones IP públicas.
