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
    """Initialize all session state variables with lazy loading"""
    
    # Core managers (always needed)
    if 'user_manager' not in st.session_state:
        st.session_state.user_manager = UserManager()
    
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = OptimizedDataLoader()
    
    # Initialize flags for lazy loading
    if 'managers_initialized' not in st.session_state:
        st.session_state.managers_initialized = False
    
    if 'ai_systems_initialized' not in st.session_state:
        st.session_state.ai_systems_initialized = False

def get_games_manager():
    """Lazy load games manager"""
    if 'games_manager' not in st.session_state:
        st.session_state.games_manager = LiveGamesManager()
    return st.session_state.games_manager

def get_odds_manager():
    """Lazy load odds manager"""
    if 'odds_manager' not in st.session_state:
        st.session_state.odds_manager = OddsAPIManager()
    return st.session_state.odds_manager

def get_consensus_engine():
    """Lazy load consensus engine"""
    if 'consensus_engine' not in st.session_state:
        st.session_state.consensus_engine = DualAIConsensusEngine()
    return st.session_state.consensus_engine

def get_ai_analyzer():
    """Lazy load AI analyzer"""
    if 'ai_analyzer' not in st.session_state:
        st.session_state.ai_analyzer = AIGameAnalyzer()
    return st.session_state.ai_analyzer

def get_ai_chat():
    """Lazy load AI chat"""
    if 'ai_chat' not in st.session_state:
        from utils.ai_chat import DualAIChat
        st.session_state.ai_chat = DualAIChat()
    return st.session_state.ai_chat

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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎯 Unified Analysis", 
        "💬 AI Chat",
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
        from pages.ai_chat import show_ai_chat
        show_ai_chat()
    
    with tab3:
        from pages.ai_predictions import show_ai_predictions
        show_ai_predictions()
    
    with tab4:
        from pages.winning_picks import show_winning_picks
        show_winning_picks()
    
    with tab5:
        from pages.performance_tracking import show_performance_tracking
        show_performance_tracking()
    
    with tab6:
        from pages.live_odds import show_live_odds
        show_live_odds()
    
    with tab7:
        show_legacy_pages()

def show_legacy_pages():
    """Show legacy page navigation and authentication options"""
    st.markdown("### ⚙️ Legacy Pages & Authentication")
    st.markdown("Access individual specialized pages and authentication options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Authentication**")
        if st.button("🏠 Landing Page"):
            st.switch_page("pages/landing.py")
        if st.button("🔑 Login"):
            st.switch_page("pages/login.py")
        if st.button("✨ Sign Up"):
            st.switch_page("pages/signup.py")
        
        # Logout option if authenticated
        if st.session_state.get('user_authenticated', False):
            if st.button("🚪 Logout"):
                # Clear authentication
                st.session_state.user_authenticated = False
                st.session_state.user_email = ''
                st.session_state.user_role = 'user'
                st.success("Logged out successfully!")
                st.switch_page("pages/landing.py")
    
    with col2:
        st.markdown("**Navigation Pages**")
        if st.button("📊 User Dashboard"):
            st.switch_page("pages/user_dashboard.py")
        if st.button("⚙️ Admin Dashboard"):
            st.switch_page("pages/admin_dashboard.py")
        if st.button("🏈 All Sports"):
            st.switch_page("pages/all_sports.py")
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
        if st.button("📚 Support"):
            st.switch_page("pages/5_Support.py")

def show_sidebar_info():
    """Show sidebar with system information"""
    with st.sidebar:
        st.markdown("## 🏆 SportsBet Pro")
        st.markdown("*AI-Powered Sports Analysis*")
        
        # System status
        st.markdown("### 📊 System Status")
        
        # Get cached data counts for speed
        cache_key_games = f"sidebar_games_count_{date.today()}"
        cache_key_odds = f"sidebar_odds_count_{datetime.now().hour}"
        
        games_count = st.session_state.get(cache_key_games, 0)
        odds_count = st.session_state.get(cache_key_odds, 0)
        
        # Update counts only if cache is empty (avoid blocking sidebar)
        if games_count == 0:
            try:
                games_df = get_games_manager().get_upcoming_games_all_sports(target_date=date.today())
                games_count = len(games_df)
                st.session_state[cache_key_games] = games_count
            except:
                games_count = 0
        
        if odds_count == 0:
            try:
                odds_df = get_odds_manager().get_comprehensive_odds()
                odds_count = len(odds_df) 
                st.session_state[cache_key_odds] = odds_count
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
        
        if st.button("💬 AI Chat", key="sidebar_chat"):
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

# Test if imports work first
try:
    from utils.user_management import UserManager
    from utils.live_games import LiveGamesManager
    from utils.odds_api import OddsAPIManager
    IMPORTS_OK = True
except Exception as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)

def main():
    """Main application entry point"""
    
    # Configure page
    configure_page()
    
    if not IMPORTS_OK:
        st.error(f"Import Error: {IMPORT_ERROR}")
        st.info("Running in basic mode...")
        st.title("🏆 SportsBet Pro")
        st.markdown("Application is loading but some features may be unavailable due to import issues.")
        return
    
    try:
        # Initialize session state
        initialize_session_state()
        
        # Show sidebar
        show_sidebar_info()
        
        # Show main content
        show_main_navigation()
        
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Displaying basic interface...")
        st.title("🏆 SportsBet Pro")
        st.markdown("Application encountered an error. Please try refreshing the page.")
        
        # Show basic content
        st.markdown("""
        ### Available Features:
        - This basic interface is working
        - Full features will be restored once issues are resolved
        """)

if __name__ == "__main__":
    main()