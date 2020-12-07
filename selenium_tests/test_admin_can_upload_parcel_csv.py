import os
from django.conf import settings


def test_upload_of_csv_parcel_file(browser, admin_user, grading_parcel):
    """
    Test that admin can upload a csv file and save
    :param browser:
    :return:
    """
    browser.login(admin_user.username, admin_user.raw_password)

    # Find Split link and click
    split_link = browser.find_element_by_link_text("Splits")
    browser.slowly_click(split_link)

    # Find Upload File Button and Click
    upload_file_link = browser.find_element_by_link_text("UPLOAD FILE")
    browser.slowly_click(upload_file_link)

    # Find Upload Input and add csv file path
    csv_upload_input = browser.find_element_by_name("file")
    csv_upload_path = os.path.join(settings.BASE_DIR, "grading/tests/fixtures/123456789.csv")
    csv_upload_input.send_keys(csv_upload_path)

    # Find the upload button and click
    upload_link = browser.find_element_by_name("_upload")
    browser.slowly_click(upload_link)

    # Check that file is uploaded successfully and redirects to the split page
    # split page will contain grader (graderuser according to fixtures),
    # and some other texts

    browser.assert_body_contains_text("View split")
    browser.assert_body_contains_text("graderuser")
    browser.assert_body_contains_text("Original parcel")
    browser.assert_body_contains_text("Split by")
