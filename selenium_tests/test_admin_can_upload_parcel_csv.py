import os

from django.conf import settings


def test_upload_of_csv_parcel_file(browser, data_entry_clerk, stones):
    """
    Test that admin can upload a csv file and save
    :param browser:
    :return:
    """

    # TODO: Refactor Tests (CSV Upload file) to conform to parcel ==> original owner
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    # Find Split link and click
    split_link = browser.find_element_by_link_text("Splits")
    browser.slowly_click(split_link)

    # Find Upload File Button and Click
    upload_file_link = browser.find_element_by_link_text("UPLOAD FILE")
    browser.slowly_click(upload_file_link)

    # Find Upload Input and add csv file path
    csv_upload_input = browser.find_element_by_name("file")
    csv_upload_path = os.path.join(settings.BASE_DIR, "grading/tests/fixtures/parcel1.csv")
    csv_upload_input.send_keys(csv_upload_path)

    # Find the upload button and click
    upload_link = browser.find_element_by_name("_upload")
    browser.slowly_click(upload_link)

    # Check that file is uploaded successfully and redirects to the split page
    # split page will contain grader (graderuser according to fixtures),
    # and some other texts

    browser.assert_body_contains_text("123456789")  # this is an internal id from the uploaded csv
    browser.assert_body_contains_text(data_entry_clerk.username)
    browser.assert_body_contains_text("Original parcel")
