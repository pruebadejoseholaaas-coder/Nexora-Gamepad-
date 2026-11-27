"""Nexora Gamepad Windows desktop launcher.

The UI owns the receiver process and displays its pairing code and network log.
No account, cloud service, or telemetry is used.
"""
import os
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk


class NexoraLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexora Gamepad")
        self.root.geometry("760x570")
        self.root.minsize(650, 480)
        self.root.configure(bg="#111827")
        self.events = queue.Queue()
        self.process = None
        self.reader_thread = None

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#111827")
        style.configure("TLabel", background="#111827", foreground="#e5e7eb", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#ffffff")
        style.configure("Muted.TLabel", foreground="#9ca3af")
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("TRadiobutton", background="#111827", foreground="#e5e7eb")
        style.map("TRadiobutton", background=[("active", "#111827")], foreground=[("active", "#ffffff")])

        outer = ttk.Frame(root, padding=20)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="NEXORA GAMEPAD", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Convierte tu teléfono en un mando para juegos de PC.", style="Muted.TLabel").pack(anchor="w", pady=(2, 16))

        mode_frame = ttk.LabelFrame(outer, text="Modo de entrada", padding=10)
        mode_frame.pack(fill="x")
        self.mode = tk.StringVar(value="auto")
        ttk.Radiobutton(mode_frame, text="Automático (mando XInput si está disponible)", variable=self.mode, value="auto").pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="Teclado (ideal para PPSSPP)", variable=self.mode, value="keyboard").pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="Diagnóstico (solo recibir controles)", variable=self.mode, value="diagnostic").pack(anchor="w")

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=12)
        self.start_button = ttk.Button(actions, text="Iniciar receptor", command=self.start_receiver)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(actions, text="Detener", command=self.stop_receiver, state="disabled")
        self.stop_button.pack(side="left", padx=8)
        self.status = ttk.Label(actions, text="● DETENIDO", foreground="#fca5a5")
        self.status.pack(side="right")

        pairing = ttk.Frame(outer)
        pairing.pack(fill="x", pady=(2, 12))
        ttk.Label(pairing, text="CÓDIGO DE EMPAREJAMIENTO", style="Muted.TLabel").pack(anchor="w")
        self.code = tk.StringVar(value="------")
        code_row = ttk.Frame(pairing)
        code_row.pack(anchor="w")
        ttk.Label(code_row, textvariable=self.code, font=("Consolas", 27, "bold"), foreground="#60a5fa", background="#111827").pack(side="left")
        self.copy_button = ttk.Button(code_row, text="Copiar código", command=self.copy_code, state="disabled")
        self.copy_button.pack(side="left", padx=14)
        ttk.Label(pairing, text="Escribe este código y la IPv4 del PC en la aplicación Android.", style="Muted.TLabel").pack(anchor="w")

        ttk.Label(outer, text="Actividad y direcciones de red").pack(anchor="w")
        log_frame = ttk.Frame(outer)
        log_frame.pack(fill="both", expand=True, pady=(6, 0))
        self.log = tk.Text(log_frame, height=12, bg="#030712", fg="#d1d5db", insertbackground="#ffffff",
                           relief="flat", wrap="word", font=("Consolas", 9), state="disabled")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(outer, text="Conexión local directa. No usa cuentas, nube ni telemetría.", style="Muted.TLabel").pack(anchor="w", pady=(10, 0))
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self.process_events)

    def append_log(self, line):
        self.log.configure(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")
        if "Código de emparejamiento" in line:
            code = line.rsplit(":", 1)[-1].strip()
            if len(code) == 6 and code.isdigit():
                self.code.set(code)
                self.copy_button.configure(state="normal")

    def copy_code(self):
        code = self.code.get()
        if len(code) == 6 and code.isdigit():
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            self.append_log("Código de emparejamiento copiado al portapapeles.")

    def receiver_command(self):
        mode = self.mode.get()
        if getattr(sys, "frozen", False):
            base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
            receiver = os.path.join(base, "NexoraReceiver.exe")
            return [receiver, "--mode", mode]
        receiver_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
        return [sys.executable, receiver_script, "--mode", mode]

    def start_receiver(self):
        if self.process is not None and self.process.poll() is None:
            return
        command = self.receiver_command()
        if not os.path.isfile(command[0]):
            self.append_log("No se encontró el receptor. Revisa que el paquete esté completo.")
            return
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        # Keep Spanish status/log messages readable through the Windows pipe.
        env["PYTHONIOENCODING"] = "utf-8"
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            self.process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                creationflags=creationflags, env=env
            )
        except OSError as exc:
            self.append_log("No se pudo iniciar el receptor: " + str(exc))
            self.process = None
            return
        self.code.set("------")
        self.copy_button.configure(state="disabled")
        self.status.configure(text="● INICIANDO", foreground="#fcd34d")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.append_log("Iniciando receptor en modo: " + self.mode.get())
        self.reader_thread = threading.Thread(target=self.read_output, args=(self.process,), daemon=True)
        self.reader_thread.start()

    def read_output(self, process):
        try:
            if process.stdout is not None:
                for line in process.stdout:
                    self.events.put(("line", line.rstrip()))
        finally:
            code = process.wait()
            self.events.put(("exit", (process, code)))

    def stop_receiver(self):
        process = self.process
        if process is None or process.poll() is not None:
            return
        self.status.configure(text="● CERRANDO", foreground="#fcd34d")
        self.stop_button.configure(state="disabled")
        threading.Thread(target=self.terminate_process, args=(process,), daemon=True).start()

    def terminate_process(self, process):
        try:
            if process.stdin is not None:
                process.stdin.write("quit\n")
                process.stdin.flush()
                process.stdin.close()
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        except (OSError, BrokenPipeError):
            try:
                process.kill()
            except OSError:
                pass

    def process_events(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "line":
                    self.append_log(payload)
                    if "Nexora Gamepad escucha" in payload:
                        self.status.configure(text="● ESCUCHANDO", foreground="#86efac")
                elif kind == "exit":
                    process, code = payload
                    if process is self.process:
                        self.process = None
                        self.start_button.configure(state="normal")
                        self.stop_button.configure(state="disabled")
                        self.status.configure(text="● DETENIDO", foreground="#fca5a5")
                        self.code.set("------")
                        self.copy_button.configure(state="disabled")
                    self.append_log("Receptor finalizado (código " + str(code) + ").")
        except queue.Empty:
            pass
        self.root.after(100, self.process_events)

    def close(self):
        process = self.process
        if process is not None and process.poll() is None:
            try:
                if process.stdin is not None:
                    process.stdin.write("quit\n")
                    process.stdin.flush()
                    process.stdin.close()
                process.wait(timeout=3)
            except Exception:
                try:
                    process.kill()
                except OSError:
                    pass
        self.root.destroy()


def packaged_self_test(receiver):
    """Exercise the packaged GUI runtime and the bundled receiver lifecycle."""
    try:
        test_root = tk.Tk()
        test_root.withdraw()
        test_root.update_idletasks()
        test_root.destroy()
    except Exception as exc:
        raise SystemExit("No se pudo iniciar Tcl/Tk: " + str(exc))

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        process = subprocess.Popen(
            [receiver, "--mode", "diagnostic"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=creationflags,
            env=env,
        )
    except OSError as exc:
        raise SystemExit("No se pudo iniciar el receptor empaquetado: " + str(exc))

    output = queue.Queue()

    def collect_output():
        if process.stdout is not None:
            for line in process.stdout:
                output.put(line.rstrip())

    reader = threading.Thread(target=collect_output, daemon=True)
    reader.start()
    listening = False
    pairing_code_found = False
    deadline = time.monotonic() + 12
    try:
        while time.monotonic() < deadline:
            try:
                line = output.get(timeout=0.25)
            except queue.Empty:
                if process.poll() is not None:
                    break
                continue
            if "Nexora Gamepad escucha en UDP" in line:
                listening = True
            if "Código de emparejamiento" in line:
                code = line.rsplit(":", 1)[-1].strip()
                pairing_code_found = len(code) == 6 and code.isdigit()
            if listening and pairing_code_found:
                break

        if not listening or not pairing_code_found:
            raise SystemExit("El receptor no inició el servidor UDP o no generó el código de emparejamiento.")

        if process.stdin is not None:
            process.stdin.write("quit\\n")
            process.stdin.flush()
            process.stdin.close()
        try:
            exit_code = process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            raise SystemExit("El receptor no se cerró correctamente durante la prueba.")
        if exit_code != 0:
            raise SystemExit("El receptor terminó con código " + str(exit_code) + ".")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


def main():
    if "--self-test" in sys.argv:
        if getattr(sys, "frozen", False):
            base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        receiver = os.path.join(base, "NexoraReceiver.exe")
        if not os.path.isfile(receiver):
            raise SystemExit("No se encontró NexoraReceiver.exe dentro del paquete.")
        packaged_self_test(receiver)
        return
    root = tk.Tk()
    NexoraLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
