import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# ── Health tests ──────────────────────
def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["total_rows"] > 0

# ── KPI tests ─────────────────────────
def test_kpi_fields():
    resp = client.get("/kpi")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_revenue" in data
    assert "total_orders" in data
    assert "avg_order_value" in data
    assert "unique_customers" in data
    assert "repeat_customer_pct" in data

def test_kpi_positive_values():
    data = client.get("/kpi").json()
    assert data["total_revenue"] > 0
    assert data["total_orders"] > 0
    assert data["unique_customers"] > 0

def test_kpi_repeat_rate_range():
    data = client.get("/kpi").json()
    assert 0 <= data["repeat_customer_pct"] <= 100

def test_kpi_date_filter():
    resp = client.get("/kpi?start_date=2024-06-01&end_date=2024-06-30")
    assert resp.status_code == 200
    assert resp.json()["total_orders"] > 0

# ── Bestsellers tests ─────────────────
def test_bestsellers_returns_items():
    resp = client.get("/bestsellers")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) > 0

def test_bestsellers_top_n():
    data = client.get("/bestsellers?top_n=3").json()
    assert len(data["items"]) <= 3

def test_bestsellers_has_revenue():
    items = client.get("/bestsellers").json()["items"]
    for item in items:
        assert "total_revenue" in item
        assert item["total_revenue"] > 0

# ── Peak hours tests ──────────────────
def test_peak_hours_24():
    data = client.get("/peak-hours").json()
    assert len(data["hourly"]) == 24

def test_peak_hours_no_negative():
    for row in client.get("/peak-hours").json()["hourly"]:
        assert row["revenue"] >= 0

def test_lunch_is_peak():
    hourly = client.get("/peak-hours").json()["hourly"]
    hour_rev = {h["hour"]: h["revenue"] for h in hourly}
    avg = sum(hour_rev.values()) / 24
    assert hour_rev[13] > avg

# ── Orders tests ──────────────────────
def test_orders_returns_list():
    resp = client.get("/orders")
    assert resp.status_code == 200
    assert len(resp.json()["orders"]) > 0

def test_orders_has_columns():
    orders = client.get("/orders").json()["orders"]
    row = orders[0]
    assert "order_id" in row
    assert "item_name" in row
    assert "total_price" in row

# ── Repeat customers tests ────────────
def test_repeat_customers_min_orders():
    customers = client.get("/repeat-customers").json()["customers"]
    for c in customers:
        assert c["total_orders"] >= 2

def test_repeat_customers_sorted():
    customers = client.get("/repeat-customers").json()["customers"]
    spends = [c["total_spent"] for c in customers]
    assert spends == sorted(spends, reverse=True)

# ── Monthly trend tests ───────────────
def test_monthly_trend_has_months():
    data = client.get("/monthly-trend").json()
    assert len(data["monthly"]) > 0

def test_monthly_revenue_positive():
    for row in client.get("/monthly-trend").json()["monthly"]:
        assert row["revenue"] > 0

# ── Category tests ────────────────────
def test_category_breakdown():
    resp = client.get("/category-breakdown")
    assert resp.status_code == 200
    assert len(resp.json()["categories"]) > 0

def test_category_has_percentage():
    cats = client.get("/category-breakdown").json()["categories"]
    for cat in cats:
        assert "revenue_pct" in cat
        assert cat["revenue_pct"] > 0
# ── CRUD tests ────────────────────────
def test_create_order():
    new_order = {
        "customer_id":    "CUST9999",
        "item_name":      "Biryani",
        "category":       "Main Course",
        "quantity":       2,
        "unit_price":     320,
        "payment_method": "UPI",
        "order_type":     "Dine-in",
    }
    resp = client.post("/orders/create", json=new_order)
    assert resp.status_code == 200
    data = resp.json()
    assert "order_id" in data
    assert data["total_price"] == 640

def test_get_single_order():
    resp = client.get("/orders/1000")
    assert resp.status_code == 200
    data = resp.json()
    assert "order" in data
    assert len(data["order"]) > 0

def test_get_invalid_order():
    resp = client.get("/orders/99999")
    assert resp.status_code == 404

def test_update_order():
    update_data = {
        "customer_id":    "CUST0001",
        "item_name":      "Naan",
        "category":       "Bread",
        "quantity":       3,
        "unit_price":     40,
        "payment_method": "Cash",
        "order_type":     "Takeaway",
    }
    resp = client.put("/orders/1000", json=update_data)
    assert resp.status_code == 200
    assert "updated" in resp.json()["message"]

def test_update_invalid_order():
    update_data = {
        "customer_id":    "CUST0001",
        "item_name":      "Naan",
        "category":       "Bread",
        "quantity":       1,
        "unit_price":     40,
        "payment_method": "Cash",
        "order_type":     "Takeaway",
    }
    resp = client.put("/orders/99999", json=update_data)
    assert resp.status_code == 404

def test_delete_order():
    new_order = {
        "customer_id":    "CUST1234",
        "item_name":      "Samosa",
        "category":       "Starter",
        "quantity":       1,
        "unit_price":     50,
        "payment_method": "Cash",
        "order_type":     "Takeaway",
    }
    create_resp = client.post("/orders/create", json=new_order)
    order_id = create_resp.json()["order_id"]
    
    delete_resp = client.delete(f"/orders/{order_id}")
    assert delete_resp.status_code == 200
    assert "deleted" in delete_resp.json()["message"]

def test_delete_invalid_order():
    resp = client.delete("/orders/99999")
    assert resp.status_code == 404
# ── Week 2 tests ──────────────────────

def test_weekly_trend():
    resp = client.get("/weekly-trend")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["weekly"]) == 7

def test_weekly_correct_order():
    weekly = client.get("/weekly-trend").json()["weekly"]
    days = [w["weekday"] for w in weekly]
    assert days[0] == "Monday"
    assert days[-1] == "Sunday"

def test_payment_methods():
    resp = client.get("/payment-methods")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["payment_methods"]) > 0

def test_payment_has_percentage():
    methods = client.get("/payment-methods").json()["payment_methods"]
    for m in methods:
        assert "revenue_pct" in m
        assert m["revenue_pct"] > 0

def test_smart_insights():
    resp = client.get("/smart-insights")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["insights"]) == 4

def test_smart_insights_fields():
    insights = client.get("/smart-insights").json()["insights"]
    for insight in insights:
        assert "title" in insight
        assert "message" in insight
        assert "type" in insight

def test_export_orders_csv():
    resp = client.get("/export/orders")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]

def test_export_summary_csv():
    resp = client.get("/export/summary")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]

def test_order_type_filter():
    resp = client.get("/orders?order_type=Dine-in")
    assert resp.status_code == 200
    orders = resp.json()["orders"]
    for order in orders:
        assert order["order_type"] == "Dine-in"

def test_category_filter():
    resp = client.get("/orders?category=Starter")
    assert resp.status_code == 200
    orders = resp.json()["orders"]
    for order in orders:
        assert order["category"] == "Starter"

