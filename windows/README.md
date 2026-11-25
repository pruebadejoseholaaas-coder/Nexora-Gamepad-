# Nexora Gamepad para Windows

Receptor UDP local y puente inicial hacia un mando virtual XInput.

## Requisitos
- Windows 10/11 de 64 bits.
- Una red Wi-Fi compartida con el teléfono.
- Controlador virtual ViGEmBus instalado desde su fuente oficial para que Windows pueda crear el mando XInput. No descargues controladores desde páginas de terceros.
- El firewall de Windows puede pedir permiso para la comunicación en redes privadas.

## Ejecutar desde código
1. Instala Python 3.11 o posterior.
2. Abre una consola en esta carpeta.
3. Ejecuta `python -m pip install -r requirements.txt`.
4. Ejecuta `python main.py`.
5. Permite la comunicación únicamente en redes privadas si Windows Firewall lo pregunta.
6. Escribe en Android la dirección IPv4 local de este PC.

## Estado actual
- Recibe controles por UDP en el puerto 26760.
- Mapea botones A/B/X/Y y cruceta a un mando virtual XInput cuando ViGEmBus está disponible.
- El código Android inicial envía botones; los sticks y gatillos se incorporarán a la interfaz en una siguiente etapa.
- La vibración de retorno del juego al teléfono todavía no está implementada. La vibración táctil local del teléfono es independiente.

No abras ni reenvíes el puerto del receptor hacia Internet. Úsalo solo en tu red local.
