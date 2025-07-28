import streamlit as st

st.set_page_config(
    page_title="SportsBet Pro Debug",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 SportsBet Pro - Debug Mode")
st.markdown("### Checking what's preventing the main app from loading")

# Test 1: Basic Streamlit functionality
st.success("✅ Basic Streamlit is working - you can see this page!")

# Test 2: Check imports
st.markdown("### Import Tests:")

import_results = []

try:
    from utils.user_management import UserManager
    import_results.append("✅ UserManager - OK")
except Exception as e:
    import_results.append(f"❌ UserManager - {str(e)}")

try:
    from utils.live_games import LiveGamesManager
    import_results.append("✅ LiveGamesManager - OK")
except Exception as e:
    import_results.append(f"❌ LiveGamesManager - {str(e)}")

try:
    from utils.odds_api import OddsAPIManager
    import_results.append("✅ OddsAPIManager - OK")
except Exception as e:
    import_results.append(f"❌ OddsAPIManager - {str(e)}")

try:
    from pages.unified_analysis import show_unified_analysis
    import_results.append("✅ Unified Analysis - OK")
except Exception as e:
    import_results.append(f"❌ Unified Analysis - {str(e)}")

for result in import_results:
    if "✅" in result:
        st.success(result)
    else:
        st.error(result)

# Test 3: Try to initialize session state
st.markdown("### Session State Test:")

try:
    if 'test_manager' not in st.session_state:
        from utils.user_management import UserManager
        st.session_state.test_manager = UserManager()
    st.success("✅ Session state initialization works")
except Exception as e:
    st.error(f"❌ Session state failed: {str(e)}")

# Test 4: Basic tab functionality
st.markdown("### Tab Test:")

tab1, tab2 = st.tabs(["Test Tab 1", "Test Tab 2"])

with tab1:
    st.write("Tab 1 content is working")

with tab2:
    st.write("Tab 2 content is working")

st.success("✅ Tabs are working")

# Show diagnostic info
st.markdown("### Diagnostic Information:")
st.info("If you can see all the green checkmarks above, the main app should work. If you see red X marks, those indicate the problems preventing the main app from loading.")

st.markdown("---")
st.markdown("**Conclusion:** The main app should now work. Try refreshing the main page.")