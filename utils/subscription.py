"""
Subscription management utilities for SportsBet Pro SaaS platform
"""
import streamlit as st
from datetime import datetime, timedelta

class SubscriptionManager:
    """Manages user subscriptions and plan limitations"""
    
    def __init__(self):
        self.plans = {
            'free': {
                'name': 'Free',
                'price': 0,
                'predictions_per_day': 3,
                'sports_access': ['soccer'],
                'features': ['basic_predictions', 'live_games'],
                'api_access': False,
                'sms_alerts': False,
                'advanced_analytics': False
            },
            'basic': {
                'name': 'Basic',
                'price': 29,
                'predictions_per_day': 5,
                'sports_access': ['soccer', 'basketball', 'baseball'],
                'features': ['basic_predictions', 'live_games', 'email_alerts'],
                'api_access': False,
                'sms_alerts': False,
                'advanced_analytics': False
            },
            'pro': {
                'name': 'Pro', 
                'price': 79,
                'predictions_per_day': -1,  # Unlimited
                'sports_access': ['soccer', 'basketball', 'baseball', 'football', 'hockey'],
                'features': ['all_predictions', 'live_games', 'email_alerts', 'sms_alerts', 'advanced_analytics'],
                'api_access': False,
                'sms_alerts': True,
                'advanced_analytics': True
            },
            'enterprise': {
                'name': 'Enterprise',
                'price': 199,
                'predictions_per_day': -1,  # Unlimited
                'sports_access': 'all',
                'features': ['all_predictions', 'live_games', 'email_alerts', 'sms_alerts', 'advanced_analytics', 'api_access'],
                'api_access': True,
                'sms_alerts': True,
                'advanced_analytics': True
            }
        }
    
    def get_user_plan(self):
        """Get current user's plan"""
        if st.session_state.get('subscription_active', False):
            return st.session_state.get('subscription_plan', 'free')
        return 'free'
    
    def get_plan_features(self, plan_name):
        """Get features for a specific plan"""
        return self.plans.get(plan_name, self.plans['free'])
    
    def check_feature_access(self, feature_name):
        """Check if user has access to a specific feature"""
        plan = self.get_user_plan()
        plan_features = self.get_plan_features(plan)
        return feature_name in plan_features['features']
    
    def check_sport_access(self, sport):
        """Check if user has access to a specific sport"""
        plan = self.get_user_plan()
        plan_features = self.get_plan_features(plan)
        
        if plan_features['sports_access'] == 'all':
            return True
        
        return sport.lower() in plan_features['sports_access']
    
    def get_daily_prediction_limit(self):
        """Get daily prediction limit for user's plan"""
        plan = self.get_user_plan()
        plan_features = self.get_plan_features(plan)
        return plan_features['predictions_per_day']
    
    def check_predictions_limit(self):
        """Check if user has reached daily prediction limit"""
        limit = self.get_daily_prediction_limit()
        
        if limit == -1:  # Unlimited
            return True
        
        # Check daily usage from session state/database
        today = datetime.now().strftime('%Y-%m-%d')
        usage_key = f'predictions_used_{today}'
        used_today = st.session_state.get(usage_key, 0)
        
        return used_today < limit
    
    def use_prediction(self):
        """Record a prediction usage"""
        today = datetime.now().strftime('%Y-%m-%d')
        usage_key = f'predictions_used_{today}'
        used_today = st.session_state.get(usage_key, 0)
        st.session_state[usage_key] = used_today + 1
    
    def show_upgrade_prompt(self, feature_name):
        """Show upgrade prompt for restricted features"""
        st.error(f"🔒 {feature_name} requires a paid subscription")
        st.info("Upgrade your plan to access this feature")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Pricing", key=f"pricing_{feature_name}"):
                st.switch_page("pages/2_Pricing.py")
        with col2:
            if st.button("Learn More", key=f"learn_{feature_name}"):
                st.info("Contact sales for more information: sales@sportsbetpro.com")
    
    def get_subscription_status_widget(self):
        """Widget showing subscription status"""
        plan = self.get_user_plan()
        plan_info = self.get_plan_features(plan)
        
        if plan == 'free':
            st.sidebar.error("🆓 Free Plan")
            st.sidebar.info("Limited features available")
        else:
            st.sidebar.success(f"💎 {plan_info['name']} Plan")
            st.sidebar.info(f"${plan_info['price']}/month")
        
        # Usage stats
        limit = self.get_daily_prediction_limit()
        if limit != -1:
            today = datetime.now().strftime('%Y-%m-%d')
            usage_key = f'predictions_used_{today}'
            used = st.session_state.get(usage_key, 0)
            remaining = max(0, limit - used)
            
            st.sidebar.metric("Predictions Today", f"{used}/{limit}")
            
            if remaining == 0:
                st.sidebar.error("Daily limit reached!")
        else:
            st.sidebar.metric("Predictions", "Unlimited ∞")
    
    def require_subscription(self, min_plan='basic'):
        """Decorator/helper to require minimum subscription level"""
        current_plan = self.get_user_plan()
        plan_hierarchy = ['free', 'basic', 'pro', 'enterprise']
        
        if plan_hierarchy.index(current_plan) < plan_hierarchy.index(min_plan):
            required_plan = self.get_plan_features(min_plan)
            st.error(f"🔒 This feature requires {required_plan['name']} plan or higher")
            st.info(f"Upgrade to {required_plan['name']} (${required_plan['price']}/month) to access this feature")
            
            if st.button("Upgrade Now", key=f"upgrade_to_{min_plan}"):
                st.switch_page("pages/2_Pricing.py")
            
            return False
        
        return True