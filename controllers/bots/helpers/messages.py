from helpers.file_system import MSG_FILE
import tkinter as tk


def msg_writer(txt):
    with open(MSG_FILE, "w", encoding="utf-8") as f:
        f.write(txt)
    tk.messagebox.showinfo("Save", "Message Saved")


def msg_reader():
    try:
        with open(MSG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Test Message"