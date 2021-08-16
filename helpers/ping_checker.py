import platform
import subprocess
import time


def ping_until_up(site="www.google.com"):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    while True:
        status = subprocess.run(["ping", param, "3", site], capture_output=True)
        if status.returncode == 0:
            return
        print(f"{site} is down...")
        time.sleep(5)
