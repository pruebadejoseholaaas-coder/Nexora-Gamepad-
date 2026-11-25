import json
import socket
import sys

PORT = 26760
HOST = "0.0.0.0"

try:
    import vgamepad as vg
    GAMEPAD_AVAILABLE = True
except Exception:
    vg = None
    GAMEPAD_AVAILABLE = False

BUTTONS = {
    "A": "XUSB_GAMEPAD_A",
    "B": "XUSB_GAMEPAD_B",
    "X": "XUSB_GAMEPAD_X",
    "Y": "XUSB_GAMEPAD_Y",
    "UP": "XUSB_GAMEPAD_DPAD_UP",
    "DOWN": "XUSB_GAMEPAD_DPAD_DOWN",
    "LEFT": "XUSB_GAMEPAD_DPAD_LEFT",
    "RIGHT": "XUSB_GAMEPAD_DPAD_RIGHT",
}

def main():
    pad = None
    if GAMEPAD_AVAILABLE:
        try:
            pad = vg.VX360Gamepad()
            print("Mando virtual XInput preparado.")
        except Exception as exc:
            print("No se pudo iniciar el mando virtual.")
            print("Comprueba que el controlador ViGEmBus esté instalado.")
            print(f"Detalle: {exc}")
    else:
        print("La biblioteca vgamepad no está disponible; modo de diagnóstico.")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"Nexora Gamepad escucha en el puerto UDP {PORT}.")
    print("Busca la IP local de este PC y escríbela en Android.")
    print("Pulsa Ctrl+C para cerrar.")

    previous = set()
    while True:
        raw, address = sock.recvfrom(4096)
        try:
            data = json.loads(raw.decode("utf-8"))
            if data.get("type") != "input" or data.get("version") != 1:
                continue
            buttons = set(data.get("buttons", []))
            axes = data.get("axes", {})
            if pad is not None:
                for name, enum_name in BUTTONS.items():
                    button = getattr(vg.XUSB_BUTTON, enum_name)
                    if name in buttons and name not in previous:
                        pad.press_button(button=button)
                    elif name not in buttons and name in previous:
                        pad.release_button(button=button)

                def axis(name):
                    try:
                        value = float(axes.get(name, 0.0))
                        return max(-1.0, min(1.0, value))
                    except (TypeError, ValueError):
                        return 0.0

                pad.left_joystick(
                    x_value=int(axis("leftX") * 32767),
                    y_value=int(-axis("leftY") * 32767),
                )
                pad.right_joystick(
                    x_value=int(axis("rightX") * 32767),
                    y_value=int(-axis("rightY") * 32767),
                )
                pad.left_trigger(value=int(max(0.0, min(1.0, axis("leftTrigger"))) * 255))
                pad.right_trigger(value=int(max(0.0, min(1.0, axis("rightTrigger"))) * 255))
                pad.update()
            previous = buttons
            print(f"Control recibido desde {address[0]}: {', '.join(sorted(buttons)) or 'sin botones'}", end="\r")
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nNexora Gamepad cerrado.")
        sys.exit(0)
