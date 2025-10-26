import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="TB Burden Dashboard", layout="wide")
st.title("🌍 Tuberculosis (TB) Burden Dashboard")
st.markdown("""
This interactive dashboard visualizes **estimated TB prevalence** across countries and years.
You can explore trends, uncertainty intervals, and compare prevalence between nations.
""")

# -------------------- LOAD DATA --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("TB_Burden_Country.csv")
    # Standardize column names for safety
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
    return df

df = load_data()

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("🔎 Filters")

# Country filter
if "country" in df.columns:
    countries = st.sidebar.multiselect(
        "Select countries to visualize:",
        options=sorted(df["country"].unique()),
        default=["India"] if "India" in df["country"].unique() else sorted(df["country"].unique())[:3]
    )
else:
    st.error("The dataset does not contain a 'country' column.")
    st.stop()

# Year filter
if "year" in df.columns:
    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    years = st.sidebar.slider("Select year range:", min_year, max_year, (min_year, max_year))
    df = df[df["year"].between(*years)]
else:
    st.error("The dataset does not contain a 'year' column.")
    st.stop()

# Filtered data
filtered_df = df[df["country"].isin(countries)]

st.markdown("### 📄 Filtered Data Preview")
st.dataframe(filtered_df.head())

# -------------------- LINE PLOT: TB PREVALENCE --------------------
st.markdown("## 📈 Estimated TB Prevalence Over Time")

if "estimated_prevalence_of_tb" in df.columns:
    fig, ax = plt.subplots(figsize=(10, 5))
    for country in filtered_df["country"].unique():
        subset = filtered_df[filtered_df["country"] == country]
        ax.plot(subset["year"], subset["estimated_prevalence_of_tb"], marker="o", label=country)

    ax.set_xlabel("Year")
    ax.set_ylabel("Estimated Prevalence of TB")
    ax.set_title("Estimated TB Prevalence Over Time")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
else:
    st.warning("No column named 'estimated_prevalence_of_TB' found in the dataset.")

# -------------------- ERROR BAR PLOT --------------------
st.markdown("## 📉 Prevalence with Uncertainty Bounds")

lower_col = "estimated_prevalence_of_tblower_bound"
upper_col = "estimated_prevalence_of_tbupper_bound"

if lower_col in df.columns and upper_col in df.columns:
    fig, ax = plt.subplots(figsize=(10, 5))

    for country in filtered_df["country"].unique():
        subset = filtered_df[filtered_df["country"] == country]
        y = subset["estimated_prevalence_of_tb"]
        y_lower = subset[lower_col]
        y_upper = subset[upper_col]
        yerr = [y - y_lower, y_upper - y]

        ax.errorbar(subset["year"], y, yerr=yerr, fmt='-o', capsize=4, label=country)

    ax.set_xlabel("Year")
    ax.set_ylabel("Estimated Prevalence of TB")
    ax.set_title("Estimated TB Prevalence with Uncertainty Intervals")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
else:
    st.info("Uncertainty bounds not available — skipping error bar plot.")

# -------------------- SUMMARY STATISTICS --------------------
st.markdown("## 📊 Summary Statistics")

if "estimated_prevalence_of_tb" in df.columns:
    summary = (
        filtered_df.groupby("country")["estimated_prevalence_of_tb"]
        .agg(["mean", "max", "min"])
        .round(2)
        .sort_values(by="mean", ascending=False)
    )
    st.dataframe(summary)
else:
    st.warning("Summary statistics unavailable — 'estimated_prevalence_of_TB' not found.")

# -------------------- FOOTER --------------------
st.markdown("""
---
**Dashboard created using Streamlit and Matplotlib**  
Built by Akshay Chandra 🧠 — exploring global health data through open science.
""")
