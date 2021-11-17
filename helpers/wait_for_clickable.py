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
    try_count = 0
    while try_count < 20:
        try:
            try_count += 1
            if driver:
                close_unnecessary_dialogs_if_any(driver)

            # ------- scrolling to proper position ---------
            desired_y = (element.size['height'] / 2) + element.location['y']
            current_y = (driver.execute_script('return window.innerHeight') / 2) + driver.execute_script('return window.pageYOffset')
            scroll_y_by = desired_y - current_y
            driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)
            # ------- scrolling to proper position ---------
            
            driver.execute_script("arguments[0].click();", element)

            break

        except Exception as e:
            print(f"try_count: {try_count} ", e)
            time.sleep(2)
