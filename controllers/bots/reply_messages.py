import json
import time
import re

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
from helpers.file_system import CREDS_FILE
from helpers.mt_wait_for_loader import mt_wait_for_loader
from helpers.post_remark import post_remarks
from helpers.wait_for_clickable import wait_for_clickable_and_click
from helpers.user_agent import random_user_agent

DIGIT_REGEX = re.compile(r"\d+")
MESSAGE_TEXT = """
Hello,
This is a test message.

Send message here.
"""


class regex_text_to_be_present_in_element(EC.text_to_be_present_in_element):
    def __call__(self, driver):
        try:
            matched = DIGIT_REGEX.match(
                EC._find_element(driver, self.locator).get_attribute("innerHTML")
            )

            return matched != None
        except EC.StaleElementReferenceException:
            return False


def bot(root, details=None, driver=None):
    WAIT_TIME = 25
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

        def reply_messages():
            messages = driver.find_element_by_id(
                "form-mensagens:data-scroller-mensagens_data"
            ).find_elements_by_css_selector("tr")
            for message in messages:
                if "empty" in message.get_attribute("class"):
                    continue  # not found
                mt_wait_for_loader(  # open message
                    driver,
                    lambda: wait_for_clickable_and_click(
                        message.find_element_by_css_selector(".container-mensagem > a"),
                        driver,
                    ),
                )
                driver.find_element_by_id(  # type default text message
                    "form-chat-mensagens:input-mensagem-conversa"
                ).send_keys(MESSAGE_TEXT.strip())
                wait_for_clickable_and_click(  # send
                    driver.find_element_by_css_selector("button.btn-enviar-mensagem"),
                    driver,
                )
                time.sleep(1)  # wait for message to be sent
                wait_for_clickable_and_click(  # click on mark as read
                    driver.find_element_by_id("form-chat-mensagens:marcar-como-lido"),
                    driver,
                )

        for _ in accounts:
            driver.get(
                "https://app.mercadoturbo.com.br/sistema/mensagem/conversacoes_novo"
            )

            reply_messages()

            change_accounts(driver, accounts)

        print("everything done.")

    except Exception as e:
        print(e)
        return "system error", False

    finally:
        print("reply message complete")
        if not using_param_driver:
            driver.quit()
        bot(root)
