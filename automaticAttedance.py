# automaticAttedance.py (updated)
import cv2
import os
import csv
import datetime
import threading

# Optional tkinter import is not required here since subject is passed by UI
# For TTS, we will accept a callable text_to_speech argument

# ===============================
# CONFIG
# ===============================
CONF_THRESHOLD = 100
FRAMES_REQUIRED = 2

STUDENT_CSV = "StudentDetails/studentdetails.csv"
TRAINER_PATH = "TrainingImageLabel/Trainer.yml"
ATTENDANCE_DIR = "Attendance"


# ===============================
# BLUETOOTH OPTIONAL MODULE
# ===============================
try:
    from bluetoothScanner import BluetoothScanner
    BT_AVAILABLE = True
except Exception:
    BluetoothScanner = None
    BT_AVAILABLE = False


# ===============================
# LOAD STUDENT LIST
# ===============================
def load_student_map():
    students = {}
    if not os.path.exists(STUDENT_CSV):
        return students

    with open(STUDENT_CSV, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            enr = row[0].strip()
            name = row[1].strip()
            mac = row[2].strip().upper() if len(row) >= 3 else ""
            try:
                enr_int = int(enr)
            except:
                continue
            students[enr_int] = (name, mac)
    return students


# ===============================
# MARK ATTENDANCE
# ===============================
def mark_attendance(name, subject):
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    filename = os.path.join(ATTENDANCE_DIR, f"{subject}_{date}.csv")

    if not os.path.exists(filename):
        with open(filename, "w", newline="") as f:
            csv.writer(f).writerow(["Name", "Date", "Time"])

    already = False
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row and row[0] == name:
                already = True
                break

    if not already:
        with open(filename, "a", newline="") as f:
            csv.writer(f).writerow([name, date, time_str])
        print(f">> Attendance saved for: {name}")
    else:
        print(f">> Already marked for: {name}")


# ===============================
# MAIN ATTENDANCE FUNCTION
# ===============================
def subjectChoose(subject, text_to_speech=None):
    """
    Start attendance for a given subject.
    - subject: string (required) provided by UI
    - text_to_speech: optional callable(text) to announce events
    """
    if not subject or not str(subject).strip():
        if text_to_speech:
            text_to_speech("Please enter a valid subject name.")
        return

    subject = str(subject).strip()

    # Check trainer file
    if not os.path.exists(TRAINER_PATH):
        print("Trainer.yml missing")
        if text_to_speech:
            text_to_speech("No trained model found. Please train first.")
        return

    # Load students
    students = load_student_map()
    if not students:
        print("No students found in CSV")
        if text_to_speech:
            text_to_speech("No students registered.")
        return

    # Load face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(TRAINER_PATH)

    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # Start Bluetooth Scanner if available
    bt = None
    if BT_AVAILABLE and BluetoothScanner:
        bt = BluetoothScanner(interval=4)
        bt.daemon = True
        bt.start()

    # Start Camera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        if text_to_speech:
            text_to_speech("Camera not available")
        return

    if text_to_speech:
        text_to_speech(f"Starting attendance for {subject}")

    match_counters = {}

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)

            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                try:
                    predicted_id, conf = recognizer.predict(face_roi)
                except Exception:
                    continue

                # Draw face box & label
                color = (0, 255, 0) if conf < CONF_THRESHOLD else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, f"ID: {predicted_id}  Conf:{conf:.1f}",
                            (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                # Frame confirmation counting
                if conf < CONF_THRESHOLD:
                    match_counters[predicted_id] = match_counters.get(predicted_id, 0) + 1
                else:
                    match_counters[predicted_id] = 0

                # Enough frames confirmed
                if match_counters.get(predicted_id, 0) >= FRAMES_REQUIRED:
                    info = students.get(predicted_id)
                    if not info:
                        match_counters[predicted_id] = -9999
                        continue

                    name, expected_mac = info

                    # Bluetooth check
                    detected_macs = []
                    if bt:
                        try:
                            devs = bt.get_devices() or []
                            detected_macs = [m.upper() for m, _ in devs]
                        except Exception:
                            detected_macs = []

                    if expected_mac == "" or expected_mac.upper() in detected_macs:
                        mark_attendance(name, subject)
                        if text_to_speech:
                            text_to_speech(f"Attendance marked for {name}")
                        match_counters[predicted_id] = -9999
                    else:
                        print(f"Face matched for {name} but MAC {expected_mac} not detected")
                        match_counters[predicted_id] = 0

            cv2.imshow(f"Attendance - {subject} (Press ESC to stop)", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        if bt:
            bt.stop()
        if text_to_speech:
            text_to_speech("Attendance session ended")
