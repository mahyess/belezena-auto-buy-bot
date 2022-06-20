import datetime
import time

def quinta(driver, details):
    QUINTA_URL = (
        "https://form.jotform.com/221671104177046"
    )
    driver.get(QUINTA_URL)

    driver.find_element_by_id(
        "input_3"
    ).send_keys(details["cpf"])

    driver.find_element_by_id(
        "input_4"
    ).send_keys(details["customer_email"])

    driver.find_element_by_id(
        "input_5"
    ).send_keys(details["customer_email_password"])

    driver.find_element_by_id(
        "input_6"
    ).send_keys(details["meurastre_url"])
    timer.sleep(1)
    driver.find_element_by_id("input_2").send_keys(Keys.ENTER)
    
   
    timer.sleep(3)
    


    
    return 0
