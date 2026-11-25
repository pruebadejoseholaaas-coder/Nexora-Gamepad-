# Nexora Gamepad para Windows

Receptor UDP local y puente de entrada a un mando virtual XInput.

## Requisitos
- Windows 10/11 de 64 bits.
- Teléfono y PC en la misma red Wi-Fi.
- Para ejecutar desde código: Python 3.11 o posterior.
- Para que los juegos detecten XInput se requiere un controlador virtual compatible con `vgamepad`. El backend tradicional de ViGEmBus está retirado y archivado; no vamos a incluir ni instalar ese controlador automáticamente. Si el mando virtual no está disponible, el receptor ofrece un modo alternativo de teclado para PPSSPP.

## Uso
1. Ejecuta `NexoraGamepad.exe` o `python main.py`.
2. El receptor muestra un código temporal de seis dígitos.
3. Si Windows Firewall pregunta, permite la comunicación solo en redes privadas.
4. Consulta la IPv4 del PC en Configuración > Red e Internet > Wi-Fi.
5. Introduce la IP y el código en Android y pulsa **CONECTAR**.

El primer teléfono que complete el emparejamiento queda autorizado hasta reiniciar el receptor. Para cambiar de teléfono, cierra y vuelve a iniciar el programa.

## Funciones
- Escucha UDP en el puerto 26760.
- Emparejamiento básico mediante código temporal.
- Mapeo de botones, cruceta, sticks y gatillos a XInput.
- Libera controles al perder el flujo de paquetes o cerrar el receptor.
- Modo alternativo de teclado para PPSSPP, activado expresamente al iniciar si no hay mando virtual.
- Modo diagnóstico si el usuario rechaza el modo teclado.

Consulta [PPSSPP.md](PPSSPP.md) para configurar las teclas. El modo teclado envía entradas a la ventana activa: mantén PPSSPP en primer plano.

## Seguridad
El código viaja sin cifrado y no sustituye autenticación criptográfica. Usa solo una red local de confianza, no compartas el código y no abras el puerto 26760 hacia Internet.
