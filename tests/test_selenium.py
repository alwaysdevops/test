import os
import threading

import pytest


@pytest.fixture()
def live_server_url(tmp_path):
    from werkzeug.serving import make_server

    from app import create_app

    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "selenium.db")})
    server = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


@pytest.mark.skipif(
    os.environ.get("RUN_SELENIUM") != "1",
    reason="Set RUN_SELENIUM=1 and provide a browser driver to run Selenium tests.",
)
def test_homepage_loads_in_browser(live_server_url):
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    driver = webdriver.Chrome()
    try:
        driver.get(live_server_url)
        assert driver.find_element(By.TAG_NAME, "h1").text == "Register for an upcoming event"
    finally:
        driver.quit()
