import datetime
import time

def quinta(driver, details):
    QUINTA_URL = (
        "https://quintadb.com/widgets/dcL8ktW4XbfRVdJSkNWRz8/a-j1RcGrrfl4obW6ZcNMyW"
    )
    driver.get(QUINTA_URL)

    driver.find_element_by_xpath(
        ".//label[contains(text(), 'CPF')]/following-sibling::input"
    ).send_keys(details["cpf"])

    driver.find_element_by_xpath(
        ".//label[contains(text(), 'Email')]/following-sibling::input"
    ).send_keys(details["customer_email"])

    driver.find_element_by_xpath(
        ".//label[contains(text(), 'Senha')]/following-sibling::input"
    ).send_keys(details["customer_email_password"])

    driver.find_element_by_xpath(
        ".//label[contains(text(), 'Link')]/following-sibling::input"
    ).send_keys(details["meurastre_url"])
    driver.find_element_by_id("dtype_cwW7FdGI9dSikPWRRcOSkX").send_keys(Keys.ENTER)
    pyautogui.press('enter')
    driver.find_element_by_name("button").click()
    timer.sleep(2)
    driver.find_element_by_text("Enviar").click()
    driver.find_element_by_id("dtype_cwW7FdGI9dSikPWRRcOSkX").send_keys(Keys.ENTER)
    pyautogui.press('enter')
    return 0
