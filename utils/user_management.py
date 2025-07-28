import streamlit as st
from datetime import datetime

class UserManager:
    """Manages user authentication and role-based access"""
    
    def __init__(self):
        self.admin_users = ['admin@sportsbet.com', 'admin']
        
    def initialize_session(self):
        """Initialize user session state"""
        if 'user_authenticated' not in st.session_state:
            st.session_state.user_authenticated = False
        if 'user_role' not in st.session_state:
            st.session_state.user_role = 'user'
        if 'user_email' not in st.session_state:
            st.session_state.user_email = ''
            
    def is_admin(self):
        """Check if current user is admin"""
        return (st.session_state.get('user_authenticated', False) and 
                st.session_state.get('user_role') == 'admin')
                
    def is_authenticated(self):
        """Check if user is authenticated"""
        return st.session_state.get('user_authenticated', False)
        
    def login_form(self):
        """Display login form"""
        st.markdown("### Login to SportsBet Pro")
        
        # Display demo credentials
        st.info("**Demo Login Credentials:**")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Customer Access:**")
            st.code("Email: user@demo.com\nPassword: password")
        with col2:
            st.markdown("**Admin Access:**")
            st.code("Email: admin@sportsbet.com\nPassword: admin123")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="user@demo.com or admin@sportsbet.com")
            password = st.text_input("Password", type="password", placeholder="password or admin123")
            submitted = st.form_submit_button("Login", type="primary")
            
            if submitted:
                # Simple authentication for demo
                if email and password:
                    # Check credentials
                    valid_login = False
                    
                    # Admin credentials
                    if email == "admin@sportsbet.com" and password == "admin123":
                        valid_login = True
                        st.session_state.user_role = 'admin'
                    # Customer credentials  
                    elif email == "user@demo.com" and password == "password":
                        valid_login = True
                        st.session_state.user_role = 'user'
                    # Fallback - any email/password for testing
                    elif email and password:
                        valid_login = True
                        if email in self.admin_users:
                            st.session_state.user_role = 'admin'
                        else:
                            st.session_state.user_role = 'user'
                    
                    if valid_login:
                        st.session_state.user_authenticated = True
                        st.session_state.user_email = email
                        st.success(f"Welcome {'Admin' if self.is_admin() else 'Customer'}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Use demo credentials above.")
                else:
                    st.error("Please enter email and password")
                    
    def logout(self):
        """Logout user"""
        st.session_state.user_authenticated = False
        st.session_state.user_role = 'user'
        st.session_state.user_email = ''
        st.rerun()
        
    def get_user_info(self):
        """Get current user information"""
        return {
            'email': st.session_state.get('user_email', ''),
            'role': st.session_state.get('user_role', 'user'),
            'authenticated': st.session_state.get('user_authenticated', False)
        }