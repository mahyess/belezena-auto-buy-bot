import platform
import subprocess
import time


def ping_until_up(site="www.belezanaweb.com.br"):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    while True:
        status_1 = subprocess.run(
            ["ping", param, "3", "www.belezanaweb.com.br"], capture_output=True
        )
        status_2 = subprocess.run(
            ["ping", param, "3", "www.useragentstring.com"], capture_output=True
        )
        if status_1.returncode == 0 and status_2.returncode == 0:
            return
        print("www.belezanaweb.com.br or www.useragentstring.com is down...")
        time.sleep(5)
