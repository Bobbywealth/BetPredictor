import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, date, timedelta
import json

# Simple working version for deployment
try:
    st.set_page_config(
        page_title="SportsBet Pro - AI Sports Analysis", 
        page_icon="🏆",
        layout="wide"
    )
except Exception as e:
    st.error(f"Config error: {e}")
    # Continue anyway

st.title("🏆 SportsBet Pro - AI Sports Analysis")
st.markdown("### Real-time sports data with AI-powered predictions")

# Test API connections
def test_apis():
    """Test all API connections"""
    st.subheader("🔗 API Status")
    
    # Test Odds API
    try:
        odds_url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
        params = {
            'apiKey': 'ffb7d086c82de331b0191d11a3386eac',
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        response = requests.get(odds_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ The Odds API: Found {len(data)} NFL games with live odds")
        else:
            st.error(f"❌ Odds API Error: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Odds API Error: {str(e)}")
    
    # Test ESPN API
    try:
        espn_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        response = requests.get(espn_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            st.success(f"✅ ESPN API: Found {len(events)} NFL events")
        else:
            st.error(f"❌ ESPN API Error: {response.status_code}")
    except Exception as e:
        st.error(f"❌ ESPN API Error: {str(e)}")
    
    # Test AI APIs
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if openai_key:
        st.success("✅ OpenAI API Key: Configured")
    else:
        st.error("❌ OpenAI API Key: Missing")
    
    if gemini_key:
        st.success("✅ Gemini API Key: Configured")
    else:
        st.error("❌ Gemini API Key: Missing")

def show_live_odds():
    """Show live betting odds"""
    st.subheader("💰 Live Betting Odds")
    
    try:
        odds_url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
        params = {
            'apiKey': 'ffb7d086c82de331b0191d11a3386eac',
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        
        with st.spinner("Loading live odds..."):
            response = requests.get(odds_url, params=params, timeout=15)
            
        if response.status_code == 200:
            games = response.json()
            
            if games:
                odds_data = []
                for game in games[:10]:  # Show first 10 games
                    home_team = game.get('home_team', 'Unknown')
                    away_team = game.get('away_team', 'Unknown')
                    commence_time = game.get('commence_time', '')
                    
                    # Parse time
                    game_time = 'TBD'
                    if commence_time:
                        try:
                            dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                            game_time = dt.strftime('%m/%d %I:%M %p ET')
                        except:
                            pass
                    
                    # Get best odds
                    bookmakers = game.get('bookmakers', [])
                    home_odds = away_odds = 'N/A'
                    
                    if bookmakers:
                        for bookmaker in bookmakers:
                            markets = bookmaker.get('markets', [])
                            for market in markets:
                                if market.get('key') == 'h2h':
                                    outcomes = market.get('outcomes', [])
                                    for outcome in outcomes:
                                        if outcome.get('name') == home_team:
                                            home_odds = outcome.get('price', 'N/A')
                                        elif outcome.get('name') == away_team:
                                            away_odds = outcome.get('price', 'N/A')
                                    break
                            if home_odds != 'N/A':
                                break
                    
                    odds_data.append({
                        'Game': f"{away_team} @ {home_team}",
                        'Time': game_time,
                        'Away Odds': away_odds,
                        'Home Odds': home_odds
                    })
                
                if odds_data:
                    df = pd.DataFrame(odds_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No odds data available")
            else:
                st.info("No games found")
        else:
            st.error(f"Failed to load odds: {response.status_code}")
            
    except Exception as e:
        st.error(f"Error loading odds: {str(e)}")

def show_live_games():
    """Show live games from ESPN"""
    st.subheader("🏈 Live NFL Games")
    
    try:
        espn_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        
        with st.spinner("Loading live games..."):
            response = requests.get(espn_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            
            if events:
                games_data = []
                for event in events:
                    name = event.get('name', 'Unknown')
                    status = event.get('status', {}).get('type', {}).get('description', 'Unknown')
                    date_str = event.get('date', '')
                    
                    # Parse date
                    game_date = 'TBD'
                    if date_str:
                        try:
                            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            game_date = dt.strftime('%m/%d %I:%M %p ET')
                        except:
                            pass
                    
                    # Get scores
                    competitions = event.get('competitions', [])
                    score_info = 'TBD'
                    if competitions:
                        competitors = competitions[0].get('competitors', [])
                        if len(competitors) >= 2:
                            team1_score = competitors[0].get('score', '0')
                            team2_score = competitors[1].get('score', '0')
                            if team1_score != '0' or team2_score != '0':
                                score_info = f"{team1_score} - {team2_score}"
                    
                    games_data.append({
                        'Game': name,
                        'Time': game_date,
                        'Status': status,
                        'Score': score_info
                    })
                
                if games_data:
                    df = pd.DataFrame(games_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No game data available")
            else:
                st.info("No games found")
        else:
            st.error(f"Failed to load games: {response.status_code}")
            
    except Exception as e:
        st.error(f"Error loading games: {str(e)}")

# Main app layout
col1, col2 = st.columns(2)

with col1:
    show_live_games()

with col2:
    show_live_odds()

st.markdown("---")
test_apis()

st.markdown("---")
st.info("🚀 **Full AI Analysis Coming Soon!** This simplified version tests all APIs. The complete app with winning picks will load once deployment is stable.")