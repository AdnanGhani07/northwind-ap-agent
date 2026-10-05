"""Data models and schemas for synthetic AP data generation and ground truth."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProblemType(str, Enum):
    CLEAN_MATCH = "CLEAN_MATCH"
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    NEAR_DUPLICATE = "NEAR_DUPLICATE"
    PRICE_VARIANCE = "PRICE_VARIANCE"
    QTY_MISMATCH = "QTY_MISMATCH"
    MISSING_PO = "MISSING_PO"
    WRONG_VENDOR = "WRONG_VENDOR"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"


class MatchOutcome(str, Enum):
    CLEAN_MATCH = "CLEAN_MATCH"
    PRICE_VARIANCE = "PRICE_VARIANCE"
    QTY_MISMATCH = "QTY_MISMATCH"
    NO_PO = "NO_PO"
    DUPLICATE_SUSPECT = "DUPLICATE_SUSPECT"
    VENDOR_UNRESOLVED = "VENDOR_UNRESOLVED"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"


class ResolutionCategory(str, Enum):
    AUTO_APPROVE = "AUTO_APPROVE"
    HUMAN_REVIEW_PRICE_VARIANCE = "HUMAN_REVIEW_PRICE_VARIANCE"
    HUMAN_REVIEW_QTY_MISMATCH = "HUMAN_REVIEW_QTY_MISMATCH"
    REJECT_DUPLICATE = "REJECT_DUPLICATE"
    HUMAN_REVIEW_NO_PO = "HUMAN_REVIEW_NO_PO"
    HUMAN_REVIEW_VENDOR = "HUMAN_REVIEW_VENDOR"
    HUMAN_REVIEW_CURRENCY = "HUMAN_REVIEW_CURRENCY"


class VendorRecord(BaseModel):
    vendor_id: str
    canonical_name: str
    tax_id: str
    address: str
    payment_terms: str
    currency: str = "USD"
    variants: List[str] = Field(default_factory=list)


class POLineItem(BaseModel):
    line_number: int
    sku: str
    description: str
    quantity: int
    unit_price: float
    total: float


class PurchaseOrder(BaseModel):
    po_number: str
    vendor_id: str
    vendor_name: str
    order_date: str
    currency: str
    line_items: List[POLineItem]
    subtotal: float
    tax: float
    total: float
    status: str = "OPEN"


class GoodsReceiptLineItem(BaseModel):
    line_number: int
    sku: str
    quantity_received: int
    received_date: str


class GoodsReceipt(BaseModel):
    receipt_id: str
    po_number: str
    vendor_id: str
    receipt_date: str
    received_by: str
    line_items: List[GoodsReceiptLineItem]


class InvoiceLineItem(BaseModel):
    line_number: int
    sku: str
    description: str
    quantity: int
    unit_price: float
    total: float


class InvoiceGroundTruth(BaseModel):
    invoice_id: str
    filename: str
    file_type: str  # "pdf" or "email"
    template: str
    split: str  # "dev" or "test"
    vendor_id: str
    vendor_name_on_invoice: str
    canonical_vendor_name: str
    invoice_number: str
    invoice_date: str
    currency: str
    po_reference: Optional[str] = None
    line_items: List[InvoiceLineItem]
    subtotal: float
    tax_amount: float
    total_amount: float
    problem_type: ProblemType
    problem_details: Dict[str, Any] = Field(default_factory=dict)
    expected_match_outcome: MatchOutcome
    expected_resolution_category: ResolutionCategory
