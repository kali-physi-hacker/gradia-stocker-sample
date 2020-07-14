from collections import namedtuple

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import pytest


def assert_body_contains_text(browser, search_string):
    try:
        browser.find_element_by_xpath(f'//*[text()[contains(., "{search_string}")]]')
    except NoSuchElementException:
        print(browser.get_body_text())
        pytest.fail(f"unable to find {search_string} in browser body:\n\n{browser.get_body_text()}")


def login(browser, username, password):
    browser.goto("/admin/login/")
    browser.find_element_by_name("username").send_keys(username)
    browser.find_element_by_name("password").send_keys(password)
    browser.find_element_by_name("password").send_keys(Keys.RETURN)


@pytest.fixture
def browser(live_server, settings):
    # pytest-django automatically sets debug to false
    # we need it to be true because otherwise django.conf.urls.static just
    # ignores everything, and we don't serve the translation files
    settings.DEBUG = True
    try:
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)  # seconds

        driver.goto = lambda url: driver.get(live_server.url + url)
        driver.get_body_text = lambda: driver.find_element_by_css_selector("body").text
        driver.login = lambda username, password: login(driver, username, password)
        # TODO : this is going to suck if search_string has " or '
        driver.assert_body_contains_text = lambda search_string: assert_body_contains_text(driver, search_string)

        yield driver
    finally:
        driver.quit()


User = namedtuple("User", ["username", "password"])


@pytest.fixture
def user(django_user_model):
    # the way that our pytest-django live-server is setup, the db is
    # automatically flushed in between tests
    user_data = User(username="alice@alice.com", password="alicepassword")
    django_user_model.objects.create_user(user_data.username, email=user_data.username, password=user_data.password)
    return user_data
