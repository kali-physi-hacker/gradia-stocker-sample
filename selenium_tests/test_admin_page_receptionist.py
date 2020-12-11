from selenium.webdriver.support.ui import Select

from customer_page_mixin import create_customer_browser_mixin  # noqa


def test_receptionist_can_create_new_customer(
    browser, receptionist, create_customer_browser_mixin
):  # noqa
    # Roxy is a receptionist
    # A customer has submitted documents to go through the registration process
    # and the customer has passed KYC and DD
    customer_details = {
        "name": "new_customer",
        "address": "customer_address",
        "phone": "12345",
        "email": "cust@customer.com",
    }

    # Roxy log into the erp portal
    browser.login(receptionist.username, receptionist.raw_password)

    # she goes to checks whether the customer already exists in the system
    browser.go_to_customer_page()
    browser.search_in_admin_list_view("new_customer")

    # and sees that the customer is new and does not exist in the system yet
    browser.assert_body_contains_text("0 entitys")

    # she enters the customer details
    browser.create_customer(customer_details)

    # now the customer shows up in the search
    browser.go_to_customer_page()
    browser.search_in_admin_list_view("new_customer")
    browser.assert_body_contains_text("1 entity")
    browser.find_element_by_link_text("new_customer")


def test_receptionist_can_receive_stones_and_create_a_receipt(
    browser, receptionist, create_customer_browser_mixin  # noqa
):
    browser.login(receptionist.username, receptionist.raw_password)
    # Customer Van Klaren is an old customer
    browser.create_customer()

    # Van Klaren employee Winnie comes in with a bag of stones
    # Roxy the receptionist meets the customer, and checks that the guest is an
    # authorized employee of Van Klaren
    # She searches for the customer name and finds it
    browser.go_to_customer_page()
    browser.search_in_admin_list_view("Van Klaren")
    browser.assert_body_contains_text("1 entity")
    browser.find_element_by_link_text("Van Klaren")

    # TODO: click into customer and check that Winnie the employee is
    # an authorized person for Van Klaren

    # Having checked that, Roxy opens a physical receipt for the customer
    # After the customer has left, Roxy goes to put the receipt data into ERP
    browser.go_to_receipt_page()
    browser.click_add()

    # Roxy selects Van Klaren from the customer dropdown menu
    customer_dropdown = Select(browser.find_element_by_id("id_entity"))

    customer_dropdown.select_by_visible_text("Van Klaren")

    # she enters the receipt code
    browser.find_element_by_name("code").send_keys("VK20200723")

    # she adds a new parcel that goes with this receipt
    browser.click_add(should_disappear=False)
    browser.find_element_by_name("parcel_set-0-gradia_parcel_code").send_keys(
        "VK20200723-1"
    )
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys(
        "500"
    )

    # she saved it
    browser.click_save()

    # the receipt is now shows up
    browser.go_to_receipt_page()
    browser.search_in_admin_list_view("VK20200723")
    browser.find_element_by_link_text("receipt VK20200723")

    # the parcel is now shows up
    browser.go_to_parcel_page()
    browser.search_in_admin_list_view("VK20200723-1")
    browser.find_element_by_link_text("VK20200723-1")
