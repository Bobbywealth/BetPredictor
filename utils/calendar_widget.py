import streamlit as st
import calendar
from datetime import datetime, date, timedelta
import pandas as pd

class SportsCalendarWidget:
    """Interactive calendar widget for sports game selection"""
    
    def __init__(self, live_games_manager):
        self.games_manager = live_games_manager
    
    def render_monthly_calendar(self, selected_date=None):
        """Render an interactive monthly calendar with game counts"""
        if not selected_date:
            selected_date = date.today()
        
        # Calendar navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Previous Month"):
                if selected_date.month == 1:
                    new_date = selected_date.replace(year=selected_date.year - 1, month=12, day=1)
                else:
                    new_date = selected_date.replace(month=selected_date.month - 1, day=1)
                st.session_state['calendar_date'] = new_date
                st.rerun()
        
        with col2:
            st.markdown(f"### {calendar.month_name[selected_date.month]} {selected_date.year}")
        
        with col3:
            if st.button("Next Month →"):
                if selected_date.month == 12:
                    new_date = selected_date.replace(year=selected_date.year + 1, month=1, day=1)
                else:
                    new_date = selected_date.replace(month=selected_date.month + 1, day=1)
                st.session_state['calendar_date'] = new_date
                st.rerun()
        
        # Get monthly games data
        monthly_games = self.games_manager.get_monthly_calendar_games(
            selected_date.year, 
            selected_date.month
        )
        
        # Create games count by date
        games_by_date = {}
        if len(monthly_games) > 0:
            games_by_date = monthly_games.groupby('date').size().to_dict()
        
        # Generate calendar grid
        cal = calendar.monthcalendar(selected_date.year, selected_date.month)
        
        # Calendar headers
        st.markdown("**Sun | Mon | Tue | Wed | Thu | Fri | Sat**")
        
        # Calendar grid
        for week in cal:
            week_cols = st.columns(7)
            for i, day in enumerate(week):
                with week_cols[i]:
                    if day == 0:
                        st.write("")  # Empty cell for days not in month
                    else:
                        day_date = date(selected_date.year, selected_date.month, day)
                        day_str = f"{selected_date.year}-{selected_date.month:02d}-{day:02d}"
                        game_count = games_by_date.get(day_str, 0)
                        
                        # Style the day based on games
                        if game_count > 0:
                            if st.button(f"**{day}**\n{game_count} games", key=f"cal_{day}"):
                                st.session_state['selected_date'] = day_date
                                return day_date
                        else:
                            if st.button(f"{day}", key=f"cal_{day}"):
                                st.session_state['selected_date'] = day_date
                                return day_date
        
        return selected_date
    
    def render_date_selector(self):
        """Render a simple date selector"""
        st.markdown("### 📅 Select Date")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_date = st.date_input(
                "Choose date for games",
                value=st.session_state.get('selected_date', date.today()),
                min_value=date.today() - timedelta(days=30),
                max_value=date.today() + timedelta(days=365)
            )
        
        with col2:
            if st.button("🔄 Refresh Games", type="primary"):
                st.session_state['games_refreshed'] = True
        
        # Quick date buttons
        st.markdown("**Quick Select:**")
        quick_cols = st.columns(4)
        
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        quick_dates = [
            ("Today", today),
            ("Tomorrow", tomorrow),
            ("Next Week", next_week),
            ("This Weekend", today + timedelta(days=(5-today.weekday()) % 7))
        ]
        
        for i, (label, quick_date) in enumerate(quick_dates):
            with quick_cols[i]:
                if st.button(label, key=f"quick_{label}"):
                    st.session_state['selected_date'] = quick_date
                    selected_date = quick_date
                    st.rerun()
        
        return selected_date
    
    def show_date_games_summary(self, selected_date, games_df):
        """Show summary of games for selected date"""
        if len(games_df) == 0:
            st.info(f"No games scheduled for {selected_date.strftime('%B %d, %Y')}")
            return
        
        # Group by sport/league
        games_summary = games_df.groupby(['sport', 'league']).size().reset_index(name='count')
        
        st.markdown(f"### Games for {selected_date.strftime('%B %d, %Y')}")
        
        for _, row in games_summary.iterrows():
            sport_emoji = {
                'basketball': '🏀',
                'baseball': '⚾',
                'football': '🏈',
                'hockey': '🏒',
                'soccer': '⚽'
            }.get(row['sport'], '🏆')
            
            st.markdown(f"{sport_emoji} **{row['sport'].title()} ({row['league']})**: {row['count']} games")