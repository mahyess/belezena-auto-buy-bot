import json
from selenium.webdriver.common.keys import Keys
from controllers.bots.helpers.mercado_accounts import change_accounts, get_accounts
from controllers.bots.helpers.webdriver import driver_setup_mercado, get_bot_driver
from helpers.mt_wait_for_loader import mt_wait_for_loader
from helpers.passgen import generate_password
from helpers.ping_checker import ping_until_up
from controllers.router_restart_bot import router_restart
import re
import csv
import requests
from helpers.post_remark import post_remarks
from helpers.wait_for_clickable import wait_for_clickable_and_click

from selenium.webdriver.support.wait import WebDriverWait

from helpers.csv_reader import FEEDER_FILE_FIELDNAMES, updater
from helpers.file_system import CREDS_FILE, ERROR_FILE, FEEDING_FILE
from helpers.user_agent import random_user_agent
import time
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime as dt
from unidecode import unidecode

import controllers.bots.belezanaweb as botfile

import random as r


def email_generator(first_name, last_name):
    return (
            first_name.lower().split(" ")[0]
            + r.choice([".", "-", "_", "", "a", "1", "b", "0"])
            + last_name.lower().split(" ")[0]
            + str(r.randint(1, 1950))
            + r.choice(["a", "1", "b", "0"])
            + r.choice(["@gmail.com", "@hotmail.com", "@yahoo.com", "@outlook.com"])
    )


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
    driver, waiter = get_bot_driver()
    try:
        driver, accounts = driver_setup_mercado(driver)
        change_accounts(driver, accounts=accounts, to_account="AABOPOMEGA28")

        def start_fetching_products(
                root, product=None, order_number=None, paginated=False
        ):
            try:
                if product is None:
                    if not paginated:
                        driver.get(
                            "https://app.mercadoturbo.com.br/sistema/venda/vendas_ml"
                        )
                        time.sleep(2)
                    wait_for_clickable_and_click(
                        driver.find_element_by_xpath(
                            # span with text "Produtos"
                            "//span[contains(@class, 'TabVendasTexto') and text()='Env. Pendente-Outros']"
                        ),
                        driver,
                    )
                    time.sleep(5)
                    available_products = driver.find_elements_by_xpath(
                        "//span[text()='Aguardando Impress??o']/ancestor::*[contains(@class, 'ui-datatable-selectable')]"
                    )
                    if not len(available_products):
                        next_btn = driver.find_element_by_class_name(
                            "ui-paginator-next"
                        )

                        if "disabled" not in next_btn.get_attribute("class"):
                            wait_for_clickable_and_click(
                                driver.find_element_by_class_name("ui-paginator-next"),
                                driver,
                            )
                            time.sleep(4)

                            start_fetching_products(root, paginated=True)
                        else:
                            change_accounts(driver, accounts, root)
                            start_fetching_products(root)

                    product = available_products[0]

                if order_number is None:
                    order_number = product.get_attribute("data-rk")

                next_product, next_order_number = product, order_number
                with open(ERROR_FILE, "r", newline="") as error_file:
                    file_reader = csv.DictReader(error_file, delimiter=",")

                    for line_count, row in enumerate(file_reader):
                        if row.get("order_number") == order_number and any(
                                x in row.get("remarks")
                                for x in [
                                    "Out of Stock",
                                    "Not enough quantity",
                                    "No CPF",
                                    "excess request",
                                ]
                        ):
                            try:
                                _, date = row.get("remarks").partition(" - ")
                                if date != str(dt.today().date()):
                                    break
                            except ValueError:
                                pass
                            try:
                                next_product = next_product.find_element_by_xpath(
                                    "following-sibling::*[contains(@class, 'ui-datatable-selectable') and .//span[text()='Aguardando Impress??o']]"
                                )
                                next_order_number = next_product.get_attribute(
                                    "data-rk"
                                )
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

                                    start_fetching_products(root, paginated=True)
                                else:
                                    change_accounts(driver, accounts, root)
                                    start_fetching_products(root)
                                # next_btn = driver.find_element_by_class_name(
                                #     "ui-paginator-next"
                                # )

                                # if "disabled" not in next_btn.get_attribute("class"):
                                #     wait_for_clickable_and_click(
                                #         driver.find_element_by_class_name(
                                #             "ui-paginator-next"
                                #         ),
                                #         driver,
                                #     )
                                #     time.sleep(4)

                                #     next_product = driver.find_element_by_class_name(
                                #         "//span[text()='Aguardando Impress??o']/ancestor::*[contains(@class, 'ui-datatable-selectable')]"
                                #     )
                                #     next_order_number = next_product.get_attribute(
                                #         "data-rk"
                                #     )
                                #     start_fetching_products(
                                #         root,
                                #         product=next_product,
                                #         order_number=next_order_number,
                                #     )
                                # else:

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

                # scroll to top
                driver.execute_script(
                    "arguments[0].scrollIntoView();",
                    driver.find_element_by_class_name("route-bar-breadcrumb"),
                )

                # open dialog
                wait_for_clickable_and_click(
                    product.find_element_by_xpath(
                        ".//*[contains(@title, 'Clique para editar o endere??o do comprador')]"
                    ),
                    driver,
                )
                dialog = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "editarEnderecoDialog"))
                )
                WebDriverWait(driver, 10).until(
                    lambda d: "false" in dialog.get_attribute("aria-hidden")
                )

                (
                    details["customer_first_name"],
                    details["customer_last_name"],
                ) = f"""{
                unidecode(
                    dialog.find_element_by_xpath(
                        ".//label[contains(text(), 'Nome Destinat??rio')]/following-sibling::input"
                    )
                    .get_attribute("value")
                )}  """.split(
                    " ", 1
                )

                details["cpf"] = dialog.find_element_by_xpath(
                    ".//label[contains(text(), 'CPF / CNPJ')]/following-sibling::input"
                ).get_attribute("value")
                details["cep"] = dialog.find_element_by_xpath(
                    ".//form[@id='form-dialog-endereco']/div/label[contains(text(), 'CEP')]/following-sibling::input"
                ).get_attribute("value")
                details["street_address"] = dialog.find_element_by_xpath(
                    ".//label[contains(text(), 'Endere??o')]/following-sibling::input"
                ).get_attribute("value")
                details["number"] = dialog.find_element_by_xpath(
                    ".//label[contains(text(), 'N??mero')]/following-sibling::input"
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
                    dialog.find_element_by_class_name("ui-dialog-titlebar-close"),
                    driver,
                )

                if len(details["cpf"]) != 11:
                    NO_CPF_MSG = "Ola, caro cliente! Agradecemos pela sua compra! Mas sentimos muito em informar que n??o emitimos nota fiscal para pessoa jur??dica, necessitando assim um numero CPF para darmos continuidade na entrega. Att"
                    # ------------ message send -----------------
                    mt_wait_for_loader(
                        driver,
                        lambda: wait_for_clickable_and_click(
                            product.find_element_by_css_selector(
                                "span.fa-message-lines"
                            ),
                            driver,
                        ),
                    )
                    dialog = WebDriverWait(driver, 25).until(
                        EC.visibility_of_element_located((By.ID, "mensagensDialog"))
                    )

                    dialog = driver.find_element_by_id("mensagensDialog")
                    messages = dialog.find_elements_by_css_selector("p.p-text-left")
                    is_cpf_request_sent = False
                    details["cpf"] = None
                    for i, message in enumerate(messages):
                        if NO_CPF_MSG in message.text:
                            is_cpf_request_sent = True

                        if not i:
                            # ignore first message
                            continue

                        cpf = re.search(
                            r"\d{3}\.?\ ?\d{3}\.?\ ?\d{3}\-?\.?\ ?\d{2}", message.text
                        )
                        if cpf:
                            details["cpf"] = (
                                cpf.group(0)
                                .replace(".", "")
                                .replace("-", "")
                                .replace(" ", "")
                            )
                            break

                    if not details["cpf"]:
                        updater(details, f"No CPF - {str(dt.today().date())}", False)
                        if not is_cpf_request_sent:
                            dialog.find_element_by_css_selector("textarea").send_keys(
                                NO_CPF_MSG
                            )

                            mt_wait_for_loader(
                                driver,
                                lambda: wait_for_clickable_and_click(
                                    dialog.find_element_by_css_selector(
                                        "button[type='submit'][class*='ui-button-success']"
                                    ),
                                    driver,
                                ),
                            )

                    wait_for_clickable_and_click(
                        dialog.find_element_by_css_selector(
                            "a[class*='ui-dialog-titlebar-close']"
                        ),
                        driver,
                    )

                    if not details["cpf"]:
                        start_fetching_products(root)
                    # ------------ message send -----------------

                cpf_data_response = requests.get(
                    f"http://168.138.144.219/MaykeDrumondToken1000012.php?consultar={details['cpf']}&tipo=cpf&fbclid=IwAR1vYqiABMTjWVGsZBNSpejIUASzutvkHrl0TROCYbsQgm0ZyrIxvuepBTk"
                )
                cpf_data = cpf_data_response.json()
                if cpf_data_response.status_code == 200 and cpf_data.get("status"):
                    # if this request is succesfull
                    if cpf_data.get("nome"):
                        (
                            details["customer_first_name"],
                            details["customer_last_name"],
                        ) = (
                            unidecode(cpf_data.get("nome")).title().split(" ", 1)
                        )

                    details["gender"] = cpf_data.get("sexoDescricao", "F")
                    # details["complement"] = details["complement"] if not details["complement"] == "NA" else ""
                    details["birthdate"] = cpf_data.get("nascimento", "12/12/1992")

                    ddd = cpf_data.get("ddd", "11")
                    ddd = ddd if ddd else "11"
                    details["telephone"] = (
                            ddd + "99" + f"1{dt.now().strftime('%d%H%M%S')}"
                    )
                else:
                    cpf_data_response = requests.get(
                        f"http://168.138.144.219/PRIVADOPORCREDITOS02.php?consultar={details['cpf']}&fbclid=IwAR2a5wxiPtP3G2HMV_9hCVlTEemjSJ16ENI8klpMlzlXN7o27ypwCkXiDjk"
                    )
                    cpf_data = cpf_data_response.json()

                    if (
                            cpf_data_response.status_code == 200
                            and cpf_data.get("retorno") == "OK"
                    ):
                        # if this request is succesfull
                        cpf_data = cpf_data.get("msg")

                        if cpf_data.get("nome"):
                            (
                                details["customer_first_name"],
                                details["customer_last_name"],
                            ) = (
                                unidecode(cpf_data.get("nome")).title().split(" ", 1)
                            )

                        details["gender"] = cpf_data.get("sexo", "F")[0]
                        # if gender not in M or F, set gender to F
                        if details["gender"] not in ["M", "F"]:
                            details["gender"] = "F"

                        # details["complement"] = details["complement"] if not details["complement"] == "NA" else ""
                        details["birthdate"] = cpf_data.get("nascimento", "12/12/1992")

                        ddd = cpf_data.get("ddd", "11")
                        details["telephone"] = (
                                ddd + "99" + f"1{dt.now().strftime('%d%H%M%S')}"
                        )
                    else:
                        details = {
                            **details,
                            "gender": "F",
                            "birthdate": "11/02/1990",
                            "telephone": "1199" + f"1{dt.now().strftime('%d%H%M%S')}",
                        }

                details["customer_email"] = email_generator(
                    details["customer_first_name"], details["customer_last_name"]
                )

                details["customer_email_password"] = generate_password()

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

                    print("starting beleza bot")

                    remarks, success = botfile.bot(root, details)
                    updater(details, remarks, success)
                    root.refresh_ui()
                    time.sleep(3)
                    # if len(driver.find_elements_by_id("onesignal-slidedown-cancel-button")):
                    #     wait_for_clickable_and_click(
                    #         driver.find_element_by_id("onesignal-slidedown-cancel-button")
                    #     )
                    if remarks:
                        # ------------ remarks -----------------
                        post_remarks(driver, product, remarks)
                        time.sleep(3)
                        # ------------ remarks -----------------

                    if success:
                        time.sleep(2)
                        # ------------ cpf and delivery date -----------------
                        wait_for_clickable_and_click(
                            product.find_element_by_css_selector("a.ButtonEnvio"),
                            driver,
                        )
                        dialog = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located(
                                (By.ID, "jaEntregueiDialog")
                            )
                        )
                        WebDriverWait(driver, 10).until(
                            lambda d: "false" in dialog.get_attribute("aria-hidden")
                        )

                        remarks_field = dialog.find_element_by_css_selector(
                            "input[type='text']"
                        )

                        time.sleep(1)
                        remarks_field.send_keys(details["cpf"])
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
                            dialog.find_element_by_css_selector(
                                "button[type='submit']"
                            ),
                            driver,
                        )
                        # ------------ cpf and delivery date -----------------
                        time.sleep(2)

                        # ------------ message send -----------------
                        mt_wait_for_loader(
                            driver,
                            lambda: wait_for_clickable_and_click(
                                product.find_element_by_css_selector(
                                    "span.fa-message-lines"
                                ),
                                driver,
                            ),
                        )
                        time.sleep(2)

                        dialog = driver.find_element_by_id("mensagensDialog")

                        dialog.find_element_by_css_selector("textarea").send_keys(
                            "Ol??, caro cliente! Para sua comodidade, voc?? pode acompanhar a entrega do seu pedido acessando: imediataexpress.info/tracking/"
                        )

                        mt_wait_for_loader(
                            driver,
                            lambda: wait_for_clickable_and_click(
                                dialog.find_element_by_css_selector(
                                    "button[type='submit'][class*='ui-button-success']"
                                ),
                                driver,
                            ),
                        )

                        wait_for_clickable_and_click(
                            dialog.find_element_by_css_selector(
                                "a[class*='ui-dialog-titlebar-close']"
                            ),
                            driver,
                        )
                        # ------------ message send -----------------

                except Exception as e:
                    print(e)
                    updater(details, "system error", False)

                finally:
                    start_fetching_products(root)

            except Exception as e:
                print("restarting", e)
                # time.sleep(30)
            finally:
                root.refresh_ui()
                start_fetching_products(root)

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
        bot(root)
