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

def show_winning_picks():
    """Display high-confidence winning picks with dual AI consensus"""
    
    st.title("🏆 High-Confidence Winning Picks")
    st.markdown("**Advanced dual AI consensus system combining ChatGPT & Gemini for maximum accuracy**")
    
    # Responsible gambling warning
    st.warning("""
    ⚠️ **RESPONSIBLE GAMBLING NOTICE**: These are analytical insights for educational purposes only. 
    Sports betting involves risk. Never bet more than you can afford to lose. 
    Please gamble responsibly.
    """)
    
    # Initialize systems
    if 'picks_generator' not in st.session_state:
        st.session_state.picks_generator = WinningPicksGenerator()
    
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = OptimizedDataLoader()
    
    if 'odds_manager' not in st.session_state:
        st.session_state.odds_manager = OddsAPIManager()
    
    if 'result_tracker' not in st.session_state:
        st.session_state.result_tracker = GameResultTracker()
    
    # Controls
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        pick_date = st.date_input(
            "📅 Pick Date",
            value=date.today(),
            min_value=date.today(),
            max_value=date.today() + timedelta(days=7),
            key="winning_picks_date"
        )
    
    with col2:
        sports_filter = st.multiselect(
            "🏈 Sports",
            options=['NFL', 'NBA', 'MLB', 'NHL', 'WNBA'],
            default=['NFL', 'NBA', 'MLB'],
            key="sports_filter_picks"
        )
    
    with col3:
        max_picks = st.number_input(
            "Max Picks",
            min_value=1,
            max_value=10,
            value=5,
            key="max_picks"
        )
    
    with col4:
        if st.button("🚀 Generate Picks", type="primary"):
            # Clear cache to force fresh analysis
            st.session_state.picks_generator.cache.clear_cache("daily_picks")
            st.rerun()
    
    # Load games data
    date_str = pick_date.strftime('%Y-%m-%d')
    
    with st.spinner("Loading games with live odds..."):
        # Load games efficiently
        games_df = st.session_state.data_loader.load_games_with_cache(date_str, sports_filter)
        
        # Load and merge odds
        if len(games_df) > 0:
            odds_df = st.session_state.data_loader.load_odds_with_cache()
            if len(odds_df) > 0:
                # Merge games with odds
                games_df = merge_with_odds_data(games_df, odds_df, pick_date)
    
    if len(games_df) == 0:
        st.info(f"No games found for {pick_date.strftime('%B %d, %Y')} in selected sports")
        return
    
    # Generate winning picks
    st.markdown("---")
    
    with st.spinner("🤖 Analyzing with dual AI system (ChatGPT + Gemini)..."):
        picks_df = st.session_state.picks_generator.generate_daily_picks(games_df, max_picks)
    
    if len(picks_df) == 0:
        st.warning("No high-confidence picks identified for today. Check back later or adjust criteria.")
        return
    
    # Display results
    display_winning_picks(picks_df)

def merge_with_odds_data(games_df: pd.DataFrame, odds_df: pd.DataFrame, target_date: date) -> pd.DataFrame:
    """Merge games with odds data efficiently"""
    if len(games_df) == 0 or len(odds_df) == 0:
        return games_df
    
    try:
        # Filter odds for target date
        date_str = target_date.strftime('%Y-%m-%d')
        filtered_odds = odds_df[odds_df['date'] == date_str] if 'date' in odds_df.columns else odds_df
        
        # Create merge keys
        def create_merge_key(row):
            home = row.get('home_team', {}).get('name', '') if isinstance(row.get('home_team'), dict) else str(row.get('home_team', ''))
            away = row.get('away_team', {}).get('name', '') if isinstance(row.get('away_team'), dict) else str(row.get('away_team', ''))
            return f"{away.lower().strip()}_{home.lower().strip()}"
        
        games_df['merge_key'] = games_df.apply(create_merge_key, axis=1)
        
        if 'home_team' in filtered_odds.columns and 'away_team' in filtered_odds.columns:
            filtered_odds['merge_key'] = filtered_odds.apply(
                lambda x: f"{str(x.get('away_team', '')).lower().strip()}_{str(x.get('home_team', '')).lower().strip()}", 
                axis=1
            )
            
            # Merge
            odds_cols = ['merge_key', 'home_odds', 'away_odds', 'best_bookmaker']
            available_cols = [col for col in odds_cols if col in filtered_odds.columns]
            
            merged_df = games_df.merge(
                filtered_odds[available_cols], 
                on='merge_key', 
                how='left'
            )
            
            return merged_df.drop('merge_key', axis=1)
    
    except Exception as e:
        st.error(f"Error merging odds data: {e}")
    
    return games_df

def display_winning_picks(picks_df: pd.DataFrame):
    """Display winning picks with comprehensive analysis"""
    
    # Summary metrics
    summary = st.session_state.picks_generator.get_pick_summary(picks_df)
    
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
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Top Picks", 
        "🤖 AI Analysis", 
        "📊 Pick Analytics", 
        "📋 Detailed Breakdown"
    ])
    
    with tab1:
        show_top_picks(picks_df)
    
    with tab2:
        show_ai_consensus_analysis(picks_df)
    
    with tab3:
        show_picks_analytics(picks_df, summary)
    
    with tab4:
        show_detailed_breakdown(picks_df)

def show_top_picks(picks_df: pd.DataFrame):
    """Display top picks with rankings"""
    st.markdown("### 🏆 Today's Top Winning Picks")
    
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
                # Pick header
                st.markdown(f"### {pick['away_team']} @ {pick['home_team']}")
                
                # Game details
                col2a, col2b, col2c = st.columns(3)
                with col2a:
                    st.markdown(f"🏆 **{pick['sport']}**")
                    st.markdown(f"📅 {pick['date']} | 🕐 {pick['time']}")
                
                with col2b:
                    st.markdown(f"🎯 **Pick: {pick['consensus_pick']}**")
                    confidence = pick['confidence']
                    conf_color = get_confidence_color(confidence)
                    st.markdown(f"📈 <span style='color:{conf_color}; font-weight:bold'>Confidence: {confidence:.1%}</span>", unsafe_allow_html=True)
                
                with col2c:
                    strength = pick['recommendation_strength']
                    strength_color = get_strength_color(strength)
                    st.markdown(f"💪 <span style='color:{strength_color}; font-weight:bold'>{strength}</span>", unsafe_allow_html=True)
                    st.markdown(f"⚡ Edge Score: **{pick['edge_score']:.2f}**")
                
                # AI Analysis Summary
                agreement_status = pick['agreement_status']
                if agreement_status == 'STRONG_CONSENSUS':
                    st.success("🤖 **Both ChatGPT and Gemini strongly agree**")
                elif agreement_status in ['SINGLE_AI_OPENAI', 'SINGLE_AI_GEMINI']:
                    ai_name = 'ChatGPT' if 'OPENAI' in agreement_status else 'Gemini'
                    st.info(f"🤖 **Strong {ai_name} analysis**")
                elif agreement_status == 'DISAGREEMENT':
                    st.warning("⚠️ **AI models disagree - proceed with caution**")
                
                # Key reasoning
                reasoning = pick.get('pick_reasoning', [])
                if reasoning:
                    st.markdown("**Key Analysis Points:**")
                    for reason in reasoning[:3]:  # Show top 3 reasons
                        st.markdown(f"• {reason}")
                
                # Success metrics
                col3a, col3b, col3c = st.columns(3)
                with col3a:
                    success_prob = pick['success_probability']
                    st.metric("Success Probability", f"{success_prob:.1%}")
                
                with col3b:
                    value_rating = pick['value_rating']
                    value_color = get_value_color(value_rating)
                    st.markdown(f"**Value Rating**")
                    st.markdown(f"<span style='color:{value_color}; font-weight:bold'>{value_rating}</span>", unsafe_allow_html=True)
                
                with col3c:
                    action = pick['recommendation_action']
                    st.markdown(f"**Recommendation**")
                    st.markdown(f"**{action.replace('_', ' ').title()}**")
            
            # Action buttons  
            button_col1, button_col2 = st.columns(2)
            
            with button_col1:
                # Expandable detailed analysis
                with st.expander("🔍 View Detailed AI Analysis"):
                    show_individual_pick_analysis(pick)
            
            with button_col2:
                # Track prediction button
                if st.button(f"📊 Track This Pick", key=f"track_{i}_{hash(str(pick))}"):
                    tracking_id = st.session_state.result_tracker.track_prediction(pick.to_dict())
                    st.success(f"✅ Prediction tracked! ID: {tracking_id[:8]}...")
                    st.info("Check the Performance Tracking page to monitor results")
            
            st.markdown("---")

def show_ai_consensus_analysis(picks_df: pd.DataFrame):
    """Show detailed AI consensus analysis"""
    st.markdown("### 🤖 Dual AI Consensus Analysis")
    
    # Consensus breakdown
    consensus_counts = picks_df['agreement_status'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Consensus pie chart
        fig = px.pie(
            values=consensus_counts.values,
            names=[status.replace('_', ' ').title() for status in consensus_counts.index],
            title="AI Agreement Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Confidence distribution
        fig = px.histogram(
            picks_df,
            x='confidence',
            nbins=10,
            title="Confidence Distribution",
            labels={'confidence': 'Confidence Level', 'count': 'Number of Picks'}
        )
        fig.update_xaxis(tickformat='.0%')
        st.plotly_chart(fig, use_container_width=True)
    
    # AI Analysis Comparison
    st.markdown("#### 🔍 ChatGPT vs Gemini Analysis")
    
    for idx, pick in picks_df.iterrows():
        with st.expander(f"{pick['away_team']} @ {pick['home_team']} - AI Comparison"):
            
            full_analysis = pick.get('full_analysis', {})
            ai_analyses = full_analysis.get('ai_analyses', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 🧠 ChatGPT Analysis")
                openai_analysis = ai_analyses.get('openai', {})
                
                if 'error' not in openai_analysis:
                    st.markdown(f"**Prediction:** {openai_analysis.get('predicted_winner', 'N/A')}")
                    st.markdown(f"**Confidence:** {openai_analysis.get('confidence', 0):.1%}")
                    
                    # Key factors
                    factors = openai_analysis.get('key_factors', [])
                    if factors:
                        st.markdown("**Key Factors:**")
                        for factor in factors[:3]:
                            st.markdown(f"• {factor}")
                    
                    # Analysis snippet
                    analysis_text = openai_analysis.get('analysis', '')
                    if analysis_text and len(analysis_text) > 50:
                        st.markdown(f"**Analysis:** {analysis_text[:200]}...")
                else:
                    st.error("ChatGPT analysis failed")
            
            with col2:
                st.markdown("##### 🔮 Gemini Analysis")
                gemini_analysis = ai_analyses.get('gemini', {})
                
                if 'error' not in gemini_analysis:
                    st.markdown(f"**Prediction:** {gemini_analysis.get('prediction', 'N/A')}")
                    st.markdown(f"**Confidence:** {gemini_analysis.get('confidence_score', 0):.1%}")
                    
                    # Critical factors
                    factors = gemini_analysis.get('critical_factors', [])
                    if factors:
                        st.markdown("**Critical Factors:**")
                        for factor in factors[:3]:
                            st.markdown(f"• {factor}")
                    
                    # Analysis snippet
                    analysis_text = gemini_analysis.get('detailed_analysis', '')
                    if analysis_text and len(analysis_text) > 50:
                        st.markdown(f"**Analysis:** {analysis_text[:200]}...")
                else:
                    st.error("Gemini analysis failed")

def show_picks_analytics(picks_df: pd.DataFrame, summary: Dict):
    """Show pick analytics and statistics"""
    st.markdown("### 📊 Pick Analytics & Statistics")
    
    # Success metrics visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Confidence vs Edge Score",
            "Success Probability Distribution", 
            "Recommendation Strength",
            "Value Rating Distribution"
        ),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Scatter plot: Confidence vs Edge Score
    fig.add_trace(
        go.Scatter(
            x=picks_df['confidence'],
            y=picks_df['edge_score'],
            mode='markers+text',
            text=picks_df['away_team'] + ' @ ' + picks_df['home_team'],
            textposition="top center",
            marker=dict(
                size=picks_df['success_probability'] * 50,
                color=picks_df['composite_score'],
                colorscale='Viridis',
                showscale=True
            ),
            name="Games"
        ),
        row=1, col=1
    )
    
    # Success probability histogram
    fig.add_trace(
        go.Histogram(
            x=picks_df['success_probability'],
            nbinsx=8,
            name="Success Probability"
        ),
        row=1, col=2
    )
    
    # Recommendation strength
    strength_counts = picks_df['recommendation_strength'].value_counts()
    fig.add_trace(
        go.Bar(
            x=strength_counts.index,
            y=strength_counts.values,
            name="Strength Distribution"
        ),
        row=2, col=1
    )
    
    # Value rating
    value_counts = picks_df['value_rating'].value_counts()
    fig.add_trace(
        go.Bar(
            x=value_counts.index,
            y=value_counts.values,
            name="Value Distribution"
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Performance Metrics")
        st.json({
            "Average Confidence": f"{summary.get('avg_confidence', 0):.1%}",
            "Average Edge Score": f"{summary.get('avg_edge_score', 0):.3f}",
            "Average Success Probability": f"{summary.get('avg_success_prob', 0):.1%}",
            "Strong Recommendation Rate": f"{summary.get('strong_picks', 0) / summary.get('total_picks', 1) * 100:.1f}%"
        })
    
    with col2:
        st.markdown("#### 🏈 Distribution Breakdown")
        st.json({
            "Sports": summary.get('sports_breakdown', {}),
            "Recommendations": summary.get('recommendation_breakdown', {}),
            "AI Consensus": summary.get('consensus_breakdown', {})
        })

def show_detailed_breakdown(picks_df: pd.DataFrame):
    """Show detailed breakdown of all picks"""
    st.markdown("### 📋 Detailed Pick Breakdown")
    
    # Interactive dataframe
    display_columns = [
        'away_team', 'home_team', 'sport', 'consensus_pick', 
        'confidence', 'edge_score', 'success_probability',
        'value_rating', 'recommendation_action', 'agreement_status'
    ]
    
    available_columns = [col for col in display_columns if col in picks_df.columns]
    
    # Format the display dataframe
    display_df = picks_df[available_columns].copy()
    
    # Format percentage columns
    if 'confidence' in display_df.columns:
        display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.1%}")
    if 'success_probability' in display_df.columns:
        display_df['success_probability'] = display_df['success_probability'].apply(lambda x: f"{x:.1%}")
    if 'edge_score' in display_df.columns:
        display_df['edge_score'] = display_df['edge_score'].apply(lambda x: f"{x:.3f}")
    
    # Rename columns for display
    column_renames = {
        'away_team': 'Away Team',
        'home_team': 'Home Team',
        'sport': 'Sport',
        'consensus_pick': 'AI Pick',
        'confidence': 'Confidence',
        'edge_score': 'Edge Score',
        'success_probability': 'Success Prob',
        'value_rating': 'Value Rating',
        'recommendation_action': 'Recommendation',
        'agreement_status': 'AI Agreement'
    }
    
    display_df = display_df.rename(columns=column_renames)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Export functionality
    csv_data = picks_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Picks as CSV",
        data=csv_data,
        file_name=f"winning_picks_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

def show_individual_pick_analysis(pick):
    """Show detailed analysis for individual pick"""
    
    full_analysis = pick.get('full_analysis', {})
    
    # Success metrics
    success_metrics = full_analysis.get('success_metrics', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Success Metrics")
        st.json({
            "Edge Score": f"{success_metrics.get('edge_score', 0):.3f}",
            "Success Probability": f"{success_metrics.get('success_probability', 0):.1%}",
            "Kelly Criterion": f"{success_metrics.get('kelly_criterion', 0):.3f}",
            "Expected Value": f"{success_metrics.get('expected_value', 0):.3f}",
            "Risk Level": success_metrics.get('risk_level', 'Unknown')
        })
    
    with col2:
        st.markdown("#### 🎯 Recommendation Details")
        recommendation = full_analysis.get('recommendation', {})
        st.json({
            "Action": recommendation.get('action', 'Unknown'),
            "Strength": recommendation.get('strength', 'Unknown'),
            "Risk Warning": recommendation.get('risk_warning', True)
        })
    
    # Reasoning
    reasoning = recommendation.get('reasoning', [])
    if reasoning:
        st.markdown("#### 💡 Recommendation Reasoning")
        for reason in reasoning:
            st.markdown(f"• {reason}")

def get_confidence_color(confidence: float) -> str:
    """Get color based on confidence level"""
    if confidence >= 0.8:
        return '#00C851'  # Green
    elif confidence >= 0.65:
        return '#ffbb33'  # Orange
    else:
        return '#ff4444'  # Red

def get_strength_color(strength: str) -> str:
    """Get color based on recommendation strength"""
    colors = {
        'VERY_HIGH': '#00C851',
        'HIGH': '#007E33',
        'MEDIUM': '#ffbb33',
        'LOW': '#ff4444',
        'WEAK': '#666666'
    }
    return colors.get(strength, '#666666')

def get_value_color(value_rating: str) -> str:
    """Get color based on value rating"""
    colors = {
        'EXCELLENT': '#00C851',
        'GOOD': '#007E33',
        'FAIR': '#ffbb33',
        'POOR': '#ff4444'
    }
    return colors.get(value_rating, '#666666')

if __name__ == "__main__":
    show_winning_picks()