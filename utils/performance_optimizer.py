
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from functools import lru_cache, wraps
import time

class PerformanceOptimizer:
    """Performance optimization utilities for the SportsBet Pro app"""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def optimize_dataframe(df_hash: str, df_data: str) -> pd.DataFrame:
        """Optimize DataFrame for display with caching"""
        df = pd.read_json(df_data)
        
        # Remove infinite values that cause chart warnings
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Fill NaN values with appropriate defaults
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Optimize data types
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        return df
    
    @staticmethod
    def clean_chart_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean data for chart display to prevent infinite extent warnings"""
        cleaned_data = data.copy()
        
        for key, value in cleaned_data.items():
            if isinstance(value, (list, np.ndarray)):
                # Remove infinite values
                cleaned_value = []
                for item in value:
                    if isinstance(item, (int, float)) and np.isfinite(item):
                        cleaned_value.append(item)
                    elif not isinstance(item, (int, float)):
                        cleaned_value.append(item)
                    else:
                        cleaned_value.append(0)  # Replace infinite with 0
                cleaned_data[key] = cleaned_value
            elif isinstance(value, (int, float)) and not np.isfinite(value):
                cleaned_data[key] = 0
        
        return cleaned_data
    
    @staticmethod
    def debounce(wait_time: float):
        """Debounce decorator to prevent rapid function calls"""
        def decorator(func):
            last_called = [0.0]
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                current_time = time.time()
                if current_time - last_called[0] >= wait_time:
                    last_called[0] = current_time
                    return func(*args, **kwargs)
                return None
            return wrapper
        return decorator
    
    @staticmethod
    def batch_process(items: List[Any], batch_size: int = 10):
        """Process items in batches to prevent UI blocking"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    
    @staticmethod
    def lazy_load_component(component_func, placeholder_text: str = "Loading..."):
        """Lazy load heavy components"""
        if f"{component_func.__name__}_loaded" not in st.session_state:
            with st.spinner(placeholder_text):
                result = component_func()
                st.session_state[f"{component_func.__name__}_loaded"] = result
                return result
        return st.session_state[f"{component_func.__name__}_loaded"]

class DataStreamOptimizer:
    """Optimize data streaming and real-time updates"""
    
    def __init__(self):
        self.update_intervals = {
            'live_odds': 30,      # 30 seconds
            'game_scores': 10,    # 10 seconds  
            'predictions': 300,   # 5 minutes
            'performance': 600    # 10 minutes
        }
    
    def should_update(self, data_type: str) -> bool:
        """Check if data should be updated based on intervals"""
        last_update_key = f"last_update_{data_type}"
        interval = self.update_intervals.get(data_type, 60)
        
        if last_update_key not in st.session_state:
            st.session_state[last_update_key] = time.time()
            return True
        
        time_since_update = time.time() - st.session_state[last_update_key]
        
        if time_since_update >= interval:
            st.session_state[last_update_key] = time.time()
            return True
        
        return False
    
    def get_time_until_next_update(self, data_type: str) -> int:
        """Get seconds until next update"""
        last_update_key = f"last_update_{data_type}"
        interval = self.update_intervals.get(data_type, 60)
        
        if last_update_key not in st.session_state:
            return 0
        
        time_since_update = time.time() - st.session_state[last_update_key]
        return max(0, int(interval - time_since_update))

# Global optimizer instances
performance_optimizer = PerformanceOptimizer()
stream_optimizer = DataStreamOptimizer()
