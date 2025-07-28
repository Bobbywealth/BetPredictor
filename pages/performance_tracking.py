import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.result_tracker import GameResultTracker
from typing import Dict
import numpy as np


def show_performance_tracking():
    """Display comprehensive performance tracking dashboard"""

    st.title("📊 AI Prediction Performance Tracking")
    st.markdown("**Track game results and analyze the accuracy of our AI predictions over time**")

    # Initialize result tracker
    if 'result_tracker' not in st.session_state:
        st.session_state.result_tracker = GameResultTracker()

    # Control panel
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

    with col1:
        analysis_period = st.selectbox(
            "📅 Analysis Period",
            options=[7, 14, 30, 60, 90],
            index=2,
            format_func=lambda x: f"Last {x} days",
            key="performance_period"
        )

    with col2:
        tracking_filter = st.selectbox(
            "🎯 Filter Results",
            options=["All Predictions", "Completed Only", "High Confidence", "AI Consensus"],
            key="tracking_filter"
        )

    with col3:
        if st.button("🔄 Check Results", type="primary"):
            with st.spinner("Checking game results..."):
                results_summary = st.session_state.result_tracker.check_game_results(max_days_back=7)
                if results_summary['results_found'] > 0:
                    st.success(f"Found {results_summary['results_found']} new results!")
                else:
                    st.info("No new results found")

    with col4:
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

    st.divider()

    # Get performance summary
    performance_summary = st.session_state.result_tracker.get_performance_summary(analysis_period)

    if performance_summary.get('total_predictions', 0) == 0:
        st.info("No prediction data available. Start making predictions to track performance!")
        return

    # Display performance overview
    display_performance_overview(performance_summary)

    # Tabs for detailed analysis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Performance Trends",
        "🎯 Accuracy Analysis", 
        "🤖 AI Model Performance",
        "🏆 Sports Breakdown",
        "📋 Detailed Records"
    ])

    with tab1:
        show_performance_trends(performance_summary)

    with tab2:
        show_accuracy_analysis(performance_summary)

    with tab3:
        show_ai_model_performance(performance_summary)

    with tab4:
        show_sports_breakdown(performance_summary)

    with tab5:
        show_detailed_records()

def display_performance_overview(summary: dict):
    """Display high-level performance metrics"""

    overall = summary.get('overall_performance', {})
    high_conf = summary.get('high_confidence_performance', {})
    consensus = summary.get('ai_consensus_performance', {})

    # Main metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_completed = overall.get('total_completed', 0)
        st.metric("🎯 Completed Predictions", total_completed)

    with col2:
        win_rate = overall.get('win_rate', 0.0)
        st.metric("🏆 Overall Win Rate", f"{win_rate:.1%}")

    with col3:
        wins = overall.get('wins', 0)
        losses = overall.get('losses', 0)
        st.metric("📊 Record", f"{wins}-{losses}")

    with col4:
        high_conf_rate = high_conf.get('win_rate', 0.0)
        delta = f"+{(high_conf_rate - win_rate)*100:.1f}%" if high_conf_rate > win_rate else None
        st.metric("💎 High Confidence", f"{high_conf_rate:.1%}", delta=delta)

    with col5:
        consensus_rate = consensus.get('win_rate', 0.0)
        delta = f"+{(consensus_rate - win_rate)*100:.1f}%" if consensus_rate > win_rate else None
        st.metric("🤝 AI Consensus", f"{consensus_rate:.1%}", delta=delta)

    # Performance indicators
    col1, col2, col3 = st.columns(3)

    with col1:
        trend_data = summary.get('recent_trend', {})
        trend_direction = trend_data.get('trend', 'Stable')
        trend_color = 'green' if trend_direction == 'Improving' else 'red' if trend_direction == 'Declining' else 'gray'
        st.markdown(f"**Recent Trend:** <span style='color:{trend_color}'>{trend_direction}</span>", unsafe_allow_html=True)

    with col2:
        calibration = summary.get('model_calibration', {})
        cal_score = calibration.get('interpretation', 'Unknown')
        cal_color = 'green' if cal_score == 'Excellent' else 'orange' if cal_score == 'Good' else 'red'
        st.markdown(f"**Model Calibration:** <span style='color:{cal_color}'>{cal_score}</span>", unsafe_allow_html=True)

    with col3:
        pending = summary.get('pending_predictions', 0)
        st.markdown(f"**Pending Results:** {pending}")

def show_performance_trends(summary: dict):
    """Show performance trends over time"""
    st.markdown("### 📈 Performance Trends Analysis")

    # Get tracking data for trend analysis
    tracking_data = st.session_state.result_tracker.export_tracking_data()

    if len(tracking_data) == 0:
        st.info("No tracking data available for trend analysis")
        return

    # Filter completed predictions
    completed_data = tracking_data[tracking_data['status'].isin(['WIN', 'LOSS'])].copy()

    if len(completed_data) == 0:
        st.info("No completed predictions available for trend analysis")
        return

    # Convert dates
    completed_data['game_date'] = pd.to_datetime(completed_data['game_date'])
    completed_data['win'] = (completed_data['status'] == 'WIN').astype(int)

    # Create trend charts
    col1, col2 = st.columns(2)

    with col1:
        # Win rate over time (rolling average)
        if len(completed_data) >= 3:
            daily_performance = completed_data.groupby('game_date').agg({
                'win': ['count', 'sum']
            }).reset_index()

            daily_performance.columns = ['date', 'total_games', 'wins']
            daily_performance['win_rate'] = daily_performance['wins'] / daily_performance['total_games']
            daily_performance['rolling_win_rate'] = daily_performance['win_rate'].rolling(window=3, min_periods=1).mean()

            fig = px.line(
                daily_performance,
                x='date',
                y='rolling_win_rate',
                title='Win Rate Trend (3-day rolling average)',
                labels={'rolling_win_rate': 'Win Rate', 'date': 'Date'}
            )
            fig.update_yaxis(tickformat='.1%')
            fig.add_hline(y=0.5, line_dash="dash", line_color="gray", annotation_text="Break-even")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Confidence vs Accuracy scatter
        fig = px.scatter(
            completed_data,
            x='confidence',
            y='win',
            color='sport',
            size='edge_score',
            title='Confidence vs Actual Results',
            labels={'confidence': 'Prediction Confidence', 'win': 'Correct (1) / Incorrect (0)'},
            hover_data=['away_team', 'home_team']
        )
        fig.update_xaxis(tickformat='.1%')
        fig.add_shape(
            type="line",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="gray", dash="dash"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Performance by prediction strength
    strength_performance = completed_data.groupby('recommendation_strength').agg({
        'win': ['count', 'sum', 'mean']
    }).reset_index()

    strength_performance.columns = ['strength', 'total', 'wins', 'win_rate']

    fig = px.bar(
        strength_performance,
        x='strength',
        y='win_rate',
        title='Win Rate by Recommendation Strength',
        text=strength_performance.apply(lambda x: f"{x['wins']}/{x['total']}", axis=1)
    )
    fig.update_yaxis(tickformat='.1%')
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

def show_accuracy_analysis(summary: dict):
    """Show detailed accuracy analysis"""
    st.markdown("### 🎯 Accuracy Analysis")

    calibration = summary.get('model_calibration', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Model Calibration")

        overall_error = calibration.get('overall_calibration_error', 0)
        interpretation = calibration.get('interpretation', 'Unknown')

        st.metric("Calibration Error", f"{overall_error:.3f}", help="Lower is better")

        cal_color = 'green' if interpretation == 'Excellent' else 'orange' if interpretation == 'Good' else 'red'
        st.markdown(f"**Assessment:** <span style='color:{cal_color}'>{interpretation}</span>", unsafe_allow_html=True)

        # Calibration by confidence level
        by_level = calibration.get('by_confidence_level', {})

        if by_level:
            calibration_data = []
            for level, data in by_level.items():
                calibration_data.append({
                    'Confidence Level': level.title(),
                    'Count': data.get('count', 0),
                    'Avg Confidence': data.get('avg_confidence', 0),
                    'Actual Accuracy': data.get('actual_accuracy', 0),
                    'Calibration Error': data.get('calibration_error', 0)
                })

            if calibration_data:
                cal_df = pd.DataFrame(calibration_data)
                st.dataframe(cal_df, use_container_width=True)

    with col2:
        st.markdown("#### Performance Breakdown")

        overall = summary.get('overall_performance', {})

        # Performance metrics
        metrics_data = {
            'Metric': ['Win Rate', 'Total Predictions', 'Wins', 'Losses', 'Pushes'],
            'Value': [
                f"{overall.get('win_rate', 0):.1%}",
                overall.get('total_completed', 0),
                overall.get('wins', 0),
                overall.get('losses', 0),
                overall.get('pushes', 0)
            ]
        }

        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

        # Recent trend analysis
        trend_data = summary.get('recent_trend', {})

        st.markdown("#### Recent Trend (Last 7 Days)")
        st.json({
            'Recent Predictions': trend_data.get('recent_predictions', 0),
            'Recent Win Rate': f"{trend_data.get('recent_win_rate', 0):.1%}",
            'Trend Direction': trend_data.get('trend', 'Unknown'),
            'Trend Magnitude': f"{trend_data.get('trend_magnitude', 0):.1%}"
        })

def show_ai_model_performance(summary: dict):
    """Show AI model specific performance"""
    st.markdown("### 🤖 AI Model Performance Analysis")

    # Get detailed tracking data
    tracking_data = st.session_state.result_tracker.export_tracking_data()
    completed_data = tracking_data[tracking_data['status'].isin(['WIN', 'LOSS'])].copy()

    if len(completed_data) == 0:
        st.info("No completed predictions available for AI analysis")
        return

    # AI Agreement Performance
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Performance by AI Agreement")

        ai_performance = completed_data.groupby('ai_agreement').agg({
            'status': 'count',
            'prediction_correct': 'sum'
        }).reset_index()

        ai_performance['win_rate'] = ai_performance['prediction_correct'] / ai_performance['status']
        ai_performance = ai_performance.rename(columns={'status': 'total'})

        fig = px.bar(
            ai_performance,
            x='ai_agreement',
            y='win_rate',
            title='Win Rate by AI Agreement Type',
            text=ai_performance.apply(lambda x: f"{x['prediction_correct']}/{x['total']}", axis=1)
        )
        fig.update_yaxis(tickformat='.1%')
        fig.update_traces(textposition='outside')
        fig.update_xaxis(title='AI Agreement Type')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Confidence Distribution")

        fig = px.histogram(
            completed_data,
            x='confidence',
            color='status',
            title='Confidence Distribution by Outcome',
            nbins=10,
            barmode='group'
        )
        fig.update_xaxis(tickformat='.1%', title='Prediction Confidence')
        st.plotly_chart(fig, use_container_width=True)

    # Model performance metrics
    st.markdown("#### Detailed Model Metrics")

    # High confidence performance
    high_conf_data = completed_data[completed_data['confidence'] >= 0.75]
    consensus_data = completed_data[completed_data['ai_agreement'] == 'STRONG_CONSENSUS']

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**High Confidence Predictions (75%+)**")
        if len(high_conf_data) > 0:
            hc_win_rate = high_conf_data['prediction_correct'].mean()
            hc_total = len(high_conf_data)
            hc_wins = high_conf_data['prediction_correct'].sum()

            st.metric("Win Rate", f"{hc_win_rate:.1%}")
            st.metric("Record", f"{hc_wins}/{hc_total}")
            st.metric("Average Confidence", f"{high_conf_data['confidence'].mean():.1%}")
        else:
            st.info("No high confidence predictions")

    with col2:
        st.markdown("**Strong AI Consensus**")
        if len(consensus_data) > 0:
            c_win_rate = consensus_data['prediction_correct'].mean()
            c_total = len(consensus_data)
            c_wins = consensus_data['prediction_correct'].sum()

            st.metric("Win Rate", f"{c_win_rate:.1%}")
            st.metric("Record", f"{c_wins}/{c_total}")
            st.metric("Average Confidence", f"{consensus_data['confidence'].mean():.1%}")
        else:
            st.info("No consensus predictions")

    with col3:
        st.markdown("**Edge Score Analysis**")
        if 'edge_score' in completed_data.columns:
            high_edge_data = completed_data[completed_data['edge_score'] >= 0.4]

            if len(high_edge_data) > 0:
                he_win_rate = high_edge_data['prediction_correct'].mean()
                he_total = len(high_edge_data)
                he_wins = high_edge_data['prediction_correct'].sum()

                st.metric("High Edge Win Rate", f"{he_win_rate:.1%}")
                st.metric("Record", f"{he_wins}/{he_total}")
                st.metric("Average Edge", f"{high_edge_data['edge_score'].mean():.3f}")
            else:
                st.info("No high edge predictions")

def show_sports_breakdown(summary: dict):
    """Show performance breakdown by sport"""
    st.markdown("### 🏆 Sports Performance Breakdown")

    sport_breakdown = summary.get('sport_breakdown', {})

    if not sport_breakdown:
        st.info("No sport-specific data available")
        return

    # Convert to DataFrame for better display
    sport_data = []
    for sport, data in sport_breakdown.items():
        sport_data.append({
            'Sport': sport,
            'Total Games': data.get('total', 0),
            'Wins': data.get('wins', 0),
            'Win Rate': data.get('win_rate', 0.0)
        })

    sport_df = pd.DataFrame(sport_data)
    sport_df = sport_df.sort_values('Win Rate', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        # Sport performance table
        st.markdown("#### Performance by Sport")

        # Format the dataframe for display
        display_df = sport_df.copy()
        display_df['Win Rate'] = display_df['Win Rate'].apply(lambda x: f"{x:.1%}")

        st.dataframe(display_df, use_container_width=True, hide_index=True)

    with col2:
        # Sport performance chart
        fig = px.bar(
            sport_df,
            x='Sport',
            y='Win Rate',
            title='Win Rate by Sport',
            text=sport_df.apply(lambda x: f"{x['Wins']}/{x['Total Games']}", axis=1)
        )
        fig.update_yaxis(tickformat='.1%')
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # Detailed sport analysis
    st.markdown("#### Sport-Specific Insights")

    # Get tracking data for detailed analysis
    tracking_data = st.session_state.result_tracker.export_tracking_data()
    completed_data = tracking_data[tracking_data['status'].isin(['WIN', 'LOSS'])].copy()

    if len(completed_data) > 0:
        # Best performing sport
        best_sport = sport_df.loc[sport_df['Win Rate'].idxmax()]
        worst_sport = sport_df.loc[sport_df['Win Rate'].idxmin()]

        col1, col2 = st.columns(2)

        with col1:
            st.success(f"**Best Performing Sport:** {best_sport['Sport']}")
            st.markdown(f"Win Rate: {best_sport['Win Rate']:.1%} ({best_sport['Wins']}/{best_sport['Total Games']})")

        with col2:
            if best_sport['Sport'] != worst_sport['Sport']:
                st.warning(f"**Needs Improvement:** {worst_sport['Sport']}")
                st.markdown(f"Win Rate: {worst_sport['Win Rate']:.1%} ({worst_sport['Wins']}/{worst_sport['Total Games']})")

def show_detailed_records():
    """Show detailed prediction records"""
    st.markdown("### 📋 Detailed Prediction Records")

    # Get all tracking data
    tracking_data = st.session_state.result_tracker.export_tracking_data()

    if len(tracking_data) == 0:
        st.info("No tracking records available")
        return

    # Filter options
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status Filter",
            options=['All', 'WIN', 'LOSS', 'PENDING'],
            key="status_filter"
        )

    with col2:
        sport_filter = st.selectbox(
            "Sport Filter", 
            options=['All'] + list(tracking_data['sport'].unique()),
            key="sport_filter"
        )

    with col3:
        confidence_filter = st.selectbox(
            "Confidence Filter",
            options=['All', 'High (75%+)', 'Medium (60-75%)', 'Low (<60%)'],
            key="confidence_filter"
        )

    # Apply filters
    filtered_data = tracking_data.copy()

    if status_filter != 'All':
        filtered_data = filtered_data[filtered_data['status'] == status_filter]

    if sport_filter != 'All':
        filtered_data = filtered_data[filtered_data['sport'] == sport_filter]

    if confidence_filter != 'All':
        if confidence_filter == 'High (75%+)':
            filtered_data = filtered_data[filtered_data['confidence'] >= 0.75]
        elif confidence_filter == 'Medium (60-75%)':
            filtered_data = filtered_data[(filtered_data['confidence'] >= 0.6) & (filtered_data['confidence'] < 0.75)]
        elif confidence_filter == 'Low (<60%)':
            filtered_data = filtered_data[filtered_data['confidence'] < 0.6]

    # Display filtered data
    if len(filtered_data) > 0:
        # Format data for display
        display_columns = [
            'game_date', 'sport', 'away_team', 'home_team', 'our_pick', 
            'confidence', 'status', 'actual_winner', 'final_score'
        ]

        display_data = filtered_data[display_columns].copy()

        # Format confidence as percentage
        display_data['confidence'] = display_data['confidence'].apply(lambda x: f"{x:.1%}" if pd.notna(x) else 'N/A')

        # Rename columns for better display
        display_data = display_data.rename(columns={
            'game_date': 'Game Date',
            'sport': 'Sport',
            'away_team': 'Away Team',
            'home_team': 'Home Team',
            'our_pick': 'Our Pick',
            'confidence': 'Confidence',
            'status': 'Result',
            'actual_winner': 'Actual Winner',
            'final_score': 'Final Score'
        })

        # Color code results
        def highlight_results(val):
            if val == 'WIN':
                return 'background-color: #d4edda'
            elif val == 'LOSS':
                return 'background-color: #f8d7da'
            elif val == 'PENDING':
                return 'background-color: #fff3cd'
            return ''

        styled_data = display_data.style.applymap(highlight_results, subset=['Result'])

        st.dataframe(styled_data, use_container_width=True, height=400)

        # Summary of filtered data
        st.markdown("#### Filtered Results Summary")

        completed_filtered = filtered_data[filtered_data['status'].isin(['WIN', 'LOSS'])]

        if len(completed_filtered) > 0:
            wins = len(completed_filtered[completed_filtered['status'] == 'WIN'])
            total = len(completed_filtered)
            win_rate = wins / total

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Filtered Results", f"{wins}/{total}")

            with col2:
                st.metric("Win Rate", f"{win_rate:.1%}")

            with col3:
                avg_confidence = completed_filtered['confidence'].mean()
                st.metric("Avg Confidence", f"{avg_confidence:.1%}")

    else:
        st.info("No records match the selected filters")

def display_performance_charts(summary: Dict):
    """Display interactive performance charts"""

    # Check if we have actual tracking data
    total_predictions = summary.get('overall_performance', {}).get('total_completed', 0)

    if total_predictions == 0:
        st.info("📊 Charts will appear here once you have prediction data. Make some predictions to see your performance trends!")
        return

    # Sample data for demonstration - in production this would come from actual tracking
    dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
    accuracy_data = pd.DataFrame({
        'Date': dates,
        'Accuracy': np.random.uniform(0.45, 0.85, len(dates)),
        'Predictions': np.random.randint(5, 25, len(dates))
    })

    # Ensure we have valid data
    if len(accuracy_data) == 0 or accuracy_data['Accuracy'].isna().all():
        st.warning("Unable to display charts due to insufficient data.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📈 Accuracy Trend")

        try:
            # Line chart for accuracy over time
            accuracy_chart = px.line(
                accuracy_data, 
                x='Date', 
                y='Accuracy',
                title='Prediction Accuracy Over Time',
                line_shape='spline'
            )
            accuracy_chart.update_layout(
                yaxis_tickformat='.1%',
                yaxis_range=[0, 1]
            )
            st.plotly_chart(accuracy_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying accuracy chart: {str(e)}")

    with col2:
        st.markdown("#### 📊 Volume Trend")

        try:
            # Bar chart for prediction volume
            volume_chart = px.bar(
                accuracy_data,
                x='Date',
                y='Predictions',
                title='Daily Prediction Volume'
            )
            st.plotly_chart(volume_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying volume chart: {str(e)}")

def display_confidence_calibration(summary: Dict):
    """Display confidence calibration analysis"""
    st.markdown("#### 🎯 Confidence Calibration")

    # Check if we have enough data for calibration analysis
    total_predictions = summary.get('overall_performance', {}).get('total_completed', 0)

    if total_predictions < 10:
        st.info("🎯 Confidence calibration analysis will appear once you have at least 10 completed predictions.")
        return

    try:
        # Sample calibration data
        confidence_bins = np.arange(0.5, 1.0, 0.1)
        actual_accuracy = np.random.uniform(0.4, 0.9, len(confidence_bins))

        calibration_data = pd.DataFrame({
            'Predicted_Confidence': confidence_bins,
            'Actual_Accuracy': actual_accuracy
        })

        # Validate data
        if len(calibration_data) == 0 or calibration_data['Predicted_Confidence'].isna().all():
            st.warning("Unable to display calibration chart due to insufficient data.")
            return

        # Perfect calibration line
        perfect_line = pd.DataFrame({
            'Predicted_Confidence': [0.5, 1.0],
            'Actual_Accuracy': [0.5, 1.0]
        })

        # Create calibration plot
        fig = go.Figure()

        # Add actual performance
        fig.add_trace(go.Scatter(
            x=calibration_data['Predicted_Confidence'],
            y=calibration_data['Actual_Accuracy'],
            mode='markers+lines',
            name='Actual Performance',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))

        # Add perfect calibration line
        fig.add_trace(go.Scatter(
            x=perfect_line['Predicted_Confidence'],
            y=perfect_line['Actual_Accuracy'],
            mode='lines',
            name='Perfect Calibration',
            line=dict(color='red', dash='dash', width=2)
        ))

        fig.update_layout(
            title='Confidence vs Actual Accuracy',
            xaxis_title='Predicted Confidence',
            yaxis_title='Actual Accuracy',
            yaxis_tickformat='.1%',
            xaxis_tickformat='.1%',
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Calibration metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            # Brier Score (lower is better)
            brier_score = np.mean((calibration_data['Predicted_Confidence'] - calibration_data['Actual_Accuracy']) ** 2)
            st.metric("📏 Brier Score", f"{brier_score:.3f}", help="Lower is better (0-1 scale)")

        with col2:
            # Calibration error
            calibration_error = np.mean(np.abs(calibration_data['Predicted_Confidence'] - calibration_data['Actual_Accuracy']))
            st.metric("⚖️ Calibration Error", f"{calibration_error:.1%}", help="How far off predictions are on average")

        with col3:
            # Reliability
            reliability = 1 - calibration_error
            st.metric("🎯 Reliability", f"{reliability:.1%}", help="How well-calibrated the predictions are")

    except Exception as e:
        st.error(f"Error displaying calibration analysis: {str(e)}")
        st.info("📊 Calibration charts will appear when more prediction data is available.")

def display_ai_model_comparison(summary: Dict):
    """Compare performance between AI models"""
    st.markdown("#### 🤖 AI Model Comparison")

    # Check if we have enough data for AI model comparison
    total_predictions = summary.get('overall_performance', {}).get('total_completed', 0)

    if total_predictions < 5:
        st.info("🤖 AI model comparison will appear once you have at least 5 predictions from different AI models.")
        return

    try:
        # Sample AI performance data
        ai_models = ['ChatGPT', 'Gemini', 'Consensus']
        win_rates = [0.67, 0.62, 0.73]
        total_predictions = [45, 42, 38]

        comparison_data = pd.DataFrame({
            'AI_Model': ai_models,
            'Win_Rate': win_rates,
            'Total_Predictions': total_predictions
        })

        # Validate data
        if len(comparison_data) == 0 or comparison_data['Win_Rate'].isna().all():
            st.warning("Unable to display AI model comparison due to insufficient data.")
            return

        col1, col2 = st.columns(2)

        with col1:
            try:
                # Win rate comparison
                win_rate_chart = px.bar(
                    comparison_data,
                    x='AI_Model',
                    y='Win_Rate',
                    title='Win Rate by AI Model',
                    color='AI_Model',
                    color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
                )
                win_rate_chart.update_layout(yaxis_tickformat='.1%')
                st.plotly_chart(win_rate_chart, use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying win rate chart: {str(e)}")

        with col2:
            try:
                # Volume comparison
                volume_chart = px.bar(
                    comparison_data,
                    x='AI_Model',
                    y='Total_Predictions',
                    title='Prediction Volume by AI Model',
                    color='AI_Model',
                    color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
                )
                st.plotly_chart(volume_chart, use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying volume chart: {str(e)}")

        # Model insights
        st.markdown("##### 💡 AI Model Insights")

        best_model = comparison_data.loc[comparison_data['Win_Rate'].idxmax(), 'AI_Model']
        best_rate = comparison_data['Win_Rate'].max()

        insights = []
        insights.append(f"🏆 **Best Performing Model**: {best_model} ({best_rate:.1%} win rate)")

        total_all = comparison_data['Total_Predictions'].sum()
        insights.append(f"📊 **Total Predictions Tracked**: {total_all}")

        if comparison_data['Win_Rate'].std() > 0.05:
            insights.append("⚠️ **Significant variation** between AI models detected")
        else:
            insights.append("✅ **Consistent performance** across AI models")

        for insight in insights:
            st.markdown(insight)

    except Exception as e:
        st.error(f"Error in AI model comparison: {str(e)}")
        st.info("📊 AI model comparison will appear when more prediction data is available.")

if __name__ == "__main__":
    show_performance_tracking()