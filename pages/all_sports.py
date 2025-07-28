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
    """Comprehensive sports games display across all categories"""
    user_manager = st.session_state.user_manager
    
    # Check authentication
    if not user_manager.is_authenticated():
        st.error("Please login to access all sports data")
        st.stop()
    
    # Header
    col1, col2, col3 = st.columns([2, 3, 2])
    with col1:
        if st.button("← Back to Home", key="back_home"):
            st.switch_page("app.py")
    with col2:
        st.markdown("<h2 style='text-align: center;'>🏈 All Sports Categories</h2>", unsafe_allow_html=True)
    with col3:
        user_info = user_manager.get_user_info()
        st.markdown(f"<div style='text-align: right; padding-top: 1rem;'>{user_info['role'].title()}</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Sports categories tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["⚽ All Games", "🏀 Basketball", "⚾ Baseball", "🏈 Football", "⚽ Soccer", "🏒 Other Sports"])
    
    with tab1:
        show_all_games()
    
    with tab2:
        show_basketball_games()
    
    with tab3:
        show_baseball_games()
    
    with tab4:
        show_football_games()
    
    with tab5:
        show_soccer_games()
    
    with tab6:
        show_other_sports()

def show_all_games():
    """Display all games from all sports"""
    st.markdown("### 🏈 All Live Sports Games")
    
    # Date selector for filtering
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        selected_date = st.date_input("Select Date", value=datetime.now().date(), key="all_games_date")
    with col2:
        st.markdown("<div style='padding-top: 2rem;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh All Games", type="primary"):
            st.session_state.pop('live_games_manager', None)
    with col3:
        # Show selected date info
        st.markdown(f"<div style='padding-top: 2rem; text-align: right;'>**{selected_date}**</div>", unsafe_allow_html=True)
    
    with st.spinner(f"Loading all sports data for {selected_date}..."):
        live_games_manager = st.session_state.get('live_games_manager')
        if not live_games_manager:
            live_games_manager = LiveGamesManager()
            st.session_state.live_games_manager = live_games_manager
        
        all_games_df = live_games_manager.get_upcoming_games_all_sports(target_date=selected_date)
        
        if isinstance(all_games_df, pd.DataFrame) and len(all_games_df) > 0:
            # Sports summary
            sports_summary = all_games_df.groupby(['sport', 'league']).size().reset_index(name='count')
            
            st.markdown("#### 📊 Sports Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            total_games = len(all_games_df)
            total_sports = all_games_df['sport'].nunique()
            total_leagues = all_games_df['league'].nunique()
            
            with col1:
                st.metric("Total Games", total_games)
            with col2:
                st.metric("Sports Categories", total_sports)
            with col3:
                st.metric("Leagues", total_leagues)
            with col4:
                st.metric("Live Updates", "Real-time")
            
            st.divider()
            
            # Games by sport breakdown
            st.markdown("#### 🏆 Games by Sport")
            sport_counts = all_games_df['sport'].value_counts()
            
            for sport, count in sport_counts.items():
                with st.expander(f"{sport.title()} ({count} games)", expanded=True):
                    sport_games = all_games_df[all_games_df['sport'] == sport]
                    display_games_table(sport_games)
        else:
            st.info("No games currently available. Our system searches across MLB, NBA, NFL, MLS, Premier League, and other major sports.")

def show_basketball_games():
    """Display basketball games"""
    st.markdown("### 🏀 Basketball Games")
    display_sport_games('basketball', ['NBA', 'WNBA', 'College Basketball'])

def show_baseball_games():
    """Display baseball games"""
    st.markdown("### ⚾ Baseball Games")
    display_sport_games('baseball', ['MLB', 'College Baseball'])

def show_football_games():
    """Display football games"""
    st.markdown("### 🏈 Football Games")
    display_sport_games('football', ['NFL', 'College Football'])

def show_soccer_games():
    """Display soccer games"""
    st.markdown("### ⚽ Soccer Games")
    display_sport_games('soccer', ['MLS', 'Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Champions League'])

def show_other_sports():
    """Display other sports"""
    st.markdown("### 🏒 Other Sports")
    
    with st.spinner("Loading other sports..."):
        live_games_manager = st.session_state.get('live_games_manager')
        if not live_games_manager:
            live_games_manager = LiveGamesManager()
            st.session_state.live_games_manager = live_games_manager
        
        all_games_df = live_games_manager.get_upcoming_games_all_sports()
        
        if isinstance(all_games_df, pd.DataFrame) and len(all_games_df) > 0:
            # Filter for other sports (not basketball, baseball, football, soccer)
            main_sports = ['basketball', 'baseball', 'football', 'soccer']
            other_games = all_games_df[~all_games_df['sport'].isin(main_sports)]
            
            if len(other_games) > 0:
                st.success(f"Found {len(other_games)} games in other sports categories")
                display_games_table(other_games)
            else:
                st.info("No other sports games currently available")
        else:
            st.info("No games data available")

def display_sport_games(sport_filter, expected_leagues):
    """Display games for a specific sport"""
    # Date selector for sport-specific filtering
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_date = st.date_input("Select Date", value=datetime.now().date(), key=f"{sport_filter}_date")
    with col2:
        if st.button(f"🔄 Refresh {sport_filter.title()}", type="primary"):
            st.session_state.pop('live_games_manager', None)
    
    with st.spinner(f"Loading {sport_filter} games for {selected_date}..."):
        live_games_manager = st.session_state.get('live_games_manager')
        if not live_games_manager:
            live_games_manager = LiveGamesManager()
            st.session_state.live_games_manager = live_games_manager
        
        all_games_df = live_games_manager.get_upcoming_games_all_sports(
            target_date=selected_date,
            sport_filter=sport_filter
        )
        
        if isinstance(all_games_df, pd.DataFrame) and len(all_games_df) > 0:
            # All games are already filtered by sport and date
            st.success(f"Found {len(all_games_df)} {sport_filter} games for {selected_date}")
            
            # Group by league
            leagues = all_games_df['league'].unique()
            for league in leagues:
                league_games = all_games_df[all_games_df['league'] == league]
                with st.expander(f"{league} ({len(league_games)} games)", expanded=True):
                    display_games_table(league_games)
        else:
            date_msg = f" for {selected_date}" if selected_date != datetime.now().date() else ""
            st.info(f"No {sport_filter} games found{date_msg}. Try selecting a different date.")
            st.markdown(f"**Expected leagues:** {', '.join(expected_leagues)}")
            st.caption("*Some sports may be in off-season periods*")

def display_games_table(games_df):
    """Display games in a formatted table"""
    if len(games_df) == 0:
        st.info("No games to display")
        return
    
    for idx, game in games_df.iterrows():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
        
        with col1:
            # Game info
            away_team = game.get('away_team', {})
            home_team = game.get('home_team', {})
            
            if isinstance(away_team, dict) and isinstance(home_team, dict):
                st.markdown(f"**{away_team.get('name', 'TBD')} @ {home_team.get('name', 'TBD')}**")
                st.caption(f"{game.get('league', 'Unknown')} | {game.get('date', 'TBD')} | {game.get('time', 'TBD')}")
            else:
                st.markdown(f"**{game.get('game_name', 'Unknown Game')}**")
                st.caption(f"{game.get('league', 'Unknown')} | {game.get('date', 'TBD')}")
        
        with col2:
            # Score or status
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
                st.markdown("**TBD**")
        
        with col3:
            # Status
            status = game.get('status', 'Scheduled')
            if status == 'Final':
                st.success("Final")
            elif status == 'Live':
                st.warning("Live")
            else:
                st.info("Scheduled")
        
        with col4:
            # Action button
            if st.button(f"Analyze", key=f"analyze_{idx}_{game.get('game_id', idx)}"):
                show_game_analysis(game)
        
        st.divider()

def show_game_analysis(game):
    """Show detailed game analysis"""
    with st.expander("🤖 Detailed Game Analysis", expanded=True):
        game_analyzer = st.session_state.get('game_analyzer')
        if not game_analyzer:
            game_analyzer = GameAnalyzer()
            st.session_state.game_analyzer = game_analyzer
        
        # Generate analysis
        analysis = game_analyzer.analyze_game(game)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**AI Prediction:**")
            st.success(f"Winner: {analysis.get('predicted_winner', 'Analysis pending')}")
            st.info(f"Confidence: {analysis.get('confidence', 0):.1%}")
        
        with col2:
            st.markdown("**Key Factors:**")
            factors = analysis.get('key_factors', ['Advanced analytics processing', 'Historical performance review', 'Current form analysis'])
            for factor in factors[:3]:
                st.caption(f"• {factor}")
        
        with col3:
            st.markdown("**Game Details:**")
            st.caption(f"League: {game.get('league', 'N/A')}")
            st.caption(f"Sport: {game.get('sport', 'N/A').title()}")
            st.caption(f"Source: {game.get('source', 'N/A')}")

if __name__ == "__main__":
    main()