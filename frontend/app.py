import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import date
st.set_page_config(
    page_title="Restaurant Sales Dashboard",
    page_icon="🍽️",
    layout="wide",
)

API_BASE = "http://localhost:8000"
def api_get(endpoint, params=None):
    try:
        resp = requests.get(f"{API_BASE}/{endpoint}", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None

st.title("🍽️ Restaurant Sales Dashboard")
st.divider()

st.sidebar.header("Filters")

start_date = st.sidebar.date_input(
    "From Date",
    value=date(2024, 1, 1),
    min_value=date(2024, 1, 1),
    max_value=date(2024, 12, 31),
)

end_date = st.sidebar.date_input(
    "To Date",
    value=date(2024, 12, 31),
    min_value=date(2024, 1, 1),
    max_value=date(2024, 12, 31),
)

params = {
    "start_date": str(start_date),
    "end_date":   str(end_date),
}
st.subheader("📊 Key Performance Indicators")

kpi_data = api_get("kpi", params)

if kpi_data:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Revenue", f"Rs.{kpi_data['total_revenue']:,.0f}")
    with col2:
        st.metric("Total Orders", kpi_data['total_orders'])
    with col3:
        st.metric("Avg Order Value", f"Rs.{kpi_data['avg_order_value']:,.0f}")
    with col4:
        st.metric("Unique Customers", kpi_data['unique_customers'])
    with col5:
        st.metric("Repeat Rate", f"{kpi_data['repeat_customer_pct']}%")

st.divider()
st.subheader("🏆 Bestselling Items")

best_data = api_get("bestsellers", params)

if best_data:
    df_best = pd.DataFrame(best_data["items"])
    
    fig = px.bar(
        df_best,
        x="total_revenue",
        y="item_name",
        orientation="h",
        color="total_revenue",
        color_continuous_scale="Reds",
        labels={"total_revenue": "Revenue (Rs.)", "item_name": "Item"},
    )
    
    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        height=350,
        yaxis=dict(categoryorder="total ascending"),
    )
    
    st.plotly_chart(fig, use_container_width=True)

    