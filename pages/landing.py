import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.user_management import UserManager

def show_landing():
    """SportsBet Pro Landing Page"""
    
    st.set_page_config(
        page_title="SportsBet Pro - AI Sports Analysis",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize user manager
    if 'user_manager' not in st.session_state:
        st.session_state.user_manager = UserManager()
    
    user_manager = st.session_state.user_manager
    user_manager.initialize_session()
    
    # Check if user is already authenticated
    if user_manager.is_authenticated():
        st.switch_page("app.py")
        return
    
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 1rem;">🏆 SportsBet Pro</h1>
        <h2 style="color: #666; font-weight: 300; margin-bottom: 2rem;">AI-Powered Sports Analysis & Prediction Platform</h2>
        <p style="font-size: 1.2rem; color: #888; max-width: 800px; margin: 0 auto;">
            Advanced dual AI consensus system combining ChatGPT and Gemini with real-time sports data 
            and betting odds for comprehensive game insights and responsible gambling education.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick access buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown("### 🎯 Features")
        st.markdown("""
        - **Dual AI Analysis**: ChatGPT + Gemini consensus
        - **Live Odds Integration**: Real-time betting data
        - **Performance Tracking**: Win/loss analytics
        - **28+ Sports**: NFL, NBA, MLB, NHL, WNBA & more
        - **Responsible Gambling**: Educational insights only
        """)
    
    with col2:
        st.markdown("### 🚀 Get Started")
        
        if st.button("🔑 Login", type="primary", use_container_width=True):
            st.switch_page("pages/login.py")
        
        if st.button("✨ Create Account", use_container_width=True):
            st.switch_page("pages/signup.py")
        
        if st.button("👁️ View Demo", use_container_width=True):
            st.info("Demo credentials: user@demo.com / password")
            st.switch_page("pages/login.py")
    
    with col3:
        st.markdown("### 📊 Live Stats")
        try:
            from utils.live_games import LiveGamesManager
            from utils.odds_api import OddsAPIManager
            
            games_manager = LiveGamesManager()
            odds_manager = OddsAPIManager()
            
            # Get live data counts
            from datetime import date
            games_df = games_manager.get_upcoming_games_all_sports(target_date=date.today())
            odds_df = odds_manager.get_comprehensive_odds()
            
            st.metric("Games Today", len(games_df))
            st.metric("Live Odds Available", len(odds_df))
            st.metric("Sports Covered", "28+")
            
        except Exception as e:
            st.metric("Games Today", "Loading...")
            st.metric("Live Odds Available", "Loading...")
            st.metric("Sports Covered", "28+")
    
    st.divider()
    
    # Responsible gambling notice
    st.warning("""
    ⚠️ **RESPONSIBLE GAMBLING NOTICE**: SportsBet Pro provides analytical insights for educational and entertainment purposes only. 
    Sports betting involves risk. Never bet more than you can afford to lose. This platform promotes responsible gambling practices.
    """)
    
    # How it works section
    st.markdown("## 🔬 How It Works")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        ### 1️⃣ Data Collection
        - Live sports data from ESPN & other sources
        - Real-time betting odds from 312+ games
        - Historical performance metrics
        """)
    
    with col2:
        st.markdown("""
        ### 2️⃣ AI Analysis
        - ChatGPT game analysis & predictions
        - Gemini statistical modeling
        - Dual AI consensus system
        """)
    
    with col3:
        st.markdown("""
        ### 3️⃣ Insights Generation
        - High-confidence picks identification
        - Value betting analysis
        - Performance tracking
        """)
    
    with col4:
        st.markdown("""
        ### 4️⃣ Results Tracking
        - Real-time score monitoring
        - Prediction accuracy analysis
        - Educational feedback
        """)
    
    st.divider()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #666;">
        <p>© 2025 SportsBet Pro - Educational Sports Analysis Platform</p>
        <p>Built with advanced AI, real-time data, and responsible gambling principles</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    show_landing()

if __name__ == "__main__":
    main()