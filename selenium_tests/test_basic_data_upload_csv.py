import os
import re


def test_user_can_upload_basic_stone_data(browser, data_entry_clerk, tanly, gary, kary, initial_stones, inclusions):

    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    link = browser.find_element_by_link_text("Stones")
    browser.slowly_click(link)

    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    gia_link = browser.find_element_by_link_text("Basic Stone Data")
    browser.slowly_click(gia_link)

    os.chdir("../django_backend")
    basic_csv_file_path = os.path.join(os.getcwd(), "grading/tests/fixtures/basic-01.csv")
    upload_file_input = browser.find_element_by_name("file")
    upload_file_input.send_keys(basic_csv_file_path)

    browser.find_element_by_name("_upload").click()

    assert re.match(r"^http://localhost:\d+/admin/grading/split/\d+/change/", browser.current_url) is not None


def test_upload_fails_if_invalid_basic_inclusions_field(
    browser, data_entry_clerk, tanly, gary, kary, initial_stones
):

    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    link = browser.find_element_by_link_text("Stones")
    browser.slowly_click(link)

    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    gia_link = browser.find_element_by_link_text("Basic Stone Data")
    browser.slowly_click(gia_link)

    os.chdir("../django_backend")
    basic_csv_file_path = os.path.join(os.getcwd(), "grading/tests/fixtures/basic-01.csv")
    upload_file_input = browser.find_element_by_name("file")
    upload_file_input.send_keys(basic_csv_file_path)

    browser.find_element_by_name("_upload").click()

    browser.assert_body_contains_text("Enter a list of values.")
    browser.assert_body_contains_text(
        "Stone csv data upload failed. Check the table below to find out the problems with your csv file."
    )


def test_basic_data_upload_fails_if_invalid_data_type(
    browser, data_entry_clerk, tanly, gary, kary, initial_stones, inclusions
):

    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    link = browser.find_element_by_link_text("Stones")
    browser.slowly_click(link)

    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    gia_link = browser.find_element_by_link_text("Basic Stone Data")
    browser.slowly_click(gia_link)

    os.chdir("../django_backend")
    basic_csv_file_path = os.path.join(os.getcwd(), "grading/tests/fixtures/basic-01-type.csv")
    upload_file_input = browser.find_element_by_name("file")
    upload_file_input.send_keys(basic_csv_file_path)

    browser.find_element_by_name("_upload").click()

    browser.assert_body_contains_text(
        "Stone csv data upload failed. Check the table below to find out the problems with your csv file."
    )
    browser.assert_body_contains_text("Enter a number.")
    browser.assert_body_contains_text("Select a valid choice. 9.0 is not one of the available choices.")
