import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

def process_rfm_and_churn(df_summary, snapshot_date=None):
    """
    Cleans customer summary data, computes RFM metrics & scores,
    and trains a Random Forest Classifier model to output Churn Probabilities and Risk Categories.
    """
    if df_summary.empty:
        return df_summary

    df = df_summary.copy()

    # Convert date strings to datetime objects
    df['join_date'] = pd.to_datetime(df['join_date'])
    df['last_order_date'] = pd.to_datetime(df['last_order_date'])
    
    if snapshot_date is None:
        # Default snapshot date to current max order date or fixed cutoff
        if df['last_order_date'].dropna().empty:
            snapshot_date = pd.to_datetime('2026-07-25')
        else:
            snapshot_date = df['last_order_date'].max() + pd.Timedelta(days=1)
    else:
        snapshot_date = pd.to_datetime(snapshot_date)

    # 1. Feature Engineering & RFM Calculation
    # Recency: Days since last order (fill null with large number for 0 orders)
    df['recency_days'] = (snapshot_date - df['last_order_date']).dt.days.fillna(999)
    df['recency_days'] = df['recency_days'].apply(lambda x: max(0, x))

    # Frequency & Monetary
    df['frequency'] = df['total_orders'].fillna(0)
    df['monetary'] = df['total_spent'].fillna(0.0)
    df['avg_order_value'] = df['avg_order_value'].fillna(0.0)
    df['returned_orders'] = df['returned_orders'].fillna(0)
    df['tenure_days'] = (snapshot_date - df['join_date']).dt.days.fillna(30)
    df['tenure_days'] = df['tenure_days'].apply(lambda x: max(1, x))

    # RFM Scoring (1 to 4 scales)
    # Recency: lower recency_days gets higher score
    df['R_score'] = pd.qcut(df['recency_days'].rank(method='first', ascending=False), q=4, labels=[1, 2, 3, 4]).astype(int)
    # Frequency: higher order count gets higher score
    df['F_score'] = pd.qcut(df['frequency'].rank(method='first', ascending=True), q=4, labels=[1, 2, 3, 4]).astype(int)
    # Monetary: higher spent gets higher score
    df['M_score'] = pd.qcut(df['monetary'].rank(method='first', ascending=True), q=4, labels=[1, 2, 3, 4]).astype(int)

    # Customer Segment Categorization based on RFM
    def assign_segment(row):
        r, f, m = row['R_score'], row['F_score'], row['M_score']
        if r >= 3 and f >= 3 and m >= 3:
            return "Champions"
        elif f >= 3 and m >= 3:
            return "Loyal Customers"
        elif r >= 3 and f <= 2:
            return "Promising / New"
        elif r <= 2 and f >= 3:
            return "At-Risk VIPs"
        elif r <= 2 and f <= 2:
            return "Hibernating / Lost"
        else:
            return "Needs Attention"

    df['rfm_segment'] = df.apply(assign_segment, axis=1)

    # 2. Machine Learning Model: Random Forest Churn Predictor
    # Define Ground Truth Churn Target for training (Recency > 90 days or long inactive)
    df['is_churned_target'] = np.where((df['recency_days'] > 90) | ((df['recency_days'] > 60) & (df['frequency'] <= 2)), 1, 0)

    feature_cols = ['recency_days', 'frequency', 'monetary', 'avg_order_value', 'returned_orders', 'tenure_days']
    X = df[feature_cols]
    y = df['is_churned_target']

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Random Forest Classifier Model
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf_model.fit(X_scaled, y)

    # Predict Churn Probability (%)
    churn_probs = rf_model.predict_proba(X_scaled)[:, 1] * 100.0
    df['churn_risk_pct'] = np.round(churn_probs, 1)

    # Churn Risk Level Categorization
    def assign_risk_level(prob):
        if prob < 35.0:
            return "Low Risk"
        elif prob < 70.0:
            return "Moderate Risk"
        else:
            return "High Churn Risk"

    df['churn_risk_level'] = df['churn_risk_pct'].apply(assign_risk_level)

    # Feature Importance for analysis
    importances = dict(zip(feature_cols, rf_model.feature_importances_))

    return df, importances, rf_model

if __name__ == "__main__":
    from db_setup import init_db, get_customer_summary_sql
    init_db()
    raw_df = get_customer_summary_sql()
    df_processed, feat_imp, model = process_rfm_and_churn(raw_df)
    print("Processed RFM & Churn DataFrame Head:")
    print(df_processed[['customer_id', 'name', 'recency_days', 'frequency', 'monetary', 'rfm_segment', 'churn_risk_pct', 'churn_risk_level']].head(10))
    print("\nFeature Importances:", feat_imp)
