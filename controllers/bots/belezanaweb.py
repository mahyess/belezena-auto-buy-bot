import csv
from datetime import datetime

from selenium.webdriver.support.wait import WebDriverWait
from controllers.bots.quintadb import quinta
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
    using_param_driver = False
    if not driver:
        options = Options()
        options.add_argument(f"user-agent={random_user_agent(root)}")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(25)
    else:
        using_param_driver = True

    try:
        print("start bot...")
        # go to item details page
        product_name = details["name"]
        driver.get(f"https://www.belezanaweb.com.br/busca?q={product_name}")
        # product_cards = driver.find_elements_by_class_name("showcase-item-image")
        # for product in product_cards:
        #     if product_name.lower() in product.get_attribute("innerHTML").lower():
        #         product.click()
        #         break
        product = None
        while not product:
            products = driver.find_elements_by_xpath(
                f"//a[contains(@class, 'showcase-item-image') and .//img[contains(translate(@alt, '{product_name.upper()}', '{product_name.lower()}'), '{product_name.lower()}')]]"
            )
            if len(products):
                product = products[0]
            else:
                # load_more_btns = driver.find_elements_by_css_selector(
                #     "button.btn-load-more"
                # )
                # if len(load_more_btns):
                #     wait_for_clickable_and_click(load_more_btns[0], driver)
                # else:
                #     return f"Out of Stock - {str(datetime.today().date())}", False
                return f"Out of Stock - {str(datetime.today().date())}", False

        wait_for_clickable_and_click(
            product,
            driver,
        )

        # # driver.get(item_url)
        # if len(driver.find_elements_by_class_name("banner-close-button")):
        #     wait_for_clickable_and_click(
        #         driver.find_element_by_class_name("banner-close-button")
        #     )
        if len(driver.find_elements_by_xpath("//button[contains(text(), 'Avise-me')]")):
            return f"Out of Stock - {str(datetime.today().date())}", False

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
        # driver.find_element_by_id("postalCode").send_keys(details["cep"])

        # get quantity select dropdown and select desired value
        try:
            Select(
                driver.find_element_by_css_selector(
                    f"select[data-cy='SelectItem'][name='{item_sku}']"
                )
            ).select_by_value(f"{details['quantity']}")
        except Exception as e:
            return "Not enough quantity", False

        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("a[data-cy='ProceedCheckout']"), driver
        )

        # email in login form
        driver.find_element_by_id("email").send_keys(details["customer_email"])

        print("...login email form")
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button[type='submit']"), driver
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
                driver.find_element_by_css_selector(f"label[for='{gender_value}']"),
                driver,
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
        # if len(driver.find_elements_by_xpath(f"//span[.='{address_label}']")):
        #     address_card = driver.find_element_by_xpath(
        #         # f"//li[./label/span.='{address_label}']"
        #         f"//li[.//*[text()='{address_label}']]"
        #     )
        #     wait_for_clickable_and_click(address_card)
        #     wait_for_clickable_and_click(
        #         address_card.find_element_by_xpath(".//div/button")
        #     )
        #     print("...chosen address")

        # else:
        # if not saved and there is another address card, trigger new form
        # if len(driver.find_elements_by_css_selector("label[for='addAddress']")):
        #    driver.find_element_by_css_selector("label[for='addAddress']").click()
        # this is the first one being saved, sending directly to form
        driver.find_element_by_id("label").send_keys(details["address_label"])
        driver.find_element_by_id("postalCode").send_keys(details["cep"])

        driver.find_element_by_id("streetAddress").send_keys(details["street_address"])
        driver.find_element_by_id("district").send_keys(details["district"])
        driver.find_element_by_id("number").send_keys(details["number"])
        Select(driver.find_element_by_id("addressType")).select_by_value(
            f"{address_type_dict[details['address_label'].lower()]}"
        )
        driver.find_element_by_id("complement").send_keys(details["complement"])

        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button[type='submit']"), driver
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
                        wait_for_clickable_and_click(
                            # driver.find_element_by_xpath(
                            #     "//div[.//*[contains(@name, 'shipping')]][1]/label"
                            # ),
                            driver.find_element_by_css_selector(
                                "div[data-cy='RadioCard']"
                            ),
                            driver,
                        )

                        # card number
                        iframe = driver.find_element_by_css_selector(
                            "span[data-cse='encryptedCardNumber']"
                        ).find_element_by_css_selector("iframe")
                        driver.switch_to.frame(iframe)
                        number_input = driver.find_element_by_id("encryptedCardNumber")
                        number_input.send_keys(Keys.CONTROL, "a")
                        number_input.send_keys(data["number"])
                        driver.switch_to.default_content()

                        # expiry date
                        iframe = driver.find_element_by_css_selector(
                            "span[data-cse='encryptedExpiryDate']"
                        ).find_element_by_css_selector("iframe")
                        driver.switch_to.frame(iframe)
                        number_input = driver.find_element_by_id("encryptedExpiryDate")
                        number_input.send_keys(Keys.CONTROL, "a")
                        number_input.send_keys(data["expiry_month"])
                        number_input.send_keys(str(data["expiry_year"])[2:])
                        driver.switch_to.default_content()

                        # cvv
                        iframe = driver.find_element_by_css_selector(
                            "span[data-cse='encryptedSecurityCode']"
                        ).find_element_by_css_selector("iframe")
                        driver.switch_to.frame(iframe)
                        number_input = driver.find_element_by_id(
                            "encryptedSecurityCode"
                        )
                        number_input.send_keys(Keys.CONTROL, "a")
                        number_input.send_keys(data["cvc"])
                        driver.switch_to.default_content()

                        # name
                        holder_name_input = driver.find_element_by_id("holderName")
                        holder_name_input.send_keys(Keys.CONTROL, "a")
                        holder_name_input.send_keys(
                            f"{details['customer_first_name']} {details['customer_last_name']}"
                        )

                        Select(
                            driver.find_element_by_id("installments")
                        ).select_by_value("1")

                        # before_proceed_url = driver.current_url
                        # driver.find_element_by_css_selector(
                        #     "label[for='BOLETO']"
                        # ).click()
                        loading_div = driver.find_element_by_css_selector(
                            "div[class='loading']"
                        )

                        wait_for_clickable_and_click(
                            driver.find_element_by_css_selector(
                                "button[data-cy='ProceedSuccess']"
                            ),
                            driver,
                        )
                        # if order number is found, it means the order is complete
                        # if len(
                        #     driver.find_elements_by_css_selector(
                        #         "span[data-cy='OrderNumber']"
                        #     )
                        # ):
                        # loading_div = WebDriverWait(driver, 30).until(
                        #     EC.visibility_of_element_located(
                        #         (By.XPATH, "//div[contains(@class,'loading')")
                        #     )
                        # )
                        WebDriverWait(driver, 30).until(
                            lambda d: "is-visible" in loading_div.get_attribute("class")
                        )
                        WebDriverWait(driver, 30).until(
                            lambda d: "is-visible"
                            not in loading_div.get_attribute("class")
                        )

                        # runs if order number is not found
                        driver.implicitly_wait(5)
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
                                try:
                                    toast = driver.find_element_by_css_selector(
                                        "div[data-cy='dangerToast']"
                                    )
                                    is_excessive = len(
                                        toast.find_elements_by_xpath(
                                            "//*[contains(text(), 'excedido')]"
                                        )
                                    )
                                    if is_excessive:
                                        root.is_reset_router_check.set(True)
                                        return "excess request", False
                                except Exception as e:
                                    pass

                            # if some other errors, consider card problem, change card and try again
                            card_file_updater(data)
                            print("Card removed")
                            root.refresh_ui()

                        driver.implicitly_wait(25)
                        try:
                            time.sleep(10)
                            print(
                                "******** order is successful. page is changed probably."
                            )
                            print(f"******** page link is {driver.current_url}")
                            if "transacional/sucesso" in driver.current_url:
                                print(
                                    "******** if condition is matched. it has t/s in url."
                                )
                                # root.is_reset_router_check.set(False)

                                meurastre_url = driver.find_element_by_xpath(
                                    '//a[contains(@href,"https://meurastre.io/")]'
                                ).get_attribute("href")

                                try:
                                    quinta(
                                        driver,
                                        {
                                            **details,
                                            "site": "belezanaweb",
                                            "meurastre_url": meurastre_url,
                                        },
                                    )
                                except Exception as e:
                                    pass

                                # getting this link is enough, so return here.. other code can stay here, doesn't matter
                                return (
                                    meurastre_url,
                                    True,
                                )

                                print("******** trying to click on meurastre link.")
                                wait_for_clickable_and_click(
                                    driver.find_element_by_xpath(
                                        '//a[contains(@href,"https://meurastre.io/")]'
                                    ),
                                    driver,
                                )
                                print("******** meurastre page is opened.")
                                driver.find_element_by_css_selector(
                                    "input[type='email']"
                                ).send_keys(details["customer_email"])
                                print("******** enter email.")
                                driver.find_element_by_css_selector(
                                    "input[type='email']"
                                ).send_keys(Keys.ENTER)
                                print("******** button click.")
                                time.sleep(2)

                                print("******** return successfully.")
                                return driver.current_url, True
                        except Exception as e:
                            return f"Sucess but {e}", True

                        # refresh the page
                        driver.get(driver.current_url)

                    except Exception as e:
                        print(e)
                        return f"Out of Stock - {str(datetime.today().date())}", False

            # reach here, if every card is used up
            # prompt to add more cards
            _ = ui.custom_dialogs.load_more_credit_card(root)
            # repeat the process until return is True
            return read_cards_and_enter(root, driver)

        remarks, success = read_cards_and_enter(root, driver)
        return remarks, success

    except Exception as e:
        print(e)
        return "system error", False

    finally:
        if not using_param_driver:
            driver.quit()
