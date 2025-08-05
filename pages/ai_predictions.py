import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.live_games import LiveGamesManager
from utils.ai_analysis import AIGameAnalyzer, AIGameFinder
import json

def show_ai_predictions():
    """AI-Powered Game Predictions Page"""
    
    st.title("🤖 AI-Powered Sports Predictions")
    st.markdown("Get intelligent game analysis and predictions powered by ChatGPT and Gemini AI")
    
    # Responsible gambling disclaimer
    st.warning("⚠️ **Responsible Gambling Notice**: AI predictions are for entertainment and educational purposes only. Sports betting involves risk. Only bet what you can afford to lose.")
    
    # Initialize managers
    if 'games_manager' not in st.session_state:
        st.session_state.games_manager = LiveGamesManager()
    
    if 'ai_analyzer' not in st.session_state:
        st.session_state.ai_analyzer = AIGameAnalyzer()
    
    if 'ai_finder' not in st.session_state:
        st.session_state.ai_finder = AIGameFinder()
    
    # Controls row - moved up for better UX
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_date = st.date_input(
            "📅 Select Date for AI Analysis",
            value=date.today(),
            min_value=date.today(),
            max_value=date.today() + timedelta(days=30)
        )
    
    with col2:
        if st.button("🔄 Refresh Analysis", type="primary"):
            # Clear cached AI analyses
            for key in list(st.session_state.keys()):
                if isinstance(key, str) and key.startswith('ai_analysis_'):
                    del st.session_state[key]
            st.rerun()
    
    with col3:
        if st.button("🚀 Load Games", type="secondary"):
            # Force reload games without cache notifications
            st.session_state.show_cache_notifications = False
            st.rerun()
    
    # Get games for selected date
    with st.spinner("Fetching games for AI analysis..."):
        # Disable cache notifications during game loading
        original_cache_setting = st.session_state.get('show_cache_notifications', False)
        st.session_state.show_cache_notifications = False
        
        games_df = st.session_state.games_manager.get_upcoming_games_all_sports(target_date=selected_date)
        
        # Restore original cache setting
        st.session_state.show_cache_notifications = original_cache_setting
    
    if len(games_df) == 0:
        st.info(f"No games found for {selected_date.strftime('%B %d, %Y')}. Try selecting a different date.")
        return
    
    # Tabs for different AI features
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Game Analysis", 
        "🏆 AI Recommendations", 
        "🔍 Smart Search", 
        "📊 Betting Insights"
    ])
    
    with tab1:
        show_game_analysis_tab(games_df, selected_date)
    
    with tab2:
        show_ai_recommendations_tab(games_df)
    
    with tab3:
        show_smart_search_tab(games_df)
    
    with tab4:
        show_betting_insights_tab(games_df)

def show_game_analysis_tab(games_df: pd.DataFrame, selected_date: date):
    """Show AI game analysis"""
    st.markdown("### 🎯 AI Game Analysis")
    st.markdown("Select a game for detailed AI-powered analysis using ChatGPT and Gemini")
    
    # Game selection
    game_options = {}
    for idx, game in games_df.iterrows():
        home_team_data = game.get('home_team', {}) or {}
        away_team_data = game.get('away_team', {}) or {}
        home_team = home_team_data.get('name', 'Unknown')
        away_team = away_team_data.get('name', 'Unknown')
        league = game.get('league', 'Unknown')
        game_time = game.get('time', 'TBD')
        
        display_name = f"{away_team} @ {home_team} ({league}) - {game_time}"
        game_options[display_name] = idx
    
    if not game_options:
        st.info("No games available for analysis")
        return
    
    selected_game_name = st.selectbox(
        "Choose a game to analyze:",
        options=list(game_options.keys()),
        key="game_analysis_selector"
    )
    
    if selected_game_name:
        game_idx = game_options[selected_game_name]
        selected_game = games_df.iloc[game_idx]
        
        # AI Analysis options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧠 Analyze with ChatGPT", type="primary", key=f"openai_analysis_{game_idx}"):
                analyze_with_openai(selected_game, game_idx)
        
        with col2:
            if st.button("⚡ Analyze with Gemini", type="secondary", key=f"gemini_analysis_{game_idx}"):
                analyze_with_gemini(selected_game, game_idx)
        
        # Display results area
        st.markdown("---")
        
        # Show existing analyses
        show_cached_analyses(game_idx)

def show_ai_recommendations_tab(games_df: pd.DataFrame):
    """Show AI game recommendations"""
    st.markdown("### 🏆 AI Game Recommendations")
    st.markdown("Get personalized game recommendations based on AI analysis")
    
    if st.button("🎯 Get AI Recommendations", type="primary"):
        with st.spinner("AI is analyzing today's games for recommendations..."):
            try:
                recommendations = st.session_state.ai_analyzer.get_game_recommendations(games_df)
                
                if recommendations and not any('error' in rec for rec in recommendations):
                    st.markdown("#### 🌟 Top Recommended Games")
                    
                    for i, rec in enumerate(recommendations, 1):
                        if 'error' not in rec:
                            excitement = rec.get('excitement_level', 7)
                            stars = "⭐" * min(excitement, 10)
                            
                            with st.expander(f"{i}. {rec.get('game', 'Unknown Game')} {stars}"):
                                st.markdown(f"**Excitement Level**: {excitement}/10")
                                st.markdown(f"**Why Watch**: {rec.get('reason', 'Great matchup!')}")
                else:
                    st.error("Unable to generate recommendations at this time")
                    
            except Exception as e:
                st.error(f"Recommendation error: {str(e)}")

def show_smart_search_tab(games_df: pd.DataFrame):
    """Show AI-powered smart search"""
    st.markdown("### 🔍 Smart Game Search")
    st.markdown("Use natural language to find games. Try: 'Lakers game', 'high scoring basketball', 'rivalry matchups'")
    
    search_query = st.text_input(
        "Search for games:",
        placeholder="e.g., 'close basketball games', 'teams from California', 'primetime games'"
    )
    
    if search_query and st.button("🔍 Smart Search"):
        with st.spinner("AI is searching for relevant games..."):
            try:
                matches = st.session_state.ai_finder.smart_game_search(search_query, games_df)
                
                if matches and not any('error' in match for match in matches):
                    st.markdown(f"#### 🎯 Search Results for: '{search_query}'")
                    
                    for match in matches:
                        if 'error' not in match:
                            game_id = match.get('game_id', 0)
                            relevance = match.get('relevance_score', 0.5)
                            reason = match.get('match_reason', 'Relevant match')
                            
                            if game_id < len(games_df):
                                game = games_df.iloc[game_id]
                                home_team = game.get('home_team', {}).get('name', 'Unknown')
                                away_team = game.get('away_team', {}).get('name', 'Unknown')
                                league = game.get('league', 'Unknown')
                                game_time = game.get('time', 'TBD')
                                
                                relevance_stars = "🎯" * int(relevance * 5)
                                
                                with st.container():
                                    st.markdown(f"**{away_team} @ {home_team}** ({league}) - {game_time}")
                                    st.markdown(f"**Relevance**: {relevance_stars} ({relevance:.1%})")
                                    st.markdown(f"**Match Reason**: {reason}")
                                    st.markdown("---")
                else:
                    st.info("No matching games found for your search")
                    
            except Exception as e:
                st.error(f"Search error: {str(e)}")

def show_betting_insights_tab(games_df: pd.DataFrame):
    """Show responsible betting insights"""
    st.markdown("### 📊 Educational Betting Insights")
    st.markdown("Learn about sports analytics and statistical trends (Educational purposes only)")
    
    # Another responsible gambling warning
    st.error("🚨 **Important**: This section is for educational purposes only. Sports betting involves significant financial risk. Please gamble responsibly.")
    
    # Game selection for betting insights
    game_options = {}
    for idx, game in games_df.iterrows():
        home_team_data = game.get('home_team', {}) or {}
        away_team_data = game.get('away_team', {}) or {}
        home_team = home_team_data.get('name', 'Unknown')
        away_team = away_team_data.get('name', 'Unknown')
        league = game.get('league', 'Unknown')
        
        display_name = f"{away_team} @ {home_team} ({league})"
        game_options[display_name] = idx
    
    if game_options:
        selected_game_name = st.selectbox(
            "Choose a game for educational analysis:",
            options=list(game_options.keys()),
            key="betting_insights_selector"
        )
        
        if selected_game_name and st.button("📈 Get Educational Insights"):
            game_idx = game_options[selected_game_name]
            selected_game = games_df.iloc[game_idx]
            
            with st.spinner("Generating educational betting insights..."):
                try:
                    insights = st.session_state.ai_analyzer.generate_betting_insights(selected_game.to_dict())
                    
                    if 'error' not in insights:
                        st.markdown(f"#### 📊 Statistical Analysis: {selected_game_name}")
                        
                        # Analysis
                        if 'analysis' in insights:
                            st.markdown("**📈 Statistical Analysis:**")
                            st.info(insights['analysis'])
                        
                        # Risk factors
                        if 'risk_factors' in insights:
                            st.markdown("**⚠️ Risk Factors to Consider:**")
                            for factor in insights['risk_factors']:
                                st.markdown(f"• {factor}")
                        
                        # Educational insights
                        if 'educational_insights' in insights:
                            st.markdown("**🎓 Educational Points:**")
                            st.success(insights['educational_insights'])
                        
                        # Responsible gambling note
                        st.error(insights.get('responsible_gambling_note', '⚠️ Please gamble responsibly'))
                        
                    else:
                        st.error(f"Unable to generate insights: {insights.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"Insights error: {str(e)}")

def analyze_with_openai(game_data: pd.Series, game_idx: int):
    """Analyze game with OpenAI"""
    cache_key = f"ai_analysis_openai_{game_idx}"
    
    if cache_key not in st.session_state:
        with st.spinner("ChatGPT is analyzing the game..."):
            try:
                analysis = st.session_state.ai_analyzer.analyze_game_with_openai(game_data.to_dict())
                st.session_state[cache_key] = analysis
                st.success("ChatGPT analysis completed!")
            except Exception as e:
                st.error(f"OpenAI analysis failed: {str(e)}")
                return
    
    analysis = st.session_state[cache_key]
    
    if 'error' not in analysis:
        st.markdown("#### 🧠 ChatGPT Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Predicted Winner:**")
            st.success(analysis.get('predicted_winner', 'Unknown'))
            
            st.markdown("**Confidence Level:**")
            confidence = analysis.get('confidence', 0.5)
            st.progress(confidence)
            st.write(f"{confidence:.1%}")
        
        with col2:
            st.markdown("**Risk Level:**")
            risk_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
            risk_level = analysis.get('risk_level', 'MEDIUM')
            st.markdown(f"{risk_color.get(risk_level, '🟡')} {risk_level}")
        
        # Detailed analysis
        if 'analysis' in analysis:
            st.markdown("**📝 Detailed Analysis:**")
            st.info(analysis['analysis'])
        
        # Key factors
        if 'key_factors' in analysis:
            st.markdown("**🔑 Key Factors:**")
            for factor in analysis['key_factors']:
                st.markdown(f"• {factor}")
        
        # Betting insight
        if 'betting_insight' in analysis:
            st.markdown("**💡 Insight:**")
            st.warning(analysis['betting_insight'])
    else:
        st.error(f"OpenAI analysis failed: {analysis.get('error', 'Unknown error')}")

def analyze_with_gemini(game_data: pd.Series, game_idx: int):
    """Analyze game with Gemini"""
    cache_key = f"ai_analysis_gemini_{game_idx}"
    
    if cache_key not in st.session_state:
        with st.spinner("Gemini AI is analyzing the game..."):
            try:
                analysis = st.session_state.ai_analyzer.analyze_game_with_gemini(game_data.to_dict())
                st.session_state[cache_key] = analysis
                st.success("Gemini analysis completed!")
            except Exception as e:
                st.error(f"Gemini analysis failed: {str(e)}")
                return
    
    analysis = st.session_state[cache_key]
    
    if 'error' not in analysis:
        st.markdown("#### ⚡ Gemini AI Analysis")
        
        # Team analysis
        if 'team_analysis' in analysis:
            st.markdown("**📊 Team Analysis:**")
            st.info(analysis['team_analysis'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Prediction:**")
            st.success(analysis.get('prediction', 'Unknown'))
            
            if 'confidence_score' in analysis:
                st.markdown("**Confidence:**")
                confidence = analysis['confidence_score']
                st.progress(confidence)
                st.write(f"{confidence:.1%}")
        
        with col2:
            if 'score_prediction' in analysis:
                st.markdown("**Score Prediction:**")
                st.info(analysis['score_prediction'])
        
        # Critical factors
        if 'critical_factors' in analysis:
            st.markdown("**⚠️ Critical Factors:**")
            for factor in analysis['critical_factors']:
                st.markdown(f"• {factor}")
        
        # Recommendation
        if 'recommendation' in analysis:
            st.markdown("**🎯 Recommendation:**")
            st.success(analysis['recommendation'])
    else:
        st.error(f"Gemini analysis failed: {analysis.get('error', 'Unknown error')}")

def show_cached_analyses(game_idx: int):
    """Show any cached AI analyses for this game"""
    openai_key = f"ai_analysis_openai_{game_idx}"
    gemini_key = f"ai_analysis_gemini_{game_idx}"
    
    has_openai = openai_key in st.session_state
    has_gemini = gemini_key in st.session_state
    
    if has_openai or has_gemini:
        st.markdown("---")
        st.markdown("### 🔍 Previous AI Analyses")
        
        if has_openai:
            with st.expander("🧠 ChatGPT Analysis", expanded=True):
                analysis = st.session_state[openai_key]
                if 'error' not in analysis:
                    st.json(analysis)
                else:
                    st.error(analysis['error'])
        
        if has_gemini:
            with st.expander("⚡ Gemini Analysis", expanded=True):
                analysis = st.session_state[gemini_key]
                if 'error' not in analysis:
                    st.json(analysis)
                else:
                    st.error(analysis['error'])

if __name__ == "__main__":
    show_ai_predictions()