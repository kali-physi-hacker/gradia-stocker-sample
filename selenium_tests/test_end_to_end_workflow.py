from django.contrib.auth.models import User

from selenium.webdriver.support.ui import Select

from customers.models import Entity
from grading.models import Parcel, Receipt
from ownerships.models import ParcelTransfer, StoneTransfer
from purchases.models import Parcel, Receipt, Seller

from test_admin_page_receptionist import customer_page_mixin

from functools import partial

import pytest

    
def test_end_to_end_workflow(browser, customer_page_mixin, receptionist, vault_manager, grader, data_entry_clerk):
    
      #################################################################
     ##1. client gives us stones, we open a receipt with one parcel ##
    #################################################################

    browser.login(receptionist.username, receptionist.raw_password)
    browser.create_customer()
    browser.go_to_customer_page()
    browser.search_in_admin_list_view("Van Klaren")
    browser.assert_body_contains_text("1 entity")
    browser.find_element_by_link_text("Van Klaren")
    browser.go_to_receipt_page()
    browser.click_add()
    customer_dropdown = Select(browser.find_element_by_id("id_entity"))
    customer_dropdown.select_by_visible_text("Van Klaren")
    browser.find_element_by_name("code").send_keys("VK20200723")
    browser.click_add()
    browser.find_element_by_name("parcel_set-0-gradia_parcel_code").send_keys("VK20200723-1")
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys("500")
    browser.click_save()
    browser.logout()


      #################################################################
     ## 2. vault gives parcel to grader                             ##
    #################################################################


    browser.login(vault_manager.username, vault_manager.raw_password)
    browser.go_to_parcel_page()
    vault_filter = browser.find_element_by_link_text("With the vault")
    browser.slowly_click(vault_filter)
    browser.find_element_by_partial_link_text("VK20200723-1")
    browser.assert_body_contains_text(f"vault, unconfirmed")
    confirm_link = browser.find_element_by_link_text("Confirm Stones for Vault")
    browser.slowly_click(confirm_link)
    browser.assert_body_contains_text("You are about to confirm")
    proceed_button = browser.find_element_by_name("proceed")
    browser.slowly_click(proceed_button)
    browser.go_to_parcel_page()
    vault_filter = browser.find_element_by_link_text("With the vault")
    browser.assert_body_contains_text(f"vault, confirmed")
    
    
    browser.go_to_split_page()
    browser.click_add()
    parcel_dropdown = Select(browser.find_element_by_id("id_original_parcel"))
    parcel_dropdown.select_by_visible_text("parcel VK20200723-1 (1.000ct, 1pcs, receipt VK20200723)")
    add_link = browser.find_element_by_link_text("Add another Parcel")
    add_link.click()
    browser.find_element_by_name("parcel_set-0-gradia_parcel_code").send_keys("VK20200723-1A")
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys("500")
    add_link = browser.find_element_by_link_text("Add another Parcel")
    add_link.click()
    browser.find_element_by_name("parcel_set-1-gradia_parcel_code").send_keys("VK20200723-1B")
    browser.find_element_by_name("parcel_set-1-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-1-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-1-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-1-reference_price_per_carat").send_keys("500")
    browser.click_save()


    browser.go_to_transfer_page()
    browser.click_add()
    parcel_dropdown = Select(browser.find_element_by_id("id_item"))
    parcel_dropdown.select_by_visible_text("parcel VK20200723-1A (1.000ct, 1pcs, receipt VK20200723)")
    to_user_dropdown = Select(browser.find_element_by_id("id_to_user"))
    to_user_dropdown.select_by_visible_text(str(grader))
    browser.click_save()
    browser.logout()

     #################################################################
     ## 3. Grader confirmed recieved parcel                        ##
    #################################################################

    browser.login(grader.username, grader.raw_password)
    parcel_link = browser.find_element_by_partial_link_text("Parcel")
    browser.slowly_click(parcel_link)
    owner_filter = browser.find_element_by_link_text("With me")
    browser.slowly_click(owner_filter)
    browser.find_element_by_partial_link_text("VK20200723-1A")
    confirm_link = browser.find_element_by_link_text("Confirm Received")
    browser.slowly_click(confirm_link)
    browser.assert_body_contains_text("You are about to confirm")
    proceed_button = browser.find_element_by_name("proceed")
    browser.slowly_click(proceed_button)

     #####################################################################
     ## 4. grader finishes grading  parcel and returns parcel to vault ##                      ##
    ####################################################################

    browser.go_to_parcel_page()
    owner_filter = browser.find_element_by_link_text("With me")
    browser.slowly_click(owner_filter)
    browser.assert_body_contains_text("1 parcel")
    return_link = browser.find_element_by_link_text("Return to Vault")
    browser.slowly_click(return_link)
    browser.assert_body_contains_text("You are about to confirm")
    proceed_button = browser.find_element_by_name("proceed")
    browser.slowly_click(proceed_button)
    browser.logout()

      ####################################################################
     ## 5. vault confirms received parcel                              ##
    ####################################################################


    browser.login(vault_manager.username, vault_manager.raw_password)
    browser.go_to_parcel_page()
    vault_filter = browser.find_element_by_link_text("With the vault")
    browser.slowly_click(vault_filter)
    browser.find_element_by_partial_link_text("VK20200723-1A")
    browser.assert_body_contains_text(f"vault, unconfirmed")
    confirm_link = browser.find_element_by_link_text("Confirm Stones for Vault")
    browser.slowly_click(confirm_link)
    browser.assert_body_contains_text("You are about to confirm")
    proceed_button = browser.find_element_by_name("proceed")
    browser.slowly_click(proceed_button)
    browser.go_to_parcel_page()
    vault_filter = browser.find_element_by_link_text("With the vault")
    browser.assert_body_contains_text(f"vault, confirmed")
    browser.logout()


      ####################################################################
     ## 6. data entry splits parcel into 2 stones                      ##
    ####################################################################


    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)
    parcel_link = browser.find_element_by_link_text("Splits")
    browser.slowly_click(parcel_link)
    browser.click_add()
    parcel_dropdown = Select(browser.find_element_by_id("id_original_parcel"))
    parcel_dropdown.select_by_visible_text("parcel VK20200723-1A (1.000ct, 1pcs, receipt VK20200723)")
    add_link = browser.find_element_by_link_text("Add another Stone")

    for ii in range(2):
        add_link.click()
        grader_dropdown = Select(browser.find_element_by_name(f"stone_set-{ii}-grader_1"))
        grader_dropdown.select_by_visible_text(str(grader))
        browser.find_element_by_name(f"stone_set-{ii}-sequence_number").send_keys("23")
        browser.find_element_by_name(f"stone_set-{ii}-stone_id").send_keys("G12345")
        browser.find_element_by_name(f"stone_set-{ii}-carats").send_keys("2")
        browser.find_element_by_name(f"stone_set-{ii}-color").send_keys("D")
        browser.find_element_by_name(f"stone_set-{ii}-clarity").send_keys("VS2")
        browser.find_element_by_name(f"stone_set-{ii}-fluo").send_keys("a")
        browser.find_element_by_name(f"stone_set-{ii}-culet").send_keys("x")
        browser.find_element_by_name(f"stone_set-{ii}-table_pct").send_keys("10.1")
        browser.find_element_by_name(f"stone_set-{ii}-pavilion_depth_pct").send_keys("10.1")
        browser.find_element_by_name(f"stone_set-{ii}-total_depth_pct").send_keys("10.1")
    browser.click_save()

    browser.logout()


      ####################################################################
     ## 7. vault sends 2 stones to goldway                             ##
    ####################################################################

    browser.login(vault_manager.username, vault_manager.raw_password)

    browser.go_to_stone_page()
    # he sees that there are 3 stones in the vault
    owner_filter = browser.find_element_by_link_text("With the vault")
    browser.slowly_click(owner_filter)
    browser.assert_body_contains_text("2 stones")

    # he ticks the checkbox for the first and second stone
    browser.find_element_by_xpath("//tbody/tr[@class='row1']//input").click()
    browser.find_element_by_xpath("//tbody/tr[@class='row2']//input").click()

    # he selects "send to goldway" from the action dropdown menu
    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Transfer to Goldway")
    browser.click_go()

    browser.logout()

