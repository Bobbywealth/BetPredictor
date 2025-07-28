import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.cache_manager import OptimizedDataLoader, BatchAnalysisManager
from utils.deep_analysis import DeepGameAnalyzer
from utils.odds_api import OddsAPIManager
from utils.ai_analysis import AIGameAnalyzer

def show_deep_analysis_dashboard():
    """Comprehensive deep analysis dashboard for all games"""
    
    st.title("🔍 Deep Game Analysis Dashboard")
    st.markdown("Comprehensive analysis for all games with AI insights, betting odds, and performance metrics")
    
    # Initialize optimized systems
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = OptimizedDataLoader()
    
    if 'deep_analyzer' not in st.session_state:
        st.session_state.deep_analyzer = DeepGameAnalyzer()
    
    if 'batch_analyzer' not in st.session_state:
        st.session_state.batch_analyzer = BatchAnalysisManager()
    
    if 'odds_manager' not in st.session_state:
        st.session_state.odds_manager = OddsAPIManager()
    
    # Performance controls
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        selected_date = st.date_input(
            "📅 Analysis Date",
            value=date.today(),
            min_value=date.today(),
            max_value=date.today() + timedelta(days=14),
            key="deep_analysis_date"
        )
    
    with col2:
        analysis_depth = st.selectbox(
            "🎯 Analysis Depth",
            options=["Quick Overview", "Standard Analysis", "Deep Analysis", "Complete Analysis"],
            index=2,
            key="analysis_depth"
        )
    
    with col3:
        max_games = st.number_input(
            "Max Games",
            min_value=5,
            max_value=50,
            value=20,
            step=5,
            key="max_games_analysis"
        )
    
    with col4:
        if st.button("🚀 Analyze", type="primary"):
            # Clear analysis cache to force refresh
            st.session_state.data_loader.cache.clear_cache("comprehensive_analysis")
            st.rerun()
    
    # Load data efficiently
    date_str = selected_date.strftime('%Y-%m-%d')
    
    with st.spinner("Loading games with optimized caching..."):
        # Load games with caching
        games_df = st.session_state.data_loader.load_games_with_cache(date_str)
        
        # Load odds with caching
        odds_df = st.session_state.data_loader.load_odds_with_cache()
        
        # Merge games with odds data
        if len(odds_df) > 0:
            # Merge on team names and date
            merged_df = merge_games_with_odds(games_df, odds_df, selected_date)
        else:
            merged_df = games_df
    
    if len(merged_df) == 0:
        st.warning(f"No games found for {selected_date.strftime('%B %d, %Y')}")
        return
    
    # Limit games for performance
    display_df = merged_df.head(max_games)
    
    # Perform analysis based on depth
    with st.spinner(f"Performing {analysis_depth.lower()}..."):
        if analysis_depth == "Quick Overview":
            analyzed_df = st.session_state.batch_analyzer.analyze_games_batch(display_df, 'basic')
        elif analysis_depth == "Standard Analysis":
            analyzed_df = st.session_state.batch_analyzer.analyze_games_batch(display_df, 'advanced')
        elif analysis_depth == "Deep Analysis":
            analyzed_df = st.session_state.deep_analyzer.perform_comprehensive_analysis(display_df)
        else:  # Complete Analysis
            analyzed_df = st.session_state.deep_analyzer.perform_comprehensive_analysis(display_df)
            analyzed_df = st.session_state.deep_analyzer.batch_ai_analysis(analyzed_df, max_games=min(10, len(analyzed_df)))
    
    # Display results
    show_analysis_results(analyzed_df, analysis_depth)

def merge_games_with_odds(games_df: pd.DataFrame, odds_df: pd.DataFrame, target_date: date) -> pd.DataFrame:
    """Efficiently merge games with odds data"""
    if len(games_df) == 0 or len(odds_df) == 0:
        return games_df
    
    # Filter odds for target date
    odds_date_str = target_date.strftime('%Y-%m-%d')
    filtered_odds = odds_df[odds_df['date'] == odds_date_str] if 'date' in odds_df.columns else odds_df
    
    # Create merge keys
    if 'home_team' in games_df.columns and 'away_team' in games_df.columns:
        games_df['merge_key'] = games_df.apply(
            lambda x: f"{x.get('away_team', {}).get('name', '') if isinstance(x.get('away_team'), dict) else x.get('away_team', '')}_{x.get('home_team', {}).get('name', '') if isinstance(x.get('home_team'), dict) else x.get('home_team', '')}", 
            axis=1
        )
    
    if 'home_team' in filtered_odds.columns and 'away_team' in filtered_odds.columns:
        filtered_odds['merge_key'] = filtered_odds.apply(
            lambda x: f"{x.get('away_team', '')}_{x.get('home_team', '')}", 
            axis=1
        )
    
    # Merge data
    if 'merge_key' in games_df.columns and 'merge_key' in filtered_odds.columns:
        merged_df = games_df.merge(
            filtered_odds[['merge_key', 'home_odds', 'away_odds', 'best_bookmaker']], 
            on='merge_key', 
            how='left'
        )
        merged_df = merged_df.drop('merge_key', axis=1)
        return merged_df
    
    return games_df

def show_analysis_results(analyzed_df: pd.DataFrame, analysis_depth: str):
    """Display comprehensive analysis results"""
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_games = len(analyzed_df)
        st.metric("Total Games Analyzed", total_games)
    
    with col2:
        if 'overall_rating' in analyzed_df.columns:
            avg_rating = analyzed_df['overall_rating'].mean()
            st.metric("Average Rating", f"{avg_rating:.1f}/10")
        else:
            st.metric("Analysis Complete", "✓")
    
    with col3:
        if 'priority_level' in analyzed_df.columns:
            high_priority = len(analyzed_df[analyzed_df['priority_level'].isin(['Must See', 'High Priority'])])
            st.metric("High Priority Games", high_priority)
        else:
            sports_count = analyzed_df['sport'].nunique() if 'sport' in analyzed_df.columns else 0
            st.metric("Sports Covered", sports_count)
    
    with col4:
        if 'ai_prediction' in analyzed_df.columns:
            ai_analyzed = len(analyzed_df[analyzed_df['ai_prediction'].notna() & (analyzed_df['ai_prediction'] != 'N/A')])
            st.metric("AI Analyzed", ai_analyzed)
        else:
            st.metric("Analysis Depth", analysis_depth)
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Games Overview", 
        "🎯 Top Recommendations", 
        "📈 Analysis Charts", 
        "🔍 Detailed Insights"
    ])
    
    with tab1:
        show_games_overview(analyzed_df)
    
    with tab2:
        show_top_recommendations(analyzed_df)
    
    with tab3:
        show_analysis_charts(analyzed_df)
    
    with tab4:
        show_detailed_insights(analyzed_df)

def show_games_overview(analyzed_df: pd.DataFrame):
    """Show comprehensive games overview"""
    st.markdown("### 📊 Games Analysis Overview")
    
    # Sort by overall rating or interest score
    sort_column = 'overall_rating' if 'overall_rating' in analyzed_df.columns else 'interest_score'
    if sort_column in analyzed_df.columns:
        display_df = analyzed_df.sort_values(sort_column, ascending=False)
    else:
        display_df = analyzed_df
    
    for idx, game in display_df.iterrows():
        with st.container():
            # Game header
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                # Team names
                if isinstance(game.get('home_team'), dict):
                    home_team = game.get('home_team', {}).get('name', 'Unknown')
                    away_team = game.get('away_team', {}).get('name', 'Unknown')
                else:
                    home_team = game.get('home_team', 'Unknown')
                    away_team = game.get('away_team', 'Unknown')
                
                st.markdown(f"**{away_team} @ {home_team}**")
                
                # Game details
                game_date = game.get('date', 'TBD')
                game_time = game.get('time', 'TBD')
                sport = game.get('sport', 'Unknown')
                league = game.get('league', 'Unknown')
                
                st.markdown(f"📅 {game_date} | 🕐 {game_time} | 🏆 {sport} ({league})")
            
            with col2:
                # Rating
                if 'overall_rating' in game.index:
                    rating = game.get('overall_rating', 5.0)
                    st.metric("Rating", f"{rating:.1f}/10")
                elif 'interest_score' in game.index:
                    score = game.get('interest_score', 5.0)
                    st.metric("Interest", f"{score:.1f}/10")
            
            with col3:
                # Priority or recommendation
                if 'priority_level' in game.index:
                    priority = game.get('priority_level', 'Medium')
                    color = get_priority_color(priority)
                    st.markdown(f"<span style='color:{color}; font-weight:bold'>{priority}</span>", unsafe_allow_html=True)
                elif 'viewing_rec' in game.index:
                    rec = game.get('viewing_rec', 'Worth Watching')
                    st.markdown(f"**{rec}**")
            
            with col4:
                # Odds or AI prediction
                if 'home_odds' in game.index and game.get('home_odds', 'N/A') != 'N/A':
                    home_odds = game.get('home_odds', 'N/A')
                    away_odds = game.get('away_odds', 'N/A')
                    st.markdown(f"**Odds Available**")
                    st.markdown(f"{home_odds} | {away_odds}")
                elif 'ai_prediction' in game.index and game.get('ai_prediction', 'N/A') != 'N/A':
                    ai_pred = game.get('ai_prediction', 'N/A')
                    ai_conf = game.get('ai_confidence', 0.0)
                    st.markdown(f"**AI: {ai_pred}**")
                    st.markdown(f"Conf: {ai_conf:.1%}")
            
            # Additional analysis if available
            if 'betting_value' in game.index or 'market_efficiency' in game.index:
                analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
                
                with analysis_col1:
                    if 'betting_value' in game.index:
                        betting_value = game.get('betting_value', 'N/A')
                        st.markdown(f"💰 Value: **{betting_value}**")
                
                with analysis_col2:
                    if 'competition_level' in game.index:
                        comp_level = game.get('competition_level', 'Standard')
                        st.markdown(f"🏆 Level: **{comp_level}**")
                
                with analysis_col3:
                    if 'momentum_factor' in game.index:
                        momentum = game.get('momentum_factor', 'Balanced')
                        st.markdown(f"📈 Momentum: **{momentum}**")
            
            # Deep insights button
            if st.button(f"🔍 Deep Insights", key=f"insights_{idx}_{hash(str(game))}"):
                show_game_deep_insights(game)
            
            st.markdown("---")

def show_top_recommendations(analyzed_df: pd.DataFrame):
    """Show top game recommendations"""
    st.markdown("### 🎯 Top Game Recommendations")
    
    # Sort by rating or priority
    if 'overall_rating' in analyzed_df.columns:
        top_games = analyzed_df.nlargest(10, 'overall_rating')
    elif 'interest_score' in analyzed_df.columns:
        top_games = analyzed_df.nlargest(10, 'interest_score')
    else:
        top_games = analyzed_df.head(10)
    
    for i, (idx, game) in enumerate(top_games.iterrows(), 1):
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 2])
            
            with col1:
                # Ranking
                if i <= 3:
                    medals = ["🥇", "🥈", "🥉"]
                    st.markdown(f"# {medals[i-1]}")
                else:
                    st.markdown(f"### #{i}")
            
            with col2:
                # Game info
                if isinstance(game.get('home_team'), dict):
                    home_team = game.get('home_team', {}).get('name', 'Unknown')
                    away_team = game.get('away_team', {}).get('name', 'Unknown')
                else:
                    home_team = game.get('home_team', 'Unknown')
                    away_team = game.get('away_team', 'Unknown')
                
                st.markdown(f"**{away_team} @ {home_team}**")
                
                # Why recommended
                reasons = []
                if 'entertainment_value' in game.index:
                    reasons.append(f"Entertainment: {game.get('entertainment_value', 'Good')}")
                if 'competition_level' in game.index:
                    reasons.append(f"Level: {game.get('competition_level', 'Standard')}")
                if 'betting_value' in game.index and game.get('betting_value') != 'N/A':
                    reasons.append(f"Value: {game.get('betting_value', 'Standard')}")
                
                if reasons:
                    st.markdown(" • ".join(reasons))
            
            with col3:
                # Rating and recommendation
                if 'overall_rating' in game.index:
                    rating = game.get('overall_rating', 5.0)
                    st.metric("Rating", f"{rating:.1f}/10")
                
                if 'priority_level' in game.index:
                    priority = game.get('priority_level', 'Medium')
                    color = get_priority_color(priority)
                    st.markdown(f"<div style='text-align:center; color:{color}; font-weight:bold'>{priority}</div>", unsafe_allow_html=True)
            
            st.markdown("---")

def show_analysis_charts(analyzed_df: pd.DataFrame):
    """Show analysis visualization charts"""
    st.markdown("### 📈 Analysis Visualizations")
    
    if len(analyzed_df) == 0:
        st.info("No data available for visualization")
        return
    
    # Charts based on available data
    col1, col2 = st.columns(2)
    
    with col1:
        if 'overall_rating' in analyzed_df.columns:
            # Rating distribution
            fig = px.histogram(
                analyzed_df, 
                x='overall_rating',
                title='Game Rating Distribution',
                nbins=10,
                labels={'overall_rating': 'Overall Rating', 'count': 'Number of Games'}
            )
            st.plotly_chart(fig, use_container_width=True)
        elif 'interest_score' in analyzed_df.columns:
            # Interest score distribution
            fig = px.histogram(
                analyzed_df, 
                x='interest_score',
                title='Interest Score Distribution',
                nbins=10
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'sport' in analyzed_df.columns:
            # Games by sport
            sport_counts = analyzed_df['sport'].value_counts()
            fig = px.pie(
                values=sport_counts.values,
                names=sport_counts.index,
                title='Games by Sport'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Additional charts based on analysis depth
    if 'priority_level' in analyzed_df.columns:
        priority_counts = analyzed_df['priority_level'].value_counts()
        fig = px.bar(
            x=priority_counts.index,
            y=priority_counts.values,
            title='Games by Priority Level',
            labels={'x': 'Priority Level', 'y': 'Number of Games'}
        )
        st.plotly_chart(fig, use_container_width=True)

def show_detailed_insights(analyzed_df: pd.DataFrame):
    """Show detailed analysis insights"""
    st.markdown("### 🔍 Detailed Analysis Insights")
    
    # Select game for detailed insights
    game_options = {}
    for idx, game in analyzed_df.iterrows():
        if isinstance(game.get('home_team'), dict):
            home_team = game.get('home_team', {}).get('name', 'Unknown')
            away_team = game.get('away_team', {}).get('name', 'Unknown')
        else:
            home_team = game.get('home_team', 'Unknown')
            away_team = game.get('away_team', 'Unknown')
        
        display_name = f"{away_team} @ {home_team} ({game.get('sport', 'Unknown')})"
        game_options[display_name] = idx
    
    if game_options:
        selected_game_name = st.selectbox(
            "Select game for detailed insights:",
            options=list(game_options.keys()),
            key="detailed_insights_selector"
        )
        
        if selected_game_name:
            game_idx = game_options[selected_game_name]
            selected_game = analyzed_df.loc[game_idx]
            
            show_game_deep_insights(selected_game)

def show_game_deep_insights(game_data: pd.Series):
    """Show deep insights for a specific game"""
    
    if 'deep_analyzer' not in st.session_state:
        st.session_state.deep_analyzer = DeepGameAnalyzer()
    
    with st.spinner("Generating deep insights..."):
        insights = st.session_state.deep_analyzer.get_game_deep_insights(game_data)
    
    # Display insights in organized sections
    col1, col2 = st.columns(2)
    
    with col1:
        # Statistical breakdown
        st.markdown("#### 📊 Statistical Breakdown")
        stats = insights.get('statistical_breakdown', {})
        for key, value in stats.items():
            st.markdown(f"**{key.replace('_', ' ').title()}**: {value}")
        
        # Market sentiment
        st.markdown("#### 💰 Market Analysis")
        market = insights.get('market_sentiment', {})
        for key, value in market.items():
            st.markdown(f"**{key.replace('_', ' ').title()}**: {value}")
    
    with col2:
        # Key factors
        st.markdown("#### 🔑 Key Factors")
        factors = insights.get('key_factors', [])
        for factor in factors:
            st.markdown(f"• {factor}")
        
        # Risk assessment
        st.markdown("#### ⚠️ Risk Assessment")
        risks = insights.get('risk_assessment', {})
        for key, value in risks.items():
            st.markdown(f"**{key.replace('_', ' ').title()}**: {value}")
    
    # Additional insights
    if 'value_proposition' in insights:
        st.markdown("#### 💎 Value Proposition")
        value_prop = insights['value_proposition']
        for key, value in value_prop.items():
            st.markdown(f"**{key.replace('_', ' ').title()}**: {value}")
    
    if 'betting_angles' in insights:
        st.markdown("#### 🎯 Key Analysis Points")
        angles = insights['betting_angles']
        for angle in angles:
            st.markdown(f"• {angle}")

def get_priority_color(priority: str) -> str:
    """Get color for priority level"""
    colors = {
        'Must See': '#FF4B4B',
        'High Priority': '#FF8C00', 
        'Medium Priority': '#FFA500',
        'Low Priority': '#90EE90'
    }
    return colors.get(priority, '#666666')

if __name__ == "__main__":
    show_deep_analysis_dashboard()