import json
import os
import csv
import platform
from pathlib import Path


PLATFORM = ""
if platform.system().startswith("Linux"):
    PLATFORM = "Linux"
elif platform.system().startswith("Win"):
    PLATFORM = "Windows"
else:
    raise RuntimeError("Only linux and Windows are supported")


if not os.path.exists(str(Path.home()) + "/.autobuy"):
    os.makedirs(str(Path.home()) + "/.autobuy")

FEEDING_FILE = str(Path.home()) + "/.autobuy/feeder.csv"
ERROR_FILE = str(Path.home()) + "/.autobuy/error.csv"
COMPLETED_FILE = str(Path.home()) + "/.autobuy/completed.csv"
CARD_FILE = str(Path.home()) + "/.autobuy/card.csv"
CREDS_FILE = str(Path.home()) + "/.autobuy/creds.json"
MSG_FILE = str(Path.home()) + "/.autobuy/msg.txt"


FIELDNAMES = [
    "order_number",
    "name",
    "quantity",
    "customer_first_name",
    "customer_last_name",
    "customer_email",
    "customer_email_password",
    "birthdate",
    "gender",
    "cpf",
    "cep",
    "telephone",
    "address_label",
    "street_address",
    "district",
    "reference_point",
    "number",
    "complement",
]


def file_initializer(filename, fieldnames=FIELDNAMES):
    is_file_exists = os.path.isfile(filename)
    if not is_file_exists:
        with open(filename, "a", newline="") as save_file:
            if "completed" in filename or "error" in filename:
                fieldnames = [*fieldnames, "remarks"]
            file_writer = csv.DictWriter(
                save_file, delimiter=",", fieldnames=fieldnames
            )

            file_writer.writeheader()


file_initializer(FEEDING_FILE)
file_initializer(ERROR_FILE)
file_initializer(COMPLETED_FILE)
file_initializer(CARD_FILE, ["number", "expiry_month", "expiry_year", "cvc"])

# for creds file
is_file_exists = os.path.isfile(CREDS_FILE)
if not is_file_exists:
    with open(CREDS_FILE, "w") as save_file:
        save_file.write(
            json.dumps(
                {
                    "email": "",
                    "operador": "",
                    "password": "",
                    "quantity": 5,
                    "price": 0,
                },
                indent=4,
            )
        )
