from functools import partial

from selenium import webdriver

import pytest
from customers.models import Entity
from extended_browser_fixtures import setup_browser_helper_functions
from grading.models import Parcel, Receipt
from ownerships.models import ParcelTransfer
from urls import goto
from user_fixtures import *  # NOQA


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
def receipt(django_user_model, erp, admin_user):
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
