from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
from datetime import date, datetime
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

def save_data(df):
    df.drop(columns=["date", "hour", "month", "weekday"],
            errors="ignore").to_csv(DATA_PATH, index=False)

class OrderCreate(BaseModel):
    customer_id:    str
    item_name:      str
    category:       str
    quantity:       int
    unit_price:     float
    payment_method: str
    order_type:     str

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

@app.get("/orders")
def get_orders(
    start_date: Optional[date] = Query(None),
    end_date:   Optional[date] = Query(None),
):
    df = load_data()
    
    if start_date:
        df = df[df["date"] >= start_date]
    if end_date:
        df = df[df["date"] <= end_date]
    
    df_sorted = df.sort_values("order_datetime", ascending=False).head(50)
    
    return {
        "total_rows": len(df),
        "orders": df_sorted[[
            "order_id", "order_datetime", "customer_id",
            "item_name", "category", "quantity",
            "unit_price", "total_price", "payment_method", "order_type",
        ]].to_dict(orient="records"),
    }

# ── CRUD Operations ───────────────────────────────────────────────────────────

@app.post("/orders/create")
def create_order(order: OrderCreate):
    df = load_data()
    
    new_order_id = int(df["order_id"].max()) + 1
    new_row = {
        "order_id":       new_order_id,
        "order_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "customer_id":    order.customer_id,
        "item_name":      order.item_name,
        "category":       order.category,
        "quantity":       order.quantity,
        "unit_price":     order.unit_price,
        "total_price":    order.unit_price * order.quantity,
        "payment_method": order.payment_method,
        "order_type":     order.order_type,
    }
    
    new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(new_df)
    
    return {
        "message": "Order created successfully",
        "order_id": new_order_id,
        "total_price": new_row["total_price"],
    }

@app.get("/orders/{order_id}")
def get_single_order(order_id: int):
    df = load_data()
    
    order = df[df["order_id"] == order_id]
    
    if order.empty:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    return {"order": order[[
        "order_id", "order_datetime", "customer_id",
        "item_name", "category", "quantity",
        "unit_price", "total_price", "payment_method", "order_type",
    ]].to_dict(orient="records")}

@app.put("/orders/{order_id}")
def update_order(order_id: int, order: OrderCreate):
    df = load_data()
    
    if not (df["order_id"] == order_id).any():
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    df.loc[df["order_id"] == order_id, "customer_id"]    = order.customer_id
    df.loc[df["order_id"] == order_id, "item_name"]      = order.item_name
    df.loc[df["order_id"] == order_id, "category"]       = order.category
    df.loc[df["order_id"] == order_id, "quantity"]        = order.quantity
    df.loc[df["order_id"] == order_id, "unit_price"]     = order.unit_price
    df.loc[df["order_id"] == order_id, "total_price"]    = order.unit_price * order.quantity
    df.loc[df["order_id"] == order_id, "payment_method"] = order.payment_method
    df.loc[df["order_id"] == order_id, "order_type"]     = order.order_type
    
    save_data(df)
    
    return {"message": f"Order {order_id} updated successfully"}

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    df = load_data()
    
    if not (df["order_id"] == order_id).any():
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    df = df[df["order_id"] != order_id]
    save_data(df)
    
    return {"message": f"Order {order_id} deleted successfully"}