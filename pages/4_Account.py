import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

def main():
    st.set_page_config(
        page_title="SportsBet Pro - Account",
        page_icon="👤",
        layout="wide"
    )
    
    st.title("👤 Account Management")
    
    # User Profile Section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Profile Information")
        
        # Demo user data - would integrate with authentication system
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {
                'name': 'John Smith',
                'email': 'john.smith@email.com',
                'phone': '+1 (555) 123-4567',
                'timezone': 'UTC-5 (Eastern)',
                'joined_date': '2025-01-15'
            }
        
        with st.form("profile_form"):
            name = st.text_input("Full Name", value=st.session_state.user_profile['name'])
            email = st.text_input("Email", value=st.session_state.user_profile['email'])
            phone = st.text_input("Phone", value=st.session_state.user_profile['phone'])
            timezone = st.selectbox("Timezone", [
                'UTC-8 (Pacific)', 'UTC-7 (Mountain)', 
                'UTC-6 (Central)', 'UTC-5 (Eastern)',
                'UTC+0 (GMT)', 'UTC+1 (CET)'
            ], index=3)
            
            if st.form_submit_button("Update Profile"):
                st.session_state.user_profile.update({
                    'name': name, 'email': email, 
                    'phone': phone, 'timezone': timezone
                })
                st.success("Profile updated successfully!")
    
    with col2:
        st.subheader("Subscription Details")
        
        # Current subscription info
        if st.session_state.get('subscription_active'):
            plan = st.session_state.get('subscription_plan', 'pro').title()
            st.success(f"✅ {plan} Plan Active")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Plan", plan)
                st.metric("Status", "Active")
            with col_b:
                st.metric("Next Billing", "Aug 27, 2025")
                st.metric("Amount", "$79.00")
            
            # Subscription actions
            st.subheader("Manage Subscription")
            col_x, col_y = st.columns(2)
            
            with col_x:
                if st.button("Change Plan"):
                    st.info("Redirecting to pricing page...")
            
            with col_y:
                if st.button("Cancel Subscription", type="secondary"):
                    st.warning("Are you sure? You'll lose access to all premium features.")
                    if st.button("Confirm Cancellation"):
                        st.session_state.subscription_active = False
                        st.error("Subscription cancelled.")
        else:
            st.error("❌ No Active Subscription")
            st.info("Upgrade to access premium features")
            if st.button("View Plans"):
                st.switch_page("pages/2_Pricing.py")
    
    st.divider()
    
    # Notification Preferences
    st.subheader("🔔 Notification Preferences")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Email Notifications**")
        email_predictions = st.checkbox("New predictions", value=True)
        email_results = st.checkbox("Prediction results", value=True)
        email_weekly = st.checkbox("Weekly reports", value=False)
    
    with col2:
        st.markdown("**SMS Notifications**") 
        sms_high_confidence = st.checkbox("High confidence picks", value=False)
        sms_live_updates = st.checkbox("Live game updates", value=False)
        sms_results = st.checkbox("Daily results", value=False)
    
    with col3:
        st.markdown("**Push Notifications**")
        push_breaking = st.checkbox("Breaking news", value=True)
        push_game_start = st.checkbox("Game starting soon", value=False)
        push_bet_settled = st.checkbox("Bet settled", value=True)
    
    if st.button("Save Notification Preferences"):
        st.success("Notification preferences saved!")
    
    st.divider()
    
    # Betting History
    st.subheader("📊 Betting History")
    
    # Sample betting history data
    history_data = {
        'Date': ['2025-07-27', '2025-07-26', '2025-07-25', '2025-07-24', '2025-07-23'],
        'Game': ['Lakers vs Warriors', 'Red Sox vs Yankees', 'Man City vs Arsenal', 'Chiefs vs Bills', 'Celtics vs Heat'],
        'Bet': ['Lakers +5.5', 'Over 8.5', 'Man City ML', 'Under 47.5', 'Celtics -3'],
        'Stake': ['$100', '$150', '$75', '$200', '$125'],
        'Odds': ['-110', '-105', '+150', '-108', '-112'],
        'Result': ['Pending', 'Won', 'Won', 'Lost', 'Won'],
        'Profit/Loss': ['-', '+$142.50', '+$112.50', '-$200', '+$111.60']
    }
    
    history_df = pd.DataFrame(history_data)
    st.dataframe(history_df, use_container_width=True)
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bets", "127")
    with col2:
        st.metric("Win Rate", "73.2%")
    with col3:
        st.metric("Total Profit", "+$2,847.30")
    with col4:
        st.metric("ROI", "+24.8%")
    
    st.divider()
    
    # Security Settings
    st.subheader("🔒 Security Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Password**")
        if st.button("Change Password"):
            st.info("Password reset link sent to your email")
        
        st.markdown("**Two-Factor Authentication**")
        if st.button("Enable 2FA"):
            st.success("2FA setup initiated - check your email")
    
    with col2:
        st.markdown("**API Keys**")
        if st.session_state.get('subscription_plan') == 'enterprise':
            if st.button("Manage API Keys"):
                st.switch_page("pages/3_API_Documentation.py")
        else:
            st.info("API access available with Enterprise plan")
        
        st.markdown("**Login History**")
        if st.button("View Login History"):
            st.dataframe({
                'Date': ['2025-07-27 09:15', '2025-07-26 14:22', '2025-07-25 11:08'],
                'IP Address': ['192.168.1.1', '10.0.0.1', '192.168.1.1'],
                'Location': ['New York, NY', 'Los Angeles, CA', 'New York, NY'],
                'Device': ['Chrome/Windows', 'Safari/iPhone', 'Chrome/Windows']
            })
    
    st.divider()
    
    # Data Export
    st.subheader("📁 Data Export")
    st.markdown("Download your data for backup or analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export Betting History"):
            st.success("Betting history exported to CSV")
    
    with col2:
        if st.button("Export Predictions"):
            st.success("All predictions exported to JSON")
    
    with col3:
        if st.button("Export All Data"):
            st.success("Complete data archive created")
    
    # Account Deletion
    st.divider()
    st.subheader("⚠️ Danger Zone")
    
    with st.expander("Delete Account"):
        st.error("This action cannot be undone!")
        st.write("Deleting your account will:")
        st.write("• Remove all your data permanently")
        st.write("• Cancel your subscription")
        st.write("• Revoke API access")
        
        if st.button("I understand, delete my account", type="secondary"):
            st.error("Account deletion initiated. You have 7 days to cancel this request.")

if __name__ == "__main__":
    main()