# Nexora Gamepad para Windows

Receptor UDP local y puente de entrada a un mando virtual XInput o teclado.

## Requisitos
- Windows 10/11 de 64 bits.
- Python 3.11 o posterior si se ejecuta desde código.
- PC y teléfono conectados mediante Wi-Fi, anclaje USB o anclaje Bluetooth PAN.
- Para que los juegos detecten un mando XInput se necesita un controlador virtual compatible con `vgamepad`. Instalar la biblioteca de Python no instala ese controlador.
- Nexora no descarga ni instala controladores de sistema. ViGEmBus está retirado y archivado; no se incluye ni se instala automáticamente.
- Si no hay un controlador virtual disponible, puedes usar el modo teclado opcional para PPSSPP.

## Uso
1. Ejecuta `NexoraGamepad.exe` o `python main.py`.
2. El receptor muestra un código temporal de seis dígitos. Puedes introducir el mismo código en hasta cuatro teléfonos.
3. Si Windows Firewall pregunta, permite la comunicación solo en redes privadas.
4. En el teléfono, selecciona Wi-Fi, USB o Bluetooth.
5. Introduce en Android la IPv4 del adaptador de Windows correspondiente a esa conexión y el código de seis dígitos.
6. Pulsa **CONECTAR**.

### Cómo encontrar la IP correcta
Abre CMD o PowerShell y ejecuta `ipconfig`.
- Wi-Fi: usa la IPv4 del adaptador Wi-Fi que comparte la red con el teléfono.
- USB: conecta el cable, activa Anclaje USB en Android y usa la IPv4 del adaptador Ethernet/RNDIS.
- Bluetooth: empareja los dispositivos, activa Anclaje Bluetooth en Android y conecta Windows a la red PAN; usa la IPv4 del adaptador Bluetooth.

El nombre exacto del adaptador depende del controlador y de Windows. No uses la IP pública ni la puerta de enlace; introduce la IPv4 asignada al propio PC en esa interfaz.

## Funciones
- UDP en el puerto 26760, escuchando en las interfaces locales.
- Código temporal de emparejamiento compartido por hasta cuatro teléfonos.
- Salida XInput únicamente si el PC ya dispone de un controlador virtual compatible con `vgamepad`.
- Modo teclado opcional para PPSSPP, sin instalar controladores adicionales.
- Liberación de controles al perder el flujo de paquetes.

## Seguridad
El código viaja sin cifrado y no sustituye autenticación criptográfica. Usa redes de confianza, permite el acceso solo en redes privadas y no abras ni reenvíes el puerto 26760 hacia Internet.