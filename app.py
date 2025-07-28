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
    """Main application with modern navigation"""
    user_manager = st.session_state.user_manager
    
    # Check authentication
    if not user_manager.is_authenticated():
        # Welcome page for unauthenticated users
        st.title("🏆 SportsBet Pro")
        st.markdown("### Professional AI-Powered Sports Analytics Platform")
        
        st.markdown("""
        Welcome to SportsBet Pro - your gateway to professional sports analytics and AI-powered predictions.
        
        **Features:**
        - Real-time game analysis and predictions
        - Advanced analytics dashboard
        - Personalized performance tracking
        - Professional betting insights
        """)
        
        st.info("Please login to access your personalized dashboard")
        user_manager.login_form()
        return
    
    # Navigation based on user role
    user_info = user_manager.get_user_info()
    
    # Modern sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👤 {user_info['email'].split('@')[0].title()}")
        st.caption(f"Role: {user_info['role'].title()}")
        
        if st.button("🚪 Logout"):
            user_manager.logout()
            
        st.divider()
        
        # Navigation based on role
        if user_manager.is_admin():
            st.markdown("### 🔧 Admin Navigation")
            if st.button("⚙️ Admin Dashboard", use_container_width=True):
                st.switch_page("pages/admin_dashboard.py")
            if st.button("👥 User Dashboard", use_container_width=True):
                st.switch_page("pages/user_dashboard.py")
            if st.button("🔧 API Documentation", use_container_width=True):
                st.switch_page("pages/3_API_Documentation.py")
        else:
            st.markdown("### 📊 User Navigation")
            if st.button("📊 My Dashboard", use_container_width=True):
                st.switch_page("pages/user_dashboard.py")
            if st.button("💰 Pricing", use_container_width=True):
                st.switch_page("pages/2_Pricing.py")
            if st.button("👤 Account", use_container_width=True):
                st.switch_page("pages/4_Account.py")
            if st.button("🎧 Support", use_container_width=True):
                st.switch_page("pages/5_Support.py")
    
    # Default to user dashboard
    st.switch_page("pages/user_dashboard.py")

if __name__ == "__main__":
    main()