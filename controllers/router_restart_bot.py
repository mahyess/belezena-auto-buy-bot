from selenium.webdriver.common.keys import Keys
from helpers.wait_for_clickable import wait_for_clickable_and_click
import time, socket
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_router_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
        IP = IP.split(".")
        IP[-1] = "1"
        IP = ".".join(IP)
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def router_restart(root):
    router_ip = get_router_ip()
    if router_ip not in ["192.168.15.1", "192.168.1.1"]:
        router_ip = root.router_ip.get()
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    try:
        if router_ip == "192.168.15.1":
            driver.get("http://192.168.15.1/cgi-bin/device-management-resets.cgi")
            driver.find_element_by_id("Loginuser").send_keys("admin")
            driver.find_element_by_id("LoginPassword").send_keys("Cavalo123")
            driver.find_element_by_id("acceptLogin").click()

            WebDriverWait(driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "basefrm"))
            )
            wait_for_clickable_and_click(
                driver.find_element_by_xpath("//a[.//span[@id='MLG_Resets_Reboot']]"),
                driver,
            )

            WebDriverWait(driver, 5).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.CLASS_NAME, "fancybox-iframe")
                )
            )
            wait_for_clickable_and_click(
                driver.find_element_by_xpath("//a[.//span[@id='MLG_Pop_Reboot_Yes']]"),
                driver,
            )

            time.sleep(90)

        elif router_ip == "192.168.1.1":
            driver.get("http://192.168.1.1/index.html#login")
            driver.find_element_by_id("txtPwd").send_keys("vivo")
            driver.find_element_by_id("txtPwd").send_keys(Keys.ENTER)
            wait_for_clickable_and_click(
                driver.find_element_by_id("h_connect_btn"), driver
            )
            time.sleep(60)
            wait_for_clickable_and_click(
                driver.find_element_by_id("h_connect_btn"), driver
            )
            time.sleep(5)

    except Exception as e:
        print(e)
        raise e

    finally:
        driver.quit()
