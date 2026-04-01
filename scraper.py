import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from langchain_community.tools import DuckDuckGoSearchRun

# Online Search Engine (FREE & Working)
online_search = DuckDuckGoSearchRun()

def get_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# --- 1. MATCH SCHEDULE (LIVE) ---
def get_match_schedule(day_type="today"):
    try:
        query = f"cricket match schedule {day_type} 2026 ipl international"
        result = online_search.run(query)
        return f"Sir, online data ke mutabik: {result[:500]}"
    except:
        return "Sir, internet se schedule fetch nahi ho raha hai."

# --- 2. LIVE SCORE (REAL-TIME) ---
def get_live_score():
    try:
        # Direct live score search
        result = online_search.run("current live cricket score summary")
        if "no live match" in result.lower():
            return "Sir, abhi koi live match nahi chal raha hai."
        return f"Current Score Update: {result[:400]}"
    except:
        return "Sir, live score server se connect nahi ho pa raha hoon."

# --- 3. POINTS TABLE ---
def get_points_table():
    try:
        result = online_search.run("latest IPL 2026 points table standings")
        return f"Points Table Update: {result[:400]}"
    except:
        return "Sir, points table fetch nahi ho rahi."