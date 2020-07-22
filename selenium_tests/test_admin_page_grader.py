from django.contrib.auth.models import User

from ownerships.models import ParcelTransfer


def test_grader_can_confirm_received_stones(browser, erp, grader, receipt):
    # Tanly is a grader
    # the vault has given her a parcel to grade
    parcel = receipt.parcel_set.first()
    vault = User.objects.get(username="vault")
    ParcelTransfer.initiate_transfer(parcel, vault, grader)

    # she logs in to the admin portal
    browser.login(grader.username, grader.raw_password)

    # she has access to view parcels
    parcel_link = browser.find_element_by_partial_link_text("Parcel")
    browser.slowly_click(parcel_link)

    # stash this for later
    parcel_page_url = browser.current_url

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
    browser.goto(parcel_page_url)
    owner_filter = browser.find_element_by_link_text("With me")
    browser.slowly_click(owner_filter)
    browser.find_element_by_partial_link_text(parcel.gradia_parcel_code)
    browser.assert_body_contains_text(f"{grader.username}, confirmed")
    browser.find_element_by_link_text("Return to Vault")
