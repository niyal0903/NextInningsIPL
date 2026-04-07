"""
JARVIS - INCREDIBLE IPL 2026 AGENT v11.0
===============================================
Features: ML Prediction | Local LLM Expert | Real-time Analysis
"""
import re, time, os, threading, queue
import numpy as np
from sklearn.linear_model import LinearRegression # ML Power
import ollama # LLM Power (Local AI)
from ddgs import DDGS
# ... (Purane imports jaise matplotlib, win32com wagera pehle jaise hi rahenge)

# ══════════════════════════════════════════════════════════════════════
#  NEW: MACHINE LEARNING ENGINE (Predicts Future Scores)
# ══════════════════════════════════════════════════════════════════════
def ml_predict_performance(scores):
    """
    Agar Kohli ne last 5 matches mein [20, 45, 10, 80, 30] banaye hain, 
    toh ML trend line check karke agle match ka score predict karega.
    """
    if len(scores) < 3: return "Inconsistent data for ML"
    
    X = np.array(range(len(scores))).reshape(-1, 1)
    y = np.array(scores)
    
    model = LinearRegression()
    model.fit(X, y)
    
    prediction = model.predict(np.array([[len(scores)]]))[0]
    return int(max(0, prediction))

# ══════════════════════════════════════════════════════════════════════
#  NEW: LLM EXPERT BRAIN (Ollama Integration)
# ══════════════════════════════════════════════════════════════════════
def get_llm_expert_opinion(context_data):
    """
    Jarvis ab sirf stats nahi bolega, ek real agent ki tarah raye (opinion) dega.
    """
    try:
        prompt = f"Act as an elite IPL 2026 Cricket Agent. Analyze this data and give a 2-line strategic insight: {context_data}"
        # Make sure Ollama is running locally with 'mistral' or 'llama3'
        response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except:
        return "Sir, my neural core is offline, but the stats suggest a high-impact performance."

# ══════════════════════════════════════════════════════════════════════
#  UPGRADED: INCREDIBLE PLAYER ANALYSIS
# ══════════════════════════════════════════════════════════════════════
def get_incredible_player_report(player_name):
    # 1. Fresh Data Fetching (Purana scraper logic)
    print(f"Sir, scanning IPL 2026 database for {player_name}...")
    res = search(f"{player_name} IPL 2026 recent scores and form", mode="text", n=5)
    txt = " ".join([r.get("body","") for r in res])
    
    # Extract numbers for ML
    recent_scores = [int(s) for s in re.findall(r'\b(\d{1,3})\b', txt) if int(s) < 180][:5]
    
    # 2. ML Prediction
    predicted_score = ml_predict_performance(recent_scores) if recent_scores else "N/A"
    
    # 3. LLM Insight
    context = f"Player {player_name} recent scores {recent_scores}. Predicted next score {predicted_score}."
    expert_talk = get_llm_expert_opinion(context)
    
    # 4. Final Incredible Response
    report = (
        f"--- INCREDIBLE AGENT REPORT ---\n"
        f"PLAYER: {player_name}\n"
        f"RECENT FORM: {recent_scores}\n"
        f"ML PROJECTION: Expecting around {predicted_score} runs in the next outing.\n"
        f"EXPERT BRIEF: {expert_talk}\n"
    )
    return report

# ══════════════════════════════════════════════════════════════════════
#  UPGRADED: MAIN CONTROL LOOP
# ══════════════════════════════════════════════════════════════════════
def jarvis_main():
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    def speak(text):
        print(f"\n[JARVIS]: {text}")
        speaker.Speak(text)

    speak("Incredible Agent v11.0 is active. ML and LLM cores initialized for IPL 2026.")
    
    while True:
        query = input("\n[YOU]: ").lower()
        
        if "exit" in query: break
        
        if "analyze" in query:
            player = query.replace("analyze", "").strip()
            report = get_incredible_player_report(player)
            speak(report)
            
        elif "score" in query:
            # Purana v10 live scorecard logic yahan call karein
            speak("Fetching live feeds, Sir...")
            # ... call get_live_scorecard() ...

if __name__ == "__main__":
    jarvis_main()