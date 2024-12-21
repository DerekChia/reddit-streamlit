import streamlit as st
import clickhouse_connect
import os

client = clickhouse_connect.get_client(
    host=os.environ["CLICKHOUSE_HOST"],
    port=os.environ["CLICKHOUSE_PORT"],
    username=os.environ["CLICKHOUSE_USERNAME"],
    password=os.environ["CLICKHOUSE_PASSWORD"],
)

res = client.query("select 1")

st.write(res)
