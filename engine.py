import time
import re
from scraper import search, all_text, clean, is_junk

# 1. Player Stats (Real Data Extraction using new Scraper)
def get_player_stats(player_name):
    try:
        # Naya search method use kar rahe hain (No Browser needed)
        query = f"{player_name} last 5 T20 innings scores IPL 2026"
        res = search(query, mode="text", n=5)
        raw_data = all_text(res)
        
        # Regex se runs nikalna (0 se 200 tak ke numbers)
        runs_found = re.findall(r'\b([0-9]{1,3})\b', raw_data)
        
        # Filter numbers to get realistic cricket scores
        runs = [int(r) for r in runs_found if 0 <= int(r) <= 200]
        
        if len(runs) >= 3:
            last_5 = runs[:5]
            avg = sum(last_5) / len(last_5)
            highest = max(last_5)
            return [last_5, avg, highest]
        return None
    except Exception as e:
        print(f"Error in get_player_stats: {e}")
        return None

# 2. Predict Score (ML Logic)
def predict_next_score(player_name):
    stats = get_player_stats(player_name)
    if stats:
        # ML Logic: Last 5 ka weighted average + form bonus
        predicted = int((stats[1] * 0.7) + (stats[2] * 0.3)) 
        return predicted
    return "Data available nahi hai"

# 3. Bowling Stats
def get_bowling_stats(player_name):
    try:
        query = f"{player_name} career bowling wickets and economy IPL 2026"
        res = search(query, mode="text", n=5)
        data = all_text(res)
        
        # Wickets dhoondna
        wickets_found = re.findall(r'(\d{1,3})\s*(?:wickets|wkts)', data, re.IGNORECASE)
        
        return {
            'total_wickets': wickets_found[0] if wickets_found else "Unknown",
            'economy': "7.5", # Default baseline
            'wickets_list': [1, 0, 2, 1, 1] # Recent form dummy list
        }
    except:
        return None

# 4. Predict Wickets
def predict_next_wickets(player_name):
    # Simple form-based logic
    name_l = player_name.lower()
    if any(kw in name_l for kw in ["spinner", "rashid", "chahal", "kuldeep"]):
        return 2
    return 1

# 5. Compare Players
def compare_players(p1, p2):
    s1 = get_player_stats(p1)
    s2 = get_player_stats(p2)
    if s1 and s2:
        diff = round(abs(s1[1] - s2[1]), 2)
        winner = p1 if s1[1] > s2[1] else p2
        return f"Sir, {winner} better lag raha hai, average mein {diff} runs ka fark hai."
    return "Data insufficient sir."

# 6. Fetch Innings Runs (For Graphs)
def fetch_innings_runs(player_name):
    stats = get_player_stats(player_name)
    # Agar data mile to theek, warna zero return karo graph ke liye
    return stats[0] if (stats and stats[0]) else [0, 0, 0, 0, 0]