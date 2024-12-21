import streamlit as st
import clickhouse_connect
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

client = clickhouse_connect.get_client(
    host=os.environ["CLICKHOUSE_HOST"],
    port=os.environ["CLICKHOUSE_PORT"],
    username=os.environ["CLICKHOUSE_USERNAME"],
    password=os.environ["CLICKHOUSE_PASSWORD"],
)

st.set_page_config(layout="wide")

timeframe_option_map = {
    1: "1h",
    6: "6h",
    24: "1d",
    72: "3d",
    168: "1w",
    720: "1m",
}
timeframe = st.sidebar.segmented_control(
    "Timeframe",
    options=timeframe_option_map.keys(),
    format_func=lambda option: timeframe_option_map[option],
    selection_mode="single",
    default=24,
)

granularity_option_map = {
    "Minute": "minute",
    "Hour": "hour",
    "Day": "day",
}

granularity = st.sidebar.segmented_control(
    "Granularity",
    options=granularity_option_map.keys(),
    format_func=lambda option: granularity_option_map[option],
    selection_mode="single",
    default="Minute",
)

##
total_submission_count = client.query(
    "select count() from reddit.submissions"
).result_rows[0][0]

total_comment_count = client.query("select count() from reddit.comments").result_rows[
    0
][0]

##
submission_count = client.query(
    f"select count() from reddit.submissions where inserted_at >= now() - interval {timeframe} hour"
).result_rows[0][0]

comment_count = client.query(
    f"select count() from reddit.comments where inserted_at >= now() - interval {timeframe} hour"
).result_rows[0][0]

submission_count_last_timeframe = client.query(
    f"select count() from reddit.submissions where inserted_at between now() - interval {timeframe*2} hour and now() - interval {timeframe} hour"
).result_rows[0][0]

comment_count_last_timeframe = client.query(
    f"select count() from reddit.comments where inserted_at between now() - interval {timeframe*2} hour and now() - interval {timeframe} hour"
).result_rows[0][0]

##
df_submission_frequency_count = client.query_df(
    f"select toStartOf{granularity}(inserted_at) timestamp, count() count from reddit.submissions where inserted_at >= now() - interval {timeframe} hour group by 1 order by 1"
)

df_comment_frequency_count = client.query_df(
    f"select toStartOf{granularity}(inserted_at) timestamp, count() count from reddit.comments where inserted_at >= now() - interval {timeframe} hour group by 1 order by 1"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Submissions", total_submission_count)
col2.metric("Total Comments", total_comment_count)

col3.metric(
    f"Submissions in last {timeframe_option_map[timeframe]}",
    submission_count,
    submission_count - submission_count_last_timeframe,
)
col4.metric(
    f"Comments in last {timeframe_option_map[timeframe]}",
    comment_count,
    comment_count - comment_count_last_timeframe,
)


col1, col2 = st.columns(2)

col1.subheader("Submission", divider="blue")
col1.line_chart(
    df_submission_frequency_count, x="timestamp", y="count", color="#0047AB"
)

col2.subheader("Comment", divider="green")
col2.line_chart(df_comment_frequency_count, x="timestamp", y="count", color="#228B22")


df_result = client.query_df("select body, inserted_at from reddit.comments limit 10;")
st.write(df_result)
