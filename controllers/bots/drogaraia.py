import csv

from selenium.webdriver.support.wait import WebDriverWait
import ui.custom_dialogs

from helpers.csv_reader import card_file_updater
from helpers.file_system import CARD_FILE
from helpers.wait_for_clickable import wait_for_clickable_and_click
from helpers.user_agent import random_user_agent
import time
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys


def bot(root, details, driver=None):
    gender_dict = {
        "M": "gender-input-1",
        "F": "gender-input-2",
    }
    # address_label = "casa"
    address_type_dict = {
        "casa": "HOME",
        "apartamento": "APARTMENT",
        "caixa postal": "POST_OFFICE_BOX",
        "condomínio": "CONDOMINIUM",
        "comercial": "BUSINESS",
        "rural": "RURAL",
        "outro": "OTHER",
    }
    using_param_driver = False
    if not driver:
        options = Options()
        options.add_argument(f"user-agent={random_user_agent(root)}")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(8)
    else:
        using_param_driver = True

    try:
        print("start bot...")
        # go to item details page
        product_name = details["name"]
        driver.get(f"https://busca.drogaraia.com.br/search?w={product_name}")
        
        wait_for_clickable_and_click(
            driver.find_element_by_xpath(
                f"//a[contains(@class, 'product-image') and .//img[contains(translate(@alt, '{product_name.upper()}', '{product_name.lower()}'), '{product_name.lower()}')]]"
            ),
            driver,
        )

        if len(driver.find_elements_by_xpath("//button[contains(text(), 'Avise-me')]")):
            return "Out of Stock", False

        driver.find_element_by_id("qty").send_keys(details["quantity"])

        loading_div = driver.find_element_by_id("addtocart_popup")
        # click on buy button
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button[title^='Comprar']")
        )

        WebDriverWait(driver, 30).until(
            lambda d: "no-display" not in loading_div.get_attribute("class")
        )
        WebDriverWait(driver, 30).until(
            lambda d: "no-display" in loading_div.get_attribute("class")
        )

        driver.get("https://www.drogaraia.com.br/checkout/cart/")

        driver.find_element_by_id("postcode").send_keys(details["cep"])
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button.btn-more[title='OK']"), driver
        )

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "co-shipping-method-form"))
        )

        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button.btn-proceed-checkout"), driver
        )
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button[title='Cadastre-se']"), driver
        )

        # email in login form
        driver.find_element_by_id("full-name-input").send_keys(f'{details["customer_first_name"]} {details["customer_last_name"]}')
        driver.find_element_by_id("email_address").send_keys(details["customer_email"])
        driver.find_element_by_id("taxvat").send_keys(details["cpf"])
        driver.find_element_by_id("telephone").send_keys(details["telephone"])
        driver.find_element_by_id("password").send_keys(details["customer_email_password"])
        driver.find_element_by_id("confirmation").send_keys(details["customer_email_password"])
        driver.find_element_by_id("dob-date").send_keys(details["birthDate"])
        gender_value = gender_dict[details["gender"]]
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector(f"label[for='{gender_value}']"),
            driver,
        )
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("label[for='lgpd-acceptance-yes']"),
            driver,
        )

        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button[title='register']"), driver
        )

    except Exception as e:
        print(e)
        return "system error", False

    finally:
        if not using_param_driver:
            driver.quit()
