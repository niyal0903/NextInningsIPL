# import speech_recognition as sr
# import threading
# import pythoncom
# import win32com.client
# import os
# import re
# import time
# from ddgs import DDGS 

# # -------- ALAG FILES SE IMPORT --------
# from engine import fetch_innings_runs, get_player_stats, predict_next_score, compare_players, get_bowling_stats, predict_next_wickets
# from scraper import get_live_score, get_match_schedule, get_points_table
# from graphs import show_batting_graph, show_bowling_graph

# # --- THE 100% NO-BLOCK SCORE EXTRACTOR ---
# def online_search_direct(query):
#     try:
#         # Hum query ko bahut specific rakhenge taaki DuckDuckGo seedha answer de
#         search_query = f"IPL 2026 {query} live score teams runs overs"
        
#         with DDGS() as ddgs:
#             # Hum 8 results scan karenge taaki "Protected" data ko skip karke Asli Score dhoondein
#             results = list(ddgs.text(search_query, max_results=8))
            
#             if results:
#                 for r in results:
#                     body = r.get('body', '').lower()
#                     title = r.get('title', '').lower()
#                     combined = title + " " + body
                    
#                     # LOGIC: Check if it contains both a Score (/) and Team Names/VS
#                     if ("/" in combined or "overs" in combined) and ("vs" in combined or "beat" in combined or "won" in combined):
                        
#                         # CLEANING: Faltu ki website descriptions hatana
#                         garbage = ["view all", "cricbuzz", "ball-by-ball", "full coverage", "stay updated", "summary", "1 hour ago", "minutes ago", "subscription"]
#                         for word in garbage:
#                             combined = re.sub(word, '', combined, flags=re.IGNORECASE)
                        
#                         # Clean links
#                         clean_ans = re.sub(r'http\S+', '', combined)
                        
#                         # Sirf pehle 22 words (Short & Clear Answer)
#                         final_msg = " ".join(clean_ans.split()[:22])
#                         return final_msg.strip()

#             return "Sir, match is live but scoreboard is currently hidden by the server. Trying again..."
#     except Exception as e:
#         return "Sir, connection link broken. Please check if firewall is blocking Jarvis."

# # -------- JARVIS VOICE LOOP --------
# def jarvis_loop():
#     pythoncom.CoInitialize()
#     speaker = win32com.client.Dispatch("SAPI.SpVoice")

#     def speak(text):
#         print("Jarvis:", text)
#         speaker.Speak(text)

#     recognizer = sr.Recognizer()
#     recognizer.dynamic_energy_threshold = True 
    
#     speak("Jarvis is online. 100 percent working live link established.")

#     while True:
#         try:
#             with sr.Microphone() as source:
#                 print("Listening...")
#                 recognizer.adjust_for_ambient_noise(source, duration=0.5)
#                 audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

#             print("Recognizing...")
#             command = recognizer.recognize_google(audio, language="en-IN").lower().strip()
#             print("You said:", command)

#             if "jarvis" in command:
#                 speak("Yes sir")

#             # --- THE 100% FIXED SCORE COMMAND ---
#             elif any(word in command for word in ["score", "match kya hua", "kya score hai"]):
#                 speak("Fetching live scoreboard...")
#                 # Search directly for current score
#                 ans = online_search_direct("current match score")
#                 speak(f"Sir, {ans}")

#             # --- EXIT ---
#             elif any(word in command for word in ["exit", "stop", "bye"]):
#                 speak("Goodbye sir")
#                 os._exit(0)

#         except:
#             pass

# # Start the thread
# voice_thread = threading.Thread(target=jarvis_loop)
# voice_thread.daemon = True
# voice_thread.start()

# while True:
#     time.sleep(1)
import speech_recognition as sr
import threading
import pythoncom
import win32com.client
import os
import time
from ddgs import DDGS

# --- THE UNSTOPPABLE BATTING-FOCUSED SCORE EXTRACTOR ---
def online_search_direct(intent):
    try:
        with DDGS() as ddgs:
            # --- INTENT 1: Sirf Match ka naam pata karna ---
            if intent == "match_name":
                search_query = "IPL 2026 today match teams who is playing"
                
                # News mein 'vs' dhundho
                results = list(ddgs.news(search_query, max_results=5))
                if results:
                    for r in results:
                        title = r.get('title', '')
                        if " vs " in title.lower() or " vs. " in title.lower():
                            # Faltu news sources ko hata kar clean title dena
                            clean_title = title.split('|')[0].replace("IPL 2026:", "").strip()
                            return f"Sir, aaj ka match hai: {clean_title}"
                
                # Agar news mein na mile toh text search karein
                text_results = list(ddgs.text(search_query, max_results=3))
                if text_results:
                    for tr in text_results:
                        body = tr.get('body', '')
                        if " vs " in body.lower():
                            return "Sir, aaj khela jayega: " + " ".join(body.split()[:20])
                
                return "Sir, aaj ke match ka naam abhi server par update nahi hua hai."

            # --- INTENT 2: Live Score pata karna ---
            elif intent == "score":
                search_query = "IPL 2026 live score today match scorecard batting team overs"
                
                results = list(ddgs.news(search_query, max_results=6))
                if results:
                    for r in results:
                        title = r.get('title', '')
                        if any(x in title.lower() for x in ["/", "batting", "overs", "needs", "won by"]):
                            clean_ans = title.replace("Cricbuzz", "").replace("IPL 2026:", "").strip()
                            return clean_ans

                text_results = list(ddgs.text(search_query, max_results=3))
                if text_results:
                    for tr in text_results:
                        body = tr.get('body', '')
                        if "/" in body or "batting" in body.lower():
                            return " ".join(body.split()[:20])

                return "Sir, live update is coming in. Please ask again in a moment."

    except Exception as e:
        return "Sir, I'm unable to reach the live match server right now."

# -------- JARVIS VOICE LOOP --------
def jarvis_loop():
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    def speak(text):
        if any(x in text.lower() for x in ["/", "vs", "batting", "overs", "won"]):
            display_text = text.replace("Sir, ", "").strip()
            print("\n" + "═"*70)
            print(f"🏏  LIVE STATUS: {display_text}")
            print("═"*70 + "\n")
        else:
            print("Jarvis:", text)
        
        speaker.Speak(text)

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True 
    
    speak("Jarvis is online. Match tracking systems synchronized.")

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

            print("Recognizing...")
            command = recognizer.recognize_google(audio, language="en-IN").lower().strip()
            print(f"You said: {command}")

            if "jarvis" in command:
                speak("Yes sir")

            # --- CONDITION 1: Aaj ka match pucha ---
            elif "aaj ka match" in command or "today match" in command or "kiska match" in command:
                speak("Checking today's schedule...")
                ans = online_search_direct("match_name")
                speak(ans)

            # --- CONDITION 2: Live score pucha ---
            elif "score" in command or "batting" in command or "kya hua" in command:
                speak("Checking live score...")
                ans = online_search_direct("score")
                speak(f"Sir, {ans}")

            elif any(word in command for word in ["exit", "stop", "bye"]):
                speak("Goodbye sir, shutting down systems.")
                os._exit(0)

        except Exception:
            pass # Ignore errors like timeouts or unrecognised speech quietly

# Start the Thread
if __name__ == "__main__":
    voice_thread = threading.Thread(target=jarvis_loop)
    voice_thread.daemon = True
    voice_thread.start()

    # Main thread ko zinda rakhne ke liye loop
    while True:
        time.sleep(1)



# import speech_recognition as sr
# import threading
# import pythoncom
# import win32com.client
# import os
# import time

# # -------- ALAG FILES SE IMPORT --------
# from engine import fetch_innings_runs, get_player_stats, predict_next_score, compare_players, get_bowling_stats, predict_next_wickets
# from scraper import get_live_score, get_match_schedule, get_points_table
# from graphs import show_batting_graph, show_bowling_graph

# # -------- JARVIS VOICE LOOP --------
# def jarvis_loop():
#     pythoncom.CoInitialize()
#     speaker = win32com.client.Dispatch("SAPI.SpVoice")

#     def speak(text):
#         print("Jarvis:", text)
#         speaker.Speak(text)

#     recognizer = sr.Recognizer()
#     # Background noise ko control karne ke liye
#     recognizer.dynamic_energy_threshold = True 
    
#     speak("Jarvis is online. Tell me sir.")

#     while True:
#         try:
#             with sr.Microphone() as source:
#                 print("Listening...")
#                 recognizer.adjust_for_ambient_noise(source, duration=0.5)
#                 audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

#             print("Recognizing...")
#             # Hindi-English dono mix commands catch karne ke liye
#             command = recognizer.recognize_google(audio, language="en-IN").lower().strip()
#             print("You said:", command)

#             # 1. Wake word
#             if "jarvis" in command:
#                 speak("Yes sir, I am listening")

#             # 2. Live Score (Keywords badha diye hain)
#             elif any(word in command for word in ["live score", "current score", "score", "match kya hua", "score kya hai"]):
#                 speak("Fetching live score sir please wait")
#                 speak(get_live_score())

#             # 3. Match Schedule (Fixed: Ab ye "schedule" pakka catch karega)
#             # 3. Match Schedule (Fixed for "Call" vs "Kal" issue)
#             elif any(word in command for word in ["match", "schedule", "fixtures", "kiska match hai", "today", "tomorrow", "yesterday"]):
#                 day = "today" # Default
                
#                 # Yesterday logic (Handling "Call" instead of "Kal")
#                 if any(word in command for word in ["yesterday", "beeta hua", "last match", "call"]):
#                     day = "yesterday"
                
#                 # Tomorrow logic (Handling "Kal" or "Tomorrow")
#                 elif any(word in command for word in ["tomorrow", "kal", "next match"]):
#                     day = "tomorrow"
                
#                 # Today logic
#                 elif "today" in command or "aaj" in command:
#                     day = "today"

#                 # Action: Ab Jarvis 100% bolega
#                 speak(f"Checking {day} match schedule for you sir...")
                
#                 try:
#                     from scraper import get_match_schedule
#                     result = get_match_schedule(day) 
#                     speak(result) 
#                 except Exception as e:
#                     print(f"Error: {e}")
#                     speak("Sir, schedule check karne mein problem ho rahi hai.")

#             # 4. Points Table
#             elif any(word in command for word in ["points table", "standings", "ranking", "kaun upar hai"]):
#                 speak("Fetching points table sir please wait")
#                 speak(get_points_table())

#             # 5. Player Comparison
#             elif any(word in command for word in ["compare", "vs", "versus", "better player", "mukabla"]):
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
#                     speak("Please say two player names with 'and' in between sir")

#             # 6. ML Prediction
#             elif any(word in command for word in ["predict", "prediction", "next score", "wickets", "kitne wicket lega"]):
#                 speak("Which player sir?")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
                
#                 speak("Batting prediction chahiye ya bowling sir?")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 pred_type = recognizer.recognize_google(audio, language="en-IN").lower().strip()
                
#                 if "bowling" in pred_type or "wicket" in pred_type:
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

#             # 7. Player Stats
#             elif any(word in command for word in ["player stats", "statistics", "record", "performance", "kaisa khelta hai"]):
#                 speak("Which player sir")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
#                 stats = get_player_stats(player)
#                 if stats:
#                     last5, avg, highest = stats
#                     speak(f"{player} last five innings runs {last5}")
#                     speak(f"Average run {round(avg, 2)}")
#                     speak(f"Highest run {highest}")
#                 else:
#                     speak("Player data not found")

#             # 8. Bowling Stats
#             elif any(word in command for word in ["bowling stats", "bowling record", "wickets list", "kitne wicket liye"]):
#                 speak("Which player sir")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
#                 stats = get_bowling_stats(player)
#                 if stats:
#                     speak(f"{player} bowling stats sir")
#                     speak(f"Total wickets {stats['total_wickets']}, Economy rate {stats['economy']}")
#                     speak(f"Last five innings wickets are {stats['wickets_list']}")
#                 else:
#                     speak(f"{player} ka bowling data nahi mila sir")

#             # 9. Graphs (Batting & Bowling)
#             elif "graph" in command or "chart" in command:
#                 speak("Which player sir?")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
                
#                 if "bat" in command or "run" in command:
#                     speak(f"Showing batting graph for {player}")
#                     show_batting_graph(player)
#                 else:
#                     speak(f"Showing bowling graph for {player}")
#                     show_bowling_graph(player)

#             # 10. Exit
#             elif any(word in command for word in ["exit", "stop", "bye", "goodbye", "chalo bye"]):
#                 speak("Goodbye sir, have a nice day")
#                 os._exit(0)

#         except Exception as e:
#             print("Listening...") # Loop chalta rahega

# # -------- START VOICE THREAD --------
# voice_thread = threading.Thread(target=jarvis_loop)
# voice_thread.daemon = True
# voice_thread.start()

# while True:
#     time.sleep(1)