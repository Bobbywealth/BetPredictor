import streamlit as st
import time
from typing import Dict, Any
import pandas as pd

class PerformanceOptimizer:
    """Performance optimization utilities for SportsBet Pro"""
    
    @staticmethod
    def optimize_dataframe_display(df: pd.DataFrame, max_rows: int = 1000) -> pd.DataFrame:
        """Optimize DataFrame for faster display"""
        if len(df) > max_rows:
            return df.head(max_rows)
        return df
    
    @staticmethod
    def batch_process_games(games_list: list, batch_size: int = 10):
        """Process games in batches to avoid blocking UI"""
        for i in range(0, len(games_list), batch_size):
            yield games_list[i:i + batch_size]
    
    @staticmethod
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def cached_api_call(api_func, *args, **kwargs):
        """Generic cached API call wrapper"""
        return api_func(*args, **kwargs)
    
    @staticmethod
    def show_performance_stats():
        """Display performance statistics"""
        from utils.performance_cache import performance_cache
        
        stats = performance_cache.get_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Cache Hit Rate", f"{stats['hit_rate']:.1f}%")
        
        with col2:
            st.metric("Cache Size", stats['cache_size'])
        
        with col3:
            st.metric("Time Saved", f"{stats['total_time_saved']:.1f}s")
        
        with col4:
            st.metric("API Calls Cached", stats['hits'])

# Global performance optimizer
performance_optimizer = PerformanceOptimizer()