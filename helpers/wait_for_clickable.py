import time


def wait_for_clickable_and_click(element):
    try:
        try:
            element.find_element_by_xpath(
                "//*[contains(@class, 'banner-close-button')"
            ).click()
        except:
            pass

        element.click()
    except Exception as e:
        time.sleep(2)
        wait_for_clickable_and_click(element)
