"""
Packages a Power BI archive structure (.pbix) containing the report layout,
metadata, diagrams, and settings for the Audit Transaction Exception Dashboard.
"""

import os
import zipfile
import json

def build_pbix():
    pbix_path = os.path.join("dashboard", "audit_exception_dashboard.pbix")

    # Layout JSON matching the report visuals
    report_layout = {
        "id": 0,
        "name": "Audit_Transaction_Exceptions",
        "title": "Audit Transaction Exception Dashboard",
        "resourcePackages": [],
        "sections": [
            {
                "id": 0,
                "name": "ReportSection_ExceptionsOverview",
                "displayName": "Audit Exception Overview",
                "filters": "[]",
                "ordinal": 0,
                "visualContainers": [
                    {
                        "x": 200, "y": 20, "z": 1000, "width": 220, "height": 110,
                        "config": json.dumps({
                            "name": "Card_TotalTransactions",
                            "layouts": [{"id": 0, "position": {"x": 200, "y": 20, "z": 1000, "width": 220, "height": 110}}],
                            "singleVisual": {
                                "visualType": "card",
                                "projections": {"Values": [{"queryRef": "Transactions.TotalTransactions"}]},
                                "title": "Total Transactions"
                            }
                        })
                    },
                    {
                        "x": 440, "y": 20, "z": 1001, "width": 220, "height": 110,
                        "config": json.dumps({
                            "name": "Card_TotalAmount",
                            "layouts": [{"id": 0, "position": {"x": 440, "y": 20, "z": 1001, "width": 220, "height": 110}}],
                            "singleVisual": {
                                "visualType": "card",
                                "projections": {"Values": [{"queryRef": "Transactions.TotalAmount"}]},
                                "title": "Total Transaction Amount"
                            }
                        })
                    },
                    {
                        "x": 680, "y": 20, "z": 1002, "width": 220, "height": 110,
                        "config": json.dumps({
                            "name": "Card_FlaggedCount",
                            "layouts": [{"id": 0, "position": {"x": 680, "y": 20, "z": 1002, "width": 220, "height": 110}}],
                            "singleVisual": {
                                "visualType": "card",
                                "projections": {"Values": [{"queryRef": "Transactions.FlaggedTransactions"}]},
                                "title": "Flagged Exceptions"
                            }
                        })
                    },
                    {
                        "x": 920, "y": 20, "z": 1003, "width": 220, "height": 110,
                        "config": json.dumps({
                            "name": "Card_FlaggedPct",
                            "layouts": [{"id": 0, "position": {"x": 920, "y": 20, "z": 1003, "width": 220, "height": 110}}],
                            "singleVisual": {
                                "visualType": "card",
                                "projections": {"Values": [{"queryRef": "Transactions.FlaggedPercentage"}]},
                                "title": "Flagged Percentage"
                            }
                        })
                    },
                    {
                        "x": 200, "y": 150, "z": 1004, "width": 300, "height": 320,
                        "config": json.dumps({
                            "name": "Chart_FlaggedByReason",
                            "singleVisual": {
                                "visualType": "columnChart",
                                "projections": {
                                    "Category": [{"queryRef": "Transactions.flag_reason"}],
                                    "Y": [{"queryRef": "Transactions.FlaggedTransactions"}]
                                },
                                "title": "Flagged Transactions by Flag Reason"
                            }
                        })
                    },
                    {
                        "x": 520, "y": 150, "z": 1005, "width": 360, "height": 320,
                        "config": json.dumps({
                            "name": "Chart_SpendByDept",
                            "singleVisual": {
                                "visualType": "barChart",
                                "projections": {
                                    "Category": [{"queryRef": "Transactions.Department"}],
                                    "Y": [{"queryRef": "Transactions.TotalAmount"}]
                                },
                                "title": "Transaction Amount by Department"
                            }
                        })
                    },
                    {
                        "x": 900, "y": 150, "z": 1006, "width": 320, "height": 320,
                        "config": json.dumps({
                            "name": "Chart_MonthlyTrend",
                            "singleVisual": {
                                "visualType": "lineChart",
                                "projections": {
                                    "Category": [{"queryRef": "Transactions.Month"}],
                                    "Y": [{"queryRef": "Transactions.TotalAmount"}]
                                },
                                "title": "Monthly Transaction Amount"
                            }
                        })
                    },
                    {
                        "x": 200, "y": 490, "z": 1007, "width": 360, "height": 340,
                        "config": json.dumps({
                            "name": "Chart_TopVendors",
                            "singleVisual": {
                                "visualType": "barChart",
                                "projections": {
                                    "Category": [{"queryRef": "Transactions.Vendor"}],
                                    "Y": [{"queryRef": "Transactions.FlaggedAmount"}]
                                },
                                "title": "Top 10 Flagged Vendors"
                            }
                        })
                    },
                    {
                        "x": 580, "y": 490, "z": 1008, "width": 640, "height": 340,
                        "config": json.dumps({
                            "name": "Table_Exceptions",
                            "singleVisual": {
                                "visualType": "tableEx",
                                "projections": {
                                    "Values": [
                                        {"queryRef": "Transactions.Transaction_ID"},
                                        {"queryRef": "Transactions.Date"},
                                        {"queryRef": "Transactions.Vendor"},
                                        {"queryRef": "Transactions.Amount"},
                                        {"queryRef": "Transactions.Department"},
                                        {"queryRef": "Transactions.flag_reason"}
                                    ]
                                },
                                "title": "Transaction Exception Detail"
                            }
                        })
                    },
                    {
                        "x": 20, "y": 20, "z": 1009, "width": 160, "height": 810,
                        "config": json.dumps({
                            "name": "Slicers_Panel",
                            "singleVisual": {
                                "visualType": "slicer",
                                "projections": {
                                    "Values": [{"queryRef": "Transactions.Department"}]
                                },
                                "title": "Department Slicer"
                            }
                        })
                    }
                ],
                "width": 1280,
                "height": 850
            }
        ]
    }

    content_types_xml = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="xml" ContentType="application/xml" />
  <Override PartName="/Report/Layout" ContentType="application/json" />
  <Override PartName="/Settings" ContentType="application/json" />
  <Override PartName="/Version" ContentType="application/json" />
</Types>"""

    version_info = "1.28"
    settings_json = {"useNewFilterPaneExperience": True, "allowChangeFilterTypes": True}

    with zipfile.ZipFile(pbix_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types_xml)
        z.writestr("Version", version_info)
        z.writestr("Settings", json.dumps(settings_json, indent=2))
        z.writestr("Report/Layout", json.dumps(report_layout, indent=2))

    print(f"Generated Power BI dashboard archive at: {pbix_path}")

if __name__ == "__main__":
    build_pbix()
