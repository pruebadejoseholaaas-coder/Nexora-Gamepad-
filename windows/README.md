# Receptor de Nexora Gamepad para Windows

## Qué hace
El receptor recibe por UDP los controles enviados por los teléfonos Android, combina hasta cuatro teléfonos y los presenta como un único mando compartido. Escucha en el puerto **26760**.

## Primera ejecución
1. Descarga `NexoraGamepad.exe` desde los artefactos de GitHub Actions o desde una versión publicada.
2. Ejecuta el archivo en Windows. La aplicación abre una ventana para iniciar y detener el receptor, elegir el modo de entrada y consultar el código de emparejamiento.
3. Elige **Automático** para intentar XInput, **Teclado** para usar PPSSPP o **Diagnóstico** para comprobar la conexión sin controlar un juego.
4. Si Windows Firewall pregunta, permite el acceso únicamente en redes privadas y de confianza.
5. Cuando el receptor esté iniciado, mostrará un código temporal de seis dígitos y las direcciones IPv4 disponibles.
6. En Android, introduce la IPv4 del adaptador de red que comparte conexión con el teléfono y el código mostrado en Windows.
7. Pulsa **Detener** en Nexora cuando termines.

## Modos de control
- **XInput:** se activa si `vgamepad` puede crear el mando virtual y hay un controlador virtual compatible instalado. No se instala ningún controlador automáticamente.
- **Teclado:** selecciona el modo teclado en la ventana antes de iniciar. Consulta [PPSSPP.md](PPSSPP.md) para ver las teclas y configurar PPSSPP.
- **Diagnóstico:** si no activas teclado y XInput no está disponible, el receptor recibe paquetes pero no envía controles al juego.

El backend actual usa `vgamepad`. Su funcionamiento depende de un controlador virtual compatible; ViGEmBus está archivado y no se distribuye con Nexora. El modo teclado es la alternativa que no necesita ese controlador.

## Conexión
- **Wi-Fi:** PC y teléfonos en la misma red local.
- **USB:** activa Anclaje USB en Android y usa en Windows la IPv4 del adaptador Ethernet/RNDIS.
- **Bluetooth:** activa Anclaje Bluetooth/PAN y usa la IPv4 del adaptador de red Bluetooth.

USB y Bluetooth PAN transportan tráfico de red; Nexora todavía no implementa USB HID ni Bluetooth HID/RFCOMM nativo.

## Seguridad
El código temporal dificulta conexiones casuales, los intentos incorrectos se limitan por IP y el receptor acota la memoria usada para registrar direcciones que fallan el emparejamiento. También valida y normaliza los ejes recibidos y descarta estructuras de entrada fuera de los límites. El protocolo UDP no cifra el tráfico. No compartas el código, no abras el puerto 26760 hacia Internet y evita redes públicas. Cierra el receptor al terminar.
