import platform
import subprocess
import time

import os

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = os.open(os.devnull, os.O_RDWR)


def ping_until_up(root=None, site="www.belezanaweb.com.br", to_return=False):
    count = 0
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        while True:
            status_1 = (
                subprocess.call(["ping", param, "3", "www.belezanaweb.com.br"]) == 0
            )
            status_2 = (
                subprocess.call(["ping", param, "3", "app.mercadoturbo.com.br"]) == 0
            )
            count += 1
            if status_1 and status_2:
                return True
            if to_return and count > 10:
                return False
                
            print("www.belezanaweb.com.br or app.mercadoturbo.com.br is down...")
            time.sleep(5)
    except Exception as e:
        if root:
            root.show_message_box("from ping until up", e, "warning")
        else:
            print(e)
