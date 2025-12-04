# login.py
from tkinter import messagebox
import tkinter as tk
import attendance

def check_login():
    user = user_e.get()
    pw = pw_e.get()
    if user == "admin" and pw == "1234":
        login_root.destroy()
        attendance.run_attendance_ui()
    else:
        messagebox.showerror("Error", "Invalid username or password")

login_root = tk.Tk()
login_root.title("Login")
login_root.geometry("400x200")

tk.Label(login_root, text="Username:").pack(pady=5)
user_e = tk.Entry(login_root)
user_e.pack(pady=5)
tk.Label(login_root, text="Password:").pack(pady=5)
pw_e = tk.Entry(login_root, show="*")
pw_e.pack(pady=5)
tk.Button(login_root, text="Login", command=check_login).pack(pady=10)

login_root.mainloop()