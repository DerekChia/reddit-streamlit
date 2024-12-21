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

res = client.query(f"""
    select raw.title::String || ' ' || raw.selftext::String as body from reddit.submissions 
    where raw.subreddit_name_prefixed::String = '{subreddit}' limit 250
    """)

docs = [result_row[0] for result_row in res.result_rows]

for doc in docs:
    #     print(call_ollama(f"""
    #     This is submission in Reddit, is this a problem that someone is reporting? Answer yes or no. Here's the {doc}
    #     """))

    st.write(
        call_ollama(f"""
    Summarize this paragraph in a few words: {doc}
    """)
    )
