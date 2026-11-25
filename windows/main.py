import json
import math
import secrets
import socket
import sys
import time

PORT = 26760
HOST = "0.0.0.0"
PACKET_TIMEOUT_SECONDS = 1.0
MAX_PACKET_BYTES = 4096

try:
    import vgamepad as vg
    GAMEPAD_AVAILABLE = True
except Exception:
    vg = None
    GAMEPAD_AVAILABLE = False

BUTTONS = {
    "A": "XUSB_GAMEPAD_A", "B": "XUSB_GAMEPAD_B",
    "X": "XUSB_GAMEPAD_X", "Y": "XUSB_GAMEPAD_Y",
    "UP": "XUSB_GAMEPAD_DPAD_UP", "DOWN": "XUSB_GAMEPAD_DPAD_DOWN",
    "LEFT": "XUSB_GAMEPAD_DPAD_LEFT", "RIGHT": "XUSB_GAMEPAD_DPAD_RIGHT",
    "LB": "XUSB_GAMEPAD_LEFT_SHOULDER", "RB": "XUSB_GAMEPAD_RIGHT_SHOULDER",
    "BACK": "XUSB_GAMEPAD_BACK", "START": "XUSB_GAMEPAD_START",
    "LS": "XUSB_GAMEPAD_LEFT_THUMB", "RS": "XUSB_GAMEPAD_RIGHT_THUMB",
}

def clamp(value, low, high):
    try:
        number = float(value)
        if not math.isfinite(number):
            return 0.0
        return max(low, min(high, number))
    except (TypeError, ValueError):
        return 0.0

def release_all(pad):
    if pad is None:
        return
    for enum_name in BUTTONS.values():
        try:
            pad.release_button(button=getattr(vg.XUSB_BUTTON, enum_name))
        except Exception:
            pass
    pad.left_joystick(x_value=0, y_value=0)
    pad.right_joystick(x_value=0, y_value=0)
    pad.left_trigger(value=0)
    pad.right_trigger(value=0)
    pad.update()

def parse_input(data):
    """Validate an input message and return normalized button/axis containers."""
    if not isinstance(data, dict) or data.get("version") != 1 or data.get("type") != "input":
        return None
    buttons_data = data.get("buttons", [])
    axes = data.get("axes", {})
    if not isinstance(buttons_data, list) or not isinstance(axes, dict):
        return None
    buttons = {name for name in buttons_data if isinstance(name, str) and name in BUTTONS}
    return buttons, axes

def send_json(sock, address, payload):
    try:
        sock.sendto(json.dumps(payload, separators=(",", ":")).encode("utf-8"), address)
    except OSError:
        pass

def main():
    pad = None
    if GAMEPAD_AVAILABLE:
        try:
            pad = vg.VX360Gamepad()
            print("Mando virtual XInput preparado.")
        except Exception as exc:
            print("No se pudo iniciar el mando virtual.")
            print("Revisa que exista un controlador virtual compatible.")
            print("Detalle:", exc)
    else:
        print("Biblioteca vgamepad no disponible: modo diagnóstico.")

    pairing_code = f"{secrets.randbelow(1000000):06d}"
    paired_ip = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(PACKET_TIMEOUT_SECONDS)
    sock.bind((HOST, PORT))
    print("Nexora Gamepad escucha en UDP", PORT)
    print("Código de emparejamiento (introdúcelo en Android):", pairing_code)
    print("El primer teléfono que use el código quedará emparejado hasta reiniciar el receptor.")
    print("Busca la IPv4 del PC en Configuración > Red e Internet > Wi-Fi.")
    print("Introduce esa IP en Android y pulsa CONECTAR.")
    print("Permite el acceso solo en redes privadas si Firewall lo solicita.")
    print("No expongas este puerto a Internet. Ctrl+C para salir.")

    previous = set()
    last_sender = None
    last_notice = 0.0
    try:
        while True:
            try:
                raw, address = sock.recvfrom(MAX_PACKET_BYTES)
            except socket.timeout:
                if previous or last_sender is not None:
                    release_all(pad)
                    previous.clear()
                    last_sender = None
                    print("\nTeléfono inactivo: controles liberados.")
                continue
            try:
                data = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if not isinstance(data, dict) or data.get("version") != 1:
                continue
            if data.get("type") == "hello":
                send_json(sock, address, {"type": "hello_ack", "version": 1, "name": "Nexora Gamepad"})
                if last_sender != address[0]:
                    print("\nTeléfono conectado:", address[0])
                last_sender = address[0]
                continue
            if address[0] != paired_ip or data.get("code") != pairing_code:
                continue
            parsed = parse_input(data)
            if parsed is None:
                continue
            buttons, axes = parsed
            if pad is not None:
                for name, enum_name in BUTTONS.items():
                    button = getattr(vg.XUSB_BUTTON, enum_name)
                    if name in buttons and name not in previous:
                        pad.press_button(button=button)
                    elif name not in buttons and name in previous:
                        pad.release_button(button=button)
                pad.left_joystick(x_value=int(clamp(axes.get("leftX",0),-1,1)*32767), y_value=int(-clamp(axes.get("leftY",0),-1,1)*32767))
                pad.right_joystick(x_value=int(clamp(axes.get("rightX",0),-1,1)*32767), y_value=int(-clamp(axes.get("rightY",0),-1,1)*32767))
                pad.left_trigger(value=int(clamp(axes.get("leftTrigger",0),0,1)*255))
                pad.right_trigger(value=int(clamp(axes.get("rightTrigger",0),0,1)*255))
                pad.update()
            previous = buttons
            last_sender = address[0]
            send_json(sock, address, {"type": "input_ack", "version": 1})
            now = time.monotonic()
            if now-last_notice > 2:
                print("Controles recibidos de", last_sender, "|", "XInput activo" if pad is not None else "modo diagnóstico")
                last_notice = now
    except KeyboardInterrupt:
        print("\nCerrando Nexora Gamepad...")
    finally:
        release_all(pad)
        sock.close()

if __name__ == "__main__":
    main()
