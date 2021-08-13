# from tkinter.ttk import Progressbar
# from tkinter import *

# # First create application class
# class Application(Frame):
#     def __init__(self, master=None):
#         Frame.__init__(self, master)

#         self.pack()
#         self.create_widgets()

#     # Create main GUI window
#     def create_widgets(self):
#         # self.search_var = StringVar()
#         # self.search_var.trace("w", lambda name, index, mode: self.update_list())
#         # self.entry = Entry(self, textvariable=self.search_var, width=13)

#         # self.entry.grid(row=0, column=0, padx=10, pady=3)
#         # self.lbox.grid(row=1, column=0, padx=10, pady=3)

#         self.load_data_btn = Button(self, text="Load Data", width=20)
#         self.load_card_btn = Button(self, text="Load Credit Card", width=20)

#         self.total_data_loaded_text = StringVar()
#         self.total_card_loaded_text = StringVar()
#         self.total_data_loaded_lbl = Label(self, text="Total data loaded: 0")
#         self.total_card_loaded_lbl = Label(self, text="Total credit card loaded: 0")

#         self.autobuy_btn = Button(self, text="Auto Buy", width=20)
#         self.pause_btn = Button(self, text="Pause", width=20)
#         self.clear_btn = Button(self, text="Clear", width=20)

#         self.load_data_btn.grid(row=1, column=0, padx=10, pady=3)
#         self.load_card_btn.grid(row=1, column=1, padx=10, pady=3)
#         self.total_data_loaded_lbl.grid(row=1, column=1, padx=10, pady=3)


#         self.lb1 = Label(self, text="Total data loaded: 0")
#         self.lb1.grid(row=3, column=0, padx=10, pady=3)


# root = Tk()
# root.title("Auto buy bot")
# Label(root, text="Enter text to Search brands/categories.").pack()
# app = Application(master=root)
# print("Starting mainloop()")
# app.mainloop()


import tkinter as tk
from tkinter.constants import RIDGE


class Example:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("700x300")
        self.root.title("Auto Buy Bot")
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

        self.root.mainloop()

    def setup_top_left_frame(self):
        # menu left
        self.top_left_frame = tk.Frame(self.root, width=300, height=75, bg="#fff")
        self.load_data_btn = tk.Button(
            self.top_left_frame, text="Load Data", width=10, bg="sky blue"
        )
        self.load_data_btn.pack(padx=10, pady=5, side="left")
        self.load_credit_data_btn = tk.Button(
            self.top_left_frame, text="Load Credit Card", width=10, bg="sky blue"
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
            self.top_right_frame, text="Auto Buy", width=10, bg="green"
        )
        self.auto_buy_btn.pack(padx=10, pady=5, side="left")
        self.pause_btn = tk.Button(
            self.top_right_frame, text="Pause", width=10, bg="orange"
        )
        self.pause_btn.pack(padx=10, pady=5, side="left")
        self.clear_btn = tk.Button(
            self.top_right_frame, text="Clear", width=10, bg="#bada55"
        )
        self.clear_btn.pack(padx=10, pady=5, side="left")

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
        tk.Label(
            self.success_count_frame,
            text="31/354",
            width="14",
        ).pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.success_count_frame,
            text="Successfull",
            foreground="blue",
            width="14",
        ).pack(padx=10, pady=5, fill="both", expand=1)
        self.error_count_frame = tk.Frame(self.report_frame, bg="#111")
        tk.Label(
            self.error_count_frame,
            text="02/354",
            width="14",
        ).pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.error_count_frame,
            text="Error",
            foreground="red",
            width="14",
        ).pack(padx=10, pady=5, fill="both", expand=1)
        self.order_left_count_frame = tk.Frame(self.report_frame, bg="#111")
        tk.Label(
            self.order_left_count_frame,
            text="321/354",
            width="14",
        ).pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.order_left_count_frame,
            text="Orders Left",
            foreground="green",
            width="14",
        ).pack(padx=10, pady=5, fill="both", expand=1)
        self.cc_left_count_frame = tk.Frame(self.report_frame, bg="#111")
        tk.Label(self.cc_left_count_frame, text="39/45", width="14").pack(
            padx=10, pady=5, fill="both", expand=1
        )
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
        self.save_btn = tk.Button(self.status_frame, text="Save", width=10, bg="green")
        self.save_btn.pack(padx=10, pady=5, side="left")
        self.status_lbl = tk.Label(
            self.status_frame, text="Status: Paused", foreground="orange"
        )
        self.status_lbl.pack(fill="both", expand=True)


Example()
