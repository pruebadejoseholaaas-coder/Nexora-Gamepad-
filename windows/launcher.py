"""Nexora Gamepad Windows desktop launcher.

The UI owns the receiver process and displays its pairing code and network log.
No account, cloud service, or telemetry is used.
"""
import os
import queue
import subprocess
import sys
import threading
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
        ttk.Label(pairing, textvariable=self.code, font=("Consolas", 27, "bold"), foreground="#60a5fa", background="#111827").pack(anchor="w")
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
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            self.process = subprocess.Popen(
                command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                creationflags=creationflags, env=env
            )
        except OSError as exc:
            self.append_log("No se pudo iniciar el receptor: " + str(exc))
            self.process = None
            return
        self.code.set("------")
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
            process.terminate()
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
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
                    self.append_log("Receptor finalizado (código " + str(code) + ").")
        except queue.Empty:
            pass
        self.root.after(100, self.process_events)

    def close(self):
        process = self.process
        if process is not None and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=2)
            except Exception:
                try:
                    process.kill()
                except OSError:
                    pass
        self.root.destroy()


def main():
    root = tk.Tk()
    NexoraLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
