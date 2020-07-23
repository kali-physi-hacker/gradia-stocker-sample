import time
from collections import namedtuple
from functools import partial

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import pytest
from customers.models import Entity
from grading.models import Parcel, Receipt
from ownerships.models import ParcelTransfer
from urls import add_urls_helper_functions, goto


def assert_body_contains_text(browser, search_string):
    try:
        browser.find_element_by_xpath(f'//*[text()[contains(., "{search_string}")]]')
    except NoSuchElementException:
        print(browser.get_body_text())
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
    time.sleep(0.5)
    elem.click()
    if elem_should_disappear:
        browser.wait_till_gone(elem)
    time.sleep(0.3)


def click_add(browser):
    add_link = browser.find_element_by_xpath("//a[contains(translate(., 'AD', 'ad'), 'add')]")
    # when clicking inline add new row, elem stays
    browser.slowly_click(add_link, elem_should_disappear=False)


def click_save(browser):
    save_elem = browser.find_element_by_name("_save")
    browser.slowly_click(save_elem, elem_should_disappear=True)


def search_in_admin_list_view(browser, search_string):
    search_bar = browser.find_element_by_name("q")
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
    browser.click_save = partial(click_save, browser)
    browser.search_in_admin_list_view = partial(search_in_admin_list_view, browser)
    # TODO : this is going to suck if search_string has " or '
    browser.assert_body_contains_text = partial(assert_body_contains_text, browser)


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
        driver.implicitly_wait(5)  # seconds

        driver.goto = partial(goto, driver, live_server.url)
        setup_browser_helper_functions(driver)

        yield driver
    finally:
        driver.quit()


@pytest.fixture
def erp(django_user_model):
    # for the erp to work, there are some users and group permissions that we need
    django_user_model.objects.create_user("vault")

    # create permission groups
    grader_group = Group.objects.create(name="grader")
    grader_group.permissions.add(
        Permission.objects.get(
            codename="view_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
        Permission.objects.get(
            codename="add_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
    )

    receptionist_group = Group.objects.create(name="receptionist")
    receptionist_group.permissions.add(
        Permission.objects.get(
            codename="view_entity", content_type=ContentType.objects.get(app_label="customers", model="entity")
        ),
        Permission.objects.get(
            codename="add_entity", content_type=ContentType.objects.get(app_label="customers", model="entity")
        ),
        Permission.objects.get(
            codename="view_receipt", content_type=ContentType.objects.get(app_label="grading", model="receipt")
        ),
        Permission.objects.get(
            codename="add_receipt", content_type=ContentType.objects.get(app_label="grading", model="receipt")
        ),
        Permission.objects.get(
            codename="view_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
        Permission.objects.get(
            codename="add_parcel", content_type=ContentType.objects.get(app_label="grading", model="parcel")
        ),
    )

    buyer_group = Group.objects.create(name="buyer")
    buyer_group.permissions.add(
        Permission.objects.get(
            codename="view_seller", content_type=ContentType.objects.get(app_label="purchases", model="seller")
        ),
        Permission.objects.get(
            codename="add_seller", content_type=ContentType.objects.get(app_label="purchases", model="seller")
        ),
        Permission.objects.get(
            codename="view_receipt", content_type=ContentType.objects.get(app_label="purchases", model="receipt")
        ),
        Permission.objects.get(
            codename="add_receipt", content_type=ContentType.objects.get(app_label="purchases", model="receipt")
        ),
        Permission.objects.get(
            codename="view_parcel", content_type=ContentType.objects.get(app_label="purchases", model="parcel")
        ),
        Permission.objects.get(
            codename="add_parcel", content_type=ContentType.objects.get(app_label="purchases", model="parcel")
        ),
    )


UserData = namedtuple("User", ["username", "password"])


@pytest.fixture
def user(django_user_model):
    # the way that our pytest-django live-server is setup, the db is
    # automatically flushed in between tests
    user_data = UserData(username="alice@alice.com", password="alicepassword")
    created_user = django_user_model.objects.create_user(
        user_data.username, email=user_data.username, password=user_data.password
    )
    created_user.raw_password = user_data.password
    return created_user


@pytest.fixture
def grader(django_user_model, erp):
    user_data = UserData(username="grader@grader.com", password="graderpassword")
    user = django_user_model.objects.create_user(
        user_data.username, email=user_data.username, password=user_data.password, is_staff=True
    )
    grader_group = Group.objects.get(name="grader")
    user.groups.add(grader_group)

    user.raw_password = user_data.password
    return user


@pytest.fixture
def receptionist(django_user_model, erp):
    user_data = UserData(username="receptionist@receptionist.com", password="receptionistpassword")
    user = django_user_model.objects.create_user(
        user_data.username, email=user_data.username, password=user_data.password, is_staff=True
    )
    receptionist_group = Group.objects.get(name="receptionist")
    user.groups.add(receptionist_group)

    user.raw_password = user_data.password
    return user


@pytest.fixture
def buyer(django_user_model, erp):
    user_data = UserData(username="buyer@buyer.com", password="buyerpassword")
    user = django_user_model.objects.create_user(
        user_data.username, email=user_data.username, password=user_data.password, is_staff=True
    )
    buyer_group = Group.objects.get(name="buyer")
    user.groups.add(buyer_group)

    user.raw_password = user_data.password
    return user


@pytest.fixture
def receipt(django_user_model, admin_user):
    created_receipt = Receipt.objects.create(
        entity=Entity.objects.create(name="Van Klaren", address="addressy", phone="12345678", email="vk@vk.com"),
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
        item=parcel, from_user=admin_user, to_user=django_user_model.objects.get(username="vault")
    )
    # vault confirms it has received this parcel
    ParcelTransfer.confirm_received(parcel)
    created_receipt.parcel_set.add(parcel)
    return created_receipt
