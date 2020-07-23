from selenium.webdriver.support.ui import Select

from test_admin_page_receptionist import create_entity


def test_buyer_can_take_a_bag_of_stones(browser, buyer):
    # gary the buyer has found a new seller to trade with
    # he goes to add that seller's info
    browser.login(buyer.username, buyer.raw_password)
    browser.go_to_purchases_page()
    browser.slowly_click(browser.find_element_by_link_text("Sellers"))

    seller_details = {
        "name": "seller 1",
        "address": "seller address 1",
        "phone": "12345",
        "email": "seller@seller.com",
    }
    create_entity(browser, seller_details)

    # he sees that a new seller has been created
    browser.go_to_purchases_page()
    browser.slowly_click(browser.find_element_by_link_text("Sellers"))
    browser.assert_body_contains_text("1 seller")
    browser.find_element_by_link_text("seller 1")

    # he then gets 2 bags of stones from them
    # TODO: confirm he gets a physical receipt from them
    # he goes to record this in the ERP
    browser.go_to_purchases_page()
    browser.slowly_click(browser.find_element_by_link_text("Receipts"))
    browser.click_add()

    # he selects Van Klaren from the customer dropdown menu
    customer_dropdown = Select(browser.find_element_by_id("id_entity"))
    customer_dropdown.select_by_visible_text("seller 1")

    # he enters the receipt code
    browser.find_element_by_name("code").send_keys("123456")

    # he adds a new parcel that goes with this receipt
    browser.click_add()
    # there is no gradia parcel code for this
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys("500")

    # he adds another parcel
    browser.click_add()
    browser.find_element_by_name("parcel_set-1-customer_parcel_code").send_keys("002")
    browser.find_element_by_name("parcel_set-1-total_carats").send_keys("2")
    browser.find_element_by_name("parcel_set-1-total_pieces").send_keys("2")
    browser.find_element_by_name("parcel_set-1-reference_price_per_carat").send_keys("500")

    # he saves
    browser.click_save()

    # there is a new receipt created
    browser.go_to_purchases_page()
    browser.slowly_click(browser.find_element_by_link_text("Receipts"))
    browser.search_in_admin_list_view("123456")
    browser.find_element_by_link_text("receipt 123456")

    # there are two parcels created
    browser.go_to_purchases_page()
    browser.slowly_click(browser.find_element_by_link_text("Parcels"))
    browser.find_element_by_link_text("001")
    browser.find_element_by_link_text("002")
