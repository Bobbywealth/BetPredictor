"""
Enhanced AI Prompts with Real Data Integration
Improves prediction accuracy by providing structured data to AI models
"""

from typing import Dict, List
from datetime import datetime

class EnhancedAIPromptEngine:
    """Generate enhanced prompts with real-time data and quantitative baselines"""
    
    def __init__(self):
        self.sport_contexts = {
            'NFL': {
                'key_factors': ['offensive/defensive efficiency', 'turnover differential', 'red zone performance', 'injury reports', 'weather conditions'],
                'betting_markets': ['spread', 'total', 'moneyline', 'player props'],
                'critical_stats': ['yards per play', 'third down conversion', 'time of possession', 'sack rate']
            },
            'NBA': {
                'key_factors': ['pace of play', 'offensive/defensive rating', 'rebounding differential', 'injury reports', 'rest days'],
                'betting_markets': ['spread', 'total', 'moneyline', 'player props'],
                'critical_stats': ['effective field goal %', 'turnover rate', 'free throw rate', 'offensive rebounding %']
            },
            'MLB': {
                'key_factors': ['starting pitching matchup', 'bullpen strength', 'recent offensive form', 'weather conditions', 'ballpark factors'],
                'betting_markets': ['run line', 'total', 'moneyline', 'first 5 innings'],
                'critical_stats': ['ERA', 'WHIP', 'OPS', 'team batting average', 'bullpen ERA']
            }
        }
    
    def generate_enhanced_prompt(self, game_data: Dict, real_time_data: Dict, quantitative_baseline: Dict) -> str:
        """Generate comprehensive prompt with all available data"""
        
        sport = game_data.get('sport', 'NFL')
        home_team = self._extract_team_name(game_data.get('home_team', {}))
        away_team = self._extract_team_name(game_data.get('away_team', {}))
        
        # Build the enhanced prompt
        prompt = f"""**PROFESSIONAL SPORTS ANALYSIS REQUEST**

**GAME DETAILS:**
- Sport: {sport}
- Matchup: {away_team} @ {home_team}
- Date: {game_data.get('date', 'TBD')}
- Time: {game_data.get('time', 'TBD')}
- Venue: {game_data.get('venue', 'TBD')}

**QUANTITATIVE BASELINE ANALYSIS:**
{self._format_quantitative_data(quantitative_baseline)}

**REAL-TIME DATA SUMMARY:**
{self._format_real_time_data(real_time_data, sport)}

**ANALYSIS REQUIREMENTS:**

You are a professional sports analyst with access to comprehensive real-time data and quantitative models. Your analysis will be used by experienced bettors who require:

1. **ACCURACY OVER VOLUME** - Only recommend bets when you have genuine conviction
2. **DATA-DRIVEN DECISIONS** - Base analysis on provided statistics, not general knowledge
3. **CONSERVATIVE CONFIDENCE** - High confidence (80%+) should be rare and well-justified
4. **SPECIFIC REASONING** - Explain exactly why the data supports your conclusion

**CRITICAL ANALYSIS FRAMEWORK:**

{self._get_sport_specific_framework(sport)}

**REQUIRED JSON OUTPUT:**
```json
{{
    "analysis_summary": "2-3 sentence summary of key findings from the data",
    "predicted_winner": "{home_team} or {away_team}",
    "confidence": 0.XX,
    "primary_reasoning": [
        "Most important factor from the data",
        "Second most important factor",
        "Third supporting factor"
    ],
    "quantitative_validation": {{
        "baseline_probability": {quantitative_baseline.get('home_win_probability', 0.5):.3f},
        "data_quality_score": {real_time_data.get('data_quality_score', 0.3):.2f},
        "key_statistical_edge": "specific stat that provides advantage",
        "confidence_justification": "why this confidence level is appropriate"
    }},
    "betting_recommendations": {{
        "primary_bet": {{
            "type": "moneyline/spread/total",
            "selection": "specific pick",
            "confidence": 0.XX,
            "reasoning": "why this bet has value",
            "suggested_units": 1-3
        }},
        "avoid": "what bets to avoid and why"
    }},
    "risk_factors": [
        "Main risk to this prediction",
        "Secondary concern"
    ],
    "data_reliability": {{
        "injury_data_current": true/false,
        "weather_data_available": true/false,
        "statistical_sample_adequate": true/false,
        "overall_data_confidence": "high/medium/low"
    }}
}}
```

**CRITICAL INSTRUCTIONS:**
- Use ONLY the provided data - do not rely on general knowledge about teams
- If data quality is low (< 0.5), keep confidence below 70%
- Weather significantly impacts outdoor sports - factor this heavily
- Injury reports can change everything - adjust confidence accordingly
- The quantitative baseline provides the statistical foundation - respect it
- Be conservative: it's better to pass on a bet than make a poor prediction
- Focus on identifying genuine edges, not just picking winners

**DATA QUALITY STANDARDS:**
- High confidence (75%+) requires data_quality_score > 0.6
- Medium confidence (60-74%) requires data_quality_score > 0.4
- Low confidence (50-59%) for data_quality_score < 0.4
- Never exceed 85% confidence unless data is exceptional and supports it

Analyze the provided data thoroughly and provide your professional assessment."""

        return prompt
    
    def _extract_team_name(self, team_data) -> str:
        """Extract team name from various formats"""
        if isinstance(team_data, dict):
            return team_data.get('name', team_data.get('displayName', 'Unknown'))
        return str(team_data) if team_data else 'Unknown'
    
    def _format_quantitative_data(self, baseline: Dict) -> str:
        """Format quantitative baseline data for prompt"""
        
        if not baseline or baseline.get('error'):
            return "❌ Quantitative baseline unavailable - proceed with caution"
        
        home_prob = baseline.get('home_win_probability', 0.5)
        confidence = baseline.get('confidence_score', 0.3)
        
        formatted = f"""✅ **Quantitative Model Results:**
- Home Win Probability: {home_prob:.1%}
- Model Confidence: {confidence:.2f}/1.0
- Base Home Advantage: {baseline.get('base_home_advantage', 0.5):.1%}"""

        # Add specific adjustments
        if baseline.get('strength_differential'):
            formatted += f"\n- Team Strength Differential: {baseline['strength_differential']:+.3f}"
        
        if baseline.get('weather_factor'):
            formatted += f"\n- Weather Adjustment: {baseline['weather_factor']:+.3f}"
            
        if baseline.get('injury_factor'):
            formatted += f"\n- Injury Impact: {baseline['injury_factor']:+.3f}"
        
        # Add key insights
        insights = baseline.get('key_insights', [])
        if insights:
            formatted += "\n- Key Statistical Insights: " + "; ".join(insights[:2])
        
        return formatted
    
    def _format_real_time_data(self, real_time_data: Dict, sport: str) -> str:
        """Format real-time data for prompt"""
        
        if not real_time_data:
            return "❌ No real-time data available"
        
        formatted = f"**Data Quality Score: {real_time_data.get('data_quality_score', 0.0):.2f}/1.0**\n"
        
        # Weather data
        weather = real_time_data.get('weather', {})
        if weather and weather.get('source') != 'Fallback':
            formatted += f"\n🌤️ **Weather Conditions:**\n"
            formatted += f"- Temperature: {weather.get('temperature', 'N/A')}°F\n"
            formatted += f"- Conditions: {weather.get('conditions', 'Unknown')}\n"
            formatted += f"- Wind: {weather.get('wind_speed', 'N/A')} mph\n"
            formatted += f"- Humidity: {weather.get('humidity', 'N/A')}%"
        
        # Injury data
        injuries = real_time_data.get('injuries', {})
        if injuries.get('reports'):
            formatted += f"\n🏥 **Injury Reports:**\n"
            for report in injuries['reports'][:3]:  # Top 3 most important
                formatted += f"- {report.get('team', 'Team')}: {report.get('status', 'Status unknown')} (Impact: {report.get('impact', 'minimal')})\n"
        
        # Team statistics
        team_stats = real_time_data.get('team_stats', {})
        if team_stats.get('home_stats') and team_stats.get('away_stats'):
            formatted += f"\n📊 **Season Statistics Available:**\n"
            formatted += f"- Current season stats for both teams\n"
            formatted += f"- Last updated: {team_stats.get('last_updated', 'Unknown')}"
        
        # Recent form
        recent_form = real_time_data.get('recent_form', {})
        if recent_form.get('home_form') or recent_form.get('away_form'):
            formatted += f"\n📈 **Recent Form Data:**\n"
            if recent_form.get('home_form', {}).get('trend'):
                formatted += f"- Home team trend: {recent_form['home_form']['trend']}\n"
            if recent_form.get('away_form', {}).get('trend'):
                formatted += f"- Away team trend: {recent_form['away_form']['trend']}"
        
        if len(formatted.strip()) <= 50:  # Minimal data
            formatted += "\n⚠️ **Limited real-time data available - rely more heavily on quantitative baseline**"
        
        return formatted
    
    def _get_sport_specific_framework(self, sport: str) -> str:
        """Get sport-specific analysis framework"""
        
        context = self.sport_contexts.get(sport, self.sport_contexts['NFL'])
        
        framework = f"""**{sport}-SPECIFIC ANALYSIS PRIORITIES:**

**Key Factors to Analyze:**
{chr(10).join(f"- {factor}" for factor in context['key_factors'])}

**Critical Statistics:**
{chr(10).join(f"- {stat}" for stat in context['critical_stats'])}

**Betting Markets to Consider:**
{chr(10).join(f"- {market}" for market in context['betting_markets'])}"""

        # Add sport-specific guidance
        if sport == 'NFL':
            framework += """

**NFL-Specific Considerations:**
- Weather has major impact on outdoor games (wind >15mph, temp <20°F, precipitation)
- Injury reports released throughout week - key players can change everything
- Home field advantage varies significantly by team (dome vs outdoor, crowd noise)
- Divisional games often closer than statistics suggest
- Short week games (Thursday/Monday) may favor certain team types"""

        elif sport == 'NBA':
            framework += """

**NBA-Specific Considerations:**
- Rest days and back-to-back games significantly impact performance
- Pace of play affects total scoring - look for pace mismatches
- Home court advantage varies by venue (altitude, crowd, travel)
- Star player availability can swing games by 8+ points
- Fourth quarter execution often determines close games"""

        elif sport == 'MLB':
            framework += """

**MLB-Specific Considerations:**
- Starting pitcher matchup is primary factor (ERA, WHIP, recent form)
- Weather affects ball flight significantly (wind direction, temperature, humidity)
- Ballpark factors influence scoring (dimensions, altitude, wind patterns)
- Bullpen usage in recent games affects availability
- Day vs night games can impact certain teams/players"""
        
        return framework
    
    def generate_fast_prompt(self, game_data: Dict, quantitative_baseline: Dict) -> str:
        """Generate faster prompt for high-volume analysis"""
        
        sport = game_data.get('sport', 'NFL')
        home_team = self._extract_team_name(game_data.get('home_team', {}))
        away_team = self._extract_team_name(game_data.get('away_team', {}))
        
        home_prob = quantitative_baseline.get('home_win_probability', 0.5)
        
        prompt = f"""**RAPID SPORTS ANALYSIS**

**Game:** {away_team} @ {home_team} ({sport})
**Quantitative Baseline:** Home win probability: {home_prob:.1%}

As a professional analyst, provide a quick but accurate assessment based on statistical analysis.

**Required JSON Output:**
{{
    "predicted_winner": "{home_team} or {away_team}",
    "confidence": 0.XX,
    "primary_reason": "main statistical factor supporting this pick",
    "secondary_reason": "supporting factor",
    "betting_value": "best bet type for this game",
    "risk_level": "low/medium/high"
}}

**Instructions:**
- Base prediction on quantitative baseline ({home_prob:.1%} home win probability)
- Keep confidence conservative (60-75% typical range)
- Focus on strongest statistical edge
- Identify best betting opportunity"""

        return prompt
