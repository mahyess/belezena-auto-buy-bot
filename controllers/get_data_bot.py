from selenium.webdriver.common.keys import Keys
from helpers.ping_checker import ping_until_up
from controllers.router_restart_bot import router_restart
import re
import csv
import requests
from helpers.wait_for_clickable import wait_for_clickable_and_click

from selenium.webdriver.support.wait import WebDriverWait

from helpers.csv_reader import FEEDER_FILE_FIELDNAMES, updater
from helpers.file_system import ERROR_FILE, FEEDING_FILE
from helpers.user_agent import random_user_agent
import time
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
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
    root.status = 1
    root.refresh_ui()

    options = Options()
    options.add_argument(f"user-agent={random_user_agent(root)}")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    try:
        driver.get("https://app.mercadoturbo.com.br//login_operador")
        driver.find_element_by_xpath("//input[contains(@id, 'input-conta')]").send_keys(
            "brenoml0721@gmail.com"
        )
        driver.find_element_by_xpath(
            "//input[contains(@id, 'input-usuario')]"
        ).send_keys("operado1")
        driver.find_element_by_css_selector("input[type='password']").send_keys(
            "36461529"
        )
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button[type='submit']"), driver
        )
        print("submit")
        time.sleep(3)

        print("order page")
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
        # -----------
        def start_fetching_products(root, product=None, order_number=None):
            try:
                driver.get("https://app.mercadoturbo.com.br/sistema/venda/vendas_ml")
                if product is None:
                    product = driver.find_element_by_xpath(
                        "//span[text()='Aguardando Impressão']/ancestor::*[contains(@class, 'ui-datatable-selectable')]"
                        # "//div[contains(@class, 'ui-datatable-selectable') and .//*[text()='Aguardando Impressão']]"
                    )

                if order_number is None:
                    order_number = product.get_attribute("data-rk")

            except Exception as e:
                time.sleep(30)
                start_fetching_products(root)

            next_product, next_order_number = product, order_number
            with open(ERROR_FILE, "r", newline="") as error_file:
                file_reader = csv.DictReader(error_file, delimiter=",")

                for line_count, row in enumerate(file_reader):
                    if row.get("order_number") == order_number:
                        try:
                            next_product = next_product.find_element_by_xpath(
                                "following-sibling::*[contains(@class, 'ui-datatable-selectable') and .//span[text()='Aguardando Impressão']]"
                            )
                            next_order_number = next_product.get_attribute("data-rk")
                            start_fetching_products(
                                root,
                                product=next_product,
                                order_number=next_order_number,
                            )
                        except NoSuchElementException:
                            next_btn = driver.find_element_by_class_name(
                                "ui-paginator-next"
                            )

                            if "disabled" not in next_btn.get_attribute("class"):
                                wait_for_clickable_and_click(
                                    driver.find_element_by_class_name(
                                        "ui-paginator-next"
                                    ),
                                    driver,
                                )
                                time.sleep(4)

                                next_product = driver.find_element_by_class_name(
                                    "ui-datatable-selectable"
                                )
                                next_order_number = next_product.get_attribute(
                                    "data-rk"
                                )
                                start_fetching_products(
                                    root,
                                    product=next_product,
                                    order_number=next_order_number,
                                )
                            else:
                                time.sleep(30)
                                start_fetching_products(root)

            details = {
                "address_label": "casa",
                "reference_point": "",
                "order_number": order_number,
            }

            name_span = product.find_element_by_id(
                f"TituloAnuncio_{details['order_number']}"
            )
            details["name"] = name_span.text.strip()
            details["quantity"] = (
                name_span.find_element_by_xpath("preceding-sibling::span")
                .text.replace("x", "")
                .strip()
            )

            # open dialog
            wait_for_clickable_and_click(
                product.find_element_by_xpath(
                    ".//*[contains(@aria-label, 'Clique para editar o endereço do comprador')]"
                ),
                driver,
            )
            dialog = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "editarEnderecoDialog"))
            )
            WebDriverWait(driver, 10).until(
                lambda d: "false" in dialog.get_attribute("aria-hidden")
            )

            details["cpf"] = dialog.find_element_by_xpath(
                ".//label[contains(text(), 'CPF / CNPJ')]/following-sibling::input"
            ).get_attribute("value")
            details["cep"] = dialog.find_element_by_xpath(
                ".//form[@id='form-dialog-endereco']/div/label[contains(text(), 'CEP')]/following-sibling::input"
            ).get_attribute("value")
            details["street_address"] = dialog.find_element_by_xpath(
                ".//label[contains(text(), 'Endereço')]/following-sibling::input"
            ).get_attribute("value")
            details["number"] = dialog.find_element_by_xpath(
                ".//label[contains(text(), 'Número')]/following-sibling::input"
            ).get_attribute("value")
            details["complement"] = dialog.find_element_by_xpath(
                ".//label[contains(text(), 'Complemento')]/following-sibling::input"
            ).get_attribute("value")
            details["reference_point"] = dialog.find_element_by_xpath(
                ".//label[contains(text(), 'Bairro')]/following-sibling::input"
            ).get_attribute("value")
            details["district"] = dialog.find_element_by_xpath(
                ".//label[contains(text(), 'Cidade')]/following-sibling::input"
            ).get_attribute("value")

            time.sleep(1)
            wait_for_clickable_and_click(
                dialog.find_element_by_class_name("ui-dialog-titlebar-close"), driver
            )

            cpf_data_response = requests.get(
                f"http://140.238.187.29/maykedrumon210901091034114.php?cpf={details['cpf']}"
            )
            if cpf_data_response.status_code == 200:
                # if this request is succesfull
                cpf_data = cpf_data_response.json()

                (details["customer_first_name"], details["customer_last_name"],) = (
                    cpf_data.get("nome", "agenericname randomized")
                    .title()
                    .split(" ", 1)
                )

                details["gender"] = cpf_data.get("sexoDescricao", "F")
                # details["complement"] = details["complement"] if not details["complement"] == "NA" else ""
                details["birthdate"] = cpf_data.get("nascimento", "12/12/1992")

                ddd = cpf_data.get("ddd", "11")
                details["telephone"] = ddd + "99" + f"1{dt.now().strftime('%d%H%M%S')}"
            else:
                pass

            details[
                "customer_email"
            ] = f"{details['customer_first_name']}_{details['customer_last_name']}{dt.now().strftime('%S%M')}@gmail.com".replace(
                " ", "_"
            ).lower()
            details[
                "customer_email_password"
            ] = f"Abc{dt.now().strftime('%Y%m%d%H%M%S')}"

            details = strip_dict(details)

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

                remarks, success = botfile.bot(root, details)
                updater(details, remarks, success)
                root.refresh_ui()
                time.sleep(2)
                # if len(driver.find_elements_by_id("onesignal-slidedown-cancel-button")):
                #     wait_for_clickable_and_click(
                #         driver.find_element_by_id("onesignal-slidedown-cancel-button")
                #     )
                if success:
                    wait_for_clickable_and_click(
                        product.find_element_by_css_selector(
                            "a[class*='statusDoPedido']"
                        ),
                        driver,
                    )
                    dialog = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.ID, "jaEntregueiDialog"))
                    )
                    WebDriverWait(driver, 10).until(
                        lambda d: "false" in dialog.get_attribute("aria-hidden")
                    )

                    remarks_field = dialog.find_element_by_css_selector(
                        "input[type='text']"
                    )

                    time.sleep(1)
                    remarks_field.send_keys(
                        f"{remarks}?email={details['customer_email']}"
                    )
                    time.sleep(1)
                    remarks_field.send_keys(
                        Keys.TAB,
                        Keys.UP,
                        Keys.UP,
                        Keys.UP,
                        Keys.UP,
                        Keys.UP,
                        Keys.UP,
                        Keys.UP,
                        Keys.UP,
                        Keys.UP,
                        Keys.UP,
                        Keys.UP,
                        Keys.UP,
                    )

                    wait_for_clickable_and_click(
                        dialog.find_element_by_css_selector("button[type='submit']"),
                        driver,
                    )
                    time.sleep(3)

                else:
                    if remarks != "":
                        remarks_input_btn = product.find_element_by_id("div-toggle")
                        wait_for_clickable_and_click(remarks_input_btn, driver)
                        remarks_form = remarks_input_btn.find_element_by_xpath(
                            "following-sibling::div"
                        )
                        remarks_form.find_element_by_xpath(
                            ".//div[contains(@class, 'mt-width-full')]/input"
                        ).send_keys(f"{remarks}")
                        wait_for_clickable_and_click(
                            remarks_form.find_element_by_css_selector(
                                "button[type='submit'][class*='ui-button-success']"
                            ),
                            driver,
                        )
                        time.sleep(2)
            except Exception as e:
                print(e)
                updater(details, "system error", False)
            finally:
                # driver.get(driver.current_url)
                root.refresh_ui()
                if root.status:
                    start_fetching_products(root)
                else:
                    driver.refresh()

        start_fetching_products(root)

    except Exception as e:
        print(e)
        import sys

        _, _, exc_tb = sys.exc_info()
        print(exc_tb.tb_lineno)
    finally:
        root.status = 0
        root.refresh_ui()
        driver.quit()
