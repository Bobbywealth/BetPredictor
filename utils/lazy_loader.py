import streamlit as st
from typing import Callable, Any, Dict
import importlib
import sys

class LazyLoader:
    """Lazy loading system for heavy components"""
    
    def __init__(self):
        self._loaded_modules = {}
        self._cached_components = {}
    
    def load_component(self, component_name: str, loader_func: Callable) -> Any:
        """Load component only when needed"""
        if component_name not in self._cached_components:
            try:
                with st.spinner(f"Loading {component_name}..."):
                    self._cached_components[component_name] = loader_func()
            except Exception as e:
                st.error(f"Failed to load {component_name}: {str(e)}")
                return None
        
        return self._cached_components[component_name]
    
    def lazy_import(self, module_name: str, attribute: str = None):
        """Import module only when accessed"""
        if module_name not in self._loaded_modules:
            try:
                self._loaded_modules[module_name] = importlib.import_module(module_name)
            except ImportError as e:
                st.error(f"Failed to import {module_name}: {str(e)}")
                return None
        
        module = self._loaded_modules[module_name]
        return getattr(module, attribute) if attribute else module
    
    def preload_critical_components(self):
        """Preload essential components in background"""
        critical_components = [
            ('user_manager', lambda: self.lazy_import('utils.user_management', 'UserManager')),
            ('live_games', lambda: self.lazy_import('utils.live_games', 'LiveGamesManager')),
            ('odds_api', lambda: self.lazy_import('utils.odds_api', 'OddsAPIManager'))
        ]
        
        for name, loader in critical_components:
            if name not in st.session_state:
                component = self.load_component(name, loader)
                if component:
                    st.session_state[name] = component()

# Global lazy loader
lazy_loader = LazyLoader()