from django.contrib.auth.models import User
from selenium.webdriver.support.ui import Select

from ownerships.models import ParcelTransfer, StoneTransfer

def test_grader_can_download_id_stones(browser, stones, grader):
    
    browser.login(grader.username, grader.raw_password)
    browser.go_to_stone_page()

    # she ticks the checkbox for the first stone
    browser.find_element_by_css_selector(
        f'input[value="{stones[0].id}"]').click()
    # she ticks the checkbox for the second stone
    browser.find_element_by_css_selector(
        f'input[value="{stones[1].id}"]').click()
    
    browser.find_element_by_css_selector(
        f'input[value="{stones[2].id}"]').click()
    
    # browser.find_element_by_css_selector(
    #     f'input[value="{stones[3].id}"]').click()
    
    # browser.find_element_by_css_selector(
    #     f'input[value="{stones[4].id}"]').click()

    # she selects "Download Diamond(s) External Nanotech IDs" from the action dropdown menu
    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Download Diamond(s) External Nanotech IDs")

    browser.click_go()
    

    
def test_grader_can_download_master_report(browser, stones, grader):
    
    browser.login(grader.username, grader.raw_password)
    browser.go_to_stone_page()

    # she ticks the checkbox for the first stone
    browser.find_element_by_css_selector(
        f'input[value="{stones[0].id}"]').click()
    # she ticks the checkbox for the second stone
    browser.find_element_by_css_selector(
        f'input[value="{stones[1].id}"]').click()
    
    browser.find_element_by_css_selector(
        f'input[value="{stones[2].id}"]').click()
    
    # browser.find_element_by_css_selector(
    #     f'input[value="{stones[3].id}"]').click()
    
    # browser.find_element_by_css_selector(
    #     f'input[value="{stones[4].id}"]').click()

    # she selects "Download Master Report" from the action dropdown menu
    action_dropdown = Select(browser.find_element_by_name("action"))
    action_dropdown.select_by_visible_text("Download Master Report")

    browser.click_go()