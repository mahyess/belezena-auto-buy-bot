from selenium.webdriver.support.wait import WebDriverWait


def mt_wait_for_loader(driver, statements):
    waiter = WebDriverWait(driver, 10)
    spinner = driver.find_element_by_css_selector("div.dialog-aguarde")
    statements()
    waiter.until(lambda: "false" in spinner.get_attribute("aria-hidden"))
    waiter.until(lambda: "true" in spinner.get_attribute("aria-hidden"))
