# _*_ coding: utf-8 _*_
import re
import time

from selenium.webdriver.support import expected_conditions as EC

from controllers.bots.helpers.mercado_accounts import change_accounts
from controllers.bots.helpers.messages import msg_reader
from controllers.bots.helpers.webdriver import get_bot_driver, driver_setup_mercado
from helpers.mt_wait_for_loader import mt_wait_for_loader
from helpers.wait_for_clickable import wait_for_clickable_and_click

DIGIT_REGEX = re.compile(r"\d+")


class regex_text_to_be_present_in_element(EC.text_to_be_present_in_element):
    def __call__(self, driver):
        try:
            matched = DIGIT_REGEX.match(
                EC._find_element(driver, self.locator).get_attribute("innerHTML")
            )

            return matched is not None
        except EC.StaleElementReferenceException:
            return False


def bot(root, driver=None):
    MESSAGE_TEXT = msg_reader()

    if driver is None:
        driver, waiter = get_bot_driver(root)
    try:
        driver, accounts = driver_setup_mercado(driver)

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

        for account in accounts:
            driver.get("https://app.mercadoturbo.com.br/sistema/mensagem/conversacoes_novo")
            reply_messages()
            change_accounts(driver, accounts, to_account=account)

        print("everything done.")

    except Exception as e:
        print(e)
        return "system error", False

    finally:
        print("reply message complete")
        driver.quit()
        bot(root)
