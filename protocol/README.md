# Protocolo Nexora Gamepad

Versión 1: UDP en red local, puerto 26760.

El transporte es independiente de la interfaz de red. Puede funcionar por Wi-Fi, por Ethernet/RNDIS creado mediante Anclaje USB o por Bluetooth PAN creado mediante Anclaje Bluetooth. El teléfono envía los paquetes a la IPv4 del PC en la interfaz correspondiente.

## Mensajes Android → Windows
- `hello`: solicita emparejamiento; incluye `code` de seis dígitos.
- `input`: estado completo de botones y ejes; incluye el mismo `code`.

## Mensajes Windows → Android
- `hello_ack`: confirma emparejamiento.
- `input_ack`: confirma que el receptor sigue procesando controles.

## Entrada
El paquete `input` contiene `buttons`, `axes` y `code`. Sticks se normalizan entre -1 y 1; gatillos entre 0 y 1.

## Seguridad y límites
El código se transmite sin cifrado; es una barrera básica para redes locales de confianza, no autenticación criptográfica. No reenvíes el puerto hacia Internet.

USB y Bluetooth PAN son transportes de red compartida; el protocolo actual no implementa USB HID, Bluetooth HID ni Bluetooth RFCOMM nativo.

La vibración de retorno y los perfiles configurables todavía no forman parte de este protocolo.