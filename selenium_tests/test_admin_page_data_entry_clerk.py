from selenium.webdriver.support.ui import Select


def test_data_entry_can_split_parcel_to_stones(browser, data_entry_clerk, grader, receipt):
    # Yuki is a data entry clerk
    # there is a parcel that a grader has finished grading and has returned to
    # the vault
    parcel = receipt.parcel_set.first()

    # she logs in to the admin portal
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    # she goes to add a split
    parcel_link = browser.find_element_by_link_text("Splits")
    browser.slowly_click(parcel_link)
    browser.click_add()

    # she selects the correct parcel to split on
    parcel_dropdown = Select(browser.find_element_by_id("id_original_parcel"))
    parcel_dropdown.select_by_visible_text(str(parcel))

    # she adds one stone
    add_link = browser.find_element_by_link_text("Add another Stone")
    add_link.click()

    grader_dropdown = Select(browser.find_element_by_name("stone_set-0-grader_1"))
    grader_dropdown.select_by_visible_text(str(grader))
    browser.find_element_by_name("stone_set-0-sequence_number").send_keys("23")
    browser.find_element_by_name("stone_set-0-stone_id").send_keys("G12345")
    browser.find_element_by_name("stone_set-0-carats").send_keys("2")
    browser.find_element_by_name("stone_set-0-color").send_keys("D")
    browser.find_element_by_name("stone_set-0-clarity").send_keys("VS2")
    browser.find_element_by_name("stone_set-0-fluo").send_keys("a")
    browser.find_element_by_name("stone_set-0-culet").send_keys("x")

    # she adds another stone
    add_link.click()
    grader_dropdown = Select(browser.find_element_by_name("stone_set-1-grader_1"))
    grader_dropdown.select_by_visible_text(str(grader))
    browser.find_element_by_name("stone_set-1-sequence_number").send_keys("23")
    browser.find_element_by_name("stone_set-1-stone_id").send_keys("G12345")
    browser.find_element_by_name("stone_set-1-carats").send_keys("2")
    browser.find_element_by_name("stone_set-1-color").send_keys("D")
    browser.find_element_by_name("stone_set-1-clarity").send_keys("VS2")
    browser.find_element_by_name("stone_set-1-fluo").send_keys("a")
    browser.find_element_by_name("stone_set-1-culet").send_keys("x")

    # she saves
    browser.click_save()

    # now the parcel shows up as having been split
    browser.go_to_parcel_page()
    browser.assert_body_contains_text(f"split, unconfirmed")
    # and we can see stones in the vault
    browser.go_to_stone_page()
    browser.assert_body_contains_text(f"vault, confirmed")
