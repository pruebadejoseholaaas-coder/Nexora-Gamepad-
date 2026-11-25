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

# Teclas pensadas para asignarse manualmente en PPSSPP.
KEYBOARD_BUTTONS = {
    "A": 0x4A, "B": 0x4B, "X": 0x55, "Y": 0x49,
    "UP": 0x26, "DOWN": 0x28, "LEFT": 0x25, "RIGHT": 0x27,
    "LB": 0x51, "RB": 0x45, "BACK": 0x08, "START": 0x0D,
    "LS": 0x43, "RS": 0x56,
}
KEYBOARD_AXES = {
    ("leftX", -1): 0x41, ("leftX", 1): 0x44,
    ("leftY", -1): 0x57, ("leftY", 1): 0x53,
    ("rightX", -1): 0x46, ("rightX", 1): 0x48,
    ("rightY", -1): 0x54, ("rightY", 1): 0x47,
}
KEYBOARD_TRIGGERS = {"leftTrigger": 0x31, "rightTrigger": 0x32}
KEYEVENTF_KEYUP = 0x0002


def keyboard_keys(buttons, axes):
    """Return the currently-held virtual keys for the optional PPSSPP mode."""
    keys = {KEYBOARD_BUTTONS[name] for name in buttons if name in KEYBOARD_BUTTONS}
    for (axis, direction), key in KEYBOARD_AXES.items():
        value = clamp(axes.get(axis, 0), -1, 1)
        if value * direction > 0.55:
            keys.add(key)
    for axis, key in KEYBOARD_TRIGGERS.items():
        if clamp(axes.get(axis, 0), 0, 1) > 0.5:
            keys.add(key)
    return keys


def apply_keyboard_state(current, previous):
    """Send only key transitions; Windows releases are also sent on disconnect."""
    import ctypes
    for key in previous - current:
        ctypes.windll.user32.keybd_event(key, 0, KEYEVENTF_KEYUP, 0)
    for key in current - previous:
        ctypes.windll.user32.keybd_event(key, 0, 0, 0)


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
    keyboard_mode = False
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
    if pad is None:
        try:
            answer = input("¿Activar modo teclado para PPSSPP? [s/N]: ").strip().lower()
            keyboard_mode = answer in ("s", "si", "sí", "y", "yes")
        except EOFError:
            keyboard_mode = False
        if keyboard_mode:
            print("Modo teclado activo. Usa PPSSPP en primer plano y configura sus teclas según windows/PPSSPP.md.")
        else:
            print("Modo diagnóstico: no se enviarán controles al PC.")

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
    previous_keyboard = set()
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
                    if previous_keyboard:
                        apply_keyboard_state(set(), previous_keyboard)
                        previous_keyboard.clear()
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
                if data.get("code") != pairing_code:
                    continue
                if paired_ip is None:
                    paired_ip = address[0]
                    print("\nTeléfono emparejado:", paired_ip)
                if address[0] != paired_ip:
                    continue
                send_json(sock, address, {"type": "hello_ack", "version": 1, "name": "Nexora Gamepad"})
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
            elif keyboard_mode:
                current_keyboard = keyboard_keys(buttons, axes)
                apply_keyboard_state(current_keyboard, previous_keyboard)
                previous_keyboard = current_keyboard
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
        if previous_keyboard:
            apply_keyboard_state(set(), previous_keyboard)
        sock.close()

if __name__ == "__main__":
    main()
