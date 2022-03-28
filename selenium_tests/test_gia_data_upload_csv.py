import os


def test_user_can_upload_gia_data(browser, data_entry_clerk, initial_stones, gia_transfer):

    # kary goes to `pythonanywhere.erp...com` and is redirected to log in
    # kary enters username and password and clicks on login button to open admin dashboard.
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    # Kary clicks on the `split` link on the left sidebar to view content on the right side
    link = browser.find_element_by_link_text("Stones")
    browser.slowly_click(link)

    # Kary clicks on `upload stone data` link on the right view. A new page is opened displaying links to do the actual upload
    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    # Kary clicks on `Sarine Data` link to open the upload page.
    gia_link = browser.find_element_by_link_text("Gia Grading Data")
    browser.slowly_click(gia_link)

    # Kary clicks on the `choose file` button to upload the csv file
    upload_file_link = browser.find_element_by_xpath("//input[@type='file']")
    os.chdir("../django_backend")
    upload_file_link.send_keys(os.getcwd() + "/grading/tests/fixtures/gia.csv")

    # Kary clicks on the `Upload Csv` button to upload the csv file
    # Kary is redirected to the split page.
    sarine_upload_link = browser.find_element_by_class_name("default")
    browser.slowly_click(sarine_upload_link)
    browser.assert_body_contains_text("View split")


def test_gia_data_upload_fails_if_date_from_gia_is_not_provided(browser, data_entry_clerk, initial_stones):

    # kary goes to `pythonanywhere.erp...com` and is redirected to log in
    # kary enters username and password and clicks on login button to open admin dashboard.
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    # Kary clicks on the `split` link on the left sidebar to view content on the right side
    link = browser.find_element_by_link_text("Stones")
    browser.slowly_click(link)

    # Kary clicks on `upload stone data` link on the right view. A new page is opened displaying links to do the actual upload
    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    # Kary clicks on `Sarine Data` link to open the upload page.
    gia_link = browser.find_element_by_link_text("Gia Grading Data")
    browser.slowly_click(gia_link)

    # Kary clicks on the `choose file` button to upload the csv file
    upload_file_link = browser.find_element_by_xpath("//input[@type='file']")
    os.chdir("../django_backend")
    upload_file_link.send_keys(os.getcwd() + "/grading/tests/fixtures/gia-invalid.csv")

    # Kary clicks on the `Upload Csv` button to upload the csv file
    # Kary is redirected to the split page.
    sarine_upload_link = browser.find_element_by_class_name("default")
    browser.slowly_click(sarine_upload_link)

    # Kary is redirected to error page
    browser.assert_body_contains_text("Data Upload Failed")
    browser.assert_body_contains_text(
        "Select a valid choice. bar is not one of the available choices."
    )  # Some error message


def test_user_cannot_upload_grading_results_twice_for_the_same_stone(browser, data_entry_clerk, gia_transfer):

    # 1st Upload
    # kary goes to `pythonanywhere.erp...com` and is redirected to log in
    # kary enters username and password and clicks on login button to open admin dashboard.
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    # Kary clicks on the `split` link on the left sidebar to view content on the right side
    link = browser.find_element_by_link_text("Stones")
    browser.slowly_click(link)

    # Kary clicks on `upload stone data` link on the right view. A new page is opened displaying links to do the actual upload
    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    # Kary clicks on `Sarine Data` link to open the upload page.
    gia_link = browser.find_element_by_link_text("Gia Grading Data")
    browser.slowly_click(gia_link)

    # Kary clicks on the `choose file` button to upload the csv file
    upload_file_link = browser.find_element_by_xpath("//input[@type='file']")
    os.chdir("../django_backend")
    upload_file_link.send_keys(os.getcwd() + "/grading/tests/fixtures/gia.csv")

    # Kary clicks on the `Upload Csv` button to upload the csv file
    # Kary is redirected to the split page.
    sarine_upload_link = browser.find_element_by_class_name("default")
    browser.slowly_click(sarine_upload_link)
    browser.assert_body_contains_text("View split")

    # 2nd Upload
    browser.find_element_by_link_text("Splits").click()

    # Kary clicks on the `split` link on the left sidebar to view content on the right side
    link = browser.find_element_by_link_text("Stones")
    browser.slowly_click(link)

    # Kary clicks on `upload stone data` link on the right view. A new page is opened displaying links to do the actual upload
    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    # Kary clicks on `Sarine Data` link to open the upload page.
    gia_link = browser.find_element_by_link_text("Gia Grading Data")
    browser.slowly_click(gia_link)

    # Kary clicks on the `choose file` button to upload the csv file
    upload_file_link = browser.find_element_by_xpath("//input[@type='file']")
    os.chdir("../django_backend")
    upload_file_link.send_keys(os.getcwd() + "/grading/tests/fixtures/gia.csv")

    # Kary clicks on the `Upload Csv` button to upload the csv file
    # Kary is redirected to the split page.
    sarine_upload_link = browser.find_element_by_class_name("default")
    browser.slowly_click(sarine_upload_link)

    body_text = browser.get_body_text()
    for internal_id in (1, 5, 6):
        error_string = f"Stone with internal_id: `{internal_id}` has already been uploaded"
        found_error = body_text.find(error_string)
        assert found_error != -1
