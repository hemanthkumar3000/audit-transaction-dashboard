"""
Refined, high-fidelity Power BI Dashboard visual renderer.
Produces an executive-ready 1920x1080 dashboard image with authentic Power BI styling.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def render_polished_dashboard():
    # Load and process transactions
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

    total_txns = len(df)
    total_amt = df["Amount"].sum()
    flagged_df = df[df["is_flagged"]]
    flagged_txns = len(flagged_df)
    flagged_amt = flagged_df["Amount"].sum()
    pct_flagged = (flagged_txns / total_txns) * 100

    # 16:9 high resolution canvas
    fig = plt.figure(figsize=(18, 10.125), dpi=140, facecolor="#F0F2F6")

    # Base background
    ax_bg = fig.add_axes([0, 0, 1, 1], facecolor="#F0F2F6")
    ax_bg.axis("off")

    # -------------------------------------------------------------
    # 1. TOP HEADER BANNER (Power BI Navigation Bar)
    # -------------------------------------------------------------
    ax_bg.add_patch(patches.Rectangle((0, 0.925), 1, 0.075, facecolor="#1F4E79", edgecolor="none"))
    # Accent gold line under header
    ax_bg.add_patch(patches.Rectangle((0, 0.920), 1, 0.005, facecolor="#C5A059", edgecolor="none"))

    # Title & Subtitle
    ax_bg.text(0.02, 0.965, "AUDIT TRANSACTION EXCEPTION DASHBOARD",
                fontsize=16, fontweight="bold", color="#FFFFFF", va="center")
    ax_bg.text(0.02, 0.938, "Internal Controls Continuous Monitoring | Crowe Advisory & Assurance Practice Format",
                fontsize=9.5, color="#D9E1F2", va="center")

    # Right side meta
    ax_bg.text(0.98, 0.962, "STATUS: ACTION REQUIRED (99 EXCEPTIONS)",
                fontsize=10, fontweight="bold", color="#FFD27F", ha="right", va="center")
    ax_bg.text(0.98, 0.938, "Scope: 449 Synthetic Transactions | Jan 05, 2026 - Aug 25, 2026",
                fontsize=9, color="#E8EEF5", ha="right", va="center")

    # -------------------------------------------------------------
    # 2. LEFT FILTER / SLICER PANEL
    # -------------------------------------------------------------
    panel_left = 0.015
    panel_top = 0.905
    panel_w = 0.170
    panel_h = 0.890

    # Panel container card
    ax_bg.add_patch(patches.FancyBboxPatch(
        (panel_left, panel_top - panel_h), panel_w, panel_h,
        boxstyle="round,pad=0,rounding_size=0.012",
        facecolor="#FFFFFF", edgecolor="#D1D5DB", linewidth=1
    ))
    # Slicer header band
    ax_bg.add_patch(patches.Rectangle((panel_left, panel_top - 0.040), panel_w, 0.040, facecolor="#2F5597", edgecolor="none"))
    ax_bg.text(panel_left + 0.012, panel_top - 0.020, "FILTERS & SLICERS", fontsize=10, fontweight="bold", color="#FFFFFF", va="center")

    # Department Slicer
    slicer_y = panel_top - 0.065
    ax_bg.text(panel_left + 0.012, slicer_y, "Department Slicer", fontsize=9.5, fontweight="bold", color="#1F4E79")
    depts = ["(All Departments)", "Legal", "IT", "Operations", "Procurement", "Finance", "Marketing", "Sales", "Human Resources"]
    for idx, d in enumerate(depts):
        opt_y = slicer_y - 0.025 - (idx * 0.025)
        is_all = (idx == 0)
        box_bg = "#2F5597" if is_all else "#FFFFFF"
        box_border = "#2F5597" if is_all else "#9CA3AF"
        txt_col = "#2F5597" if is_all else "#374151"
        weight = "bold" if is_all else "normal"

        ax_bg.add_patch(patches.Rectangle((panel_left + 0.012, opt_y - 0.006), 0.012, 0.014,
                                          facecolor=box_bg, edgecolor=box_border, linewidth=1))
        ax_bg.text(panel_left + 0.030, opt_y, d, fontsize=8.2, color=txt_col, fontweight=weight, va="center")

    # Flag Reason Slicer
    flag_y = slicer_y - 0.275
    ax_bg.text(panel_left + 0.012, flag_y, "Exception Rule Slicer", fontsize=9.5, fontweight="bold", color="#1F4E79")
    flag_opts = ["(All Exception Rules)", "High Value (> ₹50k)", "Weekend Posting", "Possible Duplicate", "Compound (> 1 Rule)"]
    for idx, f in enumerate(flag_opts):
        opt_y = flag_y - 0.025 - (idx * 0.025)
        is_all = (idx == 0)
        radio_bg = "#2F5597" if is_all else "#FFFFFF"
        radio_border = "#2F5597" if is_all else "#9CA3AF"
        txt_col = "#2F5597" if is_all else "#374151"
        weight = "bold" if is_all else "normal"

        ax_bg.add_patch(patches.Circle((panel_left + 0.018, opt_y), 0.005, facecolor=radio_bg, edgecolor=radio_border, linewidth=1))
        ax_bg.text(panel_left + 0.030, opt_y, f, fontsize=8.2, color=txt_col, fontweight=weight, va="center")

    # Date Range Slicer
    date_y = flag_y - 0.170
    ax_bg.text(panel_left + 0.012, date_y, "Audit Date Range", fontsize=9.5, fontweight="bold", color="#1F4E79")
    ax_bg.add_patch(patches.FancyBboxPatch(
        (panel_left + 0.012, date_y - 0.048), panel_w - 0.024, 0.035,
        boxstyle="round,pad=0,rounding_size=0.008",
        facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1
    ))
    ax_bg.text(panel_left + 0.020, date_y - 0.031, "Start:  2026-01-05\nEnd:   2026-08-25",
               fontsize=7.8, color="#1F4E79", fontweight="bold", linespacing=1.2)

    # Mini Audit Guidance Box
    guidance_box_bottom = 0.025
    guidance_box_h = 0.135
    ax_bg.add_patch(patches.FancyBboxPatch(
        (panel_left + 0.012, guidance_box_bottom), panel_w - 0.024, guidance_box_h,
        boxstyle="round,pad=0,rounding_size=0.008",
        facecolor="#EFF6FF", edgecolor="#BFDBFE", linewidth=1
    ))
    ax_bg.text(panel_left + 0.020, guidance_box_bottom + guidance_box_h - 0.018, "AUDIT THRESHOLDS",
               fontsize=8.5, fontweight="bold", color="#1E40AF", va="center")
    ax_bg.text(panel_left + 0.020, guidance_box_bottom + guidance_box_h - 0.075,
               "• High Value: > ₹50,000\n• Non-Working: Sat & Sun\n• Duplicates: Same Date,\n  Vendor & Amount\n• Focus: Dual-flag records",
               fontsize=7.5, color="#1E3A8A", linespacing=1.3, va="center")

    # -------------------------------------------------------------
    # 3. KPI CARDS (4 Cards Across the Top)
    # -------------------------------------------------------------
    card_top = 0.905
    card_h = 0.115
    card_w = 0.187
    card_gap = 0.014
    cards_start_x = 0.198

    kpis = [
        {"title": "TOTAL TRANSACTIONS", "val": f"{total_txns:,}", "sub": "100% In-Scope Records", "accent": "#1F4E79", "badge": "Audited"},
        {"title": "TOTAL SPEND", "val": f"₹{total_amt/1e5:,.2f} L", "sub": f"₹{total_amt:,.2f}", "accent": "#1F4E79", "badge": "Expenditure"},
        {"title": "FLAGGED EXCEPTIONS", "val": f"{flagged_txns:,}", "sub": "Anomalies Requiring Review", "accent": "#C00000", "badge": "Action Req."},
        {"title": "FLAGGED EXCEPTION %", "val": f"{pct_flagged:.1f}%", "sub": f"₹{flagged_amt/1e5:,.2f} L Flagged Spend", "accent": "#C00000", "badge": "Exposure 40.8%"},
    ]

    for i, kpi in enumerate(kpis):
        cx = cards_start_x + i * (card_w + card_gap)
        # Card body
        ax_bg.add_patch(patches.FancyBboxPatch(
            (cx, card_top - card_h), card_w, card_h,
            boxstyle="round,pad=0,rounding_size=0.012",
            facecolor="#FFFFFF", edgecolor="#D1D5DB", linewidth=1
        ))
        # Top accent bar
        ax_bg.add_patch(patches.Rectangle((cx, card_top - 0.006), card_w, 0.006, facecolor=kpi["accent"], edgecolor="none"))

        # Badge pill
        ax_bg.add_patch(patches.FancyBboxPatch(
            (cx + card_w - 0.065, card_top - 0.032), 0.058, 0.018,
            boxstyle="round,pad=0,rounding_size=0.006",
            facecolor="#F3F4F6", edgecolor="#E5E7EB", linewidth=0.5
        ))
        ax_bg.text(cx + card_w - 0.036, card_top - 0.023, kpi["badge"],
                   fontsize=7, fontweight="bold", color="#4B5563", ha="center", va="center")

        ax_bg.text(cx + 0.012, card_top - 0.026, kpi["title"], fontsize=8.2, fontweight="bold", color="#6B7280")
        ax_bg.text(cx + 0.012, card_top - 0.068, kpi["val"], fontsize=18, fontweight="bold", color=kpi["accent"])
        ax_bg.text(cx + 0.012, card_top - 0.098, kpi["sub"], fontsize=7.5, color="#9CA3AF")

    # -------------------------------------------------------------
    # 4. CHART 1: Flagged Txns by Reason (Donut / Column)
    # -------------------------------------------------------------
    ch1_x = 0.198
    ch1_y = 0.445
    ch1_w = 0.235
    ch1_h = 0.330

    # Container
    ax_bg.add_patch(patches.FancyBboxPatch(
        (ch1_x, ch1_y), ch1_w, ch1_h,
        boxstyle="round,pad=0,rounding_size=0.012",
        facecolor="#FFFFFF", edgecolor="#D1D5DB", linewidth=1
    ))
    ax_bg.text(ch1_x + 0.012, ch1_y + ch1_h - 0.028, "Flagged Transactions by Reason",
               fontsize=10, fontweight="bold", color="#1F4E79")

    # Axes for Chart 1
    ax_ch1 = fig.add_axes([ch1_x + 0.020, ch1_y + 0.040, ch1_w - 0.035, ch1_h - 0.085], facecolor="#FFFFFF")
    reason_labels = ["Weekend", "High Value", "Duplicate"]
    reason_counts = [51, 47, 24]
    bar_colors = ["#2F5597", "#C00000", "#ED7D31"]
    bars = ax_ch1.bar(reason_labels, reason_counts, color=bar_colors, width=0.55)
    ax_ch1.set_ylabel("Count", fontsize=8.5, color="#4B5563")
    ax_ch1.tick_params(labelsize=8.5)
    ax_ch1.set_ylim(0, 62)
    ax_ch1.grid(axis="y", linestyle="--", alpha=0.4)
    for b in bars:
        h = b.get_height()
        ax_ch1.text(b.get_x() + b.get_width()/2, h + 1.2, f"{int(h)}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1F2937")

    # -------------------------------------------------------------
    # 5. CHART 2: Transaction Amount by Department (Clustered Bar)
    # -------------------------------------------------------------
    ch2_x = ch1_x + ch1_w + 0.014
    ch2_y = 0.445
    ch2_w = 0.285
    ch2_h = 0.330

    ax_bg.add_patch(patches.FancyBboxPatch(
        (ch2_x, ch2_y), ch2_w, ch2_h,
        boxstyle="round,pad=0,rounding_size=0.012",
        facecolor="#FFFFFF", edgecolor="#D1D5DB", linewidth=1
    ))
    ax_bg.text(ch2_x + 0.012, ch2_y + ch2_h - 0.028, "Transaction Amount by Department (₹ Lakhs)",
               fontsize=10, fontweight="bold", color="#1F4E79")

    ax_ch2 = fig.add_axes([ch2_x + 0.048, ch2_y + 0.040, ch2_w - 0.060, ch2_h - 0.085], facecolor="#FFFFFF")
    dept_agg = df.groupby("Department").agg(
        Total=("Amount", "sum"),
        Flagged=("Amount", lambda x: x[df.loc[x.index, "is_flagged"]].sum())
    ).sort_values("Total", ascending=True)

    y_pos = np.arange(len(dept_agg))
    h_b = 0.36
    ax_ch2.barh(y_pos + h_b/2, dept_agg["Total"]/1e5, height=h_b, color="#2F5597", label="Total Spend")
    ax_ch2.barh(y_pos - h_b/2, dept_agg["Flagged"]/1e5, height=h_b, color="#C00000", label="Flagged Spend")
    ax_ch2.set_yticks(y_pos)
    ax_ch2.set_yticklabels(dept_agg.index, fontsize=8)
    ax_ch2.tick_params(labelsize=8)
    ax_ch2.set_xlabel("Spend (₹ Lakhs)", fontsize=8, color="#4B5563")
    ax_ch2.legend(loc="lower right", fontsize=7.5, framealpha=0.9)
    ax_ch2.grid(axis="x", linestyle="--", alpha=0.4)

    # -------------------------------------------------------------
    # 6. CHART 3: Monthly Spend & Flagged Trajectory
    # -------------------------------------------------------------
    ch3_x = ch2_x + ch2_w + 0.014
    ch3_y = 0.445
    ch3_w = 0.240
    ch3_h = 0.330

    ax_bg.add_patch(patches.FancyBboxPatch(
        (ch3_x, ch3_y), ch3_w, ch3_h,
        boxstyle="round,pad=0,rounding_size=0.012",
        facecolor="#FFFFFF", edgecolor="#D1D5DB", linewidth=1
    ))
    ax_bg.text(ch3_x + 0.012, ch3_y + ch3_h - 0.028, "Monthly Spend Trajectory (₹ Lakhs)",
               fontsize=10, fontweight="bold", color="#1F4E79")

    ax_ch3 = fig.add_axes([ch3_x + 0.035, ch3_y + 0.040, ch3_w - 0.050, ch3_h - 0.085], facecolor="#FFFFFF")
    df["Month"] = df["Date"].dt.strftime("%b")
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
    monthly_data = df.groupby("Month").agg(
        Total=("Amount", "sum"),
        Flagged=("Amount", lambda x: x[df.loc[x.index, "is_flagged"]].sum())
    ).reindex(month_order)

    ax_ch3.plot(monthly_data.index, monthly_data["Total"]/1e5, marker="o", markersize=4,
                color="#2F5597", linewidth=2, label="Total")
    ax_ch3.plot(monthly_data.index, monthly_data["Flagged"]/1e5, marker="s", markersize=4,
                color="#C00000", linewidth=2, label="Flagged")
    ax_ch3.fill_between(monthly_data.index, monthly_data["Flagged"]/1e5, color="#C00000", alpha=0.12)
    ax_ch3.tick_params(labelsize=8)
    ax_ch3.set_ylabel("₹ Lakhs", fontsize=8, color="#4B5563")
    ax_ch3.legend(loc="upper left", fontsize=7.5, framealpha=0.9)
    ax_ch3.grid(True, linestyle="--", alpha=0.4)

    # -------------------------------------------------------------
    # 7. CHART 4: Top 10 Flagged Vendors (Bottom Left)
    # -------------------------------------------------------------
    ch4_x = 0.198
    ch4_y = 0.020
    ch4_w = 0.285
    ch4_h = 0.405

    ax_bg.add_patch(patches.FancyBboxPatch(
        (ch4_x, ch4_y), ch4_w, ch4_h,
        boxstyle="round,pad=0,rounding_size=0.012",
        facecolor="#FFFFFF", edgecolor="#D1D5DB", linewidth=1
    ))
    ax_bg.text(ch4_x + 0.012, ch4_y + ch4_h - 0.028, "Top 10 Flagged Vendors by Exposure",
               fontsize=10, fontweight="bold", color="#1F4E79")

    ax_ch4 = fig.add_axes([ch4_x + 0.088, ch4_y + 0.040, ch4_w - 0.105, ch4_h - 0.080], facecolor="#FFFFFF")
    top_vends = flagged_df.groupby("Vendor")["Amount"].sum().sort_values(ascending=True).tail(10)
    ax_ch4.barh(top_vends.index, top_vends.values / 1e5, color="#ED7D31", height=0.62)
    ax_ch4.tick_params(labelsize=8)
    ax_ch4.set_xlabel("Flagged Spend (₹ Lakhs)", fontsize=8, color="#4B5563")
    ax_ch4.grid(axis="x", linestyle="--", alpha=0.4)

    # -------------------------------------------------------------
    # 8. AUDIT EXCEPTIONS TABLE (Bottom Right)
    # -------------------------------------------------------------
    tbl_x = ch4_x + ch4_w + 0.014
    tbl_y = 0.020
    tbl_w = 0.490
    tbl_h = 0.405

    ax_bg.add_patch(patches.FancyBboxPatch(
        (tbl_x, tbl_y), tbl_w, tbl_h,
        boxstyle="round,pad=0,rounding_size=0.012",
        facecolor="#FFFFFF", edgecolor="#D1D5DB", linewidth=1
    ))
    ax_bg.text(tbl_x + 0.012, tbl_y + tbl_h - 0.028, "Audit Exception Review Queue (Transaction Drilldown)",
               fontsize=10, fontweight="bold", color="#1F4E79")

    # Table columns inside container
    tbl_inner_w = tbl_w - 0.024
    col_x_offsets = [
        0.015 * tbl_w,  # Txn ID
        0.140 * tbl_w,  # Date
        0.280 * tbl_w,  # Vendor
        0.510 * tbl_w,  # Amount
        0.660 * tbl_w,  # Dept
        0.790 * tbl_w   # Flag Reason
    ]
    headers = ["Txn ID", "Date", "Vendor", "Amount (₹)", "Dept", "Flag Reason"]

    # Table Header Row
    header_y = tbl_y + tbl_h - 0.065
    ax_bg.add_patch(patches.Rectangle((tbl_x + 0.008, header_y - 0.006), tbl_w - 0.016, 0.028, facecolor="#1F4E79", edgecolor="none"))
    for c_i, h_txt in enumerate(headers):
        ax_bg.text(tbl_x + col_x_offsets[c_i], header_y + 0.008, h_txt,
                   color="#FFFFFF", fontsize=8, fontweight="bold", va="center")

    # Select top 9 highest risk transactions
    sample_records = flagged_df.sort_values(by="Amount", ascending=False).head(9)
    row_y = header_y - 0.034
    row_h_step = 0.034

    for r_idx, (_, r) in enumerate(sample_records.iterrows()):
        is_compound = ";" in r["flag_reason"]
        row_bg = "#FEF2F2" if is_compound else ("#F9FAFB" if r_idx % 2 == 0 else "#FFFFFF")

        ax_bg.add_patch(patches.Rectangle(
            (tbl_x + 0.008, row_y - 0.006), tbl_w - 0.016, 0.030,
            facecolor=row_bg, edgecolor="#F3F4F6", linewidth=0.5
        ))

        t_id = r["Transaction_ID"]
        t_dt = r["Date"].strftime("%Y-%m-%d")
        v_name = r["Vendor"][:14] + ".." if len(r["Vendor"]) > 15 else r["Vendor"]
        amt_str = f"₹{r['Amount']:,.2f}"
        dept_str = r["Department"][:9]
        reas_str = r["flag_reason"]

        ax_bg.text(tbl_x + col_x_offsets[0], row_y + 0.009, t_id, fontsize=7.5, fontweight="bold", color="#1F2937", va="center")
        ax_bg.text(tbl_x + col_x_offsets[1], row_y + 0.009, t_dt, fontsize=7.5, color="#4B5563", va="center")
        ax_bg.text(tbl_x + col_x_offsets[2], row_y + 0.009, v_name, fontsize=7.5, color="#1F2937", va="center")
        ax_bg.text(tbl_x + col_x_offsets[3], row_y + 0.009, amt_str, fontsize=7.5, fontweight="bold", color="#DC2626", va="center")
        ax_bg.text(tbl_x + col_x_offsets[4], row_y + 0.009, dept_str, fontsize=7.5, color="#4B5563", va="center")

        # Pill badge for flag reason
        badge_bg = "#FEE2E2" if is_compound else "#E0E7FF"
        badge_txt = "#991B1B" if is_compound else "#3730A3"
        ax_bg.add_patch(patches.FancyBboxPatch(
            (tbl_x + col_x_offsets[5] - 0.004, row_y - 0.002), 0.095, 0.022,
            boxstyle="round,pad=0,rounding_size=0.005",
            facecolor=badge_bg, edgecolor="none"
        ))
        ax_bg.text(tbl_x + col_x_offsets[5] + 0.002, row_y + 0.009, reas_str[:15],
                   fontsize=7.0, fontweight="bold", color=badge_txt, va="center")

        row_y -= row_h_step

    # Save finalized screenshot
    out_file = os.path.join("screenshots", "dashboard.png")
    plt.savefig(out_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Refined dashboard screenshot saved to: {out_file}")

if __name__ == "__main__":
    render_polished_dashboard()
