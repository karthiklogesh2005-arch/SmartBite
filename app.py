import streamlit as st
import pandas as pd
import plotly.express as px
import os
import subprocess
import sys

# Environment configuration
os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"

st.set_page_config(
    page_title="SmartBite Analytics Platform", 
    page_icon="🍔", 
    layout="wide"
)

st.title("🍔 SmartBite Analytics: Multi-Source Food Delivery Intelligence")
st.markdown("Scalable analytics platform integrating operational orders, customer demographics, city weather, and holiday calendars using Apache Spark and Streamlit.")

st.sidebar.title("📌 Navigation Tabs")
app_mode = st.sidebar.selectbox("Select Dashboard Module", [
    "📊 Executive Orders & Demand", 
    "👥 Customer Demographics & Profiles", 
    "🌦️ Meteorological & City Weather", 
    "🎉 Holiday Calendar & Planning",
    "⚙️ Spark Pipeline Controller"
])

@st.cache_data
def load_output_csv(filename):
    file_path = os.path.join("data/output", f"{filename}.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

# Load processed output CSV datasets
orders_df = load_output_csv("cleaned_orders")
customers_df = load_output_csv("cleaned_customers")

# Safely coerce customer numeric columns to avoid string-to-mean errors
if customers_df is not None:
    if 'Age' in customers_df.columns:
        customers_df['Age'] = pd.to_numeric(customers_df['Age'], errors='coerce')
    if 'Family size' in customers_df.columns:
        customers_df['Family size'] = pd.to_numeric(customers_df['Family size'], errors='coerce')

weather_df = load_output_csv("cleaned_weather")
holidays_df = load_output_csv("cleaned_holidays")
demand_day_df = load_output_csv("demand_by_day")
demand_cuisine_df = load_output_csv("demand_by_cuisine")
delivery_perf_df = load_output_csv("delivery_performance")
top_restaurants_df = load_output_csv("top_restaurants_sql")

if app_mode == "📊 Executive Orders & Demand":
    st.header("Executive Orders & Operational Demand")
    if orders_df is None:
        st.warning("⚠️ Processed orders data not found. Please run the Spark pipeline from the Spark Pipeline Controller tab.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Orders", f"{len(orders_df):,}")
        col2.metric("Total Revenue ($)", f"${orders_df['cost_of_the_order'].sum():,.2f}")
        col3.metric("Avg Order Value ($)", f"${orders_df['cost_of_the_order'].mean():.2f}")
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Orders by Day of the Week")
            if demand_day_df is not None:
                fig = px.bar(demand_day_df, x='day_of_the_week', y='total_orders', color='day_of_the_week', title="Order Distribution by Weekday")
            else:
                day_counts = orders_df['day_of_the_week'].value_counts().reset_index()
                day_counts.columns = ['day_of_the_week', 'count']
                fig = px.bar(day_counts, x='day_of_the_week', y='count', color='day_of_the_week', title="Order Distribution by Weekday")
            st.plotly_chart(fig, width='stretch')
            
        with c2:
            st.subheader("Top Cuisine Types")
            if demand_cuisine_df is not None:
                fig = px.pie(demand_cuisine_df.head(8), names='cuisine_type', values='total_orders', title="Cuisine Share")
            else:
                cuisine_counts = orders_df['cuisine_type'].value_counts().head(8).reset_index()
                cuisine_counts.columns = ['cuisine_type', 'count']
                fig = px.pie(cuisine_counts, names='cuisine_type', values='count', title="Cuisine Share")
            st.plotly_chart(fig, width='stretch')
            
        if top_restaurants_df is not None:
            st.markdown("---")
            st.subheader("Top 10 Restaurants (Spark SQL Analysis)")
            st.dataframe(top_restaurants_df, width='stretch')

elif app_mode == "👥 Customer Demographics & Profiles":
    st.header("Customer Demographics & Survey Profiles")
    if customers_df is None:
        st.warning("⚠️ Customer data not found. Please run the Spark pipeline.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Surveyed Customers", len(customers_df))
        col2.metric("Average Age", f"{customers_df['Age'].mean():.1f} years" if 'Age' in customers_df.columns and not customers_df['Age'].isnull().all() else "N/A")
        col3.metric("Average Family Size", f"{customers_df['Family size'].mean():.1f} members" if 'Family size' in customers_df.columns and not customers_df['Family size'].isnull().all() else "N/A")
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Customer Occupation Breakdown")
            if 'Occupation' in customers_df.columns:
                occ = customers_df['Occupation'].value_counts().reset_index()
                occ.columns = ['Occupation', 'Count']
                fig = px.bar(occ, x='Occupation', y='Count', color='Occupation', title="Users by Occupation")
                st.plotly_chart(fig, width='stretch')
        with c2:
            st.subheader("Monthly Income Distribution")
            if 'Monthly Income' in customers_df.columns:
                inc = customers_df['Monthly Income'].value_counts().reset_index()
                inc.columns = ['Monthly Income', 'Count']
                fig = px.pie(inc, names='Monthly Income', values='Count', title="Income Brackets")
                st.plotly_chart(fig, width='stretch')

elif app_mode == "🌦️ Meteorological & City Weather":
    st.header("City-wise Weather & Environmental Conditions")
    if weather_df is None:
        st.warning("⚠️ Weather data not found. Please run the Spark pipeline.")
    else:
        selected_city = st.selectbox("Select City for Weather Analysis", sorted(weather_df['city'].unique()) if 'city' in weather_df.columns else [])
        city_data = weather_df[weather_df['city'] == selected_city] if 'city' in weather_df.columns else weather_df
        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Temperature (°C)", f"{city_data['tavg'].mean():.1f}" if 'tavg' in city_data.columns and not city_data['tavg'].isnull().all() else "N/A")
        col2.metric("Avg Precipitation (mm)", f"{city_data['prcp'].mean():.1f}" if 'prcp' in weather_df.columns and not city_data['prcp'].isnull().all() else "N/A")
        col3.metric("Records Tracked", len(city_data))
        
        st.markdown("---")
        st.subheader(f"Weather Trends for {selected_city}")
        if 'date' in city_data.columns and 'tavg' in city_data.columns:
            fig = px.line(city_data, x='date', y='tavg', title=f"Average Temperature Timeline - {selected_city}")
            st.plotly_chart(fig, width='stretch')

elif app_mode == "🎉 Holiday Calendar & Planning":
    st.header("2021 National & Restricted Holidays Calendar")
    if holidays_df is None:
        st.warning("⚠️ Holidays data not found. Please run the Spark pipeline.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Total Tracked Holidays (2021)", len(holidays_df))
        col2.metric("Holiday Types", holidays_df['holiday_type'].nunique() if 'holiday_type' in holidays_df.columns else 1)
        
        st.markdown("---")
        st.subheader("Holiday Schedule Overview")
        st.dataframe(holidays_df, width='stretch')
        if 'holiday_type' in holidays_df.columns:
            fig = px.histogram(holidays_df, x='holiday_type', color='holiday_type', title="Distribution by Holiday Type")
            st.plotly_chart(fig, width='stretch')

elif app_mode == "⚙️ Spark Pipeline Controller":
    st.header("Apache Spark Multi-Source Pipeline Control")
    st.markdown("Trigger distributed PySpark data ingestion, cleaning, and aggregation across all four datasets.")
    
    if st.button("🚀 Run PySpark Multi-Source Pipeline"):
        # Define pipeline steps with user-friendly descriptions
        steps = [
            ("Data Ingestion", "data_ingestion.py"),
            ("Data Cleaning & Processing", "data_cleaning.py"),
            ("Demand & Revenue Analysis", "demand_analysis.py"),
            ("Delivery Performance Analysis", "delivery_analysis.py"),
            ("Spark SQL Aggregations", "spark_sql_analysis.py"),
            ("Output Verification & Export", "export_results.py")
        ]
        
        total_steps = len(steps)
        progress_bar = st.progress(0)
        status_text = st.empty()
        output_logs = []
        
        success_all = True
        for i, (step_name, script_name) in enumerate(steps):
            status_text.markdown(f"**Step {i+1} of {total_steps}**: Running `{script_name}` ({step_name})...")
            script_path = os.path.join("src", script_name)
            
            try:
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                
                output_logs.append(f"=== {script_name} ===\n{result.stdout}")
                if result.stderr:
                    output_logs.append(result.stderr)
                    
                if result.returncode != 0:
                    success_all = False
                    output_logs.append(f"[X] Error: {script_name} failed with exit code {result.returncode}")
                    break
            except Exception as e:
                success_all = False
                output_logs.append(f"[X] Exception running {script_name}: {e}")
                break
                
            # Update progress bar
            progress_bar.progress((i + 1) / total_steps)
            
        if success_all:
            status_text.markdown("✅ **All pipeline steps completed successfully!**")
            st.success("✅ All datasets successfully processed through Apache Spark!")
            with st.expander("🔍 View Detailed Execution Logs"):
                st.code("\n".join(output_logs))
            st.rerun()
        else:
            status_text.markdown("❌ **Pipeline execution failed.**")
            st.error("❌ Pipeline failed during execution. Check logs below:")
            with st.expander("🔍 View Error Logs"):
                st.code("\n".join(output_logs))