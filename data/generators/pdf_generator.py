"""Multi-template PDF invoice generator using ReportLab."""

import os
from typing import List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from data.generators.schema import InvoiceLineItem


def create_invoice_pdf(
    file_path: str,
    template_name: str,
    vendor_name: str,
    invoice_number: str,
    invoice_date: str,
    po_reference: str | None,
    currency: str,
    line_items: List[InvoiceLineItem],
    subtotal: float,
    tax_amount: float,
    total_amount: float,
    remit_address: str = "123 Industrial Parkway, Sector 4, Chicago, IL 60601",
) -> None:
    """Renders a PDF invoice using one of 5 distinct visual templates."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    # Color palette choices per template
    if template_name == "minimal_modern":
        primary_color = colors.HexColor("#1A1A1A")
        accent_color = colors.HexColor("#737373")
        table_header_bg = colors.HexColor("#F5F5F5")
    elif template_name == "classic_boxed":
        primary_color = colors.HexColor("#1E3A8A")
        accent_color = colors.HexColor("#3B82F6")
        table_header_bg = colors.HexColor("#EFF6FF")
    elif template_name == "industrial_compact":
        primary_color = colors.HexColor("#14532D")
        accent_color = colors.HexColor("#16A34A")
        table_header_bg = colors.HexColor("#F0FDF4")
    elif template_name == "scan_fax":
        primary_color = colors.HexColor("#000000")
        accent_color = colors.HexColor("#333333")
        table_header_bg = colors.HexColor("#E5E5E5")
    else:  # standard_grid
        primary_color = colors.HexColor("#0F172A")
        accent_color = colors.HexColor("#0284C7")
        table_header_bg = colors.HexColor("#F1F5F9")

    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
    )
    subtitle_style = ParagraphStyle(
        "InvoiceSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=accent_color,
    )
    header_val_style = ParagraphStyle(
        "HeaderVal",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=primary_color,
    )
    cell_style = ParagraphStyle(
        "CellNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
    )
    cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
    )

    story = []

    # 1. Header Block
    po_display = po_reference if po_reference else "N/A (Pending)"
    header_data = [
        [
            Paragraph(f"<b>{vendor_name}</b>", title_style),
            Paragraph("<b>INVOICE</b>", title_style),
        ],
        [
            Paragraph(remit_address, subtitle_style),
            Paragraph(f"<b>Invoice #:</b> {invoice_number}", header_val_style),
        ],
        [
            Paragraph(
                "<b>Bill To:</b> Northwind Industrial Supply Co.<br/>"
                "100 Industrial Blvd, Suite 200, Chicago, IL 60607",
                subtitle_style,
            ),
            Paragraph(
                f"<b>Date:</b> {invoice_date}<br/>"
                f"<b>PO Ref:</b> {po_display}<br/>"
                f"<b>Currency:</b> {currency}",
                subtitle_style,
            ),
        ],
    ]
    header_table = Table(header_data, colWidths=[320, 220])
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 16))

    # 2. Line Items Table
    table_rows = [
        [
            Paragraph("<b>#</b>", cell_bold),
            Paragraph("<b>SKU</b>", cell_bold),
            Paragraph("<b>Description</b>", cell_bold),
            Paragraph("<b>Qty</b>", cell_bold),
            Paragraph(f"<b>Unit Price ({currency})</b>", cell_bold),
            Paragraph(f"<b>Total ({currency})</b>", cell_bold),
        ]
    ]

    for item in line_items:
        table_rows.append(
            [
                Paragraph(str(item.line_number), cell_style),
                Paragraph(item.sku, cell_style),
                Paragraph(item.description, cell_style),
                Paragraph(str(item.quantity), cell_style),
                Paragraph(f"{item.unit_price:.2f}", cell_style),
                Paragraph(f"{item.total:.2f}", cell_style),
            ]
        )

    item_table = Table(table_rows, colWidths=[30, 85, 205, 50, 85, 85])
    item_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), table_header_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), primary_color),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                ("ALIGN", (4, 0), (-1, 0), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(item_table)
    story.append(Spacer(1, 14))

    # 3. Totals Block
    totals_data = [
        ["Subtotal:", f"{currency} {subtotal:.2f}"],
        ["Tax (Est):", f"{currency} {tax_amount:.2f}"],
        ["Total Due:", f"{currency} {total_amount:.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[430, 110])
    totals_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, -2), "Helvetica"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, -1), (-1, -1), primary_color),
                ("LINEABOVE", (0, -1), (-1, -1), 1, primary_color),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(totals_table)

    # 4. Footer Note
    story.append(Spacer(1, 20))
    footer_text = (
        f"Payment Terms: Net 30. Remit payment to {vendor_name}. Thank you for your business."
    )
    story.append(Paragraph(footer_text, subtitle_style))

    doc.build(story)
