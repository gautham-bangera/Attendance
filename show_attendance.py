# show_attendance.py
import csv
from tkinter import filedialog, Tk

def subjectchoose(text_to_speech=None):
    root = Tk()
    root.withdraw()
    file = filedialog.askopenfilename(title="Select attendance CSV", initialdir="./Attendance", filetypes=[("CSV files","*.csv")])
    if not file:
        return
    print("Opening:", file)
    with open(file, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)
    if text_to_speech:
        text_to_speech("Attendance file opened")