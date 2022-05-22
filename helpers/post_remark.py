from helpers.wait_for_clickable import wait_for_clickable_and_click


def post_remarks(driver, wrapper_element=None, remarks=None):
    if not wrapper_element:
        wrapper_element = driver

    remarks_input_btn = wrapper_element.find_element_by_id("div-toggle")
    wait_for_clickable_and_click(remarks_input_btn, driver)
    remarks_form = remarks_input_btn.find_element_by_xpath(
        "following-sibling::div"
    )
    remarks_form.find_element_by_xpath(
        ".//div[contains(@class, 'mt-width-full')]/input"
    ).send_keys(remarks)
    wait_for_clickable_and_click(
        remarks_form.find_element_by_css_selector(
            "button[type='submit'][class*='ui-button-success']"
        ),
        driver,
    )
    
    return