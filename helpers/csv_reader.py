# csv reader
# from _typeshed import NoneType
import csv
from helpers.file_system import CARD_FILE, COMPLETED_FILE, ERROR_FILE, FEEDING_FILE

FEEDER_FILE_FIELDNAMES = [
    "link",
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
CARD_FILE_FIELDNAMES = ["number", "holder_name", "expiry_month", "expiry_year", "cvc"]


def updater(completed_row: str, success_link=None):
    lines = list()
    success = list()
    failure = list()
    with open(FEEDING_FILE, "r", newline="") as read_file:
        reader = csv.DictReader(
            read_file, delimiter=",", fieldnames=FEEDER_FILE_FIELDNAMES
        )
        for row in reader:
            if row != completed_row:
                lines.append(row)
            else:
                if success_link:
                    row["success_link"] = success_link
                    success.append(row)
                else:
                    failure.append(row)

    with open(FEEDING_FILE, "w", newline="") as write_file:
        writer = csv.DictWriter(
            write_file, delimiter=",", fieldnames=FEEDER_FILE_FIELDNAMES
        )
        writer.writerows(lines)

    with open(COMPLETED_FILE, "a", newline="") as write_file:
        writer = csv.DictWriter(
            write_file,
            delimiter=",",
            fieldnames=[*FEEDER_FILE_FIELDNAMES, "success_link"],
        )
        writer.writerows(success)

    with open(ERROR_FILE, "a", newline="") as write_file:
        writer = csv.DictWriter(
            write_file,
            delimiter=",",
            fieldnames=FEEDER_FILE_FIELDNAMES,
        )
        writer.writerows(failure)

    return


def card_file_updater(completed_row: str):
    lines = list()
    with open(CARD_FILE, "r", newline="") as read_file:
        reader = csv.DictReader(
            read_file, delimiter=",", fieldnames=CARD_FILE_FIELDNAMES
        )
        for row in reader:
            if row != completed_row:
                lines.append(row)

    with open(CARD_FILE, "w", newline="") as write_file:
        writer = csv.DictWriter(
            write_file, delimiter=",", fieldnames=CARD_FILE_FIELDNAMES
        )
        writer.writerows(lines)


def is_empty_csv(filename):
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for i, _ in enumerate(reader):
            if i:  # found the second row
                return False
    return True


def get_lines_count(filename):
    with open(filename, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        return len(list(reader)) - 1
