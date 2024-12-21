import streamlit as st
import clickhouse_connect
import os

client = clickhouse_connect.get_client(
    host=os.environ["CLICKHOUSE_HOST"],
    port=os.environ["CLICKHOUSE_PORT"],
    username=os.environ["CLICKHOUSE_USERNAME"],
    password=os.environ["CLICKHOUSE_PASSWORD"],
)

df_result = client.query_df("select body, inserted_at from reddit.comments limit 10;")

st.write(df_result)
