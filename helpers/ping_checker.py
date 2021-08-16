import subprocess
import time


def ping_until_up(site="www.google.com"):
    while True:
        status = subprocess.run(["ping", "-c", "3", site], capture_output=True)
        if status.returncode == 0:
            return
        print(f"{site} is down...")
        time.sleep(5)
