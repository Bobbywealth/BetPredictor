import streamlit as st
import time
import pandas as pd

# Simple but effective performance optimizations

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_games_data():
    """Cache expensive games data calls"""
    try:
        from utils.live_games import LiveGamesManager
        from datetime import date
        
        games_manager = LiveGamesManager()
        return games_manager.get_upcoming_games_all_sports(target_date=date.today())
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)  # Cache for 5 minutes  
def cached_odds_data():
    """Cache expensive odds data calls"""
    try:
        from utils.odds_api import OddsAPIManager
        
        odds_manager = OddsAPIManager()
        return odds_manager.get_comprehensive_odds()
    except:
        return pd.DataFrame()

def optimize_dataframe(df: pd.DataFrame, max_rows: int = 500) -> pd.DataFrame:
    """Optimize DataFrame display for speed"""
    if len(df) > max_rows:
        return df.head(max_rows)
    return df

def show_loading_placeholder(message: str = "Loading..."):
    """Show loading placeholder that auto-clears"""
    placeholder = st.empty()
    placeholder.info(f"⚡ {message}")
    return placeholder

def clear_placeholder(placeholder):
    """Clear loading placeholder"""
    if placeholder:
        placeholder.empty()

# Quick performance metrics
def show_speed_metrics():
    """Show simple speed metrics"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        games_count = len(cached_games_data())
        st.metric("Games Cached", games_count)
    
    with col2:
        odds_count = len(cached_odds_data()) 
        st.metric("Odds Cached", odds_count)
    
    with col3:
        load_time = time.time() - st.session_state.get('page_load_start', time.time())
        st.metric("Load Time", f"{load_time:.1f}s")