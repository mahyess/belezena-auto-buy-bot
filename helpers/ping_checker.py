import platform
import subprocess
import time

import os

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = os.open(os.devnull, os.O_RDWR)


def ping_until_up(root, site="www.belezanaweb.com.br"):
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        while True:
            status_1 = subprocess.run(
                ["ping", param, "3", "www.belezanaweb.com.br"],
                capture_output=True,
                stdin=DEVNULL,
                stderr=DEVNULL,
            )
            status_2 = subprocess.run(
                ["ping", param, "3", "www.useragentstring.com"],
                capture_output=True,
                stdin=DEVNULL,
                stderr=DEVNULL,
            )
            if status_1.returncode == 0 and status_2.returncode == 0:
                return
            print("www.belezanaweb.com.br or www.useragentstring.com is down...")
            time.sleep(5)
    except Exception as e:
        root.show_message_box("from ping until up", e, "warning")
