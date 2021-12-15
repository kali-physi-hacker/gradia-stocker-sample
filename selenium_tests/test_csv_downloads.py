import os
import time
import pandas as pd
from selenium.webdriver.support.ui import Select

from grading.models import Stone


def test_user_can_download_basic_grading_csv_template_success(
    browser, data_entry_clerk, initial_stones, download_file_dir
):
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    stone_tab = browser.find_element_by_link_text("Stones")
    browser.slowly_click(stone_tab)

    show_stones = browser.find_element_by_link_text("Including splits and exited")
    browser.slowly_click(show_stones)

    checkbox_1 = browser.find_element_by_class_name("action-checkbox")
    browser.slowly_click(checkbox_1, elem_should_disappear=False)

    select_from_dropdown = Select(browser.find_element_by_name("action"))
    select_from_dropdown.select_by_visible_text("Download Basic Grading CSV Template")

    browser.click_go(elem_should_disappear=False)

    # wait for 2 seconds for the file to be downloaded and store in path
    time.sleep(2)

    downloaded_csv_file = os.listdir(download_file_dir)[0]
    csv_file_path = os.path.join(download_file_dir, downloaded_csv_file)

    csv_file_content = (
        "internal_id",
        "basic_diamond_description",
        "basic_grader_1",
        "basic_grader_2",
        "basic_grader_3",
        "basic_carat",
        "basic_color_1",
        "basic_color_2",
        "basic_color_3",
        "basic_color_final",
        "basic_clarity_1",
        "basic_clarity_2",
        "basic_clarity_3",
        "basic_clarity_final",
        "basic_fluorescence_1",
        "basic_fluorescence_2",
        "basic_fluorescence_3",
        "basic_fluorescence_final",
        "basic_culet_1",
        "basic_culet_2",
        "basic_culet_3",
        "basic_culet_final",
        "basic_culet_characteristic_1",
        "basic_culet_characteristic_2",
        "basic_culet_characteristic_3",
        "basic_culet_characteristic_final",
        "basic_girdle_condition_1",
        "basic_girdle_condition_2",
        "basic_girdle_condition_3",
        "basic_girdle_condition_final",
        "basic_inclusions_1",
        "basic_inclusions_2",
        "basic_inclusions_3",
        "basic_inclusions_final",
        "basic_polish_1",
        "basic_polish_2",
        "basic_polish_3",
        "basic_polish_final",
        "girdle_min_grade",
        "basic_girdle_min_grade_final",
        "basic_remarks",
    )

    read_file = pd.read_csv(csv_file_path)
    data_frame = pd.DataFrame(read_file).to_dict().keys()
    for text in csv_file_content:
        if text not in data_frame:
            raise AssertionError(f"unable to find the text, {text} in csv file")


def test_user_can_download_adjust_goldway_csv_success(browser, data_entry_clerk, initial_stones, download_file_dir):
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    stone_tab = browser.find_element_by_link_text("Stones")
    browser.slowly_click(stone_tab)

    show_stones = browser.find_element_by_link_text("Including splits and exited")
    browser.slowly_click(show_stones)

    checkbox_1 = browser.find_element_by_class_name("action-checkbox")
    browser.slowly_click(checkbox_1, elem_should_disappear=False)

    select_from_dropdown = Select(browser.find_element_by_name("action"))
    select_from_dropdown.select_by_visible_text("Download Adjust Goldway CSV")

    browser.click_go(elem_should_disappear=False)

    # wait for 2 seconds for the file to be downloaded and store in path
    time.sleep(2)

    downloaded_csv_file = os.listdir(download_file_dir)[0]
    csv_file_path = os.path.join(download_file_dir, downloaded_csv_file)

    csv_file_content = (
        "internal_id",
        "nano_etch_inscription",
        "gw_adjust_grader_1",
        "gw_adjust_grader_2",
        "gw_adjust_grader_3",
        "basic_color_final",
        "gw_color",
        "gw_color_adjusted_1",
        "gw_color_adjusted_2",
        "gw_color_adjusted_3",
        "gw_color_adjusted_final",
        "basic_clarity_final",
        "gw_clarity",
        "gw_clarity_adjusted_1",
        "gw_clarity_adjusted_2",
        "gw_clarity_adjusted_3",
        "gw_clarity_adjusted_final",
        "basic_fluorescence_final",
        "gw_fluorescence",
        "gw_fluorescence_adjusted_1",
        "gw_fluorescence_adjusted_2",
        "gw_fluorescence_adjusted_3",
        "gw_fluorescence_adjusted_final",
        "gw_adjust_remarks",
    )

    read_file = pd.read_csv(csv_file_path)
    data_frame = pd.DataFrame(read_file).to_dict().keys()
    for text in csv_file_content:
        if text not in data_frame:
            raise AssertionError(f"unable to find the text, {text} in the csv file")


def test_user_can_download_to_gia_csv_success(browser, data_entry_clerk, initial_stones, download_file_dir):

    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    stone_tab = browser.find_element_by_link_text("Stones")
    browser.slowly_click(stone_tab)

    show_stones = browser.find_element_by_link_text("Including splits and exited")
    browser.slowly_click(show_stones)

    checkbox_1 = browser.find_element_by_class_name("action-checkbox")
    browser.slowly_click(checkbox_1, elem_should_disappear=False)
    for stone in Stone.objects.all():
        stone.external_id = f"inscription-{stone.pk}"
        stone.save()
    select_from_dropdown = Select(browser.find_element_by_name("action"))
    select_from_dropdown.select_by_visible_text("Download GIA CSV Transfer")

    browser.click_go(elem_should_disappear=False)

    # wait for 2 seconds for the file to be downloaded and store in path
    time.sleep(2)

    downloaded_csv_file = os.listdir(download_file_dir)[0]
    csv_file_path = os.path.join(download_file_dir, downloaded_csv_file)

    csv_file_content = (
        "date_from_gia",
        "nano_etch_inscription",
        "basic_carat",
        "basic_color_final",
    )
    read_file = pd.read_csv(csv_file_path)
    data_frame = pd.DataFrame(read_file).to_dict().keys()
    for text in csv_file_content:
        if text not in data_frame:
            raise AssertionError(f"unable to find the text, {text} in the csv file")


def test_user_can_download_to_gia_csv_failure(browser, data_entry_clerk, initial_stones, download_file_dir):

    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    stone_tab = browser.find_element_by_link_text("Stones")
    browser.slowly_click(stone_tab)

    show_stones = browser.find_element_by_link_text("Including splits and exited")
    browser.slowly_click(show_stones)

    checkbox_1 = browser.find_element_by_class_name("action-checkbox")
    browser.slowly_click(checkbox_1, elem_should_disappear=False)

    select_from_dropdown = Select(browser.find_element_by_name("action"))
    select_from_dropdown.select_by_visible_text("Download GIA CSV Transfer")

    browser.click_go(elem_should_disappear=False)
    browser.assert_body_contains_text("There is not enough data to download")


def test_user_can_download_basic_report_success(browser, data_entry_clerk, initial_stones, download_file_dir):
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    stone_tab = browser.find_element_by_link_text("Stones")
    browser.slowly_click(stone_tab)

    show_stones = browser.find_element_by_link_text("Including splits and exited")
    browser.slowly_click(show_stones)

    checkbox_1 = browser.find_element_by_class_name("action-checkbox")
    browser.slowly_click(checkbox_1, elem_should_disappear=False)

    select_from_dropdown = Select(browser.find_element_by_name("action"))
    select_from_dropdown.select_by_visible_text("Download Basic Report")

    browser.click_go(elem_should_disappear=False)

    # wait for 2 seconds for the file to be downloaded and store in path
    time.sleep(2)

    downloaded_csv_file = os.listdir(download_file_dir)[0]
    csv_file_path = os.path.join(download_file_dir, downloaded_csv_file)

    csv_file_content = (
        "internal_id",
        "diameter_min",
        "diameter_max",
        "height",
        "table_size",
        "crown_angle",
        "pavilion_angle",
        "star_length",
        "lower_half",
        "girdle_thickness_number",
        "girdle_min_number",
        "girdle_max_number",
        "culet_size",
        "crown_height",
        "pavilion_depth",
        "total_depth",
        "table_size_rounded",
        "crown_angle_rounded",
        "pavilion_angle_rounded",
        "star_length_rounded",
        "lower_half_rounded",
        "girdle_thickness_rounded",
        "girdle_min_grade",
        "girdle_max_grade",
        "culet_size_description",
        "crown_height_rounded",
        "pavilion_depth_rounded",
        "total_depth_rounded",
        "sarine_cut_pre_polish_symmetry",
        "sarine_symmetry",
        "roundness",
        "roundness_grade",
        "table_size_dev",
        "table_size_dev_grade",
        "crown_angle_dev",
        "crown_angle_dev_grade",
        "pavilion_angle_dev",
        "pavilion_angle_dev_grade",
        "star_length_dev",
        "star_length_dev_grade",
        "lower_half_dev",
        "lower_half_dev_grade",
        "girdle_thick_dev",
        "girdle_thick_dev_grade",
        "crown_height_dev",
        "crown_height_dev_grade",
        "pavilion_depth_dev",
        "pavilion_depth_dev_grade",
        "misalignment",
        "misalignment_grade",
        "table_edge_var",
        "table_edge_var_grade",
        "table_off_center",
        "table_off_center_grade",
        "culet_off_center",
        "culet_off_center_grade",
        "table_off_culet",
        "table_off_culet_grade",
        "star_angle",
        "star_angle_grade",
        "upper_half_angle",
        "upper_half_angle_grade",
        "lower_half_angle",
        "lower_half_angle_grade",
    )

    read_file = pd.read_csv(csv_file_path)
    data_frame = pd.DataFrame(read_file).to_dict().keys()
    for text in csv_file_content:
        if text not in data_frame:
            raise AssertionError(f"unable to find the text, {text} in the csv file")


def test_user_can_download_adjust_gia_csv_success(browser, data_entry_clerk, initial_stones, download_file_dir):
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    stone_tab = browser.find_element_by_link_text("Stones")
    browser.slowly_click(stone_tab)

    show_stones = browser.find_element_by_link_text("Including splits and exited")
    browser.slowly_click(show_stones)

    checkbox_1 = browser.find_element_by_class_name("action-checkbox")
    browser.slowly_click(checkbox_1, elem_should_disappear=False)

    select_from_dropdown = Select(browser.find_element_by_name("action"))
    select_from_dropdown.select_by_visible_text("Download Adjust GIA CSV")

    browser.click_go(elem_should_disappear=False)

    # wait for 2 seconds for the file to be downloaded and store in path
    time.sleep(2)

    downloaded_csv_file = os.listdir(download_file_dir)[0]
    csv_file_path = os.path.join(download_file_dir, downloaded_csv_file)

    csv_file_content = (
        "gia_code",
        "nano_etch_inscription",
        "gia_adjust_grader_1",
        "gia_adjust_grader_2",
        "gia_adjust_grader_3",
        "gia_color_adjusted_final",
        "gia_color",
        "gia_color_adjusted_1",
        "gia_color_adjusted_2",
        "gia_color_adjusted_3",
        "gia_color_adjusted_final",
        "basic_culet_final",
        "gia_culet_adjusted_1",
        "gia_culet_adjusted_2",
        "gia_culet_adjusted_3",
        "gia_culet_adjusted_final",
        "basic_culet_characteristic_final",
        "gia_culet_characteristic_1",
        "gia_culet_characteristic_2",
        "gia_culet_characteristic_3",
        "gia_culet_characteristic_final",
        "gia_adjust_remarks",
    )

    read_file = pd.read_csv(csv_file_path)
    data_frame = pd.DataFrame(read_file).to_dict().keys()
    for text in csv_file_content:
        if text not in data_frame:
            raise AssertionError(f"unable to find the text, {text} in the csv file")


def test_user_can_download_tripple_report_success(browser, data_entry_clerk, initial_stones, download_file_dir):
    browser.login(data_entry_clerk.username, data_entry_clerk.raw_password)

    stone_tab = browser.find_element_by_link_text("Stones")
    browser.slowly_click(stone_tab)

    show_stones = browser.find_element_by_link_text("Including splits and exited")
    browser.slowly_click(show_stones)

    checkbox_1 = browser.find_element_by_class_name("action-checkbox")
    browser.slowly_click(checkbox_1, elem_should_disappear=False)

    select_from_dropdown = Select(browser.find_element_by_name("action"))
    select_from_dropdown.select_by_visible_text("Download Triple Report")

    browser.click_go(elem_should_disappear=False)

    # wait for 2 seconds for the file to be downloaded and store in path
    time.sleep(2)

    downloaded_csv_file = os.listdir(download_file_dir)[0]
    csv_file_path = os.path.join(download_file_dir, downloaded_csv_file)

    csv_file_content = (
        "internal_id",
        "goldway_code",
        "gia_code",
        "basic_carat_final",
        "gw_color_adjusted_final",
        "gw_clarity_adjusted_final",
        "gw_fluorescence_adjusted_final",
        "gia_culet_characteristic_final",
        "gia_culet_adjusted_final",
        "basic_inclusions_final",
        "basic_inclusions_final",
        "gia_polish_adjusted_final",
        "diameter_min",
        "diameter_max",
        "height",
        "table_size",
        "crown_angle",
        "pavilion_angle",
        "star_length",
        "lower_half",
        "girdle_thickness_number",
        "girdle_min_number",
        "girdle_max_number",
        "crown_height",
        "pavilion_depth",
        "total_depth",
        "sarine_cut_pre_polish_symmetry",
        "sarine_symmetry",
        "blockchain_address",
        "basic_remarks",
        "gw_remarks",
        "gw_adjust_remarks",
        "gia_remarks",
        "post_gia_remarks",
    )

    read_file = pd.read_csv(csv_file_path)
    data_frame = pd.DataFrame(read_file).to_dict().keys()
    for text in csv_file_content:
        if text not in data_frame:
            raise AssertionError(f"unable to find the text, {text} in the csv file")