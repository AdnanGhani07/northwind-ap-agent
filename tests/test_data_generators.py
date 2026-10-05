"""Tests for Phase 1 data generation and ground truth validation."""

import json
import os

from data.generators.schema import InvoiceGroundTruth, MatchOutcome, ProblemType, ResolutionCategory


def test_messy_csv_files_exist():
    raw_dir = "data/raw"
    expected_files = [
        "vendors.csv",
        "vendors_legacy_latin1.csv",
        "purchase_orders.csv",
        "po_line_items.csv",
        "goods_receipts.csv",
        "goods_receipt_line_items.csv",
    ]
    for filename in expected_files:
        path = os.path.join(raw_dir, filename)
        assert os.path.exists(path), f"Expected CSV file {path} does not exist"
        assert os.path.getsize(path) > 0, f"CSV file {path} is empty"


def test_latin1_csv_decodable():
    """Verify that legacy CSV with German/French accents can be decoded with latin-1."""
    legacy_path = os.path.join("data/raw", "vendors_legacy_latin1.csv")
    with open(legacy_path, "r", encoding="latin-1") as f:
        content = f.read()
    assert len(content) > 0
    assert "Müller" in content or "Montréal" in content or "SUPPLIER_NAME" in content


def test_invoices_generated_count():
    pdf_dir = "data/samples/pdf"
    email_dir = "data/samples/email"

    assert os.path.exists(pdf_dir), f"PDF directory {pdf_dir} missing"
    assert os.path.exists(email_dir), f"Email directory {email_dir} missing"

    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    email_files = [f for f in os.listdir(email_dir) if f.endswith(".txt")]

    assert len(pdf_files) == 800, f"Expected 800 PDF invoices, found {len(pdf_files)}"
    assert len(email_files) == 100, f"Expected 100 email invoices, found {len(email_files)}"


def test_ground_truth_and_splits():
    gt_path = os.path.join("data/ground_truth", "ground_truth.json")
    test_path = os.path.join("data/ground_truth", "test_split.json")
    dev_path = os.path.join("data/ground_truth", "dev_split.json")

    assert os.path.exists(gt_path), "Ground truth file missing"
    assert os.path.exists(test_path), "Test split file missing"
    assert os.path.exists(dev_path), "Dev split file missing"

    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)
    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    with open(dev_path, "r", encoding="utf-8") as f:
        dev_data = json.load(f)

    assert len(gt_data) == 900, f"Expected 900 ground truth items, got {len(gt_data)}"
    assert len(test_data) == 150, f"Expected 150 locked test split items, got {len(test_data)}"
    assert len(dev_data) == 750, f"Expected 750 dev split items, got {len(dev_data)}"

    # Validate Pydantic schema parsing on all records
    for record in gt_data:
        parsed = InvoiceGroundTruth(**record)
        assert parsed.invoice_id.startswith("INV-")
        assert parsed.total_amount > 0
        assert len(parsed.line_items) >= 1
        assert parsed.expected_match_outcome in list(MatchOutcome)
        assert parsed.expected_resolution_category in list(ResolutionCategory)


def test_injected_problem_distribution():
    gt_path = os.path.join("data/ground_truth", "ground_truth.json")
    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    counts = {}
    for r in gt_data:
        pt = r["problem_type"]
        counts[pt] = counts.get(pt, 0) + 1

    assert counts[ProblemType.CLEAN_MATCH.value] == 729  # 81%
    assert counts[ProblemType.EXACT_DUPLICATE.value] == 27  # 3%
    assert counts[ProblemType.NEAR_DUPLICATE.value] == 18  # 2%
    assert counts[ProblemType.PRICE_VARIANCE.value] == 36  # 4%
    assert counts[ProblemType.QTY_MISMATCH.value] == 36  # 4%
    assert counts[ProblemType.MISSING_PO.value] == 18  # 2%
    assert counts[ProblemType.WRONG_VENDOR.value] == 27  # 3%
    assert counts[ProblemType.CURRENCY_MISMATCH.value] == 9  # 1%
