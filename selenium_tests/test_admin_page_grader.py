def test_example(browser, admin_user):
    # needs to be staff to access the ERP page
    browser.login("admin", "password")

    browser.goto("/admin")

    browser.assert_body_contains_text("Portfolio Overview")
