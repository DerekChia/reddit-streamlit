import streamlit as st
import clickhouse_connect
import os
from dotenv import load_dotenv

import ollama
import time

load_dotenv()


def call_ollama(prompt):
    response = ollama.chat(
        model="llama3.2", messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


client = clickhouse_connect.get_client(
    host=os.environ["CLICKHOUSE_HOST"],
    port=os.environ["CLICKHOUSE_PORT"],
    username=os.environ["CLICKHOUSE_USERNAME"],
    password=os.environ["CLICKHOUSE_PASSWORD"],
)

st.sidebar.text_input(
    "Search",
    "Some text",
    key="placeholder",
)

st.write("test")


# subreddit = 'r/DogAdvice'
subreddit = "r/CatAdvice"
# subreddit = 'r/relationship_advice'

df_res = client.query_df("""
    select * from reddit.submissions_summary order by inserted_at desc limit 100
    """)

df_res = df_res.astype({"hash_title_selftext": "str"})
st.dataframe(df_res, use_container_width=True, height=1000)
