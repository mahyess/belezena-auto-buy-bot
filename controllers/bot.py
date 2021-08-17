import csv
from helpers.csv_reader import card_file_updater
from helpers.file_system import CARD_FILE
from helpers.wait_for_clickable import wait_for_clickable_and_click
from selenium.webdriver.support.wait import WebDriverWait
from helpers.user_agent import random_user_agent
import platform
import time
from tkinter import Tk
from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def bot(details, error=None):
    retry = 0
    if retry > 1:
        raise error

    gender_dict = {
        "F": "female",
        "M": "male",
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

    options = Options()
    options.add_argument(f"user-agent={random_user_agent()}")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    try:
        print("start bot...")
        # go to item details page
        driver.get(details["link"])
        # driver.get(item_url)
        if len(driver.find_elements_by_class_name("banner-close-button")):
            wait_for_clickable_and_click(
                driver.find_element_by_class_name("banner-close-button")
            )

        # get item sku
        item_sku = driver.find_element_by_xpath(
            "//meta[@property='product:retailer_item_id']"
        ).get_attribute("content")

        # get item checkout link and go to the link
        buy_btn = driver.find_element_by_css_selector(
            "a[href^='https://checkout.belezanaweb.com.br/sacola?skus=']"
        )
        print("...goto product checkout")
        driver.get(buy_btn.get_attribute("href"))

        # enter cep_address code
        driver.find_element_by_id("postalCode").send_keys(details["cep"])

        # get quantity select dropdown and select desired value
        Select(
            driver.find_element_by_css_selector(
                f"select[data-cy='SelectItem'][name='{item_sku}']"
            )
        ).select_by_value(f"{details['quantity']}")

        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("a[data-cy='ProceedCheckout']")
        )

        # email in login form
        driver.find_element_by_id("email").send_keys(details["customer_email"])

        print("...login email form")
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button[type='submit']")
        )

        # if already signed up
        if len(driver.find_elements_by_css_selector("button[data-cy='RegisterUser']")):
            driver.find_element_by_id("givenName").send_keys(
                details["customer_first_name"]
            )
            driver.find_element_by_id("familyName").send_keys(
                details["customer_last_name"]
            )
            driver.find_element_by_id("cpf").send_keys(details["cpf"])
            driver.find_element_by_id("birthDate").send_keys(
                details["birthdate"].replace("/", "")
            )
            driver.find_element_by_id("telephone").send_keys(details["telephone"])
            driver.find_element_by_id("password").send_keys(
                details["customer_email_password"]
            )
            gender_value = gender_dict[details["gender"]]
            wait_for_clickable_and_click(
                driver.find_element_by_css_selector(f"label[for='{gender_value}']")
            )

            # submit register form
            driver.find_element_by_id("password").send_keys(Keys.ENTER)
            print("...complete signup")
            # the step below has some issue, so the above statement is workaround.
            # driver.find_element_by_css_selector("button[data-cy='RegisterUser']").click()
        else:
            driver.find_element_by_id("password").send_keys(
                details["customer_email_password"]
            )
            driver.find_element_by_id("password").send_keys(Keys.ENTER)
            print("...complete login")

        # sacola form complete

        # endereco form start
        # if current address label is already saved
        address_label = details["address_label"]
        if len(driver.find_elements_by_xpath(f"//span[.='{address_label}']")):
            address_card = driver.find_element_by_xpath(
                # f"//li[./label/span.='{address_label}']"
                f"//li[.//*[text()='{address_label}']]"
            )
            wait_for_clickable_and_click(address_card)
            wait_for_clickable_and_click(
                address_card.find_element_by_xpath(".//div/button")
            )
            print("...chosen address")

        else:
            # if not saved and there is another address card, trigger new form
            if len(driver.find_elements_by_css_selector("label[for='addAddress']")):
                driver.find_element_by_css_selector("label[for='addAddress']").click()
            # this is the first one being saved, sending directly to form
            driver.find_element_by_id("label").send_keys(details["address_label"])
            driver.find_element_by_id("postalCode").send_keys(details["cep"])

            driver.find_element_by_id("streetAddress").send_keys(
                details["street_address"]
            )
            driver.find_element_by_id("district").send_keys(details["district"])
            driver.find_element_by_id("number").send_keys(details["number"])
            Select(driver.find_element_by_id("addressType")).select_by_value(
                f"{address_type_dict[details['address_label'].lower()]}"
            )
            driver.find_element_by_id("complement").send_keys(details["complement"])

            wait_for_clickable_and_click(
                driver.find_element_by_css_selector("button[type='submit']")
            )
            print("...create new address")

        # endereco form complete
        # pagamento form start

        print("...choose by ticket")
        if len(driver.find_elements_by_css_selector("label[for='super-express']")):
            wait_for_clickable_and_click(
                driver.find_element_by_css_selector("label[for='super-express']")
            )

        with open(CARD_FILE, "r", newline="") as csv_file:
            file_reader = csv.DictReader(
                csv_file,
                delimiter=",",
            )
            for line_count, data in enumerate(file_reader):
                try:
                    number_input = driver.find_element_by_id("number")
                    number_input.clear()
                    number_input.send_keys(data["number"])
                    holder_name_input = driver.find_element_by_id("holderName")
                    holder_name_input.clear()
                    holder_name_input.send_keys(data["holder_name"])
                    Select(driver.find_element_by_id("expiryMonth")).select_by_value(
                        f"{data['expiry_month']}"
                    )
                    Select(driver.find_element_by_id("expiryYear")).select_by_value(
                        f"{data['expiry_year']}"
                    )
                    cvc_input = driver.find_element_by_id("cvc")
                    cvc_input.clear()
                    cvc_input.send_keys(f"{data['cvc']}")
                    Select(driver.find_element_by_id("installment")).select_by_value(
                        "1"
                    )

                    wait_for_clickable_and_click(
                        driver.find_element_by_css_selector(
                            "button[data-cy='ProceedSuccess']"
                        )
                    )
                    time.sleep(5)

                    if len(
                        driver.find_elements_by_css_selector(
                            "div[data-cy='dangerLightToast']"
                        )
                    ):
                        card_file_updater(data)
                        continue
                    else:
                        break

                except Exception as e:
                    print(e)

        print("...success")

        # order_number = driver.find_element_by_css_selector(
        #     "span[data-cy='OrderNumber']"
        # ).text
        # print(f"Order number: {order_number}")

        # order_link = f"https://meurastre.io/rastreio/{order_number}"
        # driver.get(order_link)
        print("...complete bot")

        return "order_link"

    except ValueError as e:
        retry += 1
        bot(details, error=e)

    finally:
        driver.quit()
