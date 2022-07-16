import json

from helpers.file_system import CREDS_FILE


def get_creds():
    with open(CREDS_FILE, "r") as f:
        return json.load(f)
