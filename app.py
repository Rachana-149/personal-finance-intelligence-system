import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Personal Finance Intelligence System",
    layout="wide"
)

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv("sample_expense_dataset.csv")

df["Date"] = pd.to_datetime(df["Date"])

# ---------------- UI STYLE ---------------- #

st.markdown(
    """
    <style>

    .stApp {
        background-color: #F5F7FA;
    }

    section[data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #E5E7EB;
    }

    h1 {
        color: #111827 !important;
        font-size: 40px !important;
        font-weight: 700 !important;
    }

    h2, h3 {
        color: #111827 !important;
        font-weight: 600 !important;
    }

    p, label {
        color: #374151 !important;
    }

    .stDownloadButton > button {
        background-color: #059669;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        width: 100%;
        height: 45px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- TITLE ---------------- #

st.title("💰 Personal Finance Intelligence System")

st.subheader(
    "Smart Expense Analytics & Budget Monitoring Dashboard"
)

# ---------------- SIDEBAR FILTERS ---------------- #

st.sidebar.header("Dashboard Filters")

uploaded_file = st.sidebar.file_uploader(
    "Upload Your CSV File (Optional)",
    type=["csv"]
)

# CUSTOM CSV

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    df["Date"] = pd.to_datetime(df["Date"])

# CATEGORY FILTER

selected_category = st.sidebar.multiselect(
    "Select Category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

# DATE FILTER

start_date = st.sidebar.date_input(
    "Start Date",
    df["Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    df["Date"].max()
)

# APPLY FILTERS

filtered_df = df[
    (df["Category"].isin(selected_category)) &
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date))
]

# ---------------- KPI SECTION ---------------- #

total_expense = filtered_df["Amount"].sum()

average_expense = filtered_df["Amount"].mean()

highest_category = (
    filtered_df.groupby("Category")["Amount"]
    .sum()
    .idxmax()
)

total_transactions = len(filtered_df)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Expenses",
        f"₹{total_expense:.2f}"
    )

with col2:

    st.metric(
        "Average Expense",
        f"₹{average_expense:.2f}"
    )

with col3:

    st.metric(
        "Highest Category",
        highest_category
    )

with col4:

    st.metric(
        "Transactions",
        total_transactions
    )

# ---------------- DATA TABLE ---------------- #

st.markdown("## Expense Records")

st.dataframe(
    filtered_df,
    width="stretch"
)

# ---------------- DOWNLOAD BUTTON ---------------- #

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Report",
    data=csv,
    file_name="expense_report.csv",
    mime="text/csv"
)

# ---------------- CHARTS ---------------- #

chart_col1, chart_col2 = st.columns(2)

# PIE CHART

with chart_col1:

    st.markdown("## Expense Distribution")

    pie_chart = px.pie(
        filtered_df,
        names="Category",
        values="Amount",
        hole=0.4,
        template="plotly_white"
    )

    st.plotly_chart(
        pie_chart,
        width="stretch",
        key="pie_chart"
    )

# TREND CHART

with chart_col2:

    st.markdown("## Expense Trend")

    trend_option = st.selectbox(
        "Trend View",
        ["Daily", "Weekly", "Monthly", "Yearly"]
    )

    if trend_option == "Daily":

        trend_data = (
            filtered_df.groupby(
                filtered_df["Date"].dt.date
            )["Amount"]
            .sum()
            .reset_index()
        )

        x_value = "Date"

    elif trend_option == "Weekly":

        trend_data = (
            filtered_df.groupby(
                filtered_df["Date"].dt.to_period("W")
            )["Amount"]
            .sum()
            .reset_index()
        )

        trend_data["Date"] = trend_data["Date"].astype(str)

        x_value = "Date"

    elif trend_option == "Monthly":

        trend_data = (
            filtered_df.groupby(
                filtered_df["Date"].dt.to_period("M")
            )["Amount"]
            .sum()
            .reset_index()
        )

        trend_data["Date"] = trend_data["Date"].astype(str)

        x_value = "Date"

    else:

        trend_data = (
            filtered_df.groupby(
                filtered_df["Date"].dt.to_period("Y")
            )["Amount"]
            .sum()
            .reset_index()
        )

        trend_data["Date"] = trend_data["Date"].astype(str)

        x_value = "Date"

    trend_chart = px.line(
        trend_data,
        x=x_value,
        y="Amount",
        markers=True,
        template="plotly_white"
    )

    st.plotly_chart(
        trend_chart,
        width="stretch",
        key="trend_chart"
    )

# ---------------- BOTTOM SECTION ---------------- #

bottom1, bottom2 = st.columns(2)

# ---------------- BUDGET ---------------- #

with bottom1:

    st.markdown("## Budget Monitoring")

    if "budget" not in st.session_state:
        st.session_state["budget"] = 5000.0

    budget = st.number_input(
        "Set Monthly Budget",
        min_value=0.0,
        value=st.session_state["budget"],
        format="%.2f"
    )

    st.session_state["budget"] = budget

    remaining_budget = budget - total_expense

    if total_expense > budget:

        st.error(
            f"Budget Exceeded by ₹{abs(remaining_budget):.2f}"
        )

    else:

        st.success(
            f"Remaining Budget: ₹{remaining_budget:.2f}"
        )

# ---------------- FORECAST + INSIGHTS ---------------- #

with bottom2:

    st.markdown("## Expense Forecast")

    if len(filtered_df) >= 5:

        forecast_value = (
            filtered_df["Amount"]
            .rolling(window=5)
            .mean()
            .iloc[-1]
        )

        st.info(
            f"Predicted Next Expense: ₹{forecast_value:.2f}"
        )

    else:

        st.warning(
            "Minimum 5 records required for forecasting."
        )

    # HIGHEST EXPENSE

    st.markdown("## Highest Expense")

    highest_expense = filtered_df.loc[
        filtered_df["Amount"].idxmax()
    ]

    st.success(
        f"""
        Highest Expense:
        ₹{highest_expense['Amount']:.2f}

        Category:
        {highest_expense['Category']}
        """
    )

# ---------------- SMART INSIGHTS ---------------- #

st.markdown("## Smart Insight")

category_totals = (
    filtered_df.groupby("Category")["Amount"]
    .sum()
)

top_category = category_totals.idxmax()

top_amount = category_totals.max()

st.info(
    f"""
    Highest spending category:
    {top_category}

    Total spent:
    ₹{top_amount:.2f}
    """
)

if total_expense < 10000:

    st.success(
        "Your spending pattern is currently balanced."
    )

elif total_expense < 30000:

    st.warning(
        "Your monthly expenses are moderately high."
    )

else:

    st.error(
        "Your expenses are increasing rapidly."
    )

# ---------------- FOOTER ---------------- #

st.markdown("---")

st.caption(
    "Personal Finance Intelligence System | Streamlit Analytics Dashboard"
)