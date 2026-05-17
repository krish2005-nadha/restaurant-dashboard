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

# ── Sidebar filters ────────────────────────────────────────────────────────────
st.sidebar.header("🔍 Filters")

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

order_type = st.sidebar.selectbox(
    "Order Type",
    options=["All", "Dine-in", "Takeaway", "Delivery"],
)

category = st.sidebar.selectbox(
    "Category",
    options=["All", "Main Course", "Starter", "Breakfast", "Dessert", "Beverages", "Bread"],
)

st.sidebar.divider()
st.sidebar.header("📤 Export Data")

params = {
    "start_date": str(start_date),
    "end_date":   str(end_date),
}

if order_type != "All":
    params["order_type"] = order_type
if category != "All":
    params["category"] = category

# ── Export buttons ─────────────────────────────────────────────────────────────
if st.sidebar.button("⬇️ Download Orders CSV"):
    resp = requests.get(f"{API_BASE}/export/orders", params=params)
    if resp.status_code == 200:
        st.sidebar.download_button(
            label="Save orders.csv",
            data=resp.content,
            file_name="orders.csv",
            mime="text/csv",
        )

if st.sidebar.button("⬇️ Download Summary CSV"):
    resp = requests.get(f"{API_BASE}/export/summary", params=params)
    if resp.status_code == 200:
        st.sidebar.download_button(
            label="Save summary.csv",
            data=resp.content,
            file_name="sales_summary.csv",
            mime="text/csv",
        )

# ── KPI Cards ──────────────────────────────────────────────────────────────────
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

# ── Smart Insights ─────────────────────────────────────────────────────────────
st.subheader("💡 Smart Insights")

insights_data = api_get("smart-insights", params)

if insights_data:
    cols = st.columns(4)
    icons = {"warning": "⚠️", "success": "✅", "info": "ℹ️"}
    for col, insight in zip(cols, insights_data["insights"]):
        with col:
            icon = icons.get(insight["type"], "ℹ️")
            st.info(f"**{icon} {insight['title']}**\n\n{insight['message']}")

st.divider()

# ── Row 1: Bestsellers + Category ──────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
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

with col_right:
    st.subheader("🍱 Category Breakdown")
    cat_data = api_get("category-breakdown", params)
    if cat_data:
        df_cat = pd.DataFrame(cat_data["categories"])
        fig = px.pie(
            df_cat,
            values="revenue",
            names="category",
            hole=0.4,
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Row 2: Peak Hours + Payment Methods ────────────────────────────────────────
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.subheader("⏰ Peak Hours")
    hour_data = api_get("peak-hours", params)
    if hour_data:
        df_hour = pd.DataFrame(hour_data["hourly"])
        fig = px.bar(
            df_hour,
            x="hour",
            y="revenue",
            color="revenue",
            color_continuous_scale="Oranges",
            labels={"hour": "Hour of Day", "revenue": "Revenue (Rs.)"},
        )
        fig.update_layout(
            coloraxis_showscale=False,
            height=300,
            xaxis=dict(tickmode="linear", dtick=1),
        )
        st.plotly_chart(fig, use_container_width=True)

with col_r2:
    st.subheader("💳 Payment Methods")
    payment_data = api_get("payment-methods", params)
    if payment_data:
        df_pay = pd.DataFrame(payment_data["payment_methods"])
        fig = px.pie(
            df_pay,
            values="revenue",
            names="payment_method",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Row 3: Monthly + Weekly ────────────────────────────────────────────────────
col_l3, col_r3 = st.columns(2)

with col_l3:
    st.subheader("📈 Monthly Revenue Trend")
    monthly_data = api_get("monthly-trend", params)
    if monthly_data:
        df_mon = pd.DataFrame(monthly_data["monthly"])
        fig = px.line(
            df_mon,
            x="month",
            y="revenue",
            markers=True,
            labels={"month": "Month", "revenue": "Revenue (Rs.)"},
        )
        fig.update_traces(
            line=dict(color="#e94560", width=3),
            marker=dict(size=8, color="#e94560"),
        )
        fig.update_layout(
            height=300,
            xaxis=dict(
                tickmode="array",
                tickvals=list(range(1, 13)),
                ticktext=["Jan","Feb","Mar","Apr","May","Jun",
                          "Jul","Aug","Sep","Oct","Nov","Dec"],
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

with col_r3:
    st.subheader("📅 Weekly Revenue Trend")
    weekly_data = api_get("weekly-trend", params)
    if weekly_data:
        df_week = pd.DataFrame(weekly_data["weekly"])
        fig = px.bar(
            df_week,
            x="weekday",
            y="revenue",
            color="revenue",
            color_continuous_scale="Blues",
            labels={"weekday": "Day", "revenue": "Revenue (Rs.)"},
        )
        fig.update_layout(
            coloraxis_showscale=False,
            height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Tabs: Orders + Repeat Customers ───────────────────────────────────────────
tab1, tab2 = st.tabs(["📋 Recent Orders", "🔁 Repeat Customers"])

with tab1:
    orders_data = api_get("orders", params)
    if orders_data:
        df_orders = pd.DataFrame(orders_data["orders"])
        st.caption(f"Showing {len(df_orders)} of {orders_data['total_rows']} orders")
        st.dataframe(
            df_orders.rename(columns={
                "order_id":       "Order ID",
                "order_datetime": "Date/Time",
                "customer_id":    "Customer",
                "item_name":      "Item",
                "category":       "Category",
                "quantity":       "Qty",
                "unit_price":     "Unit Price",
                "total_price":    "Total",
                "payment_method": "Payment",
                "order_type":     "Type",
            }),
            use_container_width=True,
            hide_index=True,
            height=400,
        )

with tab2:
    repeat_data = api_get("repeat-customers", params)
    if repeat_data:
        df_rep = pd.DataFrame(repeat_data["customers"])
        st.dataframe(
            df_rep.rename(columns={
                "customer_id":  "Customer ID",
                "total_spent":  "Total Spent (Rs.)",
                "total_orders": "Total Orders",
                "last_visit":   "Last Visit",
            }),
            use_container_width=True,
            hide_index=True,
            height=400,
        )

st.divider()
st.caption("PRJ-053 ")