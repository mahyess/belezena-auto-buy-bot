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
class Example:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("some application")

        # menu left
        self.menu_left = tk.Frame(self.root, width=150, bg="#ababab")
        self.menu_left_upper = tk.Frame(self.menu_left, width=150, height=150, bg="red")
        self.menu_left_lower = tk.Frame(self.menu_left, width=150, bg="blue")

        self.test = tk.Label(self.menu_left_upper, text="test")
        self.test.pack()

        self.menu_left_upper.pack(side="top", fill="both", expand=True)
        self.menu_left_lower.pack(side="top", fill="both", expand=True)

        # right area
        self.some_title_frame = tk.Frame(self.root, bg="#dfdfdf")

        self.some_title = tk.Label(
            self.some_title_frame, text="some title", bg="#dfdfdf"
        )
        self.some_title.pack()

        self.canvas_area = tk.Canvas(
            self.root, width=500, height=400, background="#ffffff"
        )
        self.canvas_area.grid(row=1, column=1)

        # status bar
        self.status_frame = tk.Frame(self.root)
        self.status = tk.Label(self.status_frame, text="this is the status bar")
        self.status.pack(fill="both", expand=True)

        self.menu_left.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.some_title_frame.grid(row=0, column=1, sticky="ew")
        self.canvas_area.grid(row=1, column=1, sticky="nsew")
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.root.mainloop()


Example()
