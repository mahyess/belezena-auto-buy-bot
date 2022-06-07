import tkinter as tk
import chromedriver_autoinstaller

from ui import BaseFrame


def main():
    installed = chromedriver_autoinstaller.install()
    root = tk.Tk()
    root.geometry("950x300")
    root.title("Auto Buy Bot")
    BaseFrame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
