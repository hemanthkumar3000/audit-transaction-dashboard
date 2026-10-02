"""
Generates an interactive, standalone HTML/JS Audit Exception Dashboard
allowing immediate interactive exploration of the 449 transactions in any browser.
"""

import json
import os
import pandas as pd

def build_interactive_html():
    csv_path = os.path.join("data", "transactions.csv")
    df = pd.read_csv(csv_path)

    df["Date"] = pd.to_datetime(df["Date"])
    df["Amount"] = pd.to_numeric(df["Amount"])
    df["high_value_flag"] = df["Amount"] > 50000
    df["weekend_flag"] = df["Date"].dt.dayofweek >= 5
    df["duplicate_flag"] = df.duplicated(subset=["Date", "Vendor", "Amount"], keep=False)

    df["flag_reason"] = ""
    df.loc[df["high_value_flag"], "flag_reason"] += "High Value; "
    df.loc[df["weekend_flag"], "flag_reason"] += "Weekend; "
    df.loc[df["duplicate_flag"], "flag_reason"] += "Possible Duplicate; "
    df["flag_reason"] = df["flag_reason"].str.rstrip("; ")
    df["is_flagged"] = df["flag_reason"] != ""
    df["Date_Str"] = df["Date"].dt.strftime("%Y-%m-%d")

    records = df[[
        "Transaction_ID", "Date_Str", "Department", "Employee_ID",
        "Vendor", "Amount", "Payment_Method", "high_value_flag",
        "weekend_flag", "duplicate_flag", "flag_reason", "is_flagged"
    ]].rename(columns={"Date_Str": "Date"}).to_dict(orient="records")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Audit Transaction Exception Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --primary: #1F4E79;
      --primary-light: #2F5597;
      --danger: #C00000;
      --warning: #ED7D31;
      --bg: #F0F2F6;
      --card-bg: #FFFFFF;
      --border: #D1D5DB;
      --text-main: #1F2937;
      --text-muted: #6B7280;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
    body {{ background-color: var(--bg); color: var(--text-main); padding-bottom: 40px; }}
    
    /* Header */
    header {{
      background: linear-gradient(135deg, #1F4E79 0%, #0F2B48 100%);
      color: white;
      padding: 16px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 4px solid #C5A059;
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }}
    header h1 {{ font-size: 1.4rem; font-weight: 700; letter-spacing: -0.02em; }}
    header p {{ font-size: 0.85rem; color: #D9E1F2; margin-top: 4px; }}
    .header-badge {{
      background: rgba(255,255,255,0.12);
      border: 1px solid rgba(255,255,255,0.25);
      border-radius: 6px;
      padding: 8px 14px;
      text-align: right;
    }}
    .header-badge .status {{ color: #FFD27F; font-weight: bold; font-size: 0.85rem; }}
    .header-badge .sub {{ font-size: 0.75rem; color: #E5E7EB; }}

    /* Layout */
    .dashboard-container {{
      display: grid;
      grid-template-columns: 260px 1fr;
      gap: 20px;
      padding: 20px 28px;
      max-width: 1720px;
      margin: 0 auto;
    }}

    /* Slicers Sidebar */
    .sidebar {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
      height: fit-content;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .sidebar h2 {{
      font-size: 0.95rem;
      color: var(--primary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 16px;
      border-bottom: 2px solid #E5E7EB;
      padding-bottom: 8px;
    }}
    .filter-group {{ margin-bottom: 18px; }}
    .filter-group label {{
      display: block;
      font-size: 0.8rem;
      font-weight: 700;
      color: #374151;
      margin-bottom: 6px;
    }}
    select, input[type="date"], input[type="text"] {{
      width: 100%;
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 0.85rem;
      color: #1F2937;
      background: #F9FAFB;
      outline: none;
    }}
    select:focus, input:focus {{ border-color: var(--primary); background: #FFF; }}
    .filter-btn-group {{ display: flex; flex-direction: column; gap: 6px; margin-top: 6px; }}
    .filter-btn {{
      padding: 7px 10px;
      text-align: left;
      font-size: 0.8rem;
      border-radius: 6px;
      border: 1px solid #E5E7EB;
      background: #F9FAFB;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      transition: all 0.15s;
    }}
    .filter-btn:hover {{ background: #EFF6FF; border-color: #BFDBFE; }}
    .filter-btn.active {{
      background: #1F4E79;
      color: white;
      border-color: #1F4E79;
      font-weight: bold;
    }}

    .guidance-box {{
      background: #EFF6FF;
      border: 1px solid #BFDBFE;
      border-radius: 8px;
      padding: 12px;
      margin-top: 20px;
      font-size: 0.78rem;
      color: #1E3A8A;
      line-height: 1.4;
    }}
    .guidance-box strong {{ display: block; margin-bottom: 4px; color: #1E40AF; }}

    /* Main Content */
    .main-panel {{ display: flex; flex-direction: column; gap: 20px; }}

    /* KPI Cards */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }}
    .kpi-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px 18px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .kpi-card::before {{
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0; height: 4px;
      background: var(--primary);
    }}
    .kpi-card.danger::before {{ background: var(--danger); }}
    .kpi-title {{ font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }}
    .kpi-val {{ font-size: 1.6rem; font-weight: 800; color: var(--primary); margin: 6px 0 2px 0; }}
    .kpi-card.danger .kpi-val {{ color: var(--danger); }}
    .kpi-sub {{ font-size: 0.75rem; color: #9CA3AF; }}

    /* Charts Grid */
    .charts-row-1 {{
      display: grid;
      grid-template-columns: 1fr 1.3fr 1.1fr;
      gap: 16px;
    }}
    .charts-row-2 {{
      display: grid;
      grid-template-columns: 1.1fr 1.6fr;
      gap: 16px;
    }}
    .chart-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px 18px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      display: flex;
      flex-direction: column;
    }}
    .chart-card h3 {{
      font-size: 0.9rem;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 12px;
    }}
    .chart-canvas-container {{ position: relative; flex: 1; min-height: 220px; }}

    /* Table */
    .table-container {{
      overflow-x: auto;
      max-height: 340px;
      margin-top: 8px;
      border: 1px solid #E5E7EB;
      border-radius: 6px;
    }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; text-align: left; }}
    th {{
      background: #1F4E79;
      color: white;
      padding: 9px 12px;
      font-weight: 600;
      position: sticky;
      top: 0;
      z-index: 2;
    }}
    td {{ padding: 8px 12px; border-bottom: 1px solid #F3F4F6; }}
    tr:nth-child(even) {{ background: #F9FAFB; }}
    tr:hover {{ background: #EFF6FF; }}
    tr.compound {{ background: #FEF2F2 !important; }}
    
    .badge {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 12px;
      font-size: 0.72rem;
      font-weight: 600;
    }}
    .badge-danger {{ background: #FEE2E2; color: #991B1B; }}
    .badge-primary {{ background: #E0E7FF; color: #3730A3; }}
    .badge-warning {{ background: #FFEDD5; color: #9A3412; }}

    .table-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
    .export-btn {{
      background: #107C41;
      color: white;
      border: none;
      padding: 6px 12px;
      font-size: 0.78rem;
      font-weight: 600;
      border-radius: 4px;
      cursor: pointer;
    }}
    .export-btn:hover {{ background: #0E6836; }}

    @media (max-width: 1200px) {{
      .dashboard-container {{ grid-template-columns: 1fr; }}
      .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .charts-row-1, .charts-row-2 {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

  <header>
    <div>
      <h1>Audit Transaction Exception Dashboard</h1>
      <p>Internal Controls Continuous Monitoring & Risk Analytics | Advisory Format</p>
    </div>
    <div class="header-badge">
      <div class="status" id="headerStatus">99 EXCEPTIONS FLAGGED</div>
      <div class="sub">Total Scope: 449 Transactions</div>
    </div>
  </header>

  <div class="dashboard-container">
    <!-- Sidebar Slicers -->
    <aside class="sidebar">
      <h2>Filters & Slicers</h2>

      <div class="filter-group">
        <label for="searchFilter">Quick Search</label>
        <input type="text" id="searchFilter" placeholder="Vendor, ID, Dept..." oninput="applyFilters()">
      </div>

      <div class="filter-group">
        <label for="deptSelect">Department Slicer</label>
        <select id="deptSelect" onchange="applyFilters()">
          <option value="ALL">(All Departments)</option>
          <option value="Legal">Legal</option>
          <option value="IT">IT</option>
          <option value="Operations">Operations</option>
          <option value="Procurement">Procurement</option>
          <option value="Finance">Finance</option>
          <option value="Marketing">Marketing</option>
          <option value="Sales">Sales</option>
          <option value="Human Resources">Human Resources</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Exception Rule Slicer</label>
        <div class="filter-btn-group">
          <button class="filter-btn active" data-rule="ALL" onclick="selectRule(this, 'ALL')">
            <span>(All Records)</span> <span id="cntAll">449</span>
          </button>
          <button class="filter-btn" data-rule="FLAGGED" onclick="selectRule(this, 'FLAGGED')">
            <span>Any Flagged Exception</span> <span id="cntFlagged">99</span>
          </button>
          <button class="filter-btn" data-rule="HIGH_VAL" onclick="selectRule(this, 'HIGH_VAL')">
            <span>High Value (&gt; ₹50k)</span> <span id="cntHigh">47</span>
          </button>
          <button class="filter-btn" data-rule="WEEKEND" onclick="selectRule(this, 'WEEKEND')">
            <span>Weekend Posting</span> <span id="cntWknd">51</span>
          </button>
          <button class="filter-btn" data-rule="DUPLICATE" onclick="selectRule(this, 'DUPLICATE')">
            <span>Possible Duplicate</span> <span id="cntDup">24</span>
          </button>
        </div>
      </div>

      <div class="filter-group">
        <label>Date Range Slicer</label>
        <input type="date" id="dateStart" value="2026-01-05" onchange="applyFilters()">
        <div style="height: 6px;"></div>
        <input type="date" id="dateEnd" value="2026-08-25" onchange="applyFilters()">
      </div>

      <div class="guidance-box">
        <strong>AUDIT BUSINESS RULES</strong>
        • <b>High Value:</b> Amount &gt; ₹50,000<br>
        • <b>Weekend:</b> Posted on Sat / Sun<br>
        • <b>Duplicate:</b> Same Date, Vendor, and Amount<br>
        • <b>Compound Risk:</b> Highlighted in soft red
      </div>
    </aside>

    <!-- Main Content Panel -->
    <main class="main-panel">
      <!-- Top KPI Row -->
      <section class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-title">Total Transactions</div>
          <div class="kpi-val" id="kpiTotalTxns">449</div>
          <div class="kpi-sub">100% In-Scope Records</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-title">Total Transaction Amount</div>
          <div class="kpi-val" id="kpiTotalAmt">₹152.16 L</div>
          <div class="kpi-sub" id="kpiTotalAmtExact">₹15,216,053.91</div>
        </div>

        <div class="kpi-card danger">
          <div class="kpi-title">Flagged Exceptions</div>
          <div class="kpi-val" id="kpiFlaggedTxns">99</div>
          <div class="kpi-sub" id="kpiFlaggedSub">Anomalies Requiring Review</div>
        </div>

        <div class="kpi-card danger">
          <div class="kpi-title">Flagged Percentage</div>
          <div class="kpi-val" id="kpiFlaggedPct">22.0%</div>
          <div class="kpi-sub" id="kpiFlaggedSpend">₹62.13 L (40.8% of spend)</div>
        </div>
      </section>

      <!-- Charts Row 1 -->
      <section class="charts-row-1">
        <div class="chart-card">
          <h3>Flagged Transactions by Flag Reason</h3>
          <div class="chart-canvas-container">
            <canvas id="chartReasons"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <h3>Transaction Amount by Department (₹ Lakhs)</h3>
          <div class="chart-canvas-container">
            <canvas id="chartDept"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <h3>Monthly Transaction Amount (₹ Lakhs)</h3>
          <div class="chart-canvas-container">
            <canvas id="chartMonthly"></canvas>
          </div>
        </div>
      </section>

      <!-- Charts Row 2 & Table -->
      <section class="charts-row-2">
        <div class="chart-card">
          <h3>Top 10 Flagged Vendors by Exposure</h3>
          <div class="chart-canvas-container">
            <canvas id="chartVendors"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="table-toolbar">
            <h3>Audit Exception Review Queue (<span id="tableCount">99</span> Records)</h3>
            <button class="export-btn" onclick="exportFilteredCSV()">Export Filtered CSV</button>
          </div>
          <div class="table-container">
            <table id="exceptionsTable">
              <thead>
                <tr>
                  <th>Txn ID</th>
                  <th>Date</th>
                  <th>Vendor</th>
                  <th style="text-align: right;">Amount (₹)</th>
                  <th>Department</th>
                  <th>Flag Reason</th>
                </tr>
              </thead>
              <tbody id="tableBody"></tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  </div>

  <script>
    const RAW_DATA = {json.dumps(records)};
    let activeRule = "ALL";
    let chartReasonsInst, chartDeptInst, chartMonthlyInst, chartVendorsInst;

    function selectRule(btn, rule) {{
      document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeRule = rule;
      applyFilters();
    }}

    function applyFilters() {{
      const dept = document.getElementById("deptSelect").value;
      const search = document.getElementById("searchFilter").value.toLowerCase().trim();
      const startDate = document.getElementById("dateStart").value;
      const endDate = document.getElementById("dateEnd").value;

      const filtered = RAW_DATA.filter(row => {{
        if (dept !== "ALL" && row.Department !== dept) return false;
        if (startDate && row.Date < startDate) return false;
        if (endDate && row.Date > endDate) return false;

        if (activeRule === "FLAGGED" && !row.is_flagged) return false;
        if (activeRule === "HIGH_VAL" && !row.high_value_flag) return false;
        if (activeRule === "WEEKEND" && !row.weekend_flag) return false;
        if (activeRule === "DUPLICATE" && !row.duplicate_flag) return false;

        if (search) {{
          const blob = `${{row.Transaction_ID}} ${{row.Vendor}} ${{row.Department}} ${{row.Employee_ID}} ${{row.flag_reason}}`.toLowerCase();
          if (!blob.includes(search)) return false;
        }}
        return true;
      }});

      updateKPIs(filtered);
      updateCharts(filtered);
      updateTable(filtered);
    }}

    function updateKPIs(data) {{
      const totalCount = data.length;
      const totalAmt = data.reduce((sum, r) => sum + r.Amount, 0);
      const flagged = data.filter(r => r.is_flagged);
      const flaggedCount = flagged.length;
      const flaggedAmt = flagged.reduce((sum, r) => sum + r.Amount, 0);
      const pct = totalCount > 0 ? (flaggedCount / totalCount) * 100 : 0;
      const spendPct = totalAmt > 0 ? (flaggedAmt / totalAmt) * 100 : 0;

      document.getElementById("kpiTotalTxns").textContent = totalCount.toLocaleString();
      document.getElementById("kpiTotalAmt").textContent = "₹" + (totalAmt / 100000).toFixed(2) + " L";
      document.getElementById("kpiTotalAmtExact").textContent = "₹" + totalAmt.toLocaleString(undefined, {{minimumFractionDigits: 2, maximumFractionDigits: 2}});

      document.getElementById("kpiFlaggedTxns").textContent = flaggedCount.toLocaleString();
      document.getElementById("kpiFlaggedPct").textContent = pct.toFixed(1) + "%";
      document.getElementById("kpiFlaggedSpend").textContent = "₹" + (flaggedAmt / 100000).toFixed(2) + " L (" + spendPct.toFixed(1) + "% of spend)";
      document.getElementById("headerStatus").textContent = flaggedCount + " EXCEPTIONS IN CURRENT VIEW";
    }}

    function updateCharts(data) {{
      // 1. Reasons
      const highVal = data.filter(r => r.high_value_flag).length;
      const weekend = data.filter(r => r.weekend_flag).length;
      const duplicate = data.filter(r => r.duplicate_flag).length;

      chartReasonsInst.data.datasets[0].data = [weekend, highVal, duplicate];
      chartReasonsInst.update();

      // 2. Department Spend
      const depts = ["Legal", "IT", "Operations", "Procurement", "Finance", "Marketing", "Human Resources", "Sales"];
      const totalByDept = depts.map(d => data.filter(r => r.Department === d).reduce((s, r) => s + r.Amount, 0) / 100000);
      const flaggedByDept = depts.map(d => data.filter(r => r.Department === d && r.is_flagged).reduce((s, r) => s + r.Amount, 0) / 100000);

      chartDeptInst.data.labels = depts;
      chartDeptInst.data.datasets[0].data = totalByDept;
      chartDeptInst.data.datasets[1].data = flaggedByDept;
      chartDeptInst.update();

      // 3. Monthly Trend
      const months = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08"];
      const mLabels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"];
      const monthlyTotal = months.map(m => data.filter(r => r.Date.startsWith(m)).reduce((s, r) => s + r.Amount, 0) / 100000);
      const monthlyFlagged = months.map(m => data.filter(r => r.Date.startsWith(m) && r.is_flagged).reduce((s, r) => s + r.Amount, 0) / 100000);

      chartMonthlyInst.data.labels = mLabels;
      chartMonthlyInst.data.datasets[0].data = monthlyTotal;
      chartMonthlyInst.data.datasets[1].data = monthlyFlagged;
      chartMonthlyInst.update();

      // 4. Top Vendors
      const vendorSpend = {{}};
      data.filter(r => r.is_flagged).forEach(r => {{
        vendorSpend[r.Vendor] = (vendorSpend[r.Vendor] || 0) + r.Amount;
      }});
      const sortedVendors = Object.entries(vendorSpend).sort((a, b) => b[1] - a[1]).slice(0, 10);
      chartVendorsInst.data.labels = sortedVendors.map(v => v[0]);
      chartVendorsInst.data.datasets[0].data = sortedVendors.map(v => v[1] / 100000);
      chartVendorsInst.update();
    }}

    function updateTable(data) {{
      const tbody = document.getElementById("tableBody");
      tbody.innerHTML = "";
      const displayData = data.filter(r => r.is_flagged).sort((a, b) => b.Amount - a.Amount);
      document.getElementById("tableCount").textContent = displayData.length;

      displayData.forEach(r => {{
        const isCompound = r.flag_reason.includes(";");
        const tr = document.createElement("tr");
        if (isCompound) tr.className = "compound";

        let badgeClass = "badge-primary";
        if (isCompound) badgeClass = "badge-danger";
        else if (r.flag_reason.includes("High")) badgeClass = "badge-danger";
        else if (r.flag_reason.includes("Duplicate")) badgeClass = "badge-warning";

        tr.innerHTML = `
          <td><b>${{r.Transaction_ID}}</b></td>
          <td>${{r.Date}}</td>
          <td>${{r.Vendor}}</td>
          <td style="text-align: right; font-weight: 700; color: #C00000;">₹${{r.Amount.toLocaleString(undefined, {{minimumFractionDigits: 2}})}}</td>
          <td>${{r.Department}}</td>
          <td><span class="badge ${{badgeClass}}">${{r.flag_reason}}</span></td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    function initCharts() {{
      // Reasons Bar
      chartReasonsInst = new Chart(document.getElementById("chartReasons"), {{
        type: 'bar',
        data: {{
          labels: ['Weekend', 'High Value', 'Duplicate'],
          datasets: [{{
            data: [51, 47, 24],
            backgroundColor: ['#2F5597', '#C00000', '#ED7D31'],
            borderRadius: 4
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{ y: {{ beginAtZero: true, grid: {{ color: '#F3F4F6' }} }} }}
        }}
      }});

      // Department Horizontal Bar
      chartDeptInst = new Chart(document.getElementById("chartDept"), {{
        type: 'bar',
        data: {{
          labels: [],
          datasets: [
            {{ label: 'Total Spend', data: [], backgroundColor: '#2F5597', borderRadius: 4 }},
            {{ label: 'Flagged Spend', data: [], backgroundColor: '#C00000', borderRadius: 4 }}
          ]
        }},
        options: {{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          scales: {{ x: {{ grid: {{ color: '#F3F4F6' }} }} }}
        }}
      }});

      // Monthly Line
      chartMonthlyInst = new Chart(document.getElementById("chartMonthly"), {{
        type: 'line',
        data: {{
          labels: [],
          datasets: [
            {{ label: 'Total Spend', data: [], borderColor: '#2F5597', tension: 0.2, fill: false }},
            {{ label: 'Flagged Spend', data: [], borderColor: '#C00000', backgroundColor: 'rgba(192, 0, 0, 0.1)', tension: 0.2, fill: true }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{ y: {{ grid: {{ color: '#F3F4F6' }} }} }}
        }}
      }});

      // Top Vendors Bar
      chartVendorsInst = new Chart(document.getElementById("chartVendors"), {{
        type: 'bar',
        data: {{
          labels: [],
          datasets: [{{ label: 'Flagged Spend (₹ L)', data: [], backgroundColor: '#ED7D31', borderRadius: 4 }}]
        }},
        options: {{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{ x: {{ grid: {{ color: '#F3F4F6' }} }} }}
        }}
      }});
    }}

    function exportFilteredCSV() {{
      const dept = document.getElementById("deptSelect").value;
      const search = document.getElementById("searchFilter").value.toLowerCase().trim();
      const startDate = document.getElementById("dateStart").value;
      const endDate = document.getElementById("dateEnd").value;

      const filtered = RAW_DATA.filter(row => {{
        if (!row.is_flagged) return false;
        if (dept !== "ALL" && row.Department !== dept) return false;
        if (startDate && row.Date < startDate) return false;
        if (endDate && row.Date > endDate) return false;
        if (search) {{
          const blob = `${{row.Transaction_ID}} ${{row.Vendor}} ${{row.Department}} ${{row.Employee_ID}} ${{row.flag_reason}}`.toLowerCase();
          if (!blob.includes(search)) return false;
        }}
        return true;
      }});

      let csv = "Transaction_ID,Date,Department,Employee_ID,Vendor,Amount,Payment_Method,Flag_Reason\\n";
      filtered.forEach(r => {{
        csv += `"${{r.Transaction_ID}}","${{r.Date}}","${{r.Department}}","${{r.Employee_ID}}","${{r.Vendor}}",${{r.Amount}},"${{r.Payment_Method}}","${{r.flag_reason}}"\\n`;
      }});

      const blob = new Blob([csv], {{ type: "text/csv;charset=utf-8;" }});
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "audit_exceptions_export.csv";
      link.click();
    }}

    window.onload = function() {{
      initCharts();
      applyFilters();
    }};
  </script>
</body>
</html>
"""

    out_file = os.path.join("dashboard", "interactive_dashboard.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Interactive web dashboard generated at: {out_file}")

if __name__ == "__main__":
    build_interactive_html()
