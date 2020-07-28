# used in conftest
from functools import partial


def goto(browser, server_address, url):
    if url[:4] == "http":
        browser.get(url)
    else:
        browser.get(server_address + url)


def go_to_from_admin_portal(browser, admin_page_url):
    # check that we can see the link from the admin portal
    # not just that we can directly go to it
    browser.goto("/admin/")
    link = browser.find_element_by_css_selector(f'a[href^="{admin_page_url}"]')
    browser.slowly_click(link)


def add_urls_helper_functions(browser):
    browser.go_to_customer_page = partial(go_to_from_admin_portal, browser, "/admin/customers/entity/")
    browser.go_to_split_page = partial(go_to_from_admin_portal, browser, "/admin/grading/split/")
    browser.go_to_receipt_page = partial(go_to_from_admin_portal, browser, "/admin/grading/receipt/")
    browser.go_to_parcel_page = partial(go_to_from_admin_portal, browser, "/admin/grading/parcel/")
    browser.go_to_stone_page = partial(go_to_from_admin_portal, browser, "/admin/grading/stone/")
    browser.go_to_transfer_page = partial(go_to_from_admin_portal, browser, "/admin/ownerships/parceltransfer/")
    browser.go_to_purchases_page = partial(go_to_from_admin_portal, browser, "/admin/purchases/")
