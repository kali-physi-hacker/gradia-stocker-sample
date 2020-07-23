from django.contrib.auth.models import User

from ownerships.models import ParcelTransfer
from selenium.webdriver.support.ui import Select


def test_create_new_customer(browser, erp, receptionist):
    #Roxy is a receptionist
    #A customer approach Roxy to make a transaction.

    #Roxy log into the receptionist portal
    browser.login(receptionist.username, receptionist.raw_password)

    #Roxy check whether the customer already exists in the system or not.
    cust_link = browser.find_element_by_partial_link_text("Entitys")
    browser.slowly_click(cust_link)

    #She sees that the customer is new and does not exist in the system yet. She proceed to create a new customer.
    add_link = browser.find_element_by_xpath("//div[@id='content-main']//a[@class='addlink']")
    browser.slowly_click(add_link)
    
    #She fills in the deatil of the new customer
    browser.find_element_by_name("name").send_keys("new_customer")
    browser.find_element_by_name("address").send_keys("new_customer")
    browser.find_element_by_name("phone").send_keys("1")
    browser.find_element_by_name("email").send_keys("newcustomer@newcustomer.com")
    
    #She save the customer detail
    browser.find_element_by_name('_save').click()

    #She double checked it if the form she saved already been saved in the database
    browser.assert_body_contains_text("new_customer")

def test_customer_exists(browser, erp, receptionist, create_customer):
    #Tanly is a receptionist
    #She logs in to the admin portal
    create_customer('Van Klaren','Address 1','1','vanklaren@vanklaren.com')
    browser.login(receptionist.username, receptionist.raw_password)

    #She checked whether there exists a Customers yet.
    cust_link = browser.find_element_by_partial_link_text("Entitys")
    browser.slowly_click(cust_link)

    #She sees that there exists a customer as expected
    browser.assert_body_contains_text("Van Klaren")

def test_create_a_receipt(erp, grader, create_customer, browser):
    #An old customer comes in with a stone. Nicky is responsible to create the receipt 
    create_customer('Van Klaren','Address 1','1','vanklaren@vanklaren.com')

    #He logged in into the system to create the receipt
    browser.login(grader.username, grader.raw_password)

    #He clicked into the Customer Receipts
    parcel_link = browser.find_element_by_partial_link_text("Customer")
    browser.slowly_click(parcel_link)

    #He wants to create a new receipt by clicking 'Add Customer Receipt'
    add_link = browser.find_element_by_xpath("//div[@id='content-main']//a[@class='addlink']")
    browser.slowly_click(add_link)

    #He select the customer name in the entity column
    select = Select(browser.find_element_by_id("id_entity"))

    select.select_by_visible_text("Van Klaren")
    
    browser.find_element_by_name("code").send_keys("vk")

    #He clicked the "Add another Parcel" to add a new parcel.
    add_link = browser.find_element_by_link_text("Add another Parcel- Check Inventory").click()

    #He fills in the parcel details.
    browser.find_element_by_name("parcel_set-0-gradia_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("001")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys("1")
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys("1")
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys("500")

    #He saved it
    browser.find_element_by_name('_save').click()

    #He double checked wheter the receipt is well created
    browser.assert_body_contains_text("receipt vk")

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
