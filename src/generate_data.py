"""
Synthetic Transaction Data Generator for Audit Exception Analysis
Generates realistic corporate expense/AP transaction records with known audit exceptions:
1. High-value transactions (> ₹50,000 threshold)
2. Weekend transactions (Saturday/Sunday postings)
3. Duplicate-looking transactions (identical Date, Vendor, and Amount)
"""

import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_transactions(num_records=450, random_seed=42):
    random.seed(random_seed)
    np.random.seed(random_seed)

    departments = [
        "Finance", "IT", "Operations", "Marketing",
        "Procurement", "Human Resources", "Sales", "Legal"
    ]

    dept_employees = {
        "Finance": ["EMP101", "EMP102", "EMP103", "EMP104"],
        "IT": ["EMP105", "EMP106", "EMP107", "EMP108"],
        "Operations": ["EMP109", "EMP110", "EMP111"],
        "Marketing": ["EMP112", "EMP113", "EMP114"],
        "Procurement": ["EMP115", "EMP116", "EMP117"],
        "Human Resources": ["EMP118", "EMP119"],
        "Sales": ["EMP120", "EMP121", "EMP122"],
        "Legal": ["EMP123", "EMP124", "EMP125"]
    }

    vendors = [
        "ABC Supplies", "Apex Technology", "Global Logistics Corp",
        "Stellar Consulting", "OfficeMart Solutions", "CloudCore Systems",
        "Delta Services", "Metro Facility Services", "Horizon Media Works",
        "Zenith Travel Partners", "QuickCourier Express", "Nexus Cyber Solutions"
    ]

    payment_methods = ["Bank Transfer", "Credit Card", "ACH", "Check", "Wire Transfer"]

    start_date = datetime(2026, 1, 5)
    end_date = datetime(2026, 8, 25)
    date_range_days = (end_date - start_date).days

    records = []

    # 1. Base normal transactions (approx 340 records)
    for i in range(1, 351):
        txn_id = f"TXN{1000 + i}"
        # Pick a weekday mostly
        while True:
            offset = random.randint(0, date_range_days)
            dt = start_date + timedelta(days=offset)
            if dt.weekday() < 5:  # Monday to Friday
                break

        dept = random.choice(departments)
        emp = random.choice(dept_employees[dept])
        vendor = random.choice(vendors)
        # Regular amount under ₹50,000
        amount = round(random.uniform(1500, 48500), 2)
        # round some to nice 100s/50s
        if random.random() < 0.7:
            amount = round(amount / 50) * 50
        method = random.choice(payment_methods)

        records.append({
            "Transaction_ID": txn_id,
            "Date": dt.strftime("%Y-%m-%d"),
            "Department": dept,
            "Employee_ID": emp,
            "Vendor": vendor,
            "Amount": amount,
            "Payment_Method": method
        })

    # 2. High-value transactions (> 50,000) - approx 35 records
    for i in range(351, 386):
        txn_id = f"TXN{1000 + i}"
        offset = random.randint(0, date_range_days)
        dt = start_date + timedelta(days=offset)
        # mostly weekdays
        if random.random() < 0.85:
            while dt.weekday() >= 5:
                dt += timedelta(days=1)

        dept = random.choice(["Finance", "IT", "Procurement", "Legal", "Operations"])
        emp = random.choice(dept_employees[dept])
        vendor = random.choice(["Apex Technology", "Stellar Consulting", "CloudCore Systems", "Nexus Cyber Solutions", "Global Logistics Corp"])
        # High value between 52,000 and 195,000
        amount = round(random.uniform(52000, 195000), 2)
        if random.random() < 0.6:
            amount = round(amount / 500) * 500
        method = random.choice(["Wire Transfer", "Bank Transfer", "ACH"])

        records.append({
            "Transaction_ID": txn_id,
            "Date": dt.strftime("%Y-%m-%d"),
            "Department": dept,
            "Employee_ID": emp,
            "Vendor": vendor,
            "Amount": amount,
            "Payment_Method": method
        })

    # 3. Weekend transactions (Saturday/Sunday) - approx 40 records
    weekend_dates = []
    curr = start_date
    while curr <= end_date:
        if curr.weekday() in (5, 6): # Saturday or Sunday
            weekend_dates.append(curr)
        curr += timedelta(days=1)

    for i in range(386, 426):
        txn_id = f"TXN{1000 + i}"
        dt = random.choice(weekend_dates)
        dept = random.choice(departments)
        emp = random.choice(dept_employees[dept])
        vendor = random.choice(vendors)
        # some regular amounts, a few high value on weekend!
        if i in (423, 424, 425):
            amount = round(random.uniform(55000, 110000), 2)  # Multi-flag! High value AND Weekend
        else:
            amount = round(random.uniform(2200, 45000), 2)
            if random.random() < 0.5:
                amount = round(amount / 100) * 100
        method = random.choice(payment_methods)

        records.append({
            "Transaction_ID": txn_id,
            "Date": dt.strftime("%Y-%m-%d"),
            "Department": dept,
            "Employee_ID": emp,
            "Vendor": vendor,
            "Amount": amount,
            "Payment_Method": method
        })

    # 4. Duplicate transactions (pairs/triplets with same Date, Vendor, Amount) - approx 24 records (11 groups)
    duplicate_specs = [
        ("2026-02-14", "ABC Supplies", 14500.00, "Finance", "EMP102", "Bank Transfer", 2),
        ("2026-03-10", "Apex Technology", 68000.00, "IT", "EMP106", "Wire Transfer", 2), # Duplicate + High Value!
        ("2026-04-05", "OfficeMart Solutions", 8950.00, "Marketing", "EMP113", "Credit Card", 2), # Sunday + Duplicate!
        ("2026-04-22", "Global Logistics Corp", 32400.00, "Operations", "EMP110", "ACH", 3), # Triplet
        ("2026-05-18", "CloudCore Systems", 74000.00, "IT", "EMP105", "Bank Transfer", 2), # Duplicate + High Value!
        ("2026-06-02", "Delta Services", 19200.00, "Procurement", "EMP116", "Check", 2),
        ("2026-06-20", "Zenith Travel Partners", 46800.00, "Sales", "EMP121", "Credit Card", 2), # Saturday + Duplicate!
        ("2026-07-11", "Horizon Media Works", 28500.00, "Marketing", "EMP114", "Bank Transfer", 2), # Saturday + Duplicate!
        ("2026-07-28", "Metro Facility Services", 12300.00, "Operations", "EMP109", "ACH", 2),
        ("2026-08-08", "Nexus Cyber Solutions", 85000.00, "IT", "EMP107", "Wire Transfer", 2), # Saturday + Duplicate + High Value (Triple flag!)
        ("2026-08-18", "Stellar Consulting", 92000.00, "Legal", "EMP124", "Wire Transfer", 3), # Duplicate + High Value Triplet!
    ]

    txn_counter = 426
    for dt_str, vendor, amt, dept, emp, method, count in duplicate_specs:
        for copy_idx in range(count):
            txn_id = f"TXN{1000 + txn_counter}"
            txn_counter += 1
            # Slight variations in employee or payment method for realistic duplicate billing
            rec_emp = emp if copy_idx == 0 else random.choice(dept_employees[dept])
            rec_method = method if copy_idx == 0 else random.choice(payment_methods)
            records.append({
                "Transaction_ID": txn_id,
                "Date": dt_str,
                "Department": dept,
                "Employee_ID": rec_emp,
                "Vendor": vendor,
                "Amount": amt,
                "Payment_Method": rec_method
            })

    # Convert to DataFrame
    df = pd.DataFrame(records)

    # Sort deterministically by Transaction_ID
    df = df.sort_values("Transaction_ID").reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate_transactions()
    output_path = "data/transactions.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} transactions and saved to {output_path}")
    print("\nSample records:")
    print(df.head())
    print("\nSummary stats:")
    print(df.describe())
