from functools import partial

import pytest


# this function is separated out for use in the external purchases stuff
# we use this same function, but on a different page. ie. on the purchases page
# and not the customer page
def create_entity(browser, entity_details):
    browser.click_add()

    # She fills in the details of the new entity
    browser.find_element_by_name("name").send_keys(entity_details["name"])
    browser.find_element_by_name("address").send_keys(entity_details["address"])
    browser.find_element_by_name("phone").send_keys(entity_details["phone"])
    browser.find_element_by_name("email").send_keys(entity_details["email"])

    # TODO: also fill in the authorized personnels form

    # She saves the entity detail
    browser.click_save()


def create_customer(browser, customer_details=None):
    if customer_details is None:
        customer_details = {
            "name": "Van Klaren",
            "address": "customer_address",
            "phone": "12345",
            "email": "cust@customer.com",
        }

    browser.go_to_customer_page()
    create_entity(browser, customer_details)


@pytest.fixture
def create_customer_browser_mixin(browser):
    browser.create_customer = partial(create_customer, browser)
