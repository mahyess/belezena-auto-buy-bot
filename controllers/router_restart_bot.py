import time
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def router_restart():
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    try:
        driver.get("http://192.168.15.1/cgi-bin/device-management-resets.cgi")
        # if not len(driver.find_elements_by_xpath('//button[text()="Logout"]')):
        driver.find_element_by_id("Loginuser").send_keys("admin")
        driver.find_element_by_id("LoginPassword").send_keys("5e65a942")
        driver.find_element_by_id("acceptLogin").click()

        WebDriverWait(driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "basefrm"))
        )
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[.//span[@id='MLG_Resets_Reboot']]",
                )
            )
        ).click()
        WebDriverWait(driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.CLASS_NAME, "fancybox-iframe")
            )
        )
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "//a[.//span[@id='MLG_Pop_Reboot_Yes']]",
                )
            )
        ).click()

        time.sleep(90)

    except Exception as e:
        print(e)
        raise e

    finally:
        driver.quit()
