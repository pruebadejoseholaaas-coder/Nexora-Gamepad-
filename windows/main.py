import json
import math
import secrets
import socket
import subprocess
import sys
import threading
import time

PORT = 26760
HOST = "0.0.0.0"
PACKET_TIMEOUT_SECONDS = 1.0
MAX_PACKET_BYTES = 4096
MAX_CLIENTS = 4

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
    allowed_axes = {"leftX", "leftY", "rightX", "rightY", "leftTrigger", "rightTrigger"}
    axes = {name: value for name, value in axes.items() if name in allowed_axes}
    return buttons, axes


def expire_inactive_clients(client_seen, client_states, paired_ips, now, timeout=PACKET_TIMEOUT_SECONDS):
    """Remove stale phones and return their IPs so callers can refresh controls."""
    expired = [ip for ip, seen in client_seen.items() if now - seen > timeout]
    for ip in expired:
        client_seen.pop(ip, None)
        client_states.pop(ip, None)
        paired_ips.discard(ip)
    return expired


def merge_client_states(client_states):
    if not client_states:
        return set(), {}
    buttons = set().union(*(state[0] for state in client_states.values()))
    axes = {}
    axis_names = ("leftX", "leftY", "rightX", "rightY", "leftTrigger", "rightTrigger")
    for name in axis_names:
        values = [clamp(state[1].get(name, 0), -1 if "Trigger" not in name else 0, 1)
                  for state in client_states.values()]
        axes[name] = max(values, key=abs) if "Trigger" not in name else max(values, default=0)
    return buttons, axes


def apply_controls(pad, keyboard_mode, buttons, axes, previous, previous_keyboard):
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
        return current_keyboard
    return previous_keyboard


def show_network_addresses():
    """Show IPv4 addresses reported by Windows so the phone can target this PC."""
    try:
        result = subprocess.run(
            ["ipconfig"], capture_output=True, text=True, errors="replace",
            timeout=5, check=False
        )
        lines = result.stdout.splitlines()
        matches = []
        for index, line in enumerate(lines):
            if "IPv4" in line or "IPv4" in line.upper():
                adapter = ""
                for previous_line in reversed(lines[:index]):
                    candidate = previous_line.strip()
                    if candidate.endswith(":"):
                        adapter = candidate
                        break
                matches.append((adapter, line.strip()))
        if matches:
            print("\nDirecciones IPv4 detectadas en Windows:")
            for adapter, address_line in matches:
                if adapter:
                    print(" ", adapter)
                print("   ", address_line)
            print("Usa la IPv4 del adaptador por el que está conectado el teléfono.")
        else:
            print("\nNo se detectaron IPv4 automáticamente. Ejecuta ipconfig en Windows.")
    except (OSError, subprocess.SubprocessError):
        print("\nNo se pudo consultar ipconfig. Ejecuta ipconfig en Windows.")


def send_json(sock, address, payload):
    try:
        sock.sendto(json.dumps(payload, separators=(",", ":")).encode("utf-8"), address)
    except OSError:
        pass


def build_rumble_message(pairing_code, large_motor, small_motor, duration_ms=120):
    """Convert XInput motor values into a bounded Android haptics message."""
    large = clamp(large_motor, 0, 255)
    small = clamp(small_motor, 0, 255)
    strength = max(large, small) / 255.0
    duration = max(0, min(500, int(duration_ms)))
    return {
        "type": "rumble",
        "version": 1,
        "code": pairing_code,
        "strength": strength,
        "durationMs": duration,
    }


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
    paired_ips = set()
    client_states = {}
    client_seen = {}
    client_addresses = {}
    clients_lock = threading.Lock()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(PACKET_TIMEOUT_SECONDS)
    sock.bind((HOST, PORT))

    rumble_callback = None
    if pad is not None and hasattr(pad, "register_notification"):
        def on_game_rumble(client, target, large_motor, small_motor, led_number, user_data):
            message = build_rumble_message(pairing_code, large_motor, small_motor)
            if message["strength"] <= 0:
                return
            with clients_lock:
                destinations = list(client_addresses.values())
            for destination in destinations:
                send_json(sock, destination, message)

        try:
            pad.register_notification(callback_function=on_game_rumble)
            rumble_callback = on_game_rumble
            print("Vibración de juegos habilitada para teléfonos emparejados.")
        except Exception as exc:
            print("La retroalimentación de vibración no está disponible:", exc)

    print("Nexora Gamepad escucha en UDP", PORT)
    print("Código de emparejamiento (introdúcelo en Android):", pairing_code)
    print("Hasta cuatro teléfonos pueden usar el mismo código y quedar emparejados hasta reiniciar el receptor.")
    show_network_addresses()
    print("Introduce en Android la IPv4 del adaptador que comparte red con el teléfono.")
    print("Permite el acceso solo en redes privadas si Firewall lo solicita.")
    print("No expongas este puerto a Internet. Ctrl+C para salir.")

    previous = set()
    previous_keyboard = set()
    last_notice = 0.0
    try:
        while True:
            try:
                raw, address = sock.recvfrom(MAX_PACKET_BYTES)
            except socket.timeout:
                now = time.monotonic()
                expired = expire_inactive_clients(client_seen, client_states, paired_ips, now)
                if expired:
                    with clients_lock:
                        for ip in expired:
                            client_addresses.pop(ip, None)
                for ip in expired:
                    print("\nTeléfono desconectado:", ip)
                if expired:
                    buttons, axes = merge_client_states(client_states)
                    previous_keyboard = apply_controls(pad, keyboard_mode, buttons, axes, previous, previous_keyboard)
                    previous = buttons
                    if not client_states:
                        release_all(pad)
                        if previous_keyboard:
                            apply_keyboard_state(set(), previous_keyboard)
                            previous_keyboard.clear()
                        previous.clear()
                        print("\nTodos los teléfonos desconectados: controles liberados.")
                continue
            try:
                data = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if not isinstance(data, dict) or data.get("version") != 1:
                continue
            now = time.monotonic()
            expired = expire_inactive_clients(client_seen, client_states, paired_ips, now)
            if expired:
                with clients_lock:
                    for ip in expired:
                        client_addresses.pop(ip, None)
            for ip in expired:
                print("\nTeléfono desconectado:", ip)
            if expired:
                buttons, axes = merge_client_states(client_states)
                previous_keyboard = apply_controls(pad, keyboard_mode, buttons, axes, previous, previous_keyboard)
                previous = buttons
                if not client_states:
                    release_all(pad)
                    if previous_keyboard:
                        apply_keyboard_state(set(), previous_keyboard)
                        previous_keyboard.clear()
                    previous.clear()
                    print("\nTodos los teléfonos desconectados: controles liberados.")
            if data.get("type") == "hello":
                if data.get("code") != pairing_code:
                    continue
                if address[0] not in paired_ips:
                    if len(paired_ips) >= MAX_CLIENTS:
                        send_json(sock, address, {"type": "busy", "version": 1, "message": "Máximo de teléfonos conectados alcanzado"})
                        continue
                    paired_ips.add(address[0])
                    client_states[address[0]] = (set(), {}, time.monotonic())
                    print("\nTeléfono emparejado:", address[0], "|", len(paired_ips), "de", MAX_CLIENTS)
                client_seen[address[0]] = time.monotonic()
                with clients_lock:
                    client_addresses[address[0]] = address
                send_json(sock, address, {"type": "hello_ack", "version": 1, "name": "Nexora Gamepad"})
                continue
            if address[0] not in paired_ips or data.get("code") != pairing_code:
                continue
            parsed = parse_input(data)
            if parsed is None:
                continue
            buttons, axes = parsed
            now = time.monotonic()
            client_states[address[0]] = (buttons, axes, now)
            client_seen[address[0]] = now
            with clients_lock:
                client_addresses[address[0]] = address
            merged_buttons, merged_axes = merge_client_states(client_states)
            previous_keyboard = apply_controls(pad, keyboard_mode, merged_buttons, merged_axes, previous, previous_keyboard)
            previous = merged_buttons
            send_json(sock, address, {"type": "input_ack", "version": 1})
            now = time.monotonic()
            if now-last_notice > 2:
                print("Controles recibidos | teléfonos conectados:", len(paired_ips), "|", "XInput activo" if pad is not None else ("teclado PPSSPP activo" if keyboard_mode else "modo diagnóstico"))
                last_notice = now
    except KeyboardInterrupt:
        print("\nCerrando Nexora Gamepad...")
    finally:
        if rumble_callback is not None:
            try:
                pad.unregister_notification()
            except Exception:
                pass
        with clients_lock:
            client_addresses.clear()
        release_all(pad)
        if previous_keyboard:
            apply_keyboard_state(set(), previous_keyboard)
        sock.close()

if __name__ == "__main__":
    main()
