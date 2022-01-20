from selenium.webdriver.support.wait import WebDriverWait


def mt_wait_for_loader(driver, statements):
    waiter = WebDriverWait(driver, 10)
    spinner = driver.find_element_by_css_selector("div.dialog-aguarde")
    print(statements)
    try:
        statements()
    except Exception as e:
        print(e)
    waiter.until(lambda _: "false" in spinner.get_attribute("aria-hidden"))
    waiter.until(lambda _: "true" in spinner.get_attribute("aria-hidden"))
