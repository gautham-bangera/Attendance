# attendance_ui_live_optimized.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import os
import csv

# ---------------- Safe optional imports ----------------
try: import takeImage
except: takeImage = None
try: import trainImage
except: trainImage = None
try: import automaticAttedance_debug as automaticAttendance
except: automaticAttendance = None
try: import show_attendance
except: show_attendance = None

# ---------------- Utilities ----------------
def text_to_speech_proxy(text: str):
    print("TTS:", text)  # fallback
    try:
        import attendance as att_mod
        if hasattr(att_mod, "text_to_speech"):
            att_mod.text_to_speech(text)
    except: pass

def load_icon(path: str, size=(36, 36)):
    if not path or not os.path.exists(path): return None
    return ImageTk.PhotoImage(Image.open(path).resize(size))

# ---------------- Main UI ----------------
def run_main_ui():
    root = tk.Tk()
    root.title("Smart Attendance")
    root.geometry("1000x600")
    root.configure(bg="#0f1720")
    root.resizable(False, False)

    # ---------------- Sidebar ----------------
    sidebar = tk.Frame(root, width=260, bg="#0b1220")
    sidebar.place(x=0, y=0, height=600)

    tk.Label(sidebar, text="CLASS VISION", fg="white", bg="#0b1220", font=("Inter", 18, "bold")).pack(pady=(28, 12))

    icons_dir = "UI_Image"
    icons = {
        "register": load_icon(os.path.join(icons_dir, "register.png")),
        "train": load_icon(os.path.join(icons_dir, "verifyy.png")),
        "attendance": load_icon(os.path.join(icons_dir, "attendance.png")),
        "show": load_icon(os.path.join(icons_dir, "0003.png")),
    }

    def sidebar_btn(text, icon, cmd):
        f = tk.Frame(sidebar, bg="#0b1220")
        f.pack(fill="x", padx=14, pady=8)
        b = tk.Button(f, text=f"  {text}", image=icon, compound="left",
                      bg="#0b1220", fg="white", anchor="w", bd=0,
                      activebackground="#111827", font=("Inter", 12),
                      padx=8, pady=8, command=cmd)
        b.image = icon
        b.pack(fill="x")
        return b

    # ---------------- Content ----------------
    content = tk.Frame(root, bg="#081018")
    content.place(x=260, y=0, width=740, height=600)

    tk.Label(content, text="Smart Attendance System", bg="#081018", fg="white",
             font=("Inter", 24, "bold")).pack(pady=(36,6))
    tk.Label(content, text="Face Recognition + Bluetooth verification", bg="#081018",
             fg="#9ca3af", font=("Inter", 12)).pack()

    card = tk.Frame(content, bg="#0b1220")
    card.pack(pady=18, padx=20, fill="x")
    lbl_stat = tk.Label(card, text="Ready", bg="#0b1220", fg="#86efac", font=("Inter", 11, "bold"))
    lbl_stat.pack(anchor="w", padx=12, pady=10)

    # ---------------- Live Attendance ----------------
    tk.Label(content, text="Live Attendance:", bg="#081018", fg="white", font=("Inter", 12, "bold")).pack(anchor="w", padx=24)
    attendance_listbox = tk.Listbox(content, bg="#1f2937", fg="white", font=("Inter", 11), height=12)
    attendance_listbox.pack(fill="both", padx=20, pady=6)
    attendance_count_label = tk.Label(content, text="Total: 0", bg="#081018", fg="#86efac", font=("Inter", 11, "bold"))
    attendance_count_label.pack(anchor="e", padx=24)

    footer = tk.Label(root, text="Built with ♥  —  CLASS VISION", bg="#081018", fg="#6b7280", font=("Inter", 10))
    footer.place(x=260, y=570)

    # ---------------- Panel Animation ----------------
    panel_width = 360
    panel_hidden_x = 1000
    panel_shown_x = 1000 - panel_width
    panel = tk.Frame(root, bg="#0d1720", width=panel_width, height=600)
    panel.place(x=panel_hidden_x, y=0)

    tk.Label(panel, text="Start Attendance", bg="#0d1720", fg="white", font=("Inter", 14, "bold")).pack(pady=(32,8))
    tk.Label(panel, text="Subject name", bg="#0d1720", fg="#9ca3af", font=("Inter", 10)).pack(anchor="w", padx=16, pady=(12,4))
    subject_e = tk.Entry(panel, font=("Inter",12), bd=0, highlightthickness=1, relief="flat")
    subject_e.pack(fill="x", padx=16, pady=(0,12))

    start_btn = tk.Button(panel, text="Start Attendance", bg="#0b84ff", fg="white", font=("Inter", 12, "bold"), bd=0, padx=8, pady=8)
    start_btn.pack(padx=16, pady=(6,12), fill="x")
    close_btn = tk.Button(panel, text="Close", bg="#111827", fg="white", bd=0, padx=8, pady=8)
    close_btn.pack(padx=16, pady=(0,24), fill="x")

    def animate_panel(start_x, end_x, step):
        cur_x = start_x
        def _step():
            nonlocal cur_x
            if (step<0 and cur_x+step<=end_x) or (step>0 and cur_x+step>=end_x):
                panel.place(x=end_x,y=0)
                return
            cur_x+=step
            panel.place(x=cur_x,y=0)
            root.after(8,_step)
        _step()

    def slide_in(): animate_panel(panel_hidden_x, panel_shown_x, -12)
    def slide_out(): animate_panel(int(panel.winfo_x()), panel_hidden_x, 12)

    # ---------------- Commands ----------------
    def cmd_register():
        if takeImage is None: return messagebox.showwarning("Missing module", "takeImage module not found.")
        open_register_ui()
    def cmd_train():
        if trainImage is None: return messagebox.showwarning("Missing module", "trainImage module not found.")
        def _work():
            text_to_speech_proxy("Training started")
            msg = trainImage.trainImages()
            messagebox.showinfo("Training", str(msg))
            text_to_speech_proxy("Training completed")
        threading.Thread(target=_work, daemon=True).start()
    def cmd_attendance():
        if automaticAttendance is None: return messagebox.showwarning("Missing module", "automaticAttendance module not found.")
        subject_e.delete(0,tk.END); slide_in(); subject_e.focus_set()
    def cmd_show():
        if show_attendance is None: return messagebox.showwarning("Missing module", "show_attendance module not found.")
        try:
            if hasattr(show_attendance,"subjectchoose"): show_attendance.subjectchoose(text_to_speech_proxy)
            elif hasattr(show_attendance,"show"): show_attendance.show()
        except Exception as e: messagebox.showerror("Error", str(e))

    # ---------------- Start attendance ----------------
    def start_attendance_from_panel():
        subj = subject_e.get().strip()
        if not subj: return messagebox.showerror("Missing","Please enter a subject name.")
        def on_marked(name):
            attendance_listbox.insert(tk.END,name)
            attendance_count_label.config(text=f"Total: {attendance_listbox.size()}")
        threading.Thread(target=lambda: automaticAttendance.subjectChoose(subj,
                                                                        text_to_speech=text_to_speech_proxy,
                                                                        on_marked=on_marked),
                         daemon=True).start()
        slide_out()

    start_btn.config(command=start_attendance_from_panel)
    close_btn.config(command=slide_out)

    # ---------------- Sidebar Buttons ----------------
    sidebar_btn("Register Face", icons["register"], cmd_register)
    sidebar_btn("Train Model", icons["train"], cmd_train)
    sidebar_btn("Take Attendance", icons["attendance"], cmd_attendance)
    sidebar_btn("View Attendance", icons["show"], cmd_show)

    # ---------------- Registration Window ----------------
    def open_register_ui():
        win = tk.Toplevel(root)
        win.title("Register Student")
        win.geometry("480x360")
        win.configure(bg="#081018")
        frm = tk.Frame(win,bg="#081018"); frm.pack(pady=20,padx=16,fill="both",expand=True)

        tk.Label(frm,text="Enrollment ID",bg="#081018",fg="white").grid(row=0,column=0,sticky="e",pady=6)
        enr_e = tk.Entry(frm); enr_e.grid(row=0,column=1,pady=6,padx=8)
        tk.Label(frm,text="Full Name",bg="#081018",fg="white").grid(row=1,column=0,sticky="e",pady=6)
        name_e = tk.Entry(frm); name_e.grid(row=1,column=1,pady=6,padx=8)
        tk.Label(frm,text="Bluetooth MAC (optional)",bg="#081018",fg="white").grid(row=2,column=0,sticky="e",pady=6)
        mac_e = tk.Entry(frm); mac_e.grid(row=2,column=1,pady=6,padx=8)

        status = tk.Label(frm,text="",bg="#081018",fg="#9ca3af"); status.grid(row=4,column=0,columnspan=2,pady=6)

        def save_and_capture():
            enr, name, mac = enr_e.get().strip(), name_e.get().strip(), mac_e.get().strip().replace("-",":").upper()
            if not enr or not name: return messagebox.showerror("Missing fields","Enrollment and Name are required.")
            os.makedirs(os.path.dirname("StudentDetails/studentdetails.csv"), exist_ok=True)
            with open("StudentDetails/studentdetails.csv","a",newline="",encoding="utf-8") as f:
                csv.writer(f).writerow([enr,name,mac])
            status.config(text=f"Saved {name}")
            text_to_speech_proxy(f"Registering {name}")
            if takeImage: threading.Thread(target=lambda: takeImage.takeImages(enr,name),daemon=True).start()

        tk.Button(frm,text="Save & Capture Face",command=save_and_capture,bg="#0b1220",fg="white").grid(row=3,column=0,columnspan=2,pady=12)

    root.mainloop()

if __name__=="__main__":
    run_main_ui()
