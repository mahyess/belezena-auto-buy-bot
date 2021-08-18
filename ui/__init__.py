import threading
from helpers.file_system import CARD_FILE, COMPLETED_FILE, ERROR_FILE, FEEDING_FILE
from helpers.csv_reader import get_lines_count
import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter.constants import END, RIDGE
from controllers import (
    auto_buy,
    clear,
    clear_credit,
    load_credit_card,
    load_data,
    pause,
    save,
)


class BaseFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.root = parent
        self.status = 0
        self.total_data = 0

        self.setup_top_left_frame()
        self.setup_top_right_frame()
        self.setup_middle_frame()
        self.setup_bottom_frame()

        self.top_left_frame.grid(row=0, column=0, sticky="ew")
        self.top_right_frame.grid(row=0, column=1, sticky="new")
        self.report_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="sew")

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.refresh_ui()

        self.root.mainloop()

    def setup_top_left_frame(self):
        # menu left
        self.top_left_frame = tk.Frame(self.root, width=300, height=75, bg="#fff")
        self.load_data_btn = tk.Button(
            self.top_left_frame,
            text="Load Data",
            width=12,
            bg="sky blue",
            command=lambda: load_data(self),
        )
        self.load_data_btn.pack(padx=10, pady=5, side="left")
        self.load_credit_data_btn = tk.Button(
            self.top_left_frame,
            text="Load Credit Card",
            width=15,
            bg="sky blue",
            command=lambda: load_credit_card(self),
        )
        self.load_credit_data_btn.pack(padx=10, pady=5, side="left")

    def setup_top_right_frame(self):
        # right area
        self.top_right_frame = tk.Frame(self.root, bg="#fff")

        self.total_data_loaded_lbl = tk.Label(
            self.top_right_frame,
            text="Total data loaded: ",
            # foreground="#ffffff"
        )
        self.total_data_loaded_lbl.pack(
            padx=10,
            pady=5,
        )
        self.total_credit_data_loaded_lbl = tk.Label(
            self.top_right_frame,
            text="Total credit card loaded: ",
        )
        self.total_credit_data_loaded_lbl.pack(
            padx=10,
            pady=5,
        )

        self.auto_buy_btn = tk.Button(
            self.top_right_frame,
            text="Auto Buy",
            width=10,
            bg="green",
            command=lambda: threading.Thread(target=auto_buy, args=(self,)).start(),
        )
        self.auto_buy_btn.pack(padx=10, pady=5, side="left")
        self.pause_btn = tk.Button(
            self.top_right_frame,
            text="Pause",
            width=10,
            bg="orange",
            command=lambda: pause(self),
        )
        self.pause_btn.pack(padx=10, pady=5, side="left")
        self.clear_btn = tk.Button(
            self.top_right_frame,
            text="Clear",
            width=10,
            bg="#bada55",
            command=lambda: clear(self),
        )
        self.clear_btn.pack(padx=10, pady=5, side="left")
        self.clear_credit_btn = tk.Button(
            self.top_right_frame,
            text="Clear Credit",
            width=10,
            bg="#bada55",
            command=lambda: clear_credit(self),
        )
        self.clear_credit_btn.pack(padx=10, pady=5, side="left")

    def setup_middle_frame(self):
        self.report_frame = tk.Frame(
            self.root,
            width=500,
            height=400,
            background="#ffffff",
            highlightbackground="#ffffff",
            highlightthickness=2,
            borderwidth=2,
            relief=RIDGE,
        )
        self.report_frame.place(relx=5, rely=5, anchor="center")
        tk.Label(self.report_frame, text="Report: ", font=(14)).pack(
            padx=10,
            pady=5,
            # side="left",
        )

        self.success_count_frame = tk.Frame(self.report_frame, bg="#111")
        self.success_count = tk.Label(
            self.success_count_frame,
            text="31/354",
            width="14",
        )
        self.success_count.pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.success_count_frame,
            text="Successfull",
            foreground="blue",
            width="14",
        ).pack(padx=10, pady=5, fill="both", expand=1)

        self.error_count_frame = tk.Frame(self.report_frame, bg="#111")
        self.error_count = tk.Label(
            self.error_count_frame,
            text="02/354",
            width="14",
        )
        self.error_count.pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.error_count_frame,
            text="Error",
            foreground="red",
            width="14",
        ).pack(padx=10, pady=5, fill="both", expand=1)

        self.order_left_count_frame = tk.Frame(self.report_frame, bg="#111")
        self.remaining_count = tk.Label(
            self.order_left_count_frame,
            text="321/354",
            width="14",
        )
        self.remaining_count.pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.order_left_count_frame,
            text="Orders Left",
            foreground="green",
            width="14",
        ).pack(padx=10, pady=5, fill="both", expand=1)

        self.cc_left_count_frame = tk.Frame(self.report_frame, bg="#111")
        self.cc_count = tk.Label(self.cc_left_count_frame, text="39/45", width="14")
        self.cc_count.pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.cc_left_count_frame, text="CC Left", foreground="green", width="14"
        ).pack(padx=10, pady=5, fill="both", expand=1)

        self.success_count_frame.pack(padx=10, pady=5, side="left")
        self.error_count_frame.pack(padx=10, pady=5, side="left")
        self.order_left_count_frame.pack(padx=10, pady=5, side="left")
        self.cc_left_count_frame.pack(padx=10, pady=5, side="left")

    def setup_bottom_frame(self):
        # status bar
        self.status_frame = tk.Frame(self.root)
        self.status_lbl = tk.Label(
            self.status_frame, text="Status: Paused", foreground="orange"
        )
        self.status_lbl.pack(fill="both", expand=True)

    def onOpen(self):
        ftypes = [("Csv files", "*.csv"), ("All files", "*")]
        dlg = filedialog.Open(self, filetypes=ftypes)
        return dlg.show()

    @staticmethod
    def show_message_box(title, message, message_type="info"):
        if message_type == "error":
            tk.messagebox.showerror(title, message)
        elif message_type == "warning":
            tk.messagebox.showwarning(title, message)
        elif message_type == "question":
            return tk.messagebox.askokcancel(title, message)
        else:
            tk.messagebox.showinfo(title, message)

    def refresh_ui(self):

        success_count = get_lines_count(COMPLETED_FILE)
        remaining_count = get_lines_count(FEEDING_FILE)
        error_count = get_lines_count(ERROR_FILE)
        card_count = get_lines_count(CARD_FILE)
        self.total_data = success_count + remaining_count + error_count

        self.total_data_loaded_lbl.config(
            text="Total Data Loaded: " + str(self.total_data)
        )
        self.total_credit_data_loaded_lbl.config(
            text="Total Credit Cards Loaded: " + str(card_count)
        )

        self.success_count.config(text=f"{success_count}/{self.total_data}")
        self.remaining_count.config(text=f"{remaining_count}/{self.total_data}")
        self.error_count.config(text=f"{error_count}/{self.total_data}")
        self.cc_count.config(text=f"{card_count}")

        self.status_lbl.config(
            text="Status: Active" if bool(self.status) else "Status: Inactive",
            foreground="Green" if bool(self.status) else "Orange",
        )
