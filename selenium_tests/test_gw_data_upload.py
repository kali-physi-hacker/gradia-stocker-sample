import os
import re


def test_user_can_upload_gw_if_valid_csv_file(
    browser, data_entry_clerk, tanly, gary, kary, initial_stones, goldway_transfer
):
    browser.login(username=data_entry_clerk.username, password=data_entry_clerk.raw_password)

    browser.find_element_by_link_text("Stones").click()
    browser.find_element_by_link_text("UPLOAD STONE DATA").click()

    browser.find_element_by_link_text("Goldway Stone Data").click()

    os.chdir("../django_backend")
    gia_csv_file_path = os.path.join(os.getcwd(), "grading/tests/fixtures/gold_way-01.csv")
    upload_file_input = browser.find_element_by_name("file")
    upload_file_input.send_keys(gia_csv_file_path)

    browser.find_element_by_name("_upload").click()

    assert re.match(r"^http://localhost:\d+/admin/grading/split/\d+/change/", browser.current_url) is not None


def test_user_upload_gw_fails_if_invalid_csv_file(browser, data_entry_clerk, tanly, gary, kary, initial_stones):
    browser.login(username=data_entry_clerk.username, password=data_entry_clerk.raw_password)

    browser.find_element_by_link_text("Stones").click()
    browser.find_element_by_link_text("UPLOAD STONE DATA").click()

    browser.find_element_by_link_text("Goldway Stone Data").click()

    os.chdir("../django_backend")
    gia_csv_file_path = os.path.join(os.getcwd(), "grading/tests/fixtures/gold_way_invalid.csv")
    upload_file_input = browser.find_element_by_name("file")
    upload_file_input.send_keys(gia_csv_file_path)

    browser.find_element_by_name("_upload").click()

    # import pdb; pdb.set_trace()
    assert re.match(r"^http://localhost:\d+/grading/gw_data_upload_url/", browser.current_url) is not None
    browser.assert_body_contains_text("Data Upload Failed")
    browser.assert_body_contains_text("Enter a valid date/time.")  # Some error message
