# attendance.py
# Main launcher: ensures folders, provides TTS, starts the enhanced UI.

import os
import csv
import threading
import pyttsx3

# Ensure project dirs
os.makedirs("StudentDetails", exist_ok=True)
os.makedirs("TrainingImage", exist_ok=True)
os.makedirs("TrainingImageLabel", exist_ok=True)
os.makedirs("Attendance", exist_ok=True)

STUDENT_CSV = "StudentDetails/studentdetails.csv"
if not os.path.exists(STUDENT_CSV):
    with open(STUDENT_CSV, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["Enrollment", "Name", "MAC"])

# Text to speech utility (thread-safe wrapper)
engine = pyttsx3.init()
_engine_lock = threading.Lock()

def text_to_speech(text: str):
    def _speak():
        with _engine_lock:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass
    threading.Thread(target=_speak, daemon=True).start()

# Launch UI
if __name__ == "__main__":
    # Delay importing UI until resources in place (avoid side-effects)
    from attendance_ui import run_main_ui
    # run_main_ui will import modules and pass text_to_speech around where needed
    run_main_ui()
