import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from database import (
    add_expense,
    fetch_expenses,
    delete_expense
)

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Personal Finance Intelligence System",
    layout="wide"
)

# ---------------- UI ---------------- #

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

    .stButton > button {
        background-color: #2563EB;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        width: 100%;
        height: 45px;
    }

    .stButton > button:hover {
        background-color: #1D4ED8;
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

    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
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

# ---------------- SIDEBAR ---------------- #

st.sidebar.header("Add Expense")

expense_date = st.sidebar.date_input(
    "Date",
    date.today()
)

category = st.sidebar.selectbox(
    "Category",
    [
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Entertainment",
        "Other"
    ]
)

amount = st.sidebar.number_input(
    "Amount",
    min_value=0.0,
    format="%.2f"
)

description = st.sidebar.text_input(
    "Description"
)

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

# ---------------- SAVE EXPENSE ---------------- #

if st.sidebar.button("Save Expense"):

    add_expense(
        str(expense_date),
        category,
        amount,
        description
    )

    st.sidebar.success(
        "Expense Added Successfully!"
    )

# ---------------- FETCH DATA ---------------- #

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

else:

    data = fetch_expenses()

    df = pd.DataFrame(
        data,
        columns=[
            "ID",
            "Date",
            "Category",
            "Amount",
            "Description"
        ]
    )

# ---------------- DATE CONVERSION ---------------- #

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])

# ---------------- FILTERS ---------------- #

st.sidebar.header("Filters")

selected_category = st.sidebar.multiselect(
    "Select Category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

if not df.empty:

    start_date = st.sidebar.date_input(
        "Start Date",
        df["Date"].min()
    )

    end_date = st.sidebar.date_input(
        "End Date",
        df["Date"].max()
    )

    df = df[
        (df["Category"].isin(selected_category)) &
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ]

# ---------------- KPI SECTION ---------------- #

if not df.empty:

    total_expense = df["Amount"].sum()

    average_expense = df["Amount"].mean()

    highest_category = (
        df.groupby("Category")["Amount"]
        .sum()
        .idxmax()
    )

    total_transactions = len(df)

else:

    total_expense = 0
    average_expense = 0
    highest_category = "N/A"
    total_transactions = 0

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown(
        f"""
        <div style='background:white;
                    padding:20px;
                    border-radius:16px;
                    border:1px solid #E5E7EB;'>

        <p style='font-size:14px;color:#6B7280;'>
        Total Expenses
        </p>

        <h2 style='color:#111827;'>
        ₹{total_expense:.2f}
        </h2>

        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div style='background:#F0FDF4;
                    padding:20px;
                    border-radius:16px;
                    border:1px solid #DCFCE7;'>

        <p style='font-size:14px;color:#6B7280;'>
        Average Expense
        </p>

        <h2 style='color:#111827;'>
        ₹{average_expense:.2f}
        </h2>

        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div style='background:#FEFCE8;
                    padding:20px;
                    border-radius:16px;
                    border:1px solid #FEF08A;'>

        <p style='font-size:14px;color:#6B7280;'>
        Highest Category
        </p>

        <h2 style='color:#111827;'>
        {highest_category}
        </h2>

        </div>
        """,
        unsafe_allow_html=True
    )

with col4:

    st.markdown(
        f"""
        <div style='background:#F5F3FF;
                    padding:20px;
                    border-radius:16px;
                    border:1px solid #DDD6FE;'>

        <p style='font-size:14px;color:#6B7280;'>
        Transactions
        </p>

        <h2 style='color:#111827;'>
        {total_transactions}
        </h2>

        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------- TABLE ---------------- #

st.markdown("## Expense Records")

st.dataframe(
    df,
    width="stretch"
)

# ---------------- DELETE + DOWNLOAD ---------------- #

col_del, col_download = st.columns(2)

with col_del:

    st.markdown("### Delete Expense")

    delete_id = st.number_input(
        "Enter Expense ID",
        min_value=1,
        step=1
    )

    if st.button("Delete Expense"):

        deleted_rows = delete_expense(delete_id)

        if deleted_rows > 0:

            st.success(
                f"Expense ID {delete_id} deleted successfully!"
            )

            st.rerun()

        else:

            st.error(
                f"Expense ID {delete_id} does not exist!"
            )

with col_download:

    st.markdown("### Download Report")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="expense_report.csv",
        mime="text/csv"
    )

# ---------------- CHARTS ---------------- #

chart_col1, chart_col2 = st.columns(2)

# PIE CHART

with chart_col1:

    st.markdown("## Expense Distribution")

    if not df.empty:

        pie_chart = px.pie(
            df,
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

    if not df.empty:

        trend_option = st.selectbox(
            "Trend View",
            ["Daily", "Weekly", "Monthly", "Yearly"]
        )

        if trend_option == "Daily":

            trend_data = (
                df.groupby(df["Date"].dt.date)["Amount"]
                .sum()
                .reset_index()
            )

            x_value = "Date"

        elif trend_option == "Weekly":

            trend_data = (
                df.groupby(df["Date"].dt.to_period("W"))["Amount"]
                .sum()
                .reset_index()
            )

            trend_data["Date"] = trend_data["Date"].astype(str)

            x_value = "Date"

        elif trend_option == "Monthly":

            trend_data = (
                df.groupby(df["Date"].dt.to_period("M"))["Amount"]
                .sum()
                .reset_index()
            )

            trend_data["Date"] = trend_data["Date"].astype(str)

            x_value = "Date"

        else:

            trend_data = (
                df.groupby(df["Date"].dt.to_period("Y"))["Amount"]
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

    # INITIALIZE SESSION STATE

    if "budget" not in st.session_state:
        st.session_state["budget"] = 0.0

    # INPUT BOX

    budget = st.number_input(
        "Set Monthly Budget",
        min_value=0.0,
        value=st.session_state["budget"],
        format="%.2f",
        key="budget_input"
    )

    # STORE VALUE

    st.session_state["budget"] = budget

    # LOGIC

    if budget > 0:

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

    # FORECAST

    st.markdown("## Expense Forecast")

    if not df.empty:

        if len(df) >= 5:

            forecast_value = (
                df["Amount"]
                .rolling(window=2)
                .mean()
                .iloc[-1]
            )

            st.info(
                f"Predicted Next Expense: ₹{forecast_value:.2f}"
            )

        else:

            st.warning(
                "Add at least 5 expense records for forecasting."
            )

    # HIGHEST EXPENSE

    st.markdown("## Highest Expense")

    if not df.empty:

        highest_expense = df.loc[
            df["Amount"].idxmax()
        ]

        st.success(
            f"""
            Highest expense:
            ₹{highest_expense['Amount']:.2f}

            Category:
            {highest_expense['Category']}
            """
        )

    # SMART INSIGHT

st.markdown("## Smart Insight")

if not df.empty:

    # CATEGORY ANALYSIS

    category_totals = (
        df.groupby("Category")["Amount"]
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

    # OVERALL SPENDING ANALYSIS

    if total_expense < 2000:

        st.success(
            "Your overall spending is under control."
        )

    elif total_expense < 5000:

        st.warning(
            "Your spending is moderate. Monitor expenses carefully."
        )

    else:

        st.error(
            "Your expenses are increasing rapidly."
        )