import streamlit as st
import clickhouse_connect
import os
import pandas as pd
import numpy as np

client = clickhouse_connect.get_client(
    host=os.environ["CLICKHOUSE_HOST"],
    port=os.environ["CLICKHOUSE_PORT"],
    username=os.environ["CLICKHOUSE_USERNAME"],
    password=os.environ["CLICKHOUSE_PASSWORD"],
)

st.sidebar.selectbox("Interval", ["hour", "day", "week"], key="interval")


df_result = client.query_df("select body, inserted_at from reddit.comments limit 10;")
st.write(df_result)

df_result = client.query_df(
    "select toStartOfHour(inserted_at) timestamp, count() count from reddit.comments group by 1 order by 2"
)

chart_data = pd.DataFrame(df_result, columns=["timestamp", "count"])
st.bar_chart(chart_data)
