"""Seeded master generator for Northwind AP dataset.

Generates:
1. Vendor master with variants (250 vendors).
2. Messy ERP CSV dumps (Purchase Orders & Goods Receipts) with inconsistent date formats,
   trailing whitespace, renamed columns, and a Latin-1 encoded file.
3. 800 PDF invoices across 5 templates + 100 email-body invoices.
4. Labeled problem injections (duplicates, price variance, qty mismatch,
   missing PO, wrong vendor, currency).
5. Ground truth JSON annotations and locked 150-invoice test split.

Usage:
    python -m data.generators.generate_data --seed 42
"""

import argparse
import csv
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from data.generators.pdf_generator import create_invoice_pdf
from data.generators.schema import (
    GoodsReceipt,
    GoodsReceiptLineItem,
    InvoiceGroundTruth,
    InvoiceLineItem,
    MatchOutcome,
    POLineItem,
    ProblemType,
    PurchaseOrder,
    ResolutionCategory,
    VendorRecord,
)

# Product Catalog for realistic industrial supply items
PRODUCT_CATALOG = [
    ("FST-M8-50", "Hex Bolt M8x50 Grade 8.8 Zinc", 0.45),
    ("FST-M10-60", "Hex Bolt M10x60 Grade 10.9 Black", 0.85),
    ("NUT-M8-NYL", "Nylon Insert Lock Nut M8", 0.18),
    ("NUT-M10-HEX", "Standard Hex Nut M10 Class 8", 0.22),
    ("WSH-M8-FLT", "Flat Washer M8 Stainless Steel", 0.12),
    ("TOOL-DRL-05", "HSS Cobalt Drill Bit 5.0mm", 4.50),
    ("TOOL-END-12", "Carbide End Mill 4-Flute 12mm", 32.00),
    ("TOOL-TAP-M8", "Spiral Point Tap M8x1.25", 14.50),
    ("MRO-LUB-400", "Synthetic Industrial Bearing Grease 400g", 8.75),
    ("MRO-DEG-05L", "Heavy Duty Citrus Degreaser 5L", 24.50),
    ("MRO-WIP-100", "Lint-Free Industrial Shop Wipes (100pk)", 18.00),
    ("SAF-GLV-09", "Nitrile Coated Work Gloves Size L", 3.20),
    ("SAF-EYE-CLR", "Anti-Fog Safety Glasses Clear", 5.50),
    ("SAF-RES-N95", "Particulate Respirator N95 (20pk)", 28.00),
    ("PNEU-FTG-08", "Push-in Pneumatic Fitting 8mm Tube", 2.10),
    ("PNEU-TUB-50M", "Polyurethane Pneumatic Tubing 8mm 50m", 38.00),
    ("HYD-SEA-045", "Nitrile O-Ring Kit 450-Piece", 22.50),
    ("HYD-VLV-12", "High Pressure Ball Valve 1/2in NPT", 46.00),
]

BASE_VENDORS = [
    (
        "ACME Fasteners Inc.",
        "US-11223344",
        "Chicago, IL",
        "Net 30",
        ["Acme Fasteners", "ACME Corp - Fasteners Div"],
    ),
    (
        "Midwest Precision Tooling LLC",
        "US-22334455",
        "Detroit, MI",
        "Net 30",
        ["Midwest Precision", "MPT Tooling"],
    ),
    (
        "Vanguard Safety Gear Co.",
        "US-33445566",
        "Cleveland, OH",
        "Net 45",
        ["Vanguard Safety", "Vanguard Protective Gear"],
    ),
    (
        "Apex Industrial Lubricants",
        "US-44556677",
        "Indianapolis, IN",
        "Net 30",
        ["Apex Lubricants", "Apex Ind"],
    ),
    (
        "Titan Hydraulics Corp.",
        "US-55667788",
        "Milwaukee, WI",
        "Net 30",
        ["Titan Hydraulics", "Titan Fluid Power"],
    ),
    (
        "Global Pneumatics Supply",
        "US-66778899",
        "Minneapolis, MN",
        "Net 60",
        ["Global Pneumatics", "GPS Pneumatics"],
    ),
    (
        "Superior Bearing & Seal Inc.",
        "US-77889900",
        "Akron, OH",
        "Net 30",
        ["Superior Bearing", "Superior Seals"],
    ),
    (
        "Tri-State Industrial Hardware",
        "US-88990011",
        "Peoria, IL",
        "Net 30",
        ["Tri-State Hardware", "Tri-State Ind"],
    ),
    (
        "Frontier Cutting Tools",
        "US-99001122",
        "Rockford, IL",
        "Net 45",
        ["Frontier Tools", "Frontier Cutting"],
    ),
    (
        "Delta Abrasives Corp.",
        "US-10111213",
        "Cincinnati, OH",
        "Net 30",
        ["Delta Abrasives", "Delta Grinding"],
    ),
    (
        "Müller Precision Tooling GmbH",
        "DE-99887766",
        "Stuttgart, Germany",
        "Net 30",
        ["Muller Tooling", "Mueller Tooling GmbH"],
    ),
    (
        "Montréal Industrial Fittings",
        "CA-55443322",
        "Montréal, QC",
        "Net 30",
        ["Montreal Fittings", "Montreal Ind Fittings"],
    ),
]

TEMPLATES = [
    "standard_grid",
    "minimal_modern",
    "classic_boxed",
    "industrial_compact",
    "scan_fax",
]


def generate_vendors(rng: random.Random) -> List[VendorRecord]:
    """Generates 250 vendor records with canonical names and dirty variants."""
    vendors = []
    # Seed with base vendors (including Latin-1 vendor names)
    for i, (name, tax_id, addr, terms, variants) in enumerate(BASE_VENDORS):
        vendors.append(
            VendorRecord(
                vendor_id=f"VEND-{1000 + i}",
                canonical_name=name,
                tax_id=tax_id,
                address=addr,
                payment_terms=terms,
                currency="EUR" if "GmbH" in name else ("CAD" if "QC" in addr else "USD"),
                variants=variants,
            )
        )

    # Generate remaining vendors up to 250
    suffixes = ["Corp", "Inc.", "LLC", "Supplies", "Industries", "Manufacturing", "Distributors"]
    domains = [
        "Tooling",
        "Fasteners",
        "Metals",
        "Hardware",
        "Packaging",
        "Electrical",
        "Safety",
        "Valves",
        "Pumps",
        "Bearings",
    ]
    cities = [
        "Chicago, IL",
        "Gary, IN",
        "Kalamazoo, MI",
        "Toledo, OH",
        "Green Bay, WI",
        "Fort Wayne, IN",
        "Grand Rapids, MI",
    ]

    for i in range(len(BASE_VENDORS), 250):
        base_name = f"{rng.choice(domains)} {rng.choice(suffixes)} {i}"
        canonical = f"Northwind {base_name}"
        variants = [
            f"{base_name}",
            f"NW {base_name}",
            f"{canonical.upper()}",
        ]
        vendors.append(
            VendorRecord(
                vendor_id=f"VEND-{1000 + i}",
                canonical_name=canonical,
                tax_id=f"US-{rng.randint(10000000, 99999999)}",
                address=rng.choice(cities),
                payment_terms=rng.choice(["Net 30", "Net 45", "Net 60", "2/10 Net 30"]),
                currency="USD",
                variants=variants,
            )
        )
    return vendors


def generate_pos_and_receipts(
    vendors: List[VendorRecord], rng: random.Random, count: int = 900
) -> Tuple[List[PurchaseOrder], List[GoodsReceipt]]:
    """Generates synthetic Purchase Orders and corresponding dock Goods Receipts."""
    pos = []
    receipts = []
    base_date = datetime(2026, 7, 1)

    for i in range(count):
        po_num = f"PO-{10000 + i}"
        vendor = rng.choice(vendors)
        po_date = (base_date + timedelta(days=rng.randint(0, 75))).strftime("%Y-%m-%d")

        # 1 to 4 line items
        num_items = rng.randint(1, 4)
        selected_catalog = rng.sample(PRODUCT_CATALOG, num_items)
        po_items = []
        gr_items = []

        subtotal = 0.0
        for line_no, (sku, desc, unit_price) in enumerate(selected_catalog, 1):
            qty = rng.choice([20, 50, 100, 200, 500])
            line_total = round(qty * unit_price, 2)
            subtotal += line_total

            po_items.append(
                POLineItem(
                    line_number=line_no,
                    sku=sku,
                    description=desc,
                    quantity=qty,
                    unit_price=unit_price,
                    total=line_total,
                )
            )

            # Standard GR receives exact quantity 2 to 5 days after PO
            rec_date = (
                datetime.strptime(po_date, "%Y-%m-%d") + timedelta(days=rng.randint(2, 5))
            ).strftime("%Y-%m-%d")
            gr_items.append(
                GoodsReceiptLineItem(
                    line_number=line_no,
                    sku=sku,
                    quantity_received=qty,
                    received_date=rec_date,
                )
            )

        tax = round(subtotal * 0.06, 2)
        total = round(subtotal + tax, 2)

        po = PurchaseOrder(
            po_number=po_num,
            vendor_id=vendor.vendor_id,
            vendor_name=vendor.canonical_name,
            order_date=po_date,
            currency=vendor.currency,
            line_items=po_items,
            subtotal=round(subtotal, 2),
            tax=tax,
            total=total,
        )
        pos.append(po)

        gr = GoodsReceipt(
            receipt_id=f"GR-{20000 + i}",
            po_number=po_num,
            vendor_id=vendor.vendor_id,
            receipt_date=(datetime.strptime(po_date, "%Y-%m-%d") + timedelta(days=4)).strftime(
                "%Y-%m-%d"
            ),
            received_by=rng.choice(["Dock-1 (J. Miller)", "Dock-2 (T. Brooks)", "Receiving Bay 3"]),
            line_items=gr_items,
        )
        receipts.append(gr)

    return pos, receipts


def write_messy_csvs(
    vendors: List[VendorRecord],
    pos: List[PurchaseOrder],
    receipts: List[GoodsReceipt],
    output_dir: str,
) -> None:
    """Exports ERP tables with realistic legacy quirks: mixed dates, whitespaces,
    latin-1 encoding, renamed columns."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Vendor Master (Clean UTF-8 CSV)
    vendors_path = os.path.join(output_dir, "vendors.csv")
    with open(vendors_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["VENDOR_ID", "CANONICAL_NAME", "TAX_ID", "ADDRESS", "PAYMENT_TERMS", "CURRENCY"]
        )
        for v in vendors:
            # Trailing whitespace quirk on some records
            space = " " if int(v.vendor_id.split("-")[1]) % 5 == 0 else ""
            writer.writerow(
                [
                    v.vendor_id,
                    f"{v.canonical_name}{space}",
                    v.tax_id,
                    v.address,
                    v.payment_terms,
                    v.currency,
                ]
            )

    # 2. Legacy Vendor Directory (Latin-1 encoded with German & French accents)
    legacy_vendors_path = os.path.join(output_dir, "vendors_legacy_latin1.csv")
    with open(legacy_vendors_path, "w", newline="", encoding="latin-1", errors="replace") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "SUPPLIER_NAME", "TAX_NUM", "REMIT_CITY", "DEF_CURR"])
        for v in vendors:
            writer.writerow([v.vendor_id, v.canonical_name, v.tax_id, v.address, v.currency])

    # 3. Purchase Orders (Messy date formats: MM/DD/YYYY vs YYYY-MM-DD, renamed headers)
    pos_path = os.path.join(output_dir, "purchase_orders.csv")
    with open(pos_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "P_O_NUMBER",
                "VENDOR_ID",
                "ORDER_DATE",
                "CURRENCY",
                "SUBTOTAL",
                "TAX",
                "TOTAL_AMOUNT",
                "LINE_COUNT",
            ]
        )
        for po in pos:
            # Mixed date format quirk
            dt = datetime.strptime(po.order_date, "%Y-%m-%d")
            po_date_str = (
                dt.strftime("%m/%d/%Y")
                if int(po.po_number.split("-")[1]) % 2 == 0
                else po.order_date
            )
            writer.writerow(
                [
                    po.po_number,
                    po.vendor_id,
                    po_date_str,
                    po.currency,
                    po.subtotal,
                    po.tax,
                    po.total,
                    len(po.line_items),
                ]
            )

    # 4. PO Line Items
    po_lines_path = os.path.join(output_dir, "po_line_items.csv")
    with open(po_lines_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["PO_NUM", "LINE_NO", "SKU", "ITEM_DESC", "ORDER_QTY", "UNIT_PRICE", "LINE_TOTAL"]
        )
        for po in pos:
            for item in po.line_items:
                writer.writerow(
                    [
                        po.po_number,
                        item.line_number,
                        item.sku,
                        item.description,
                        item.quantity,
                        item.unit_price,
                        item.total,
                    ]
                )

    # 5. Goods Receipts (Inconsistent column naming: REC_ID, PO_REF, DOCK_DATE)
    receipts_path = os.path.join(output_dir, "goods_receipts.csv")
    with open(receipts_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["RECEIPT_NO", "PO_REFERENCE", "VENDOR_ID", "DOCK_DATE", "RECEIVING_AGENT"])
        for gr in receipts:
            # Mixed date formatting
            dt = datetime.strptime(gr.receipt_date, "%Y-%m-%d")
            gr_date_str = (
                dt.strftime("%d/%m/%Y")
                if int(gr.receipt_id.split("-")[1]) % 3 == 0
                else gr.receipt_date
            )
            writer.writerow(
                [gr.receipt_id, gr.po_number, gr.vendor_id, gr_date_str, gr.received_by]
            )

    # 6. Goods Receipt Line Items
    gr_lines_path = os.path.join(output_dir, "goods_receipt_line_items.csv")
    with open(gr_lines_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["RECEIPT_NO", "LINE_NO", "SKU", "QTY_DELIVERED", "RECEIVED_AT"])
        for gr in receipts:
            for item in gr.line_items:
                writer.writerow(
                    [
                        gr.receipt_id,
                        item.line_number,
                        item.sku,
                        item.quantity_received,
                        item.received_date,
                    ]
                )


def generate_invoices_and_ground_truth(
    vendors: List[VendorRecord],
    pos: List[PurchaseOrder],
    receipts: List[GoodsReceipt],
    rng: random.Random,
    total_invoices: int = 900,
    pdf_count: int = 800,
    email_count: int = 100,
    pdf_dir: str = "data/samples/pdf",
    email_dir: str = "data/samples/email",
) -> List[InvoiceGroundTruth]:
    """Generates 900 invoices (800 PDFs, 100 emails) with labeled injected problems."""
    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(email_dir, exist_ok=True)

    vendor_lookup = {v.vendor_id: v for v in vendors}
    gr_lookup = {g.po_number: g for g in receipts}

    # Problem distribution exact counts across 900 invoices:
    # Exact Duplicates: 3% = 27
    # Near Duplicates: 2% = 18
    # Price Variance: 4% = 36
    # Qty Mismatch / Partial: 4% = 36
    # Missing PO: 2% = 18
    # Wrong Vendor: 3% = 27
    # Currency Issues: 1% = 9
    # Clean Matches: Remaining 729 (~81%)

    problem_assignments = (
        [ProblemType.EXACT_DUPLICATE] * 27
        + [ProblemType.NEAR_DUPLICATE] * 18
        + [ProblemType.PRICE_VARIANCE] * 36
        + [ProblemType.QTY_MISMATCH] * 36
        + [ProblemType.MISSING_PO] * 18
        + [ProblemType.WRONG_VENDOR] * 27
        + [ProblemType.CURRENCY_MISMATCH] * 9
    )
    clean_count = total_invoices - len(problem_assignments)
    problem_assignments += [ProblemType.CLEAN_MATCH] * clean_count
    rng.shuffle(problem_assignments)

    ground_truth_records: List[InvoiceGroundTruth] = []
    duplicate_source_records: List[
        Tuple[InvoiceGroundTruth, List[InvoiceLineItem], float, float, float]
    ] = []

    for idx in range(total_invoices):
        invoice_id = f"INV-{idx + 1:04d}"
        file_type = "pdf" if idx < pdf_count else "email"
        template = rng.choice(TEMPLATES) if file_type == "pdf" else "plain_email"
        problem = problem_assignments[idx]

        po = pos[idx]
        vendor = vendor_lookup[po.vendor_id]
        gr = gr_lookup[po.po_number]

        # Base clean attributes
        inv_number = f"INV-2026-{10000 + idx}"
        dt = datetime.strptime(po.order_date, "%Y-%m-%d") + timedelta(days=rng.randint(3, 7))
        inv_date = dt.strftime("%Y-%m-%d")
        currency = po.currency
        vendor_name_on_invoice = vendor.canonical_name
        po_reference = po.po_number

        # Deep copy line items from PO
        line_items = [
            InvoiceLineItem(
                line_number=it.line_number,
                sku=it.sku,
                description=it.description,
                quantity=it.quantity,
                unit_price=it.unit_price,
                total=it.total,
            )
            for it in po.line_items
        ]
        subtotal = po.subtotal
        tax_amount = po.tax
        total_amount = po.total

        problem_details = {}
        expected_match = MatchOutcome.CLEAN_MATCH
        expected_resolution = ResolutionCategory.AUTO_APPROVE

        # Apply specific problem mutations
        if problem == ProblemType.EXACT_DUPLICATE and duplicate_source_records:
            source, s_items, s_sub, s_tax, s_tot = rng.choice(duplicate_source_records)
            inv_number = source.invoice_number
            inv_date = source.invoice_date
            po_reference = source.po_reference
            vendor_name_on_invoice = source.vendor_name_on_invoice
            currency = source.currency
            line_items = [InvoiceLineItem(**item.model_dump()) for item in s_items]
            subtotal, tax_amount, total_amount = s_sub, s_tax, s_tot
            expected_match = MatchOutcome.DUPLICATE_SUSPECT
            expected_resolution = ResolutionCategory.REJECT_DUPLICATE
            problem_details = {"original_invoice_id": source.invoice_id, "type": "exact_hash_match"}

        elif problem == ProblemType.NEAR_DUPLICATE and duplicate_source_records:
            source, s_items, s_sub, s_tax, s_tot = rng.choice(duplicate_source_records)
            inv_number = f"{source.invoice_number}-A"  # Added suffix
            dt_shifted = datetime.strptime(source.invoice_date, "%Y-%m-%d") + timedelta(days=2)
            inv_date = dt_shifted.strftime("%Y-%m-%d")
            po_reference = source.po_reference
            vendor_name_on_invoice = source.vendor_name_on_invoice
            currency = source.currency
            line_items = [InvoiceLineItem(**item.model_dump()) for item in s_items]
            subtotal, tax_amount, total_amount = s_sub, s_tax, s_tot
            expected_match = MatchOutcome.DUPLICATE_SUSPECT
            expected_resolution = ResolutionCategory.REJECT_DUPLICATE
            problem_details = {
                "original_invoice_id": source.invoice_id,
                "type": "near_duplicate_vendor_amount",
            }

        elif problem == ProblemType.PRICE_VARIANCE:
            # Increase unit price by 8% to 15% (outside 2% tolerance)
            target_item = rng.choice(line_items)
            old_price = target_item.unit_price
            new_price = round(old_price * rng.uniform(1.08, 1.15), 2)
            target_item.unit_price = new_price
            target_item.total = round(target_item.quantity * new_price, 2)
            subtotal = round(sum(it.total for it in line_items), 2)
            tax_amount = round(subtotal * 0.06, 2)
            total_amount = round(subtotal + tax_amount, 2)
            expected_match = MatchOutcome.PRICE_VARIANCE
            expected_resolution = ResolutionCategory.HUMAN_REVIEW_PRICE_VARIANCE
            problem_details = {
                "sku": target_item.sku,
                "po_price": old_price,
                "invoice_price": new_price,
            }

        elif problem == ProblemType.QTY_MISMATCH:
            # Invoice bills for 100% of PO, but dock only received partial (50-70%)
            target_item = line_items[0]
            received_qty = int(target_item.quantity * rng.uniform(0.5, 0.7))
            gr.line_items[0].quantity_received = received_qty  # update dock receipt
            expected_match = MatchOutcome.QTY_MISMATCH
            expected_resolution = ResolutionCategory.HUMAN_REVIEW_QTY_MISMATCH
            problem_details = {
                "sku": target_item.sku,
                "billed_qty": target_item.quantity,
                "received_qty": received_qty,
            }

        elif problem == ProblemType.MISSING_PO:
            po_reference = None
            expected_match = MatchOutcome.NO_PO
            expected_resolution = ResolutionCategory.HUMAN_REVIEW_NO_PO
            problem_details = {"reason": "missing_or_unquoted_po_header"}

        elif problem == ProblemType.WRONG_VENDOR:
            # Use ambiguous variant or different vendor name
            vendor_name_on_invoice = (
                rng.choice(vendor.variants)
                if vendor.variants
                else f"{vendor.canonical_name} Dist. Group"
            )
            expected_match = MatchOutcome.VENDOR_UNRESOLVED
            expected_resolution = ResolutionCategory.HUMAN_REVIEW_VENDOR
            problem_details = {
                "invoice_vendor_text": vendor_name_on_invoice,
                "canonical_vendor": vendor.canonical_name,
            }

        elif problem == ProblemType.CURRENCY_MISMATCH:
            currency = "CAD" if po.currency == "USD" else "USD"
            expected_match = MatchOutcome.CURRENCY_MISMATCH
            expected_resolution = ResolutionCategory.HUMAN_REVIEW_CURRENCY
            problem_details = {"invoice_currency": currency, "po_currency": po.currency}

        # Deterministic Split: first 150 invoices locked as test set; remaining 750 as dev set
        split = "test" if idx < 150 else "dev"

        filename = f"{invoice_id}.pdf" if file_type == "pdf" else f"{invoice_id}.txt"
        file_path = os.path.join(pdf_dir if file_type == "pdf" else email_dir, filename)

        # Render invoice file
        if file_type == "pdf":
            create_invoice_pdf(
                file_path=file_path,
                template_name=template,
                vendor_name=vendor_name_on_invoice,
                invoice_number=inv_number,
                invoice_date=inv_date,
                po_reference=po_reference,
                currency=currency,
                line_items=line_items,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                remit_address=vendor.address,
            )
        else:
            # Plain email body invoice
            render_email_invoice(
                file_path=file_path,
                vendor_name=vendor_name_on_invoice,
                invoice_number=inv_number,
                invoice_date=inv_date,
                po_reference=po_reference,
                currency=currency,
                line_items=line_items,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
            )

        gt_record = InvoiceGroundTruth(
            invoice_id=invoice_id,
            filename=filename,
            file_type=file_type,
            template=template,
            split=split,
            vendor_id=vendor.vendor_id,
            vendor_name_on_invoice=vendor_name_on_invoice,
            canonical_vendor_name=vendor.canonical_name,
            invoice_number=inv_number,
            invoice_date=inv_date,
            currency=currency,
            po_reference=po_reference,
            line_items=line_items,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            problem_type=problem,
            problem_details=problem_details,
            expected_match_outcome=expected_match,
            expected_resolution_category=expected_resolution,
        )
        ground_truth_records.append(gt_record)

        # Store for future duplicate sampling (only clean matches become sources)
        if problem == ProblemType.CLEAN_MATCH:
            duplicate_source_records.append(
                (gt_record, line_items, subtotal, tax_amount, total_amount)
            )

    return ground_truth_records


def render_email_invoice(
    file_path: str,
    vendor_name: str,
    invoice_number: str,
    invoice_date: str,
    po_reference: str | None,
    currency: str,
    line_items: List[InvoiceLineItem],
    subtotal: float,
    tax_amount: float,
    total_amount: float,
) -> None:
    """Renders plain text billing email body."""
    po_str = po_reference if po_reference else "None"
    clean_vendor = vendor_name.lower().replace(" ", "").replace(",", "").replace(".", "")[:12]
    lines = [
        f"From: billing@{clean_vendor}.com",
        "To: ap-invoices@northwindsupply.com",
        f"Subject: Invoice {invoice_number} from {vendor_name} ({po_str})",
        f"Date: {invoice_date} 09:00:00 -0500",
        "",
        "Dear Northwind Accounts Payable,",
        "",
        f"Please find our billing details below for order reference: {po_str}",
        f"Invoice Number: {invoice_number}",
        f"Invoice Date: {invoice_date}",
        f"Currency: {currency}",
        f"Purchase Order: {po_str}",
        "",
        "--- Line Items ---",
    ]
    for it in line_items:
        lines.append(
            f"{it.line_number}. SKU: {it.sku} | {it.description} | "
            f"Qty: {it.quantity} | Unit: {it.unit_price:.2f} | Total: {it.total:.2f}"
        )

    lines.extend(
        [
            "",
            f"Subtotal: {currency} {subtotal:.2f}",
            f"Tax: {currency} {tax_amount:.2f}",
            f"Total Due: {currency} {total_amount:.2f}",
            "",
            "Payment Terms: Net 30. Thank you for your business.",
            f"Remit To: {vendor_name} Billing Department",
        ]
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Northwind AP dataset.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    print(f"=== Starting Northwind AP Data Generation (Seed: {args.seed}) ===")
    rng = random.Random(args.seed)

    # Output directory layout
    raw_dir = "data/raw"
    samples_pdf_dir = "data/samples/pdf"
    samples_email_dir = "data/samples/email"
    gt_dir = "data/ground_truth"
    os.makedirs(gt_dir, exist_ok=True)

    # 1. Generate Vendors (250)
    print("Generating 250 vendor master records...")
    vendors = generate_vendors(rng)

    # 2. Generate POs and Goods Receipts (900)
    print("Generating 900 POs and warehouse Goods Receipts...")
    pos, receipts = generate_pos_and_receipts(vendors, rng, count=900)

    # 3. Write Messy CSVs
    print("Writing messy ERP CSV dumps...")
    write_messy_csvs(vendors, pos, receipts, raw_dir)

    # 4. Generate Invoices (800 PDFs, 100 emails) & Inject Problems
    print("Generating 800 PDF invoices across 5 templates + 100 email invoices...")
    gt_records = generate_invoices_and_ground_truth(
        vendors=vendors,
        pos=pos,
        receipts=receipts,
        rng=rng,
        total_invoices=900,
        pdf_count=800,
        email_count=100,
        pdf_dir=samples_pdf_dir,
        email_dir=samples_email_dir,
    )

    # 5. Split Dataset (150 test locked, 750 dev)
    test_split = [r.model_dump() for r in gt_records if r.split == "test"]
    dev_split = [r.model_dump() for r in gt_records if r.split == "dev"]

    print(
        f"Saving Ground Truth: {len(gt_records)} total "
        f"(Test: {len(test_split)}, Dev: {len(dev_split)})"
    )
    with open(os.path.join(gt_dir, "ground_truth.json"), "w", encoding="utf-8") as f:
        json.dump([r.model_dump() for r in gt_records], f, indent=2)

    with open(os.path.join(gt_dir, "test_split.json"), "w", encoding="utf-8") as f:
        json.dump(test_split, f, indent=2)

    with open(os.path.join(gt_dir, "dev_split.json"), "w", encoding="utf-8") as f:
        json.dump(dev_split, f, indent=2)

    # Summary report
    problem_counts: Dict[str, int] = {}
    for r in gt_records:
        pt = r.problem_type.value
        problem_counts[pt] = problem_counts.get(pt, 0) + 1

    print("\n=== Dataset Generation Complete ===")
    print(f"Total Invoices: {len(gt_records)}")
    print(f"  - PDFs: 800 (in {samples_pdf_dir})")
    print(f"  - Emails: 100 (in {samples_email_dir})")
    print(f"  - Locked Test Set: {len(test_split)} (in data/ground_truth/test_split.json)")
    print(f"  - Dev Set: {len(dev_split)} (in data/ground_truth/dev_split.json)")
    print("\nInjected Problem Distribution:")
    for pt, count in sorted(problem_counts.items()):
        pct = (count / len(gt_records)) * 100
        print(f"  - {pt:20s}: {count:4d} ({pct:.1f}%)")


if __name__ == "__main__":
    main()
