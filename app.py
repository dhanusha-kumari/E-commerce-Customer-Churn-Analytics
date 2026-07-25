import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import custom modules
from db_setup import init_db, get_customer_summary_sql, get_monthly_sales_sql, get_raw_orders_sql
from analytics import process_rfm_and_churn

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Customer Insights & Churn Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI
st.markdown("""
    <style>
        /* Main background & fonts */
        .main {
            background-color: #0f172a;
            color: #f8fafc;
        }
        
        /* Header styling */
        .header-container {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 50%, #3b82f6 100%);
            padding: 1.8rem 2rem;
            border-radius: 14px;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            border: 1px solid #334155;
        }
        .header-title {
            color: #ffffff;
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .header-subtitle {
            color: #94a3b8;
            font-size: 1.05rem;
            margin-top: 0.4rem;
            font-weight: 400;
        }
        .developer-badge {
            display: inline-block;
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
            border: 1px solid #3b82f6;
            padding: 0.35rem 0.85rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 0.8rem;
        }

        /* Metric Cards */
        .metric-card {
            background-color: #1e293b;
            border: 1px solid #334155;
            padding: 1.2rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            border-color: #3b82f6;
        }
        .metric-label {
            color: #94a3b8;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-value {
            color: #f8fafc;
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0.4rem 0;
        }
        .metric-delta {
            font-size: 0.85rem;
            font-weight: 600;
        }
        .text-green { color: #10b981; }
        .text-red { color: #ef4444; }
        .text-blue { color: #3b82f6; }
        .text-yellow { color: #f59e0b; }

        /* Hide streamlit default top padding */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Loading & Initialization
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    init_db()
    df_customers = get_customer_summary_sql()
    df_monthly = get_monthly_sales_sql()
    df_orders = get_raw_orders_sql()
    df_rfm_churn, feat_importances, _ = process_rfm_and_churn(df_customers)
    return df_rfm_churn, df_monthly, df_orders, feat_importances

df_rfm_churn, df_monthly, df_orders, feat_importances = load_data()

# ---------------------------------------------------------
# Sidebar Navigation & Filters
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric-line/100/3b82f6/shopping-bag.png", width=70)
st.sidebar.title("🔍 Analytics Controls")
st.sidebar.markdown("Filter dashboard metrics & customer segments:")

# Date Range Filter
min_date = pd.to_datetime(df_orders['order_date']).min().date()
max_date = pd.to_datetime(df_orders['order_date']).max().date()

selected_date_range = st.sidebar.date_input(
    "📅 Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Category Filter
all_categories = sorted(df_rfm_churn['preferred_category'].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "🏷️ Customer Category",
    options=all_categories,
    default=all_categories
)

# Churn Risk Level Filter
risk_levels = ["All", "High Churn Risk", "Moderate Risk", "Low Risk"]
selected_risk = st.sidebar.selectbox("⚠️ Churn Risk Tier", options=risk_levels)

# Minimum Spent Slider
max_spend_val = float(df_rfm_churn['total_spent'].max())
min_spent = st.sidebar.slider(
    "💰 Min Total Spent ($)",
    min_value=0.0,
    max_value=max_spend_val,
    value=0.0,
    step=50.0
)

# Filter Application
filtered_customers = df_rfm_churn.copy()

if selected_categories:
    filtered_customers = filtered_customers[filtered_customers['preferred_category'].isin(selected_categories)]

if selected_risk != "All":
    filtered_customers = filtered_customers[filtered_customers['churn_risk_level'] == selected_risk]

filtered_customers = filtered_customers[filtered_customers['total_spent'] >= min_spent]

# Filter orders by date range
if len(selected_date_range) == 2:
    start_d, end_d = selected_date_range
    filtered_orders = df_orders[
        (pd.to_datetime(df_orders['order_date']).dt.date >= start_d) &
        (pd.to_datetime(df_orders['order_date']).dt.date <= end_d)
    ]
else:
    filtered_orders = df_orders.copy()

# ---------------------------------------------------------
# Main App Header
# ---------------------------------------------------------
st.markdown("""
    <div class="header-container">
        <div class="header-title">E-Commerce Customer Insights & Churn Analytics Dashboard</div>
        <div class="header-subtitle">Advanced Customer Segmentation, SQL Transactional Analytics & ML Churn Risk Prediction</div>
        <div class="developer-badge">✨ Developed by Pyda Venkata Dhanusha Kumari</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# KPI Metrics Row
# ---------------------------------------------------------
total_revenue = filtered_customers['total_spent'].sum()
active_cust_count = len(filtered_customers)
avg_aov = filtered_customers['avg_order_value'].mean() if active_cust_count > 0 else 0
high_risk_count = len(filtered_customers[filtered_customers['churn_risk_level'] == 'High Churn Risk'])
high_risk_pct = (high_risk_count / active_cust_count * 100) if active_cust_count > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value text-blue">${total_revenue:,.2f}</div>
            <div class="metric-delta text-green">▲ Aggregated via SQL</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Customers</div>
            <div class="metric-value text-blue">{active_cust_count:,}</div>
            <div class="metric-delta text-blue">Filtered Cohort</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Order Value</div>
            <div class="metric-value text-green">${avg_aov:,.2f}</div>
            <div class="metric-delta text-green">Per Completed Order</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">High Churn Risk</div>
            <div class="metric-value text-red">{high_risk_count} <span style="font-size:1.1rem; color:#f8fafc;">({high_risk_pct:.1f}%)</span></div>
            <div class="metric-delta text-red">Random Forest Predictions</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3 Key Visualizations Section
# ---------------------------------------------------------
st.subheader("📊 Executive Analytics & Visualizations")

tab1, tab2, tab3 = st.tabs([
    "📈 1. Monthly Sales Trends", 
    "🎯 2. Customer Segment Distribution", 
    "🔥 3. Churn Risk Heatmap & Matrix"
])

# ---------------------------------------------------------
# CHART 1: Monthly Sales Trends
# ---------------------------------------------------------
with tab1:
    st.markdown("#### Monthly Sales Revenue & Active Customer Growth")
    
    # Process filtered orders monthly
    df_filtered_monthly = filtered_orders[filtered_orders['status'] == 'Completed'].copy()
    df_filtered_monthly['year_month'] = pd.to_datetime(df_filtered_monthly['order_date']).dt.to_period('M').astype(str)
    
    monthly_agg = df_filtered_monthly.groupby('year_month').agg(
        revenue=('amount', 'sum'),
        orders=('order_id', 'count'),
        unique_customers=('customer_id', 'nunique')
    ).reset_index()

    if not monthly_agg.empty:
        fig_monthly = go.Figure()
        
        # Line for Revenue
        fig_monthly.add_trace(go.Scatter(
            x=monthly_agg['year_month'],
            y=monthly_agg['revenue'],
            name="Monthly Revenue ($)",
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3, shape='spline'),
            marker=dict(size=7, color='#60a5fa'),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.15)'
        ))

        # Bar for Orders
        fig_monthly.add_trace(go.Bar(
            x=monthly_agg['year_month'],
            y=monthly_agg['orders'],
            name="Completed Orders",
            yaxis='y2',
            marker_color='rgba(16, 185, 129, 0.4)',
            marker_line_color='#10b981',
            marker_line_width=1
        ))

        fig_monthly.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            height=420,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(title="Month", showgrid=False),
            yaxis=dict(title="Revenue ($)", showgrid=True, gridcolor='#334155'),
            yaxis2=dict(title="Order Count", overlaying='y', side='right', showgrid=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified"
        )
        st.plotly_chart(fig_monthly, width='stretch')
    else:
        st.info("No order data available for the selected date range.")

# ---------------------------------------------------------
# CHART 2: Customer Segment Distribution (RFM)
# ---------------------------------------------------------
with tab2:
    col_seg1, col_seg2 = st.columns([1.2, 1])
    
    with col_seg1:
        st.markdown("#### Customer Breakdown by RFM Segment")
        segment_counts = filtered_customers['rfm_segment'].value_counts().reset_index()
        segment_counts.columns = ['rfm_segment', 'count']

        fig_donut = px.pie(
            segment_counts,
            values='count',
            names='rfm_segment',
            hole=0.5,
            color='rfm_segment',
            color_discrete_map={
                "Champions": "#10b981",
                "Loyal Customers": "#3b82f6",
                "Promising / New": "#06b6d4",
                "At-Risk VIPs": "#f59e0b",
                "Hibernating / Lost": "#ef4444",
                "Needs Attention": "#8b5cf6"
            }
        )
        fig_donut.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            height=400,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
        )
        st.plotly_chart(fig_donut, width='stretch')

    with col_seg2:
        st.markdown("#### Avg Monetary Spend per Segment")
        seg_spend = filtered_customers.groupby('rfm_segment')['total_spent'].mean().reset_index()
        seg_spend = seg_spend.sort_values(by='total_spent', ascending=True)

        fig_bar_spend = px.bar(
            seg_spend,
            x='total_spent',
            y='rfm_segment',
            orientation='h',
            labels={'total_spent': 'Avg Total Spend ($)', 'rfm_segment': 'Segment'},
            color='total_spent',
            color_continuous_scale='Viridis'
        )
        fig_bar_spend.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            height=400,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor='#334155')
        )
        st.plotly_chart(fig_bar_spend, width='stretch')

# ---------------------------------------------------------
# CHART 3: Churn Risk Heatmap & Matrix
# ---------------------------------------------------------
with tab3:
    col_heat1, col_heat2 = st.columns([1.3, 1])

    with col_heat1:
        st.markdown("#### Recency vs. Frequency Churn Risk Heatmap")
        st.caption("Average Churn Risk Probability (%) grouped by Recency & Frequency scores.")

        # Pivot table for Heatmap: R_score vs F_score avg churn probability
        pivot_churn = filtered_customers.pivot_table(
            index='R_score',
            columns='F_score',
            values='churn_risk_pct',
            aggfunc='mean'
        ).fillna(0)

        # Dynamically build axis labels from the actual pivot columns/index
        f_labels = [f'F{int(c)}' for c in pivot_churn.columns]
        r_label_map = {1: 'R1 (Inactive)', 2: 'R2', 3: 'R3', 4: 'R4 (Active)'}
        r_labels = [r_label_map.get(int(r), f'R{int(r)}') for r in pivot_churn.index]

        fig_heat = px.imshow(
            pivot_churn,
            labels=dict(x="Frequency Score (1=Low, 4=High)", y="Recency Score (1=Old, 4=Recent)", color="Avg Churn Risk %"),
            x=f_labels,
            y=r_labels,
            color_continuous_scale='Reds',
            text_auto='.1f'
        )
        fig_heat.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_heat, width='stretch')

    with col_heat2:
        st.markdown("#### Random Forest Feature Importances")
        st.caption("Key driver metrics predicting customer churn risk.")
        
        df_feat = pd.DataFrame(list(feat_importances.items()), columns=['Feature', 'Importance'])
        df_feat = df_feat.sort_values(by='Importance', ascending=True)

        fig_feat = px.bar(
            df_feat,
            x='Importance',
            y='Feature',
            orientation='h',
            color='Importance',
            color_continuous_scale='Blues'
        )
        fig_feat.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            height=400,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(gridcolor='#334155')
        )
        st.plotly_chart(fig_feat, width='stretch')

st.markdown("---")

# ---------------------------------------------------------
# Interactive Customer Risk Explorer Table
# ---------------------------------------------------------
st.subheader("⚡ Customer Churn Risk Explorer & Targeted Actions")

search_term = st.text_input("🔎 Search Customer Name, Email, or ID", placeholder="Type customer name or ID...")

display_df = filtered_customers.copy()

if search_term:
    display_df = display_df[
        display_df['name'].str.contains(search_term, case=False, na=False) |
        display_df['email'].str.contains(search_term, case=False, na=False) |
        display_df['customer_id'].str.contains(search_term, case=False, na=False)
    ]

# Format fields for display
display_table = display_df[[
    'customer_id', 'name', 'email', 'preferred_category', 'country', 
    'total_orders', 'total_spent', 'recency_days', 'rfm_segment', 
    'churn_risk_pct', 'churn_risk_level'
]].copy()

display_table.columns = [
    'Customer ID', 'Customer Name', 'Email', 'Category', 'Country', 
    'Total Orders', 'Total Spent ($)', 'Recency (Days)', 'RFM Segment', 
    'Churn Risk %', 'Risk Level'
]

# Action Recommendation Logic
def recommend_action(row):
    risk = row['Risk Level']
    seg = row['RFM Segment']
    if risk == 'High Churn Risk':
        return '🚨 Urgent: 25% Off Win-back Promo'
    elif seg == 'At-Risk VIPs':
        return '⭐ VIP Personal Outreach & Gift'
    elif seg == 'Champions':
        return '💎 Invite to Exclusive Loyalty Club'
    elif risk == 'Moderate Risk':
        return '📧 Re-engagement Email Campaign'
    else:
        return '✅ Retain via Standard Engagement'

display_table['Recommended Action'] = display_table.apply(recommend_action, axis=1)

st.dataframe(
    display_table.style.format({
        'Total Spent ($)': '${:,.2f}',
        'Churn Risk %': '{:.1f}%',
        'Total Orders': '{:,.0f}',
        'Recency (Days)': '{:,.0f}'
    }),
    use_container_width=True,
    height=380
)

# Download CSV Export Button
csv_data = display_table.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Churn Risk Analysis Report (CSV)",
    data=csv_data,
    file_name=f"churn_risk_report_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# Footer
st.markdown("""
    <div style="text-align: center; color: #64748b; margin-top: 3rem; font-size: 0.85rem;">
        E-Commerce Customer Insights & Churn Analytics Dashboard • Developed by Pyda Venkata Dhanusha Kumari • Powered by Streamlit, SQLite & Scikit-Learn
    </div>
""", unsafe_allow_html=True)
