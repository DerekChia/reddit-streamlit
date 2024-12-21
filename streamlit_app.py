import streamlit as st


pg = st.navigation(
    [
        st.Page("pages/main.py", title="Main", icon="🔥"),
        st.Page("pages/statistics.py", title="Statistics", icon="📈"),
    ]
)
pg.run()
