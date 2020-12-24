import os
import shutil
from functools import partial

from selenium import webdriver

import pytest
from extended_browser_fixtures import setup_browser_helper_functions
from grading_fixtures import *  # NOQA
from urls import goto
from user_fixtures import *  # NOQA
from webdriver_manager.chrome import ChromeDriverManager

SELENIUM_PATH = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def download_file_dir():
    download_dir = os.path.join((SELENIUM_PATH), "downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    yield download_dir
    shutil.rmtree(download_dir)


# function to take care of downloading file
def enable_download_headless(browser, download_dir):
    browser.command_executor._commands["send_command"] = ("POST", "/session/$sessionId/chromium/send_command")
    params = {"cmd": "Page.setDownloadBehavior", "params": {"behavior": "allow", "downloadPath": download_dir}}
    browser.execute("send_command", params)


@pytest.fixture
def browser(live_server, settings, download_file_dir):
    # pytest-django automatically sets debug to false
    # we need it to be true because otherwise django.conf.urls.static just
    # ignores everything, and we don't serve the translation files
    settings.DEBUG = True
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    # change the <path_to_download_default_directory> to whatever your default download folder is located
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_file_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False,
        },
    )
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    # change the <path_to_place_downloaded_file> to your directory where you would like to place the downloaded file

    try:
        driver.implicitly_wait(5)  # seconds

        driver.goto = partial(goto, driver, live_server.url)
        setup_browser_helper_functions(driver)
        # function to handle setting up headless download
        enable_download_headless(driver, download_file_dir)

        yield driver
    finally:
        pass
        # driver.quit()
