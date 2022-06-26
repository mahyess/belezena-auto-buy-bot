from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def quinta(driver, details):
    driver.get("https://form.jotform.com/221671104177046")
    driver.find_element_by_id("input_3").send_keys(details["cpf"])
    driver.find_element_by_id("input_4").send_keys(details["customer_email"])
    driver.find_element_by_id("input_5").send_keys(details["customer_email_password"])
    driver.find_element_by_id("input_6").send_keys(details["meurastre_url"], Keys.ENTER)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "thankyou"))
    )
    return
