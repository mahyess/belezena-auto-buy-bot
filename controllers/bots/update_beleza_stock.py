import csv
import json
import time
import requests
from lxml import html
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.wait import WebDriverWait
from controllers.bots.helpers.mercado_accounts import change_accounts, get_accounts
from helpers.file_system import CREDS_FILE
from helpers.mt_wait_for_loader import mt_wait_for_loader
from helpers.ping_checker import ping_until_up

from helpers.wait_for_clickable import wait_for_clickable_and_click
from helpers.user_agent import random_user_agent
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)


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
INVENTORY_URL = "https://app.mercadoturbo.com.br/sistema/anuncio/gerenciador"


def bot(root, driver=None, current_account=None, data_ri=0, is_active=True):
    if not driver:
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        # options.add_argument("--headless")
        options.add_argument(f"user-agent={random_user_agent(root)}")
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(25)

    waiter = WebDriverWait(driver, 10)

    try:
        if not assert_page_to_inventory(driver):
            with open(CREDS_FILE, "r") as f:
                creds = json.load(f)
            driver.get("https://app.mercadoturbo.com.br//login_operador")
            driver.find_element_by_xpath(
                "//input[contains(@id, 'input-conta')]"
            ).send_keys(creds.get("email", "brenoml0921@yahoo.com"))
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

            assert_page_to_inventory(driver)

        accounts = get_accounts(driver)
        current_account = current_account or accounts[1]
        change_accounts(driver, accounts=accounts, to_account=current_account)
        if not is_active:
            change_active_to_passive(driver)

        while True:
            if not INVENTORY_URL in driver.current_url or data_ri % 20 == 0:
                change_accounts(driver, accounts=accounts, to_account=current_account)
                if not (assert_page_to_inventory(driver) or is_active):
                    change_active_to_passive(driver)
                for _ in range(data_ri // 20):
                    next_btn = driver.find_elements_by_css_selector(
                        "a.ui-paginator-next"
                    )[-1]
                    if "ui-state-disabled" not in next_btn.get_attribute("class"):
                        mt_wait_for_loader(
                            driver,
                            lambda: wait_for_clickable_and_click(
                                next_btn,
                                driver,
                                nonjsclick=True,
                            ),
                        )

            try:
                product = driver.find_element_by_css_selector(
                    f"tr[data-ri='{str(data_ri)}']"
                )
                data_ri += 1
            except NoSuchElementException:
                if not assert_page_to_inventory(driver):
                    bot(
                        root,
                        driver=driver,
                        current_account=current_account,
                        data_ri=data_ri,
                        is_active=is_active,
                    )
                data_ri = 0
                if is_active:
                    is_active = False
                    change_active_to_passive(driver)

                else:
                    is_active = True
                    current_account = change_accounts(driver, accounts)

                page_1_btns = driver.find_elements_by_css_selector(
                    "a.ui-paginator-page[aria-label='Page 1']"
                )
                if len(page_1_btns) and "ui-state-active" not in page_1_btns[
                    0
                ].get_attribute("class"):
                    mt_wait_for_loader(
                        driver,
                        lambda: wait_for_clickable_and_click(
                            driver.find_element_by_css_selector(
                                "a.ui-paginator-page[aria-label='Page 1']"
                            ),
                            driver,
                            nonjsclick=True,
                        ),
                    )

                continue
            try:
                update_single(driver, product)
            except Exception as e:
                print("error changing values here. but we continue")

    except Exception as e:
        driver.quit()
        bot(
            root,
            current_account=current_account,
            data_ri=data_ri,
            is_active=is_active,
        )


def assert_page_to_inventory(driver):
    if not INVENTORY_URL in driver.current_url:
        driver.get(INVENTORY_URL)
        return False
    return True


def update_single(driver, product):
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
    price = round((price * (1 + PRICE_PERCENT / 100)), 2)
    if float(price) < 7:
        price = str(7)
    price = str(price).replace(".", ",")
    stock = str(QTY) if is_available else "0"

    if current_stock != stock or price != current_price:
        wait_for_clickable_and_click(
            product.find_element_by_class_name("cellEdit").find_element_by_class_name(
                "ui-row-editor-pencil"
            ),
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
        mt_wait_for_loader(
            driver,
            lambda: wait_for_clickable_and_click(
                product.find_element_by_class_name(
                    "cellEdit"
                ).find_element_by_class_name("ui-row-editor-check"),
                driver,
            ),
        )


def change_active_to_passive(driver):
    state_active_to_paused_changer = ActionChains(driver)
    state_active_to_paused_changer.send_keys(Keys.ARROW_DOWN)
    state_active_to_paused_changer.send_keys(Keys.ENTER)

    wait_for_clickable_and_click(
        driver.find_element_by_xpath(
            "//h4[contains(., 'Status:')]/following-sibling::div[@role='combobox']"
        ),
        driver,
        nonjsclick=True,
    )
    mt_wait_for_loader(
        driver,
        lambda: state_active_to_paused_changer.perform(),
    )
    mt_wait_for_loader(
        driver,
        lambda: driver.find_element_by_css_selector(
            "input[placeholder='Buscar por']"
        ).send_keys(Keys.ENTER),
    )


def update_single_test_without_scrape(driver, product):
    wait_for_clickable_and_click(
        product.find_element_by_class_name("cellEdit").find_element_by_class_name(
            "ui-row-editor-pencil"
        ),
        driver,
    )
    mt_wait_for_loader(
        driver,
        lambda: wait_for_clickable_and_click(
            product.find_element_by_class_name("cellEdit").find_element_by_class_name(
                "ui-row-editor-check"
            ),
            driver,
        ),
    )
    return
