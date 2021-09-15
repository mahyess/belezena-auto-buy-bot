import time


def close_unnecessary_dialogs_if_any(element):
    try:
        print("// closing banner if found")
        element.find_element_by_xpath("//*[@id, 'onetrust-accept-btn-handler']").click()
        print("// closed banner")
    except Exception as e:
        print(e)

    try:
        print("// closing notification dialog if found")
        element.find_element_by_xpath(
            "//*[@id, 'onesignal-slidedown-cancel-button']"
        ).click()
        print("// closed notification dialog")
    except Exception as e:
        print(e)


def wait_for_clickable_and_click(element):
    try:
        close_unnecessary_dialogs_if_any(element)

        element.click()
    except Exception as e:
        time.sleep(2)
        wait_for_clickable_and_click(element)
