import datetime


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

    driver.find_element_by_css_selector("button[type='submit']").click()

    return 0
