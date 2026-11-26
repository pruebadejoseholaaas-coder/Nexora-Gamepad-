# Nexora Gamepad para Android

App de mando en horizontal. Requiere Android 8.0 o posterior.

## Conexión por Wi-Fi, USB o Bluetooth

En la pantalla principal puedes elegir el tipo de conexión. El selector guarda tu preferencia y muestra los pasos; los paquetes de control usan el mismo protocolo UDP y Android los envía por la interfaz de red que corresponda a la IP del PC.

### Wi-Fi
1. Conecta el PC y el teléfono a la misma red Wi-Fi.
2. Introduce en Nexora la IPv4 del PC y el código de seis dígitos que muestra el receptor Windows.

### USB
1. Conecta el teléfono al PC con un cable USB que permita datos.
2. En Android, abre Ajustes > Punto de acceso/Compartir Internet y activa **Anclaje USB**.
3. En Windows, abre `ipconfig` y localiza la dirección IPv4 del adaptador de Ethernet/RNDIS creado por el teléfono.
4. Introduce esa IPv4 en Nexora, junto con el código del receptor.

### Bluetooth
1. Empareja el teléfono y el PC desde los ajustes Bluetooth de ambos.
2. En Android, activa **Anclaje Bluetooth** o **Compartir Internet por Bluetooth**.
3. En Windows, conéctate a la red PAN del teléfono si no se conecta automáticamente.
4. En Windows, abre `ipconfig` y localiza la IPv4 del adaptador de red Bluetooth.
5. Introduce esa IPv4 en Nexora y el código del receptor.

Los nombres de los menús pueden variar según la marca y la versión de Android. USB y Bluetooth PAN son conexiones de red; no son modos USB HID ni Bluetooth HID.

## Emparejamiento
El receptor Windows muestra un código temporal de seis dígitos. Introdúcelo en cada teléfono que quieras conectar. Se permiten hasta cuatro teléfonos por sesión y todos comparten el mismo mando del PC; los botones se combinan y los ejes se mezclan usando el valor de mayor magnitud.

## Controles y perfiles
- Botones A/B/X/Y, cruceta, hombros, gatillos y sticks.
- Perfiles locales: General, PPSSPP, Acción y Personal.
- Cada perfil guarda su propia sensibilidad, zona muerta y diseño de botones frontales.
- Puedes alternar entre diseño Xbox y Nintendo; cambian las asignaciones predeterminadas.
- El botón **MAPEAR** abre un editor visual para asignar A, B, X o Y a cada botón frontal. La configuración se guarda por perfil.
- Los perfiles se seleccionan manualmente; no detectan automáticamente el juego abierto en Windows.
- Vibración local configurable.
- Recepción preparada para vibración de retorno desde Windows: solo acepta mensajes del PC conectado con el código de sesión, duración máxima de 500 ms y límite de frecuencia. La emisión desde los juegos de Windows todavía está pendiente.
- Los ajustes se guardan en el teléfono.

## Privacidad
No necesita cuenta, nube ni servidores externos. Los datos de control se envían directamente al PC dentro de la conexión local elegida.