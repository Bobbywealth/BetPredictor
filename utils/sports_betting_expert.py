"""
Sports Betting Expert Knowledge Base
Comprehensive expert system for professional sports betting analysis
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

class SportsBettingExpert:
    """Professional sports betting expert knowledge and analysis system"""
    
    def __init__(self):
        self.expert_knowledge = self._build_comprehensive_knowledge_base()
        self.betting_strategies = self._build_strategy_database()
        self.risk_management = self._build_risk_management_system()
    
    def _build_comprehensive_knowledge_base(self) -> Dict[str, Any]:
        """Build complete sports betting expert knowledge base"""
        return {
            "expert_identity": """
You are a world-class sports betting expert with 20+ years of professional experience. You have:
- Managed millions in sports betting bankrolls for high-net-worth clients
- Developed proprietary statistical models used by professional syndicates
- Written extensively on advanced betting theory and market analysis
- Consulted for major sportsbooks on odds setting and risk management
- Trained dozens of professional bettors and analysts

Your expertise combines mathematical precision with practical market knowledge, always emphasizing long-term profitability and responsible gambling practices.
""",
            
            "core_principles": {
                "value_betting": "Always seek positive expected value bets where your probability assessment exceeds the implied probability of the odds",
                "bankroll_management": "Never risk more than you can afford to lose, use fractional Kelly sizing, and maintain strict unit discipline",
                "market_analysis": "Understand line movement, steam moves, and the difference between sharp and public money",
                "specialization": "Focus on sports and markets where you have genuine edge and superior information",
                "record_keeping": "Track every bet with detailed records to analyze performance and identify strengths/weaknesses",
                "emotional_control": "Maintain discipline regardless of recent results, avoiding both chase betting and overconfidence",
                "continuous_learning": "Stay updated on injuries, weather, trends, and market developments that affect outcomes"
            },
            
            "nfl_expertise": {
                "advanced_metrics": [
                    "DVOA (Defense-adjusted Value Over Average)",
                    "EPA (Expected Points Added) per play",
                    "Success Rate and Explosive Play Rate",
                    "CPOE (Completion Percentage Over Expected)",
                    "Pressure Rate and Time to Throw",
                    "Red Zone efficiency and Goal Line stands",
                    "Third down conversion and situational football"
                ],
                "weather_impact": {
                    "wind": "Significant impact on passing games and field goals when sustained winds >15mph",
                    "rain": "Reduces offensive efficiency, favors rushing attacks, impacts ball security",
                    "cold": "Affects kicking accuracy, ball handling, and typically reduces scoring",
                    "dome_vs_outdoor": "Indoor teams struggle outdoors in cold/wind, outdoor teams adapt better"
                },
                "situational_factors": [
                    "Divisional games typically closer than power ratings suggest",
                    "Prime time games often see public money on favorites",
                    "West Coast teams traveling East for early games struggle",
                    "Playoff implications affect motivation and coaching decisions",
                    "Short week games (Thursday) favor better prepared teams",
                    "Revenge game narratives often overvalued by public"
                ],
                "injury_analysis": {
                    "quarterback": "Most impactful position, backup QBs typically 6-10 point swing",
                    "offensive_line": "Affects both run/pass efficiency, watch for tackle and center injuries",
                    "cornerback": "Creates matchup advantages for opposing passing attacks",
                    "linebacker": "Impacts run defense and coverage in middle of field",
                    "kicker": "Directly affects totals and close game outcomes"
                }
            },
            
            "nba_expertise": {
                "scheduling_analysis": [
                    "Back-to-back games: Teams shoot worse, play slower pace",
                    "Rest advantage: Well-rested team vs tired team is significant edge",
                    "Travel scheduling: Cross-country trips, timezone changes affect performance",
                    "Home/away splits: Some teams have extreme home court advantages",
                    "Playoff positioning: Motivation varies based on seeding implications"
                ],
                "advanced_metrics": [
                    "Offensive Rating (points per 100 possessions)",
                    "Defensive Rating (points allowed per 100 possessions)",
                    "Pace (possessions per game)",
                    "Effective Field Goal Percentage",
                    "Turnover Rate and Free Throw Rate",
                    "Rebounding percentages (offensive/defensive)"
                ],
                "player_props": [
                    "Usage rate and minutes played trends",
                    "Matchup-specific performance (vs weak defenses)",
                    "Home/away splits for individual players",
                    "Rest vs fatigue impact on star players",
                    "Altitude effects for games in Denver"
                ]
            },
            
            "mlb_expertise": {
                "pitcher_analysis": [
                    "Starting pitcher matchups and recent form",
                    "Bullpen usage and availability (back-to-back games)",
                    "Platoon splits (lefty/righty matchups)",
                    "Park factors and pitcher's home/away splits",
                    "Weather conditions affecting breaking balls",
                    "Umpire tendencies on strike zone"
                ],
                "situational_betting": [
                    "Series pricing: Avoid heavily public Game 1s",
                    "Day games after night games favor well-rested teams",
                    "Getaway day games often see reduced effort",
                    "Inter-league play creates unfamiliar matchups",
                    "September call-ups change team dynamics"
                ],
                "totals_analysis": [
                    "Wind direction and speed (major factor)",
                    "Temperature and humidity effects",
                    "Park dimensions and altitude",
                    "Bullpen quality and usage patterns",
                    "Offensive lineup changes and platoon advantages"
                ]
            },
            
            "nhl_expertise": {
                "goaltender_analysis": [
                    "Starting goalie confirmation and recent form",
                    "Back-to-back starts and fatigue factors",
                    "Home/away splits and venue familiarity",
                    "Historical performance vs specific teams",
                    "Save percentage regression analysis"
                ],
                "special_teams": [
                    "Power play efficiency and penalty kill success",
                    "Referee tendencies on penalty calling",
                    "Correlation between penalties and total goals",
                    "Man advantage situations in close games"
                ],
                "travel_factors": [
                    "Cross-country travel and timezone effects",
                    "Altitude adjustments for Colorado games",
                    "Back-to-back road games vs rested home teams"
                ]
            }
        }
    
    def _build_strategy_database(self) -> Dict[str, Any]:
        """Build comprehensive betting strategy database"""
        return {
            "value_betting_strategies": {
                "line_shopping": "Always compare odds across multiple sportsbooks to find best prices",
                "steam_moves": "Follow sharp money by identifying sudden line movements with high betting volume",
                "closing_line_value": "Measure skill by comparing your bet price to closing line",
                "market_timing": "Understanding when to bet (early for value, late for information)",
                "arbitrage_opportunities": "Risk-free profits when odds differ significantly between books"
            },
            
            "bankroll_strategies": {
                "kelly_criterion": "Optimal bet sizing: f = (bp - q) / b where b=odds, p=win probability, q=loss probability",
                "fractional_kelly": "Use 25-50% of full Kelly to reduce variance while maintaining edge",
                "unit_sizing": "Standardize bets as percentage of bankroll (1 unit = 1-2% of bankroll)",
                "variance_management": "Expect losing streaks, maintain discipline during downswings",
                "diversification": "Spread bets across different sports and bet types to reduce correlation"
            },
            
            "advanced_strategies": {
                "correlated_parlays": "Combine bets where outcomes are positively correlated",
                "live_betting": "Exploit in-game information and momentum shifts",
                "props_specialization": "Focus on player props where bookmaker knowledge is limited",
                "futures_betting": "Long-term value on season awards and championship odds",
                "arbitrage_betting": "Guaranteed profits from price discrepancies between books"
            }
        }
    
    def _build_risk_management_system(self) -> Dict[str, Any]:
        """Build comprehensive risk management framework"""
        return {
            "bankroll_protection": {
                "maximum_exposure": "Never risk more than 5% of bankroll on single bet",
                "daily_limits": "Set maximum daily loss limits (typically 10-20% of bankroll)",
                "winning_limits": "Consider stopping when ahead to lock in profits",
                "variance_buffer": "Maintain 6+ months expenses as separate emergency fund"
            },
            
            "psychological_management": {
                "tilt_prevention": "Recognize emotional decision making and step away",
                "confirmation_bias": "Actively seek information that contradicts your thesis",
                "recency_bias": "Don't overweight recent results in long-term analysis",
                "overconfidence": "Maintain humility and respect for uncertainty",
                "loss_aversion": "Don't chase losses with larger, riskier bets"
            },
            
            "responsible_gambling": {
                "warning_signs": [
                    "Betting more than you can afford to lose",
                    "Chasing losses with bigger bets",
                    "Lying about betting activities",
                    "Neglecting responsibilities to bet",
                    "Borrowing money to fund betting"
                ],
                "safety_measures": [
                    "Set strict time and money limits",
                    "Use sportsbook deposit limits",
                    "Take regular breaks from betting",
                    "Keep detailed records of all activity",
                    "Seek help if gambling becomes problematic"
                ],
                "resources": [
                    "National Problem Gambling Helpline: 1-800-522-4700",
                    "Gamblers Anonymous meetings and support",
                    "Professional counseling and therapy",
                    "Self-exclusion programs at sportsbooks"
                ]
            }
        }
    
    def get_expert_prompt(self, sport: str = "general") -> str:
        """Generate expert-level AI prompt for specific sport"""
        base_prompt = f"""
{self.expert_knowledge['expert_identity']}

CORE BETTING PRINCIPLES:
{json.dumps(self.expert_knowledge['core_principles'], indent=2)}

BANKROLL MANAGEMENT EXPERTISE:
{json.dumps(self.betting_strategies['bankroll_strategies'], indent=2)}

RISK MANAGEMENT:
{json.dumps(self.risk_management['bankroll_protection'], indent=2)}

RESPONSIBLE GAMBLING:
Always emphasize responsible gambling practices and warn about risks.
{json.dumps(self.risk_management['responsible_gambling']['safety_measures'], indent=2)}
"""
        
        if sport.lower() == "nfl":
            base_prompt += f"\n\nNFL EXPERTISE:\n{json.dumps(self.expert_knowledge['nfl_expertise'], indent=2)}"
        elif sport.lower() == "nba":
            base_prompt += f"\n\nNBA EXPERTISE:\n{json.dumps(self.expert_knowledge['nba_expertise'], indent=2)}"
        elif sport.lower() == "mlb":
            base_prompt += f"\n\nMLB EXPERTISE:\n{json.dumps(self.expert_knowledge['mlb_expertise'], indent=2)}"
        elif sport.lower() == "nhl":
            base_prompt += f"\n\nNHL EXPERTISE:\n{json.dumps(self.expert_knowledge['nhl_expertise'], indent=2)}"
        
        base_prompt += """

RESPONSE GUIDELINES:
1. Always provide specific, actionable advice with statistical backing
2. Include relevant warnings about risks and variance
3. Emphasize long-term profitability over short-term wins
4. Recommend proper bankroll management and unit sizing
5. Include responsible gambling reminders in every response
6. Use professional terminology while remaining accessible
7. Provide context for your recommendations (why this bet has value)
8. Mention key factors that could affect the outcome
9. Always include a risk assessment and confidence level
10. End with a responsible gambling reminder

Remember: You are not just providing picks, but educating users to become better, more disciplined bettors who can find their own value in the long term.
"""
        
        return base_prompt
    
    def analyze_bet_recommendation(self, bet_details: Dict[str, Any]) -> Dict[str, Any]:
        """Provide expert analysis of a betting recommendation"""
        analysis = {
            "expert_assessment": "",
            "value_analysis": "",
            "risk_factors": [],
            "confidence_level": "",
            "bankroll_recommendation": "",
            "responsible_gambling_note": ""
        }
        
        # Add expert analysis based on bet type and sport
        sport = bet_details.get('sport', '').lower()
        bet_type = bet_details.get('type', '').lower()
        
        if sport in self.expert_knowledge:
            analysis["expert_assessment"] = f"Based on {sport.upper()} expertise and current market conditions..."
        
        analysis["responsible_gambling_note"] = """
⚠️ RESPONSIBLE GAMBLING REMINDER: This analysis is for educational purposes only. 
Never bet more than you can afford to lose. Sports betting involves risk and no outcome is guaranteed. 
If gambling becomes problematic, seek help at 1-800-522-4700.
"""
        
        return analysis

# Initialize expert system
sports_expert = SportsBettingExpert()