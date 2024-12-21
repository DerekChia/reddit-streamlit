import streamlit as st
import clickhouse_connect
import os
from dotenv import load_dotenv

load_dotenv()

client = clickhouse_connect.get_client(
    host=os.environ["CLICKHOUSE_HOST"],
    port=os.environ["CLICKHOUSE_PORT"],
    username=os.environ["CLICKHOUSE_USERNAME"],
    password=os.environ["CLICKHOUSE_PASSWORD"],
)

## Sidebar
timeframe_option_map = {
    3: "3h",
    24: "1d",
    72: "3d",
    168: "1w",
    720: "1M",
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

subreddit_tracked = client.query(
    "select countDistinct(raw._path) from reddit.subreddits"
).result_rows[0][0]

##
df_submission_frequency_count = client.query_df(
    f"select toStartOf{granularity}(inserted_at) timestamp, count() count from reddit.submissions where inserted_at >= now() - interval {timeframe} hour group by 1 order by 1"
)

df_comment_frequency_count = client.query_df(
    f"select toStartOf{granularity}(inserted_at) timestamp, count() count from reddit.comments where inserted_at >= now() - interval {timeframe} hour group by 1 order by 1"
)

##
st.title("Statistics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Submissions", total_submission_count)
col2.metric("Total Comments", total_comment_count)
col3.metric("Subreddits Tracked", subreddit_tracked)

col4.metric(
    f"Submissions in last {timeframe_option_map[timeframe]}",
    submission_count,
    submission_count - submission_count_last_timeframe,
)
col5.metric(
    f"Comments in last {timeframe_option_map[timeframe]}",
    comment_count,
    comment_count - comment_count_last_timeframe,
)


##
col1, col2 = st.columns(2)

col1.subheader("Submission", divider="blue")
col1.line_chart(
    df_submission_frequency_count, x="timestamp", y="count", color="#0047AB"
)

col2.subheader("Comment", divider="green")
col2.line_chart(df_comment_frequency_count, x="timestamp", y="count", color="#228B22")


##
col1, col2, col3 = st.columns(3)

col1.subheader("Most submissions", divider="orange")
query = f"SELECT CAST(raw.subreddit_name_prefixed, 'String') AS subreddit, count() AS count FROM reddit.submissions WHERE inserted_at > now() - interval {timeframe} hour GROUP BY ALL ORDER BY count DESC LIMIT 10"

col1.dataframe(client.query_df(query), hide_index=True)

col2.subheader("Most comments", divider="orange")
query = f"SELECT CAST(raw.subreddit_name_prefixed, 'String') AS subreddit, count() AS count FROM reddit.comments WHERE inserted_at > now() - interval {timeframe} hour GROUP BY ALL ORDER BY count DESC LIMIT 10"

col2.dataframe(client.query_df(query), hide_index=True)

col3.subheader("Top subscribers", divider="orange")
query = "select raw._path as subreddit, raw.subscribers::UInt32 as subscribers from reddit.subreddits order by 2 desc limit 10"
col3.dataframe(client.query_df(query), hide_index=True)


##
st.subheader("Recent submissions", divider="orange")
query = "SELECT raw.subreddit_name_prefixed::String as subreddit, raw.title as title, substring(trimBoth(replaceAll(CAST(raw.selftext, 'String'), '\n', ' ')), 1, 100) AS text, 'https://reddit.com' || raw.permalink::String as link FROM reddit.submissions WHERE text != '' ORDER BY inserted_at DESC LIMIT 10"

df = client.query_df(query)

st.data_editor(
    df,
    column_config={
        "subreddit": st.column_config.Column("subreddit", width="small"),
        "title": st.column_config.Column("title", width="medium"),
        "text": st.column_config.Column("text", width="large"),
        "link": st.column_config.LinkColumn("Link", display_text="Link"),
    },
    hide_index=True,
    use_container_width=True,
)

##
st.subheader("Hot comments", divider="orange")
query = f"SELECT CAST(raw.subreddit_name_prefixed, 'String') AS subreddit, substring(raw.link_title::String, 1, 100) as title, max(raw.num_comments::UInt32) as num_comments FROM reddit.comments WHERE inserted_at > now() - interval {timeframe} hour group by all ORDER BY num_comments DESC LIMIT 10"

st.dataframe(client.query_df(query), hide_index=True, use_container_width=True)
