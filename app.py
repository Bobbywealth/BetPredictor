import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.user_management import UserManager
from utils.game_analyzer import GameAnalyzer

# Page configuration
st.set_page_config(
    page_title="SportsBet Pro",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize managers
if 'user_manager' not in st.session_state:
    st.session_state.user_manager = UserManager()
if 'game_analyzer' not in st.session_state:
    st.session_state.game_analyzer = GameAnalyzer()

# Initialize user session
st.session_state.user_manager.initialize_session()

def main():
    """Main application with organized navigation"""
    user_manager = st.session_state.user_manager
    
    # Check authentication
    if not user_manager.is_authenticated():
        # Clean welcome page
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 2rem 0;'>
                <h1>🏆 SportsBet Pro</h1>
                <h3>Professional Sports Analytics Platform</h3>
                <p style='color: #666; margin: 1rem 0;'>
                    AI-powered predictions and analytics for professional sports betting
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Feature highlights
            st.markdown("---")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown("**🎯 Live Predictions**\nReal-time AI analysis")
            with col_b:
                st.markdown("**📊 Advanced Analytics**\nDeep statistical insights")
            with col_c:
                st.markdown("**🔒 Secure Platform**\nProfessional-grade security")
            
            st.markdown("---")
            user_manager.login_form()
        return
    
    # Navigation for authenticated users
    user_info = user_manager.get_user_info()
    
    # Clean header
    header_col1, header_col2, header_col3 = st.columns([2, 3, 2])
    with header_col1:
        st.markdown("# 🏆 SportsBet Pro")
    with header_col2:
        st.markdown(f"<div style='text-align: center; padding-top: 1rem;'><h4>Welcome, {user_info['email'].split('@')[0].title()}</h4></div>", unsafe_allow_html=True)
    with header_col3:
        if st.button("🚪 Logout", type="secondary"):
            user_manager.logout()
    
    st.divider()
    
    # Organized navigation tabs
    if user_manager.is_admin():
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🏠 Dashboard", "👥 User View", "🏈 All Sports", "🤖 AI Predictions", "💰 Live Odds", "📚 API Docs", "⚙️ Settings"])
        
        with tab1:
            st.switch_page("pages/admin_dashboard.py")
        with tab2:
            st.switch_page("pages/user_dashboard.py")
        with tab3:
            st.switch_page("pages/all_sports.py")
        with tab4:
            st.switch_page("pages/ai_predictions.py")
        with tab5:
            st.switch_page("pages/live_odds.py")
        with tab6:
            st.switch_page("pages/3_API_Documentation.py")
        with tab7:
            st.info("Admin settings coming soon")
    else:
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🏠 Dashboard", "🏈 All Sports", "🤖 AI Predictions", "💰 Live Odds", "💲 Pricing", "👤 Account", "🎧 Support"])
        
        with tab1:
            st.switch_page("pages/user_dashboard.py")
        with tab2:
            st.switch_page("pages/all_sports.py")
        with tab3:
            st.switch_page("pages/ai_predictions.py")
        with tab4:
            st.switch_page("pages/live_odds.py")
        with tab5:
            st.switch_page("pages/2_Pricing.py")
        with tab6:
            st.switch_page("pages/4_Account.py")
        with tab7:
            st.switch_page("pages/5_Support.py")

if __name__ == "__main__":
    main()