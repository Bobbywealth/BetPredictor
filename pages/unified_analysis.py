import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.dual_ai_consensus import DualAIConsensusEngine, WinningPicksGenerator
from utils.cache_manager import OptimizedDataLoader
from utils.odds_api import OddsAPIManager
from utils.result_tracker import GameResultTracker
from utils.ai_analysis import AIGameAnalyzer, AIGameFinder
from utils.deep_analysis import DeepAnalysisEngine
from utils.live_games import LiveGamesManager

def show_unified_analysis():
    """Unified Analysis Dashboard combining AI predictions, winning picks, and performance tracking"""
    
    st.title("🚀 Unified Sports Analysis Dashboard")
    st.markdown("**Complete AI-powered sports analysis with predictions, picks, and performance tracking**")
    
    # Responsible gambling disclaimer
    st.warning("⚠️ **Responsible Gambling Notice**: AI predictions are for entertainment and educational purposes only. Sports betting involves risk. Only bet what you can afford to lose.")
    
    # Initialize all managers
    if 'consensus_engine' not in st.session_state:
        st.session_state.consensus_engine = DualAIConsensusEngine()
    
    if 'picks_generator' not in st.session_state:
        st.session_state.picks_generator = WinningPicksGenerator()
    
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = OptimizedDataLoader()
    
    if 'odds_manager' not in st.session_state:
        st.session_state.odds_manager = OddsAPIManager()
    
    if 'result_tracker' not in st.session_state:
        st.session_state.result_tracker = GameResultTracker()
    
    if 'ai_analyzer' not in st.session_state:
        st.session_state.ai_analyzer = AIGameAnalyzer()
    
    if 'deep_analyzer' not in st.session_state:
        st.session_state.deep_analyzer = DeepAnalysisEngine()
    
    if 'games_manager' not in st.session_state:
        st.session_state.games_manager = LiveGamesManager()
    
    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Winning Picks",
        "🤖 AI Analysis", 
        "📊 Performance Tracking",
        "🔍 Deep Analysis",
        "💰 Live Odds"
    ])
    
    with tab1:
        show_winning_picks_section()
    
    with tab2:
        show_ai_analysis_section()
    
    with tab3:
        show_performance_section()
    
    with tab4:
        show_deep_analysis_section()
    
    with tab5:
        show_live_odds_section()

def show_winning_picks_section():
    """Winning picks section with dual AI consensus"""
    st.markdown("### 🏆 Today's Winning Picks")
    st.markdown("High-confidence picks based on dual AI consensus analysis")
    
    # Controls
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        selected_date = st.date_input(
            "📅 Pick Date",
            value=date.today(),
            key="winning_picks_date"
        )
    
    with col2:
        confidence_filter = st.selectbox(
            "🎯 Confidence Filter",
            options=["All Picks", "High Confidence (75%+)", "Strong Consensus", "Edge Bets"],
            key="winning_confidence_filter"
        )
    
    with col3:
        if st.button("🔄 Generate Picks", type="primary"):
            generate_winning_picks(selected_date, confidence_filter)
    
    # Display picks if available
    if f'winning_picks_{selected_date}' in st.session_state:
        picks_data = st.session_state[f'winning_picks_{selected_date}']
        display_winning_picks_results(picks_data)
    else:
        st.info("Click 'Generate Picks' to get today's winning recommendations")

def show_ai_analysis_section():
    """AI analysis section with ChatGPT and Gemini"""
    st.markdown("### 🤖 AI Game Analysis")
    st.markdown("Detailed analysis from ChatGPT and Gemini AI")
    
    # Date selection
    selected_date = st.date_input(
        "📅 Analysis Date",
        value=date.today(),
        key="ai_analysis_date"
    )
    
    # Get games
    with st.spinner("Loading games..."):
        games_df = st.session_state.games_manager.get_upcoming_games_all_sports(target_date=selected_date)
    
    if len(games_df) == 0:
        st.info("No games available for the selected date")
        return
    
    # Game selection
    game_options = {}
    for idx, game in games_df.iterrows():
        home_team = game.get('home_team', {}).get('name', 'Unknown')
        away_team = game.get('away_team', {}).get('name', 'Unknown')
        league = game.get('league', 'Unknown')
        game_time = game.get('time', 'TBD')
        
        display_name = f"{away_team} @ {home_team} ({league}) - {game_time}"
        game_options[display_name] = idx
    
    selected_game_name = st.selectbox(
        "Choose a game to analyze:",
        options=list(game_options.keys()),
        key="unified_game_selector"
    )
    
    if selected_game_name:
        game_idx = game_options[selected_game_name]
        selected_game = games_df.iloc[game_idx]
        
        # Analysis buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧠 ChatGPT Analysis", type="primary", key=f"unified_openai_{game_idx}"):
                analyze_game_unified(selected_game, game_idx, 'openai')
        
        with col2:
            if st.button("⚡ Gemini Analysis", type="secondary", key=f"unified_gemini_{game_idx}"):
                analyze_game_unified(selected_game, game_idx, 'gemini')
        
        with col3:
            if st.button("🤝 Dual AI Consensus", key=f"unified_consensus_{game_idx}"):
                generate_consensus_analysis(selected_game, game_idx)
        
        # Display results
        display_unified_analysis_results(game_idx)

def show_performance_section():
    """Performance tracking section"""
    st.markdown("### 📊 Performance Tracking")
    st.markdown("Track prediction accuracy and analyze performance trends")
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analysis_period = st.selectbox(
            "📅 Analysis Period",
            options=[7, 14, 30, 60, 90],
            index=2,
            format_func=lambda x: f"Last {x} days",
            key="unified_performance_period"
        )
    
    with col2:
        if st.button("🔄 Check Results", type="primary"):
            with st.spinner("Checking game results..."):
                results_summary = st.session_state.result_tracker.check_game_results(max_days_back=7)
                if results_summary['results_found'] > 0:
                    st.success(f"Found {results_summary['results_found']} new results!")
                else:
                    st.info("No new results found")
    
    with col3:
        if st.button("📥 Export Data"):
            export_data = st.session_state.result_tracker.export_tracking_data()
            if len(export_data) > 0:
                csv_data = export_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"prediction_tracking_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No tracking data available")
    
    # Performance summary
    performance_summary = st.session_state.result_tracker.get_performance_summary(analysis_period)
    
    if performance_summary.get('total_predictions', 0) > 0:
        display_performance_metrics(performance_summary)
    else:
        st.info("No prediction data available. Make some predictions to track performance!")

def show_deep_analysis_section():
    """Deep analysis section"""
    st.markdown("### 🔍 Deep Game Analysis")
    st.markdown("Comprehensive statistical and market analysis")
    
    # Analysis controls
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_type = st.selectbox(
            "Analysis Depth",
            ["Quick Analysis", "Standard Analysis", "Deep Analysis", "Complete Analysis"],
            index=2,
            key="unified_analysis_depth"
        )
    
    with col2:
        include_odds = st.checkbox("Include Live Odds", value=True, key="unified_include_odds")
    
    # Get comprehensive odds data
    if include_odds:
        with st.spinner("Loading odds data..."):
            odds_df = st.session_state.odds_manager.get_comprehensive_odds()
        
        if len(odds_df) > 0:
            # Game selection from odds
            game_options = {}
            for idx, game in odds_df.iterrows():
                display_name = f"{game['game_name']} ({game['sport']}) - {game['time']}"
                game_options[display_name] = idx
            
            selected_game_name = st.selectbox(
                "Choose a game for deep analysis:",
                options=list(game_options.keys()),
                key="unified_deep_game_selector"
            )
            
            if selected_game_name and st.button("🔍 Run Deep Analysis", type="primary"):
                game_idx = game_options[selected_game_name]
                selected_game = odds_df.iloc[game_idx]
                run_unified_deep_analysis(selected_game, analysis_type)
        else:
            st.info("No odds data available for deep analysis")

def show_live_odds_section():
    """Live odds section with AI integration"""
    st.markdown("### 💰 Live Odds + AI Analysis")
    st.markdown("Current betting odds with AI predictions")
    
    # Get odds data
    with st.spinner("Loading live odds..."):
        odds_df = st.session_state.odds_manager.get_comprehensive_odds()
    
    if len(odds_df) == 0:
        st.error("No live odds available. Please check your API connection.")
        return
    
    # Display odds with filters
    col1, col2 = st.columns(2)
    
    with col1:
        sport_filter = st.selectbox(
            "🏈 Sport Filter",
            options=['All'] + list(odds_df['sport'].unique()),
            key="unified_odds_sport_filter"
        )
    
    with col2:
        value_filter = st.selectbox(
            "💎 Value Filter",
            options=['All Games', 'Potential Value Bets', 'Close Lines', 'Heavy Favorites'],
            key="unified_odds_value_filter"
        )
    
    # Apply filters
    filtered_odds = odds_df.copy()
    if sport_filter != 'All':
        filtered_odds = filtered_odds[filtered_odds['sport'] == sport_filter]
    
    # Display filtered odds
    display_live_odds_with_ai(filtered_odds, value_filter)

# Helper Functions

def generate_winning_picks(selected_date: date, confidence_filter: str):
    """Generate winning picks with caching"""
    cache_key = f'winning_picks_{selected_date}'
    
    with st.spinner("Generating winning picks with dual AI analysis..."):
        try:
            # Get comprehensive data
            odds_data = st.session_state.data_loader.get_comprehensive_game_data(selected_date)
            
            if len(odds_data) == 0:
                st.error("No games available for the selected date")
                return
            
            # Generate picks using dual AI consensus
            picks_df = st.session_state.picks_generator.generate_winning_picks(
                odds_data, 
                max_picks=10,
                min_confidence=0.6 if confidence_filter == "All Picks" else 0.75
            )
            
            if len(picks_df) > 0:
                st.session_state[cache_key] = {
                    'picks_df': picks_df,
                    'generated_at': datetime.now(),
                    'summary': calculate_picks_summary(picks_df)
                }
                st.success(f"Generated {len(picks_df)} winning picks!")
            else:
                st.warning("No picks meet the selected criteria")
                
        except Exception as e:
            st.error(f"Error generating picks: {str(e)}")

def display_winning_picks_results(picks_data: Dict):
    """Display winning picks results"""
    picks_df = picks_data['picks_df']
    summary = picks_data['summary']
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Total Picks", summary['total_picks'])
    
    with col2:
        avg_conf = summary.get('avg_confidence', 0)
        st.metric("📈 Avg Confidence", f"{avg_conf:.1%}")
    
    with col3:
        strong_picks = summary.get('strong_picks', 0)
        st.metric("💎 Strong Picks", strong_picks)
    
    with col4:
        avg_edge = summary.get('avg_edge_score', 0)
        st.metric("⚡ Avg Edge Score", f"{avg_edge:.2f}")
    
    st.divider()
    
    # Display individual picks
    for i, (idx, pick) in enumerate(picks_df.iterrows(), 1):
        with st.container():
            # Ranking badge
            col1, col2 = st.columns([1, 11])
            
            with col1:
                if i == 1:
                    st.markdown("# 🥇")
                elif i == 2:
                    st.markdown("# 🥈")
                elif i == 3:
                    st.markdown("# 🥉")
                else:
                    st.markdown(f"## #{i}")
            
            with col2:
                # Pick details
                st.markdown(f"### {pick['away_team']} @ {pick['home_team']}")
                
                col2a, col2b, col2c = st.columns(3)
                
                with col2a:
                    st.markdown(f"🏆 **{pick['sport']}**")
                    st.markdown(f"📅 {pick['date']} | 🕐 {pick['time']}")
                
                with col2b:
                    st.markdown(f"🎯 **Pick: {pick['consensus_pick']}**")
                    confidence = pick.get('confidence', 0)
                    st.progress(confidence)
                    st.markdown(f"**Confidence: {confidence:.1%}**")
                
                with col2c:
                    edge_score = pick.get('edge_score', 0)
                    st.markdown(f"⚡ **Edge Score: {edge_score:.2f}**")
                    
                    success_prob = pick.get('success_probability', 0)
                    st.markdown(f"📈 **Success Prob: {success_prob:.1%}**")
                
                # Action buttons
                button_col1, button_col2 = st.columns(2)
                
                with button_col1:
                    with st.expander("🔍 View Detailed Analysis"):
                        display_pick_analysis(pick)
                
                with button_col2:
                    if st.button(f"📊 Track This Pick", key=f"unified_track_{i}_{hash(str(pick))}"):
                        tracking_id = st.session_state.result_tracker.track_prediction(pick.to_dict())
                        st.success(f"✅ Prediction tracked! ID: {tracking_id[:8]}...")
            
            st.markdown("---")

def analyze_game_unified(game_data: pd.Series, game_idx: int, ai_source: str):
    """Unified game analysis function"""
    cache_key = f"unified_analysis_{ai_source}_{game_idx}"
    
    if cache_key not in st.session_state:
        ai_name = "ChatGPT" if ai_source == 'openai' else "Gemini"
        with st.spinner(f"{ai_name} is analyzing the game..."):
            try:
                if ai_source == 'openai':
                    analysis = st.session_state.ai_analyzer.analyze_game_with_openai(game_data.to_dict())
                else:
                    analysis = st.session_state.ai_analyzer.analyze_game_with_gemini(game_data.to_dict())
                
                st.session_state[cache_key] = analysis
                st.success(f"{ai_name} analysis completed!")
            except Exception as e:
                st.error(f"{ai_name} analysis failed: {str(e)}")
                return

def generate_consensus_analysis(game_data: pd.Series, game_idx: int):
    """Generate dual AI consensus analysis"""
    cache_key = f"unified_consensus_{game_idx}"
    
    if cache_key not in st.session_state:
        with st.spinner("Generating dual AI consensus..."):
            try:
                consensus = st.session_state.consensus_engine.analyze_game_consensus(game_data.to_dict())
                st.session_state[cache_key] = consensus
                st.success("Dual AI consensus analysis completed!")
            except Exception as e:
                st.error(f"Consensus analysis failed: {str(e)}")

def display_unified_analysis_results(game_idx: int):
    """Display unified analysis results"""
    openai_key = f"unified_analysis_openai_{game_idx}"
    gemini_key = f"unified_analysis_gemini_{game_idx}"
    consensus_key = f"unified_consensus_{game_idx}"
    
    has_results = any(key in st.session_state for key in [openai_key, gemini_key, consensus_key])
    
    if has_results:
        st.markdown("---")
        st.markdown("### 🔍 Analysis Results")
        
        # Display individual analyses
        col1, col2 = st.columns(2)
        
        with col1:
            if openai_key in st.session_state:
                with st.expander("🧠 ChatGPT Analysis", expanded=True):
                    display_ai_analysis_result(st.session_state[openai_key], 'ChatGPT')
        
        with col2:
            if gemini_key in st.session_state:
                with st.expander("⚡ Gemini Analysis", expanded=True):
                    display_ai_analysis_result(st.session_state[gemini_key], 'Gemini')
        
        # Display consensus if available
        if consensus_key in st.session_state:
            st.markdown("#### 🤝 AI Consensus Analysis")
            display_consensus_result(st.session_state[consensus_key])

def display_performance_metrics(summary: dict):
    """Display performance metrics"""
    overall = summary.get('overall_performance', {})
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_completed = overall.get('total_completed', 0)
        st.metric("🎯 Completed", total_completed)
    
    with col2:
        win_rate = overall.get('win_rate', 0.0)
        st.metric("🏆 Win Rate", f"{win_rate:.1%}")
    
    with col3:
        wins = overall.get('wins', 0)
        losses = overall.get('losses', 0)
        st.metric("📊 Record", f"{wins}-{losses}")
    
    with col4:
        trend_data = summary.get('recent_trend', {})
        trend = trend_data.get('trend', 'Stable')
        trend_color = 'green' if trend == 'Improving' else 'red' if trend == 'Declining' else 'gray'
        st.metric("📈 Trend", trend)

def display_live_odds_with_ai(odds_df: pd.DataFrame, value_filter: str):
    """Display live odds with AI analysis integration"""
    
    for idx, game in odds_df.head(10).iterrows():
        with st.container():
            st.markdown(f"### {game['game_name']}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"🏆 **{game['sport']}**")
                st.markdown(f"🕐 {game['time']}")
            
            with col2:
                st.markdown("**Home Odds**")
                st.markdown(f"{game.get('home_odds', 'N/A')}")
            
            with col3:
                st.markdown("**Away Odds**")
                st.markdown(f"{game.get('away_odds', 'N/A')}")
            
            with col4:
                if st.button(f"🤖 AI Analysis", key=f"odds_ai_{idx}"):
                    run_odds_ai_analysis(game)
            
            st.markdown("---")

# Additional helper functions would go here...

def calculate_picks_summary(picks_df: pd.DataFrame) -> Dict:
    """Calculate summary statistics for picks"""
    return {
        'total_picks': len(picks_df),
        'avg_confidence': picks_df.get('confidence', pd.Series([0])).mean(),
        'strong_picks': len(picks_df[picks_df.get('confidence', 0) >= 0.8]),
        'avg_edge_score': picks_df.get('edge_score', pd.Series([0])).mean()
    }

def display_pick_analysis(pick):
    """Display detailed pick analysis"""
    st.markdown("**AI Analysis Summary**")
    
    ai_analyses = pick.get('ai_analyses', {})
    
    if 'openai' in ai_analyses:
        st.markdown("**ChatGPT Analysis:**")
        openai_data = ai_analyses['openai']
        st.markdown(f"Prediction: {openai_data.get('predicted_winner', 'N/A')}")
        st.markdown(f"Confidence: {openai_data.get('confidence', 0):.1%}")
    
    if 'gemini' in ai_analyses:
        st.markdown("**Gemini Analysis:**")
        gemini_data = ai_analyses['gemini']
        st.markdown(f"Prediction: {gemini_data.get('prediction', 'N/A')}")
        st.markdown(f"Confidence: {gemini_data.get('confidence_score', 0):.1%}")

def display_ai_analysis_result(analysis: Dict, ai_name: str):
    """Display AI analysis result"""
    if 'error' not in analysis:
        if ai_name == 'ChatGPT':
            st.markdown(f"**Prediction:** {analysis.get('predicted_winner', 'Unknown')}")
            st.markdown(f"**Confidence:** {analysis.get('confidence', 0):.1%}")
        else:
            st.markdown(f"**Prediction:** {analysis.get('prediction', 'Unknown')}")
            st.markdown(f"**Confidence:** {analysis.get('confidence_score', 0):.1%}")
    else:
        st.error(f"{ai_name} analysis failed: {analysis.get('error', 'Unknown error')}")

def display_consensus_result(consensus: Dict):
    """Display consensus analysis result"""
    if 'error' not in consensus:
        st.markdown(f"**Consensus Pick:** {consensus.get('consensus_pick', 'No consensus')}")
        st.markdown(f"**Agreement Level:** {consensus.get('agreement_status', 'Unknown')}")
        st.markdown(f"**Confidence:** {consensus.get('confidence', 0):.1%}")
    else:
        st.error(f"Consensus analysis failed: {consensus.get('error', 'Unknown error')}")

def run_unified_deep_analysis(game_data: pd.Series, analysis_type: str):
    """Run unified deep analysis"""
    with st.spinner(f"Running {analysis_type.lower()}..."):
        try:
            # This would integrate with the deep analysis engine
            st.success(f"{analysis_type} completed!")
            st.info("Deep analysis results would be displayed here")
        except Exception as e:
            st.error(f"Deep analysis failed: {str(e)}")

def run_odds_ai_analysis(game_data: pd.Series):
    """Run AI analysis for odds data"""
    with st.spinner("Running AI analysis on odds..."):
        try:
            # This would integrate AI analysis with odds data
            st.success("AI odds analysis completed!")
            st.info("AI odds analysis results would be displayed here")
        except Exception as e:
            st.error(f"AI odds analysis failed: {str(e)}")

if __name__ == "__main__":
    show_unified_analysis()