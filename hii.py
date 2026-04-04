from scraper import get_match_schedule
print(get_match_schedule())

"""
JARVIS IPL LIVE SCORE - DDGS VERSION (100% SURE & OPTIMIZED)
============================================================
"""

import re
import time
import os
import threading
import pythoncom
import win32com.client
import speech_recognition as sr
from ddgs import DDGS

# ══════════════════════════════════════════════════════════
#  IPL TEAM NAMES
# ══════════════════════════════════════════════════════════
IPL_TEAMS = [
    "Mumbai Indians", "Chennai Super Kings",
    "Royal Challengers Bengaluru", "Royal Challengers Bangalore",
    "Kolkata Knight Riders", "Delhi Capitals",
    "Punjab Kings", "Rajasthan Royals",
    "Sunrisers Hyderabad", "Lucknow Super Giants", "Gujarat Titans",
    "MI", "CSK", "RCB", "KKR", "DC", "PBKS", "RR", "SRH", "LSG", "GT"
]

# ══════════════════════════════════════════════════════════
#  HELPER: MATCH NAME EXTRACTOR
# ══════════════════════════════════════════════════════════
def extract_match_name(text):
    pattern = re.compile(
        r'([A-Z][a-zA-Z\s]{2,30}?)\s+(?:vs?\.?)\s+([A-Z][a-zA-Z\s]{2,30}?)(?=\s*[,|\-|:|\.|\n|$])',
        re.IGNORECASE
    )
    matches = pattern.findall(text)
    for t1, t2 in matches:
        t1, t2 = t1.strip(), t2.strip()
        for team in IPL_TEAMS:
            if team.lower() in t1.lower() or team.lower() in t2.lower():
                t1 = re.sub(r'\b(ipl|2026|match|today|live|score|cricket)\b', '', t1, flags=re.IGNORECASE).strip()
                t2 = re.sub(r'\b(ipl|2026|match|today|live|score|cricket)\b', '', t2, flags=re.IGNORECASE).strip()
                if t1 and t2:
                    return f"{t1} vs {t2}"
    return None

# ══════════════════════════════════════════════════════════
#  HELPER: SCORE LINE EXTRACTOR
# ══════════════════════════════════════════════════════════
def extract_score_line(text):
    score_patterns = [
        r'(\w[\w\s]*?)\s+(\d{1,3}/\d{1,2})\s*(?:in|after)?\s*([\d.]+)\s*overs?',
        r'need\s+\d+\s+runs?\s+(?:in|from)\s+\d+\s+(?:balls?|overs?)',
        r'\w[\w\s]*?\s+won\s+by\s+\d+\s+(?:runs?|wickets?)',
        r'target[:\s]+\d+',
        r'\d{1,3}/\d{1,2}\s*(?:all\s*out)?',
    ]
    
    sentences = re.split(r'[.!\n]', text)
    
    for sent in sentences:
        sent = sent.strip()
        for pat in score_patterns:
            if re.search(pat, sent, re.IGNORECASE):
                clean = re.sub(r'(Cricbuzz|Cricinfo|ESPNcricinfo|NDTV|Times of India|Hindustan Times|IPL 2026:?)', '', sent, flags=re.IGNORECASE)
                clean = re.sub(r'\s+', ' ', clean).strip()
                # Ensure it actually looks like a score and isn't just a date like 2026
                if len(clean) > 8 and any(char.isdigit() for char in clean):
                    return clean[:150]
    return None

# ══════════════════════════════════════════════════════════
#  MAIN SEARCH FUNCTION (OPTIMIZED FOR 100% CURRENT DATA)
# ══════════════════════════════════════════════════════════
def search_ipl(intent):
    try:
        with DDGS() as ddgs:

            # ── MATCH NAME ──────────────────────────────
            if intent == "match_name":
                queries = ["IPL 2026 today match teams playing schedule"]

                for q in queries:
                    try:
                        # 'timelimit="d"' ensures we only get today's data. 'region="in-en"' focuses on Indian sources.
                        news = list(ddgs.news(q, region="in-en", timelimit="d", max_results=10))
                        for r in news:
                            combined = r.get('title', '') + " " + r.get('body', '')
                            found = extract_match_name(combined)
                            if found:
                                return ("match", found)
                    except Exception:
                        pass

                return ("error", "Aaj ke match ki jaankari abhi server par process ho rahi hai.")

            # ── LIVE SCORE ──────────────────────────────
            elif intent == "score":
                queries = [
                    "IPL 2026 live cricket score today match current innings",
                    "IPL 2026 live scorecard batting today -highlights"
                ]

                for q in queries:
                    try:
                        # Strict filtering for current Indian news
                        news = list(ddgs.news(q, region="in-en", timelimit="d", max_results=8))
                        for r in news:
                            title = r.get('title', '')
                            body  = r.get('body', '')
                            
                            found = extract_score_line(title)
                            if found:
                                return ("score", found)
                            
                            found = extract_score_line(body)
                            if found:
                                return ("score", found)

                            if re.search(r'\d+/\d+', title) and "vs" in title.lower():
                                clean = re.sub(r'(Cricbuzz|Cricinfo|IPL 2026[:\-]?)', '', title, flags=re.IGNORECASE).strip()
                                return ("score", clean)

                    except Exception:
                        pass

                    try:
                        # Text fallback with daily limit
                        texts = list(ddgs.text(q, region="in-en", timelimit="d", max_results=5))
                        for r in texts:
                            body = r.get('body', '')
                            found = extract_score_line(body)
                            if found:
                                return ("score", found)
                    except Exception:
                        pass

                return ("error", "Sir, live match update abhi aa raha hai. Thodi der mein phir puchein.")

    except Exception as e:
        print(f"[Search Error] {e}")
        return ("error", "Network connection mein problem hai sir.")


# ══════════════════════════════════════════════════════════
#  JARVIS VOICE LOOP
# ══════════════════════════════════════════════════════════
def jarvis_loop():
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    def speak(text):
        if any(x in text for x in ["/", " vs ", "batting", "overs", "won", "runs", "wicket", "target", "need"]):
            print("\n" + "═" * 70)
            print(f"🏏  LIVE UPDATE: {text}")
            print("═" * 70 + "\n")
        else:
            print(f"Jarvis: {text}")
        speaker.Speak(text)

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True

    speak("Jarvis online. Real-time IPL tracking active.")

    while True:
        try:
            with sr.Microphone() as source:
                print("\n🎤 Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

            print("⏳ Recognizing...")
            command = recognizer.recognize_google(audio, language="en-IN").lower().strip()
            print(f"You said: '{command}'")

            if command.strip() == "jarvis":
                speak("Always ready, sir!")

            elif any(w in command for w in [
                "aaj ka match", "today match", "kiska match",
                "kon khel raha", "kaun khel raha", "which match",
                "match kaun", "match kon", "today ipl", "ipl today"
            ]):
                speak("Checking today's fixtures...")
                kind, ans = search_ipl("match_name")
                if kind == "match":
                    speak(f"Sir, aaj ka match hai: {ans}")
                else:
                    speak(f"Sir, {ans}")

            elif any(w in command for w in [
                "score", "batting", "kya hua", "kitne run",
                "live score", "current score", "score kya hai",
                "score batao", "match score", "kitne wicket"
            ]):
                speak("Fetching live telemetry...")
                kind, ans = search_ipl("score")
                speak(f"Sir, {ans}")

            elif any(w in command for w in ["exit", "stop", "bye", "band karo", "shut down", "close"]):
                speak("Systems shutting down. Goodbye sir.")
                os._exit(0)

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as ex:
            print(f"[Core Error] {ex}")
            time.sleep(1)

if __name__ == "__main__":
    print("=" * 65)
    print("  JARVIS IPL - STARTUP DIAGNOSTICS")
    print("=" * 65)

    print("🔍 Testing match search...")
    k, v = search_ipl("match_name")
    print(f"   Result [{k}]: {v}")

    print("🔍 Testing score search...")
    k, v = search_ipl("score")
    print(f"   Result [{k}]: {v}")

    print("=" * 65)
    print("✅ Initializing Audio Subsystems...\n")

    voice_thread = threading.Thread(target=jarvis_loop)
    voice_thread.daemon = True
    voice_thread.start()

    while True:
        time.sleep(1)