import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if using)
load_dotenv()

# ------------------------------
# Database Connection
# ------------------------------
DB_USER = os.getenv("DB_USER", "your_username")      # Replace with your MySQL username
DB_PASS = os.getenv("DB_PASS", "your_password")      # Replace with your MySQL password
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "ieor215_project"

# Create the database engine and test connection
try:
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except Exception as e:
    st.error(f"Error connecting to the database: {e}")
    st.stop()

# ------------------------------
# Query Helpers
# ------------------------------
@st.cache_data
def get_nutritionist_performance(min_clients=0, pay_rate_min=0, pay_rate_max=200000, 
                                 selected_nutritionists=None, health_score_min=None, 
                                 health_score_max=None, start_date=None, end_date=None):
    query = """
    SELECT 
        np.Nutritionist_ID,
        e.Pay_rate,
        np.Active_Client_Count,
        np.Total_Client_Count,
        np.Total_Health_Improvement
    FROM Nutritionist_Performance np
    JOIN ieor215_project.Employee e 
        ON np.Nutritionist_ID = e.Employee_ID
    WHERE np.Active_Client_Count >= :min_clients
      AND e.Pay_rate BETWEEN :pay_rate_min AND :pay_rate_max
    """
    
    params = {
        'min_clients': min_clients,
        'pay_rate_min': pay_rate_min,
        'pay_rate_max': pay_rate_max
    }
    
    if selected_nutritionists:
        query += " AND np.Nutritionist_ID IN :selected_nutritionists"
        params['selected_nutritionists'] = tuple(selected_nutritionists)
    
    if health_score_min is not None:
        query += " AND np.Total_Health_Improvement >= :health_score_min"
        params['health_score_min'] = health_score_min
    if health_score_max is not None:
        query += " AND np.Total_Health_Improvement <= :health_score_max"
        params['health_score_max'] = health_score_max
    
    if start_date and end_date:
        query += """
            AND EXISTS (
                SELECT 1 
                FROM ieor215_project.MEMBER_MEASUREMENTS mm
                JOIN ieor215_project.Member_Consults_Nutritionist mcn 
                    ON mm.Member_ID = mcn.Member_ID
                WHERE mcn.Employee_ID = np.Nutritionist_ID
                  AND mm.Record_Date BETWEEN :start_date AND :end_date
            )
        """
        params['start_date'] = start_date
        params['end_date'] = end_date
    
    query += " ORDER BY np.Total_Health_Improvement DESC;"
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()
    
    numeric_cols = ["Pay_rate", "Active_Client_Count", "Total_Client_Count", "Total_Health_Improvement"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

@st.cache_data
def get_nutritionist_list():
    query = """
    SELECT 
        Employee_ID, 
        Pay_rate 
    FROM 
        ieor215_project.Employee;
    """
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Error fetching nutritionist list: {e}")
        return pd.DataFrame()
    
    if not df.empty:
        df['Pay_rate'] = pd.to_numeric(df['Pay_rate'], errors='coerce')
        df['Nutritionist_Info'] = 'ID: ' + df['Employee_ID'].astype(str) + ' - Pay: $' + df['Pay_rate'].round(2).astype(str)
    return df

@st.cache_data
def get_avg_bmi_trend(start_date=None, end_date=None):
    query = "SELECT * FROM Avg_BMI_Trend WHERE 1=1"
    params = {}
    if start_date:
        query += " AND Measurement_Date >= :start_date"
        params['start_date'] = start_date
    if end_date:
        query += " AND Measurement_Date <= :end_date"
        params['end_date'] = end_date
    query += " ORDER BY Measurement_Date;"
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query), params)
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        st.error(f"Error fetching BMI trend data: {e}")
        return pd.DataFrame()
    
    if 'Avg_BMI' in df.columns:
        df['Avg_BMI'] = pd.to_numeric(df['Avg_BMI'], errors='coerce')
    return df

st.title("🏆 Top Nutritionists Dashboard")

# Sidebar filters
st.sidebar.header("🔍 Filters")

default_start_date = datetime.today() - timedelta(days=180)
default_end_date = datetime.today()
start_date = st.sidebar.date_input("Start Date", value=default_start_date)
end_date = st.sidebar.date_input("End Date", value=default_end_date)

if start_date > end_date:
    st.sidebar.error("❌ **Error:** Start date must be earlier than or equal to End date.")
    st.stop()

st.sidebar.subheader("💰 Nutritionist Pay Rate Range")
nutritionist_df = get_nutritionist_list()

if not nutritionist_df.empty:
    pay_rate_min_default = int(nutritionist_df['Pay_rate'].min())
    pay_rate_max_default = int(nutritionist_df['Pay_rate'].max())
    if pay_rate_min_default == pay_rate_max_default:
        pay_rate_max_default = pay_rate_min_default + 1000
else:
    pay_rate_min_default = 0
    pay_rate_max_default = 10000

pay_range = pay_rate_max_default - pay_rate_min_default
step = max(1, pay_range // 10)

pay_rate_min, pay_rate_max = st.sidebar.slider(
    "Select Pay Rate Range",
    min_value=pay_rate_min_default,
    max_value=pay_rate_max_default,
    value=(pay_rate_min_default, pay_rate_max_default),
    step=step,
    format="$%d"
)

st.sidebar.subheader("👤 Select Nutritionists")
selected_nutritionists = []
if not nutritionist_df.empty:
    nutritionist_options = nutritionist_df['Nutritionist_Info'].tolist()
    selected_options = st.sidebar.multiselect("Choose Nutritionists", nutritionist_options)
    
    if selected_options:
        for option in selected_options:
            try:
                nid = int(option.split(' - ')[0].split(': ')[1])
                selected_nutritionists.append(nid)
            except:
                continue
else:
    st.sidebar.warning("⚠️ No nutritionists found.")

st.sidebar.subheader("📈 Health Improvement Score Range")
query_health_min_max = """
SELECT 
    MIN(Total_Health_Improvement) AS min_score,
    MAX(Total_Health_Improvement) AS max_score
FROM 
    Nutritionist_Performance;
"""
try:
    health_min_max_df = pd.read_sql(query_health_min_max, engine)
    if not health_min_max_df.empty:
        h_min = health_min_max_df['min_score'].iloc[0]
        h_max = health_min_max_df['max_score'].iloc[0]
        if pd.isnull(h_min):
            h_min = 0.0
        if pd.isnull(h_max):
            h_max = 1000.0
    else:
        h_min, h_max = 0.0, 1000.0
except Exception as e:
    st.sidebar.error(f"Error fetching health score range: {e}")
    h_min, h_max = 0.0, 1000.0

health_score_min, health_score_max = st.sidebar.slider(
    "Select Health Improvement Score Range",
    min_value=float(h_min),
    max_value=float(h_max),
    value=(float(h_min), float(h_max)),
    step=10.0
)

st.sidebar.subheader("📊 Minimum Active Clients")
min_clients = st.sidebar.slider("Set Minimum Active Clients", 0, 10, 0, step=1)

st.sidebar.subheader("📈 Minimum Total Clients")
min_total_clients = st.sidebar.slider("Set Minimum Total Clients", 0, 10, 0, step=1)

st.sidebar.subheader("🔝 Top N Nutritionists")
top_n = st.sidebar.number_input("Select Top N Nutritionists to Display", min_value=1, max_value=10, value=10, step=1)

apply_filters = st.sidebar.button("✅ Apply Filters")
reset_filters = st.sidebar.button("🔄 Reset Filters")

if reset_filters:
    st.experimental_rerun()

if apply_filters:
    nutritionist_data = get_nutritionist_performance(
        min_clients=min_clients,
        pay_rate_min=pay_rate_min,
        pay_rate_max=pay_rate_max,
        selected_nutritionists=selected_nutritionists if selected_nutritionists else None,
        health_score_min=health_score_min,
        health_score_max=health_score_max,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    
    if not nutritionist_data.empty:
        nutritionist_data = nutritionist_data[nutritionist_data['Total_Client_Count'] >= min_total_clients]
        nutritionist_data = nutritionist_data.head(top_n)
    
    st.subheader("📋 Top Nutritionists Table")
    if not nutritionist_data.empty:
        nutritionist_data['Pay_rate'] = nutritionist_data['Pay_rate'].map("${:,.2f}".format)
        nutritionist_data['Total_Health_Improvement'] = nutritionist_data['Total_Health_Improvement'].map("{:,.2f}".format)
        
        st.dataframe(nutritionist_data)
    else:
        st.warning("⚠️ No nutritionists match the selected filters.")
    
    if not nutritionist_data.empty:
        st.subheader("📊 Total Health Improvement by Nutritionist")
        bar_chart_data = nutritionist_data.set_index("Nutritionist_ID")["Total_Health_Improvement"].astype(float)
        st.bar_chart(bar_chart_data)
    
    st.subheader("📈 Average BMI Trend (Active Members)")
    bmi_data = get_avg_bmi_trend(
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d")
    )
    if not bmi_data.empty:
        st.line_chart(bmi_data.set_index("Measurement_Date")["Avg_BMI"])
    else:
        st.warning("⚠️ No BMI trend data available for the selected date range.")
    
    st.markdown("🔍 **Use the filters on the left to refine the data and explore trends.**")
else:
    st.write("🛠️ **Adjust the filters and click 'Apply Filters' to view the data.**")
