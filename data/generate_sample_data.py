import pandas as pd
import random
from datetime import datetime, timedelta
random.seed(42)

MENU_ITEMS = [
    {"name": "Butter Chicken",  "category": "Main Course", "price": 280},
    {"name": "Paneer Tikka",    "category": "Starter",     "price": 180},
    {"name": "Masala Dosa",     "category": "Breakfast",   "price": 120},
    {"name": "Biryani",         "category": "Main Course", "price": 320},
    {"name": "Dal Tadka",       "category": "Main Course", "price": 160},
    {"name": "Gulab Jamun",     "category": "Dessert",     "price": 80},
    {"name": "Mango Lassi",     "category": "Beverages",   "price": 90},
    {"name": "Samosa",          "category": "Starter",     "price": 50},
    {"name": "Filter Coffee",   "category": "Beverages",   "price": 60},
    {"name": "Naan",            "category": "Bread",       "price": 40},
]
CUSTOMERS = [f"CUST{str(i).zfill(4)}" for i in range(1, 101)]

REPEAT_CUSTOMERS = CUSTOMERS[:30]
CASUAL_CUSTOMERS = CUSTOMERS[30:]
def random_datetime(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    base = start_date + timedelta(days=random_days)
    
    r = random.random()
    if r < 0.35:
        hour = random.randint(12, 14)
    elif r < 0.65:
        hour = random.randint(19, 21)
    elif r < 0.80:
        hour = random.randint(8, 11)
    else:
        hour = random.randint(15, 18)
    
    minute = random.randint(0, 59)
    return base.replace(hour=hour, minute=minute)
def generate_orders(n=500):
    start_date = datetime(2024, 1, 1)
    end_date   = datetime(2024, 12, 31)
    
    rows = []
    order_id = 1000

    for _ in range(n):
        if random.random() < 0.60:
            customer_id = random.choice(REPEAT_CUSTOMERS)
        else:
            customer_id = random.choice(CASUAL_CUSTOMERS)

        order_dt = random_datetime(start_date, end_date)
        
        num_items = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
        selected_items = random.sample(MENU_ITEMS, num_items)

        for item in selected_items:
            qty = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
            rows.append({
                "order_id":       order_id,
                "order_datetime": order_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "customer_id":    customer_id,
                "item_name":      item["name"],
                "category":       item["category"],
                "quantity":       qty,
                "unit_price":     item["price"],
                "total_price":    item["price"] * qty,
                "payment_method": random.choice(["Cash", "UPI", "Card"]),
                "order_type":     random.choice(["Dine-in", "Takeaway", "Delivery"]),
            })
        order_id += 1

    return pd.DataFrame(rows)
if __name__ == "__main__":
    print("Generating sample data...")
    df = generate_orders(500)
    
    df.to_csv("data/sample_orders.csv", index=False)
    
    print(f"Done! {len(df)} rows saved to data/sample_orders.csv")
    print(f"Total revenue: Rs.{df['total_price'].sum():,.0f}")
    print(f"Unique customers: {df['customer_id'].nunique()}")
    print(f"Unique items: {df['item_name'].nunique()}")