import streamlit as st


def main():
    st.sidebar.text_input(
        "Search",
        "Some text",
        key="placeholder",
    )

    st.write("test")


st.set_page_config(layout="wide")
pg = st.navigation(
    [
        st.Page(main, title="Main", icon="🔥"),
        st.Page("pages/statistics.py", title="Statistics", icon="📈"),
    ]
)
pg.run()
