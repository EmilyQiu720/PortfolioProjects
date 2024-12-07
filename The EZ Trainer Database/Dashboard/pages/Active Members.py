import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import numpy as np
import altair as alt  # for richer visualizations

# Load environment variables from .env file (if using)
load_dotenv()

DB_USER = os.getenv("DB_USER", "your_username")
DB_PASS = os.getenv("DB_PASS", "your_password")
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "ieor215_project"

try:
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    st.stop()

st.title("Active Members' BMI Change and Workout Frequency Analysis")

@st.cache_data
def load_bmi_workout_data():
    # Query from the created view
    query = "SELECT * FROM Active_Member_BMI_Workout_View;"
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)

    # Ensure numeric types
    numeric_cols = ["Average_BMI", "BMI_Change", "Workout_Session_Count", "BMI_Change_Per_Session"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df = load_bmi_workout_data()

# Sidebar Filters
st.sidebar.header("Filters")

# Average BMI Filter
st.sidebar.subheader("Filter by Average BMI")
min_bmi = float(df["Average_BMI"].min()) if not df.empty else 0.0
max_bmi = float(df["Average_BMI"].max()) if not df.empty else 100.0
avg_bmi_range = st.sidebar.slider("Average BMI Range", min_value=min_bmi, max_value=max_bmi, value=(min_bmi, max_bmi), step=0.5)

# BMI Change Filter
st.sidebar.subheader("Filter by BMI Change")
min_change = float(df["BMI_Change"].min()) if not df.empty else 0.0
max_change = float(df["BMI_Change"].max()) if not df.empty else 10.0
bmi_change_range = st.sidebar.slider("BMI Change Range", min_value=min_change, max_value=max_change, value=(min_change, max_change), step=0.5)

# Workout Session Count Filter
st.sidebar.subheader("Filter by Workout Session Count")
min_sessions = int(df["Workout_Session_Count"].min()) if not df.empty else 0
max_sessions = int(df["Workout_Session_Count"].max()) if not df.empty else 50
session_count_range = st.sidebar.slider("Workout Session Count Range", min_value=min_sessions, max_value=max_sessions, value=(min_sessions, max_sessions), step=1)

# BMI Change per Session Filter
st.sidebar.subheader("Filter by BMI Change Per Session")
min_ratio = float(df["BMI_Change_Per_Session"].min()) if not df.empty else 0.0
max_ratio = float(df["BMI_Change_Per_Session"].max()) if not df.empty else 5.0
bmi_change_per_session_range = st.sidebar.slider("BMI Change/Session Range", min_value=min_ratio, max_value=max_ratio, value=(min_ratio, max_ratio), step=0.1)

# Top N Members
st.sidebar.subheader("Top N Members")
top_n = st.sidebar.number_input("Select Top N Members to Display", min_value=1, max_value=50, value=10, step=1)

apply_filters = st.sidebar.button("Apply Filters")
reset_filters = st.sidebar.button("Reset Filters")

if reset_filters:
    st.experimental_rerun()

if apply_filters:
    # Apply filters to the df
    filtered_df = df[
        (df["Average_BMI"] >= avg_bmi_range[0]) & (df["Average_BMI"] <= avg_bmi_range[1]) &
        (df["BMI_Change"] >= bmi_change_range[0]) & (df["BMI_Change"] <= bmi_change_range[1]) &
        (df["Workout_Session_Count"] >= session_count_range[0]) & (df["Workout_Session_Count"] <= session_count_range[1]) &
        (df["BMI_Change_Per_Session"] >= bmi_change_per_session_range[0]) & (df["BMI_Change_Per_Session"] <= bmi_change_per_session_range[1])
    ]

    # Sort by Average_BMI (or any metric you choose to highlight)
    filtered_df = filtered_df.sort_values(by="Average_BMI", ascending=False)
    filtered_df = filtered_df.head(top_n)

    st.subheader("Filtered Results")
    if not filtered_df.empty:
        st.dataframe(filtered_df)

        # Bar chart: BMI_Change_Per_Session by Member_ID
        st.subheader("BMI Change Per Session (Bar Chart)")
        bar_chart = alt.Chart(filtered_df).mark_bar().encode(
            x=alt.X("Member_ID:O", sort=None),
            y="BMI_Change_Per_Session:Q",
            tooltip=["Member_ID", "BMI_Change_Per_Session", "Average_BMI", "Workout_Session_Count"]
        ).properties(height=400)
        st.altair_chart(bar_chart, use_container_width=True)

        # Scatter plot: BMI_Change vs Workout_Session_Count to see correlation
        st.subheader("Correlation between BMI Change and Workout Session Count")
        scatter_chart = alt.Chart(filtered_df).mark_circle(size=60).encode(
            x="Workout_Session_Count:Q",
            y="BMI_Change:Q",
            tooltip=["Member_ID", "Average_BMI", "BMI_Change", "Workout_Session_Count", "BMI_Change_Per_Session"]
        ).properties(height=400)
        st.altair_chart(scatter_chart, use_container_width=True)

        st.markdown("""
        **Insights**:
        - The bar chart helps identify members with the greatest BMI change per session.
        - The scatter plot shows if there's a correlation between attending more workout sessions and achieving higher BMI changes.
        """)
    else:
        st.warning("No members match the selected filters.")
else:
    st.write("Use the sidebar to set filters and click 'Apply Filters' to view the data.")

st.markdown("""
**Explanation**:
This enhanced dashboard uses the `Active_Member_BMI_Workout_View` to focus on:
- **Average_BMI**: Gives an idea of the member's BMI trend.
- **BMI_Change**: How much their BMI has changed over recorded measurements.
- **Workout_Session_Count**: How many sessions they've attended.
- **BMI_Change_Per_Session**: Efficiency metric indicating how much BMI changes per workout session.

The filters allow for a detailed investigation of specific subgroups of members, and the visualizations offer additional perspectives on the data.
""")
