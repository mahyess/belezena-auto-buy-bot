import csv
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from helpers.file_system import ERROR_FILE, FIELDNAMES


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


def change_accounts(driver, accounts=None, root=None, to_account=None):
    try:
        with open(ERROR_FILE, "w", newline="") as save_file:
            fieldnames = [*FIELDNAMES, "remarks"]
            file_writer = csv.DictWriter(
                save_file, delimiter=",", fieldnames=fieldnames
            )

            file_writer.writeheader()
            print("file cleared")
    except Exception as e:
        print("file clear problem")
    if root:
        root.refresh_ui()
    if accounts is None:
        accounts = get_accounts(driver)

    ac_dropdown = driver.find_element_by_css_selector(
        "div.SelectConta[role='combobox']"
    )

    ac_dropdown_selected = ac_dropdown.find_element_by_css_selector(
        "label.ui-inputfield"
    )
    current_selected = ac_dropdown_selected.text
    to_select = (
        to_account or accounts[(accounts.index(current_selected) + 1) % len(accounts)]
    )
    if current_selected == to_select:
        return current_selected

    ac_dropdown.click()
    while True:
        current_selected = ac_dropdown_selected.text
        actions = ActionChains(driver)
        actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        if ac_dropdown_selected.text.strip() in to_select:
            actions_submit = ActionChains(driver)
            actions_submit.send_keys(Keys.ENTER)
            actions_submit.perform()
            break
        if ac_dropdown_selected.text == current_selected:
            actions_submit = ActionChains(driver)
            actions_submit.send_keys(Keys.ARROW_UP * len(accounts))
            actions_submit.send_keys(Keys.ENTER)
            actions_submit.perform()
            break

    time.sleep(5)
    return to_select
