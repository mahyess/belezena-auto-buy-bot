import json
import time

from bs4 import BeautifulSoup
import requests
from lxml import html
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from controllers.bots.helpers.mercado_accounts import change_accounts, get_accounts
from controllers.bots.helpers.webdriver import driver_setup_mercado
from helpers.file_system import CREDS_FILE
from helpers.mt_wait_for_loader import mt_wait_for_loader
from helpers.post_remark import post_remarks
from helpers.wait_for_clickable import wait_for_clickable_and_click
from helpers.user_agent import random_user_agent


def next_page(driver):
    next = driver.find_elements_by_css_selector("a.ui-paginator-next")[-1]

    if "ui-state-disabled" not in next.get_attribute("class"):
        # s = spinner
        s = driver.find_element_by_css_selector("div.dialog-aguarde")
        wait_for_clickable_and_click(next, driver, nonjsclick=True, wait_time=10)
        WebDriverWait(driver, 10).until(
            lambda _: "false" in s.get_attribute("aria-hidden")
        )
        WebDriverWait(driver, 10).until(
            lambda _: "true" in s.get_attribute("aria-hidden")
        )


def bot(root, details=None, driver=None):
    WAIT_TIME = 8
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
    waiter = WebDriverWait(driver, WAIT_TIME)

    try:
        driver, accounts = driver_setup_mercado(driver)

        def update_single(product):
            # if delivered
            try:
                deliver_btn = product.find_element_by_css_selector("a.ButtonEnvio")
            except NoSuchElementException:
                print("update_single err: no deliver button")
                return False
            # if already marked as delivered
            if len(deliver_btn.find_elements_by_css_selector("div.GreenBack")):
                return False
            # product.find_element_by_id("div-toggle").click()
            meurastre_link_remarks = product.find_elements_by_xpath(
                './/span[contains(text(), "meurastre.io")]'
            )
            if len(meurastre_link_remarks) == 0 or meurastre_link_remarks[0].text == "":
                return False

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
                print(order_states)
            except Exception as e:
                print("soup ma problem")

            dom_changed = False
            status_remark: str = ""
            for i, step in enumerate(reversed(order_states)):
                if step["date"]:
                    status_remark = f"{step['message']} {step['date']}"
                    if step["message"] not in product.get_attribute("innerHTML"):
                        post_remarks(driver, product, status_remark)
                        dom_changed = True
                    if not i:
                        # open dialog
                        wait_for_clickable_and_click(
                            deliver_btn, driver, wait_time=WAIT_TIME
                        )
                        dialog = waiter.until(
                            EC.visibility_of_element_located(
                                (By.ID, "jaEntregueiDialog")
                            )
                        )
                        waiter.until(
                            lambda d: "false" in dialog.get_attribute("aria-hidden")
                        )

                        # select option delivered
                        wait_for_clickable_and_click(
                            # click label for id "delivered"
                            dialog.find_element_by_css_selector(
                                "label[for='form-dialog-ja-entreguei:radio-entreguei']"
                            ),
                            driver,
                            wait_time=WAIT_TIME,
                            nonjsclick=True,
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
                        if dialog.get_attribute("aria-hidden") == "false":
                            wait_for_clickable_and_click(
                                dialog.find_element_by_css_selector(
                                    "a.ui-dialog-titlebar-close"
                                ),
                                driver,
                                wait_time=WAIT_TIME,
                            )

                    break

            return dom_changed

        def update():
            # product_ids = [el.get_attribute('data-rk') for el in driver.find_element_by_id(
            #     "form-vendas:grid-vendas_data"
            # ).find_elements_by_css_selector("tr")]

            driver.get("https://app.mercadoturbo.com.br/sistema/venda/vendas_ml")
            dom_changed = True
            data_ri = -1
            while True:
                data_ri += 1
                # for _ in range(data_ri // 20):
                if data_ri and data_ri % 20 == 0:
                    next_page(driver)
                    dom_changed = True
                try:
                    if dom_changed:
                        time.sleep(5)
                    product = driver.find_element_by_id(
                        "form-vendas:grid-vendas_data"
                    ).find_element_by_css_selector(f"tr[data-ri='{data_ri}']")
                    # product = WebDriverWait(
                    #     driver.find_element_by_id("form-vendas:grid-vendas_data"),
                    #     WAIT_TIME,
                    # ).until(
                    #     EC.element_to_be_clickable(
                    #         (By.CSS_SELECTOR, f"tr[data-ri='{data_ri}']")
                    #     )
                    # )

                    dom_changed = update_single(product)
                except NoSuchElementException:
                    print("update err: no such element")
                    break
                except Exception as e:
                    print(f"products_loop err: '{e}'")

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
