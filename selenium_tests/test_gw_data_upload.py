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

    assert re.match(r"^http://localhost:\d+/grading/gw_data_upload_url/", browser.current_url) is not None
    browser.assert_body_contains_text("Data Upload Failed")
    browser.assert_body_contains_text("Enter a valid date/time.")  # Some error message

def test_upload_fails_if_user_uploads_same_stone_twice(browser, data_entry_clerk, tanly, gary, kary, initial_stones, goldway_transfer):
    """
    Tests that gia upload fails if user uploads gia for the same stone twice
    :returns:
    """

    # 1st Upload
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


    # 2nd Upload
    browser.find_element_by_link_text("Splits").click()

    browser.find_element_by_link_text("Stones").click()
    browser.find_element_by_link_text("UPLOAD STONE DATA").click()

    browser.find_element_by_link_text("Goldway Stone Data").click()

    os.chdir("../django_backend")
    gia_csv_file_path = os.path.join(os.getcwd(), "grading/tests/fixtures/gold_way-01.csv")
    upload_file_input = browser.find_element_by_name("file")
    upload_file_input.send_keys(gia_csv_file_path)

    browser.find_element_by_name("_upload").click()

    body_text = browser.get_body_text()
    for internal_id in (1, 5, 6):
        error_string = f"Stone with {internal_id} has already been uploaded"
        found_error = body_text.find(error_string)
        assert found_error != -1
