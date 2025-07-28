import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.odds_api import OddsAPIManager, OddsAnalyzer
from utils.ai_analysis import AIGameAnalyzer
import plotly.express as px
import plotly.graph_objects as go

def show_live_odds():
    """Live Betting Odds Page"""
    
    st.title("💰 Live Betting Odds")
    st.markdown("Real-time betting odds from The Odds API with AI-powered analysis")
    
    # Responsible gambling disclaimer
    st.error("⚠️ **Responsible Gambling**: Betting involves risk. Only bet what you can afford to lose. This platform is for entertainment and educational purposes only.")
    
    # Initialize managers
    if 'odds_manager' not in st.session_state:
        st.session_state.odds_manager = OddsAPIManager()
    
    if 'odds_analyzer' not in st.session_state:
        st.session_state.odds_analyzer = OddsAnalyzer()
    
    if 'ai_analyzer' not in st.session_state:
        st.session_state.ai_analyzer = AIGameAnalyzer()
    
    # API Status check
    with st.spinner("Checking Odds API status..."):
        api_status = st.session_state.odds_manager.get_api_usage()
    
    # Display API status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if api_status.get('status') == 'active':
            st.success("🟢 API Active")
        else:
            st.error("🔴 API Issue")
    
    with col2:
        remaining = api_status.get('remaining_requests', 'Unknown')
        st.metric("Requests Left", remaining)
    
    with col3:
        used = api_status.get('used_requests', 'Unknown')
        st.metric("Requests Used", used)
    
    with col4:
        if st.button("🔄 Refresh Odds", type="primary"):
            # Clear cache
            if 'comprehensive_odds' in st.session_state:
                del st.session_state['comprehensive_odds']
            st.rerun()
    
    st.divider()
    
    # Tabs for different features
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Live Odds", 
        "🎯 AI + Odds Analysis", 
        "💎 Value Bets", 
        "📈 Odds Comparison"
    ])
    
    with tab1:
        show_live_odds_tab()
    
    with tab2:
        show_ai_odds_analysis_tab()
    
    with tab3:
        show_value_bets_tab()
    
    with tab4:
        show_odds_comparison_tab()

def show_live_odds_tab():
    """Show live odds from The Odds API"""
    st.markdown("### 📊 Current Betting Odds")
    
    # Fetch comprehensive odds (cached)
    if 'comprehensive_odds' not in st.session_state:
        with st.spinner("Fetching live odds from The Odds API..."):
            odds_df = st.session_state.odds_manager.get_comprehensive_odds()
            st.session_state['comprehensive_odds'] = odds_df
    else:
        odds_df = st.session_state['comprehensive_odds']
    
    if len(odds_df) == 0:
        st.warning("No live odds available at this time. This could be due to:")
        st.markdown("- No games scheduled for today")
        st.markdown("- API rate limit reached")
        st.markdown("- Temporary API issues")
        return
    
    # Sports filter
    available_sports = odds_df['sport'].unique()
    selected_sports = st.multiselect(
        "Filter by sport:",
        options=available_sports,
        default=available_sports,
        key="odds_sports_filter"
    )
    
    if selected_sports:
        filtered_odds = odds_df[odds_df['sport'].isin(selected_sports)]
    else:
        filtered_odds = odds_df
    
    # Display odds summary
    st.markdown(f"**Total Games with Odds**: {len(filtered_odds)}")
    
    # Group by sport
    for sport in selected_sports:
        sport_odds = filtered_odds[filtered_odds['sport'] == sport]
        
        if len(sport_odds) > 0:
            st.markdown(f"### 🏆 {sport}")
            
            for idx, game in sport_odds.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{game['game_name']}**")
                        st.markdown(f"📅 {game['date']} at {game['time']}")
                    
                    with col2:
                        home_odds = game['home_odds']
                        st.markdown(f"**{game['home_team']}**")
                        if home_odds != 'N/A':
                            color = "green" if str(home_odds).startswith('+') else "red"
                            st.markdown(f"<span style='color:{color}; font-weight:bold'>{home_odds}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown("No odds")
                    
                    with col3:
                        away_odds = game['away_odds']
                        st.markdown(f"**{game['away_team']}**")
                        if away_odds != 'N/A':
                            color = "green" if str(away_odds).startswith('+') else "red"
                            st.markdown(f"<span style='color:{color}; font-weight:bold'>{away_odds}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown("No odds")
                    
                    st.markdown(f"*Source: {game.get('best_bookmaker', 'Various')}*")
                    st.markdown("---")

def show_ai_odds_analysis_tab():
    """Combine AI analysis with odds data"""
    st.markdown("### 🎯 AI Analysis + Live Odds")
    st.markdown("Get AI predictions combined with real betting odds")
    
    # Get odds data
    if 'comprehensive_odds' not in st.session_state:
        with st.spinner("Loading odds data..."):
            odds_df = st.session_state.odds_manager.get_comprehensive_odds()
            st.session_state['comprehensive_odds'] = odds_df
    else:
        odds_df = st.session_state['comprehensive_odds']
    
    if len(odds_df) == 0:
        st.info("No odds data available for AI analysis")
        return
    
    # Game selection
    game_options = {}
    for idx, game in odds_df.iterrows():
        display_name = f"{game['game_name']} ({game['sport']}) - {game['time']}"
        game_options[display_name] = idx
    
    selected_game_name = st.selectbox(
        "Choose a game for AI + Odds analysis:",
        options=list(game_options.keys()),
        key="ai_odds_game_selector"
    )
    
    if selected_game_name:
        game_idx = game_options[selected_game_name]
        selected_game = odds_df.iloc[game_idx]
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🧠 Get ChatGPT Analysis", type="primary"):
                analyze_game_with_odds(selected_game, 'openai')
        
        with col2:
            if st.button("⚡ Get Gemini Analysis", type="secondary"):
                analyze_game_with_odds(selected_game, 'gemini')
        
        # Show combined analysis if available
        show_combined_analysis(selected_game, game_idx)

def show_value_bets_tab():
    """Show potential value betting opportunities"""
    st.markdown("### 💎 Value Betting Analysis")
    st.markdown("*Educational analysis of betting value - not financial advice*")
    
    # Get odds data
    if 'comprehensive_odds' not in st.session_state:
        odds_df = st.session_state.odds_manager.get_comprehensive_odds()
        st.session_state['comprehensive_odds'] = odds_df
    else:
        odds_df = st.session_state['comprehensive_odds']
    
    if len(odds_df) == 0:
        st.info("No odds data available for value analysis")
        return
    
    # Calculate value bets
    with st.spinner("Analyzing betting value..."):
        value_bets = st.session_state.odds_analyzer.find_best_value_bets(odds_df)
    
    if value_bets:
        st.markdown("#### 🎯 Top Value Opportunities")
        st.markdown("*Lower bookmaker margins may indicate better value*")
        
        for i, bet in enumerate(value_bets, 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{i}. {bet['game']}**")
                    st.markdown(f"📅 {bet['date']}")
                
                with col2:
                    st.markdown(f"**{bet['sport']}**")
                
                with col3:
                    margin = bet['bookmaker_margin']
                    color = "green" if float(margin.replace('%', '')) < 5 else "orange" if float(margin.replace('%', '')) < 10 else "red"
                    st.markdown(f"<span style='color:{color}'>{margin}</span>", unsafe_allow_html=True)
                
                with col4:
                    rating = bet['value_rating']
                    color = "green" if rating == "High" else "orange" if rating == "Medium" else "red"
                    st.markdown(f"<span style='color:{color}'>{rating}</span>", unsafe_allow_html=True)
                
                st.markdown("---")
        
        # Educational note
        st.info("💡 **Educational Note**: Lower margins suggest better value, but remember that all betting involves risk. This analysis is for educational purposes only.")
    
    else:
        st.info("No value betting analysis available")

def show_odds_comparison_tab():
    """Show odds comparison and trends"""
    st.markdown("### 📈 Odds Analysis & Trends")
    
    # Get odds data
    if 'comprehensive_odds' not in st.session_state:
        odds_df = st.session_state.odds_manager.get_comprehensive_odds()
        st.session_state['comprehensive_odds'] = odds_df
    else:
        odds_df = st.session_state['comprehensive_odds']
    
    if len(odds_df) == 0:
        st.info("No odds data available for comparison")
        return
    
    # Odds distribution by sport
    st.markdown("#### 📊 Odds Distribution by Sport")
    
    # Create visualization of odds
    try:
        # Prepare data for visualization
        viz_data = []
        
        for idx, game in odds_df.iterrows():
            home_odds = game['home_odds']
            away_odds = game['away_odds']
            
            if home_odds != 'N/A' and away_odds != 'N/A':
                try:
                    # Convert to implied probabilities
                    home_prob = american_odds_to_probability(home_odds)
                    away_prob = american_odds_to_probability(away_odds)
                    
                    viz_data.append({
                        'Game': game['game_name'][:30] + '...' if len(game['game_name']) > 30 else game['game_name'],
                        'Sport': game['sport'],
                        'Home Team Probability': home_prob,
                        'Away Team Probability': away_prob,
                        'Home Team': game['home_team'],
                        'Away Team': game['away_team']
                    })
                except:
                    continue
        
        if viz_data:
            viz_df = pd.DataFrame(viz_data)
            
            # Create scatter plot
            fig = px.scatter(
                viz_df, 
                x='Home Team Probability', 
                y='Away Team Probability',
                color='Sport',
                hover_data=['Game', 'Home Team', 'Away Team'],
                title='Game Probabilities by Sport'
            )
            
            fig.update_layout(
                xaxis_title="Home Team Win Probability (%)",
                yaxis_title="Away Team Win Probability (%)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            st.markdown("#### 📈 Summary Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_home_prob = viz_df['Home Team Probability'].mean()
                st.metric("Avg Home Advantage", f"{avg_home_prob:.1f}%")
            
            with col2:
                total_games = len(viz_df)
                st.metric("Games Analyzed", total_games)
            
            with col3:
                sports_count = viz_df['Sport'].nunique()
                st.metric("Sports Covered", sports_count)
        
        else:
            st.info("Insufficient data for odds visualization")
    
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")

def analyze_game_with_odds(game_data: pd.Series, ai_source: str):
    """Analyze game combining AI and odds data"""
    cache_key = f"ai_odds_analysis_{ai_source}_{game_data.name}"
    
    if cache_key not in st.session_state:
        with st.spinner(f"{'ChatGPT' if ai_source == 'openai' else 'Gemini'} is analyzing game with odds..."):
            try:
                # Create enhanced prompt with odds information
                enhanced_game_data = game_data.to_dict()
                enhanced_game_data['betting_context'] = {
                    'home_odds': enhanced_game_data.get('home_odds', 'N/A'),
                    'away_odds': enhanced_game_data.get('away_odds', 'N/A'),
                    'bookmaker': enhanced_game_data.get('best_bookmaker', 'Various')
                }
                
                if ai_source == 'openai':
                    analysis = st.session_state.ai_analyzer.analyze_game_with_openai(enhanced_game_data)
                else:
                    analysis = st.session_state.ai_analyzer.analyze_game_with_gemini(enhanced_game_data)
                
                st.session_state[cache_key] = analysis
                
            except Exception as e:
                st.error(f"AI analysis failed: {str(e)}")
                return
    
    # Display the analysis
    analysis = st.session_state[cache_key]
    
    if 'error' not in analysis:
        ai_name = "ChatGPT" if ai_source == 'openai' else "Gemini"
        st.markdown(f"#### {ai_name} Analysis with Odds Context")
        
        # Show analysis with odds
        if 'analysis' in analysis:
            st.info(analysis['analysis'])
        
        # Compare AI prediction with odds
        st.markdown("#### 🔍 AI vs Betting Market")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**AI Prediction:**")
            st.success(analysis.get('predicted_winner', 'Unknown'))
            
            confidence = analysis.get('confidence', 0.5)
            st.progress(confidence)
            st.write(f"Confidence: {confidence:.1%}")
        
        with col2:
            st.markdown("**Market Odds:**")
            home_odds = game_data.get('home_odds', 'N/A')
            away_odds = game_data.get('away_odds', 'N/A')
            
            st.markdown(f"{game_data.get('home_team', 'Home')}: **{home_odds}**")
            st.markdown(f"{game_data.get('away_team', 'Away')}: **{away_odds}**")
    
    else:
        st.error(f"Analysis failed: {analysis.get('error', 'Unknown error')}")

def show_combined_analysis(game_data: pd.Series, game_idx: int):
    """Show combined AI and odds analysis if available"""
    openai_key = f"ai_odds_analysis_openai_{game_idx}"
    gemini_key = f"ai_odds_analysis_gemini_{game_idx}"
    
    has_openai = openai_key in st.session_state
    has_gemini = gemini_key in st.session_state
    
    if has_openai or has_gemini:
        st.markdown("---")
        st.markdown("### 🔍 AI + Odds Analysis Results")
        
        if has_openai and has_gemini:
            # Compare both AI analyses
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🧠 ChatGPT Analysis")
                openai_analysis = st.session_state[openai_key]
                if 'error' not in openai_analysis:
                    st.json(openai_analysis)
                
            with col2:
                st.markdown("#### ⚡ Gemini Analysis")
                gemini_analysis = st.session_state[gemini_key]
                if 'error' not in gemini_analysis:
                    st.json(gemini_analysis)
        
        elif has_openai:
            with st.expander("🧠 ChatGPT Analysis", expanded=True):
                st.json(st.session_state[openai_key])
        
        elif has_gemini:
            with st.expander("⚡ Gemini Analysis", expanded=True):
                st.json(st.session_state[gemini_key])

def american_odds_to_probability(odds_str: str) -> float:
    """Convert American odds to probability percentage"""
    try:
        if isinstance(odds_str, str):
            odds = int(odds_str.replace('+', ''))
        else:
            odds = int(odds_str)
        
        if odds > 0:
            return 100 / (odds + 100) * 100
        else:
            return abs(odds) / (abs(odds) + 100) * 100
            
    except Exception:
        return 50.0

if __name__ == "__main__":
    show_live_odds()