import streamlit as st
import sys
import os
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.user_management import UserManager

def show_signup():
    """Signup Page for SportsBet Pro"""
    
    st.set_page_config(
        page_title="Sign Up - SportsBet Pro",
        page_icon="✨",
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
            <h3>Create Your Account</h3>
            <p>Join the AI-powered sports analysis platform</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Back to landing page
    if st.button("← Back to Home"):
        st.switch_page("pages/landing.py")
    
    st.divider()
    
    # Signup form
    st.markdown("### Create New Account")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", placeholder="John")
            email = st.text_input("Email Address *", placeholder="john@example.com")
            password = st.text_input("Password *", type="password", placeholder="Choose a strong password")
        
        with col2:
            last_name = st.text_input("Last Name *", placeholder="Smith")
            phone = st.text_input("Phone (Optional)", placeholder="+1 (555) 123-4567")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Confirm your password")
        
        # Additional preferences
        st.markdown("### Preferences")
        
        col3, col4 = st.columns(2)
        
        with col3:
            favorite_sports = st.multiselect(
                "Favorite Sports (Optional)",
                options=["NFL", "NBA", "MLB", "NHL", "WNBA", "Soccer", "Tennis", "Golf"],
                default=["NFL", "NBA"]
            )
        
        with col4:
            experience_level = st.selectbox(
                "Sports Betting Experience",
                options=["Beginner", "Intermediate", "Advanced", "Professional"],
                index=0
            )
        
        # Terms and conditions
        st.markdown("### Terms & Conditions")
        
        terms_accepted = st.checkbox("""
        I agree to the Terms of Service and Privacy Policy. I understand that SportsBet Pro 
        provides educational content for entertainment purposes only.
        """)
        
        responsible_gambling = st.checkbox("""
        I acknowledge the responsible gambling notice and understand that sports betting 
        involves risk. I will only bet what I can afford to lose.
        """)
        
        # Submit button
        submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            errors = []
            
            if not first_name or not last_name:
                errors.append("First and last name are required")
            
            if not email:
                errors.append("Email address is required")
            elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                errors.append("Please enter a valid email address")
            
            if not password:
                errors.append("Password is required")
            elif len(password) < 6:
                errors.append("Password must be at least 6 characters long")
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if not terms_accepted:
                errors.append("You must accept the Terms of Service")
            
            if not responsible_gambling:
                errors.append("You must acknowledge the responsible gambling notice")
            
            # Display errors or process signup
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Simulate account creation (in real app, this would save to database)
                st.success("Account created successfully!")
                st.balloons()
                
                # Auto-login the new user
                st.session_state.user_authenticated = True
                st.session_state.user_email = email
                st.session_state.user_role = 'user'
                
                # Store user preferences (in real app, this would go to database)
                st.session_state.user_profile = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone,
                    'favorite_sports': favorite_sports,
                    'experience_level': experience_level,
                    'created_date': st.session_state.get('current_date', '2025-07-28')
                }
                
                st.info("Welcome to SportsBet Pro! Redirecting to your dashboard...")
                
                if st.button("Go to Dashboard", type="primary"):
                    st.switch_page("app.py")
    
    st.divider()
    
    # Login option
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Already have an account?")
        if st.button("Login Here", use_container_width=True):
            st.switch_page("pages/login.py")
    
    with col2:
        st.markdown("### Quick Demo Access")
        if st.button("Try Demo Account", use_container_width=True):
            st.info("Use demo credentials: user@demo.com / password")
            st.switch_page("pages/login.py")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>By creating an account, you agree to our commitment to responsible gambling education.</p>
        <p>SportsBet Pro provides analytical insights for entertainment and educational purposes only.</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    show_signup()

if __name__ == "__main__":
    main()