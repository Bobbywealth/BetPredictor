import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.title("🏆 SportsBet Pro")
st.write("Welcome to SportsBet Pro - Real Sports Data & AI Analysis")

# Test basic functionality
st.header("📊 System Status")

# Simple API test
try:
    st.write("Testing ESPN API...")
    response = requests.get("https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard", timeout=10)
    if response.status_code == 200:
        data = response.json()
        events = data.get('events', [])
        st.success(f"✅ ESPN API Working - Found {len(events)} NFL games")
        
        if events:
            st.subheader("🏈 Current NFL Games")
            for event in events[:3]:
                st.write(f"• {event.get('name', 'Unknown game')}")
    else:
        st.error("❌ ESPN API Error")
except Exception as e:
    st.error(f"❌ ESPN API Error: {str(e)}")

# Test Odds API
try:
    st.write("Testing Odds API...")
    odds_url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
    params = {
        'apiKey': 'ffb7d086c82de331b0191d11a3386eac',
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }
    response = requests.get(odds_url, params=params, timeout=10)
    if response.status_code == 200:
        games = response.json()
        st.success(f"✅ Odds API Working - Found {len(games)} games with odds")
        
        if games:
            st.subheader("💰 Sample Betting Odds")
            for game in games[:3]:
                home = game.get('home_team', 'Unknown')
                away = game.get('away_team', 'Unknown')
                st.write(f"• {away} @ {home}")
    else:
        st.error(f"❌ Odds API Error: {response.status_code}")
except Exception as e:
    st.error(f"❌ Odds API Error: {str(e)}")

# Show current time to verify app is running
st.write(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.success("🚀 Basic app is working! Full features coming soon...")

# Simple data display
if st.button("Show Sample Data"):
    df = pd.DataFrame({
        'Team': ['Chiefs', 'Bills', 'Cowboys', '49ers'],
        'Wins': [12, 11, 10, 9],
        'Losses': [4, 5, 6, 7]
    })
    st.dataframe(df)