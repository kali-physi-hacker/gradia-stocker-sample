import pytest
from selenium.webdriver.support.ui import Select
from grading.models import Receipt, Parcel
from ownerships.models import ParcelTransfer
from customers.models import Entity


@pytest.fixture
def grading_receipt(django_user_model, vault_manager):
    created_receipt = Receipt.objects.create(
        entity=Entity.objects.create(name="Van Klaren", address="addressy", phone="12345678", email="vk@vk.com"),
        code="KaryReceipt",
        intake_by=vault_manager,
    )
    parcel1 = Parcel.objects.create(
        receipt=created_receipt,
        gradia_parcel_code="R50221",
        customer_parcel_code="VK_01",
        total_carats=2,
        total_pieces=2,
        reference_price_per_carat=1,
    )

    parcel2 = Parcel.objects.create(
        receipt=created_receipt,
        gradia_parcel_code="R50222",
        customer_parcel_code="Vk_02",
        total_carats=4,
        total_pieces=3,
        reference_price_per_carat=1,
    )
    parcel3 = Parcel.objects.create(
        receipt=created_receipt,
        gradia_parcel_code="R50223",
        customer_parcel_code="VK_03",
        total_carats=1,
        total_pieces=1,
        reference_price_per_carat=1,
    )
    ParcelTransfer.objects.create(
        item=parcel1,
        from_user=vault_manager,
        to_user=django_user_model.objects.get(username="vault"),
        created_by=vault_manager,
    )

    ParcelTransfer.objects.create(
        item=parcel2,
        from_user=vault_manager,
        to_user=django_user_model.objects.get(username="vault"),
        created_by=vault_manager,
    )
    ParcelTransfer.objects.create(
        item=parcel3,
        from_user=vault_manager,
        to_user=django_user_model.objects.get(username="vault"),
        created_by=vault_manager,
    )
    # vault confirms it has received this parcel
    ParcelTransfer.confirm_received(parcel1)
    created_receipt.parcel_set.add(parcel1)
    ParcelTransfer.confirm_received(parcel2)
    created_receipt.parcel_set.add(parcel2)
    ParcelTransfer.confirm_received(parcel3)
    created_receipt.parcel_set.add(parcel3)
    return created_receipt


def test_graders_can_close_out_a_rejected_parcel(browser, vault_manager, grading_receipt):
    browser.login(vault_manager.username, vault_manager.raw_password)
    browser.go_to_split_page()
    browser.click_add()

    # we now realize that we need to reject some stones in the parcel.
    parcel_dropdown = Select(browser.find_element_by_id("id_original_parcel"))

    # our target parcel is the first parcel R50221
    target_parcel = grading_receipt.parcel_set.first()  

    #anthony select the parcel which had be rejected, that is the target parcel
    parcel_dropdown.select_by_visible_text(str(target_parcel))

    #anthony splits the target_parcel into smaller sub_parcels with
    #anthony adds the passed_parcel details
    add_link = browser.find_element_by_link_text("Add another Parcel")
    add_link.click()
    browser.find_element_by_name("parcel_set-0-gradia_parcel_code").send_keys("R50221_passed")
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("Vk_02")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys("500")

    #adds the rejected_parcel details
    add_link = browser.find_element_by_link_text("Add another Parcel")
    add_link.click()
    browser.find_element_by_name("parcel_set-1-gradia_parcel_code").send_keys("R50221_rejected")
    browser.find_element_by_name("parcel_set-1-customer_parcel_code").send_keys("Vk_02")
    browser.find_element_by_name("parcel_set-1-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-1-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-1-reference_price_per_carat").send_keys("500")
    browser.click_save()

    # anthony goes to the parcel page
    browser.go_to_parcel_page()

    #anthony find the rejected_parcels and close it out
    browser.find_element_by_link_text("R50221_rejected")
    browser.slowly_click(browser.find_element_by_link_text("Close Parcel"))

    #anthony confirms that he wants to close out and click proceed
    browser.assert_body_contains_text("You are about to close out the parcel")
    proceed_button = browser.find_element_by_name("proceed")
    browser.slowly_click(proceed_button)

    #after anthony clicks on proceed, a page shows up with details showing that parcel is closed

    #last parcel is the rejected parcel
    rejected_parcel = grading_receipt.parcel_set.last() 
    rejected_parcel.refresh_from_db()

    #checks if rejected parcel closed out is True
    assert rejected_parcel.closed_out() is True
