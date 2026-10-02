# Power BI Dashboard Setup & DAX Reference Guide

**Project:** Audit Transaction Exception Dashboard  
**Target File:** `dashboard/audit_exception_dashboard.pbix`  
**Data Sources:** `data/transactions.csv` or SQLite `data/audit_transactions.db`  

---

## 1. Quick Data Connection (Power Query M)

To connect directly to the cleaned transaction data in Power BI Desktop:

1. Open **Power BI Desktop**.
2. Click **Get Data** > **Text/CSV** > Select `data/transactions.csv`.
3. In Power Query Editor, verify data types:
   - `Transaction_ID`: Text
   - `Date`: Date
   - `Department`: Text
   - `Employee_ID`: Text
   - `Vendor`: Text
   - `Amount`: Decimal Number (Currency)
   - `Payment_Method`: Text

### Power Query M Code (Advanced Editor)
```powerquery
let
    Source = Csv.Document(File.Contents("..\data\transactions.csv"), [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"Transaction_ID", type text},
        {"Date", type date},
        {"Department", type text},
        {"Employee_ID", type text},
        {"Vendor", type text},
        {"Amount", Currency.Type},
        {"Payment_Method", type text}
    }),
    #"Added High Value Flag" = Table.AddColumn(#"Changed Type", "high_value_flag", each [Amount] > 50000, type logical),
    #"Added Weekend Flag" = Table.AddColumn(#"Added High Value Flag", "weekend_flag", each Date.DayOfWeek([Date], Day.Monday) >= 5, type logical),
    #"Added Duplicate Flag" = Table.AddColumn(#"Added Weekend Flag", "duplicate_flag", each
        let
            currDate = [Date],
            currVendor = [Vendor],
            currAmt = [Amount],
            matchRows = Table.SelectRows(#"Added Weekend Flag", each [Date] = currDate and [Vendor] = currVendor and [Amount] = currAmt)
        in
            Table.RowCount(matchRows) > 1,
        type logical
    ),
    #"Added Flag Reason" = Table.AddColumn(#"Added Duplicate Flag", "flag_reason", each
        Text.TrimEnd(
            (if [high_value_flag] then "High Value; " else "") &
            (if [weekend_flag] then "Weekend; " else "") &
            (if [duplicate_flag] then "Possible Duplicate; " else ""),
            {";", " "}
        ),
        type text
    ),
    #"Added Is Flagged" = Table.AddColumn(#"Added Flag Reason", "is_flagged", each [flag_reason] <> "", type logical),
    #"Added Risk Score" = Table.AddColumn(#"Added Is Flagged", "risk_score", each
        (if [high_value_flag] then 1 else 0) +
        (if [weekend_flag] then 1 else 0) +
        (if [duplicate_flag] then 1 else 0),
        Int64.Type
    )
in
    #"Added Risk Score"
```

---

## 2. DAX Measures Library

Create a dedicated **Measures Table** or add these measures to `Transactions`:

### 1. Total Transactions
```dax
Total Transactions = COUNTROWS('Transactions')
```

### 2. Total Transaction Spend
```dax
Total Spend = SUM('Transactions'[Amount])
```

### 3. Flagged Exceptions Count
```dax
Flagged Exceptions = 
CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[is_flagged] = TRUE()
)
```

### 4. Flagged Exception Percentage
```dax
Flagged Exception % = 
DIVIDE([Flagged Exceptions], [Total Transactions], 0)
```

### 5. Flagged Exposure Amount
```dax
Flagged Spend = 
CALCULATE(
    SUM('Transactions'[Amount]),
    'Transactions'[is_flagged] = TRUE()
)
```

### 6. Flagged Spend Percentage
```dax
Flagged Spend % = 
DIVIDE([Flagged Spend], [Total Spend], 0)
```

### 7. High-Value Exceptions
```dax
High Value Count = 
CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[high_value_flag] = TRUE()
)
```

### 8. Weekend Exceptions
```dax
Weekend Count = 
CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[weekend_flag] = TRUE()
)
```

### 9. Duplicate Exceptions
```dax
Duplicate Count = 
CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[duplicate_flag] = TRUE()
)
```

### 10. Multi-Flag Compound Risk Count
```dax
Compound Risk Exceptions = 
CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[risk_score] > 1
)
```

---

## 3. Visual Layout Specifications

### Canvas Settings
- **Page Size:** 16:9 (1280 x 720 px or 1920 x 1080 px)
- **Background Color:** `#F0F2F6` (Neutral Warm Gray)

### Visual 1–4: Executive KPI Cards (Top Banner)
- **Card 1:** `Total Transactions` (Format: `#,##0`) | Accent: Navy `#1F4E79`
- **Card 2:** `Total Spend` (Format: `₹#,##0.00` / Lakhs) | Accent: Navy `#1F4E79`
- **Card 3:** `Flagged Exceptions` (Format: `#,##0`) | Accent: Alert Red `#C00000`
- **Card 4:** `Flagged Exception %` (Format: `0.0%`) | Accent: Alert Red `#C00000`

### Visual 5: Slicer Panel (Left Rail)
- **Department Slicer:** Vertical list with checkbox selection
- **Exception Rule Slicer:** Single/multi-select radio buttons
- **Date Range Slicer:** Between slider (`2026-01-05` to `2026-08-25`)

### Visual 6: Flagged Transactions by Reason (Bar / Column Chart)
- **X-axis:** `flag_reason` (or unpivoted rule names: High Value, Weekend, Duplicate)
- **Y-axis:** `[Flagged Exceptions]`
- **Data Labels:** On (Inside End)
- **Colors:** Weekend (`#2F5597`), High Value (`#C00000`), Duplicate (`#ED7D31`)

### Visual 7: Transaction Amount by Department (Clustered Horizontal Bar)
- **Y-axis:** `Department`
- **X-axis:** `[Total Spend]` and `[Flagged Spend]`
- **Legend:** Total Spend (Navy `#2F5597`), Flagged Spend (Red `#C00000`)
- **Sort:** Total Spend descending

### Visual 8: Monthly Spend Trajectory (Line & Area Chart)
- **X-axis:** `Date` (Hierarchy: Month)
- **Y-axis:** `[Total Spend]`, `[Flagged Spend]`
- **Markers:** Enabled (Circle / Square)

### Visual 9: Top 10 Flagged Vendors (Horizontal Bar Chart)
- **Y-axis:** `Vendor` (Filter: Top 10 by `[Flagged Spend]`)
- **X-axis:** `[Flagged Spend]`
- **Color:** Warning Orange (`#ED7D31`)

### Visual 10: Audit Exception Review Queue (Table)
- **Columns:**
  1. `Transaction_ID`
  2. `Date`
  3. `Vendor`
  4. `Amount` (Right-aligned, Currency format)
  5. `Department`
  6. `flag_reason` (Conditional formatting: soft red background for multi-flag)
- **Filter on visual:** `is_flagged = TRUE`
- **Sort:** `Amount` descending
