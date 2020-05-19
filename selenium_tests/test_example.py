from selenium import webdriver


def test_can_see_gradia_video_in_search_result():
    try:
        # anthony opens his browser
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)

        # he goes to youtube.com
        driver.get("https://www.youtube.com")

        # he searches for blah
        elem = driver.find_element_by_css_selector("input")
        elem.send_keys("GRADIA intro")

        # he hits enter
        elem.submit()

        # he sees this
        youtube_text = driver.find_element_by_css_selector("body").text
        assert "GRADIA Intro Animation" in youtube_text
    finally:
        driver.quit()
