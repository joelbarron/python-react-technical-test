import os
import sys

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    binary_path = os.getenv("CHROME_BINARY", "/usr/bin/chromium")
    driver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
    options.binary_location = binary_path
    service = Service(driver_path)
    return webdriver.Chrome(service=service, options=options)


def extract_first_paragraph(driver: webdriver.Chrome, term: str) -> str:
    # Wikipedia search UI is stable and quick, but we still wait for content.
    driver.get("https://www.wikipedia.org/")
    search = driver.find_element(By.ID, "searchInput")
    search.clear()
    search.send_keys(term)
    search.send_keys(Keys.ENTER)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mw-content-text p")))
    paragraphs = driver.find_elements(By.CSS_SELECTOR, "#mw-content-text p")
    for paragraph in paragraphs:
        text = paragraph.text.strip()
        if text:
            return text
    return ""


def summarize(text: str) -> str:
    base_url = os.getenv("BACKEND_BASE_URL", "http://backend:8000")
    res = requests.post(f"{base_url}/assistant/summarize", json={"text": text}, timeout=20)
    res.raise_for_status()
    return res.json()["summary"]


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python wiki_summarize.py <search term>")
        return 1
    term = " ".join(sys.argv[1:])
    driver = build_driver()
    try:
        paragraph = extract_first_paragraph(driver, term)
    finally:
        driver.quit()
    if not paragraph:
        print("No paragraph found for term.")
        return 2
    summary = summarize(paragraph)
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
