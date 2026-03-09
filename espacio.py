# pyton_keyspam.py
# Script: pulsa BACKSPACE repetidamente mientras esté activo.
# Hotkeys:
#   F9 = toggle start / stop
#   F8 = salir (termina el script)
#
# Requisitos: pip install keyboard
# En Windows ejecutar con permisos de administrador para que keyboard funcione correctamente.

import threading
import time
import sys

try:
    import keyboard  # pip install keyboard
except Exception as e:
    print("Error: falta la librería 'keyboard'. Instala con: pip install keyboard")
    raise

# Opciones:
KEY_TO_PRESS = 'backspace'   # 'backspace' o 'delete' según prefieras
PRESS_INTERVAL = 0.05        # segundos entre cada pulsación (0.05 = 20 puls/s). Ajusta si quieres más lento.
USE_BEEP = True              # True -> suena un beep corto al activar/desactivar/salir (Windows)

# --- beep simple en Windows (silencioso si no disponible) ---
def beep_ok():
    if not USE_BEEP:
        return
    try:
        import winsound
        freq = 800
        dur = 100
        winsound.Beep(freq, dur)
    except Exception:
        # si winsound no está (p.ej. no-Windows) simplemente no haga nada
        pass

# --- controlador del spam de teclas ---
running_event = threading.Event()   # si está seteado => estamos enviando teclas
exit_event = threading.Event()      # si se setea => salir completamente

def spam_worker():
    """Thread que envía la tecla KEY_TO_PRESS cada PRESS_INTERVAL mientras running_event esté seteado."""
    while not exit_event.is_set():
        if running_event.is_set():
            try:
                # presionar y soltar la tecla
                keyboard.press_and_release(KEY_TO_PRESS)
            except Exception:
                # si falla enviar la tecla, intentamos de nuevo la próxima vez
                pass
            time.sleep(PRESS_INTERVAL)
        else:
            # pequeño sleep para no consumir CPU cuando está detenido
            time.sleep(0.05)

# --- funciones para hotkeys ---
def toggle_running():
    if running_event.is_set():
        running_event.clear()
        beep_ok()
        print("[Pyton] DETENIDO (F9 para iniciar).")
    else:
        running_event.set()
        beep_ok()
        print("[Pyton] INICIADO: presionando '{}'... (F9 para detener, F8 para salir)".format(KEY_TO_PRESS))

def request_exit():
    # apaga el envío, avisa y sale
    running_event.clear()
    beep_ok()
    print("[Pyton] SALIENDO... (F8 presionado).")
    exit_event.set()

def main():
    print("Pyton key-spammer iniciado.")
    print("F9 = start/stop | F8 = salir")
    print("Presionando '{}' cada {} s cuando esté activo.".format(KEY_TO_PRESS, PRESS_INTERVAL))
    # iniciar thread trabajador
    t = threading.Thread(target=spam_worker, daemon=True)
    t.start()

    # registrar hotkeys
    try:
        keyboard.add_hotkey('f9', toggle_running)
        keyboard.add_hotkey('f8', request_exit)
    except Exception as e:
        print("Error registrando hotkeys. Asegúrate de ejecutar con permisos adecuados (en Windows: administrador).")
        raise

    # bloquear hasta que se pida salida
    try:
        while not exit_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        # si el usuario usa Ctrl+C
        request_exit()

    # esperar que thread termine (saldrá por exit_event)
    t.join(timeout=1.0)
    print("Pyton terminado. Adiós.")
    # opcionalmente cerrar proceso
    try:
        sys.exit(0)
    except SystemExit:
        pass

if __name__ == '__main__':
    main()
