# automaticAttedance_debug.py
import cv2
import os
import csv
import datetime
import threading

# ===============================
# CONFIG
# ===============================
CONF_THRESHOLD = 80  # lower for testing
FRAMES_REQUIRED = 1  # only 1 frame needed for testing
STUDENT_CSV = "StudentDetails/studentdetails.csv"
TRAINER_PATH = "TrainingImageLabel/Trainer.yml"
ATTENDANCE_DIR = "Attendance"

# ===============================
# LOAD STUDENTS
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
                enr_int = int(enr.lstrip("0") or "0")  # Fix leading zeros
            except:
                continue
            students[enr_int] = (name, mac)
    print("Loaded students:", students)
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

    # Camera setup
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        if text_to_speech:
            text_to_speech("Camera not available")
        print("Camera not available")
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
                except Exception as e:
                    print("Predict error:", e)
                    continue

                print(f"Predicted ID: {predicted_id}, Conf: {conf:.1f}")

                # Frame confirmation counting
                if conf < CONF_THRESHOLD:
                    match_counters[predicted_id] = match_counters.get(predicted_id, 0) + 1
                else:
                    match_counters[predicted_id] = 0

                print("Match counters:", match_counters)

                # Enough frames confirmed
                if match_counters.get(predicted_id, 0) >= FRAMES_REQUIRED:
                    info = students.get(predicted_id)
                    if not info:
                        match_counters[predicted_id] = -9999
                        print(f"No student info for ID {predicted_id}")
                        continue

                    name, _ = info  # MAC check disabled for testing
                    mark_attendance(name, subject)
                    if text_to_speech:
                        text_to_speech(f"Attendance marked for {name}")
                    match_counters[predicted_id] = -9999

            cv2.imshow(f"Attendance - {subject} (Press ESC to stop)", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        if text_to_speech:
            text_to_speech("Attendance session ended")
