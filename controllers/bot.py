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


def bot(root, details):
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
    options.add_argument(f"user-agent={random_user_agent(root)}")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(8)
    try:
        print("start bot...")
        # go to item details page
        driver.get(details["link"])
        print("https" in driver.current_url)

        # driver.get(item_url)
        if len(driver.find_elements_by_class_name("banner-close-button")):
            wait_for_clickable_and_click(
                driver.find_element_by_class_name("banner-close-button")
            )
        if len(driver.find_elements_by_xpath("//button[contains(text(), 'Avise-me')]")):
            return "Out of Stock", False

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
        try:
            Select(
                driver.find_element_by_css_selector(
                    f"select[data-cy='SelectItem'][name='{item_sku}']"
                )
            ).select_by_value(f"{details['quantity']}")
        except Exception as e:
            return "Out of stock", False

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
            return "already registered.", False
            driver.find_element_by_id("password").send_keys(
                details["customer_email_password"]
            )
            driver.find_element_by_id("password").send_keys(Keys.ENTER)
            if len(driver.find_elements_by_css_selector("div[data-cy='dangerToast']")):
                return "Incorrent password", False
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

        def read_cards_and_enter(root, driver):
            with open(CARD_FILE, "r", newline="") as csv_file:
                file_reader = csv.DictReader(
                    csv_file,
                    delimiter=",",
                )
                for line_count, data in enumerate(file_reader):
                    try:
                        # if len(driver.find_elements_by_class_name("toast-close")):
                        #     wait_for_clickable_and_click(
                        #         driver.find_element_by_class_name("toast-close")
                        #     )
                        if len(
                            driver.find_elements_by_css_selector(
                                "label[for='super-express']"
                            )
                        ):
                            wait_for_clickable_and_click(
                                driver.find_element_by_css_selector(
                                    "label[for='super-express']"
                                )
                            )

                        number_input = driver.find_element_by_id("number")
                        number_input.send_keys(Keys.CONTROL, "a")
                        number_input.send_keys(data["number"])
                        holder_name_input = driver.find_element_by_id("holderName")
                        holder_name_input.send_keys(Keys.CONTROL, "a")
                        holder_name_input.send_keys(data["holder_name"])
                        Select(
                            driver.find_element_by_id("expiryMonth")
                        ).select_by_value(f"{data['expiry_month']}")
                        Select(driver.find_element_by_id("expiryYear")).select_by_value(
                            f"{data['expiry_year']}"
                        )
                        cvc_input = driver.find_element_by_id("cvc")
                        cvc_input.send_keys(Keys.CONTROL, "a")
                        cvc_input.send_keys(f"{data['cvc']}")
                        Select(
                            driver.find_element_by_id("installment")
                        ).select_by_value("1")

                        # before_proceed_url = driver.current_url
                        driver.find_element_by_css_selector(
                            "label[for='BOLETO']"
                        ).click()

                        wait_for_clickable_and_click(
                            driver.find_element_by_css_selector(
                                "button[data-cy='ProceedSuccess']"
                            )
                        )
                        # if order number is found, it means the order is complete
                        # if len(
                        #     driver.find_elements_by_css_selector(
                        #         "span[data-cy='OrderNumber']"
                        #     )
                        # ):
                        el = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located(
                                (By.XPATH, "//div[@class='loading is-visible']")
                            )
                        )
                        WebDriverWait(driver, 10).until(
                            lambda d: "is-visible" not in el.get_attribute("class")
                        )
                        if "transacional/sucesso" in driver.current_url:
                            order_number = driver.find_element_by_css_selector(
                                "span[data-cy='OrderNumber']"
                            ).text
                            return f"https://meurastre.io/rastreio/{order_number}", True

                        # runs if order number is not found
                        if len(
                            driver.find_elements_by_css_selector(
                                "div[data-cy='dangerLightToast']"
                            )
                        ) or len(
                            driver.find_elements_by_css_selector(
                                "div[data-cy='dangerToast']"
                            )
                        ):
                            # if recessive order error is thrown, close the bot here.
                            if len(
                                driver.find_elements_by_css_selector(
                                    "div[data-cy='dangerToast']"
                                )
                            ):
                                toast = driver.find_element_by_css_selector(
                                    "div[data-cy='dangerToast']"
                                )
                                is_excessive = len(
                                    toast.find_elements_by_xpath(
                                        "//*[contains(text(), 'excedido')]"
                                    )
                                )
                                if is_excessive:
                                    return "excess request", False

                            # if some other errors, consider card problem, change card and try again
                            card_file_updater(data)
                            print("Card removed")
                            root.refresh_ui()

                        # refresh the page
                        driver.get(driver.current_url)

                    except Exception as e:
                        return "system error", False

            # reach here, if every card is used up
            # prompt to add more cards
            _ = ui.custom_dialogs.load_more_credit_card(root)
            # repeat the process until return is True
            read_cards_and_enter(root, driver)

        remarks, success = read_cards_and_enter(root, driver)
        return remarks, success

    except Exception as e:
        print(e)
        return "system error", False

    finally:
        driver.quit()
