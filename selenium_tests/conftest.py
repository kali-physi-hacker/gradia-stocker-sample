from functools import partial

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import pytest
from customers.models import Entity
from extended_browser_fixtures import setup_browser_helper_functions
from grading.models import (
    ClarityGrades,
    ColorGrades,
    CuletGrades,
    FluorescenceGrades,
    GeneralGrades,
    GirdleGrades,
    Parcel,
    Receipt,
    Split,
    Stone,
)
from ownerships.models import ParcelTransfer, StoneTransfer
from urls import goto
from user_fixtures import *  # NOQA

# function to take care of downloading file
def enable_download_headless(browser,download_dir):
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)

@pytest.fixture
def browser(live_server, settings):
    # pytest-django automatically sets debug to false
    # we need it to be true because otherwise django.conf.urls.static just
    # ignores everything, and we don't serve the translation files
    settings.DEBUG = True
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # change the <path_to_download_default_directory> to whatever your default download folder is located
    chrome_options.add_experimental_option("prefs", {
            "download.default_directory": "~/code/django/",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
    })
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    # change the <path_to_place_downloaded_file> to your directory where you would like to place the downloaded file
    download_dir = "~/code/django/"

    # function to handle setting up headless download
    enable_download_headless(driver, download_dir)
    try:
        driver.implicitly_wait(5)  # seconds

        driver.goto = partial(goto, driver, live_server.url)
        setup_browser_helper_functions(driver)

        yield driver
    finally:
        driver.quit()


@pytest.fixture
def receipt(django_user_model, erp, admin_user):
    created_receipt = Receipt.objects.create(
        entity=Entity.objects.create(
            name="Van Klaren", address="addressy", phone="12345678", email="vk@vk.com"
        ),
        code="VK-0001",
        intake_by=admin_user,
    )
    parcel = Parcel.objects.create(
        receipt=created_receipt,
        gradia_parcel_code="parcel1",
        customer_parcel_code="cust-parcel-1",
        total_carats=2,
        total_pieces=2,
        reference_price_per_carat=1,
    )
    # the parcel is received by admin user and put into the vault
    ParcelTransfer.objects.create(
        item=parcel,
        from_user=admin_user,
        to_user=django_user_model.objects.get(username="vault"),
        created_by=admin_user,
    )
    # vault confirms it has received this parcel
    ParcelTransfer.confirm_received(parcel)
    created_receipt.parcel_set.add(parcel)
    return created_receipt


@pytest.fixture
def stones(django_user_model, receipt, data_entry_clerk, grader, receptionist):
    parcel = receipt.parcel_set.first()
    split = Split.objects.create(original_parcel=parcel, split_by=data_entry_clerk)
    stone_list = [
        Stone.objects.create(
            data_entry_user=data_entry_clerk,
            internal_id=1,
            split_from=split,
            basic_carat=4,
            basic_culet=CuletGrades.VERY_SMALL,
            basic_fluorescence=FluorescenceGrades.MEDIUM,
            grader_1=grader,
            basic_color_1=ColorGrades.COLORLESS_D,
            basic_final_color=ColorGrades.COLORLESS_D,
            basic_clarity_1=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_final_clarity=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_polish_1=GeneralGrades.GOOD,
            basic_final_polish=GeneralGrades.GOOD,
            diameter_min=10,
            diameter_max=12,
            height=14,
            girdle_min=GirdleGrades.THIN,
            girdle_max=GirdleGrades.THIN,
            girdle_grade=GirdleGrades.THIN,
            culet_size=CuletGrades.MEDIUM,
            total_depth=43,
            total_depth_grade=GeneralGrades.EXCELLENT,
            sheryl_cut=GeneralGrades.EXCELLENT,
            sarine_cut=GeneralGrades.EXCELLENT,
            cut_grade_est_table=GeneralGrades.EXCELLENT,
            sheryl_symmetry=GeneralGrades.GOOD,
            sarine_symmetry=GeneralGrades.GOOD,
            symmetry_grade=GeneralGrades.GOOD,
            roundness=1,
            roundness_grade=GeneralGrades.GOOD,
            table_size=43,
            table_size_grade=GeneralGrades.GOOD,
            crown_angle=23,
            crown_angle_grade=GeneralGrades.GOOD,
            pavilion_angle=54,
            pavilion_angle_grade=GeneralGrades.GOOD,
            star_length=24,
            star_length_grade=GeneralGrades.GOOD,
            lower_half=94,
            lower_half_grade=GeneralGrades.GOOD,
            girdle_thick=1,
            girdle_thick_grade=GeneralGrades.GOOD,
            crown_height=53,
            crown_height_grade=GeneralGrades.GOOD,
            pavilion_depth=23,
            pavilion_depth_grade=GeneralGrades.GOOD,
            misalignment=1,
            misalignment_grade=GeneralGrades.GOOD,
            table_edge_var=1,
            table_edge_var_grade=GeneralGrades.GOOD,
            table_off_center=1,
            table_off_center_grade=GeneralGrades.GOOD,
            culet_off_center=1,
            culet_off_center_grade=GeneralGrades.GOOD,
            table_off_culet=1,
            table_off_culet_grade=GeneralGrades.GOOD,
            star_angle=1,
            star_angle_grade=GeneralGrades.GOOD,
            upper_half_angle=1,
            upper_half_angle_grade=GeneralGrades.GOOD,
            lower_half_angle=1,
            lower_half_angle_grade=GeneralGrades.GOOD,
        ),
        Stone.objects.create(
            data_entry_user=data_entry_clerk,
            internal_id=2,
            split_from=split,
            basic_carat=4,
            basic_culet=CuletGrades.VERY_SMALL,
            basic_fluorescence=FluorescenceGrades.MEDIUM,
            grader_1=grader,
            basic_color_1=ColorGrades.COLORLESS_D,
            basic_final_color=ColorGrades.COLORLESS_D,
            basic_clarity_1=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_final_clarity=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_polish_1=GeneralGrades.GOOD,
            basic_final_polish=GeneralGrades.GOOD,
            diameter_min=10,
            diameter_max=12,
            height=14,
            girdle_min=GirdleGrades.THIN,
            girdle_max=GirdleGrades.THIN,
            girdle_grade=GirdleGrades.THIN,
            culet_size=CuletGrades.MEDIUM,
            total_depth=43,
            total_depth_grade=GeneralGrades.EXCELLENT,
            sheryl_cut=GeneralGrades.EXCELLENT,
            sarine_cut=GeneralGrades.EXCELLENT,
            cut_grade_est_table=GeneralGrades.EXCELLENT,
            sheryl_symmetry=GeneralGrades.GOOD,
            sarine_symmetry=GeneralGrades.GOOD,
            symmetry_grade=GeneralGrades.GOOD,
            roundness=1,
            roundness_grade=GeneralGrades.GOOD,
            table_size=43,
            table_size_grade=GeneralGrades.GOOD,
            crown_angle=23,
            crown_angle_grade=GeneralGrades.GOOD,
            pavilion_angle=54,
            pavilion_angle_grade=GeneralGrades.GOOD,
            star_length=24,
            star_length_grade=GeneralGrades.GOOD,
            lower_half=94,
            lower_half_grade=GeneralGrades.GOOD,
            girdle_thick=1,
            girdle_thick_grade=GeneralGrades.GOOD,
            crown_height=53,
            crown_height_grade=GeneralGrades.GOOD,
            pavilion_depth=23,
            pavilion_depth_grade=GeneralGrades.GOOD,
            misalignment=1,
            misalignment_grade=GeneralGrades.GOOD,
            table_edge_var=1,
            table_edge_var_grade=GeneralGrades.GOOD,
            table_off_center=1,
            table_off_center_grade=GeneralGrades.GOOD,
            culet_off_center=1,
            culet_off_center_grade=GeneralGrades.GOOD,
            table_off_culet=1,
            table_off_culet_grade=GeneralGrades.GOOD,
            star_angle=1,
            star_angle_grade=GeneralGrades.GOOD,
            upper_half_angle=1,
            upper_half_angle_grade=GeneralGrades.GOOD,
            lower_half_angle=1,
            lower_half_angle_grade=GeneralGrades.GOOD,
        ),
        Stone.objects.create(
            data_entry_user=data_entry_clerk,
            internal_id=3,
            split_from=split,
            basic_carat=4,
            basic_culet=CuletGrades.VERY_SMALL,
            basic_fluorescence=FluorescenceGrades.MEDIUM,
            grader_1=grader,
            basic_color_1=ColorGrades.COLORLESS_D,
            basic_final_color=ColorGrades.COLORLESS_D,
            basic_clarity_1=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_final_clarity=ClarityGrades.INTERNALLY_FLAWLESS,
            basic_polish_1=GeneralGrades.GOOD,
            basic_final_polish=GeneralGrades.GOOD,
            diameter_min=10,
            diameter_max=12,
            height=14,
            girdle_min=GirdleGrades.THIN,
            girdle_max=GirdleGrades.THIN,
            girdle_grade=GirdleGrades.THIN,
            culet_size=CuletGrades.MEDIUM,
            total_depth=43,
            total_depth_grade=GeneralGrades.EXCELLENT,
            sheryl_cut=GeneralGrades.EXCELLENT,
            sarine_cut=GeneralGrades.EXCELLENT,
            cut_grade_est_table=GeneralGrades.EXCELLENT,
            sheryl_symmetry=GeneralGrades.GOOD,
            sarine_symmetry=GeneralGrades.GOOD,
            symmetry_grade=GeneralGrades.GOOD,
            roundness=1,
            roundness_grade=GeneralGrades.GOOD,
            table_size=43,
            table_size_grade=GeneralGrades.GOOD,
            crown_angle=23,
            crown_angle_grade=GeneralGrades.GOOD,
            pavilion_angle=54,
            pavilion_angle_grade=GeneralGrades.GOOD,
            star_length=24,
            star_length_grade=GeneralGrades.GOOD,
            lower_half=94,
            lower_half_grade=GeneralGrades.GOOD,
            girdle_thick=1,
            girdle_thick_grade=GeneralGrades.GOOD,
            crown_height=53,
            crown_height_grade=GeneralGrades.GOOD,
            pavilion_depth=23,
            pavilion_depth_grade=GeneralGrades.GOOD,
            misalignment=1,
            misalignment_grade=GeneralGrades.GOOD,
            table_edge_var=1,
            table_edge_var_grade=GeneralGrades.GOOD,
            table_off_center=1,
            table_off_center_grade=GeneralGrades.GOOD,
            culet_off_center=1,
            culet_off_center_grade=GeneralGrades.GOOD,
            table_off_culet=1,
            table_off_culet_grade=GeneralGrades.GOOD,
            star_angle=1,
            star_angle_grade=GeneralGrades.GOOD,
            upper_half_angle=1,
            upper_half_angle_grade=GeneralGrades.GOOD,
            lower_half_angle=1,
            lower_half_angle_grade=GeneralGrades.GOOD,
        ),
    ]
    for s in stone_list:
        StoneTransfer.objects.create(
            item=s,
            from_user=receptionist,
            to_user=django_user_model.objects.get(username="vault"),
            created_by=receptionist,
        )
    return stone_list
