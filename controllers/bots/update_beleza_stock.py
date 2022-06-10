import csv
import json
import time
import requests
from lxml import html
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.wait import WebDriverWait
from controllers.bots.helpers.mercado_accounts import change_accounts, get_accounts
from helpers.file_system import CREDS_FILE
from helpers.ping_checker import ping_until_up

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
            # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36",
        }
        headers["User-Agent"] = random_user_agent()
        with requests.Session() as s:
            if data is None:
                return s.get(url, headers=headers).content
            else:
                return s.post(url, data=data).content

    url = f"https://www.belezanaweb.com.br/busca?q={name}"

    # ping_until_up()  # wait for website to be up
    page = fetch(url)
    tree = html.fromstring(page)
    products = tree.xpath(
        f"//div[contains(@class, 'showcase-item') and .//img[contains(translate(@alt, '{name.upper()}', '{name.lower()}'), '{name.lower()}')]]"
    )

    for product in products:
        product_data = product.get("data-event")
        product_data = json.loads(product_data)
        price = product_data.get("price")
        if "showcase-item-unavailable" in product.classes:
            print("unavailable")
            return False, price

        print("available")
        return True, price

    print("Nothing")
    return False, 0


creds = json.load(open(CREDS_FILE))
QTY = creds.get("quantity")
PRICE_PERCENT = creds.get("price")


def bot(root, details=None, driver=None):
    using_param_driver = False
    if not driver:
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        # options.add_argument("--headless")
        options.add_argument(f"user-agent={random_user_agent(root)}")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(8)
    else:
        using_param_driver = True
    waiter = WebDriverWait(driver, 10)

    try:
        with open(CREDS_FILE, "r") as f:
            creds = json.load(f)
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
            driver.find_element_by_css_selector("button[type='submit']"), driver
        )
        time.sleep(3)
        accounts = get_accounts(driver)

        driver.get("https://app.mercadoturbo.com.br/sistema/anuncio/gerenciador")
        time.sleep(6)
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
            current_price = (
                product.find_element_by_class_name("cellPreco")
                .find_element_by_class_name("ui-cell-editor-output")
                .text
            )

            try:
                is_available, price = beleza_stock_scraper(name)
            except Exception as e:
                print(f"there was error finding stock for name: '{name}'")
                is_available = False
                price = 0
            price = (round((price * (1 + PRICE_PERCENT / 100)), 2))
            if float(price) < 7:
                price = str(7)
            price = str(price).replace(".",",")
            stock = str(QTY) if is_available else "0"

            if current_stock != stock or price != current_price:
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
                stock_input.send_keys(stock)
                price_input = (
                    product.find_element_by_class_name("cellPreco")
                    .find_element_by_class_name("ui-cell-editor-input")
                    .find_element_by_css_selector("input[type='text']")
                )
                price_input.send_keys(Keys.CONTROL, "a")
                price_input.send_keys(price)
                wait_for_clickable_and_click(
                    product.find_element_by_class_name(
                        "cellEdit"
                    ).find_element_by_class_name("ui-row-editor-check"),
                    driver,
                )

        def update():
            products = driver.find_element_by_id(
                "form-anuncios:grid-anuncios_data"
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
                    next_btn,
                    driver,
                    nonjsclick=True,
                )
                waiter.until(lambda d: "false" in spinner.get_attribute("aria-hidden"))
                waiter.until(lambda d: "true" in spinner.get_attribute("aria-hidden"))
                update()

        state_active_to_paused_changer = ActionChains(driver)
        state_active_to_paused_changer.send_keys(Keys.ARROW_DOWN)
        state_active_to_paused_changer.send_keys(Keys.ENTER)
        for _ in accounts:
            update()

            spinner = driver.find_element_by_css_selector("div.dialog-aguarde")

            wait_for_clickable_and_click(
                driver.find_element_by_xpath(
                    "//h4[contains(., 'Status:')]/following-sibling::div[@role='combobox']"
                ),
                driver,
                nonjsclick=True,
            )

            state_active_to_paused_changer.perform()
            waiter.until(lambda d: "false" in spinner.get_attribute("aria-hidden"))
            waiter.until(lambda d: "true" in spinner.get_attribute("aria-hidden"))

            try:
                # go to page 1 since it starts at random pages
                wait_for_clickable_and_click(
                    driver.find_elements_by_css_selector(
                        "a.ui-paginator-page[aria-label='Page 1']"
                    )[0],
                    driver,
                    nonjsclick=True,
                )
                print("hello")
                waiter.until(lambda d: "false" in spinner.get_attribute("aria-hidden"))
                waiter.until(lambda d: "true" in spinner.get_attribute("aria-hidden"))
                print("hello agin")
            except Exception as e:
                pass

            update()

            change_accounts(driver, accounts)

        print("everything done.")

    except Exception as e:
        print(e)
        return "system error", False

    finally:
        print("update stock complete")
        
        bot(root)
