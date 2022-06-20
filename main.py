# _*_ coding: utf-8 _*_
import tkinter as tk

from ui import BaseFrame


def main():
    try:
        import chromedriver_autoinstaller

        chromedriver_autoinstaller.install()
    except ImportError:
        pass

    root = tk.Tk()
    root.geometry("950x330")
    root.title("Auto Buy Bot")
    BaseFrame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
