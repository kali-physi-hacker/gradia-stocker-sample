from selenium.webdriver.support.ui import Select

from grading.models import Stone
from test_admin_page_receptionist import customer_page_mixin


def test_end_to_end_workflow(
    browser, customer_page_mixin, receptionist, vault_manager, grader, data_entry_clerk
):

    #################################################################
    # 1. client gives us stones, we open a receipt with one parcel ##
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
    browser.find_element_by_name("parcel_set-0-gradia_parcel_code").send_keys(
        "VK20200723-1"
    )
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys(
        "500"
    )
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
    parcel_dropdown.select_by_visible_text(
        "parcel VK20200723-1 (1.000ct, 1pcs, receipt VK20200723)"
    )
    add_link = browser.find_element_by_link_text("Add another Parcel")
    add_link.click()
    browser.find_element_by_name("parcel_set-0-gradia_parcel_code").send_keys(
        "VK20200723-1A"
    )
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys(
        "500"
    )
    add_link = browser.find_element_by_link_text("Add another Parcel")
    add_link.click()
    browser.find_element_by_name("parcel_set-1-gradia_parcel_code").send_keys(
        "VK20200723-1B"
    )
    browser.find_element_by_name("parcel_set-1-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-1-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-1-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-1-reference_price_per_carat").send_keys(
        "500"
    )
    browser.click_save()

    browser.go_to_transfer_page()
    browser.click_add()
    parcel_dropdown = Select(browser.find_element_by_id("id_item"))
    parcel_dropdown.select_by_visible_text(
        "parcel VK20200723-1A (1.000ct, 1pcs, receipt VK20200723)"
    )
    to_user_dropdown = Select(browser.find_element_by_id("id_to_user"))
    to_user_dropdown.select_by_visible_text(str(grader))
    browser.click_save()
    browser.logout()

    #################################################################
    ## 3. Grader confirmed received parcel                        ##
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

    ####################################################################
    ## 4. grader finishes grading  parcel and returns parcel to vault ##
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
    parcel_dropdown.select_by_visible_text(
        "parcel VK20200723-1A (1.000ct, 1pcs, receipt VK20200723)"
    )
    add_link = browser.find_element_by_link_text("Add another Stone")

    add_link.click()
    grader_dropdown = Select(browser.find_element_by_name(f"stone_set-0-grader_1"))
    grader_dropdown.select_by_visible_text(str(grader))
    browser.find_element_by_name(f"stone_set-0-sequence_number").send_keys("23")
    browser.find_element_by_name(f"stone_set-0-stone_id").send_keys("G00000001")
    browser.find_element_by_name(f"stone_set-0-carats").send_keys("0.093")
    browser.find_element_by_name(f"stone_set-0-measurement").send_keys(
        "2.90-2.92x1.777mm"
    )
    browser.find_element_by_name(f"stone_set-0-color").send_keys("D")
    browser.find_element_by_name(f"stone_set-0-clarity").send_keys("VS2")
    browser.find_element_by_name(f"stone_set-0-fluo").send_keys("a")
    browser.find_element_by_name(f"stone_set-0-culet").send_keys("VS")
    browser.find_element_by_name(f"stone_set-0-symmetry").send_keys("VG")
    browser.find_element_by_name(f"stone_set-0-polish").send_keys("EX")
    browser.find_element_by_name(f"stone_set-0-cut").send_keys("VG")
    browser.find_element_by_name(f"stone_set-0-total_depth_pct").send_keys("61.1")
    browser.find_element_by_name(f"stone_set-0-pavilion_depth_pct").send_keys("43")
    browser.find_element_by_name(f"stone_set-0-table_pct").send_keys("58")
    browser.find_element_by_name(f"stone_set-0-crown_angle").send_keys("33.5")

    add_link.click()
    grader_dropdown = Select(browser.find_element_by_name(f"stone_set-1-grader_1"))
    grader_dropdown.select_by_visible_text(str(grader))
    browser.find_element_by_name(f"stone_set-1-sequence_number").send_keys("23")
    browser.find_element_by_name(f"stone_set-1-stone_id").send_keys("G12346")
    browser.find_element_by_name(f"stone_set-1-carats").send_keys("2")
    browser.find_element_by_name(f"stone_set-1-measurement").send_keys(
        "2.90-2.92x1.777mm"
    )
    browser.find_element_by_name(f"stone_set-1-color").send_keys("D")
    browser.find_element_by_name(f"stone_set-1-clarity").send_keys("VS2")
    browser.find_element_by_name(f"stone_set-1-fluo").send_keys("a")
    browser.find_element_by_name(f"stone_set-1-culet").send_keys("x")
    browser.find_element_by_name(f"stone_set-1-symmetry").send_keys("VG")
    browser.find_element_by_name(f"stone_set-1-polish").send_keys("EX")
    browser.find_element_by_name(f"stone_set-1-cut").send_keys("VG")
    browser.find_element_by_name(f"stone_set-1-total_depth_pct").send_keys("61.1")
    browser.find_element_by_name(f"stone_set-1-pavilion_depth_pct").send_keys("43")
    browser.find_element_by_name(f"stone_set-1-table_pct").send_keys("58")
    browser.find_element_by_name(f"stone_set-1-crown_angle").send_keys("33.5")

    browser.click_save()

    browser.logout()

    ####################################################################
    ## 7. vault sends 2 stones to goldway                             ##
    ####################################################################

    browser.login(vault_manager.username, vault_manager.raw_password)
    browser.go_to_stone_page()

    owner_filter = browser.find_element_by_link_text("With the vault")
    browser.slowly_click(owner_filter)
    browser.assert_body_contains_text("2 stones")

    stone = Stone.objects.get(stone_id="G00000001")
    browser.find_element_by_css_selector(f'input[value="{stone.id}"]').click()
    stone2 = Stone.objects.get(stone_id="G12346")
    browser.find_element_by_css_selector(f'input[value="{stone2.id}"]').click()

    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Transfer to Goldway")
    browser.click_go()

    browser.logout()

    ####################################################################
    ## 8. someone confirms goldway has received stones                ##
    ####################################################################

    ####################################################################
    ## 9. goldway is ready to send us back stuff                      ##
    ####################################################################

    ####################################################################
    ## 10. when it comes back vault can confirm it                    ##
    ####################################################################

    ####################################################################
    ## 11. ditto for GIA                                              ##
    ####################################################################

    ####################################################################
    ## 12. vault transfers stones to receptionist                     ##
    ####################################################################
