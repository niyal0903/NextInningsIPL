# import speech_recognition as sr
# import threading
# import pythoncom
# import win32com.client
# import os
# import time
# import json
# import zipfile
# import numpy as np
# import pandas as pd
# import requests
# from bs4 import BeautifulSoup
# from sklearn.linear_model import LinearRegression

# # -------- NAME MAP --------
# name_map = {
#     "virat kohli": "v kohli",
#     "rohit sharma": "ro sharma",
#     "ms dhoni": "ms dhoni",
#     "suresh raina": "su raina",
#     "gautam gambhir": "g gambhir",
#     "shikhar dhawan": "s dhawan",
#     "david warner": "da warner",
#     "ab de villiers": "ab de villiers",
#     "yuvraj singh": "yuvraj singh",
#     "hardik pandya": "h pandya",
# }

# ZIP_PATH = r"N:\mega project jarvis\cricketagent\data\ipl.json.zip.zip"

# # -------- RUNS FETCH FUNCTION --------
# def fetch_innings_runs(player):
#     player_lower = player.lower().strip()
#     mapped = name_map.get(player_lower, player_lower)
#     innings_runs = []

#     with zipfile.ZipFile(ZIP_PATH, "r") as z:
#         for filename in z.namelist():
#             if not filename.endswith(".json"):
#                 continue
#             try:
#                 with z.open(filename) as f:
#                     match = json.load(f)
#                 for innings in match.get("innings", []):
#                     total = 0
#                     played = False
#                     for over in innings.get("overs", []):
#                         for ball in over.get("deliveries", []):
#                             batter = ball.get("batter", "").lower().strip()
#                             if batter == mapped:
#                                 total += ball.get("runs", {}).get("batter", 0)
#                                 played = True
#                     if played:
#                         innings_runs.append(total)
#             except:
#                 continue

#     return innings_runs

# # -------- PLAYER STATS --------
# def get_player_stats(player):
#     innings_runs = fetch_innings_runs(player)
#     if not innings_runs:
#         return None
#     last5 = innings_runs[-5:]
#     avg = sum(innings_runs) / len(innings_runs)
#     highest = max(innings_runs)
#     return last5, avg, highest

# # -------- ML PREDICTION --------
# def predict_next_score(player):
#     innings_runs = fetch_innings_runs(player)
#     if len(innings_runs) < 5:
#         return None

#     df = pd.DataFrame({
#         "innings_no": np.arange(1, len(innings_runs) + 1),
#         "runs": innings_runs
#     })

#     model = LinearRegression()
#     model.fit(df[["innings_no"]], df["runs"])
#     predicted = model.predict([[len(innings_runs) + 1]])[0]
#     return round(predicted, 1)

# # -------- PLAYER COMPARISON --------
# def compare_players(player1, player2):
#     runs1 = fetch_innings_runs(player1)
#     runs2 = fetch_innings_runs(player2)

#     if not runs1 or not runs2:
#         return "Ek ya dono players ka data nahi mila sir"

#     avg1 = round(sum(runs1) / len(runs1), 2)
#     avg2 = round(sum(runs2) / len(runs2), 2)
#     high1 = max(runs1)
#     high2 = max(runs2)
#     better = player1 if avg1 > avg2 else player2

#     return (f"{player1} average {avg1} highest {high1}. "
#             f"{player2} average {avg2} highest {high2}. "
#             f"{better} is better based on average.")

# # -------- LIVE SCORE - FREE WEB SCRAPING --------
# def get_live_score():
#     try:
#         headers = {"User-Agent": "Mozilla/5.0"}
#         url = "https://www.espncricinfo.com/live-cricket-score"
#         res = requests.get(url, headers=headers, timeout=5)
#         soup = BeautifulSoup(res.text, "html.parser")

#         matches = soup.find_all("div", class_="ds-p-4")
#         if not matches:
#             return "Abhi koi live match nahi hai sir"

#         result = ""
#         for m in matches[:2]:
#             text = m.get_text(separator=" ", strip=True)
#             if text:
#                 result += text[:150] + ". "

#         return result if result else "Live score nahi mila sir"

#     except Exception as e:
#         print("Live score error:", e)
#         return "Live score fetch karne mein problem hui sir"

# # -------- MATCH SCHEDULE - FREE WEB SCRAPING --------
# def get_match_schedule():
#     try:
#         headers = {"User-Agent": "Mozilla/5.0"}
#         url = "https://www.espncricinfo.com/series/ipl-2026"
#         res = requests.get(url, headers=headers, timeout=5)
#         soup = BeautifulSoup(res.text, "html.parser")

#         matches = soup.find_all("div", class_="ds-p-4")
#         if not matches:
#             return "Schedule nahi mila sir"

#         result = "Upcoming IPL 2026 matches: "
#         for m in matches[:3]:
#             text = m.get_text(separator=" ", strip=True)
#             if text:
#                 result += text[:100] + ". "

#         return result if result else "Schedule nahi mila sir"

#     except Exception as e:
#         print("Schedule error:", e)
#         return "Schedule fetch karne mein problem hui sir"

# # -------- POINTS TABLE - FREE WEB SCRAPING --------
# def get_points_table():
#     try:
#         headers = {"User-Agent": "Mozilla/5.0"}
#         url = "https://www.espncricinfo.com/series/ipl-2026/points-table"
#         res = requests.get(url, headers=headers, timeout=5)
#         soup = BeautifulSoup(res.text, "html.parser")

#         rows = soup.find_all("tr")
#         if not rows:
#             return "Points table nahi mila sir"

#         result = "IPL 2026 points table: "
#         for i, row in enumerate(rows[1:6], 1):
#             cols = row.find_all("td")
#             if cols:
#                 team = cols[0].get_text(strip=True)
#                 pts = cols[-1].get_text(strip=True)
#                 result += f"{i}. {team} {pts} points. "

#         return result if result else "Points table nahi mila sir"

#     except Exception as e:
#         print("Points table error:", e)
#         return "Points table fetch karne mein problem hui sir"

# # -------- JARVIS VOICE LOOP --------
# def jarvis_loop():
#     pythoncom.CoInitialize()
#     speaker = win32com.client.Dispatch("SAPI.SpVoice")

#     def speak(text):
#         print("Jarvis:", text)
#         speaker.Speak(text)

#     recognizer = sr.Recognizer()
#     speak("Jarvis is online tell me sir")

#     while True:
#         try:
#             with sr.Microphone() as source:
#                 print("Listening...")
#                 recognizer.adjust_for_ambient_noise(source, duration=1)
#                 audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

#             print("Recognizing...")
#             command = recognizer.recognize_google(audio, language="en-IN").lower().strip()
#             print("You said:", command)

#             # Wake word
#             if "jarvis" in command:
#                 speak("Yes sir")

#             # Live Score
#             elif any(word in command for word in ["live score", "current score", "score"]):
#                 speak("Fetching live score sir please wait")
#                 speak(get_live_score())

#             # Match Schedule
#             elif any(word in command for word in ["schedule", "next match", "aaj ka match", "upcoming match"]):
#                 speak("Fetching match schedule sir please wait")
#                 speak(get_match_schedule())

#             # Points Table
#             elif any(word in command for word in ["points table", "standings", "ranking"]):
#                 speak("Fetching points table sir please wait")
#                 speak(get_points_table())

#             # Player Comparison
#             elif any(word in command for word in ["compare", "vs", "versus", "better player"]):
#                 speak("Which two players to compare sir? Say with and in between")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 players = recognizer.recognize_google(audio, language="en-IN").strip()
#                 print("Players:", players)
#                 if " and " in players.lower():
#                     parts = players.lower().split(" and ")
#                     p1 = parts[0].strip().title()
#                     p2 = parts[1].strip().title()
#                     speak(f"Comparing {p1} and {p2} sir")
#                     speak(compare_players(p1, p2))
#                 else:
#                     speak("Please say two player names with and in between sir")

#             # ML Prediction
#             elif any(word in command for word in ["predict", "prediction", "next score", "next innings"]):
#                 speak("Which player to predict sir?")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
#                 print("Player:", player)
#                 speak(f"Predicting next score for {player} sir")
#                 predicted = predict_next_score(player)
#                 if predicted:
#                     speak(f"{player} predicted next innings score is {predicted} runs sir")
#                 else:
#                     speak("Not enough data to predict sir")

#             # Player Stats
#             elif any(word in command for word in [
#                 "player status", "player stats", "player statistic",
#                 "player statistics", "player state", "player record",
#                 "player performance", "cricket player stats"
#             ]):
#                 speak("Which player sir")
#                 with sr.Microphone() as source:
#                     print("Listening player name...")
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
#                 print("Player:", player)
#                 stats = get_player_stats(player)
#                 if stats:
#                     last5, avg, highest = stats
#                     speak(f"{player} last five innings runs {last5}")
#                     speak(f"Average run {round(avg, 2)}")
#                     speak(f"Highest run {highest}")
#                 else:
#                     speak("Player data not found")

#             # Exit
#             elif any(word in command for word in ["exit", "stop", "bye", "goodbye"]):
#                 speak("Goodbye sir")
#                 os._exit(0)

#         except sr.WaitTimeoutError:
#             print("No voice detected")
#         except sr.UnknownValueError:
#             print("Speech not recognized")
#         except Exception as e:
#             print("Error:", e)

# # -------- START VOICE THREAD --------
# voice_thread = threading.Thread(target=jarvis_loop)
# voice_thread.daemon = True
# voice_thread.start()

# # -------- KEEP PROGRAM RUNNING --------
# while True:
#     time.sleep(1)



# jarvis.py
# jarvis.py
import speech_recognition as sr
import threading
import pythoncom
import win32com.client
import os
import time

# -------- ALAG FILES SE IMPORT --------
from engine import fetch_innings_runs, get_player_stats, predict_next_score, compare_players, get_bowling_stats, predict_next_wickets
from scraper import get_live_score, get_match_schedule, get_points_table

# -------- JARVIS VOICE LOOP --------
def jarvis_loop():
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    def speak(text):
        print("Jarvis:", text)
        speaker.Speak(text)

    recognizer = sr.Recognizer()
    speak("Jarvis is online tell me sir")

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

            print("Recognizing...")
            command = recognizer.recognize_google(audio, language="en-IN").lower().strip()
            print("You said:", command)

            # Wake word
            if "jarvis" in command:
                speak("Yes sir")

            # Live Score
            elif any(word in command for word in ["live score", "current score", "score"]):
                speak("Fetching live score sir please wait")
                speak(get_live_score())

            # Match Schedule
            elif any(word in command for word in ["schedule", "next match", "aaj ka match", "upcoming match"]):
                speak("Fetching match schedule sir please wait")
                speak(get_match_schedule())

            # Points Table
            elif any(word in command for word in ["points table", "standings", "ranking"]):
                speak("Fetching points table sir please wait")
                speak(get_points_table())

            # Player Comparison
            elif any(word in command for word in ["compare", "vs", "versus", "better player"]):
                speak("Which two players to compare sir? Say with and in between")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                players = recognizer.recognize_google(audio, language="en-IN").strip()
                print("Players:", players)
                if " and " in players.lower():
                    parts = players.lower().split(" and ")
                    p1 = parts[0].strip().title()
                    p2 = parts[1].strip().title()
                    speak(f"Comparing {p1} and {p2} sir")
                    speak(compare_players(p1, p2))
                else:
                    speak("Please say two player names with and in between sir")

            # ML Prediction — batting ya bowling dono
            elif any(word in command for word in [
                "predict", "prediction", "next score",
                "next innings", "predict bowling", "next wicket",
                "bowling prediction", "wicket prediction"
            ]):
                speak("Which player sir?")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                player = recognizer.recognize_google(
                    audio, language="en-IN").strip()
                print("Player:", player)
                speak("Batting prediction chahiye ya bowling sir?")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                pred_type = recognizer.recognize_google(
                    audio, language="en-IN").lower().strip()
                print("Type:", pred_type)
                if "bowl" in pred_type or "wicket" in pred_type:
                    speak(f"Predicting wickets for {player} sir")
                    predicted = predict_next_wickets(player)
                    if predicted:
                        speak(f"{player} next match mein {predicted} wickets predicted hain sir")
                    else:
                        speak("Not enough bowling data to predict sir")
                else:
                    speak(f"Predicting next score for {player} sir")
                    predicted = predict_next_score(player)
                    if predicted:
                        speak(f"{player} predicted next innings score is {predicted} runs sir")
                    else:
                        speak("Not enough data to predict sir")

            # Player Stats
            elif any(word in command for word in [
                "player status", "player stats", "player statistic",
                "player statistics", "player state", "player record",
                "player performance", "cricket player stats",
            ]):
                speak("Which player sir")
                with sr.Microphone() as source:
                    print("Listening player name...")
                    audio = recognizer.listen(source)
                player = recognizer.recognize_google(audio, language="en-IN").strip()
                print("Player:", player)
                stats = get_player_stats(player)
                if stats:
                    last5, avg, highest = stats
                    speak(f"{player} last five innings runs {last5}")
                    speak(f"Average run {round(avg, 2)}")
                    speak(f"Highest run {highest}")
                else:
                    speak("Player data not found")

            # Bowling Stats
            elif any(word in command for word in [
                "bowling stats", "bowling record", "bowling performance",
                "kitne wickets", "bowler stats", "bowling figures",
                "performance", "wickets"
            ]):
                speak("Which player sir")
                with sr.Microphone() as source:
                    print("Listening player name...")
                    audio = recognizer.listen(source)
                player = recognizer.recognize_google(audio, language="en-IN").strip()
                print("Player:", player)
                stats = get_bowling_stats(player)
                if stats:
                    speak(f"{player} bowling stats sir")
                    speak(f"Total wickets {stats['total_wickets']}")
                    speak(f"Best bowling {stats['best_bowling']} wickets in a match")
                    speak(f"Economy rate {stats['economy']} runs per over")
                    speak(f"Bowling average {stats['bowling_average']}")
                    speak(f"Three wicket hauls {stats['three_fers']}")
                    speak(f"Last 5 innings wickets {stats['wickets_list']}")
                else:
                    speak(f"{player} ka bowling data nahi mila sir")

            # Full Stats — batting + bowling dono
            elif any(word in command for word in [
                "full stats", "complete stats", "all round",
                "allrounder", "batting bowling", "dono stats",
                "full performance", "poori stats"
            ]):
                speak("Which player sir?")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                player = recognizer.recognize_google(
                    audio, language="en-IN").strip()
                print("Player:", player)
                speak(f"Fetching complete stats for {player} sir please wait")
                bat_stats = get_player_stats(player)
                if bat_stats:
                    last5, avg, highest = bat_stats
                    runs = fetch_innings_runs(player)
                    fifties = sum(1 for r in runs if r >= 50)
                    hundreds = sum(1 for r in runs if r >= 100)
                    ducks = sum(1 for r in runs if r == 0)
                    speak(f"Batting stats sir")
                    speak(f"Total innings {len(runs)}")
                    speak(f"Average {avg}")
                    speak(f"Highest score {highest}")
                    speak(f"Fifties {fifties}")
                    speak(f"Hundreds {hundreds}")
                    speak(f"Ducks {ducks}")
                    speak(f"Last 5 innings {last5}")
                else:
                    speak(f"{player} ka batting data nahi mila sir")
                bowl_stats = get_bowling_stats(player)
                if bowl_stats:
                    speak(f"Bowling stats sir")
                    speak(f"Total wickets {bowl_stats['total_wickets']}")
                    speak(f"Best bowling {bowl_stats['best_bowling']} wickets in a match")
                    speak(f"Economy rate {bowl_stats['economy']}")
                    speak(f"Bowling average {bowl_stats['bowling_average']}")
                    speak(f"Three wicket hauls {bowl_stats['three_fers']}")
                    speak(f"Last 5 innings wickets {bowl_stats['wickets_list']}")
                else:
                    speak(f"{player} bowling nahi karte sir")

            # Exit
            elif any(word in command for word in ["exit", "stop", "bye", "goodbye"]):
                speak("Goodbye sir")
                os._exit(0)

        except sr.WaitTimeoutError:
            print("No voice detected")
        except sr.UnknownValueError:
            print("Speech not recognized")
        except Exception as e:
            print("Error:", e)

# -------- START VOICE THREAD --------
voice_thread = threading.Thread(target=jarvis_loop)
voice_thread.daemon = True
voice_thread.start()

# -------- KEEP PROGRAM RUNNING --------
while True:
    time.sleep(1)