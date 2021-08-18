import tkinter as tk
from controllers import load_credit_card


# from tkinter.commondialog import Dialog
import tkinter.simpledialog as sd


class CustomCCCardMessage(sd.Dialog):
    def __init__(self, parent, title="Hello", *args, **options):
        self.parent = parent
        self.master = parent
        super().__init__(parent, title, *args, **options)

    def body(self, frame):
        self.l1 = tk.Label(frame, text="Load more cards to continue.")
        self.l1.pack()

        return frame

    def buttonbox(self):
        box = tk.Frame(self)

        w = tk.Button(
            box,
            text="Load Credit Cards",
            width=10,
            command=lambda: self.on_load_credit_card(),
            default=tk.ACTIVE,
        )
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel_pressed)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.on_load_credit_card)
        self.bind("<Escape>", self.cancel_pressed)

        box.pack()

    def on_load_credit_card(self):
        load_credit_card(self.parent)
        self.destroy()

    def cancel_pressed(self):
        self.destroy()


def load_more_credit_card(root):
    CustomCCCardMessage(title="Load More Credit Cards", parent=root)
    return 1
