# scraper.py
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}

# -------- SELENIUM BROWSER SETUP --------
def get_browser():
    options = Options()
    options.add_argument("--headless")        # Browser screen nahi dikhega
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")     # Warnings hide karega
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver

# -------- LIVE SCORE --------
def get_live_score():
    try:
        driver = get_browser()
        driver.get("https://www.espncricinfo.com/live-cricket-score")
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        matches = soup.find_all("div", class_="ds-p-4")
        result = ""
        for m in matches[:2]:
            text = m.get_text(separator=" ", strip=True)
            if text:
                result += text[:150] + ". "
        return result or "Abhi koi live match nahi hai sir"
    except Exception as e:
        return "Live score fetch karne mein problem hui sir"

# -------- MATCH SCHEDULE --------
def get_match_schedule():
    try:
        driver = get_browser()
        driver.get("https://www.espncricinfo.com/series/ipl-2026-1510719/match-schedule-fixtures-and-results")
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        # Match cards dhundho
        matches = soup.find_all("div", class_="ds-p-4")
        if not matches:
            # Alternate class try karo
            matches = soup.find_all("div", class_="ci-match-batsmen-wrapper")

        result = "IPL 2026 upcoming matches: "
        count = 0
        for m in matches:
            text = m.get_text(separator=" ", strip=True)
            if text and len(text) > 10:
                result += text[:120] + ". "
                count += 1
            if count >= 3:
                break

        return result if count > 0 else "Schedule nahi mila sir"
    except Exception as e:
        print("Schedule error:", e)
        return "Schedule fetch karne mein problem hui sir"

# -------- POINTS TABLE --------
def get_points_table():
    try:
        driver = get_browser()
        driver.get("https://www.espncricinfo.com/series/ipl-2026-1510719/points-table-standings")
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        rows = soup.find_all("tr")
        if not rows:
            return "Points table abhi available nahi hai sir"

        result = "IPL 2026 points table: "
        count = 0
        for row in rows[1:11]:
            cols = row.find_all("td")
            if cols and len(cols) >= 2:
                team = cols[0].get_text(strip=True)
                pts = cols[-1].get_text(strip=True)
                if team:
                    result += f"{count+1}. {team} {pts} points. "
                    count += 1
            if count >= 8:
                break

        return result if count > 0 else "Points table abhi available nahi sir"
    except Exception as e:
        print("Points table error:", e)
        return "Points table fetch karne mein problem hui sir"

