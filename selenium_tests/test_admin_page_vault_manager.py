from django.contrib.auth.models import User

from selenium.webdriver.support.ui import Select

from customers.models import Entity
from grading.models import Parcel, Receipt
from ownerships.models import ParcelTransfer


def test_vault_manager_can_confirm_parcels_transferred_to_the_vault(browser, admin_user, vault_manager):
    created_receipt = Receipt.objects.create(
        entity=Entity.objects.create(name="Van Klaren", address="addressy", phone="12345678", email="vk@vk.com"),
        code="VK-0001",
        intake_by=admin_user,
    )
    parcel = Parcel.objects.create(
        receipt=created_receipt,
        gradia_parcel_code="parcel1",
        customer_parcel_code="cust-parcel-1",
        total_carats=2,
        total_pieces=2,
        reference_price_per_carat=1,
    )
    # the parcel is received by admin user and put into the vault
    ParcelTransfer.objects.create(item=parcel, from_user=admin_user, to_user=User.objects.get(username="vault"))

    # as vaultmanager, Anthony can confirm that vault has received this parcel
    browser.login(vault_manager.username, vault_manager.raw_password)
    browser.go_to_parcel_page()
    vault_filter = browser.find_element_by_link_text("With the vault")
    browser.slowly_click(vault_filter)
    browser.find_element_by_partial_link_text(parcel.gradia_parcel_code)
    browser.assert_body_contains_text(f"vault, unconfirmed")

    # and there is an action button prompting her to confirm she received the parcel
    confirm_link = browser.find_element_by_link_text("Confirm Stones for Vault")
    browser.slowly_click(confirm_link)
    browser.assert_body_contains_text("You are about to confirm")
    proceed_button = browser.find_element_by_name("proceed")
    browser.slowly_click(proceed_button)

    browser.go_to_parcel_page()
    vault_filter = browser.find_element_by_link_text("With the vault")
    browser.assert_body_contains_text(f"vault, confirmed")


def test_vault_manager_can_split_parcels_to_smaller_parcels(browser, receipt, vault_manager):
    # there is a parcel in the vault- it is too large
    parcel = receipt.parcel_set.first()

    # as vaultmanager, Anthony can split this parcel
    browser.login(vault_manager.username, vault_manager.raw_password)
    browser.go_to_split_page()
    browser.click_add()

    # he selects the correct parcel to split on
    parcel_dropdown = Select(browser.find_element_by_id("id_original_parcel"))
    parcel_dropdown.select_by_visible_text(str(parcel))

    # he adds one sub-parcel
    add_link = browser.find_element_by_link_text("Add another Parcel")
    add_link.click()
    browser.find_element_by_name("parcel_set-0-gradia_parcel_code").send_keys("VK20200723-1A")
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys("500")

    # he adds another sub-parcel
    add_link = browser.find_element_by_link_text("Add another Parcel")
    add_link.click()
    browser.find_element_by_name("parcel_set-1-gradia_parcel_code").send_keys("VK20200723-1B")
    browser.find_element_by_name("parcel_set-1-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-1-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-1-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-1-reference_price_per_carat").send_keys("500")

    # he saves
    browser.click_save()

    # now the original parcel shows up as split
    browser.go_to_parcel_page()
    browser.search_in_admin_list_view(parcel.gradia_parcel_code)
    browser.assert_body_contains_text("split, unconfirmed")
    # and there are two new subparcels owned by vault
    browser.search_in_admin_list_view("VK20200723-1A")
    browser.assert_body_contains_text("vault, confirmed")
    browser.search_in_admin_list_view("VK20200723-1B")
    browser.assert_body_contains_text("vault, confirmed")


def test_vault_manager_can_transfer_vault_parcels_to_others(browser, receipt, vault_manager, grader):
    # there is a parcel in the vault
    parcel = receipt.parcel_set.first()

    # Anthony the vault manager wants to transfer it to Gary the grader
    browser.login(vault_manager.username, vault_manager.raw_password)

    browser.go_to_transfer_page()

    browser.click_add()

    # he selects the correct parcel to transfer
    parcel_dropdown = Select(browser.find_element_by_id("id_item"))
    parcel_dropdown.select_by_visible_text(str(parcel))

    # he selects Gary as the user to transfer to
    to_user_dropdown = Select(browser.find_element_by_id("id_to_user"))
    to_user_dropdown.select_by_visible_text(str(grader))

    # he saves
    browser.click_save()

    # and now the parcel shows up as being with Gary
    browser.go_to_parcel_page()
    browser.assert_body_contains_text("1 parcel")
    browser.assert_body_contains_text(f"{grader}, unconfirmed")


def test_vault_manager_can_initiate_transfer_to_goldway(browser, stones, vault_manager):
    # Anthony the vault manager wants to transfer 2 stones to goldway

    browser.login(vault_manager.username, vault_manager.raw_password)

    browser.go_to_stone_page()
    # he sees that there are 3 stones in the vault
    owner_filter = browser.find_element_by_link_text("With the vault")
    browser.slowly_click(owner_filter)
    browser.assert_body_contains_text("3 stones")

    # he ticks the checkbox for the first stone
    browser.find_element_by_css_selector(f'input[value="{stones[0].id}"]').click()
    # he ticks the checkbox for the second stone
    browser.find_element_by_css_selector(f'input[value="{stones[1].id}"]').click()

    # he selects "send to goldway" from the action dropdown menu
    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Transfer to Goldway")

    browser.click_go()

    # and only one stone is still in the vault
    browser.assert_body_contains_text("1 stone")

    # now two stones show up as in transit to Goldway
    browser.go_to_stone_page()
    owner_filter = browser.find_element_by_link_text("With Goldway")
    browser.slowly_click(owner_filter)
    browser.assert_body_contains_text("2 stones")
