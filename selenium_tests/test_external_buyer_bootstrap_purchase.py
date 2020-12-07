from selenium.webdriver.support.ui import Select

import pytest
from customer_page_mixin import create_entity
from purchases.models import Parcel, Receipt, Seller


@pytest.fixture
def purchases_receipt(django_user_model, admin_user):
    created_receipt = Receipt.objects.create(
        entity=Seller.objects.create(
            name="Van Klaren", address="addressy", phone="12345678", email="vk@vk.com"
        ),
        code="VK-0001",
        intake_by=admin_user,
    )
    Parcel.objects.create(
        receipt=created_receipt,
        customer_parcel_code="cust-parcel-1",
        total_carats=2,
        total_pieces=2,
        reference_price_per_carat=1,
    )
    Parcel.objects.create(
        receipt=created_receipt,
        customer_parcel_code="cust-parcel-2",
        total_carats=2,
        total_pieces=2,
        reference_price_per_carat=1,
    )
    return created_receipt


def test_buyer_can_setup_new_sellers_and_take_in_a_bag_of_stones(browser, buyer):
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
    browser.click_add(should_disappear=False)
    # there is no gradia parcel code for this
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys(
        "500"
    )

    # he adds another parcel
    browser.click_add(should_disappear=False)
    browser.find_element_by_name("parcel_set-1-customer_parcel_code").send_keys("002")
    browser.find_element_by_name("parcel_set-1-total_carats").send_keys("2")
    browser.find_element_by_name("parcel_set-1-total_pieces").send_keys("2")
    browser.find_element_by_name("parcel_set-1-reference_price_per_carat").send_keys(
        "500"
    )

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


def test_buyer_can_mark_rejected_stones(browser, buyer, purchases_receipt):
    # buyer Gary has previously taken two parcels from the seller
    # currently there is an open receipt
    assert purchases_receipt.closed_out() is False

    # he is now ready to mark how many stones are rejected
    browser.login(buyer.username, buyer.raw_password)

    # he goes to the first parcel
    browser.go_to_purchases_page()
    browser.slowly_click(browser.find_element_by_link_text("Parcels"))
    parcel1 = purchases_receipt.parcel_set.first()
    browser.slowly_click(
        browser.find_element_by_link_text(parcel1.customer_parcel_code)
    )

    # and enters the rejection info
    browser.find_element_by_name("rejected_carats").send_keys("2")
    browser.find_element_by_name("rejected_pieces").send_keys("2")
    browser.find_element_by_name("total_price_paid").send_keys("2")
    browser.click_save()

    # he goes to the second parcel
    browser.go_to_purchases_page()
    browser.slowly_click(browser.find_element_by_link_text("Parcels"))
    parcel2 = purchases_receipt.parcel_set.last()
    browser.slowly_click(
        browser.find_element_by_link_text(parcel2.customer_parcel_code)
    )

    # and enters the rejection info
    browser.find_element_by_name("rejected_carats").send_keys("2")
    browser.find_element_by_name("rejected_pieces").send_keys("2")
    browser.find_element_by_name("total_price_paid").send_keys("2")
    browser.click_save()

    # now the seller has come to pick up the rejections
    # the seller  gives back the receipt
    # Gary closes the receipt in the ERP
    browser.go_to_purchases_page()
    browser.slowly_click(browser.find_element_by_link_text("Receipts"))
    browser.slowly_click(browser.find_element_by_link_text("Close Out"))

    # He clicks confirm
    browser.assert_body_contains_text("You are about to close out the receipt")
    proceed_button = browser.find_element_by_name("proceed")
    browser.slowly_click(proceed_button)

    # now the receipt is closed out
    purchases_receipt.refresh_from_db()
    assert purchases_receipt.closed_out() is True
