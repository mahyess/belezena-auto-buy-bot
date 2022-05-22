import json
import time

from bs4 import BeautifulSoup
import requests
from lxml import html
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from controllers.bots.helpers.mercado_accounts import change_accounts, get_accounts
from helpers.file_system import CREDS_FILE
from helpers.mt_wait_for_loader import mt_wait_for_loader
from helpers.post_remark import post_remarks
from helpers.wait_for_clickable import wait_for_clickable_and_click
from helpers.user_agent import random_user_agent


def bot(root, details=None, driver=None):
    WAIT_TIME = 3
    with open(CREDS_FILE, "r") as f:
        creds = json.load(f)
    using_param_driver = False
    if not driver:
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument(f"user-agent={random_user_agent(root)}")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(WAIT_TIME)
    else:
        using_param_driver = True
    waiter = WebDriverWait(driver, 10)

    try:
        driver.get("https://app.mercadoturbo.com.br//login_operador")
        driver.find_element_by_xpath("//input[contains(@id, 'input-conta')]").send_keys(
            creds.get("email", "brenoml0921@yahoo.com")
        )
        driver.find_element_by_xpath(
            "//input[contains(@id, 'input-usuario')]"
        ).send_keys(creds.get("operador", "operador1"))
        driver.find_element_by_css_selector("input[type='password']").send_keys(
            creds.get("password", "36461529")
        )
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button[type='submit']"),
            driver,
            wait_time=WAIT_TIME,
        )
        time.sleep(3)
        accounts = get_accounts(driver)

        driver.get("https://app.mercadoturbo.com.br/sistema/venda/vendas_ml")

        def update_single(product):
            # if delivered
            deliver_btn = product.find_element_by_css_selector("a.statusDoPedido")
            # if already marked as delivered
            if len(deliver_btn.find_elements_by_css_selector("div.GreenBack")):
                return
            # product.find_element_by_id("div-toggle").click()
            meurastre_link_remarks = product.find_elements_by_xpath(
                './/span[contains(text(), "meurastre.io")]'
            )
            if len(meurastre_link_remarks) == 0 or meurastre_link_remarks[0].text == "":
                return

            try:
                soup = BeautifulSoup(
                    requests.get(meurastre_link_remarks[0].text).text,
                    features="html.parser",
                )
                soup_text = soup.find("script", {"id": "__NEXT_DATA__"}).string
                __next_data__ = json.loads(soup_text)
                order_states = __next_data__["props"]["pageProps"]["order"][
                    "shippings"
                ][0]["steps"]
            except Exception as e:
                print("soup ma problem")

            status_remark: str = ""
            for i, step in enumerate(reversed(order_states)):
                if step["date"]:
                    status_remark = f"{step['message']} {step['date']}"
                    if step["message"] not in product.get_attribute("innerHTML"):
                        post_remarks(driver, product, status_remark)
                    if not i:
                        # open dialog
                        mt_wait_for_loader(
                            driver,
                            lambda: wait_for_clickable_and_click(
                                deliver_btn, driver, wait_time=WAIT_TIME
                            ),
                        )
                        dialog = driver.find_element_by_id("jaEntregueiDialog")

                        # select option delivered
                        wait_for_clickable_and_click(
                            # click label for id "delivered"
                            dialog.find_element_by_css_selector(
                                "label[for='form-dialog-ja-entreguei:radio-entreguei']"
                            ),
                            driver,
                            wait_time=WAIT_TIME,
                        )

                        # save
                        mt_wait_for_loader(
                            driver,
                            lambda: wait_for_clickable_and_click(
                                dialog.find_element_by_css_selector(
                                    "button[type='submit']"
                                ),
                                driver,
                                wait_time=WAIT_TIME,
                            ),
                        )

                    break

        def update():
            products = driver.find_element_by_id(
                "form-vendas:grid-vendas_data"
            ).find_elements_by_css_selector("tr")

            for product in products:
                try:
                    update_single(product)
                except Exception as e:
                    print(f"there was error updating product: '{e}'")

            next_btn = driver.find_elements_by_css_selector("a.ui-paginator-next")[-1]

            if "ui-state-disabled" not in next_btn.get_attribute("class"):
                spinner = driver.find_element_by_css_selector("div.dialog-aguarde")
                wait_for_clickable_and_click(
                    next_btn, driver, nonjsclick=True, wait_time=WAIT_TIME
                )
                waiter.until(lambda d: "false" in spinner.get_attribute("aria-hidden"))
                waiter.until(lambda d: "true" in spinner.get_attribute("aria-hidden"))
                update()

        state_active_to_paused_changer = ActionChains(driver)
        state_active_to_paused_changer.send_keys(Keys.ARROW_DOWN)
        state_active_to_paused_changer.send_keys(Keys.ENTER)
        for _ in accounts:
            update()

            change_accounts(driver, accounts)

        print("everything done.")

    except Exception as e:
        print(e)
        return "system error", False

    finally:
        print("update stock complete")
        if not using_param_driver:
            driver.quit()
        bot(root)
