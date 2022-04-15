import json
from helpers.ui_refresher import ui_refresher
from controllers.router_restart_bot import router_restart
import csv, os
from helpers.ping_checker import ping_until_up
from helpers.file_system import (
    CARD_FILE,
    COMPLETED_FILE,
    CREDS_FILE,
    ERROR_FILE,
    FEEDING_FILE,
    file_initializer,
)
import controllers.bots.update_beleza_stock as update_bot
import controllers.get_data_bot as get_data_bot_file
from helpers.csv_reader import (
    CARD_FILE_FIELDNAMES,
    get_lines_count,
    is_empty_csv,
    FEEDER_FILE_FIELDNAMES,
    updater,
)


@ui_refresher
def load_data(root):
    update_bot.bot(root)
    root.show_message_box("Successful", "Done.")
    # filename = root.onOpen()
    # try:
    #     with open(filename, "r", newline="") as input_file, open(
    #         FEEDING_FILE, "a", newline=""
    #     ) as save_file:
    #         file_reader = csv.DictReader(input_file, delimiter=",")
    #         file_writer = csv.DictWriter(
    #             save_file, delimiter=",", fieldnames=FEEDER_FILE_FIELDNAMES
    #         )

    #         for line_count, row in enumerate(file_reader):
    #             file_writer.writerow(row)

    #     root.show_message_box("Successful", f"{line_count+1} Data Imported")
    # except ValueError:
    #     root.show_message_box("Error", "Invalid File Headers", "warning")


@ui_refresher
def load_credit_card(root):
    filename = root.onOpen()
    try:
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
    except ValueError:
        root.show_message_box("Error", "Invalid File Headers", "warning")


@ui_refresher
def auto_buy(root):
    get_data_bot_file.bot(root)


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
        file_initializer(CARD_FILE, ["number", "expiry_month", "expiry_year", "cvc"])
        root.refresh_ui()


@ui_refresher
def save_creds(root):
    creds = {}
    creds["email"] = root.email_field.get()
    creds["operador"] = root.operador_field.get()
    creds["password"] = root.password_field.get()
    creds["quantity"] = root.quantity_field.get()
    creds["price"] = root.price_field.get()
    print(creds)

    with open(CREDS_FILE, "w") as save_file:
        save_file.write(json.dumps(creds, indent=4))

    root.show_message_box(
        "Save",
        "Saved.",
    )
