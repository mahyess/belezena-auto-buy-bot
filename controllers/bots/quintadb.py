import datetime


def quinta(driver, details):
    QUINTA_URL = (
        "https://quintadb.com/widgets/bVWQ_cUrjckPZcIKfnB1jG/bfxtxcHmjiW4TlW67cISkK"
    )
    driver.get(QUINTA_URL)

    driver.find_element_by_xpath(
        ".//label[contains(text(), 'Nome')]/following-sibling::input"
    ).send_keys(f'{details["customer_first_name"]} {details["customer_last_name"]}')

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
        ".//label[contains(text(), 'Site')]/following-sibling::input"
    ).send_keys(details["site"])

    driver.find_element_by_xpath(
        ".//label[contains(text(), 'Url')]/following-sibling::input"
    ).send_keys(details["meurastre_url"])

    driver.find_element_by_xpath(
        ".//label[contains(text(), 'Data e Hora')]/following-sibling::input"
    ).send_keys(datetime.now())

    driver.find_element_by_css_selector("input[type='submit']").click()

    return 0
