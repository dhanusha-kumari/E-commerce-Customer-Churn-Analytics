# E-Commerce Customer Insights & Churn Analytics Dashboard

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Random%20Forest-orange.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end customized **E-Commerce Customer Insights & Churn Risk Analytics Dashboard** built with Python, SQLite, Pandas, Scikit-Learn, Plotly, and Streamlit.

**Developed by**: Pyda Venkata Dhanusha Kumari

---

## 🌟 Key Features

- **Relational SQL Database Engine (`db_setup.py`)**: SQLite database storing `customers` and `orders` tables. Custom SQL queries using `JOIN` and `GROUP BY` to aggregate metrics.
- **RFM Customer Segmentation (`analytics.py`)**: Computes Recency, Frequency, and Monetary scores to classify customers into behavioral cohorts (*Champions*, *Loyal Customers*, *At-Risk VIPs*, *Hibernating / Lost*).
- **Machine Learning Churn Prediction**: Scikit-Learn **Random Forest Classifier** predicting customer churn probabilities (%) and feature importances.
- **Interactive Streamlit Dashboard (`app.py`)**:
  - Executive KPI Cards (Total Revenue, Active Customers, Avg Order Value, High Risk Churn Count).
  - Sidebar filters for Order Date Range, Customer Category, Spend Sliders, and Risk Level Tiers.
  - **3 Primary Plotly Visualizations**:
    1. Monthly Sales & Revenue Growth Trends
    2. Customer Segment Breakdown (Donut Chart & Spend Distribution)
    3. Recency vs. Frequency Churn Risk Heatmap & Matrix
- **Targeted Retention Actions Explorer**: Interactive table with automated retention promos and CSV export functionality.

---

## 📁 Repository Structure

```text
├── app.py              # Main Streamlit Dashboard application
├── analytics.py        # RFM processing & Random Forest ML churn predictor
├── db_setup.py         # SQLite database schema, seeder & relational SQL queries
├── requirements.txt    # Project Python dependencies
├── .gitignore          # Git exclusion config
└── README.md           # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Clone & Set Up Workspace
```bash
git clone <your-repo-url>
cd E-commerce_Customer_churn Analytics
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize SQLite Database
```bash
python db_setup.py
```

### 4. Run Streamlit Application
```bash
python -m streamlit run app.py
```
Access the application in your browser at `http://localhost:8501`.

---

## 📊 Tech Stack

- **Frontend / Dashboard**: Streamlit, Plotly
- **Data Engine & Storage**: SQLite, SQL, Pandas, NumPy
- **Machine Learning**: Scikit-Learn (Random Forest Classifier, StandardScaler)
