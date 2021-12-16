import os

"""
1. Grader does a sarine csv upload
2. Grader does a basic csv upload
3. Vault Manager then does a transfer to Goldway which is later verified
4. Grader gets results from Goldway and uploads the results as GW csv upload results
5. Graders adjust the Goldway grading results and upload the results
6. Vault Manager then does a transfer to GIA which is later verified
7. Grader gets results from GIA and uploads the results as GIA csv upload results
8. Graders adjust the GIA grading results and upload the results
"""


def upload_file_data(browser, file_name):
    os.chdir("../django_backend")
    file_path = f"{os.getcwd()}/grading/tests/fixtures/{file_name}"
    browser.find_element_by_name("file").send_keys(file_path)
    browser.find_element_by_name("_upload").click()


def upload_file_transfer(browser, file_name):
    os.chdir("../django_backend")
    file_path = f"{os.getcwd()}/ownerships/tests/resources/{file_name}"
    browser.find_element_by_name("file").send_keys(file_path)
    browser.find_element_by_name("_upload").click()


def test_walk_through(browser, django_user_model, erp, admin_user, tanly, kary, gary, inclusions):
    """
    Whole erp software V1 usage walk through test.
    i.e For a typical list of stones, the stages of upload and transfers
    they go through before they are finally exported to lab. And basically
    how customers and their receipts are been tracked.
    :param browser:
    :param erp:
    :param vault_manager:
    :param tanly:
    :return:
    """
    browser.login(username=admin_user.username, password="password")

    # Admin creates a customer
    browser.find_element_by_link_text("Users").click()
    browser.find_element_by_link_text("ADD USER").click()

    customer_name = "Customer"
    browser.find_element_by_name("username").send_keys(customer_name)
    browser.find_element_by_name("password1").send_keys("customer@pass123")
    browser.find_element_by_name("password2").send_keys("customer@pass123")
    browser.find_element_by_css_selector('input[value="Save"]').click()

    # Receptionist received stones from existing customer and Admin a receipt with multiple parcels
    browser.find_element_by_link_text("Customer receipts").click()
    browser.find_element_by_link_text("ADD CUSTOMER RECEIPT").click()
    browser.find_element_by_name("code").send_keys("VK01")

    # Create a new entity
    browser.find_element_by_css_selector("a[title='Add another entity']").click()
    browser.switch_to_window(browser.window_handles[1])
    browser.find_element_by_name("name").send_keys("John Doe")
    browser.find_element_by_name("address").send_keys("21st Street, Pytest Django")
    browser.find_element_by_name("remarks").send_keys("Just doing a couple of testing")
    browser.find_element_by_name("phone").send_keys("0123456789")
    browser.find_element_by_name("email").send_keys("johndoe@example.com")
    browser.find_element_by_name("authorizedpersonnel_set-0-position").send_keys("Grader")
    browser.find_element_by_name("authorizedpersonnel_set-0-name").send_keys("Kary")
    browser.find_element_by_name("authorizedpersonnel_set-0-email").send_keys("kary@gradia.net")
    browser.find_element_by_name("authorizedpersonnel_set-0-mobile").send_keys("1928493849")
    browser.find_element_by_name("authorizedpersonnel_set-0-hkid").send_keys("HK01")
    browser.find_element_by_name("authorizedpersonnel_set-0-remarks").send_keys("Testing test")
    browser.find_element_by_name("_save").click()

    browser.switch_to_window(browser.window_handles[0])

    # Create a new parcel
    browser.find_element_by_link_text("Add another Parcel").click()
    browser.find_element_by_name("parcel_set-0-gradia_parcel_code").send_keys("sarine-01")
    browser.find_element_by_name("parcel_set-0-customer_parcel_code").send_keys("VK01")
    browser.find_element_by_name("parcel_set-0-total_carats").send_keys(25)
    browser.find_element_by_name("parcel_set-0-total_pieces").send_keys(24)
    browser.find_element_by_name("parcel_set-0-reference_price_per_carat").send_keys(10)
    browser.find_element_by_name("_save").click()

    # Stones are split into parcels
    browser.find_element_by_link_text("Splits").click()
    browser.find_element_by_link_text("UPLOAD STONE DATA").click()
    browser.find_element_by_link_text("Sarine Stone").click()
    upload_file_data(browser=browser, file_name="sarine-01.csv")

    # Upload basic grading results
    browser.find_element_by_link_text("Splits").click()
    browser.find_element_by_link_text("UPLOAD STONE DATA").click()
    browser.find_element_by_link_text("Basic Stone Data").click()
    upload_file_data(browser=browser, file_name="basic-01.csv")

    # Transfer stones to goldway
    browser.find_element_by_link_text("Stone transfers").click()
    browser.find_element_by_link_text("TRANSFER STONES").click()
    browser.find_element_by_link_text("Goldway Transfer").click()
    upload_file_transfer(browser=browser, file_name="G048RV.csv")

    # Upload Goldway results
    browser.find_element_by_link_text("Home").click()
    browser.find_element_by_link_text("Splits").click()
    browser.find_element_by_link_text("UPLOAD STONE DATA").click()
    browser.find_element_by_link_text("Goldway Stone Data").click()
    upload_file_data(browser=browser, file_name="gold_way-01.csv")

    # Transfer stones to gia
    browser.find_element_by_link_text("Home").click()
    browser.find_element_by_link_text("Splits").click()
    browser.find_element_by_link_text("Stone transfers").click()
    browser.find_element_by_link_text("TRANSFER STONES").click()
    browser.find_element_by_link_text("GIA Transfer").click()
    upload_file_transfer(browser=browser, file_name="gia.csv")

    # Upload GIA results
    browser.find_element_by_link_text("Home").click()
    browser.find_element_by_link_text("Splits").click()
    browser.find_element_by_link_text("UPLOAD STONE DATA").click()
    browser.find_element_by_link_text("Gia Grading Data").click()
    upload_file_data(browser=browser, file_name="gia.csv")

    # Transfer to external customer
    browser.find_element_by_link_text("Home").click()
    browser.find_element_by_link_text("Stone transfers").click()
    browser.find_element_by_link_text("TRANSFER STONES").click()
    browser.find_element_by_link_text("External Transfer").click()

    browser.find_element_by_name("customer").click()
    customer_user = django_user_model.objects.get(username=customer_name)
    browser.find_element_by_css_selector(f"option[value='{customer_user.pk}']").click()
    upload_file_transfer(browser=browser, file_name="G048RV.csv")
