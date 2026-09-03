import streamlit as st
import pandas as pd
import os

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="FinTrace AI",
    page_icon="💰",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "dataset",
    "anomaly_results.csv"
)

df = pd.read_csv(DATA_PATH)

df["period"] = pd.to_datetime(df["period"])

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("💰 FinTrace AI")
st.subheader("AI-Powered Financial Risk & Cash-Flow Intelligence")

st.markdown(
    "Monitor financial anomalies, spending trends, forecasts, "
    "and risk signals from a single dashboard."
)

st.divider()

# --------------------------------------------------
# KEY METRICS
# --------------------------------------------------

latest_period = df["period"].max()

latest_data = df[df["period"] == latest_period]

latest_spending = latest_data["total_amount"].sum()

anomaly_count = int(df["is_anomaly"].sum())

anomaly_rate = (anomaly_count / len(df)) * 100
# --------------------------------------------------
# DYNAMIC FORECAST & RISK
# --------------------------------------------------

monthly_forecast_df = (
    df.groupby("period", as_index=False)
    .agg(total_spending=("total_amount", "sum"))
    .sort_values("period")
)

monthly_forecast_df["spending_change"] = (
    monthly_forecast_df["total_spending"].diff()
)

last_spending = monthly_forecast_df["total_spending"].iloc[-1]

avg_recent_change = (
    monthly_forecast_df["spending_change"]
    .tail(3)
    .mean()
)

forecast_next_month = last_spending + avg_recent_change

forecast_change = (
    (forecast_next_month - last_spending)
    / last_spending
) * 100

if forecast_change <= -10:
    risk_level = "HIGH"
elif forecast_change <= -5:
    risk_level = "MEDIUM"
else:
    risk_level = "LOW"

# --------------------------------------------------
# METRIC CARDS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Latest Monthly Spending",
        f"₹{latest_spending:,.0f}"
    )

with col2:
    st.metric(
        "Next-Month Forecast",
        f"₹{forecast_next_month:,.0f}",
        f"{forecast_change:.2f}%"
    )

with col3:
    st.metric(
        "Anomalies Detected",
        anomaly_count
    )

with col4:
    st.metric(
        "Cash-Flow Risk",
        risk_level
    )

st.divider()

# --------------------------------------------------
# PRIORITY RISK METRICS
# --------------------------------------------------

priority_anomalies = df[
    (df["is_anomaly"] == 1) &
    (df["anomaly_score"] >= 3)
]

priority_count = len(priority_anomalies)

if priority_count > 0:
    top_priority = (
        priority_anomalies
        .groupby(["department", "category"], as_index=False)
        .agg(
            anomaly_count=("is_anomaly", "count"),
            avg_score=("anomaly_score", "mean")
        )
        .sort_values(
            ["avg_score", "anomaly_count"],
            ascending=False
        )
        .iloc[0]
    )

    top_risk_area = (
        f"{top_priority['department']} — "
        f"{top_priority['category']}"
    )
else:
    top_risk_area = "None"

col5, col6 = st.columns(2)

with col5:
    st.metric(
        "High-Priority Anomalies",
        priority_count
    )

with col6:
    st.metric(
        "Top Risk Area",
        top_risk_area
    )
    
st.subheader("📊 Monthly Spending Trend")

monthly_spending = (
    df.groupby("period", as_index=False)
    .agg(total_spending=("total_amount", "sum"))
    .sort_values("period")
)

monthly_spending = monthly_spending.set_index("period")

st.line_chart(
    monthly_spending["total_spending"]
)

# --------------------------------------------------
# ANOMALY DISTRIBUTION
# --------------------------------------------------

st.subheader("🚨 Anomaly Overview")

col1, col2 = st.columns(2)

with col1:

    anomaly_summary = pd.DataFrame({
        "Status": ["Normal", "Anomaly"],
        "Count": [
            int((df["is_anomaly"] == 0).sum()),
            int((df["is_anomaly"] == 1).sum())
        ]
    })

    st.bar_chart(
        anomaly_summary.set_index("Status")
    )

with col2:

    st.metric(
        "Anomaly Rate",
        f"{anomaly_rate:.2f}%"
    )

    st.write(
        "FinTrace AI identifies unusual financial patterns "
        "using spending deviation, budget variance, transaction "
        "behavior and anomaly scoring."
    )

# --------------------------------------------------
# TOP ANOMALIES
# --------------------------------------------------

st.subheader("🔍 Detected Financial Anomalies")

anomalies = df[df["is_anomaly"] == 1].copy()

display_columns = [
    "period",
    "department",
    "category",
    "total_amount",
    "anomaly_score",
    "spending_deviation_pct",
    "budget_utilization_pct"
]

available_columns = [
    col for col in display_columns
    if col in anomalies.columns
]

anomalies_display = anomalies[
    available_columns
].sort_values(
    by="anomaly_score",
    ascending=False
)

st.dataframe(
    anomalies_display.head(20),
    use_container_width=True
)

# --------------------------------------------------
# RISK & RECOMMENDATION
# --------------------------------------------------

st.divider()

st.subheader("🤖 FinTrace AI Cash-Flow Risk Assessment")

if risk_level == "HIGH":
    risk_message = "⚠️ High financial risk detected."
elif risk_level == "MEDIUM":
    risk_message = "🟡 Moderate financial risk detected."
else:
    risk_message = "🟢 Financial position appears relatively stable."

st.info(risk_message)

st.markdown(
    """
**Recommendation**

Spending is relatively stable. Continue monitoring anomalies
and budget utilization while reviewing high-risk financial
categories identified by the system.
"""
)

# --------------------------------------------------
# FILTER
# --------------------------------------------------

st.divider()

st.subheader("🔎 Explore Financial Data")

department_options = ["All"] + sorted(
    df["department"].dropna().unique().tolist()
)

selected_department = st.selectbox(
    "Department",
    department_options
)

filtered_df = df.copy()

if selected_department != "All":
    filtered_df = filtered_df[
        filtered_df["department"] == selected_department
    ]

st.dataframe(
    filtered_df,
    use_container_width=True
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "FinTrace AI — Financial Risk & Cash-Flow Intelligence System"
)