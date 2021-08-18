import tkinter as tk
from controllers import load_credit_card


from tkinter.commondialog import Dialog


class CustomCCCardMessage(Dialog):
    command = None

    def __init__(self, parent, *args, **options):
        super().__init__(parent, *args, **options)
        self.parent = parent
        self.master = parent
        self.top = tk.Toplevel(self.parent)
        self.top.geometry("400x200")
        self.top.transient(self.parent)

        self.top.title("Credit Card Empty")
        self.f0 = tk.Frame(self.top)
        self.top.l1 = tk.Label(self.f0, text="Load more cards to continue.")
        self.top.l1.pack(pady=30)
        self.f0.pack()
        self.top.grab_set()
        self.top.f1 = tk.Frame(self.top)
        # for key in kwargs:
        import_btn = tk.Button(
            self.top.f1,
            text=f"Load Credit Cards",
            command=lambda: self.on_load_credit_card(),
        )
        import_btn.pack(side=tk.LEFT)
        self.top.f1.pack()

    def on_load_credit_card(self):
        load_credit_card(self.parent)
        self.top.destroy()
