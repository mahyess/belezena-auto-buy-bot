from controllers.router_restart_bot import router_restart
import csv, os
from helpers.ping_checker import ping_until_up
from helpers.file_system import (
    CARD_FILE,
    COMPLETED_FILE,
    ERROR_FILE,
    FEEDING_FILE,
    file_initializer,
)
import controllers.bot as botfile
from helpers.csv_reader import (
    CARD_FILE_FIELDNAMES,
    get_lines_count,
    is_empty_csv,
    FEEDER_FILE_FIELDNAMES,
    updater,
)


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
    filename = root.onOpen()

    with open(filename, "r", newline="") as input_file, open(
        CARD_FILE, "a", newline=""
    ) as save_file:
        file_reader = csv.DictReader(input_file, delimiter=",")
        file_writer = csv.DictWriter(
            save_file, delimiter=",", fieldnames=CARD_FILE_FIELDNAMES
        )

        for line_count, row in enumerate(file_reader):
            file_writer.writerow(row)

    root.show_message_box("Successful", f"{line_count+1} Data Imported")


@ui_refresher
def auto_buy(root):
    root.status = 1
    root.refresh_ui()

    if not os.path.isfile(FEEDING_FILE) or is_empty_csv(FEEDING_FILE):
        root.show_message_box("Failed", f"No data imported", "Warning")
        root.status = 0
        root.refresh_ui()
        return

    with open(FEEDING_FILE, "r", newline="") as csv_file:
        file_reader = csv.DictReader(
            csv_file,
            delimiter=",",
        )
        for line_count, row in enumerate(file_reader):
            try:
                if not get_lines_count(CARD_FILE):
                    root.show_message_box(
                        "Failed", f"You need to use new cards", "Warning"
                    )
                    root.status = 0
                    root.refresh_ui()
                    return
                if root.status == 0:
                    break
                # router_restart()
                # ping_until_up(root)
                remarks, success = botfile.bot(root, row)
                print(remarks, success)
                updater(row, remarks, success)
            except Exception as e:
                updater(row, "system error", False)
            finally:
                root.refresh_ui()
        root.status = 0


@ui_refresher
def pause(root):
    root.status = 0


@ui_refresher
def clear(root):
    result = root.show_message_box(
        "Clear",
        "Are you sure? This will clear all data you cannot recover.",
        "question",
    )
    if result:
        os.remove(FEEDING_FILE)
        os.remove(ERROR_FILE)
        os.remove(COMPLETED_FILE)
        file_initializer(FEEDING_FILE)
        file_initializer(ERROR_FILE)
        file_initializer(COMPLETED_FILE)
        root.refresh_ui()


@ui_refresher
def clear_credit(root):
    result = root.show_message_box(
        "Clear Credit",
        "Are you sure? This will clear credit data you cannot recover.",
        "question",
    )
    if result:
        os.remove(CARD_FILE)
        file_initializer(
            CARD_FILE, ["number", "holder_name", "expiry_month", "expiry_year", "cvc"]
        )
        root.refresh_ui()


@ui_refresher
def save(root):
    root.show_message_box(
        "Save",
        "This button doesn't do anything.",
    )
