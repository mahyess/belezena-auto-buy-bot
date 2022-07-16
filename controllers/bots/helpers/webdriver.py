import time

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from controllers.bots.helpers.creds import get_creds
from controllers.bots.helpers.mercado_accounts import get_accounts
from helpers.user_agent import random_user_agent
from helpers.wait_for_clickable import wait_for_clickable_and_click


def get_bot_driver(root=None):
    """
    Returns a webdriver instance.
    :param root:
    :return: driver instance and a waiter instance
    """
    from main import WAIT_TIME
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={random_user_agent(root)}")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(WAIT_TIME)
    return driver, WebDriverWait(driver, WAIT_TIME)


def driver_setup_mercado(driver):
    from main import WAIT_TIME
    creds = get_creds()
    driver.get("https://app.mercadoturbo.com.br//login_operador")
    driver.find_element_by_xpath("//input[contains(@id, 'input-conta')]").send_keys(
        creds.get("email") or "brenoml0921@yahoo.com"
    )
    driver.find_element_by_xpath(
        "//input[contains(@id, 'input-usuario')]"
    ).send_keys(creds.get("operador") or "operador1")
    driver.find_element_by_css_selector("input[type='password']").send_keys(
        creds.get("password") or "36461529"
    )
    wait_for_clickable_and_click(
        driver.find_element_by_css_selector("button[type='submit']"),
        driver,
        wait_time=WAIT_TIME,
    )
    time.sleep(3)
    return driver, get_accounts(driver)
