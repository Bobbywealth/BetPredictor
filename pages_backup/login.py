import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.user_management import UserManager

def show_login():
    """Login Page for SportsBet Pro"""
    
    st.set_page_config(
        page_title="Login - SportsBet Pro",
        page_icon="🔑",
        layout="centered"
    )
    
    # Initialize user manager
    if 'user_manager' not in st.session_state:
        st.session_state.user_manager = UserManager()
    
    user_manager = st.session_state.user_manager
    user_manager.initialize_session()
    
    # Check if user is already authenticated
    if user_manager.is_authenticated():
        st.success("Already logged in! Redirecting to dashboard...")
        st.switch_page("app.py")
        return
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1>🏆 SportsBet Pro</h1>
            <h3>Login to Your Account</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Back to landing page
    if st.button("← Back to Home"):
        st.switch_page("pages/landing.py")
    
    st.divider()
    
    # Login form using UserManager
    user_manager.login_form()
    
    # Check if login was successful
    if user_manager.is_authenticated():
        st.success(f"Welcome back! Logged in as {st.session_state.user_role}")
        st.balloons()
        
        # Redirect based on role
        if user_manager.is_admin():
            st.info("Redirecting to admin dashboard...")
            if st.button("Go to Admin Dashboard", type="primary"):
                st.switch_page("pages/admin_dashboard.py")
        else:
            st.info("Redirecting to main dashboard...")
            if st.button("Go to Dashboard", type="primary"):
                st.switch_page("app.py")
    
    st.divider()
    
    # Additional options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Don't have an account?")
        if st.button("Create New Account", use_container_width=True):
            st.switch_page("pages/signup.py")
    
    with col2:
        st.markdown("### Need Help?")
        if st.button("Demo Access", use_container_width=True):
            st.info("""
            **Demo Credentials:**
            
            **User Access:**
            - Email: user@demo.com
            - Password: password
            
            **Admin Access:**
            - Email: admin@sportsbet.com  
            - Password: admin123
            """)

def main():
    show_login()

if __name__ == "__main__":
    main()