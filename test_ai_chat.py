#!/usr/bin/env python3

import streamlit as st
from utils.ai_chat import DualAIChat
import os

st.set_page_config(page_title="AI Chat Test", layout="wide")

st.title("🧪 AI Chat Test Interface")

# Initialize AI Chat
if 'test_chat' not in st.session_state:
    st.session_state.test_chat = DualAIChat()

chat = st.session_state.test_chat

# API Key Status
col1, col2 = st.columns(2)

with col1:
    openai_status = "✅ Ready" if os.environ.get("OPENAI_API_KEY") else "❌ Missing"
    st.metric("OpenAI API Key", openai_status)

with col2:
    gemini_status = "✅ Ready" if os.environ.get("GEMINI_API_KEY") else "❌ Missing" 
    st.metric("Gemini API Key", gemini_status)

st.divider()

# Test Controls
st.subheader("🧪 Test AI Chat")

test_message = st.text_input("Test Message:", value="Hello! Can you help me with NFL picks?")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Test OpenAI Chat"):
        with st.spinner("Testing OpenAI..."):
            response = chat.get_chat_response(test_message, "openai")
            st.success("OpenAI Response Received!")
            st.json(response)

with col2:
    if st.button("Test Gemini Chat"):
        with st.spinner("Testing Gemini..."):
            response = chat.get_chat_response(test_message, "gemini")
            st.success("Gemini Response Received!")
            st.json(response)

with col3:
    if st.button("Test Both AIs"):
        with st.spinner("Testing Both AIs..."):
            response = chat.get_chat_response(test_message, "both")
            st.success("Both AI Response Received!")
            st.json(response)

st.divider()

# Quick Access
st.subheader("🚀 Quick Access")
if st.button("Go to Main AI Chat"):
    st.switch_page("pages/ai_chat.py")

st.info("This is a test interface to verify AI Chat functionality. If tests pass, the main AI Chat should work correctly.")