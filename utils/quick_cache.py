import streamlit as st
import pandas as pd
from datetime import date

# Streamlined caching for maximum speed

@st.cache_data(ttl=180)  # 3 minute cache
def get_today_games():
    """Ultra-fast cached games for today"""
    try:
        from utils.live_games import LiveGamesManager
        manager = LiveGamesManager()
        return manager.get_upcoming_games_all_sports(target_date=date.today())
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300)  # 5 minute cache  
def get_live_odds():
    """Ultra-fast cached odds data"""
    try:
        from utils.odds_api import OddsAPIManager
        manager = OddsAPIManager()
        return manager.get_comprehensive_odds()
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)  # 10 minute cache
def get_ai_predictions():
    """Cached AI predictions to avoid repeated API calls"""
    try:
        from utils.ai_analysis import AIGameAnalyzer
        analyzer = AIGameAnalyzer()
        games_df = get_today_games()
        if len(games_df) > 0:
            return analyzer.analyze_games_batch(games_df.head(5))  # Limit to 5 games for speed
        return []
    except:
        return []

def clear_all_caches():
    """Clear all Streamlit caches for fresh data"""
    st.cache_data.clear()
    st.success("🚀 All caches cleared - fresh data loaded!")

def show_cache_status():
    """Show current cache status"""
    games_count = len(get_today_games())
    odds_count = len(get_live_odds())
    predictions_count = len(get_ai_predictions())
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Games Cached", games_count)
    
    with col2:
        st.metric("💰 Odds Cached", odds_count)
    
    with col3:
        st.metric("🤖 AI Predictions", predictions_count)