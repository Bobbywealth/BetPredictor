import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import utilities and managers
from utils.user_management import UserManager
from utils.live_games import LiveGamesManager
from utils.odds_api import OddsAPIManager
from utils.cache_manager import OptimizedDataLoader
from utils.dual_ai_consensus import DualAIConsensusEngine, WinningPicksGenerator
from utils.result_tracker import GameResultTracker
from utils.ai_analysis import AIGameAnalyzer
from utils.deep_analysis import DeepGameAnalyzer

def initialize_session_state():
    """Initialize all session state variables"""
    
    # Core managers
    if 'user_manager' not in st.session_state:
        st.session_state.user_manager = UserManager()
    
    if 'games_manager' not in st.session_state:
        st.session_state.games_manager = LiveGamesManager()
    
    if 'odds_manager' not in st.session_state:
        st.session_state.odds_manager = OddsAPIManager()
    
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = OptimizedDataLoader()
    
    # AI systems
    if 'consensus_engine' not in st.session_state:
        st.session_state.consensus_engine = DualAIConsensusEngine()
    
    if 'picks_generator' not in st.session_state:
        st.session_state.picks_generator = WinningPicksGenerator()
    
    if 'result_tracker' not in st.session_state:
        st.session_state.result_tracker = GameResultTracker()
    
    if 'ai_analyzer' not in st.session_state:
        st.session_state.ai_analyzer = AIGameAnalyzer()
    
    if 'deep_analyzer' not in st.session_state:
        st.session_state.deep_analyzer = DeepGameAnalyzer()

def configure_page():
    """Configure the Streamlit page"""
    st.set_page_config(
        page_title="SportsBet Pro - AI-Powered Sports Analysis",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def show_main_navigation():
    """Show main navigation and content"""
    
    # Page header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>🏆 SportsBet Pro</h1>
        <h3>AI-Powered Sports Analysis & Prediction Platform</h3>
        <p><em>Advanced dual AI consensus system with real-time odds integration</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Responsible gambling notice
    st.warning("""
    ⚠️ **RESPONSIBLE GAMBLING NOTICE**: This platform provides analytical insights for educational purposes only. 
    Sports betting involves risk. Never bet more than you can afford to lose. Please gamble responsibly.
    """)
    
    st.divider()
    
    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Unified Analysis", 
        "🤖 AI Predictions", 
        "🏆 Winning Picks", 
        "📊 Performance", 
        "💰 Live Odds",
        "⚙️ Legacy Pages"
    ])
    
    with tab1:
        from pages.unified_analysis import show_unified_analysis
        show_unified_analysis()
    
    with tab2:
        from pages.ai_predictions import show_ai_predictions
        show_ai_predictions()
    
    with tab3:
        from pages.winning_picks import show_winning_picks
        show_winning_picks()
    
    with tab4:
        from pages.performance_tracking import show_performance_tracking
        show_performance_tracking()
    
    with tab5:
        from pages.live_odds import show_live_odds
        show_live_odds()
    
    with tab6:
        show_legacy_pages()

def show_legacy_pages():
    """Show legacy page navigation"""
    st.markdown("### ⚙️ Legacy Pages")
    st.markdown("Access individual specialized pages for detailed analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Navigation Pages**")
        if st.button("📊 User Dashboard"):
            st.switch_page("pages/user_dashboard.py")
        if st.button("⚙️ Admin Dashboard"):
            st.switch_page("pages/admin_dashboard.py")
        if st.button("🏈 All Sports"):
            st.switch_page("pages/all_sports.py")
    
    with col2:
        st.markdown("**Analysis Pages**")
        if st.button("🔍 Deep Analysis"):
            st.switch_page("pages/deep_analysis_dashboard.py")
    
    with col3:
        st.markdown("**System Pages**")
        if st.button("📋 Dashboard"):
            st.switch_page("pages/1_Dashboard.py")
        if st.button("💰 Pricing"):
            st.switch_page("pages/2_Pricing.py")
        if st.button("👤 Account"):
            st.switch_page("pages/4_Account.py")

def show_sidebar_info():
    """Show sidebar with system information"""
    with st.sidebar:
        st.markdown("## 🏆 SportsBet Pro")
        st.markdown("*AI-Powered Sports Analysis*")
        
        # System status
        st.markdown("### 📊 System Status")
        
        # Get real data counts
        try:
            games_df = st.session_state.games_manager.get_upcoming_games_all_sports(target_date=date.today())
            games_count = len(games_df)
        except:
            games_count = 0
        
        try:
            odds_df = st.session_state.odds_manager.get_comprehensive_odds()
            odds_count = len(odds_df)
        except:
            odds_count = 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Games Today", games_count)
        with col2:
            st.metric("Live Odds", odds_count)
        
        # Quick access
        st.markdown("### 🚀 Quick Access")
        if st.button("🎯 Unified Analysis", key="sidebar_unified"):
            st.rerun()
        
        if st.button("🏆 Today's Picks", key="sidebar_picks"):
            st.rerun()
        
        # System info
        st.markdown("### ℹ️ About")
        st.markdown("""
        **SportsBet Pro** combines advanced AI analysis from ChatGPT and Gemini 
        with real-time sports data and betting odds for comprehensive game insights.
        
        **Features:**
        - Dual AI consensus analysis
        - Live odds integration
        - Performance tracking
        - Responsible gambling tools
        """)

def main():
    """Main application entry point"""
    
    # Configure page
    configure_page()
    
    # Initialize session state
    initialize_session_state()
    
    # Show sidebar
    show_sidebar_info()
    
    # Show main content
    show_main_navigation()

if __name__ == "__main__":
    main()