import streamlit as st

st.set_page_config(
    page_title="SportsBet Pro Test",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 SportsBet Pro - Test Page")
st.markdown("### This is a simple test to verify Streamlit is working")

st.success("✅ Streamlit is working correctly!")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Test Metric 1", "100")

with col2:
    st.metric("Test Metric 2", "200")

with col3:
    st.metric("Test Metric 3", "300")

st.info("If you can see this page, the basic Streamlit functionality is working.")

# Test basic imports
try:
    from utils.user_management import UserManager
    st.success("✅ UserManager import successful")
except Exception as e:
    st.error(f"❌ UserManager import failed: {e}")

try:
    from utils.live_games import LiveGamesManager
    st.success("✅ LiveGamesManager import successful")
except Exception as e:
    st.error(f"❌ LiveGamesManager import failed: {e}")

st.markdown("---")
st.markdown("**Next Steps:** If this test page works, the main app should work too.")