import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def get_accounts(driver):
    ac_dropdown = driver.find_element_by_css_selector(
        "div.SelectConta[role='combobox']"
    )
    ac_dropdown_options = [
        o.get_attribute("textContent").strip()
        for o in ac_dropdown.find_element_by_css_selector(
            "select"
        ).find_elements_by_tag_name("option")
    ]

    return ac_dropdown_options


def change_accounts(driver, accounts=None):
    if accounts is None:
        accounts = get_accounts(driver)

    ac_dropdown = driver.find_element_by_css_selector(
        "div.SelectConta[role='combobox']"
    )

    ac_dropdown.click()

    ac_dropdown_selected = ac_dropdown.find_element_by_css_selector(
        "label.ui-inputfield"
    )
    current_selected = ac_dropdown_selected.text
    to_select = accounts[(accounts.index(current_selected) + 1) % len(accounts)]

    while True:
        active_selected = ac_dropdown_selected.text
        actions = ActionChains(driver)
        actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        if ac_dropdown_selected.text.strip() in to_select:
            actions_submit = ActionChains(driver)
            actions_submit.send_keys(Keys.ENTER)
            actions_submit.perform()
            break
        if ac_dropdown_selected.text == active_selected:
            actions_submit = ActionChains(driver)
            actions_submit.send_keys(Keys.ARROW_UP * len(accounts))
            actions_submit.send_keys(Keys.ENTER)
            actions_submit.perform()
            break

    time.sleep(5)
