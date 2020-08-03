import time
from functools import partial

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import pytest
from urls import add_urls_helper_functions
from user_fixtures import *  # NOQA


def assert_body_contains_text(browser, search_string):
    try:
        browser.find_element_by_xpath(f'//*[text()[contains(., "{search_string}")]]')
    except NoSuchElementException:
        pytest.fail(f"unable to find {search_string} in browser body:\n\n{browser.get_body_text()}")


def login(browser, username, password):
    browser.goto("/admin/login/")
    browser.find_element_by_name("username").send_keys(username)
    password_field = browser.find_element_by_name("password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    browser.wait_till_gone(password_field)


def wait_till_gone(browser, elem):
    try:
        WebDriverWait(browser, 2).until(EC.staleness_of(elem))
    except TimeoutException:
        raise Exception(f"element did not go away: {elem}")


def slowly_click(browser, elem, elem_should_disappear=True):
    # can go lower for headless, but need more leeway when not running headless
    time.sleep(0.4)
    elem.click()
    if elem_should_disappear:
        browser.wait_till_gone(elem)


def click_add(browser):
    add_link = browser.find_element_by_xpath("//a[contains(translate(., 'AD', 'ad'), 'add')]")
    # when clicking inline add new row, elem stays
    browser.slowly_click(add_link, elem_should_disappear=False)


def click_go(browser):
    add_link = browser.find_element_by_css_selector('button[title="Run the selected action"]')
    # when clicking inline add new row, elem stays
    browser.slowly_click(add_link, elem_should_disappear=True)


def click_save(browser):
    save_elem = browser.find_element_by_name("_save")
    browser.slowly_click(save_elem, elem_should_disappear=True)


def search_in_admin_list_view(browser, search_string):
    search_bar = browser.find_element_by_name("q")
    search_bar.clear()
    search_bar.send_keys(search_string)

    search_button = browser.find_element_by_css_selector('input[value="Search"]')
    browser.slowly_click(search_button)


# TODO: make this use some extended browser class instead
def setup_browser_helper_functions(browser):
    add_urls_helper_functions(browser)

    browser.get_body_text = lambda: browser.find_element_by_css_selector("body").text
    browser.login = partial(login, browser)
    browser.wait_till_gone = partial(wait_till_gone, browser)
    browser.slowly_click = partial(slowly_click, browser)
    browser.click_add = partial(click_add, browser)
    browser.click_go = partial(click_go, browser)
    browser.click_save = partial(click_save, browser)
    browser.search_in_admin_list_view = partial(search_in_admin_list_view, browser)
    # TODO : this is going to suck if search_string has " or '
    browser.assert_body_contains_text = partial(assert_body_contains_text, browser)
