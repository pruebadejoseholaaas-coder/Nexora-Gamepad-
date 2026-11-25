# Nexora Gamepad

Convierte un teléfono Android en un mando táctil para Windows mediante la red Wi-Fi local.

## Funciones implementadas en esta etapa
- Interfaz Android horizontal con botones A/B/X/Y, cruceta, L1/R1, L2/R2, Start, Select y pulsación de sticks.
- Dos sticks analógicos táctiles.
- Vibración háptica local activable o desactivable.
- Conexión UDP con saludo y confirmación del receptor.
- Señal de respuesta periódica para detectar cuando el PC deja de responder.
- Receptor Windows con mapeo inicial a un mando virtual XInput.
- Liberación de controles cuando se pierde el envío del teléfono o se cierra el receptor.
- Compilación automática de APK y EXE mediante GitHub Actions.

## Componentes
- `android/`: aplicación Android.
- `windows/`: receptor Windows.
- `protocol/`: protocolo local.
- `.github/workflows/`: compilaciones.

## Pendiente de completar y verificar
- Perfiles guardables y editor visual de asignación de botones.
- Vibración de retorno desde el juego del PC al teléfono.
- Emparejamiento autenticado y endurecimiento adicional de la comunicación local.
- Pruebas reales con distintos juegos y emuladores, incluido PPSSPP.
- Verificación de compatibilidad del controlador virtual en el equipo de destino.

## Privacidad y seguridad
No requiere cuenta, anuncios ni servicios en la nube. La comunicación se limita a la red local. No abras ni reenvíes el puerto UDP 26760 hacia Internet. Permite el acceso en el firewall solo para redes privadas. El protocolo actual todavía no incorpora emparejamiento criptográfico, por lo que debe usarse únicamente en una red local de confianza.

## Estado
Versión de desarrollo. Que GitHub Actions compile correctamente no sustituye las pruebas de funcionamiento en un teléfono y un PC reales.

## Licencia
GPL-3.0-or-later. Consulta `LICENSE`.
