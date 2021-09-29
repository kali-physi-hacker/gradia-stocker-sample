import os
import re


def test_user_can_upload_gia_if_valid_csv_file(browser, data_entry_clerk, tanly, gary, kary, initial_stones):
    browser.login(username=data_entry_clerk.username, password=data_entry_clerk.raw_password)

    browser.find_element_by_link_text("Splits").click()
    browser.find_element_by_link_text("UPLOAD STONE DATA").click()

    browser.find_element_by_link_text("Gia Adjust Grading Data").click()

    os.chdir("../django_backend")
    gia_csv_file_path = os.path.join(os.getcwd(), "grading/tests/fixtures/gia_adjusting.csv")
    upload_file_input = browser.find_element_by_name("file")
    upload_file_input.send_keys(gia_csv_file_path)

    browser.find_element_by_name("_upload").click()

    assert re.match(r"^http://localhost:\d+/admin/grading/split/\d+/change/", browser.current_url) is not None
