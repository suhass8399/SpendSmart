
import streamlit as st
import numpy as np
import pandas as pd

import os

FILE_NAME = "expenses.csv"


def load_expenses():
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_csv(FILE_NAME)

            if "amount" not in df.columns:
                return []

            return df.to_dict("records")

        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            return []

    return []





def save_expenses(expenses):
    columns = ["amount", "category", "description", "date"]
    df = pd.DataFrame(expenses, columns=columns)
    df.to_csv(FILE_NAME, index=False)


BUDGET_FILE = "budget_history.csv"



BUDGET_FILE = "budget_history.csv"


def save_budget_history(budget):
    today = str(pd.Timestamp.today().date())

    if os.path.exists(BUDGET_FILE):
        history = pd.read_csv(BUDGET_FILE)
    else:
        history = pd.DataFrame(columns=["date", "budget"])

    if history.empty or float(history["budget"].iloc[-1]) != budget:
        new_entry = pd.DataFrame([{
            "date": today,
            "budget": budget
        }])

        history = pd.concat(
            [history, new_entry],
            ignore_index=True
        )

        history.to_csv(BUDGET_FILE, index=False)


st.set_page_config(
    page_title="SpendSmart",
    page_icon="💰",
    layout="wide"
)

st.title("💰 SpendSmart")
st.subheader("Your Personal Expense Analyzer")
st.write("Track your expenses and understand where your money goes.")

# Initialize transaction storage
if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

# Budget
st.sidebar.header("Monthly Budget")
budget = st.sidebar.number_input(
    "Set your budget (₹)",
    min_value=0.0,
    value=5000.0,
    step=500.0
)
save_budget_history(budget)

if os.path.exists(BUDGET_FILE):
    st.sidebar.subheader("📜 Budget History")
    budget_history = pd.read_csv(BUDGET_FILE)
    budget_history = budget_history.iloc[::-1].reset_index(drop=True)

    st.sidebar.dataframe(
        budget_history,
        use_container_width=True
    )

# Expense entry form
st.header("➕ Add a New Expense")

with st.form("expense_form", clear_on_submit=True):
    amount = st.number_input(
        "Expense amount (₹)",
        min_value=0.01,
        value=100.0,
        step=10.0
    )
    description = st.text_input(
        "Description",
        placeholder="Example: Lunch"
    )



    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Shopping",
         "Entertainment", "Education", "Other"]
    )

    expense_date = st.date_input(
    "Expense date",
    value=pd.Timestamp.today().date()
)

    submitted = st.form_submit_button("Add Expense")

if submitted:
    st.session_state.expenses.append({
        "amount": amount,
        "category": category,
        "description": description.strip() or "No description",
        "date": str(expense_date)
    })

    save_expenses(st.session_state.expenses)
    st.success("Expense added successfully!")

# Analyze transactions

# Analyze transactions
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)

    # Add dates for older transactions
    if "date" not in df.columns:
        df["date"] = str(pd.Timestamp.today().date())

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date"] = df["date"].fillna(pd.Timestamp.today().normalize())

    # Monthly filter
    st.header("📅 Filter Expenses by Month")

    selected_month = st.selectbox(
        "Choose month",
        sorted(df["date"].dt.strftime("%Y-%m").unique(), reverse=True)
    )

    filtered_df = df[
        df["date"].dt.strftime("%Y-%m") == selected_month
    ]

    # Analyze selected month's expenses
    df = filtered_df
    amounts = df["amount"].to_numpy()
    
    sorted_expenses = np.sort(amounts)

    st.subheader("Expenses from Lowest to Highest")
    st.write(sorted_expenses)

    max_expense = np.max(amounts)
    max_index = np.argmax(amounts)
    st.write("Most expensive transaction:", amounts[max_index])
    min_expense = np.min(amounts)

    total = np.sum(amounts)
    average = np.mean(amounts)
    remaining = budget - total
    
    if budget > 0:

        budget_used = (total / budget) * 100
    else:

        budget_used = 0

    st.divider()
    st.header("📊 Expense Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"₹{total:.2f}")
    col2.metric("Average Expense", f"₹{average:.2f}")
    col3.metric("Budget Remaining", f"₹{remaining:.2f}")
    st.metric("Budget Used", f"{budget_used:.1f}%")
    st.progress(min(budget_used / 100, 1.0))

    col4, col5 = st.columns(2)

    col4.metric("Highest Expense", f"₹{max_expense:.2f}")
    col5.metric("Lowest Expense", f"₹{min_expense:.2f}")

    if remaining < 0:
        st.warning("You have exceeded your budget!")
    else:
        st.success("You are within your budget.")

    st.header("📁 Category-wise Spending")
    category_totals = df.groupby("category")["amount"].sum()
    st.bar_chart(category_totals)

    st.header("🧾 Transaction History")
    st.dataframe(df, use_container_width=True)

    if st.button("Clear All Transactions"):
        st.session_state.expenses = []
        st.rerun()

else:
    st.info("Add your first expense to see your dashboard!")
