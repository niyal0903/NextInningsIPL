# engine.py
import zipfile, json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from config import ZIP_PATH, name_map

# -------- BATTING --------
def fetch_innings_runs(player):
    player_lower = player.lower().strip()
    mapped = name_map.get(player_lower, player_lower)
    innings_runs = []
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        for filename in z.namelist():
            if not filename.endswith(".json"):
                continue
            try:
                with z.open(filename) as f:
                    match = json.load(f)
                for innings in match.get("innings", []):
                    total = 0
                    played = False
                    for over in innings.get("overs", []):
                        for ball in over.get("deliveries", []):
                            batter = ball.get("batter","").lower().strip()
                            if batter == mapped:
                                total += ball.get("runs",{}).get("batter",0)
                                played = True
                    if played:
                        innings_runs.append(total)
            except:
                continue
    return innings_runs

def get_player_stats(player):
    runs = fetch_innings_runs(player)
    if not runs:
        return None
    return runs[-5:], round(sum(runs)/len(runs), 2), max(runs)

def predict_next_score(player):
    runs = fetch_innings_runs(player)
    if len(runs) < 5:
        return None
    X = np.arange(1, len(runs)+1).reshape(-1, 1)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, np.array(runs))
    return round(float(model.predict([[len(runs)+1]])[0]), 1)

def compare_players(p1, p2):
    runs1 = fetch_innings_runs(p1)
    runs2 = fetch_innings_runs(p2)
    if not runs1 or not runs2:
        return "Ek ya dono players ka data nahi mila sir"
    avg1 = round(sum(runs1)/len(runs1), 2)
    avg2 = round(sum(runs2)/len(runs2), 2)
    better = p1 if avg1 > avg2 else p2
    return (f"{p1} average {avg1} highest {max(runs1)}. "
            f"{p2} average {avg2} highest {max(runs2)}. "
            f"{better} is better based on average.")

# -------- BOWLING --------
def fetch_bowling_stats(player):
    player_lower = player.lower().strip()
    mapped = name_map.get(player_lower, player_lower)
    wickets_list = []
    runs_given_list = []
    overs_list = []
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        for filename in z.namelist():
            if not filename.endswith(".json"):
                continue
            try:
                with z.open(filename) as f:
                    match = json.load(f)
                for innings in match.get("innings", []):
                    wickets = 0
                    runs_given = 0
                    balls_bowled = 0
                    bowled = False
                    for over in innings.get("overs", []):
                        for ball in over.get("deliveries", []):
                            bowler = ball.get("bowler", "").lower().strip()
                            if bowler == mapped:
                                bowled = True
                                runs_given += ball.get("runs", {}).get("total", 0)
                                balls_bowled += 1
                                wicket = ball.get("wickets", [])
                                if wicket:
                                    for w in wicket:
                                        if w.get("kind", "") != "run out":
                                            wickets += 1
                    if bowled:
                        wickets_list.append(wickets)
                        runs_given_list.append(runs_given)
                        overs_list.append(round(balls_bowled / 6, 1))
            except:
                continue
    return wickets_list, runs_given_list, overs_list

def get_bowling_stats(player):
    wickets_list, runs_given_list, overs_list = fetch_bowling_stats(player)
    if not wickets_list:
        return None
    total_wickets = sum(wickets_list)
    total_runs_given = sum(runs_given_list)
    total_overs = sum(overs_list)
    best_bowling = max(wickets_list)
    economy = round(total_runs_given / total_overs, 2) if total_overs > 0 else 0
    bowl_avg = round(total_runs_given / total_wickets, 2) if total_wickets > 0 else 0
    three_fers = sum(1 for w in wickets_list if w >= 3)
    return {
        "total_wickets": total_wickets,
        "innings": len(wickets_list),
        "best_bowling": best_bowling,
        "economy": economy,
        "bowling_average": bowl_avg,
        "three_fers": three_fers,
        "wickets_list": wickets_list[-5:]
    }

def predict_next_wickets(player):
    wickets_list, _, _ = fetch_bowling_stats(player)
    if len(wickets_list) < 5:
        return None
    X = np.arange(1, len(wickets_list)+1).reshape(-1, 1)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, np.array(wickets_list))
    predicted = model.predict([[len(wickets_list)+1]])[0]
    return round(float(predicted), 1)