import time
from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys


def router_restart(details):

    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    try:
        driver.get("192.168.15.1")
        driver.find_element_by_id("Loginuser").send_keys("admin")
        driver.find_element_by_id("LoginPassword").send_keys("5e65a942")
        driver.find_element_by_id("acceptLogin").click()
        driver.find_element_by_id("MLG_Resets_Reboot").click()
        driver.find_element_by_id("MLG_Pop_Reboot_Yes").click()
        time.sleep(90)

    except Exception as e:
        print(e)
        raise e

    finally:
        driver.quit()
