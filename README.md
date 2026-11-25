# Nexora Gamepad

Convierte un teléfono Android en un mando inalámbrico para Windows.

## Objetivo
- Conexión local por Wi-Fi, sin cuentas ni servicios en la nube.
- Controles táctiles configurables: botones, cruceta, sticks y gatillos.
- Perfiles para emuladores como PPSSPP.
- Vibración local al tocar controles.
- Objetivo de desarrollo: recibir también la vibración/rumble que produzca el juego en el PC y reproducirla en Android. Esta función requiere integración y pruebas específicas; no se considera implementada todavía.

## Componentes
- `android/`: aplicación Android.
- `windows/`: receptor para Windows y puente hacia un mando virtual.
- `protocol/`: protocolo de comunicación local.
- `.github/workflows/`: compilación automática.

## Estado
Proyecto inicial. Las compilaciones y funciones se irán habilitando y verificando por etapas.

## Privacidad
El diseño previsto es local: no necesita cuentas, analítica, anuncios ni servidores externos. La conexión se realiza dentro de la red local. Revisa el código antes de usarlo y no expongas el puerto del receptor a Internet.

## Compilar
Consulta las instrucciones de cada carpeta. Los archivos instalables se publicarán como artefactos de GitHub Actions cuando las compilaciones estén configuradas.

## Licencia
GPL-3.0-or-later. Consulta `LICENSE`.
