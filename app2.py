
import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
from datetime import datetime
from io import BytesIO

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Project EAGLE EYE",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ PROJECT EAGLE EYE")
st.subheader("Electrical Control Cabinet Quality Inspection")
st.caption("Member 4 | Streamlit Interface & Report Generation")

# ---------------- DEFAULT ELECTRICAL QC CHECKLIST ----------------
DEFAULT_CHECKS = [
    {
        "Check ID": "EC-01",
        "Inspection Item": "Component Presence",
        "Expected Result": "Components match approved BOM/drawing",
        "Status": "REVIEW",
        "Observed Result": "Pending inspection",
        "Remarks": ""
    },
    {
        "Check ID": "EC-02",
        "Inspection Item": "Component Placement",
        "Expected Result": "Positions match approved layout drawing",
        "Status": "REVIEW",
        "Observed Result": "Pending inspection",
        "Remarks": ""
    },
    {
        "Check ID": "EC-03",
        "Inspection Item": "Device Labels",
        "Expected Result": "Labels match approved device schedule",
        "Status": "REVIEW",
        "Observed Result": "Pending inspection",
        "Remarks": "Verify actual project labels"
    },
    {
        "Check ID": "EC-04",
        "Inspection Item": "Wire Identification",
        "Expected Result": "Wire markers and ferrules are legible where required",
        "Status": "REVIEW",
        "Observed Result": "Pending inspection",
        "Remarks": ""
    },
    {
        "Check ID": "EC-05",
        "Inspection Item": "Terminal Connections",
        "Expected Result": "Visible connections agree with approved wiring documents",
        "Status": "REVIEW",
        "Observed Result": "Pending inspection",
        "Remarks": "Visual check only"
    },
    {
        "Check ID": "EC-06",
        "Inspection Item": "Wire Routing",
        "Expected Result": "Routing and segregation follow project requirements",
        "Status": "REVIEW",
        "Observed Result": "Pending inspection",
        "Remarks": ""
    },
    {
        "Check ID": "EC-07",
        "Inspection Item": "Visible Component Condition",
        "Expected Result": "No obvious visible damage or contamination",
        "Status": "REVIEW",
        "Observed Result": "Pending inspection",
        "Remarks": ""
    },
    {
        "Check ID": "EC-08",
        "Inspection Item": "Drawing Verification",
        "Expected Result": "Latest approved drawing and revision are used",
        "Status": "REVIEW",
        "Observed Result": "Pending verification",
        "Remarks": ""
    }
]

# ---------------- SIDEBAR: INSPECTION DETAILS ----------------
with st.sidebar:
    st.header("Inspection Details")
    project_name = st.text_input(
        "Project Name", "Project EAGLE EYE"
    )
    panel_id = st.text_input(
        "Cabinet / Panel ID", "PANEL-001"
    )
    inspector = st.text_input("Inspector Name")
    drawing_no = st.text_input("Drawing Number")
    drawing_revision = st.text_input("Drawing Revision")
    inspection_date = st.date_input(
        "Inspection Date", datetime.now().date()
    )
    notes = st.text_area("General Notes")

# ---------------- TABS ----------------
tab_upload, tab_checklist, tab_reports, tab_status = st.tabs([
    "📤 Upload Files",
    "📋 QC Checklist",
    "📄 Reports",
    "🔌 Integration"
])

# ---------------- FILE UPLOAD ----------------
with tab_upload:
    st.header("Upload Cabinet Inspection Files")

    uploaded_files = st.file_uploader(
        "Upload cabinet photos, drawings, or spreadsheets",
        type=["png", "jpg", "jpeg", "pdf", "xlsx", "xls", "csv"],
        accept_multiple_files=True
    )

    report_images = []

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded.")

        for file in uploaded_files:
            extension = Path(file.name).suffix.lower()

            with st.expander(file.name):
                if extension in [".png", ".jpg", ".jpeg"]:
                    try:
                        image = Image.open(file).convert("RGB")
                        st.image(
                            image,
                            caption=file.name,
                            use_container_width=True
                        )
                        report_images.append(
                            (file.name, image.copy())
                        )
                    except Exception as error:
                        st.error(f"Image error: {error}")

                elif extension == ".pdf":
                    st.info(
                        "PDF uploaded. Automatic drawing extraction "
                        "is not implemented in this version."
                    )

                elif extension in [".xlsx", ".xls", ".csv"]:
                    try:
                        file.seek(0)
                        if extension == ".csv":
                            table = pd.read_csv(file)
                        else:
                            table = pd.read_excel(file)

                        st.dataframe(
                            table.head(20),
                            use_container_width=True
                        )
                    except Exception as error:
                        st.warning(
                            f"Could not preview spreadsheet: {error}"
                        )

    st.info(
        "Uploads are currently previewed only. Automatic OCR and "
        "defect detection require the team's inspection modules."
    )

# ---------------- QC CHECKLIST ----------------
with tab_checklist:
    st.header("Electrical Cabinet QC Checklist")

    if "qc_data" not in st.session_state:
        st.session_state.qc_data = pd.DataFrame(DEFAULT_CHECKS)

    if st.button("Reset Checklist"):
        st.session_state.qc_data = pd.DataFrame(DEFAULT_CHECKS)
        st.rerun()

    edited_df = st.data_editor(
        st.session_state.qc_data,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="qc_editor",
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["REVIEW", "PASS", "FAIL"],
                required=True
            )
        }
    )

    st.session_state.qc_data = edited_df

    # Normalize status values before reports and counts
    report_df = edited_df.copy()
    report_df["Status"] = (
        report_df["Status"]
        .fillna("REVIEW")
        .astype(str)
        .str.upper()
    )
    report_df.loc[
        ~report_df["Status"].isin(["REVIEW", "PASS", "FAIL"]),
        "Status"
    ] = "REVIEW"

    total = len(report_df)
    passed = int((report_df["Status"] == "PASS").sum())
    failed = int((report_df["Status"] == "FAIL").sum())
    review = int((report_df["Status"] == "REVIEW").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Checks", total)
    c2.metric("PASS", passed)
    c3.metric("FAIL", failed)
    c4.metric("REVIEW", review)

    if failed:
        st.error(
            f"{failed} item(s) marked FAIL. "
            "Record corrective actions before approval."
        )
    elif review:
        st.warning(
            f"{review} item(s) still require verification."
        )
    else:
        st.success(
            "All checklist entries are marked PASS. "
            "Required electrical tests and formal approval "
            "must still be completed separately."
        )

# ---------------- REPORT GENERATION ----------------
with tab_reports:
    st.header("Generate Inspection Reports")

    report_df = st.session_state.get(
        "qc_data", pd.DataFrame(DEFAULT_CHECKS)
    ).copy()

    report_df["Status"] = (
        report_df["Status"]
        .fillna("REVIEW")
        .astype(str)
        .str.upper()
    )
    report_df.loc[
        ~report_df["Status"].isin(["REVIEW", "PASS", "FAIL"]),
        "Status"
    ] = "REVIEW"

    metadata = {
        "Project": project_name,
        "Cabinet / Panel ID": panel_id,
        "Inspection Date": str(inspection_date),
        "Inspector": inspector or "Not provided",
        "Drawing Number": drawing_no or "Not provided",
        "Drawing Revision": drawing_revision or "Not provided",
        "Generated At": datetime.now().strftime("%d %b %Y, %H:%M"),
        "General Notes": notes or "None"
    }

    # -------- EXCEL EXPORT --------
    excel_buffer = BytesIO()

    summary_rows = [
        {"Field": key, "Value": value}
        for key, value in metadata.items()
    ]
    summary_rows.extend([
        {"Field": "Total Checks", "Value": str(len(report_df))},
        {"Field": "PASS", "Value": str(
            (report_df["Status"] == "PASS").sum()
        )},
        {"Field": "FAIL", "Value": str(
            (report_df["Status"] == "FAIL").sum()
        )},
        {"Field": "REVIEW", "Value": str(
            (report_df["Status"] == "REVIEW").sum()
        )}
    ])

    with pd.ExcelWriter(
        excel_buffer, engine="openpyxl"
    ) as writer:
        pd.DataFrame(summary_rows).to_excel(
            writer, sheet_name="Summary", index=False
        )
        report_df.to_excel(
            writer, sheet_name="QC Checklist", index=False
        )

        for sheet in writer.sheets.values():
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions
            for cells in sheet.columns:
                width = max(
                    len(str(cell.value))
                    if cell.value is not None else 0
                    for cell in cells
                )
                sheet.column_dimensions[
                    cells[0].column_letter
                ].width = min(max(width + 2, 12), 50)

    st.download_button(
        "⬇️ Download Excel QC Report",
        data=excel_buffer.getvalue(),
        file_name=f"{panel_id}_Electrical_QC_Report.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )

    # -------- PDF EXPORT --------
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, PageBreak, Image as PDFImage
        )

        pdf_buffer = BytesIO()

        document = SimpleDocTemplate(
            pdf_buffer,
            pagesize=landscape(A4),
            rightMargin=10 * mm,
            leftMargin=10 * mm,
            topMargin=10 * mm,
            bottomMargin=10 * mm
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="SmallCell",
            parent=styles["BodyText"],
            fontSize=7,
            leading=9
        ))

        story = [
            Paragraph(
                "<b>PROJECT EAGLE EYE</b>",
                styles["Title"]
            ),
            Paragraph(
                "Electrical Control Cabinet QC Report",
                styles["Heading2"]
            ),
            Spacer(1, 5 * mm)
        ]

        metadata_rows = [
            ["Field", "Value"]
        ]
        for key, value in metadata.items():
            metadata_rows.append([key, value])

        meta_table = Table(
            metadata_rows,
            colWidths=[45 * mm, 115 * mm]
        )
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#DCE6F1")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP")
        ]))
        story.extend([meta_table, Spacer(1, 5 * mm)])

        story.append(Paragraph(
            f"Total Checks: {len(report_df)} | "
            f"PASS: {(report_df['Status'] == 'PASS').sum()} | "
            f"FAIL: {(report_df['Status'] == 'FAIL').sum()} | "
            f"REVIEW: {(report_df['Status'] == 'REVIEW').sum()}",
            styles["BodyText"]
        ))
        story.append(Spacer(1, 4 * mm))

        columns = [
            "Check ID", "Inspection Item", "Expected Result",
            "Status", "Observed Result", "Remarks"
        ]

        table_rows = [[
            Paragraph(f"<b>{column}</b>", styles["SmallCell"])
            for column in columns
        ]]

        for _, row in report_df.iterrows():
            table_rows.append([
                Paragraph(
                    str(row.get(column, "")).replace("&", "&amp;"),
                    styles["SmallCell"]
                )
                for column in columns
            ])

        qc_table = Table(
            table_rows,
            colWidths=[
                18 * mm, 39 * mm, 57 * mm,
                20 * mm, 48 * mm, 55 * mm
            ],
            repeatRows=1
        )

        table_style = [
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#17365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP")
        ]

        for index, status in enumerate(
            report_df["Status"], start=1
        ):
            if status == "PASS":
                fill = colors.HexColor("#D9EAD3")
            elif status == "FAIL":
                fill = colors.HexColor("#F4CCCC")
            else:
                fill = colors.HexColor("#FFF2CC")

            table_style.append((
                "BACKGROUND", (3, index), (3, index), fill
            ))

        qc_table.setStyle(TableStyle(table_style))
        story.append(qc_table)

        if uploaded_files:
            story.append(PageBreak())
            story.append(Paragraph(
                "Uploaded Inspection Photos",
                styles["Heading2"]
            ))

            for file in uploaded_files:
                if Path(file.name).suffix.lower() in [
                    ".png", ".jpg", ".jpeg"
                ]:
                    try:
                        file.seek(0)
                        image = Image.open(file).convert("RGB")
                        image_buffer = BytesIO()
                        image.save(image_buffer, format="JPEG")
                        image_buffer.seek(0)

                        story.append(Paragraph(
                            file.name, styles["BodyText"]
                        ))
                        story.append(Spacer(1, 2 * mm))
                        story.append(PDFImage(
                            image_buffer,
                            width=110 * mm,
                            height=68 * mm
                        ))
                        story.append(Spacer(1, 5 * mm))
                    except Exception:
                        pass

        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph(
            "<b>Important:</b> REVIEW means not yet verified. "
            "This report does not certify electrical safety, "
            "terminal torque, continuity, insulation resistance, "
            "or tests requiring qualified personnel and instruments.",
            styles["SmallCell"]
        ))

        document.build(story)

        st.download_button(
            "⬇️ Download PDF QC Report",
            data=pdf_buffer.getvalue(),
            file_name=f"{panel_id}_Electrical_QC_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    except ImportError:
        st.error(
            "Install ReportLab using: pip install reportlab"
        )
    except Exception as error:
        st.error(f"PDF generation error: {error}")

# ---------------- TEAM MODULE INTEGRATION ----------------
with tab_status:
    st.header("Team Module Integration")

    st.markdown("""
    | Module | Responsibility | Status |
    |---|---|---|
    | `vision.py` | OCR, component/label detection, annotated images | Awaiting teammate |
    | `qc_engine.py` | Compare expected and detected values; assign QC status | Awaiting teammate |
    | `data_loader.py` | Load drawing/BOM/Excel/PDF expected data | Awaiting teammate |
    """)

    st.code(
        "Uploaded Files → data_loader.py → vision.py → "
        "qc_engine.py → Streamlit UI → PDF / Excel",
        language="text"
    )

    st.info(
        "This interface uses editable starter checklist data until "
        "the inspection modules are connected. Uploading a photo "
        "does not automatically detect defects in this version."
    )

st.divider()
st.caption(
    "Project EAGLE EYE | Electrical Cabinet QC | "
    "Visual inspection records do not replace formal electrical testing."
)