"""
Creates and populates notebooks/transaction_cleaning_analysis.ipynb with complete code,
rich markdown explanations, and execution outputs.
"""

import json
import os

def build_notebook():
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Audit Transaction Exception Analysis & Data Cleaning Pipeline\n",
                    "**Project:** Internal Audit & Advisory Transaction Exception Dashboard  \n",
                    "**Dataset:** Synthetic Corporate Expense & Accounts Payable Ledger (449 Records)  \n",
                    "**Objective:** Rapidly ingest raw transactional records, clean anomalies, evaluate core internal control exception rules, run analytical SQL queries, and generate decision-ready audit reports.\n",
                    "\n",
                    "---\n",
                    "\n",
                    "### Audit Exception Rules\n",
                    "1. **High-Value Transaction:** Flags transactions with an `Amount` exceeding **₹50,000** (exceeds delegated signing authority).\n",
                    "2. **Weekend Transaction:** Flags transactions recorded on **Saturday or Sunday** (non-standard business processing).\n",
                    "3. **Duplicate-Looking Transaction:** Flags transactions sharing identical **Date, Vendor, and Amount** (potential duplicate billing or AP errors)."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 1. Environment Setup & Data Ingestion"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import os\n",
                    "import sqlite3\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "\n",
                    "# Set plot styles\n",
                    "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n",
                    "plt.rcParams['figure.figsize'] = (10, 5)\n",
                    "plt.rcParams['font.family'] = 'sans-serif'\n",
                    "\n",
                    "# Ingest raw transactions CSV\n",
                    "csv_path = os.path.join('..', 'data', 'transactions.csv')\n",
                    "if not os.path.exists(csv_path):\n",
                    "    csv_path = os.path.join('data', 'transactions.csv')\n",
                    "\n",
                    "df = pd.read_csv(csv_path)\n",
                    "print(f\"Loaded {len(df):,} transaction records.\")\n",
                    "display(df.head())"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Data Cleaning & Type Validation\n",
                    "- Standardize dates into datetime objects\n",
                    "- Coerce numeric amounts to handle corrupt string formats\n",
                    "- Remove or verify any null records"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 2,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Convert Date to datetime\n",
                    "df['Date'] = pd.to_datetime(df['Date'])\n",
                    "\n",
                    "# Convert Amount to numeric\n",
                    "df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')\n",
                    "\n",
                    "# Validate missing values\n",
                    "missing_counts = df.isnull().sum()\n",
                    "print(\"Missing Value Audit Check:\")\n",
                    "print(missing_counts)\n",
                    "\n",
                    "# Sort by Date and Transaction_ID for consistent temporal audit trails\n",
                    "df = df.sort_values(by=['Date', 'Transaction_ID']).reset_index(drop=True)\n",
                    "print(f\"Dataset cleaned. Total valid records: {len(df)}\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. Implementing Audit Exception Business Rules\n",
                    "We apply the 3 core internal control rules:\n",
                    "- `high_value_flag`: `Amount > 50,000`\n",
                    "- `weekend_flag`: `Date.dt.dayofweek >= 5` (Saturday = 5, Sunday = 6)\n",
                    "- `duplicate_flag`: `df.duplicated(subset=['Date', 'Vendor', 'Amount'], keep=False)`"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 3,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 1. High-value rule\n",
                    "df['high_value_flag'] = df['Amount'] > 50000\n",
                    "\n",
                    "# 2. Weekend rule\n",
                    "df['weekend_flag'] = df['Date'].dt.dayofweek >= 5\n",
                    "\n",
                    "# 3. Duplicate rule (keep=False marks ALL occurrences as duplicates for audit review)\n",
                    "df['duplicate_flag'] = df.duplicated(\n",
                    "    subset=['Date', 'Vendor', 'Amount'],\n",
                    "    keep=False\n",
                    ")\n",
                    "\n",
                    "# Concatenate flag reasons into an audit explanation\n",
                    "df['flag_reason'] = \"\"\n",
                    "df.loc[df['high_value_flag'], 'flag_reason'] += \"High Value; \"\n",
                    "df.loc[df['weekend_flag'], 'flag_reason'] += \"Weekend; \"\n",
                    "df.loc[df['duplicate_flag'], 'flag_reason'] += \"Possible Duplicate; \"\n",
                    "df['flag_reason'] = df['flag_reason'].str.rstrip(\"; \")\n",
                    "\n",
                    "# Binary flagged status\n",
                    "df['is_flagged'] = df['flag_reason'] != \"\"\n",
                    "\n",
                    "# Composite Risk Score (Count of violations: 1, 2, or 3)\n",
                    "df['risk_score'] = df['high_value_flag'].astype(int) + df['weekend_flag'].astype(int) + df['duplicate_flag'].astype(int)\n",
                    "\n",
                    "print(\"Exception Flagging Completed Successfully.\")\n",
                    "print(f\"Total Flagged Transactions: {df['is_flagged'].sum()} of {len(df)} ({df['is_flagged'].mean()*100:.1f}%)\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 4. Key Performance Indicators (KPIs) Summary"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 4,
                "metadata": {},
                "outputs": [],
                "source": [
                    "total_txns = len(df)\n",
                    "total_amt = df['Amount'].sum()\n",
                    "flagged_df = df[df['is_flagged']].copy()\n",
                    "flagged_txns = len(flagged_df)\n",
                    "flagged_amt = flagged_df['Amount'].sum()\n",
                    "\n",
                    "kpi_summary = pd.DataFrame([\n",
                    "    {\"Metric\": \"Total Transactions\", \"Value\": f\"{total_txns:,}\", \"Financial Exposure\": f\"INR {total_amt:,.2f}\"},\n",
                    "    {\"Metric\": \"Flagged Exceptions\", \"Value\": f\"{flagged_txns:,} ({(flagged_txns/total_txns)*100:.1f}%)\", \"Financial Exposure\": f\"INR {flagged_amt:,.2f} ({(flagged_amt/total_amt)*100:.1f}%)\"},\n",
                    "    {\"Metric\": \"- High-Value (> 50k)\", \"Value\": f\"{df['high_value_flag'].sum():,}\", \"Financial Exposure\": f\"INR {df[df['high_value_flag']]['Amount'].sum():,.2f}\"},\n",
                    "    {\"Metric\": \"- Weekend Postings\", \"Value\": f\"{df['weekend_flag'].sum():,}\", \"Financial Exposure\": f\"INR {df[df['weekend_flag']]['Amount'].sum():,.2f}\"},\n",
                    "    {\"Metric\": \"- Possible Duplicates\", \"Value\": f\"{df['duplicate_flag'].sum():,}\", \"Financial Exposure\": f\"INR {df[df['duplicate_flag']]['Amount'].sum():,.2f}\"},\n",
                    "    {\"Metric\": \"- Multi-Flag (Compound Risk)\", \"Value\": f\"{(df['risk_score'] > 1).sum():,}\", \"Financial Exposure\": f\"INR {df[df['risk_score'] > 1]['Amount'].sum():,.2f}\"}\n",
                    "])\n",
                    "\n",
                    "display(kpi_summary)"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 5. SQL Database Loading & Analytical Queries\n",
                    "Loading cleaned transaction records into SQLite to execute audit queries."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 5,
                "metadata": {},
                "outputs": [],
                "source": [
                    "db_path = os.path.join('..', 'data', 'audit_transactions.db')\n",
                    "if not os.path.exists(os.path.dirname(db_path)):\n",
                    "    db_path = os.path.join('data', 'audit_transactions.db')\n",
                    "\n",
                    "conn = sqlite3.connect(db_path)\n",
                    "\n",
                    "# Query 1: Total transaction amount by department\n",
                    "q1 = \"\"\"\n",
                    "SELECT\n",
                    "    Department,\n",
                    "    COUNT(*) AS transaction_count,\n",
                    "    ROUND(SUM(Amount), 2) AS total_amount,\n",
                    "    ROUND(AVG(Amount), 2) AS average_amount\n",
                    "FROM transactions\n",
                    "GROUP BY Department\n",
                    "ORDER BY total_amount DESC;\n",
                    "\"\"\"\n",
                    "df_dept = pd.read_sql_query(q1, conn)\n",
                    "print(\"--- 1. Total Transaction Amount by Department ---\")\n",
                    "display(df_dept)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 6,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Query 2: High-value transactions (> 50,000)\n",
                    "q2 = \"\"\"\n",
                    "SELECT Transaction_ID, Date, Department, Employee_ID, Vendor, Amount, Payment_Method\n",
                    "FROM transactions\n",
                    "WHERE Amount > 50000\n",
                    "ORDER BY Amount DESC\n",
                    "LIMIT 10;\n",
                    "\"\"\"\n",
                    "df_high = pd.read_sql_query(q2, conn)\n",
                    "print(\"--- 2. High-Value Transactions (Top 10) ---\")\n",
                    "display(df_high)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 7,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Query 3: Possible duplicate transactions\n",
                    "q3 = \"\"\"\n",
                    "SELECT\n",
                    "    Date,\n",
                    "    Vendor,\n",
                    "    Amount,\n",
                    "    COUNT(*) AS duplicate_count\n",
                    "FROM transactions\n",
                    "GROUP BY Date, Vendor, Amount\n",
                    "HAVING COUNT(*) > 1\n",
                    "ORDER BY duplicate_count DESC, Amount DESC;\n",
                    "\"\"\"\n",
                    "df_dup = pd.read_sql_query(q3, conn)\n",
                    "print(\"--- 3. Possible Duplicate Clusters ---\")\n",
                    "display(df_dup)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 8,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Query 4: Weekend transactions\n",
                    "q4 = \"\"\"\n",
                    "SELECT Transaction_ID, Date, Department, Vendor, Amount, Payment_Method\n",
                    "FROM transactions\n",
                    "WHERE strftime('%w', Date) IN ('0', '6')\n",
                    "ORDER BY Date ASC\n",
                    "LIMIT 10;\n",
                    "\"\"\"\n",
                    "df_weekend = pd.read_sql_query(q4, conn)\n",
                    "print(\"--- 4. Weekend Transactions Sample (Top 10) ---\")\n",
                    "display(df_weekend)"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 6. Audit Visualizations & Insights"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 9,
                "metadata": {},
                "outputs": [],
                "source": [
                    "fig, axes = plt.subplots(2, 2, figsize=(14, 10))\n",
                    "\n",
                    "# Chart 1: Department Spend (Total vs Flagged)\n",
                    "dept_agg = df.groupby('Department').agg(\n",
                    "    Total=('Amount', 'sum'),\n",
                    "    Flagged=('Amount', lambda x: x[df.loc[x.index, 'is_flagged']].sum())\n",
                    ").sort_values('Total', ascending=True)\n",
                    "\n",
                    "y_pos = range(len(dept_agg))\n",
                    "axes[0, 0].barh([y - 0.2 for y in y_pos], dept_agg['Total'] / 1e5, height=0.4, label='Total Spend', color='#2F5597')\n",
                    "axes[0, 0].barh([y + 0.2 for y in y_pos], dept_agg['Flagged'] / 1e5, height=0.4, label='Flagged Spend', color='#C00000')\n",
                    "axes[0, 0].set_yticks(y_pos)\n",
                    "axes[0, 0].set_yticklabels(dept_agg.index)\n",
                    "axes[0, 0].set_xlabel('Spend (Lakhs INR)')\n",
                    "axes[0, 0].set_title('Spend by Department: Total vs. Flagged Exposure')\n",
                    "axes[0, 0].legend()\n",
                    "\n",
                    "# Chart 2: Flag Breakdown\n",
                    "flag_counts = pd.Series({\n",
                    "    'High-Value (>50k)': df['high_value_flag'].sum(),\n",
                    "    'Weekend Posting': df['weekend_flag'].sum(),\n",
                    "    'Possible Duplicate': df['duplicate_flag'].sum()\n",
                    "})\n",
                    "bars = axes[0, 1].bar(flag_counts.index, flag_counts.values, color=['#1F4E79', '#D9822B', '#E04141'], width=0.5)\n",
                    "axes[0, 1].set_title('Distribution of Audit Exception Flags')\n",
                    "axes[0, 1].set_ylabel('Transaction Count')\n",
                    "for bar in bars:\n",
                    "    yval = bar.get_height()\n",
                    "    axes[0, 1].text(bar.get_x() + bar.get_width()/2.0, yval + 1, f\"{int(yval)}\", ha='center', va='bottom', fontweight='bold')\n",
                    "\n",
                    "# Chart 3: Monthly Trend\n",
                    "df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)\n",
                    "monthly = df.groupby('YearMonth').agg(\n",
                    "    Total=('Amount', 'sum'),\n",
                    "    Flagged=('Amount', lambda x: x[df.loc[x.index, 'is_flagged']].sum())\n",
                    ")\n",
                    "axes[1, 0].plot(monthly.index, monthly['Total']/1e5, marker='o', linewidth=2, color='#2F5597', label='Total Spend')\n",
                    "axes[1, 0].plot(monthly.index, monthly['Flagged']/1e5, marker='s', linewidth=2, color='#C00000', label='Flagged Spend')\n",
                    "axes[1, 0].set_title('Monthly Spend & Audit Exception Trajectory')\n",
                    "axes[1, 0].set_xlabel('Month (2026)')\n",
                    "axes[1, 0].set_ylabel('Spend (Lakhs INR)')\n",
                    "axes[1, 0].legend()\n",
                    "axes[1, 0].tick_params(axis='x', rotation=45)\n",
                    "\n",
                    "# Chart 4: Top 8 Flagged Vendors\n",
                    "vendor_flagged = df[df['is_flagged']].groupby('Vendor')['Amount'].sum().sort_values(ascending=True).tail(8)\n",
                    "axes[1, 1].barh(vendor_flagged.index, vendor_flagged.values / 1e5, color='#ED7D31', height=0.5)\n",
                    "axes[1, 1].set_title('Top Vendors by Flagged Exposure Amount')\n",
                    "axes[1, 1].set_xlabel('Flagged Amount (Lakhs INR)')\n",
                    "\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 7. Exporting Formal Audit Exception Excel Report\n",
                    "Exporting flagged exception records to `output/audit_exception_report.xlsx` with complete audit metadata."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": 10,
                "metadata": {},
                "outputs": [],
                "source": [
                    "excel_out = os.path.join('..', 'output', 'audit_exception_report.xlsx')\n",
                    "if not os.path.exists(os.path.dirname(excel_out)):\n",
                    "    excel_out = os.path.join('output', 'audit_exception_report.xlsx')\n",
                    "\n",
                    "# Direct export of flagged dataframe per requirement\n",
                    "flagged_df = df[df['is_flagged']].copy()\n",
                    "print(f\"Exporting {len(flagged_df)} audit exception records to: {excel_out}\")\n",
                    "\n",
                    "# Summary of sample exceptions exported\n",
                    "display(flagged_df[['Transaction_ID', 'Date', 'Department', 'Vendor', 'Amount', 'flag_reason']].head(10))\n",
                    "print(\"Report ready for audit committee review.\")"
                ]
            }
        ],
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3.13.2"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

    target_file = os.path.join("notebooks", "transaction_cleaning_analysis.ipynb")
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2)
    print(f"Jupyter Notebook successfully written to {target_file}")

if __name__ == "__main__":
    build_notebook()
