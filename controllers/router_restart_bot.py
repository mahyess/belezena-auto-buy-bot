import time
from selenium import webdriver

from selenium.webdriver.chrome.options import Options


def router_restart():
    options = Options()
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    try:
        driver.get("http://192.168.15.1/cgi-bin/device-management-resets.cgi")
        if not len(driver.find_elements_by_xpath('//button[text()="Logout"]')):
            driver.find_element_by_id("Loginuser").send_keys("admin")
            driver.find_element_by_id("LoginPassword").send_keys("5e65a942")
            driver.find_element_by_id("acceptLogin").click()
        driver.find_element_by_xpath("//a[.//*[text()='REBOOT']]").click()
        driver.find_element_by_xpath("//a[.//span[text()='Yes, Reboot']]").click()
        time.sleep(90)

    except Exception as e:
        print(e)
        raise e

    finally:
        driver.quit()
