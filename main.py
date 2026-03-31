
# import speech_recognition as sr
# import threading
# import pythoncom
# import win32com.client
# import os
# import time

# # -------- ALAG FILES SE IMPORT --------
# from engine import fetch_innings_runs, get_player_stats, predict_next_score, compare_players, get_bowling_stats, predict_next_wickets
# from scraper import get_live_score, get_match_schedule, get_points_table

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

#             # ML Prediction — batting ya bowling dono
#             elif any(word in command for word in [
#                 "predict", "prediction", "next score",
#                 "next innings", "predict bowling", "next wicket",
#                 "bowling prediction", "wicket prediction"
#             ]):
#                 speak("Which player sir?")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(
#                     audio, language="en-IN").strip()
#                 print("Player:", player)
#                 speak("Batting prediction chahiye ya bowling sir?")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 pred_type = recognizer.recognize_google(
#                     audio, language="en-IN").lower().strip()
#                 print("Type:", pred_type)
#                 if "bowl" in pred_type or "wicket" in pred_type:
#                     speak(f"Predicting wickets for {player} sir")
#                     predicted = predict_next_wickets(player)
#                     if predicted:
#                         speak(f"{player} next match mein {predicted} wickets predicted hain sir")
#                     else:
#                         speak("Not enough bowling data to predict sir")
#                 else:
#                     speak(f"Predicting next score for {player} sir")
#                     predicted = predict_next_score(player)
#                     if predicted:
#                         speak(f"{player} predicted next innings score is {predicted} runs sir")
#                     else:
#                         speak("Not enough data to predict sir")

#             # Player Stats
#             elif any(word in command for word in [
#                 "player status", "player stats", "player statistic",
#                 "player statistics", "player state", "player record",
#                 "player performance", "cricket player stats",
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

#             # Bowling Stats
#             elif any(word in command for word in [
#                 "bowling stats", "bowling record", "bowling performance",
#                 "kitne wickets", "bowler stats", "bowling figures",
#                 "performance", "wickets"
#             ]):
#                 speak("Which player sir")
#                 with sr.Microphone() as source:
#                     print("Listening player name...")
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
#                 print("Player:", player)
#                 stats = get_bowling_stats(player)
#                 if stats:
#                     speak(f"{player} bowling stats sir")
#                     speak(f"Total wickets {stats['total_wickets']}")
#                     speak(f"Best bowling {stats['best_bowling']} wickets in a match")
#                     speak(f"Economy rate {stats['economy']} runs per over")
#                     speak(f"Bowling average {stats['bowling_average']}")
#                     speak(f"Three wicket hauls {stats['three_fers']}")
#                     speak(f"Last 5 innings wickets {stats['wickets_list']}")
#                 else:
#                     speak(f"{player} ka bowling data nahi mila sir")

#             # Full Stats — batting + bowling dono
#             elif any(word in command for word in [
#                 "full stats", "complete stats", "all round",
#                 "allrounder", "batting bowling", "dono stats",
#                 "full performance", "poori stats"
#             ]):
#                 speak("Which player sir?")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(
#                     audio, language="en-IN").strip()
#                 print("Player:", player)
#                 speak(f"Fetching complete stats for {player} sir please wait")
#                 bat_stats = get_player_stats(player)
#                 if bat_stats:
#                     last5, avg, highest = bat_stats
#                     runs = fetch_innings_runs(player)
#                     fifties = sum(1 for r in runs if r >= 50)
#                     hundreds = sum(1 for r in runs if r >= 100)
#                     ducks = sum(1 for r in runs if r == 0)
#                     speak(f"Batting stats sir")
#                     speak(f"Total innings {len(runs)}")
#                     speak(f"Average {avg}")
#                     speak(f"Highest score {highest}")
#                     speak(f"Fifties {fifties}")
#                     speak(f"Hundreds {hundreds}")
#                     speak(f"Ducks {ducks}")
#                     speak(f"Last 5 innings {last5}")
#                 else:
#                     speak(f"{player} ka batting data nahi mila sir")
#                 bowl_stats = get_bowling_stats(player)
#                 if bowl_stats:
#                     speak(f"Bowling stats sir")
#                     speak(f"Total wickets {bowl_stats['total_wickets']}")
#                     speak(f"Best bowling {bowl_stats['best_bowling']} wickets in a match")
#                     speak(f"Economy rate {bowl_stats['economy']}")
#                     speak(f"Bowling average {bowl_stats['bowling_average']}")
#                     speak(f"Three wicket hauls {bowl_stats['three_fers']}")
#                     speak(f"Last 5 innings wickets {bowl_stats['wickets_list']}")
#                 else:
#                     speak(f"{player} bowling nahi karte sir")

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




import speech_recognition as sr
import threading
import pythoncom
import win32com.client
import os
import time

# -------- ALAG FILES SE IMPORT --------
from engine import fetch_innings_runs, get_player_stats, predict_next_score, compare_players, get_bowling_stats, predict_next_wickets
from scraper import get_live_score, get_match_schedule, get_points_table
from graphs import show_batting_graph, show_bowling_graph

# -------- JARVIS VOICE LOOP --------
def jarvis_loop():
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    def speak(text):
        print("Jarvis:", text)
        speaker.Speak(text)

    recognizer = sr.Recognizer()
    # Background noise ko control karne ke liye
    recognizer.dynamic_energy_threshold = True 
    
    speak("Jarvis is online. Tell me sir.")

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

            print("Recognizing...")
            # Hindi-English dono mix commands catch karne ke liye
            command = recognizer.recognize_google(audio, language="en-IN").lower().strip()
            print("You said:", command)

            # 1. Wake word
            if "jarvis" in command:
                speak("Yes sir, I am listening")

            # 2. Live Score (Keywords badha diye hain)
            elif any(word in command for word in ["live score", "current score", "score", "match kya hua", "score kya hai"]):
                speak("Fetching live score sir please wait")
                speak(get_live_score())

            # 3. Match Schedule (Fixed: Ab ye "schedule" pakka catch karega)
            # 3. Match Schedule (Fixed for "Call" vs "Kal" issue)
            elif any(word in command for word in ["match", "schedule", "fixtures", "kiska match hai", "today", "tomorrow", "yesterday"]):
                day = "today" # Default
                
                # Yesterday logic (Handling "Call" instead of "Kal")
                if any(word in command for word in ["yesterday", "beeta hua", "last match", "call"]):
                    day = "yesterday"
                
                # Tomorrow logic (Handling "Kal" or "Tomorrow")
                elif any(word in command for word in ["tomorrow", "kal", "next match"]):
                    day = "tomorrow"
                
                # Today logic
                elif "today" in command or "aaj" in command:
                    day = "today"

                # Action: Ab Jarvis 100% bolega
                speak(f"Checking {day} match schedule for you sir...")
                
                try:
                    from scraper import get_match_schedule
                    result = get_match_schedule(day) 
                    speak(result) 
                except Exception as e:
                    print(f"Error: {e}")
                    speak("Sir, schedule check karne mein problem ho rahi hai.")

            # 4. Points Table
            elif any(word in command for word in ["points table", "standings", "ranking", "kaun upar hai"]):
                speak("Fetching points table sir please wait")
                speak(get_points_table())

            # 5. Player Comparison
            elif any(word in command for word in ["compare", "vs", "versus", "better player", "mukabla"]):
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
                    speak("Please say two player names with 'and' in between sir")

            # 6. ML Prediction
            elif any(word in command for word in ["predict", "prediction", "next score", "wickets", "kitne wicket lega"]):
                speak("Which player sir?")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                player = recognizer.recognize_google(audio, language="en-IN").strip()
                
                speak("Batting prediction chahiye ya bowling sir?")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                pred_type = recognizer.recognize_google(audio, language="en-IN").lower().strip()
                
                if "bowling" in pred_type or "wicket" in pred_type:
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

            # 7. Player Stats
            elif any(word in command for word in ["player stats", "statistics", "record", "performance", "kaisa khelta hai"]):
                speak("Which player sir")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                player = recognizer.recognize_google(audio, language="en-IN").strip()
                stats = get_player_stats(player)
                if stats:
                    last5, avg, highest = stats
                    speak(f"{player} last five innings runs {last5}")
                    speak(f"Average run {round(avg, 2)}")
                    speak(f"Highest run {highest}")
                else:
                    speak("Player data not found")

            # 8. Bowling Stats
            elif any(word in command for word in ["bowling stats", "bowling record", "wickets list", "kitne wicket liye"]):
                speak("Which player sir")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                player = recognizer.recognize_google(audio, language="en-IN").strip()
                stats = get_bowling_stats(player)
                if stats:
                    speak(f"{player} bowling stats sir")
                    speak(f"Total wickets {stats['total_wickets']}, Economy rate {stats['economy']}")
                    speak(f"Last five innings wickets are {stats['wickets_list']}")
                else:
                    speak(f"{player} ka bowling data nahi mila sir")

            # 9. Graphs (Batting & Bowling)
            elif "graph" in command or "chart" in command:
                speak("Which player sir?")
                with sr.Microphone() as source:
                    audio = recognizer.listen(source)
                player = recognizer.recognize_google(audio, language="en-IN").strip()
                
                if "bat" in command or "run" in command:
                    speak(f"Showing batting graph for {player}")
                    show_batting_graph(player)
                else:
                    speak(f"Showing bowling graph for {player}")
                    show_bowling_graph(player)

            # 10. Exit
            elif any(word in command for word in ["exit", "stop", "bye", "goodbye", "chalo bye"]):
                speak("Goodbye sir, have a nice day")
                os._exit(0)

        except Exception as e:
            print("Listening...") # Loop chalta rahega

# -------- START VOICE THREAD --------
voice_thread = threading.Thread(target=jarvis_loop)
voice_thread.daemon = True
voice_thread.start()

while True:
    time.sleep(1)