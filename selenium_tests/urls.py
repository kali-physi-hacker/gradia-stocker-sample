# used in conftest


def goto(browser, server_address, url):
    if url[:4] == "http":
        browser.get(url)
    else:
        browser.get(server_address + url)


def add_urls_helper_functions(browser):
    browser.go_to_customer_page = lambda: browser.goto("/admin/customers/entity/")
    browser.go_to_receipt_page = lambda: browser.goto("/admin/grading/receipt/")
    browser.go_to_parcel_page = lambda: browser.goto("/admin/grading/parcel/")
    browser.go_to_purchases_page = lambda: browser.goto("/admin/purchases/")
