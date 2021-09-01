from helpers.ping_checker import ping_until_up
from controllers.router_restart_bot import router_restart
import re
import csv
from helpers.wait_for_clickable import wait_for_clickable_and_click

from selenium.webdriver.support.wait import WebDriverWait
import ui.custom_dialogs

from helpers.csv_reader import FEEDER_FILE_FIELDNAMES, card_file_updater, updater
from helpers.file_system import CARD_FILE, ERROR_FILE, FEEDING_FILE
from helpers.user_agent import random_user_agent
import time
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime as dt
import controllers.bot as botfile


def html_cleaner(raw_text):
    cleanr = re.compile("<.*?>")
    return re.sub(cleanr, "", raw_text)


def strip_dict(d):
    return {
        key: strip_dict(value) if isinstance(value, dict) else value.strip()
        for key, value in d.items()
    }


def bot(root):
    line_count = 0
    root.status = 1
    root.refresh_ui()

    options = Options()
    options.add_argument(f"user-agent={random_user_agent(root)}")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    try:
        driver.get("https://app.melicontrol.com.br/access/users/login")
        driver.find_element_by_id("password").send_keys("Cavalo123/")
        driver.find_element_by_id("username").send_keys("brenoml0721@gmail.com")
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button[type='submit']")
        )

        driver.get("https://app.melicontrol.com.br/Orders")
        # filters
        # ---------
        # wait_for_clickable_and_click(
        #     driver.find_element_by_class_name("glyphicon-filter").find_element_by_xpath(
        #         "./.."
        #     )
        # )  # click on the filter icon
        # filter_options = (
        #     driver.find_element_by_class_name("glyphicon-filter")
        #     .find_element_by_xpath("./..")
        #     .find_element_by_xpath("following-sibling::ul")
        # )
        # wait_for_clickable_and_click(
        #     filter_options.find_element_by_css_selector(
        #         "input[name='orders_status[]'][value='paid']"
        #     )
        # )
        # wait_for_clickable_and_click(
        #     filter_options.find_element_by_css_selector(
        #         "input[name='orders_status[]'][value='partially_paid']"
        #     )
        # )
        # wait_for_clickable_and_click(
        #     filter_options.find_element_by_css_selector(
        #         "input[name='shipping_status'][value='pending']"
        #     )
        # )
        # wait_for_clickable_and_click(
        #     filter_options.find_element_by_id("btn-search-orders")
        # )
        time.sleep(3)
        # -----------
        def start_fetching_products(root, line_count, product=None, order_number=None):
            try:
                if product is None:
                    product = driver.find_element_by_class_name("orderEach")
                if order_number is None:
                    order_number = product.get_attribute("id").replace(
                        "panel-announcement-", ""
                    )

                # first_order = driver.find_element_by_class_name("orderEach")
                # first_order_number = first_order.get_attribute("id").replace(
                #     "panel-announcement-", ""
                # )
            except Exception as e:
                root.status = 0
                driver.quit()
                return

            with open(ERROR_FILE, "r") as error_file:
                error_file_reader = csv.DictReader(
                    error_file,
                    delimiter=",",
                    fieldnames=[*FEEDER_FILE_FIELDNAMES, "remarks"],
                )
                next_product, next_order_number = product, order_number
                for row in error_file_reader:
                    if row["order_number"] == next_order_number:
                        try:
                            next_product = next_product.find_element_by_xpath(
                                "following-sibling::div[contains(@class, 'orderEach')]"
                            )
                            next_order_number = next_product.get_attribute(
                                "id"
                            ).replace("panel-announcement-", "")
                            start_fetching_products(
                                root,
                                line_count,
                                product=next_product,
                                order_number=next_order_number,
                            )
                        except NoSuchElementException:
                            next_btn = driver.find_element_by_class_name("next")

                            if "disabled" not in next_btn.get_attribute("class"):
                                wait_for_clickable_and_click(
                                    driver.find_element_by_class_name(
                                        "next"
                                    ).find_element_by_tag_name("a")
                                )
                                time.sleep(4)

                                next_product = driver.find_element_by_class_name(
                                    "orderEach"
                                )
                                next_order_number = next_product.get_attribute(
                                    "id"
                                ).replace("panel-announcement-", "")
                                start_fetching_products(
                                    root,
                                    line_count,
                                    product=next_product,
                                    order_number=next_order_number,
                                )
                            else:
                                root.status = 0
                                driver.quit()

            details = {
                "address_label": "casa",
                "reference_point": "",
                "order_number": order_number,
            }
            (
                user_card,
                payment_card,
                post_card,
                product_card,
            ) = product.find_elements_by_class_name("panel-items")

            details["quantity"], details["name"] = html_cleaner(
                # returns something like "2 x product name"
                product_card.find_element_by_class_name(
                    "panel-heading-items"
                ).get_attribute("innerHTML")
            ).split(" x ", maxsplit=1)

            name_span = post_card.find_element_by_xpath(
                "//span[contains(text(), 'Destinatário:')]"
            )
            details["customer_first_name"], details["customer_last_name"] = (
                name_span.get_attribute("innerHTML")
                .replace("Destinatário: ", "")
                .split(" ", maxsplit=1)
            )

            details["cpf"] = (
                name_span.find_element_by_xpath("following-sibling::*")
                .get_attribute("innerHTML")
                .replace("-", "")
            )
            details["telephone"] = (
                user_card.find_element_by_class_name("fa-phone")  # phone icon
                .find_element_by_xpath("./..")  # parent column div of phone icon
                .find_element_by_xpath("following-sibling::*")  # sibling column div
                .find_element_by_tag_name("span")  # child span
                .text
            )
            details["telephone"] = (
                details["telephone"]
                if not details["telephone"] == "Sem informações"
                else ""
            )

            # -------------- remove later ------------------------
            details["cpf"] = "40262399857"
            # -------------- remove later ------------------------

            # -------------- new tab / need the old tab for later ------------------------
            driver.execute_script(
                "window.open('');"
            )  # Switch to the new window and open URL B
            driver.switch_to.window(driver.window_handles[1])
            driver.get(
                f"http://149.28.231.171/temgenteusando/inBusca/?doc={details['cpf']}"
            )

            def get_cpf_related_data(attr):
                return (
                    driver.find_element_by_xpath(f"//h5[contains(text(), '{attr}')]")
                    .find_element_by_xpath("following-sibling::p")
                    .text
                )

            details["gender"] = get_cpf_related_data("SEXO")[0]
            details["cep"] = get_cpf_related_data("cep")
            details["number"] = get_cpf_related_data("numero")
            details["complement"] = get_cpf_related_data("complemento")
            # details["complement"] = details["complement"] if not details["complement"] == "NA" else ""
            details["street_address"] = get_cpf_related_data("logradouro")
            details["district"] = get_cpf_related_data("bairro")
            details["birthdate"] = get_cpf_related_data("NASCIMENTO").split(" ")[0]
            details[
                "customer_email"
            ] = f"{details['customer_first_name']}{dt.now().strftime('%Y%m%d%H%M%S')}@gmail.com"
            details[
                "customer_email_password"
            ] = f"Abc{dt.now().strftime('%Y%m%d%H%M%S')}"

            details = strip_dict(details)
            line_count += 1

            if root.status == 0:
                return
            if root.is_reset_router_check.get():
                router_restart(root)
                ping_until_up(root)

            try:
                with open(FEEDING_FILE, "a", newline="") as save_file:
                    file_writer = csv.DictWriter(
                        save_file, delimiter=",", fieldnames=FEEDER_FILE_FIELDNAMES
                    )
                    file_writer.writerow(details)

                root.refresh_ui()
                remarks, success = botfile.bot(root, details, driver)
                updater(details, remarks, success)
                root.refresh_ui()
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(2)
                if len(driver.find_elements_by_id("onesignal-slidedown-cancel-button")):
                    wait_for_clickable_and_click(
                        driver.find_element_by_id("onesignal-slidedown-cancel-button")
                    )

                if success:
                    driver.find_element_by_css_selector(
                        "input[placeholder='Forma de Envio']"
                    ).send_keys(".")
                    driver.find_element_by_css_selector(
                        "input[placeholder='Código de Rastreio']"
                    ).send_keys(remarks)
                    Select(
                        driver.find_element_by_css_selector(
                            "select[placeholder='Prazo de entrega']"
                        )
                    ).select_by_value("288")
                    Select(
                        driver.find_element_by_css_selector(
                            "select[placeholder='Situação']"
                        )
                    ).select_by_value("shipped")
                    wait_for_clickable_and_click(
                        driver.find_element_by_id("btn-save-shipping-custom")
                    )
                    time.sleep(3)
            except Exception as e:
                print(e)
                updater(details, "system error", False)
            finally:
                # driver.get(driver.current_url)
                root.refresh_ui()
                if root.status:
                    start_fetching_products(root, line_count)
                else:
                    driver.refresh()

        start_fetching_products(root, line_count)

    except Exception as e:
        print(e)
        import sys

        _, _, exc_tb = sys.exc_info()
        print(exc_tb.tb_lineno)
    finally:
        root.status = 0
        root.refresh_ui()
        driver.quit()
        root.show_message_box("Successful", f"{line_count+1} Data Imported")
