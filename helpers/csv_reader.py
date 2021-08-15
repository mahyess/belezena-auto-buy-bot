# csv reader
# from _typeshed import NoneType
import csv
from helpers.file_system import COMPLETED_FILE, ERROR_FILE, FEEDING_FILE

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
    "number",
    "complement",
]


def updater(completed_row: str, success_link=None):
    lines = list()
    success = list()
    failure = list()
    with open(FEEDING_FILE, "r") as read_file:
        reader = csv.DictReader(
            read_file, delimiter=",", fieldnames=FEEDER_FILE_FIELDNAMES
        )
        for row in reader:
            print(row)
            print(type(row))
            if row != completed_row:
                lines.append(row)
            else:
                if success_link:
                    row["success_link"] = success_link
                    success.append(row)
                else:
                    failure.append(row)

    with open(FEEDING_FILE, "w") as write_file:
        writer = csv.DictWriter(
            write_file, delimiter=",", fieldnames=FEEDER_FILE_FIELDNAMES
        )
        writer.writerows(lines)

    with open(COMPLETED_FILE, "a") as write_file:
        writer = csv.DictWriter(
            write_file,
            delimiter=",",
            fieldnames=[*FEEDER_FILE_FIELDNAMES, "success_link"],
        )
        writer.writerows(success)

    with open(ERROR_FILE, "a") as write_file:
        writer = csv.DictWriter(
            write_file,
            delimiter=",",
            fieldnames=FEEDER_FILE_FIELDNAMES,
        )
        writer.writerows(failure)

    return


def is_empty_csv(filename):
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for i, _ in enumerate(reader):
            if i:  # found the second row
                return False
    return True


def get_lines_count(filename):
    with open(filename, "r") as csvfile:
        reader = csv.reader(csvfile)
        return len(list(reader)) - 1
