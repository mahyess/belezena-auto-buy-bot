import time


def wait_for_clickable_and_click(element):
    try:
        element.click()
    except Exception as e:
        print(e)
        time.sleep(2)
        wait_for_clickable_and_click(element)
