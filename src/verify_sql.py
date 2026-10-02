"""
Verification script for SQL queries on audit_transactions.db
"""

import sqlite3

def run_queries():
    conn = sqlite3.connect("data/audit_transactions.db")
    cursor = conn.cursor()

    print("==================================================")
    print("QUERY 1: Total transaction amount by department")
    print("==================================================")
    q1 = """
    SELECT
        Department,
        COUNT(*) AS transaction_count,
        ROUND(SUM(Amount), 2) AS total_amount,
        ROUND(AVG(Amount), 2) AS average_amount
    FROM transactions
    GROUP BY Department
    ORDER BY total_amount DESC;
    """
    for row in cursor.execute(q1).fetchall():
        print(f"{row[0]:<18} | Count: {row[1]:<4} | Total: INR {row[2]:>12,.2f} | Avg: INR {row[3]:>9,.2f}")

    print("\n==================================================")
    print("QUERY 2: High-value transactions (> 50,000)")
    print("==================================================")
    q2 = """
    SELECT Transaction_ID, Date, Department, Vendor, Amount, Payment_Method
    FROM transactions
    WHERE Amount > 50000
    ORDER BY Amount DESC
    LIMIT 5;
    """
    for row in cursor.execute(q2).fetchall():
        print(f"{row[0]} | {row[1]} | {row[2]:<12} | {row[3]:<22} | INR {row[4]:>10,.2f} | {row[5]}")
    total_high = cursor.execute("SELECT COUNT(*), ROUND(SUM(Amount),2) FROM transactions WHERE Amount > 50000").fetchone()
    print(f"Total High-Value Records: {total_high[0]} | Total Amount: INR {total_high[1]:,.2f}")

    print("\n==================================================")
    print("QUERY 3: Possible duplicate transactions")
    print("==================================================")
    q3 = """
    SELECT
        Date,
        Vendor,
        Amount,
        COUNT(*) AS duplicate_count
    FROM transactions
    GROUP BY Date, Vendor, Amount
    HAVING COUNT(*) > 1
    ORDER BY duplicate_count DESC, Amount DESC;
    """
    for row in cursor.execute(q3).fetchall():
        print(f"Date: {row[0]} | Vendor: {row[1]:<25} | Amount: INR {row[2]:>9,.2f} | Count: {row[3]}")

    print("\n==================================================")
    print("QUERY 4: Weekend transactions (Saturday/Sunday)")
    print("==================================================")
    q4 = """
    SELECT Transaction_ID, Date, Department, Vendor, Amount,
           CASE strftime('%w', Date)
               WHEN '0' THEN 'Sunday'
               WHEN '6' THEN 'Saturday'
           END AS Weekend_Day
    FROM transactions
    WHERE strftime('%w', Date) IN ('0', '6')
    ORDER BY Date, Amount DESC
    LIMIT 5;
    """
    for row in cursor.execute(q4).fetchall():
        print(f"{row[0]} | {row[1]} ({row[5]:<8}) | {row[2]:<12} | {row[3]:<22} | INR {row[4]:>10,.2f}")
    total_weekend = cursor.execute("SELECT COUNT(*), ROUND(SUM(Amount),2) FROM transactions WHERE strftime('%w', Date) IN ('0', '6')").fetchone()
    print(f"Total Weekend Records: {total_weekend[0]} | Total Amount: INR {total_weekend[1]:,.2f}")

    print("\n==================================================")
    print("BONUS AUDIT QUERY: Compound Exception Risk Summary")
    print("==================================================")
    q_bonus = """
    SELECT
        t.Department,
        COUNT(e.Transaction_ID) AS flagged_count,
        ROUND(SUM(e.Amount), 2) AS flagged_amount,
        SUM(CASE WHEN e.high_value_flag = 1 THEN 1 ELSE 0 END) AS high_val_count,
        SUM(CASE WHEN e.weekend_flag = 1 THEN 1 ELSE 0 END) AS weekend_count,
        SUM(CASE WHEN e.duplicate_flag = 1 THEN 1 ELSE 0 END) AS duplicate_count
    FROM audit_exceptions e
    JOIN transactions t ON e.Transaction_ID = t.Transaction_ID
    GROUP BY t.Department
    ORDER BY flagged_amount DESC;
    """
    for row in cursor.execute(q_bonus).fetchall():
        print(f"{row[0]:<18} | Flagged: {row[1]:<3} | INR {row[2]:>12,.2f} | HighVal: {row[3]} | Wknd: {row[4]} | Dup: {row[5]}")

    conn.close()

if __name__ == "__main__":
    run_queries()
