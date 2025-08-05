import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import os
import json

st.set_page_config(
    page_title="SportsBet Pro - AI Sports Analysis",
    page_icon="🏆", 
    layout="wide"
)

# Navigation
tab1, tab2, tab3 = st.tabs(["🏠 Home", "🏆 Winning Picks", "📊 Live Data"])

with tab1:
    st.title("🏆 SportsBet Pro")
    st.write("Welcome to SportsBet Pro - Real Sports Data & AI Analysis")

    # Test basic functionality
    st.header("📊 System Status")
    
    # Show current time
    st.write(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.success("🚀 Basic app is working! Full features available in tabs above.")

with tab2:
    st.title("🏆 High-Confidence Winning Picks") 
    st.markdown("**AI-powered sports predictions with real data**")
    
    # Date selector
    col1, col2 = st.columns([2, 2])
    with col1:
        pick_date = st.date_input(
            "📅 Pick Date",
            value=date.today(),
            min_value=date.today() - timedelta(days=1),
            max_value=date.today() + timedelta(days=7)
        )
    
    with col2:
        if st.button("🚀 Generate Picks", type="primary"):
            st.rerun()
    
    # Get games for selected date
    st.markdown("---")
    
    def get_games_for_date(target_date):
        """Get games for specific date"""
        try:
            # Get odds data
            odds_url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
            params = {
                'apiKey': 'ffb7d086c82de331b0191d11a3386eac',
                'regions': 'us',
                'markets': 'h2h',
                'oddsFormat': 'american'
            }
            
            with st.spinner("Loading games with odds..."):
                response = requests.get(odds_url, params=params, timeout=15)
            
            if response.status_code == 200:
                games = response.json()
                
                # Filter games for target date
                target_games = []
                target_str = target_date.strftime('%Y-%m-%d')
                
                for game in games:
                    commence_time = game.get('commence_time', '')
                    if commence_time:
                        try:
                            game_dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                            game_date = game_dt.strftime('%Y-%m-%d')
                            
                            if game_date == target_str:
                                target_games.append(game)
                        except:
                            continue
                
                return target_games
            else:
                st.error(f"Failed to load games: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Error loading games: {str(e)}")
            return []
    
    def generate_ai_analysis(game):
        """Generate AI analysis using OpenAI if available, otherwise mock data"""
        import random
        
        home_team = game.get('home_team', 'Unknown')
        away_team = game.get('away_team', 'Unknown')
        
        # Try real OpenAI analysis first
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                
                prompt = f"""Analyze this NFL game: {away_team} @ {home_team}
                
                Provide a JSON response with:
                - predicted_winner: team name
                - confidence: 0.0 to 1.0
                - key_factors: array of 3 key analysis points
                - recommendation: STRONG_BET, MODERATE_BET, or LEAN
                
                Focus on team performance, injuries, weather, and matchups."""
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert NFL analyst. Provide concise, data-driven analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=300
                )
                
                if response.choices[0].message.content:
                    ai_result = json.loads(response.choices[0].message.content)
                    
                    # Format the response
                    analysis = {
                        'predicted_winner': ai_result.get('predicted_winner', home_team),
                        'confidence': float(ai_result.get('confidence', 0.7)),
                        'key_factors': ai_result.get('key_factors', ['AI analysis completed']),
                        'recommendation': ai_result.get('recommendation', 'MODERATE_BET'),
                        'edge_score': float(ai_result.get('confidence', 0.7)) * 0.8,
                        'ai_consensus': '🤖 Real ChatGPT Analysis'
                    }
                    
                    return analysis
                    
            except Exception as e:
                st.warning(f"OpenAI API error: {str(e)[:100]}... Using demo mode.")
        
        # Fallback to mock analysis
        confidence = random.uniform(0.6, 0.95)
        predicted_winner = random.choice([home_team, away_team])
        
        factors = [
            f"{predicted_winner} has strong home field advantage",
            "Recent head-to-head matchups favor this pick",
            "Key player matchups look favorable", 
            "Weather conditions optimal for this style",
            "Injury reports favor the predicted winner"
        ]
        
        analysis = {
            'predicted_winner': predicted_winner,
            'confidence': confidence,
            'key_factors': random.sample(factors, 3),
            'recommendation': 'STRONG_BET' if confidence > 0.8 else 'MODERATE_BET' if confidence > 0.7 else 'LEAN',
            'edge_score': confidence * 0.8,
            'ai_consensus': '🎭 Demo Mode (Add API keys for real AI)'
        }
        
        return analysis
    
    # Load and display games
    games = get_games_for_date(pick_date)
    
    if games:
        st.success(f"🎯 Found {len(games)} games for {pick_date.strftime('%B %d, %Y')}")
        
        # Generate picks for each game
        for i, game in enumerate(games[:5], 1):  # Limit to 5 games
            home_team = game.get('home_team', 'Unknown')
            away_team = game.get('away_team', 'Unknown')
            commence_time = game.get('commence_time', '')
            
            # Parse game time
            game_time = 'TBD'
            if commence_time:
                try:
                    dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                    game_time = dt.strftime('%I:%M %p ET')
                except:
                    pass
            
            # Get AI analysis
            analysis = generate_ai_analysis(game)
            
            # Display pick
            with st.container():
                col1, col2 = st.columns([1, 11])
                
                with col1:
                    if i == 1:
                        st.markdown("# 🥇")
                    elif i == 2:
                        st.markdown("# 🥈") 
                    elif i == 3:
                        st.markdown("# 🥉")
                    else:
                        st.markdown(f"## #{i}")
                
                with col2:
                    st.markdown(f"### {away_team} @ {home_team}")
                    
                    col2a, col2b, col2c = st.columns(3)
                    with col2a:
                        st.markdown(f"🏈 **NFL**")
                        st.markdown(f"🕐 {game_time}")
                    
                    with col2b:
                        st.markdown(f"🎯 **Pick: {analysis['predicted_winner']}**")
                        confidence = analysis['confidence']
                        color = '#00C851' if confidence > 0.8 else '#ffbb33' if confidence > 0.7 else '#ff4444'
                        st.markdown(f"📈 <span style='color:{color}; font-weight:bold'>Confidence: {confidence:.1%}</span>", unsafe_allow_html=True)
                    
                    with col2c:
                        st.markdown(f"💪 **{analysis['recommendation']}**")
                        st.markdown(f"⚡ Edge Score: **{analysis['edge_score']:.2f}**")
                    
                    # AI Analysis
                    st.info(f"🤖 {analysis['ai_consensus']}")
                    
                    # Key factors
                    st.markdown("**Key Analysis Points:**")
                    for factor in analysis['key_factors']:
                        st.markdown(f"• {factor}")
                
                st.markdown("---")
    
    else:
        st.info(f"No NFL games found for {pick_date.strftime('%B %d, %Y')}. Try selecting a different date!")
        
        # Show available dates
        st.markdown("### 📅 Games Available Soon:")
        
        # Check next few days
        for days_ahead in range(1, 8):
            check_date = date.today() + timedelta(days=days_ahead)
            check_games = get_games_for_date(check_date)
            if check_games:
                st.write(f"• **{check_date.strftime('%B %d')}**: {len(check_games)} games available")

with tab3:
    st.title("📊 Live Sports Data")
    
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
                for event in events[:5]:
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
                for game in games[:5]:
                    home = game.get('home_team', 'Unknown')
                    away = game.get('away_team', 'Unknown')
                    commence_time = game.get('commence_time', '')
                    
                    # Parse time
                    game_time = 'TBD'
                    if commence_time:
                        try:
                            dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                            game_time = dt.strftime('%m/%d %I:%M %p ET')
                        except:
                            pass
                    
                    st.write(f"• {away} @ {home} - {game_time}")
        else:
            st.error(f"❌ Odds API Error: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Odds API Error: {str(e)}")

    # Show current time to verify app is running
    st.write(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")