import csv
import time
import requests

from selenium.webdriver.support.wait import WebDriverWait
from controllers.bots.helpers.mercado_accounts import change_accounts, get_accounts
from bs4 import BeautifulSoup

from helpers.wait_for_clickable import wait_for_clickable_and_click
from helpers.user_agent import random_user_agent
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys


def beleza_stock_scraper(name):
    def fetch(url, data=None):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US;en;q=0.5",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "www.belezanaweb.com.br",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-GPC": "1",
            "TE": "trailers",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36",
        }
        with requests.Session() as s:
            if data is None:
                return s.get(url, headers=headers).content
            else:
                return s.post(url, data=data).content

    url = f"https://www.belezanaweb.com.br/busca?q={name}"
    page = BeautifulSoup(fetch(url), "lxml")
    products = page.find_all("div", {"class": "showcase-item"})
    for product in products:
        if name.lower() in product.text.lower():
            if "Avise-me" in product.text:
                print("Avise-me")
                return 0
            if "Compre Agora" in product.text:
                print("Compre")
                return 5
    print("Nothing")
    return 0


def bot(root, details=None, driver=None):
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
    waiter = WebDriverWait(driver, 10)

    try:
        driver.get("https://app.mercadoturbo.com.br//login_operador")
        driver.find_element_by_xpath("//input[contains(@id, 'input-conta')]").send_keys(
            "gugui10@yahoo.com"
        )
        driver.find_element_by_xpath(
            "//input[contains(@id, 'input-usuario')]"
        ).send_keys("operador1")
        driver.find_element_by_css_selector("input[type='password']").send_keys(
            "36461529"
        )
        wait_for_clickable_and_click(
            driver.find_element_by_css_selector("button[type='submit']"), driver
        )
        time.sleep(3)
        accounts = get_accounts(driver)

        driver.get("https://app.mercadoturbo.com.br/sistema/anuncio/gerenciador")

        def update_single(product):
            if "ui-datatable-empty-message" in product.get_attribute("class"):
                return

            name = (
                product.find_element_by_class_name("cellAnuncio")
                .find_element_by_class_name("ui-cell-editor-output")
                .text
            )

            current_stock = (
                product.find_element_by_class_name("cellQtd")
                .find_element_by_class_name("ui-cell-editor-output")
                .text
            )

            stock = beleza_stock_scraper(name)

            if current_stock != str(stock):
                wait_for_clickable_and_click(
                    product.find_element_by_class_name(
                        "cellEdit"
                    ).find_element_by_class_name("ui-row-editor-pencil"),
                    driver,
                )
                stock_input = (
                    product.find_element_by_class_name("cellQtd")
                    .find_element_by_class_name("ui-cell-editor-input")
                    .find_element_by_css_selector("input[type='text']")
                )
                stock_input.send_keys(Keys.CONTROL, "a")
                stock_input.send_keys(str(stock))
                wait_for_clickable_and_click(
                    product.find_element_by_class_name(
                        "cellEdit"
                    ).find_element_by_class_name("ui-row-editor-check"),
                    driver,
                )

            print(stock)

        def update():
            products = driver.find_element_by_id(
                "form-anuncios:grid-anuncios_data"
            ).find_elements_by_css_selector("tr")

            for product in products:
                update_single(product)

            next_btn = driver.find_elements_by_css_selector("a.ui-paginator-next")[-1]

            if "ui-state-disabled" not in next_btn.get_attribute("class"):
                spinner = driver.find_element_by_css_selector("div.dialog-aguarde")
                driver.execute_script(
                    "arguments[0].scrollIntoView();",
                    next_btn,
                )
                next_btn.click()
                waiter.until(lambda d: "false" in spinner.get_attribute("aria-hidden"))
                waiter.until(lambda d: "true" in spinner.get_attribute("aria-hidden"))
                update()

        for _ in accounts:
            update()
            change_accounts(driver, accounts)

        print("everything done.")

    except Exception as e:
        print(e)
        return "system error", False

    finally:
        if not using_param_driver:
            driver.quit()
