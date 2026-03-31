from scraper import get_browser 
import time
from bs4 import BeautifulSoup
import re

# 1. Player Stats (Runs)
def get_player_stats(player_name):
    driver = get_browser()
    try:
        query = f"{player_name} last 5 innings T20 score"
        driver.get(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        page_text = soup.get_text()
        runs = re.findall(r'\b\d{1,3}\b', page_text[:2000]) 
        
        if len(runs) >= 3:
            last_5 = [int(r) for r in runs[:5]]
            avg = sum(last_5) / len(last_5)
            highest = max(last_5)
            return [last_5, avg, highest]
        return None
    finally:
        driver.quit()

# 2. Bowling Stats (Missing Function Fix)
def get_bowling_stats(player_name):
    # Filhal ye dummy data de raha hai taaki error na aaye
    return {
        'total_wickets': "Fetching...",
        'economy': "Updating...",
        'wickets_list': [1, 2, 0, 1, 3]
    }

# 3. Predict Score (ML Logic)
def predict_next_score(player_name):
    stats = get_player_stats(player_name)
    if stats:
        # Simple Prediction: Average ke hisaab se
        return int(stats[1] + 5) 
    return None

# 4. Predict Wickets
def predict_next_wickets(player_name):
    return 1 # Default prediction

# 5. Compare Players
def compare_players(p1, p2):
    s1 = get_player_stats(p1)
    s2 = get_player_stats(p2)
    if s1 and s2:
        if s1[1] > s2[1]:
            return f"Sir, {p1} ka average {round(s1[1],1)} hai, jo {p2} ke {round(s2[1],1)} se behtar hai."
        else:
            return f"Sir, statistics ke hisaab se {p2} abhi form mein hai."
    return "Sir, comparison ke liye poora data nahi mil raha."

# 6. Fetch Innings Runs (Jo main.py mang raha tha)
def fetch_innings_runs(player_name):
    stats = get_player_stats(player_name)
    return stats[0] if stats else None