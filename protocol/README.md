# Protocolo Nexora Gamepad

Versión 1: UDP en red local, puerto 26760.

El transporte es independiente de la interfaz de red. Puede funcionar por Wi-Fi, por Ethernet/RNDIS creado mediante Anclaje USB o por Bluetooth PAN creado mediante Anclaje Bluetooth. El teléfono envía los paquetes a la IPv4 del PC en la interfaz correspondiente. Un mismo receptor admite hasta cuatro teléfonos emparejados con el mismo código; sus botones se unen y para cada eje se conserva el valor de mayor magnitud.

## Mensajes Android → Windows
- `hello`: solicita emparejamiento; incluye `code` de seis dígitos.
- `input`: estado completo de botones y ejes; incluye el mismo `code`.

## Mensajes Windows → Android
- `hello_ack`: confirma emparejamiento.
- `input_ack`: confirma que el receptor sigue procesando controles.
- `rumble`: solicita vibración del teléfono emparejado; incluye `code`, `strength` (0.0–1.0) y `durationMs` (1–500). Android acepta estos mensajes solo desde la IP del PC configurado, con el código de emparejamiento correcto, mientras está conectado. Respeta el ajuste de vibración y limita la frecuencia a un mensaje cada 100 ms.

## Entrada
El paquete `input` contiene `buttons`, `axes` y `code`. Sticks se normalizan entre -1 y 1; gatillos entre 0 y 1.

## Seguridad y límites
El código se transmite sin cifrado; es una barrera básica para redes locales de confianza, no autenticación criptográfica. No reenvíes el puerto hacia Internet.

USB y Bluetooth PAN son transportes de red compartida; el protocolo actual no implementa USB HID, Bluetooth HID ni Bluetooth RFCOMM nativo.

Los perfiles y el diseño Xbox/Nintendo se gestionan localmente en Android; el protocolo recibe los nombres de botones ya adaptados. Android ya puede recibir mensajes `rumble` autenticados de forma básica con el código de sesión, con intensidad y duración limitadas. La integración del evento de vibración del juego en Windows aún está pendiente; por tanto, esta recepción no significa que los juegos ya hagan vibrar el teléfono.