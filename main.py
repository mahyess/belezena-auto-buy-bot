import tkinter as tk
from ui import BaseFrame


def main():
    root = tk.Tk()
    root.geometry("950x300")
    root.title("Auto Buy Bot")
    BaseFrame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
