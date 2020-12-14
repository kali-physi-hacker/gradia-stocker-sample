import os
import csv
from time import sleep


from django.contrib.auth.models import User
from selenium.webdriver.support.ui import Select


from ownerships.models import ParcelTransfer, StoneTransfer
from grading.models import Stone
from grading.helpers import get_stone_fields

SELENIUM_PATH = os.path.abspath(__file__)

download_dir = os.path.join(os.path.dirname(SELENIUM_PATH), "downloads")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)


def test_grader_can_download_id_stones(browser, stones, grader, download_file_dir):

    browser.login(grader.username, grader.raw_password)
    browser.go_to_stone_page()

    # she ticks the checkbox for the first stone
    browser.find_element_by_css_selector(f'input[value="{stones[0].id}"]').click()
    # she ticks the checkbox for the second stone
    browser.find_element_by_css_selector(f'input[value="{stones[1].id}"]').click()

    browser.find_element_by_css_selector(f'input[value="{stones[2].id}"]').click()

    # browser.find_element_by_css_selector(
    #     f'input[value="{stones[3].id}"]').click()

    # browser.find_element_by_css_selector(
    #     f'input[value="{stones[4].id}"]').click()

    # she selects "Download Diamond(s) External Nanotech IDs" from the action dropdown menu
    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Download Diamond(s) External Nanotech IDs")

    browser.click_go(elem_should_disappear=False)
    sleep(5)
    file_path = os.path.join((download_file_dir), os.listdir(download_file_dir)[0])
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        assert "internal_id" in reader.fieldnames
        csv_list = list(reader)
    assert str(stones[0].internal_id) in csv_list[0]["internal_id"]
    assert str(stones[1].internal_id) in csv_list[1]["internal_id"]


def test_grader_can_download_master_report(browser, stones, grader, download_file_dir):

    browser.login(grader.username, grader.raw_password)
    browser.go_to_stone_page()

    # she ticks the checkbox for the first stone
    browser.find_element_by_css_selector(f'input[value="{stones[0].id}"]').click()
    # she ticks the checkbox for the second stone
    browser.find_element_by_css_selector(f'input[value="{stones[1].id}"]').click()

    browser.find_element_by_css_selector(f'input[value="{stones[2].id}"]').click()

    # browser.find_element_by_css_selector(
    #     f'input[value="{stones[3].id}"]').click()

    # browser.find_element_by_css_selector(
    #     f'input[value="{stones[4].id}"]').click()

    # she selects "Download Master Report" from the action dropdown menu
    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Download Master Report")

    browser.click_go(elem_should_disappear=False)
    sleep(5)
    field_names = get_stone_fields(Stone)
    file_path = os.path.join((download_file_dir), os.listdir(download_file_dir)[0])
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for field in field_names:
            assert field in reader.fieldnames
        csv_list = list(reader)
    assert str(stones[0].data_entry_user) in csv_list[0]["data_entry_user"]
    assert str(stones[2].date_created) in csv_list[2]["date_created"]


def test_grader_can_download_goldway_transfer(browser, stones, grader, download_file_dir):

    browser.login(grader.username, grader.raw_password)
    browser.go_to_stone_page()

    # she ticks the checkbox for the first stone
    browser.find_element_by_css_selector(f'input[value="{stones[0].id}"]').click()
    # she ticks the checkbox for the second stone
    browser.find_element_by_css_selector(f'input[value="{stones[1].id}"]').click()

    browser.find_element_by_css_selector(f'input[value="{stones[2].id}"]').click()

    # browser.find_element_by_css_selector(
    #     f'input[value="{stones[3].id}"]').click()

    # browser.find_element_by_css_selector(
    #     f'input[value="{stones[4].id}"]').click()

    # she selects "Download Master Report" from the action dropdown menu
    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Download Goldway CV Trasfer")

    browser.click_go(elem_should_disappear=False)
    sleep(5)
    field_names = ["date_to_GW", "internal_id", "basic_carat"]
    file_path = os.path.join((download_file_dir), os.listdir(download_file_dir)[0])
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        for field in field_names:
            assert field in reader.fieldnames
        csv_list = list(reader)
    assert str(stones[2].internal_id) in csv_list[2]["internal_id"]
    assert str(stones[0].basic_carat) in csv_list[0]["basic_carat"]
