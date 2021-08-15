import platform
import time
from tkinter import Tk
from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys


# print platform
# print(platform.system())


#     for line_count, row in enumerate(feeder):
#         # if line_count == 0:
#         print(f'Column names are {", ".join(row)}')
#         print(row["link"])


def bot(details):
    # item link
    # item_url = (
    #     "https://www.belezanaweb.com.br/lancome-monsieur-big-mascara-para-cilios-10ml/"
    # )
    # item_sku = None
    # item_qty = 2
    # cep_address = "04267-010"
    # email = "xefami4535@cfcjy.com"
    # first_name = "Fernando"
    # last_name = "Souza"
    # cpf = "12528802781"
    # birthdate = "22/05/1978"
    # telephone = "11954741101"
    # password = cpf + last_name
    # gender = "M"
    gender_dict = {
        "F": "female",
        "M": "male",
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
    # number = 3
    # complement = "complementario"

    options = Options()
    PROXY = "23.23.23.23:3128"
    options.add_argument("--proxy-server=%s" % PROXY)
    # opera_profile = "/home/zeph/.config/opera"
    # options.add_argument("user-data-dir=" + opera_profile)
    # driver = webdriver.Opera(options=options)
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    try:
        # get new temporary email
        driver.get("https://10minutemail.net")
        email = driver.find_element_by_id("fe_text").get_attribute("value")

        # open new tab
        # driver.execute_script("window.open('');")
        # driver.switch_to.window(driver.window_handles[1])

        # go to item details page
        driver.get(details["link"])
        # driver.get(item_url)

        # get item sku
        item_sku = driver.find_element_by_xpath(
            "//meta[@property='product:retailer_item_id']"
        ).get_attribute("content")

        # get item checkout link and go to the link
        buy_btn = driver.find_element_by_css_selector(
            "a[href^='https://checkout.belezanaweb.com.br/sacola?skus=']"
        )
        driver.get(buy_btn.get_attribute("href"))

        # enter cep_address code
        driver.find_element_by_id("postalCode").send_keys(details["cep"])

        # get quantity select dropdown and select desired value
        Select(
            driver.find_element_by_css_selector(
                f"select[data-cy='SelectItem'][name='{item_sku}']"
            )
        ).select_by_value(f"{details['quantity']}")
        time.sleep(5)

        # proceed to checkout
        driver.find_element_by_css_selector("a[data-cy='ProceedCheckout']").click()

        # email in login form
        driver.find_element_by_id("email").send_keys(email)
        time.sleep(2)
        driver.find_element_by_css_selector("button[type='submit']").click()
        # time.sleep(5)

        # if already signed up
        if len(driver.find_elements_by_css_selector("button[data-cy='RegisterUser']")):
            driver.find_element_by_id("givenName").send_keys(
                details["customer_first_name"]
            )
            driver.find_element_by_id("familyName").send_keys(
                details["customer_last_name"]
            )
            driver.find_element_by_id("cpf").send_keys(details["cpf"])
            driver.find_element_by_id("birthDate").send_keys(
                details["birthdate"].replace("/", "")
            )
            driver.find_element_by_id("telephone").send_keys(details["telephone"])
            driver.find_element_by_id("password").send_keys(
                details["customer_email_password"]
            )
            time.sleep(2)
            gender_value = gender_dict[details["gender"]]
            driver.find_element_by_css_selector(f"label[for='{gender_value}']").click()

            # submit register form
            driver.find_element_by_id("password").send_keys(Keys.ENTER)
            # the step below has some issue, so the above statement is workaround.
            # driver.find_element_by_css_selector("button[data-cy='RegisterUser']").click()
        else:
            driver.find_element_by_id("password").send_keys(details["password"])
            driver.find_element_by_css_selector("button[type='submit']").click()
        # sacola form complete

        # endereco form start
        # if current address label is already saved
        address_label = details["address_label"]
        if len(driver.find_elements_by_xpath(f"//span[.='{address_label}']")):
            address_card = driver.find_element_by_xpath(
                # f"//li[./label/span.='{address_label}']"
                f"//li[.//*[text()='{address_label}']]"
            )
            address_card.click()
            address_card.find_element_by_xpath(".//div/button").click()

        else:
            # if not saved and there is another address card, trigger new form
            if len(driver.find_elements_by_css_selector("label[for='addAddress']")):
                driver.find_element_by_css_selector("label[for='addAddress']").click()
            # this is the first one being saved, sending directly to form
            driver.find_element_by_id("label").send_keys(details["address_label"])
            driver.find_element_by_id("postalCode").send_keys(details["cep"])

            driver.find_element_by_id("number").send_keys(details["number"])
            Select(driver.find_element_by_id("addressType")).select_by_value(
                f"{address_type_dict[details['address_label'].lower()]}"
            )
            driver.find_element_by_id("complement").send_keys(details["complement"])
            driver.find_element_by_css_selector("button[type='submit']").click()

        # endereco form complete
        # pagamento form start
        time.sleep(5)
        driver.find_element_by_css_selector("label[for='BOLETO']").click()
        time.sleep(5)
        driver.find_element_by_css_selector("button[data-cy='ProceedSuccess']").click()
        order_number = driver.find_element_by_css_selector(
            "span[data-cy='OrderNumber']"
        ).text
        print(f"Order number: {order_number}")

        # driver.switch_to.window(driver.window_handles[0])
        # driver.get("https://10minutemail.net")
        # driver.find_element_by_partial_link_text("10 Minute Mail").click()
        # driver.find_element_by_partial_link_text(order_number).click()
        # order_link = driver.find_element_by_partial_link_text(order_number).get_attribute(
        #     "href"
        # )
        # print(order_link)

        order_link = f"https://meurastre.io/rastreio/{order_number}"
        driver.get(order_link)

        return order_link

    except Exception as e:
        print(e)
        raise e

    finally:
        driver.quit()
