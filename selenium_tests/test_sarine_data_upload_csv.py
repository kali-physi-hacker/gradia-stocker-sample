import os
import pytest
import time


def test_user_can_upload_sarine_stone_data(browser, data_entry_clerk, parcels):

    # kary goes to `pythonanywhere.erp...com` and is redirected to log in
    # kary enters username and password and clicks on login button to open admin dashboard.
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    # Kary clicks on the `split` link on the left sidebar to view content on the right side
    link = browser.find_element_by_link_text("Splits")
    browser.slowly_click(link)

    # Kary clicks on `upload stone data` link on the right view. A new page is opened displaying links to do the actual upload
    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    # Kary clicks on `Sarine Data` link to open the upload page.
    gia_link = browser.find_element_by_link_text("Sarine Stone")
    browser.slowly_click(gia_link)

    # Kary clicks on the `choose file` button to upload the csv file
    upload_file_link = browser.find_element_by_xpath("//input[@type='file']")
    os.chdir("../django_backend")
    upload_file_link.send_keys(os.getcwd() + "/grading/tests/fixtures/sarine-01.csv")

    # Kary clicks on the `Upload Csv` button to upload the csv file
    # Kary is redirected to the split page.
    sarine_upload_link = browser.find_element_by_class_name("default")
    browser.slowly_click(sarine_upload_link)


def test_sarine_data_csv_upload_fails_if_grader_parcel_code_is_incorrect(browser, data_entry_clerk):

    # kary goes to `pythonanywhere.erp...com` and is redirected to log in
    # kary enters username and password and clicks on login button to open admin dashboard.
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    # Kary clicks on the `split` link on the left sidebar to view content on the right side
    link = browser.find_element_by_link_text("Splits")
    browser.slowly_click(link)

    # Kary clicks on `upload stone data` link on the right view. A new page is opened displaying links to do the actual upload
    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    # Kary clicks on `Sarine Data` link to open the upload page.
    gia_link = browser.find_element_by_link_text("Sarine Stone")
    browser.slowly_click(gia_link)

    # Kary clicks on the `choose file` button to upload the csv file
    # Kary clicks on the `Upload Csv` button to upload the csv file
    upload_file_link = browser.find_element_by_xpath("//input[@type='file']")
    os.chdir("../django_backend")
    upload_file_link.send_keys(os.getcwd() + "/grading/tests/fixtures/sarine-01-h.csv")

    sarine_upload_link = browser.find_element_by_class_name("default")
    browser.slowly_click(sarine_upload_link)

    # Kary is redirected to error page display error message indicating **No parcel with that gradia parcel code**.
    texts = (
        "Stone csv data upload failed. Check the table below to find out the problems with your csv file.",
        "No parcel with such a parcel code. Please be sure the csv file name matches the parcel code",
    )

    for text in texts:
        browser.assert_body_contains_text(text)


def test_sarine_data_csv_upload_fails_if_invalid_data_type(browser, data_entry_clerk, parcels):

    # kary goes to `pythonanywhere.erp...com` and is redirected to log in
    # kary enters username and password and clicks on login button to open admin dashboard.
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    # Kary clicks on the `split` link on the left sidebar to view content on the right side
    link = browser.find_element_by_link_text("Splits")
    browser.slowly_click(link)

    # Kary clicks on `upload stone data` link on the right view. A new page is opened displaying links to do the actual upload
    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    # Kary clicks on `Sarine Data` link to open the upload page.
    gia_link = browser.find_element_by_link_text("Sarine Stone")
    browser.slowly_click(gia_link)

    # Kary clicks on the `choose file` button to upload the csv file
    upload_file_link = browser.find_element_by_xpath("//input[@type='file']")
    os.chdir("../django_backend")
    upload_file_link.send_keys(os.getcwd() + "/grading/tests/fixtures/sarine-01-type.csv")

    # Kary clicks on the `Upload Csv` button to upload the csv file
    # Kary is redirected to the split page.
    sarine_upload_link = browser.find_element_by_class_name("default")
    browser.slowly_click(sarine_upload_link)

    # Kary is redirected to error page showing a table of the errors.
    texts = (
        "Stone csv data upload failed. Check the table below to find out the problems with your csv file.",
        "Enter a number.",
    )

    for text in texts:
        browser.assert_body_contains_text(text)


def test_field_names_are_not_correct(browser, data_entry_clerk, parcels):

    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    link = browser.find_element_by_link_text("Splits")
    browser.slowly_click(link)

    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    gia_link = browser.find_element_by_link_text("Sarine Stone")
    browser.slowly_click(gia_link)

    upload_file_link = browser.find_element_by_xpath("//input[@type='file']")
    os.chdir("../django_backend")
    upload_file_link.send_keys(os.getcwd() + "/grading/tests/fixtures/sarine-01.csv")

    sarine_upload_link = browser.find_element_by_class_name("default")
    browser.slowly_click(sarine_upload_link)

    # Check if field names are correct
    filed_names = (
        "DIAMETER MIN",
        "DIAMETER MAX",
        "HEIGHT",
        "TABLE SIZE",
        "CROWN ANGLE",
        "PAVILION ANGLE",
        "STAR LENGTH",
        "LOWER HALF",
        "GIRDLE THICKNESS NUMBER",
        "GIRDLE MIN NUMBER",
        "GIRDLE MAX NUMBER",
        "CULET SIZE",
        "CROWN HEIGHT",
        "PAVILION_DEPTH",
        "TOTAL_DEPTH",
        "TABLE_SIZE_ROUNDED",
        "CROWN_ANGLE_ROUNDED",
        "PAVILION_ANGLE_ROUNDED",
        "STAR_LENGTH_ROUNDED",
        "LOWER_HALF_ROUNDED",
        "GIRDLE_THICKNESS_ROUNDED",
        "GIRDLE_MIN_GRADE",
        "GIRDLE_MAX_GRADE",
        "CULET_SIZE_DESCRIPTION",
        "CROWN_HEIGHT_ROUNDED",
        "PAVILION_DEPTH_ROUNDED",
        "TOTAL_DEPTH_ROUNDED",
        "SARINE_CUT_PRE_POLISH_SYMMETRY",
        "SARINE_SYMMETRY",
        "ROUNDNESS",
        "ROUNDNESS_GRADE",
        "TABLE_SIZE_DEV",
        "TABLE_SIZE_DEV_GRADE",
        "CROWN_ANGLE_DEV",
        "CROWN_ANGLE_DEV_GRADE",
        "PAVILION_ANGLE_DEV",
        "PAVILION_ANGLE_DEV_GRADE",
        "STAR_LENGTH_DEV",
        "STAR_LENGTH_DEV_GRADE",
        "LOWER_HALF_DEV",
        "LOWER_HALF_DEV_GRADE",
        "GIRDLE_THICK_DEV",
        "GIRDLE_THICK_DEV_GRADE",
        "CROWN_HEIGHT_DEV",
        "CROWN_HEIGHT_DEV_GRADE",
        "PAVILION_DEPTH_DEV",
        "PAVILION_DEPTH_DEV_GRADE",
        "MISALIGNMENT",
        "MISALIGNMENT_GRADE",
        "TABLE_EDGE_VAR",
        "TABLE_EDGE_VAR_GRADE",
        "TABLE_OFF_CENTER",
        "TABLE_OFF_CENTER_GRADE",
        "CULET_OFF_CENTER",
        "CULET_OFF_CENTER_GRADE",
        "TABLE_OFF_CULET",
        "TABLE_OFF_CULET_GRADE",
        "STAR_ANGLE",
        "STAR_ANGLE_GRADE",
        "UPPER_HALF_ANGLE",
        "UPPER_HALF_ANGLE_GRADE",
        "LOWER HALF ANGLE",
        "LOWER HALF ANGLE GRADE",
    )
    for text in filed_names:
        fmt_text = " ".join(text.split("_"))
        body_text = browser.get_body_text()
        if fmt_text not in body_text:
            raise AssertionError(f"unable to find the text, {text} in browser body: \n\n{browser.get_body_text()}")


def test_uploading_the_same_stone_twice_should_error(browser, data_entry_clerk, parcels):
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    link = browser.find_element_by_link_text("Splits")
    browser.slowly_click(link)

    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    gia_link = browser.find_element_by_link_text("Sarine Stone")
    browser.slowly_click(gia_link)

    upload_file_link = browser.find_element_by_xpath("//input[@type='file']")
    os.chdir("../django_backend")
    upload_file_link.send_keys(os.getcwd() + "/grading/tests/fixtures/sarine-01.csv")

    sarine_upload_link = browser.find_element_by_class_name("default")
    browser.slowly_click(sarine_upload_link)

    home_link = browser.find_element_by_link_text("Home")
    browser.slowly_click(home_link)

    link = browser.find_element_by_link_text("Splits")
    browser.slowly_click(link)

    upload_link = browser.find_element_by_link_text("UPLOAD STONE DATA")
    browser.slowly_click(upload_link)

    gia_link = browser.find_element_by_link_text("Sarine Stone")
    browser.slowly_click(gia_link)
    # import pdb; pdb.set_trace()
    upload_file_link = browser.find_element_by_xpath("//input[@type='file']")
    os.chdir("../django_backend")
    upload_file_link.send_keys(os.getcwd() + "/grading/tests/fixtures/sarine-01.csv")

    sarine_upload_link = browser.find_element_by_class_name("default")
    browser.slowly_click(sarine_upload_link)

    browser.assert_body_contains_text("already exist")