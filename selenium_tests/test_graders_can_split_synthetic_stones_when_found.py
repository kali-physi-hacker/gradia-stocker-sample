from selenium.webdriver.support.ui import Select
from customer_page_mixin import create_customer_browser_mixin  # noqa



def test_graders_can_close_out_rejected_receipts(browser, vault_manager, receptionist, create_customer_browser_mixin, receipt):
    #Kary logs into the admin dashboard
    customer_details = {
        "name": "new_customer",
        "address": "customer_address",
        "phone": "12345",
        "email": "cust@customer.com",
    }

    browser.login(receptionist.username, receptionist.raw_password)

    browser.go_to_customer_page()
    browser.search_in_admin_list_view("new_customer")

    browser.assert_body_contains_text("0 entitys")

    browser.create_customer(customer_details)

    browser.go_to_customer_page()
    browser.search_in_admin_list_view("new_customer")
    browser.assert_body_contains_text("1 entity")
    browser.find_element_by_link_text("new_customer")
    
    browser.go_to_receipt_page()
    browser.click_add()

    customer_dropdown = Select(browser.find_element_by_id("id_entity"))

    customer_dropdown.select_by_visible_text("new_customer")
    browser.find_element_by_name("code").send_keys("receipt1")

    for i in range(3):
        browser.click_add(should_disappear=False)
        browser.find_element_by_name(f"parcel_set-{i}-gradia_parcel_code").send_keys(f'R5022{i+1}')
        browser.find_element_by_name(f"parcel_set-{i}-customer_parcel_code").send_keys("R")
        browser.find_element_by_name(f"parcel_set-{i}-total_carats").send_keys("2")
        browser.find_element_by_name(f"parcel_set-{i}-total_pieces").send_keys("2")
        browser.find_element_by_name(f"parcel_set-{i}-reference_price_per_carat").send_keys("500")
        

    
    browser.click_save()
    browser.logout()
    browser.login(vault_manager.username, vault_manager.raw_password)
    browser.go_to_split_page()
    browser.click_add()
    

    parcel_dropdown = Select(browser.find_element_by_id("id_original_parcel"))
    parcel = receipt.parcel_set.first() #R50221
    parcel_dropdown.select_by_visible_text(str(parcel))

    add_link = browser.find_element_by_link_text("Add another Parcel")
    add_link.click()
    browser.find_element_by_name("parcel_set-0-gradia_parcel_code").send_keys("R50221_passed")
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("R")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys("500")

    add_link = browser.find_element_by_link_text("Add another Parcel")
    add_link.click()
    browser.find_element_by_name("parcel_set-1-gradia_parcel_code").send_keys("R50221_rejected")
    browser.find_element_by_name("parcel_set-1-customer_parcel_code").send_keys("R")
    browser.find_element_by_name("parcel_set-1-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-1-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-1-reference_price_per_carat").send_keys("500")

    browser.click_save()
    browser.go_to_parcel_page()
    
    browser.find_element_by_link_text("R50221_rejected")
    browser.slowly_click(browser.find_element_by_link_text("Close Parcel"))

    browser.assert_body_contains_text("You are about to close out the parcel")
    proceed_button = browser.find_element_by_name("proceed")
    browser.slowly_click(proceed_button)

   