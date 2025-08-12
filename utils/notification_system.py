"""
Advanced Notification System for BetPredictor
- Real-time game finish notifications
- Pick result alerts
- Performance milestones
- Custom notification types with animations
"""

import streamlit as st
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

class NotificationManager:
    """Manages all notifications across the app"""
    
    def __init__(self):
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        if 'notification_settings' not in st.session_state:
            st.session_state.notification_settings = {
                'game_finish': True,
                'pick_results': True,
                'performance_milestones': True,
                'daily_summary': True,
                'sound_enabled': True,
                'auto_dismiss': 5  # seconds
            }
    
    def add_notification(self, 
                        title: str, 
                        message: str, 
                        type: str = "info",
                        action_button: Optional[Dict] = None,
                        auto_dismiss: bool = True,
                        sound: bool = False):
        """Add a new notification"""
        notification = {
            'id': f"notif_{int(time.time() * 1000)}",
            'title': title,
            'message': message,
            'type': type,  # success, error, warning, info, game_finish, pick_result
            'timestamp': datetime.now().isoformat(),
            'action_button': action_button,
            'auto_dismiss': auto_dismiss,
            'sound': sound,
            'dismissed': False
        }
        
        st.session_state.notifications.insert(0, notification)
        
        # Limit to last 50 notifications
        if len(st.session_state.notifications) > 50:
            st.session_state.notifications = st.session_state.notifications[:50]
        
        return notification['id']
    
    def game_finished_notification(self, game_data: Dict, pick_data: Optional[Dict] = None):
        """Notification when a game finishes"""
        if not st.session_state.notification_settings.get('game_finish', True):
            return
        
        away_team = game_data.get('away_team', 'Away')
        home_team = game_data.get('home_team', 'Home')
        away_score = game_data.get('away_score', 0)
        home_score = game_data.get('home_score', 0)
        
        title = f"🏆 Game Final"
        message = f"{away_team} {away_score} - {home_score} {home_team}"
        
        # Add pick result if available
        if pick_data:
            predicted_winner = pick_data.get('predicted_winner', '')
            actual_winner = game_data.get('winner', '')
            was_correct = predicted_winner == actual_winner
            
            if was_correct:
                message += f" ✅ Your pick ({predicted_winner}) WON!"
                notification_type = "success"
            else:
                message += f" ❌ Your pick ({predicted_winner}) lost"
                notification_type = "error"
        else:
            notification_type = "game_finish"
        
        action_button = {
            'text': 'View Details',
            'action': 'show_game_details',
            'data': game_data
        }
        
        return self.add_notification(
            title=title,
            message=message,
            type=notification_type,
            action_button=action_button,
            sound=True
        )
    
    def pick_result_notification(self, pick_data: Dict, result: str):
        """Notification for individual pick results"""
        if not st.session_state.notification_settings.get('pick_results', True):
            return
        
        away_team = pick_data.get('away_team', 'Away')
        home_team = pick_data.get('home_team', 'Home')
        predicted_winner = pick_data.get('predicted_winner', 'Unknown')
        confidence = pick_data.get('confidence', 0) * 100
        
        if result == 'win':
            title = "🎉 Pick Winner!"
            message = f"{predicted_winner} won! ({away_team} @ {home_team}) - {confidence:.0f}% confidence"
            notification_type = "success"
        else:
            title = "😔 Pick Lost"
            message = f"{predicted_winner} lost ({away_team} @ {home_team}) - {confidence:.0f}% confidence"
            notification_type = "error"
        
        action_button = {
            'text': 'View Win Tracker',
            'action': 'navigate_to_win_tracker'
        }
        
        return self.add_notification(
            title=title,
            message=message,
            type=notification_type,
            action_button=action_button,
            sound=True
        )
    
    def performance_milestone_notification(self, milestone_type: str, data: Dict):
        """Notification for performance achievements"""
        if not st.session_state.notification_settings.get('performance_milestones', True):
            return
        
        milestone_messages = {
            'win_streak': f"🔥 {data['streak']} game win streak!",
            'accuracy_milestone': f"🎯 {data['accuracy']:.1%} accuracy achieved!",
            'profit_milestone': f"💰 ${data['profit']:+.0f} profit milestone!",
            'high_confidence_win': f"⭐ High confidence pick won! ({data['confidence']:.1%})",
            'daily_perfect': f"🏆 Perfect day! {data['wins']}/{data['total']} picks correct!"
        }
        
        title = "🎉 Achievement Unlocked!"
        message = milestone_messages.get(milestone_type, "New milestone reached!")
        
        return self.add_notification(
            title=title,
            message=message,
            type="success",
            sound=True
        )
    
    def daily_summary_notification(self, summary_data: Dict):
        """End of day summary notification"""
        if not st.session_state.notification_settings.get('daily_summary', True):
            return
        
        wins = summary_data.get('wins', 0)
        losses = summary_data.get('losses', 0)
        total = wins + losses
        
        if total == 0:
            return
        
        accuracy = wins / total * 100
        profit = summary_data.get('profit', 0)
        
        title = "📊 Daily Summary"
        message = f"{wins}-{losses} record ({accuracy:.1f}% accuracy)"
        
        if profit > 0:
            message += f" • +${profit:.0f} profit 💰"
            notification_type = "success"
        elif profit < 0:
            message += f" • ${profit:.0f} loss 📉"
            notification_type = "warning"
        else:
            message += " • Break even"
            notification_type = "info"
        
        action_button = {
            'text': 'View Full Report',
            'action': 'show_daily_report',
            'data': summary_data
        }
        
        return self.add_notification(
            title=title,
            message=message,
            type=notification_type,
            action_button=action_button
        )
    
    def dismiss_notification(self, notification_id: str):
        """Dismiss a specific notification"""
        for notif in st.session_state.notifications:
            if notif['id'] == notification_id:
                notif['dismissed'] = True
                break
    
    def clear_all_notifications(self):
        """Clear all notifications"""
        st.session_state.notifications = []
    
    def get_active_notifications(self, limit: int = 10) -> List[Dict]:
        """Get active (non-dismissed) notifications"""
        notifications = st.session_state.get('notifications', [])
        active = [n for n in notifications if not n.get('dismissed', False)]
        return active[:limit]
    
    def render_notification_center(self):
        """Render the notification center UI"""
        active_notifications = self.get_active_notifications()
        
        if not active_notifications:
            st.info("📭 No new notifications")
            return
        
        st.markdown("### 🔔 Recent Notifications")
        
        for notif in active_notifications:
            self._render_single_notification(notif)
    
    def _render_single_notification(self, notification: Dict):
        """Render a single notification"""
        notif_type = notification.get('type', 'info')
        
        # Choose emoji and color based on type
        type_config = {
            'success': {'emoji': '✅', 'color': 'success'},
            'error': {'emoji': '❌', 'color': 'error'},
            'warning': {'emoji': '⚠️', 'color': 'warning'},
            'info': {'emoji': 'ℹ️', 'color': 'info'},
            'game_finish': {'emoji': '🏆', 'color': 'info'},
            'pick_result': {'emoji': '🎯', 'color': 'success'}
        }
        
        config = type_config.get(notif_type, type_config['info'])
        
        with st.container():
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            
            with col1:
                st.markdown(f"## {config['emoji']}")
            
            with col2:
                st.markdown(f"**{notification['title']}**")
                st.markdown(notification['message'])
                
                # Show timestamp
                timestamp = datetime.fromisoformat(notification['timestamp'])
                time_ago = self._time_ago(timestamp)
                st.caption(f"🕐 {time_ago}")
                
                # Action button if available
                action_button = notification.get('action_button')
                if action_button:
                    if st.button(action_button['text'], key=f"action_{notification['id']}"):
                        self._handle_notification_action(action_button)
            
            with col3:
                if st.button("✕", key=f"dismiss_{notification['id']}", help="Dismiss"):
                    self.dismiss_notification(notification['id'])
                    st.rerun()
            
            st.markdown("---")
    
    def render_floating_notifications(self):
        """Render floating notifications (for real-time alerts)"""
        active_notifications = self.get_active_notifications(limit=3)
        
        if not active_notifications:
            return
        
        # CSS for floating notifications
        st.markdown("""
        <style>
        .floating-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            z-index: 9999;
            max-width: 350px;
            animation: slideInNotification 0.5s ease-out;
        }
        
        .notification-success {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        }
        
        .notification-error {
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        }
        
        .notification-warning {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        }
        
        @keyframes slideInNotification {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        .notification-title {
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .notification-message {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .notification-dismiss {
            position: absolute;
            top: 5px;
            right: 10px;
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            font-size: 1.2rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Show most recent notification as floating
        if active_notifications:
            latest = active_notifications[0]
            notif_type = latest.get('type', 'info')
            
            notification_html = f"""
            <div class="floating-notification notification-{notif_type}" id="floating-notif-{latest['id']}">
                <button class="notification-dismiss" onclick="document.getElementById('floating-notif-{latest['id']}').style.display='none'">×</button>
                <div class="notification-title">{latest['title']}</div>
                <div class="notification-message">{latest['message']}</div>
            </div>
            """
            
            st.markdown(notification_html, unsafe_allow_html=True)
            
            # Auto-dismiss after timeout
            if latest.get('auto_dismiss', True):
                # Ensure settings exist for this session
                settings = st.session_state.get('notification_settings')
                if not isinstance(settings, dict):
                    settings = {
                        'game_finish': True,
                        'pick_results': True,
                        'performance_milestones': True,
                        'daily_summary': True,
                        'sound_enabled': True,
                        'auto_dismiss': 5,
                    }
                    st.session_state.notification_settings = settings
                timeout = settings.get('auto_dismiss', 5)
                st.markdown(f"""
                <script>
                setTimeout(function() {{
                    var elem = document.getElementById('floating-notif-{latest['id']}');
                    if (elem) elem.style.display = 'none';
                }}, {timeout * 1000});
                </script>
                """, unsafe_allow_html=True)
    
    def _time_ago(self, timestamp: datetime) -> str:
        """Calculate human-readable time ago"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    def _handle_notification_action(self, action_button: Dict):
        """Handle notification action button clicks"""
        action = action_button.get('action')
        data = action_button.get('data', {})
        
        if action == 'navigate_to_win_tracker':
            st.session_state.current_page = 'portfolio'
            st.rerun()
        elif action == 'show_game_details':
            st.session_state.selected_game_details = data
            st.rerun()
        elif action == 'show_daily_report':
            st.session_state.show_daily_report = data
            st.rerun()

# Global notification manager instance
notification_manager = NotificationManager()

def show_notification_settings():
    """Show notification settings panel"""
    st.markdown("### 🔔 Notification Settings")
    
    settings = st.session_state.notification_settings
    
    col1, col2 = st.columns(2)
    
    with col1:
        settings['game_finish'] = st.checkbox(
            "🏆 Game Finish Alerts", 
            value=settings.get('game_finish', True),
            help="Notify when games finish with scores"
        )
        
        settings['pick_results'] = st.checkbox(
            "🎯 Pick Result Alerts", 
            value=settings.get('pick_results', True),
            help="Notify when your picks win or lose"
        )
    
    with col2:
        settings['performance_milestones'] = st.checkbox(
            "🎉 Achievement Alerts", 
            value=settings.get('performance_milestones', True),
            help="Notify for win streaks, accuracy milestones"
        )
        
        settings['daily_summary'] = st.checkbox(
            "📊 Daily Summary", 
            value=settings.get('daily_summary', True),
            help="End of day performance summary"
        )
    
    settings['auto_dismiss'] = st.slider(
        "⏱️ Auto-dismiss after (seconds)", 
        min_value=3, 
        max_value=15, 
        value=settings.get('auto_dismiss', 5),
        help="How long notifications stay visible"
    )
    
    st.session_state.notification_settings = settings
    
    # Test notification button
    if st.button("🧪 Test Notification"):
        notification_manager.add_notification(
            title="🧪 Test Notification",
            message="This is a test notification to preview your settings!",
            type="success",
            sound=True
        )
        st.success("Test notification sent!")

def add_notification_to_page():
    """Add floating notifications to any page"""
    notification_manager.render_floating_notifications()

