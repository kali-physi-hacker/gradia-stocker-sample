import os
import time
import csv
from selenium.webdriver.support.ui import Select

def test_user_can_download_to_gw_csv(browser, data_entry_clerk, initial_stones, download_file_dir):
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    stone_tab = browser.find_element_by_link_text("Stones")
    browser.slowly_click(stone_tab)

    show_stones = browser.find_element_by_link_text("Including splits and exited")
    browser.slowly_click(show_stones)

    checkbox_1 = browser.find_element_by_class_name("action-checkbox")
    browser.slowly_click(checkbox_1, elem_should_disappear=False)

    select_from_dropdown = Select(browser.find_element_by_name("action"))
    select_from_dropdown.select_by_visible_text('Download Goldway CSV Transfer')

    browser.click_go(elem_should_disappear=False)

    # wait for 2 seconds for the file to be downloaded and store in path
    time.sleep(2)

    downloaded_csv_file = os.listdir(download_file_dir)[0]
    csv_file_path = os.path.join(download_file_dir, downloaded_csv_file)

    with open(csv_file_path, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        # assert content here