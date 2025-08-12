import os
import json
import logging
from datetime import datetime, date
from typing import Dict, List, Optional
import pandas as pd
import streamlit as st

# OpenAI integration
from openai import OpenAI

# Gemini integration
try:
    import google.generativeai as genai  # type: ignore
    GENAI_AVAILABLE = True
except Exception:
    genai = None  # type: ignore
    GENAI_AVAILABLE = False
from pydantic import BaseModel

# Claude (Anthropic) integration
try:
    import anthropic  # type: ignore
    ANTHROPIC_AVAILABLE = True
except Exception:
    anthropic = None  # type: ignore
    ANTHROPIC_AVAILABLE = False

class GamePrediction(BaseModel):
    """Structured prediction model"""
    predicted_winner: str
    confidence: float  # 0.0 to 1.0
    predicted_score_home: int
    predicted_score_away: int
    key_factors: List[str]
    risk_level: str  # "LOW", "MEDIUM", "HIGH"

def _get_secret_or_env(*keys: str) -> Optional[str]:
    """Lookup helper: prefer Streamlit secrets, then environment variables."""
    for key in keys:
        try:
            if key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass
        if os.environ.get(key):
            return os.environ.get(key)
    return None


class AIGameAnalyzer:
    """AI-powered game analysis using OpenAI, Gemini, and Claude"""
    
    def __init__(self):
        # Initialize OpenAI first (primary AI)
        self.openai_client = None
        openai_key = _get_secret_or_env("OPENAI_API_KEY")
        if openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                if st.session_state.get('debug_mode', False):
                    st.success("✅ OpenAI (Primary AI) initialized successfully")
            except Exception as e:
                st.error(f"❌ OpenAI initialization failed: {e}")
        else:
            st.warning("⚠️ OpenAI API key not found - primary AI unavailable")
        
        # Initialize Gemini second (enhancement AI)
        self.gemini_client = None
        gemini_key = _get_secret_or_env("GOOGLE_API_KEY", "GEMINI_API_KEY")
        if gemini_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_key)
                self.gemini_client = True
                if st.session_state.get('debug_mode', False):
                    st.success("✅ Gemini (Enhancement AI) initialized successfully")
            except Exception as e:
                if st.session_state.get('debug_mode', False):
                    st.warning(f"⚠️ Gemini initialization failed: {e}")
        elif gemini_key and not GENAI_AVAILABLE:
            if st.session_state.get('debug_mode', False):
                st.info("ℹ️ Gemini SDK not available; continuing with OpenAI-only analysis")
        else:
            if st.session_state.get('debug_mode', False):
                st.info("ℹ️ Gemini API key not found - enhancement AI unavailable")
        
        # Initialize Claude (third model - auditor/consensus)
        self.claude_client = None
        claude_key = _get_secret_or_env("ANTHROPIC_API_KEY")
        if claude_key and ANTHROPIC_AVAILABLE:
            try:
                self.claude_client = anthropic.Anthropic(api_key=claude_key)
                if st.session_state.get('debug_mode', False):
                    st.success("✅ Claude (Anthropic) initialized successfully")
            except Exception as e:
                if st.session_state.get('debug_mode', False):
                    st.warning(f"⚠️ Claude initialization failed: {e}")
        elif claude_key and not ANTHROPIC_AVAILABLE:
            if st.session_state.get('debug_mode', False):
                st.info("ℹ️ Anthropic SDK not available; continuing without Claude")
        
    def analyze_game_with_openai(self, game_data: Dict) -> Dict:
        """Analyze game using OpenAI GPT-4o"""
        try:
            if not self.openai_client:
                return {"error": "OpenAI not configured"}
            home_team = game_data.get('home_team', {}).get('name', 'Unknown')
            away_team = game_data.get('away_team', {}).get('name', 'Unknown')
            sport = game_data.get('sport', 'Unknown')
            league = game_data.get('league', 'Unknown')
            game_date = game_data.get('date', 'Unknown')
            
            prompt = f"""
            Analyze this upcoming {sport} game in {league}:
            
            **Game**: {away_team} at {home_team}
            **Date**: {game_date}
            **Sport**: {sport} ({league})
            
            Provide a comprehensive analysis including:
            1. Team strengths and weaknesses
            2. Head-to-head history insights
            3. Key players to watch
            4. Predicted outcome with confidence level
            5. Betting recommendation (if applicable)
            6. Risk assessment
            
            Format your response as JSON with these fields:
            {{
                "analysis": "detailed analysis text",
                "predicted_winner": "team name",
                "confidence": 0.75,
                "key_factors": ["factor1", "factor2", "factor3"],
                "risk_level": "MEDIUM",
                "betting_insight": "insight text"
            }}
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert sports analyst with deep knowledge of team statistics, player performance, and game predictions."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                result['ai_source'] = 'OpenAI GPT-4o'
                return result
            else:
                return {"error": "Empty response from OpenAI", "ai_source": "OpenAI GPT-4o"}
            
        except Exception as e:
            return {
                "error": f"OpenAI analysis failed: {str(e)}",
                "ai_source": "OpenAI GPT-4o"
            }
    
    def analyze_game_with_gemini(self, game_data: Dict) -> Dict:
        """Analyze game using Google Gemini"""
        try:
            if not GENAI_AVAILABLE or not self.gemini_client:
                return {"error": "Gemini SDK not available"}
            home_team = game_data.get('home_team', {}).get('name', 'Unknown')
            away_team = game_data.get('away_team', {}).get('name', 'Unknown')
            sport = game_data.get('sport', 'Unknown')
            league = game_data.get('league', 'Unknown')
            game_date = game_data.get('date', 'Unknown')
            
            prompt = f"""
            As a professional sports analyst, analyze this {sport} matchup:
            
            Game: {away_team} @ {home_team}
            League: {league}
            Date: {game_date}
            
            Provide analysis in JSON format:
            {{
                "team_analysis": "comparison of both teams",
                "prediction": "predicted winner",
                "confidence_score": 0.80,
                "score_prediction": "predicted final score",
                "critical_factors": ["factor1", "factor2"],
                "recommendation": "betting/viewing recommendation"
            }}
            """
            
            if not GENAI_AVAILABLE:
                return {"error": "Gemini SDK not available"}
            model = genai.GenerativeModel(model_name="gemini-2.5-pro", system_instruction="You are an expert sports analyst specializing in game predictions and team analysis.")
            response = model.generate_content(prompt)
            
            response_text = response.text if response.text else ""
            if response_text:
                result = json.loads(response_text)
                result['ai_source'] = 'Google Gemini'
                return result
            else:
                return {"error": "Empty response from Gemini", "ai_source": "Google Gemini"}
                
        except Exception as e:
            return {
                "error": f"Gemini analysis failed: {str(e)}",
                "ai_source": "Google Gemini"
            }

    def analyze_game_with_claude(self, game_data: Dict) -> Dict:
        """Analyze game using Claude 3.5 Sonnet with strict JSON output"""
        try:
            if not ANTHROPIC_AVAILABLE or not self.claude_client:
                return {"error": "Claude SDK not available"}
            home_team = game_data.get('home_team', {}).get('name', 'Unknown')
            away_team = game_data.get('away_team', {}).get('name', 'Unknown')
            sport = game_data.get('sport', 'Unknown')
            league = game_data.get('league', 'Unknown')
            game_date = game_data.get('date', 'Unknown')

            prompt = (
                "You are an elite quantitative sports bettor. Analyze the matchup and return STRICT JSON only.\n"
                f"Game: {away_team} @ {home_team}\n"
                f"League: {league}  Date: {game_date}\n"
                "JSON schema:{\n"
                "  \"predicted_winner\": \"Team Name\",\n"
                "  \"confidence\": 0.0,\n"
                "  \"key_factors\": [\"...\", \"...\"],\n"
                "  \"risk_level\": \"LOW|MEDIUM|HIGH\",\n"
                "  \"edge_score\": 0.0\n"
                "}"
            )

            msg = self.claude_client.messages.create(
                model="claude-3.5-sonnet-20240620",
                max_tokens=700,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )

            text = "".join([b.text for b in getattr(msg, 'content', []) if hasattr(b, 'text')])
            if text:
                try:
                    # Extract JSON payload if wrapped
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    payload = text[start:end]
                    result = json.loads(payload)
                except Exception:
                    result = {"error": "Claude returned non-JSON"}
                if 'error' not in result:
                    result['ai_source'] = 'Claude 3.5 Sonnet'
                return result
            return {"error": "Empty response from Claude", "ai_source": "Claude"}
        except Exception as e:
            return {"error": f"Claude analysis failed: {str(e)}", "ai_source": "Claude"}
    
    def get_game_recommendations(self, games_df: pd.DataFrame, user_preferences: Dict = None) -> List[Dict]:
        """Get AI-powered game recommendations"""
        try:
            if len(games_df) == 0:
                return []
            
            # Prepare games summary for AI
            games_summary = []
            for idx, game in games_df.head(10).iterrows():  # Limit to first 10 games
                games_summary.append({
                    'game': f"{game.get('away_team', {}).get('name', 'Unknown')} at {game.get('home_team', {}).get('name', 'Unknown')}",
                    'sport': game.get('sport', 'Unknown'),
                    'league': game.get('league', 'Unknown'),
                    'time': game.get('time', 'TBD')
                })
            
            prompt = f"""
            Based on these available games today, recommend the top 5 most interesting games to watch:
            
            {json.dumps(games_summary, indent=2)}
            
            Consider factors like:
            - Competitive matchups
            - Star players
            - Playoff implications
            - Historical rivalries
            - Entertainment value
            
            Return JSON with recommendations:
            {{
                "top_games": [
                    {{
                        "game": "Team A vs Team B",
                        "reason": "why this game is interesting",
                        "excitement_level": 9
                    }}
                ]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a sports entertainment expert who knows what makes games exciting for fans."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result.get('top_games', [])
            else:
                return []
            
        except Exception as e:
            return [{"error": f"Recommendations failed: {str(e)}"}]
    
    def enhanced_game_discovery(self, date_str: str, sport_filter: str = None) -> Dict:
        """AI-enhanced game discovery for specific dates"""
        try:
            prompt = f"""
            Help find the most interesting sports games on {date_str}.
            {f"Focus on {sport_filter} games." if sport_filter else "Include all major sports."}
            
            Consider:
            - Major league games (NFL, NBA, MLB, NHL, WNBA, MLS)
            - College sports if relevant
            - International competitions
            - Playoff or championship games
            - Key matchups and rivalries
            
            Return suggestions in JSON format:
            {{
                "search_suggestions": [
                    {{
                        "sport": "basketball",
                        "league": "NBA",
                        "why_interesting": "reason",
                        "search_terms": ["term1", "term2"]
                    }}
                ],
                "date_context": "what's special about this date in sports"
            }}
            """
            
            if not GENAI_AVAILABLE:
                return {"error": "Gemini SDK not available"}
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")
            response = model.generate_content(prompt)
            
            response_text = response.text if response.text else ""
            if response_text:
                # Parse response (may not be perfect JSON)
                return {"suggestions": response_text, "ai_source": "Gemini"}
            else:
                return {"suggestions": "No specific suggestions available", "ai_source": "Gemini"}
                
        except Exception as e:
            return {"error": f"Game discovery failed: {str(e)}", "ai_source": "Gemini"}
    
    def generate_betting_insights(self, game_data: Dict) -> Dict:
        """Generate responsible betting insights"""
        try:
            home_team = game_data.get('home_team', {}).get('name', 'Unknown')
            away_team = game_data.get('away_team', {}).get('name', 'Unknown')
            
            prompt = f"""
            Provide responsible betting analysis for: {away_team} at {home_team}
            
            Important: Include gambling responsibility warnings and focus on entertainment value.
            
            Analyze:
            1. Team form and recent performance
            2. Statistical trends
            3. Potential value bets (educational only)
            4. Risk factors to consider
            
            Return JSON:
            {{
                "analysis": "statistical analysis",
                "risk_factors": ["factor1", "factor2"],
                "educational_insights": "learning points",
                "responsible_gambling_note": "warning about gambling risks"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a responsible sports analyst who emphasizes entertainment and education over gambling. Always include gambling warnings."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=700
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                result['ai_source'] = 'OpenAI GPT-4o'
            else:
                result = {"error": "Empty response from OpenAI", "ai_source": "OpenAI GPT-4o"}
            
            # Ensure responsible gambling message is included
            if 'responsible_gambling_note' not in result:
                result['responsible_gambling_note'] = "⚠️ Sports betting involves risk. Only bet what you can afford to lose. This analysis is for entertainment and educational purposes only."
            
            return result
            
        except Exception as e:
            return {
                "error": f"Betting insights failed: {str(e)}",
                "responsible_gambling_note": "⚠️ Sports betting involves risk. Please gamble responsibly.",
                "ai_source": "OpenAI GPT-4o"
            }

class AIGameFinder:
    """AI-powered game discovery and search"""
    
    def __init__(self):
        self.analyzer = AIGameAnalyzer()
    
    def smart_game_search(self, query: str, available_games: pd.DataFrame) -> List[Dict]:
        """Use AI to interpret search queries and find relevant games"""
        try:
            if len(available_games) == 0:
                return []
            
            # Convert games to searchable format
            games_info = []
            for idx, game in available_games.iterrows():
                games_info.append({
                    'id': idx,
                    'teams': f"{game.get('away_team', {}).get('name', '')} vs {game.get('home_team', {}).get('name', '')}",
                    'sport': game.get('sport', ''),
                    'league': game.get('league', ''),
                    'date': game.get('date', ''),
                    'time': game.get('time', '')
                })
            
            prompt = f"""
            User search query: "{query}"
            
            Available games:
            {json.dumps(games_info[:20], indent=2)}
            
            Find games that match the user's intent. They might be searching for:
            - Specific teams
            - Sports or leagues
            - Game types or matchups
            - Time preferences
            
            Return matching game IDs and reasons:
            {{
                "matches": [
                    {{
                        "game_id": 0,
                        "relevance_score": 0.9,
                        "match_reason": "why this game matches the query"
                    }}
                ]
            }}
            """
            
            response = self.analyzer.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a sports search expert who understands user intent and matches it to available games."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
                return result.get('matches', [])
            else:
                return []
            
        except Exception as e:
            return [{"error": f"Smart search failed: {str(e)}"}]