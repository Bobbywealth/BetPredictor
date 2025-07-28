import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.user_management import UserManager
from utils.game_analyzer import GameAnalyzer
from utils.live_games import LiveGamesManager

def main():
    """Clean, organized user dashboard"""
    user_manager = st.session_state.user_manager
    
    # Check authentication
    if not user_manager.is_authenticated():
        st.error("Please login to access your dashboard")
        st.stop()
    
    # Clean header with navigation
    col1, col2, col3 = st.columns([2, 3, 2])
    with col1:
        if st.button("← Back to Home", key="back_home"):
            st.switch_page("app.py")
    with col2:
        st.markdown("<h2 style='text-align: center;'>📊 Sports Dashboard</h2>", unsafe_allow_html=True)
    with col3:
        user_info = user_manager.get_user_info()
        st.markdown(f"<div style='text-align: right; padding-top: 1rem;'>{user_info['role'].title()}</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Organized dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Today's Games", "📈 My Predictions", "📊 Analytics", "🏆 Performance"])
    
    with tab1:
        show_todays_games()
    
    with tab2:
        show_my_predictions()
    
    with tab3:
        show_analytics()
    
    with tab4:
        show_performance()

def show_todays_games():
    """Display today's games with predictions"""
    st.markdown("### 🎯 Today's Games & Predictions")
    
    # Date selector
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_date = st.date_input("Select Date", value=datetime.now().date())
    
    # Get live games
    with st.spinner("Loading live games..."):
        live_games_manager = st.session_state.get('live_games_manager')
        if not live_games_manager:
            live_games_manager = LiveGamesManager()
            st.session_state.live_games_manager = live_games_manager
        
        games_df = live_games_manager.get_upcoming_games_all_sports()
        
        if isinstance(games_df, pd.DataFrame) and len(games_df) > 0:
            st.success(f"Found {len(games_df)} live games")
            
            # Display games in organized cards
            for idx, game in games_df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 2])
                    
                    with col1:
                        # Game info
                        away_team = game.get('away_team', {})
                        home_team = game.get('home_team', {})
                        
                        if isinstance(away_team, dict) and isinstance(home_team, dict):
                            st.markdown(f"**{away_team.get('name', 'TBD')} @ {home_team.get('name', 'TBD')}**")
                            st.caption(f"{game.get('league', 'Unknown')} | {game.get('date', 'TBD')}")
                        else:
                            st.markdown(f"**{game.get('game_name', 'Unknown Game')}**")
                            st.caption(f"{game.get('league', 'Unknown')} | {game.get('date', 'TBD')}")
                    
                    with col2:
                        # Score or VS
                        if isinstance(away_team, dict) and isinstance(home_team, dict):
                            away_score = away_team.get('score', 0)
                            home_score = home_team.get('score', 0)
                            
                            try:
                                away_score = int(away_score) if away_score else 0
                                home_score = int(home_score) if home_score else 0
                                
                                if away_score > 0 or home_score > 0:
                                    st.markdown(f"**{away_score} - {home_score}**")
                                else:
                                    st.markdown("**vs**")
                            except (ValueError, TypeError):
                                st.markdown("**vs**")
                        else:
                            st.markdown("**vs**")
                    
                    with col3:
                        # Prediction button
                        if st.button(f"Get Prediction", key=f"pred_{idx}"):
                            show_game_prediction(game)
                    
                    st.divider()
        else:
            st.info("No games found for selected date. Our system fetches live data from ESPN and TheSportsDB APIs.")

def show_game_prediction(game):
    """Show AI prediction for a specific game"""
    with st.expander("🤖 AI Prediction Analysis", expanded=True):
        game_analyzer = st.session_state.get('game_analyzer')
        if not game_analyzer:
            game_analyzer = GameAnalyzer()
            st.session_state.game_analyzer = game_analyzer
        
        # Generate prediction
        prediction = game_analyzer.analyze_game(game)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Prediction:**")
            st.success(f"Winner: {prediction.get('predicted_winner', 'Unknown')}")
            st.info(f"Confidence: {prediction.get('confidence', 0):.1%}")
        
        with col2:
            st.markdown("**Key Factors:**")
            factors = prediction.get('key_factors', [])
            for factor in factors[:3]:
                st.caption(f"• {factor}")

def show_my_predictions():
    """Display user's prediction history"""
    st.markdown("### 📈 My Prediction History")
    
    # Sample prediction history
    predictions_data = {
        'Date': ['2025-07-28', '2025-07-27', '2025-07-26'],
        'Game': ['Lakers vs Warriors', 'Yankees vs Red Sox', 'Liverpool vs Arsenal'],
        'Prediction': ['Lakers', 'Yankees', 'Liverpool'],
        'Actual': ['Lakers', 'Red Sox', 'Liverpool'],
        'Result': ['✅ Correct', '❌ Wrong', '✅ Correct'],
        'Confidence': ['85%', '72%', '91%']
    }
    
    df = pd.DataFrame(predictions_data)
    st.dataframe(df, use_container_width=True)
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Predictions", "12")
    with col2:
        st.metric("Correct", "8", "66.7%")
    with col3:
        st.metric("Average Confidence", "79%")

def show_analytics():
    """Display analytics and insights"""
    st.markdown("### 📊 Performance Analytics")
    
    # Sample charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Prediction Accuracy Over Time**")
        # Sample data for visualization
        dates = pd.date_range(start='2025-07-01', end='2025-07-28', freq='D')
        accuracy = np.random.uniform(0.6, 0.9, len(dates))
        
        chart_data = pd.DataFrame({
            'Date': dates,
            'Accuracy': accuracy
        })
        st.line_chart(chart_data.set_index('Date'))
    
    with col2:
        st.markdown("**Sports Distribution**")
        sports_data = {
            'Basketball': 5,
            'Baseball': 4,
            'Soccer': 3
        }
        st.bar_chart(sports_data)

def show_performance():
    """Display performance metrics"""
    st.markdown("### 🏆 Performance Summary")
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Win Rate",
            value="67%",
            delta="5%"
        )
    
    with col2:
        st.metric(
            label="Avg Confidence",
            value="79%",
            delta="2%"
        )
    
    with col3:
        st.metric(
            label="Best Streak",
            value="7",
            delta="2"
        )
    
    with col4:
        st.metric(
            label="Total Profit",
            value="$240",
            delta="$50"
        )
    
    st.markdown("---")
    
    # Recent performance
    st.markdown("**Recent Performance (Last 7 Days)**")
    performance_data = {
        'Date': pd.date_range(start='2025-07-22', end='2025-07-28', freq='D'),
        'Predictions': [2, 1, 3, 0, 2, 1, 3],
        'Correct': [2, 0, 2, 0, 1, 1, 2],
        'Profit': [25, -10, 15, 0, -5, 20, 30]
    }
    
    perf_df = pd.DataFrame(performance_data)
    st.dataframe(perf_df, use_container_width=True)

if __name__ == "__main__":
    main()