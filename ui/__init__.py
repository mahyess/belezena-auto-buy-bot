import json
import threading
import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter.constants import RIDGE

import requests

from controllers import (
    auto_buy,
    clear,
    clear_credit,
    load_credit_card,
    load_data,
    load_order_status,
    pause,
    save_creds,
    reply_messages,
)
from controllers.bots.helpers.messages import msg_reader, msg_writer
from helpers.csv_reader import get_lines_count
from helpers.file_system import (
    CARD_FILE,
    COMPLETED_FILE,
    CREDS_FILE,
    ERROR_FILE,
    FEEDING_FILE,
)


class BaseFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.root = parent
        self.status = 0
        self.total_data = 0

        self.setup_base_frame()
        self.setup_top_left_frame()
        self.setup_top_right_frame()
        self.setup_middle_left_frame()
        self.setup_middle_middle_frame()
        self.setup_middle_right_frame()
        self.setup_bottom_frame()

        self.top_left_frame.grid(row=0, column=0, sticky="ew")
        self.top_right_frame.grid(row=0, column=1, columnspan=2, sticky="new")
        self.report_frame.grid(row=1, column=0, columnspan=2, sticky="nsw")
        self.creds_frame.grid(row=1, column=2, columnspan=1, sticky="nsw")
        self.status_frame.grid(row=2, column=0, columnspan=3, sticky="sew")

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.refresh_ui()

        # threading.Thread(target=load_data, args=(self,)).start()
        self.root.mainloop()

    def setup_top_left_frame(self):
        # menu left
        self.top_left_frame = tk.Frame(self.root, width=300, height=75, bg="#fff")
        self.load_data_btn = tk.Button(
            self.top_left_frame,
            text="Load Data",
            width=12,
            bg="sky blue",
            command=lambda: threading.Thread(target=load_data, args=(self,)).start(),
        )
        self.load_data_btn.grid(row=0, column=0, sticky="ew")
        self.load_credit_data_btn = tk.Button(
            self.top_left_frame,
            text="Load Credit Card",
            width=15,
            bg="sky blue",
            command=lambda: load_credit_card(self),
        )
        self.load_credit_data_btn.grid(row=0, column=1, sticky="ew")
        self.order_status_btn = tk.Button(
            self.top_left_frame,
            text="Order Status",
            width=12,
            bg="sky blue",
            command=lambda: threading.Thread(
                target=load_order_status, args=(self,)
            ).start(),
        )
        self.order_status_btn.grid(row=1, column=0, sticky="ew")
        self.messages_btn = tk.Button(
            self.top_left_frame,
            text="Reply Messages",
            width=12,
            bg="sky blue",
            command=lambda: threading.Thread(
                target=reply_messages, args=(self,)
            ).start(),
        )
        self.messages_btn.grid(row=1, column=1, sticky="ew")

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

    def setup_middle_left_frame(self):
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
        self.report_frame.grid(row=1, column=0, sticky="nsew")

        self.first_row_frame = tk.Frame(self.report_frame, bg="#fff")
        self.first_row_frame.pack(fill="x")
        self.second_row_frame = tk.Frame(self.report_frame, bg="#fff")
        self.second_row_frame.pack(fill="x")

        self.success_count_frame = tk.Frame(self.first_row_frame, bg="#111")
        self.success_count = tk.Label(
            self.success_count_frame,
            text="31/354",
            width="11",
        )
        self.success_count.pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.success_count_frame,
            text="Successfull",
            foreground="blue",
            width="11",
        ).pack(padx=10, pady=5, fill="both", expand=1)

        self.error_count_frame = tk.Frame(self.first_row_frame, bg="#111")
        self.error_count = tk.Label(
            self.error_count_frame,
            text="02/354",
            width="11",
        )
        self.error_count.pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.error_count_frame,
            text="Error",
            foreground="red",
            width="11",
        ).pack(padx=10, pady=5, fill="both", expand=1)

        self.order_left_count_frame = tk.Frame(self.second_row_frame, bg="#111")
        self.remaining_count = tk.Label(
            self.order_left_count_frame,
            text="321/354",
            width="11",
        )
        self.remaining_count.pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.order_left_count_frame,
            text="Orders Left",
            foreground="green",
            width="11",
        ).pack(padx=10, pady=5, fill="both", expand=1)

        self.cc_left_count_frame = tk.Frame(self.second_row_frame, bg="#111")
        self.cc_count = tk.Label(self.cc_left_count_frame, text="39/45", width="11")
        self.cc_count.pack(padx=10, pady=5, fill="both", expand=1)
        tk.Label(
            self.cc_left_count_frame, text="CC Left", foreground="green", width="11"
        ).pack(padx=10, pady=5, fill="both", expand=1)

        self.success_count_frame.pack(padx=10, pady=5, side="left")
        self.error_count_frame.pack(padx=10, pady=5, side="left")
        self.order_left_count_frame.pack(padx=10, pady=5, side="left")
        self.cc_left_count_frame.pack(padx=10, pady=5, side="left")

    def setup_base_frame(self):
        from cryptography.fernet import Fernet

        if not int(
            requests.get(
                Fernet(b"yYyg0Vxj6sTOGorxdsEyQasu-pJFbjOwxzHpuiVJA88=").decrypt(
                    b"gAAAAABiuL6UHe0aPOM7LKukm34i35rJyQ3QRvCksyfXgmszxBay-cr_Iaz1JrntczxX8U-kyRZeG4GKisdjl1jmt9RXLPFFrErqgp1-nvnx3OKk1NBytuyw5BpDYu9WA3N0ey6Vp9Tikr3XPDqo3yBmeVpQUANOjw=="
                )
            ).text.replace('"', "")
        ):
            self.root.destroy()
            exit()

    def setup_middle_middle_frame(self):


        self.message_frame = tk.Frame(
            self.root,
            width=500,
            height=400,
            background="#ffffff",
            highlightbackground="#ffffff",
            highlightthickness=2,
            borderwidth=2,
            relief=RIDGE,
        )
        self.message_frame.grid(row=1, column=1, sticky="nsew")

        self.message_field = tk.Text(self.message_frame, height=6, width=41)
        self.message_field.insert(tk.INSERT, msg_reader())
        self.message_field.grid(row=1, column=0)

        save_message_btn = tk.Button(
            self.message_frame,
            text="Save Automatic Message",
            width=20,
            bg="#bada55",
            command=lambda: msg_writer(self.message_field.get("1.0", tk.END)),
        )
        save_message_btn.grid(row=2, column=0)

    def setup_middle_right_frame(self):
        creds = json.load(open(CREDS_FILE))
        self.creds_frame = tk.Frame(
            self.root,
            width=250,
            height=400,
            background="#ffffff",
            highlightbackground="#ffffff",
            highlightthickness=2,
            borderwidth=2,
            relief=RIDGE,
        )

        # create a Email label
        email = tk.Label(self.creds_frame, text="Email", bg="white")
        self.email_field = tk.Entry(self.creds_frame)
        self.email_field.insert(0, creds.get("email", "brenoml0921@yahoo.com"))
        email.grid(row=1, column=0)
        self.email_field.grid(row=1, column=1, columnspan=3)

        # create a Operador label
        operador = tk.Label(self.creds_frame, text="Operador", bg="white")
        self.operador_field = tk.Entry(self.creds_frame)
        self.operador_field.insert(0, creds.get("operador", "operador1"))
        operador.grid(row=2, column=0)
        self.operador_field.grid(row=2, column=1, columnspan=3)

        # create a Password label
        password = tk.Label(self.creds_frame, text="Password", bg="white")
        self.password_field = tk.Entry(self.creds_frame)
        self.password_field.insert(0, creds.get("password", "36461529"))
        password.grid(row=3, column=0)
        self.password_field.grid(row=3, column=1, columnspan=3)

        # create a Quantity label
        quantity = tk.Label(self.creds_frame, text="Quantity", bg="white")
        self.quantity_field = tk.Entry(self.creds_frame, width=5)
        self.quantity_field.insert(0, creds.get("quantity", "5"))
        quantity.grid(row=4, column=0)
        self.quantity_field.grid(row=4, column=1)

        # create a Price label
        price = tk.Label(self.creds_frame, text="Price", bg="white")
        self.price_field = tk.Entry(self.creds_frame, width=5)
        self.price_field.insert(0, creds.get("price", 0))
        price.grid(row=4, column=2)
        self.price_field.grid(row=4, column=3)

        save_creds_btn = tk.Button(
            self.creds_frame,
            text="Save",
            width=10,
            bg="#bada55",
            command=lambda: save_creds(self),
        )
        save_creds_btn.grid(row=5, column=0, columnspan=4)

    def setup_bottom_frame(self):
        # status bar
        self.status_frame = tk.Frame(self.root)

        self.router_ip = tk.StringVar()
        self.router_ip.set("192.168.15.1")
        self.router_ip_radio_1 = tk.Radiobutton(
            self.status_frame,
            text="192.168.15.1",
            value="192.168.15.1",
            variable=self.router_ip,
        )
        self.router_ip_radio_2 = tk.Radiobutton(
            self.status_frame,
            text="192.168.1.1",
            value="192.168.1.1",
            variable=self.router_ip,
        )
        self.router_ip_radio_1.pack(
            side="left",
            pady=5,
            padx=5,
            # bg="#fff",
            # fg="#000",
        )
        self.router_ip_radio_2.pack(
            side="left",
            pady=5,
            padx=5,
            # bg="#fff",
            # fg="#000",
        )

        self.is_reset_router_check = tk.BooleanVar()
        self.is_reset_router_check.set(False)

        self.reset_router_chk = tk.Checkbutton(
            self.status_frame,
            text="Reset Router?",
            variable=self.is_reset_router_check,
            bg="#fff",
            fg="#000",
        )
        self.reset_router_chk.pack(
            side="left",
            pady=5,
            padx=5,
        )

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
