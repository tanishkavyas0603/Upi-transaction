"""
app.py — UPI Transaction Intelligence Dashboard
------------------------------------------------
A Streamlit dashboard for exploring UPI transaction data.
All metrics and charts are driven by filtered data — nothing is hardcoded.

Run with:
    streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import warnings
warnings.filterwarnings("ignore")

# ------------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------------
st.set_page_config(
    page_title="UPI Transaction Intelligence Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# CUSTOM CSS — clean, professional look
# ------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #F8FAFC; }

    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 4px solid #2E86AB;
        margin-bottom: 8px;
    }
    .kpi-label { font-size: 13px; color: #6B7280; font-weight: 500; margin-bottom: 4px; }
    .kpi-value { font-size: 26px; font-weight: 700; color: #111827; }
    .kpi-delta { font-size: 12px; color: #6B7280; }

    .section-header {
        font-size: 18px;
        font-weight: 700;
        color: #1F2937;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #E5E7EB;
    }

    .insight-box {
        background: #EFF6FF;
        border-left: 4px solid #2563EB;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        font-size: 14px;
        color: #1E40AF;
    }

    div[data-testid="stSidebar"] { background-color: #1E293B; }
    div[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# DATA LOADING — cached for performance
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    """Load the cleaned CSV dataset. Cached so it's only read once."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "data", "processed", "upi_transactions_clean.csv")
    df = pd.read_csv(path)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    return df


df_full = load_data()


# ------------------------------------------------------------------
# SIDEBAR — FILTERS
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")

    # Date range
    min_date = df_full["transaction_date"].min().date()
    max_date = df_full["transaction_date"].max().date()
    date_range = st.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.markdown("---")

    # Multi-select filters
    cities_all    = sorted(df_full["city"].unique())
    states_all    = sorted(df_full["state"].unique())
    txn_types     = sorted(df_full["transaction_type"].unique())
    pay_methods   = sorted(df_full["payment_method"].unique())
    categories    = sorted(df_full["merchant_category"].unique())
    statuses      = sorted(df_full["transaction_status"].unique())

    sel_cities  = st.multiselect("🌆 City",               cities_all,  default=[])
    sel_states  = st.multiselect("🗺️ State",              states_all,  default=[])
    sel_types   = st.multiselect("🔄 Transaction Type",   txn_types,   default=[])
    sel_methods = st.multiselect("📱 Payment Method",     pay_methods, default=[])
    sel_cats    = st.multiselect("🛒 Merchant Category",  categories,  default=[])
    sel_status  = st.multiselect("✅ Transaction Status", statuses,    default=[])

    st.markdown("---")
    st.markdown("*Data: Synthetic UPI dataset*")
    st.markdown("*Records: ~75,000*")


# ------------------------------------------------------------------
# APPLY FILTERS
# ------------------------------------------------------------------
df = df_full.copy()

if len(date_range) == 2:
    start_d, end_d = date_range
    df = df[(df["transaction_date"].dt.date >= start_d) &
            (df["transaction_date"].dt.date <= end_d)]

if sel_cities:  df = df[df["city"].isin(sel_cities)]
if sel_states:  df = df[df["state"].isin(sel_states)]
if sel_types:   df = df[df["transaction_type"].isin(sel_types)]
if sel_methods: df = df[df["payment_method"].isin(sel_methods)]
if sel_cats:    df = df[df["merchant_category"].isin(sel_cats)]
if sel_status:  df = df[df["transaction_status"].isin(sel_status)]


# ------------------------------------------------------------------
# GUARD: empty data
# ------------------------------------------------------------------
if df.empty:
    st.warning("No records match the selected filters. Please adjust your filters.")
    st.stop()


# ------------------------------------------------------------------
# CALCULATED METRICS (always from filtered data)
# ------------------------------------------------------------------
total_txns    = len(df)
success_df    = df[df["transaction_status"] == "Success"]
failed_df     = df[df["transaction_status"] == "Failed"]

total_value   = success_df["transaction_amount"].sum()
avg_value     = success_df["transaction_amount"].mean() if len(success_df) > 0 else 0
success_rate  = (len(success_df) / total_txns * 100) if total_txns > 0 else 0
failure_rate  = (len(failed_df)  / total_txns * 100) if total_txns > 0 else 0
unique_custs  = df["customer_id"].nunique()
unique_merch  = df["merchant_name"].nunique()


# ------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------
st.markdown("""
<div style="background: linear-gradient(135deg, #1E293B 0%, #2E86AB 100%);
            padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
    <h1 style="color:white; margin:0; font-size:28px;">💳 UPI Transaction Intelligence Dashboard</h1>
    <p style="color:#CBD5E1; margin:6px 0 0 0; font-size:14px;">
        Analysing UPI payment patterns | Synthetic Dataset for Portfolio Demonstration
    </p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------
# TOP KPI CARDS
# ------------------------------------------------------------------
st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

def kpi_card(col, label, value, delta=None):
    with col:
        delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

kpi_card(c1, "Total Transactions",    f"{total_txns:,}")
kpi_card(c2, "Total Value (Success)", f"₹{total_value/1e7:.2f} Cr")
kpi_card(c3, "Avg Transaction Value", f"₹{avg_value:,.0f}")
kpi_card(c4, "Success Rate",          f"{success_rate:.1f}%")
kpi_card(c5, "Unique Customers",      f"{unique_custs:,}")

st.markdown("<br>", unsafe_allow_html=True)


# ==================================================================
# SECTION 1: OVERVIEW
# ==================================================================
st.markdown('<div class="section-header">📈 Section 1 — Transaction Overview</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# --- Daily Volume Trend ---
with col1:
    daily = df[df["transaction_status"] == "Success"].groupby("transaction_date").size().reset_index(name="txn_count")
    daily["7d_avg"] = daily["txn_count"].rolling(7, center=True, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["transaction_date"], y=daily["txn_count"],
                             mode="lines", name="Daily Count",
                             line=dict(color="#CBD5E1", width=1), opacity=0.7))
    fig.add_trace(go.Scatter(x=daily["transaction_date"], y=daily["7d_avg"],
                             mode="lines", name="7-Day Avg",
                             line=dict(color="#2E86AB", width=2.5)))
    fig.update_layout(title="Daily Transaction Volume (Successful)",
                      xaxis_title="Date", yaxis_title="Count",
                      legend=dict(x=0, y=1), height=360, margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- Status Distribution ---
with col2:
    status_counts = df.groupby("transaction_status").size().reset_index(name="count")
    color_map = {"Success": "#27AE60", "Failed": "#E74C3C", "Pending": "#F39C12"}
    fig = px.pie(status_counts, names="transaction_status", values="count",
                 title="Transaction Status Distribution",
                 color="transaction_status", color_discrete_map=color_map,
                 hole=0.45)
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(height=360, margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- Category Performance ---
col3, col4 = st.columns(2)
with col3:
    cat_vol = df.groupby("merchant_category").size().reset_index(name="count").sort_values("count", ascending=False)
    fig = px.bar(cat_vol, y="merchant_category", x="count", orientation="h",
                 title="Transaction Volume by Category",
                 color="count", color_continuous_scale="Blues")
    fig.update_layout(height=380, yaxis_title="", xaxis_title="Count",
                      margin=dict(l=0,r=0,t=40,b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    cat_val = success_df.groupby("merchant_category")["transaction_amount"].sum().reset_index()
    cat_val.columns = ["category", "total_value"]
    cat_val = cat_val.sort_values("total_value", ascending=False)
    fig = px.bar(cat_val, y="category", x="total_value", orientation="h",
                 title="Transaction Value by Category (₹)",
                 color="total_value", color_continuous_scale="Greens")
    fig.update_layout(height=380, yaxis_title="", xaxis_title="Total Value (₹)",
                      margin=dict(l=0,r=0,t=40,b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ==================================================================
# SECTION 2: CUSTOMER & TRANSACTION ANALYSIS
# ==================================================================
st.markdown('<div class="section-header">👤 Section 2 — Customer & Transaction Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

# --- Transaction Amount Distribution ---
with col1:
    fig = px.histogram(success_df, x="transaction_amount", nbins=60,
                       title="Transaction Amount Distribution (₹)",
                       color_discrete_sequence=["#2E86AB"])
    fig.update_layout(xaxis_title="Amount (₹)", yaxis_title="Count",
                      height=360, margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- Amount Bucket Distribution ---
with col2:
    bucket_order = ["Low", "Medium", "High", "Very High"]
    bucket_df = df.groupby("amount_bucket").size().reset_index(name="count")
    bucket_df["amount_bucket"] = pd.Categorical(bucket_df["amount_bucket"], categories=bucket_order, ordered=True)
    bucket_df = bucket_df.sort_values("amount_bucket")
    fig = px.bar(bucket_df, x="amount_bucket", y="count",
                 title="Transactions by Amount Bucket",
                 color="amount_bucket",
                 color_discrete_sequence=["#93C5FD", "#3B82F6", "#1D4ED8", "#1E3A8A"])
    fig.update_layout(showlegend=False, height=360,
                      xaxis_title="Amount Bucket", yaxis_title="Count",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- Top Customers Table ---
col3, col4 = st.columns(2)
with col3:
    top_custs = (success_df.groupby("customer_id")
                 .agg(txn_count=("transaction_id", "count"),
                      total_value=("transaction_amount", "sum"))
                 .reset_index()
                 .sort_values("total_value", ascending=False)
                 .head(10))
    top_custs["total_value"] = top_custs["total_value"].apply(lambda x: f"₹{x:,.0f}")
    st.markdown("**🏆 Top 10 Customers by Transaction Value**")
    st.dataframe(top_custs.reset_index(drop=True), use_container_width=True, height=320)

# --- Age Group Analysis ---
with col4:
    def age_group(age):
        if age < 25:   return "18-24"
        elif age < 35: return "25-34"
        elif age < 45: return "35-44"
        elif age < 55: return "45-54"
        else:          return "55+"

    ag_df = success_df.copy()
    ag_df["age_group"] = ag_df["customer_age"].apply(age_group)
    ag_summary = ag_df.groupby("age_group")["transaction_amount"].mean().reset_index()
    ag_summary.columns = ["age_group", "avg_amount"]
    fig = px.bar(ag_summary, x="age_group", y="avg_amount",
                 title="Avg Transaction Amount by Age Group",
                 color="avg_amount", color_continuous_scale="Oranges")
    fig.update_layout(showlegend=False, height=320,
                      xaxis_title="Age Group", yaxis_title="Avg Amount (₹)",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)


# ==================================================================
# SECTION 3: GEOGRAPHIC ANALYSIS
# ==================================================================
st.markdown('<div class="section-header">🗺️ Section 3 — Geographic Analysis</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

city_stats = (df.groupby("city")
              .agg(txn_count=("transaction_id", "count"),
                   total_value=("transaction_amount", "sum"),
                   success_rate=("transaction_success_flag", "mean"))
              .reset_index())
city_stats["success_rate_pct"] = (city_stats["success_rate"] * 100).round(2)
city_stats = city_stats.sort_values("total_value", ascending=False)

with col1:
    top15_vol = city_stats.head(15).sort_values("txn_count")
    fig = px.bar(top15_vol, y="city", x="txn_count", orientation="h",
                 title="Top 15 Cities — Transaction Volume",
                 color="txn_count", color_continuous_scale="Blues")
    fig.update_layout(showlegend=False, height=480,
                      yaxis_title="", xaxis_title="Count",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    top15_val = city_stats.head(15).sort_values("total_value")
    top15_val["value_mn"] = top15_val["total_value"] / 1e6
    fig = px.bar(top15_val, y="city", x="value_mn", orientation="h",
                 title="Top 15 Cities — Transaction Value (₹M)",
                 color="value_mn", color_continuous_scale="Greens")
    fig.update_layout(showlegend=False, height=480,
                      yaxis_title="", xaxis_title="Value (₹M)",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col3:
    city_sr = city_stats.sort_values("success_rate_pct", ascending=False).head(15)
    city_sr_sorted = city_sr.sort_values("success_rate_pct")
    fig = px.bar(city_sr_sorted, y="city", x="success_rate_pct", orientation="h",
                 title="Top 15 Cities — Success Rate (%)",
                 color="success_rate_pct", color_continuous_scale="RdYlGn",
                 range_color=[80, 95])
    fig.update_layout(showlegend=False, height=480,
                      yaxis_title="", xaxis_title="Success Rate (%)",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)


# ==================================================================
# SECTION 4: PAYMENT ANALYSIS
# ==================================================================
st.markdown('<div class="section-header">📱 Section 4 — Payment Method Analysis</div>', unsafe_allow_html=True)

pm_stats = (df.groupby("payment_method")
            .agg(txn_count=("transaction_id", "count"),
                 total_value=("transaction_amount", "sum"),
                 success_rate=("transaction_success_flag", "mean"))
            .reset_index())
pm_stats["success_rate_pct"] = (pm_stats["success_rate"] * 100).round(2)
pm_stats = pm_stats.sort_values("txn_count", ascending=False)

col1, col2, col3 = st.columns(3)

with col1:
    fig = px.pie(pm_stats, names="payment_method", values="txn_count",
                 title="Payment Method — Usage Share", hole=0.4)
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(height=360, margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    pm_val = pm_stats.copy()
    pm_val["value_mn"] = pm_val["total_value"] / 1e6
    fig = px.bar(pm_val, x="payment_method", y="value_mn",
                 title="Payment Method — Transaction Value (₹M)",
                 color="value_mn", color_continuous_scale="Blues")
    fig.update_layout(showlegend=False, height=360,
                      xaxis_title="", yaxis_title="Value (₹M)",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col3:
    fig = px.bar(pm_stats.sort_values("success_rate_pct"),
                 x="payment_method", y="success_rate_pct",
                 title="Payment Method — Success Rate (%)",
                 color="success_rate_pct", color_continuous_scale="RdYlGn",
                 range_color=[80, 95])
    fig.update_layout(showlegend=False, height=360,
                      xaxis_title="", yaxis_title="Success Rate (%)",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)


# ==================================================================
# SECTION 5: FAILURE ANALYSIS
# ==================================================================
st.markdown('<div class="section-header">⚠️ Section 5 — Failure Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    fail_reasons = (failed_df[failed_df["failure_reason"] != "N/A"]
                    .groupby("failure_reason").size()
                    .reset_index(name="count")
                    .sort_values("count", ascending=True))
    fig = px.bar(fail_reasons, y="failure_reason", x="count", orientation="h",
                 title="Failure Reasons Distribution",
                 color="count", color_continuous_scale="Reds")
    fig.update_layout(showlegend=False, height=380,
                      yaxis_title="", xaxis_title="Count",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    cat_fail = (df.groupby("merchant_category")
                .agg(total=("transaction_id","count"),
                     failed=("transaction_status", lambda x: (x=="Failed").sum()))
                .reset_index())
    cat_fail["failure_rate"] = (cat_fail["failed"] / cat_fail["total"] * 100).round(2)
    cat_fail = cat_fail.sort_values("failure_rate", ascending=True)
    fig = px.bar(cat_fail, y="merchant_category", x="failure_rate", orientation="h",
                 title="Failure Rate by Category (%)",
                 color="failure_rate", color_continuous_scale="Oranges")
    fig.update_layout(showlegend=False, height=380,
                      yaxis_title="", xaxis_title="Failure Rate (%)",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

# --- Failure Trend Over Time ---
fail_trend = (failed_df.groupby("year_month")
              .size().reset_index(name="fail_count"))
fig = px.line(fail_trend, x="year_month", y="fail_count",
              title="Monthly Failed Transaction Trend",
              markers=True, color_discrete_sequence=["#E74C3C"])
fig.update_layout(xaxis_title="Month", yaxis_title="Failed Transactions",
                  height=320, margin=dict(l=0,r=0,t=40,b=0))
st.plotly_chart(fig, use_container_width=True)

# --- Time Pattern Charts ---
col3, col4 = st.columns(2)

with col3:
    hour_df = df.groupby("hour").size().reset_index(name="count")
    fig = px.bar(hour_df, x="hour", y="count",
                 title="Transactions by Hour of Day",
                 color="count", color_continuous_scale="Viridis")
    fig.update_layout(showlegend=False, height=320,
                      xaxis_title="Hour", yaxis_title="Count",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)

with col4:
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dow_df = df.groupby("day_name").size().reset_index(name="count")
    dow_df["day_name"] = pd.Categorical(dow_df["day_name"], categories=day_order, ordered=True)
    dow_df = dow_df.sort_values("day_name")
    fig = px.bar(dow_df, x="day_name", y="count",
                 title="Transactions by Day of Week",
                 color="count", color_continuous_scale="Purples")
    fig.update_layout(showlegend=False, height=320,
                      xaxis_title="", yaxis_title="Count",
                      margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig, use_container_width=True)


# ==================================================================
# SECTION 6: KEY INSIGHTS (Dynamic — no hardcoded values)
# ==================================================================
st.markdown('<div class="section-header">💡 Section 6 — Key Insights</div>', unsafe_allow_html=True)

def generate_insights(df, success_df, failed_df):
    insights = []

    if total_txns == 0:
        return ["Not enough data to generate insights."]

    # Insight 1: Top payment method by volume
    top_pm = df["payment_method"].value_counts().index[0]
    top_pm_pct = df["payment_method"].value_counts(normalize=True).iloc[0] * 100
    insights.append(
        f"📱 <b>{top_pm}</b> is the most used payment method, "
        f"accounting for <b>{top_pm_pct:.1f}%</b> of all transactions."
    )

    # Insight 2: Top category by transaction value
    if len(success_df) > 0:
        top_cat = success_df.groupby("merchant_category")["transaction_amount"].sum().idxmax()
        top_cat_val = success_df.groupby("merchant_category")["transaction_amount"].sum().max()
        insights.append(
            f"🛒 <b>{top_cat}</b> generated the highest successful transaction value "
            f"of <b>₹{top_cat_val/1e6:.1f}M</b>."
        )

    # Insight 3: Peak transaction hour
    peak_hour = df.groupby("hour").size().idxmax()
    insights.append(
        f"⏰ Peak transaction activity occurs at <b>{peak_hour}:00</b> — "
        f"consider prioritizing server capacity during this hour."
    )

    # Insight 4: Weekend vs weekday
    wknd_avg = df[df["is_weekend"] == 1]["transaction_amount"].mean()
    wkdy_avg = df[df["is_weekend"] == 0]["transaction_amount"].mean()
    if wknd_avg > wkdy_avg:
        diff_pct = (wknd_avg - wkdy_avg) / wkdy_avg * 100
        insights.append(
            f"📅 Weekend transactions have a <b>{diff_pct:.1f}% higher</b> average value "
            f"(₹{wknd_avg:.0f}) compared to weekdays (₹{wkdy_avg:.0f})."
        )
    else:
        diff_pct = (wkdy_avg - wknd_avg) / wknd_avg * 100
        insights.append(
            f"📅 Weekday transactions have a <b>{diff_pct:.1f}% higher</b> average value "
            f"(₹{wkdy_avg:.0f}) compared to weekends (₹{wknd_avg:.0f})."
        )

    # Insight 5: Top failure reason
    if len(failed_df) > 0:
        top_fail = failed_df[failed_df["failure_reason"] != "N/A"]["failure_reason"].value_counts().index[0]
        top_fail_pct = failed_df[failed_df["failure_reason"] != "N/A"]["failure_reason"].value_counts(normalize=True).iloc[0] * 100
        insights.append(
            f"⚠️ <b>'{top_fail}'</b> is the leading failure reason, "
            f"responsible for <b>{top_fail_pct:.1f}%</b> of all failed transactions."
        )

    # Insight 6: Top city
    top_city = city_stats.iloc[0]["city"]
    top_city_val = city_stats.iloc[0]["total_value"]
    insights.append(
        f"🏙️ <b>{top_city}</b> leads in transaction value "
        f"with <b>₹{top_city_val/1e6:.1f}M</b> in total transactions."
    )

    # Insight 7: Overall success rate observation
    insights.append(
        f"✅ The overall transaction success rate is <b>{success_rate:.1f}%</b> "
        f"across <b>{total_txns:,}</b> transactions in the selected period."
    )

    return insights


insights = generate_insights(df, success_df, failed_df)
for insight in insights:
    st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#9CA3AF; font-size:12px; padding: 12px;">
    UPI Transaction Intelligence Dashboard · Portfolio Project · Synthetic Dataset
</div>
""", unsafe_allow_html=True)
