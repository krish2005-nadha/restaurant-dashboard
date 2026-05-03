from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from datetime import date
from typing import Optional

app = FastAPI(
    title="Restaurant Sales Dashboard API",
    description="Backend for PRJ-053",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
DATA_PATH = os.path.join("data", "sample_orders.csv")

def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["order_datetime"])
    df["date"]    = df["order_datetime"].dt.date
    df["hour"]    = df["order_datetime"].dt.hour
    df["month"]   = df["order_datetime"].dt.month
    df["weekday"] = df["order_datetime"].dt.day_name()
    return df

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running!"}

@app.get("/health")
def health():
    df = load_data()
    return {
        "status": "ok",
        "total_rows": len(df),
        "date_range": {
            "start": str(df["date"].min()),
            "end":   str(df["date"].max()),
        }
    }
@app.get("/kpi")
def get_kpis(
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
):
    df = load_data()
    
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
    
    total_revenue    = float(df["total_price"].sum())
    order_level      = df.groupby("order_id")["total_price"].sum()
    total_orders     = int(order_level.count())
    avg_order_value  = float(order_level.mean())
    unique_customers = int(df["customer_id"].nunique())
    
    orders_per_customer = df.groupby("customer_id")["order_id"].nunique()
    repeat_customers    = int((orders_per_customer >= 2).sum())
    repeat_rate         = round(repeat_customers / unique_customers * 100, 1)
    
    return {
        "total_revenue":       round(total_revenue, 2),
        "total_orders":        total_orders,
        "avg_order_value":     round(avg_order_value, 2),
        "unique_customers":    unique_customers,
        "repeat_customers":    repeat_customers,
        "repeat_customer_pct": repeat_rate,
    }
@app.get("/bestsellers")
def get_bestsellers(
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
    top_n: int = Query(5),
):
    df = load_data()
    
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
    
    grouped = df.groupby(["item_name", "category"]).agg(
        total_revenue  = ("total_price", "sum"),
        total_quantity = ("quantity",    "sum"),
        total_orders   = ("order_id",    "nunique"),
    ).reset_index()
    
    grouped = grouped.sort_values("total_revenue", ascending=False).head(top_n)
    
    return {"items": grouped.to_dict(orient="records")}
@app.get("/peak-hours")
def get_peak_hours(
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
):
    df = load_data()
    
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
    
    hourly = df.groupby("hour").agg(
        revenue = ("total_price", "sum"),
        orders  = ("order_id",   "nunique"),
    ).reset_index()
    
    all_hours = pd.DataFrame({"hour": range(24)})
    hourly = all_hours.merge(hourly, on="hour", how="left").fillna(0)
    hourly["orders"] = hourly["orders"].astype(int)
    
    return {"hourly": hourly.to_dict(orient="records")}
@app.get("/repeat-customers")
def get_repeat_customers(
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
):
    df = load_data()
    
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
    
    cust = df.groupby("customer_id").agg(
        total_spent  = ("total_price", "sum"),
        total_orders = ("order_id",   "nunique"),
        last_visit   = ("order_datetime", "max"),
    ).reset_index()
    
    cust = cust[cust["total_orders"] >= 2]
    cust = cust.sort_values("total_spent", ascending=False).head(10)
    cust["last_visit"] = cust["last_visit"].astype(str)
    
    return {"customers": cust.to_dict(orient="records")}
@app.get("/monthly-trend")
def get_monthly_trend(
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
):
    df = load_data()
    
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
    
    monthly = df.groupby("month").agg(
        revenue = ("total_price", "sum"),
        orders  = ("order_id",   "nunique"),
    ).reset_index().sort_values("month")
    
    return {"monthly": monthly.to_dict(orient="records")}
@app.get("/category-breakdown")
def get_category_breakdown(
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
):
    df = load_data()
    
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
    
    cat = df.groupby("category").agg(
        revenue    = ("total_price", "sum"),
        orders     = ("order_id",   "nunique"),
        items_sold = ("quantity",   "sum"),
    ).reset_index()
    
    cat["revenue_pct"] = (cat["revenue"] / cat["revenue"].sum() * 100).round(1)
    cat = cat.sort_values("revenue", ascending=False)
    
    return {"categories": cat.to_dict(orient="records")}
