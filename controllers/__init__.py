from controllers.router_restart_bot import router_restart
import csv, os
from helpers.ping_checker import ping_until_up
import threading
from helpers.file_system import FEEDING_FILE, PLATFORM
from controllers.bot import bot
from helpers.csv_reader import is_empty_csv, FEEDER_FILE_FIELDNAMES, updater


def ui_refresher(func):
    def wrapper(root, *args):
        func(root, *args)
        root.refresh_ui()

    return wrapper


@ui_refresher
def load_data(root):
    filename = root.onOpen()

    with open(filename, "r", newline="") as input_file, open(
        FEEDING_FILE, "a", newline=""
    ) as save_file:
        file_reader = csv.DictReader(input_file, delimiter=",")
        file_writer = csv.DictWriter(
            save_file, delimiter=",", fieldnames=FEEDER_FILE_FIELDNAMES
        )

        for line_count, row in enumerate(file_reader):
            file_writer.writerow(row)

    root.show_message_box("Successful", f"{line_count+1} Data Imported")


@ui_refresher
def load_credit_card(root):
    print("load_credit_card")


@ui_refresher
def auto_buy(root):
    root.status = 1
    if not os.path.isfile(FEEDING_FILE) or is_empty_csv(FEEDING_FILE):
        root.show_message_box("Failed", f"No data imported", "Warning")
        return

    with open(FEEDING_FILE, "r", newline="") as csv_file:
        file_reader = csv.DictReader(
            csv_file,
            delimiter=",",
        )
        for line_count, row in enumerate(file_reader):
            try:
                if root.status == 0:
                    break
                router_restart()
                ping_until_up()
                order_link = bot(row)
                updater(row, order_link)
            except Exception as e:
                print(e)
                updater(row)


@ui_refresher
def pause(root):
    root.status = 0


@ui_refresher
def clear(root):
    print("clear")


@ui_refresher
def save(root):
    print("save")
