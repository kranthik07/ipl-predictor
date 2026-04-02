import requests
import schedule
import time
import os
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

# ==============================
# 1. CONFIGURATION
# ==============================
BOT_TOKEN = os.getenv('BOT_TOKEN', '8719219910:AAGH7seN0UXq5zjhlAx4X0GM5owbozGRVcs')
CHAT_ID = os.getenv('CHAT_ID', '836315825')

TEAM_MAP = {
    "mumbai indians": "mi",
    "chennai super kings": "csk",
    "royal challengers bengaluru": "rcb",
    "sunrisers hyderabad": "srh",
    "kolkata knight riders": "kkr",
    "delhi capitals": "dc",
    "rajasthan royals": "rr",
    "punjab kings": "pbks",
    "gujarat titans": "gt",
    "lucknow super giants": "lsg"
}

# ==============================
# 2. TELEGRAM FUNCTION
# ==============================
def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing!")
        return

    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}

    try:
        response = requests.post(url, data=payload)
        print("Telegram sent:", response.status_code)
    except Exception as e:
        print(f'Error sending to Telegram: {e}')

# ==============================
# 3. LOAD MODEL
# ==============================
try:
    model = joblib.load('predictor_model.pkl')
    le = joblib.load('team_encoder.pkl')
    print('Model and Encoder loaded successfully.')
except Exception as e:
    print(f'Error loading model files: {e}')
    model = None
    le = None

# ==============================
# 4. PREDICTION FUNCTION
# ==============================
def get_prediction(team1, team2):
    try:
        t1 = TEAM_MAP.get(team1.lower().strip(), team1.lower().strip())
        t2 = TEAM_MAP.get(team2.lower().strip(), team2.lower().strip())

        t1_id = le.transform([t1])[0]
        t2_id = le.transform([t2])[0]

        features = np.array([[t1_id, t2_id]])

        pred_id = model.predict(features)[0]
        winner_name = le.inverse_transform([pred_id])[0]

        prob = model.predict_proba(features)[0]
        confidence = float(max(prob))

        return winner_name.upper(), confidence

    except Exception as e:
        print("Prediction error:", e)
        return 'UNKNOWN', 0.0

# ==============================
# 5. JOB FUNCTION
# ==============================
def job():
    print(f'Executing prediction job at {datetime.now()}')

    try:
        df = pd.read_csv('ipl_2026_schedule.csv')

        # Normalize columns
        df.columns = df.columns.str.lower()

        # Convert date format safely
        df['date'] = pd.to_datetime(df['date'], format='%d-%b-%y', errors='coerce')
        df = df.dropna(subset=['date'])

        df['date'] = df['date'].dt.strftime('%Y-%m-%d')

        # Rename columns
        df.rename(columns={
            'home': 'team1',
            'away': 'team2'
        }, inplace=True)

        today = datetime.now().strftime('%Y-%m-%d')
        matches = df[df['date'] == today]

        if matches.empty:
            print(f'No matches today ({today})')
            return

        msg = f'🏏 IPL Prediction-2026\nDate: {today}\n'

        for _, row in matches.iterrows():
            team1 = row['team1']
            team2 = row['team2']

            winner, conf = get_prediction(team1, team2)

            msg += (
                f'\nMatch: {team1.upper()} vs {team2.upper()}'
                f'\nWinner: {winner}'
                f'\nConfidence: {int(conf * 100)}%\n'
            )

        send_telegram(msg)
        print('Predictions sent successfully.')

    except Exception as e:
        print(f'Job Error: {e}')

# ==============================
# 6. SCHEDULER
# ==============================
if __name__ == "__main__":
    print('Bot is starting up...')

    # Run once immediately
    job()

    # Run daily at 9 AM
    schedule.every().day.at("09:00").do(job)

    print('Scheduler active. Waiting for next run...')

    while True:
        schedule.run_pending()
        time.sleep(60)
TEAM_MAP = {
    "mumbai indians": "mi",
    "chennai super kings": "csk",
    "royal challengers bengaluru": "rcb",
    "sunrisers hyderabad": "srh",
    "kolkata knight riders": "kkr",
    "delhi capitals": "dc",
    "rajasthan royals": "rr",
    "punjab kings": "pbks",
    "gujarat titans": "gt",
    "lucknow super giants": "lsg"
}

def send_telegram(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f'Error sending to Telegram: {e}')

# 2. LOAD PRE-TRAINED MODEL
try:
    model = joblib.load('predictor_model.pkl')
    le = joblib.load('team_encoder.pkl')
    print('Model and Encoder loaded successfully.')
except Exception as e:
    print(f'Error loading model files: {e}')

def get_prediction(team1, team2):
    try:
        t1, t2 = team1.lower().strip(), team2.lower().strip()
        t1_id = le.transform([t1])[0]
        t2_id = le.transform([t2])[0]
        features = np.array([[t1_id, t2_id]])
        pred_id = model.predict(features)[0]
        winner_name = le.inverse_transform([pred_id])[0]
        prob = model.predict_proba(features)[0]
        return winner_name.upper(), max(prob)
    except:
        return 'UNKNOWN', 0.0

# 3. PREDICTION JOB
def job():
    print(f'Executing prediction job at {datetime.now()}')
    
    try:
        df = pd.read_csv('ipl_2026_schedule.csv')

        # ✅ MUST be inside try block
        df.columns = df.columns.str.lower()

        # Convert date
        df['date'] = pd.to_datetime(df['date'], format='%d-%b-%y').dt.strftime('%Y-%m-%d')

        # Rename columns
        df.rename(columns={
            'home': 'team1',
            'away': 'team2'
        }, inplace=True)

        today = datetime.now().strftime('%Y-%m-%d')
        matches = df[df['date'] == today]

        if matches.empty:
            print(f'No matches today ({today})')
            return

        msg = f'🏏 IPL Prediction-2026\nDate: {today}\n'

        for _, row in matches.iterrows():
            winner, conf = get_prediction(row['team1'], row['team2'])
            msg += f'\nMatch: {row["team1"].upper()} vs {row["team2"].upper()}\nWinner: {winner}\nConfidence: {conf:.0%}\n'

        send_telegram(msg)
        print('Predictions sent successfully.')

    except Exception as e:
        print(f'Job Error: {e}')

# 4. 24/7 SCHEDULER
if __name__ == "__main__":
    print('Bot is starting up...')
    # Run once immediately to verify
    job()
    
    # Schedule daily at 9 AM
    schedule.every().day.at("09:00").do(job)
    
    print('Scheduler active. Waiting for next run...')
    while True:
        schedule.run_pending()
        time.sleep(60)
