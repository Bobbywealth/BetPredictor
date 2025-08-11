"""
Automated Daily Picks Generation and Accuracy Tracking System
Generates picks automatically and tracks performance over time
"""

import streamlit as st
import schedule
import time
import threading
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List
import logging

class AutomatedPicksScheduler:
    """
    Handles automated daily pick generation and performance tracking
    """
    
    def __init__(self):
        self.picks_history_file = "data/daily_picks_history.json"
        self.performance_file = "data/ai_performance_tracking.json"
        self.last_generation_file = "data/last_pick_generation.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            filename='data/automated_picks.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        self.is_running = False
        self.scheduler_thread = None

    def should_generate_picks_today(self) -> bool:
        """Check if picks should be generated today"""
        
        try:
            if not os.path.exists(self.last_generation_file):
                return True
            
            with open(self.last_generation_file, 'r') as f:
                last_gen = json.load(f)
            
            last_date = datetime.fromisoformat(last_gen.get('date', '2000-01-01'))
            today = datetime.now().date()
            
            # Generate if we haven't generated today
            return last_date.date() < today
            
        except Exception as e:
            logging.error(f"Error checking last generation: {e}")
            return True

    def generate_daily_picks(self):
        """Generate picks for today automatically"""
        
        try:
            if not self.should_generate_picks_today():
                logging.info("Picks already generated today, skipping...")
                return
            
            logging.info("Starting automated daily pick generation...")
            
            # Import the necessary modules
            from utils.enhanced_ai_analyzer import EnhancedAIAnalyzer
            from utils.sports_apis import get_espn_games_for_date
            
            # Initialize the AI analyzer
            analyzer = EnhancedAIAnalyzer()
            
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Fetch games for today
            all_games = []
            sports = ['nba', 'nfl', 'mlb', 'nhl', 'ncaaf', 'ncaab']
            
            for sport in sports:
                try:
                    games = get_espn_games_for_date(today, sport)
                    if games:
                        all_games.extend(games)
                        logging.info(f"Found {len(games)} {sport.upper()} games for {today}")
                except Exception as e:
                    logging.warning(f"Error fetching {sport} games: {e}")
            
            if not all_games:
                logging.info("No games found for today, skipping pick generation")
                return
            
            # Generate AI analysis for each game
            daily_picks = []
            
            for game in all_games[:10]:  # Limit to top 10 games to avoid overload
                try:
                    # Analyze game with enhanced AI
                    analysis = analyzer.analyze_game_enhanced(game)
                    
                    if analysis and not analysis.get('error'):
                        # Create pick record
                        pick_record = {
                            'date': today,
                            'game_id': f"{game.get('away_team', {}).get('name', 'Away')}_{game.get('home_team', {}).get('name', 'Home')}_{today}",
                            'sport': game.get('sport', 'Unknown'),
                            'matchup': f"{game.get('away_team', {}).get('name', 'Away')} @ {game.get('home_team', {}).get('name', 'Home')}",
                            'predicted_winner': analysis.get('predicted_winner'),
                            'confidence': analysis.get('confidence', 0.0),
                            'recommendation_tier': analysis.get('recommendation_tier', 'MODERATE_PLAY'),
                            'expected_value': analysis.get('expected_value', 0.0),
                            'ai_reasoning': analysis.get('key_factors', [])[:3],  # Top 3 factors
                            'data_quality': analysis.get('data_quality_score', 0.8),
                            'calibrated_confidence': analysis.get('confidence', 0.0),
                            'reliability_score': analysis.get('reliability_score', 0.8),
                            'status': 'pending',  # pending, won, lost, push
                            'actual_winner': None,
                            'final_score': None,
                            'generated_at': datetime.now().isoformat()
                        }
                        
                        daily_picks.append(pick_record)
                        
                except Exception as e:
                    logging.error(f"Error analyzing game {game}: {e}")
            
            if daily_picks:
                # Save picks to history
                self.save_daily_picks(daily_picks)
                
                # Update last generation timestamp
                with open(self.last_generation_file, 'w') as f:
                    json.dump({
                        'date': datetime.now().isoformat(),
                        'picks_generated': len(daily_picks),
                        'sports_covered': list(set(pick['sport'] for pick in daily_picks))
                    }, f, indent=2)
                
                logging.info(f"Successfully generated {len(daily_picks)} automated picks for {today}")
                
                # Update Streamlit session state if available
                if hasattr(st, 'session_state'):
                    st.session_state['automated_picks_generated'] = True
                    st.session_state['last_automated_picks'] = daily_picks
            
        except Exception as e:
            logging.error(f"Error in automated pick generation: {e}")

    def save_daily_picks(self, picks: List[Dict]):
        """Save daily picks to history file"""
        
        try:
            # Load existing history
            history = []
            if os.path.exists(self.picks_history_file):
                with open(self.picks_history_file, 'r') as f:
                    history = json.load(f)
            
            # Add new picks
            history.extend(picks)
            
            # Keep only last 90 days of picks
            cutoff_date = (datetime.now() - timedelta(days=90)).date()
            history = [pick for pick in history if datetime.fromisoformat(pick['generated_at']).date() >= cutoff_date]
            
            # Save updated history
            with open(self.picks_history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving daily picks: {e}")

    def get_picks_for_date(self, date_str: str) -> List[Dict]:
        """Get picks for a specific date"""
        
        try:
            if not os.path.exists(self.picks_history_file):
                return []
            
            with open(self.picks_history_file, 'r') as f:
                history = json.load(f)
            
            return [pick for pick in history if pick['date'] == date_str]
            
        except Exception as e:
            logging.error(f"Error getting picks for date {date_str}: {e}")
            return []

    def update_pick_results(self, date_str: str):
        """Update pick results with actual game outcomes"""
        
        try:
            from utils.result_scorer import ResultScorer
            
            scorer = ResultScorer()
            picks = self.get_picks_for_date(date_str)
            
            if not picks:
                return
            
            # Get final scores for the date
            final_scores = scorer.get_final_scores_for_date(date_str)
            
            # Update pick results
            updated_picks = []
            for pick in picks:
                # Find matching game in final scores
                game_match = None
                for score_game in final_scores:
                    if (pick['matchup'].lower() in f"{score_game.get('away_team', '')} @ {score_game.get('home_team', '')}".lower()):
                        game_match = score_game
                        break
                
                if game_match and game_match.get('status') == 'completed':
                    # Determine actual winner
                    home_score = game_match.get('home_score', 0)
                    away_score = game_match.get('away_score', 0)
                    home_team = game_match.get('home_team', '')
                    away_team = game_match.get('away_team', '')
                    
                    if home_score > away_score:
                        actual_winner = home_team
                    elif away_score > home_score:
                        actual_winner = away_team
                    else:
                        actual_winner = 'TIE'
                    
                    # Update pick
                    pick['actual_winner'] = actual_winner
                    pick['final_score'] = f"{away_team} {away_score} - {home_team} {home_score}"
                    
                    # Determine if pick was correct
                    if actual_winner == 'TIE':
                        pick['status'] = 'push'
                    elif pick['predicted_winner'] == actual_winner:
                        pick['status'] = 'won'
                    else:
                        pick['status'] = 'lost'
                    
                    pick['scored_at'] = datetime.now().isoformat()
                
                updated_picks.append(pick)
            
            # Save updated picks
            if os.path.exists(self.picks_history_file):
                with open(self.picks_history_file, 'r') as f:
                    all_history = json.load(f)
                
                # Replace picks for this date
                all_history = [p for p in all_history if p['date'] != date_str]
                all_history.extend(updated_picks)
                
                with open(self.picks_history_file, 'w') as f:
                    json.dump(all_history, f, indent=2)
                
                logging.info(f"Updated results for {len(updated_picks)} picks on {date_str}")
                
        except Exception as e:
            logging.error(f"Error updating pick results for {date_str}: {e}")

    def get_performance_stats(self, days: int = 30) -> Dict:
        """Get AI performance statistics"""
        
        try:
            if not os.path.exists(self.picks_history_file):
                return self._default_performance_stats()
            
            with open(self.picks_history_file, 'r') as f:
                history = json.load(f)
            
            # Filter to last N days
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            recent_picks = [
                pick for pick in history 
                if datetime.fromisoformat(pick['generated_at']).date() >= cutoff_date
                and pick['status'] in ['won', 'lost']  # Exclude pending and pushes
            ]
            
            if not recent_picks:
                return self._default_performance_stats()
            
            # Calculate stats
            total_picks = len(recent_picks)
            wins = len([p for p in recent_picks if p['status'] == 'won'])
            accuracy = wins / total_picks if total_picks > 0 else 0
            
            # High confidence picks (80%+)
            high_conf_picks = [p for p in recent_picks if p.get('calibrated_confidence', 0) >= 0.8]
            high_conf_wins = len([p for p in high_conf_picks if p['status'] == 'won'])
            high_conf_accuracy = high_conf_wins / len(high_conf_picks) if high_conf_picks else 0
            
            # By sport breakdown
            sport_stats = {}
            for sport in set(pick['sport'] for pick in recent_picks):
                sport_picks = [p for p in recent_picks if p['sport'] == sport]
                sport_wins = len([p for p in sport_picks if p['status'] == 'won'])
                sport_stats[sport] = {
                    'picks': len(sport_picks),
                    'wins': sport_wins,
                    'accuracy': sport_wins / len(sport_picks) if sport_picks else 0
                }
            
            # ROI calculation (simplified)
            total_expected_value = sum(pick.get('expected_value', 0) for pick in recent_picks)
            avg_expected_value = total_expected_value / total_picks if total_picks > 0 else 0
            
            return {
                'total_picks': total_picks,
                'wins': wins,
                'losses': total_picks - wins,
                'accuracy': accuracy,
                'high_confidence_picks': len(high_conf_picks),
                'high_confidence_accuracy': high_conf_accuracy,
                'avg_expected_value': avg_expected_value,
                'sport_breakdown': sport_stats,
                'last_updated': datetime.now().isoformat(),
                'period_days': days
            }
            
        except Exception as e:
            logging.error(f"Error calculating performance stats: {e}")
            return self._default_performance_stats()

    def _default_performance_stats(self) -> Dict:
        """Return default performance stats when no data available"""
        return {
            'total_picks': 0,
            'wins': 0,
            'losses': 0,
            'accuracy': 0.0,
            'high_confidence_picks': 0,
            'high_confidence_accuracy': 0.0,
            'avg_expected_value': 0.0,
            'sport_breakdown': {},
            'last_updated': datetime.now().isoformat(),
            'period_days': 30
        }

    def start_automated_scheduling(self):
        """Start the automated scheduling system"""
        
        if self.is_running:
            return
        
        # Schedule daily pick generation at 6 AM
        schedule.every().day.at("06:00").do(self.generate_daily_picks)
        
        # Schedule result updates at 11 PM (after games finish)
        schedule.every().day.at("23:00").do(lambda: self.update_pick_results(
            (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        ))
        
        self.is_running = True
        
        # Run scheduler in background thread
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logging.info("Automated picks scheduler started")

    def stop_automated_scheduling(self):
        """Stop the automated scheduling system"""
        self.is_running = False
        schedule.clear()
        logging.info("Automated picks scheduler stopped")

    def force_generate_picks(self):
        """Force generate picks now (for testing)"""
        self.generate_daily_picks()

    def get_todays_automated_picks(self) -> List[Dict]:
        """Get today's automated picks if they exist"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_picks_for_date(today)
