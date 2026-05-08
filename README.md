arkdown# 🍽️ Restaurant Sales Dashboard — PRJ-053

**Student:** KRISHNA KUMAR N
**Reg No:** 411723205027
**Department:** IT
**Stack:** FastAPI + Streamlit + Pandas

---

## 📁 Project Structure
restaurant_dashboard/
├── backend/
│   └── main.py
├── frontend/
│   └── app.py
├── data/
│   ├── generate_sample_data.py
│   └── sample_orders.csv
├── tests/
│   └── test_week1.py
└── README.md

## ⚙️ Setup Instructions

### 1. Install dependencies
pip install fastapi uvicorn pandas plotly streamlit requests pytest httpx python-multipart

### 2. Generate sample data
python data/generate_sample_data.py

### 3. Start backend
python -m uvicorn backend.main:app --reload --port 8000

### 4. Start frontend
python -m streamlit run frontend/app.py

## 🔌 API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Data status |
| `/kpi` | GET | KPI metrics |
| `/orders` | GET | Recent orders |
| `/orders/{id}` | GET | Single order |
| `/orders/create` | POST | Create order |
| `/orders/{id}` | PUT | Update order |
| `/orders/{id}` | DELETE | Delete order |
| `/bestsellers` | GET | Top items |
| `/peak-hours` | GET | Hourly stats |
| `/monthly-trend` | GET | Monthly revenue |
| `/repeat-customers` | GET | Loyal customers |
| `/category-breakdown` | GET | Category stats |

## 🧪 Running Tests
python -m pytest tests/test_week1.py -v

## ✅ Week 1 Checklist
- [x] Sample data generated
- [x] FastAPI backend with 13 routes
- [x] CRUD operations
- [x] Streamlit dashboard
- [x] All tests passing
- [x] GitHub commits