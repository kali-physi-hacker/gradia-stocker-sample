from django.contrib.auth.models import User

from selenium.webdriver.support.ui import Select

from ownerships.models import ParcelTransfer, StoneTransfer


def test_grader_can_confirm_received_parcels(browser, grader, receipt):
    # Tanly is a grader
    # the vault has given her a parcel to grade
    parcel = receipt.parcel_set.first()
    vault = User.objects.get(username="vault")
    ParcelTransfer.initiate_transfer(parcel, vault, grader, grader)

    # she logs in to the admin portal
    browser.login(grader.username, grader.raw_password)

    # she has access to view parcels
    parcel_link = browser.find_element_by_partial_link_text("Parcel")
    browser.slowly_click(parcel_link)

    # and sees that there is a parcel when she filters by current owner
    owner_filter = browser.find_element_by_link_text("With me")
    browser.slowly_click(owner_filter)
    browser.find_element_by_partial_link_text(parcel.gradia_parcel_code)
    # and there is an action button prompting her to confirm she received the parcel
    confirm_link = browser.find_element_by_link_text("Confirm Received")

    # offline, she goes and weighs and counts the # of stones
    # after checking that, she clicks confirm
    browser.slowly_click(confirm_link)
    # she is taken to an "are you sure page"
    browser.assert_body_contains_text("You are about to confirm")
    # she clicks proceed
    proceed_button = browser.find_element_by_name("proceed")
    browser.slowly_click(proceed_button)

    # now the parcel shows up as with Tanly, and as confirmed
    browser.go_to_parcel_page()
    owner_filter = browser.find_element_by_link_text("With me")
    browser.slowly_click(owner_filter)
    browser.find_element_by_partial_link_text(parcel.gradia_parcel_code)
    browser.assert_body_contains_text(f"{grader.username}, confirmed")
    # and there is a new action available to her
    browser.find_element_by_link_text("Return to Vault")


def test_grader_can_return_parcel_to_vault(browser, grader, receipt):
    # Tanly is a grader
    # she has a parcel from the vault
    parcel = receipt.parcel_set.first()
    vault = User.objects.get(username="vault")
    ParcelTransfer.initiate_transfer(parcel, vault, grader, grader)
    ParcelTransfer.confirm_received(parcel)

    # she logs in to the admin portal
    browser.login(grader.username, grader.raw_password)
    browser.go_to_parcel_page()

    # she double checks that she owns the parcel
    owner_filter = browser.find_element_by_link_text("With me")
    browser.slowly_click(owner_filter)
    browser.assert_body_contains_text("1 parcel")

    # She sees that she has an option to return her stones to the vault
    return_link = browser.find_element_by_link_text("Return to Vault")
    browser.slowly_click(return_link)

    # she is taken to an "are you sure page"
    browser.assert_body_contains_text("You are about to confirm")
    # she clicks proceed
    proceed_button = browser.find_element_by_name("proceed")
    browser.slowly_click(proceed_button)

    # now the parcel no longer belongs to her
    browser.go_to_parcel_page()
    browser.assert_body_contains_text(f"vault, unconfirmed")
    owner_filter = browser.find_element_by_link_text("With me")
    browser.slowly_click(owner_filter)
    browser.assert_body_contains_text("0 parcels")


def test_grader_can_return_stones_that_belong_to_her_to_vault(browser, stones, grader):
    for stone in stones:
        StoneTransfer.confirm_received(stone)

    vault = User.objects.get(username="vault")
    for stone in stones:
        # Tanly the grader has some stones given to her by the vault
        StoneTransfer.initiate_transfer(item=stone, from_user=vault, to_user=grader, created_by=vault)
        # these stones have already been confirmed as received by Tanly
        StoneTransfer.confirm_received(stone)

    # She decides she wants to transfer the stones back to the vault

    # she logs in
    browser.login(grader.username, grader.raw_password)
    browser.go_to_stone_page()
    # she sees she has 3 stones with her
    owner_filter = browser.find_element_by_link_text("With me")
    browser.slowly_click(owner_filter)
    browser.assert_body_contains_text("3 stones")

    # she ticks the checkbox for the first stone
    browser.find_element_by_css_selector(f'input[value="{stones[0].id}"]').click()
    # she ticks the checkbox for the second stone
    browser.find_element_by_css_selector(f'input[value="{stones[1].id}"]').click()

    # she selects "send to vault" from the action dropdown menu
    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Transfer to Vault")

    browser.click_go()

    # and only one stone is still in the vault
    browser.assert_body_contains_text("1 stone")

    # now two stones show up as in transit to the vault
    browser.go_to_stone_page()
    owner_filter = browser.find_element_by_link_text("With the vault")
    browser.slowly_click(owner_filter)

    browser.assert_body_contains_text("2 stones")


def test_grader_cannot_return_stones_that_do_not_belong_to_her(browser, stones, grader):
    # Tanly is a grader, she wants to transfer back the stone to the vault
    browser.login(grader.username, grader.raw_password)

    browser.go_to_stone_page()
    # she has no stones with her, but there are 3 stones with the vault
    owner_filter = browser.find_element_by_link_text("With the vault")
    browser.slowly_click(owner_filter)
    browser.assert_body_contains_text("3 stones")

    # she ticks the checkbox for the first stone
    browser.find_element_by_css_selector(f'input[value="{stones[0].id}"]').click()
    # she ticks the checkbox for the second stone
    browser.find_element_by_css_selector(f'input[value="{stones[1].id}"]').click()

    # he selects "send to vault" from the action dropdown menu
    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Transfer to Vault")

    browser.click_go()

    # She realized that she cannot return stones that does not owned by her.
    browser.assert_body_contains_text("You are not allowed to do this.")


def test_grader_can_confirm_received_stones(browser, stones, grader):
    for stone in stones:
            StoneTransfer.confirm_received(stone)

    vault = User.objects.get(username="vault")
    for stone in stones:
        # The vault transfer some stones to Tanly the Grader
        StoneTransfer.initiate_transfer(item=stone, from_user=vault, to_user=grader, created_by=vault)

    browser.login(grader.username, grader.raw_password)
    browser.go_to_stone_page()

    # She is checking the stones that is currently with her
    owner_filter = browser.find_element_by_link_text("With me")
    browser.slowly_click(owner_filter)

    # she sees that she has 3 unconfirmed stones with her
    browser.assert_body_contains_text(f"{grader.username}, unconfirmed")

    # she ticks the checkbox for the first stone
    browser.find_element_by_css_selector(f'input[value="{stones[0].id}"]').click()
    # she ticks the checkbox for the second stone
    browser.find_element_by_css_selector(f'input[value="{stones[1].id}"]').click()

    # she selects "Confirm Received" from the action dropdown menu
    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Confirm Received Stones")

    browser.click_go()

    # she now sees that the stones is confirmed by her
    browser.assert_body_contains_text(f"{grader.username}, confirmed")





    
