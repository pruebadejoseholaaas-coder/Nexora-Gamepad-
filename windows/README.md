# Receptor de Nexora Gamepad para Windows

## Qué hace
El receptor recibe por UDP los controles enviados por los teléfonos Android, combina hasta cuatro teléfonos y los presenta como un único mando compartido. Escucha en el puerto **26760**.

## Primera ejecución
1. Descarga y extrae `NexoraGamepad.exe` desde los artefactos de GitHub Actions o desde una versión publicada.
2. Ejecuta el archivo en Windows.
3. Si Windows Firewall pregunta, permite el acceso únicamente en redes privadas y de confianza.
4. El receptor mostrará un código temporal de seis dígitos y las direcciones IPv4 disponibles.
5. En Android, introduce la IPv4 del adaptador de red que comparte conexión con el teléfono y el código mostrado en Windows.
6. Mantén abierto el receptor mientras utilizas el mando.

## Modos de control
- **XInput:** se activa si `vgamepad` puede crear el mando virtual y hay un controlador virtual compatible instalado. No se instala ningún controlador automáticamente.
- **Teclado:** si XInput no está disponible, puedes activar el modo teclado cuando el receptor lo pregunte. Consulta [PPSSPP.md](PPSSPP.md) para ver las teclas y configurar PPSSPP.
- **Diagnóstico:** si no activas teclado y XInput no está disponible, el receptor recibe paquetes pero no envía controles al juego.

El backend actual usa `vgamepad`. Su funcionamiento depende de un controlador virtual compatible; ViGEmBus está archivado y no se distribuye con Nexora. El modo teclado es la alternativa que no necesita ese controlador.

## Conexión
- **Wi-Fi:** PC y teléfonos en la misma red local.
- **USB:** activa Anclaje USB en Android y usa en Windows la IPv4 del adaptador Ethernet/RNDIS.
- **Bluetooth:** activa Anclaje Bluetooth/PAN y usa la IPv4 del adaptador de red Bluetooth.

USB y Bluetooth PAN transportan tráfico de red; Nexora todavía no implementa USB HID ni Bluetooth HID/RFCOMM nativo.

## Seguridad
El código temporal dificulta conexiones casuales y los intentos incorrectos se limitan por IP. El protocolo UDP no cifra el tráfico. No compartas el código, no abras el puerto 26760 hacia Internet y evita redes públicas. Cierra el receptor al terminar.
