# Nexora Gamepad para Windows

Receptor UDP local y puente de entrada hacia un mando virtual XInput.

## Requisitos
- Windows 10/11 de 64 bits.
- PC y teléfono conectados a la misma red Wi-Fi.
- Python 3.11 o posterior para ejecutar desde código.
- Para exponer un mando XInput a los juegos se necesita un controlador virtual compatible con la biblioteca `vgamepad`. No instales controladores desde páginas de descargas no verificadas.

## Uso
1. Ejecuta `NexoraGamepad.exe` o `python main.py`.
2. Si Windows Firewall pregunta, permite la comunicación únicamente en redes privadas.
3. Consulta la IPv4 del PC en Configuración > Red e Internet > Wi-Fi.
4. Escribe esa IP en Android y pulsa **CONECTAR**.

## Funciones
- Escucha UDP en el puerto 26760.
- Confirma la conexión y responde a los paquetes de control.
- Traduce botones, cruceta, sticks y gatillos a XInput cuando el controlador virtual está disponible.
- Libera todos los controles al perder el flujo de paquetes o al cerrar el receptor.
- Puede iniciar en modo diagnóstico si el puente XInput no está disponible.

## Seguridad
No abras ni reenvíes el puerto UDP 26760 hacia Internet. Usa Nexora únicamente en una red local de confianza. El protocolo actual no incluye emparejamiento criptográfico.

## Limitaciones conocidas
La vibración de retorno desde el juego de Windows al teléfono todavía no está implementada. El soporte de mando virtual depende de la disponibilidad y compatibilidad del controlador requerido por `vgamepad`.
