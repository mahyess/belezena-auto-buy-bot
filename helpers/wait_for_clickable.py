import time


def close_unnecessary_dialogs_if_any(driver):
    driver.implicitly_wait(0)

    try:
        print("// closing banner if found")
        driver.find_element_by_xpath("//*[@id='onetrust-accept-btn-handler']").click()
        print("// closed banner")
    except Exception as e:
        # print(e)
        pass

    try:
        print("// closing notification dialog if found")
        driver.find_element_by_xpath(
            "//*[@id='onesignal-slidedown-cancel-button']"
        ).click()
        print("// closed notification dialog")
    except Exception as e:
        # print(e)
        pass

    driver.implicitly_wait(10)


def wait_for_clickable_and_click(element, driver=None):
    try:
        if driver:
            close_unnecessary_dialogs_if_any(driver)

        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        print(e)
        time.sleep(2)
        wait_for_clickable_and_click(element)
