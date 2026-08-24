"""
TaxPreparerTools - PDF to QBO Converter
Windows desktop application.

Features:
- PDF text extraction using PyMuPDF
- Generic bank-statement transaction detection
- Heuristics for common US bank layouts
- Transaction review/editing
- Duplicate detection
- Validation
- QBO/OFX-style export suitable for QuickBooks import workflows

IMPORTANT:
Bank PDFs vary significantly. The application intentionally requires
transaction review before export rather than silently guessing.
"""

from __future__ import annotations

import csv
import hashlib
import re
import sys
import traceback
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


APP_NAME = "TaxPreparerTools PDF → QBO Converter"
VERSION = "1.0.0"

DATE_PATTERNS = [
    re.compile(r"\b(?P<m>\d{1,2})/(?P<d>\d{1,2})/(?P<y>\d{2,4})\b"),
    re.compile(r"\b(?P<m>\d{1,2})-(?P<d>\d{1,2})-(?P<y>\d{2,4})\b"),
    re.compile(
        r"\b(?P<m>\d{1,2})\s*[/\-]\s*(?P<d>\d{1,2})\b"
    ),
]

AMOUNT_RE = re.compile(
    r"""
    (?<![\w$])
    (?P<sign>-|\()?
    \$?
    (?P<number>\d{1,3}(?:,\d{3})*(?:\.\d{2})|\d+\.\d{2})
    \)?
    (?![\w])
    """,
    re.VERBOSE,
)

MONEY_ONLY_RE = re.compile(
    r"(?P<sign>-|\()?\s*\$?(?P<number>\d[\d,]*\.\d{2})\)?"
)

BANK_HINTS = {
    "chase": (
        "chase",
        "jpmorgan chase",
        "jpmorgan",
    ),
    "bank_of_america": (
        "bank of america",
        "bankofamerica",
        "bank of america, n.a.",
    ),
    "wells_fargo": (
        "wells fargo",
        "wellsfargo",
    ),
}


@dataclass
class Transaction:
    transaction_date: date
    description: str
    amount: Decimal
    transaction_type: str = "DEBIT"
    balance: Optional[Decimal] = None
    source_page: int = 0
    confidence: str = "MEDIUM"
    reviewed: bool = False

    @property
    def debit(self) -> Decimal:
        return abs(self.amount) if self.transaction_type == "DEBIT" else Decimal("0")

    @property
    def credit(self) -> Decimal:
        return self.amount if self.transaction_type == "CREDIT" else Decimal("0")

    @property
    def transaction_id(self) -> str:
        raw = (
            f"{self.transaction_date.isoformat()}|"
            f"{self.description.strip().upper()}|"
            f"{self.amount}|"
            f"{self.transaction_type}"
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_decimal(value: str) -> Optional[Decimal]:
    if not value:
        return None

    value = value.strip()
    negative = value.startswith("-") or (
        value.startswith("(") and value.endswith(")")
    )

    value = value.replace("$", "").replace(",", "")
    value = value.replace("(", "").replace(")", "")

    try:
        number = Decimal(value)
    except InvalidOperation:
        return None

    return -abs(number) if negative else abs(number)


def parse_date_from_match(match: re.Match, default_year: int) -> Optional[date]:
    try:
        month = int(match.group("m"))
        day = int(match.group("d"))
        year_text = match.groupdict().get("y")

        if year_text:
            year = int(year_text)
            if year < 100:
                year += 2000
        else:
            year = default_year

        return date(year, month, day)
    except (ValueError, TypeError):
        return None


def find_date(text: str, default_year: int) -> Optional[date]:
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            result = parse_date_from_match(match, default_year)
            if result:
                return result
    return None


def extract_amounts(text: str) -> list[Decimal]:
    values: list[Decimal] = []

    for match in MONEY_ONLY_RE.finditer(text):
        value = parse_decimal(match.group(0))
        if value is not None:
            values.append(value)

    return values


def detect_bank(text: str) -> str:
    lowered = text.lower()

    for bank, hints in BANK_HINTS.items():
        if any(hint in lowered for hint in hints):
            return bank

    return "generic"


def classify_amount(
    line: str,
    amounts: list[Decimal],
) -> tuple[Optional[Decimal], str]:
    """
    Determines whether the amount appears to be a debit or credit.

    This is intentionally conservative. Words such as CREDIT, DEPOSIT,
    PAYMENT, REFUND, and DIVIDEND usually indicate money entering the account.
    """
    if not amounts:
        return None, "DEBIT"

    amount = amounts[-1]
    lowered = line.lower()

    credit_words = (
        "credit",
        "deposit",
        "refund",
        "interest",
        "dividend",
        "payment received",
        "direct deposit",
        "ach credit",
    )

    debit_words = (
        "debit",
        "withdrawal",
        "purchase",
        "payment",
        "fee",
        "charge",
        "ach debit",
        "check",
        "atm",
    )

    if any(word in lowered for word in credit_words):
        return abs(amount), "CREDIT"

    if any(word in lowered for word in debit_words):
        return abs(amount), "DEBIT"

    if amount < 0:
        return abs(amount), "DEBIT"

    return abs(amount), "DEBIT"


def looks_like_header(line: str) -> bool:
    lowered = line.lower()

    header_words = (
        "beginning balance",
        "ending balance",
        "account summary",
        "statement period",
        "account number",
        "routing number",
        "transaction history",
        "transaction date",
        "posting date",
        "description",
        "debit",
        "credit",
        "balance",
        "page ",
        "total deposits",
        "total withdrawals",
    )

    return any(word in lowered for word in header_words)


def looks_like_transaction(line: str) -> bool:
    if not line.strip():
        return False

    if looks_like_header(line):
        return False

    if not any(pattern.search(line) for pattern in DATE_PATTERNS):
        return False

    amounts = extract_amounts(line)

    if not amounts:
        return False

    # A transaction generally needs some descriptive text.
    date_match = None
    for pattern in DATE_PATTERNS:
        date_match = pattern.search(line)
        if date_match:
            break

    if not date_match:
        return False

    remainder = line[date_match.end():]
    remainder = MONEY_ONLY_RE.sub("", remainder)
    remainder = clean_text(remainder)

    return len(remainder) >= 2


def extract_pdf_pages(pdf_path: Path) -> list[tuple[int, str]]:
    if fitz is None:
        raise RuntimeError(
            "PyMuPDF is not installed.\n\n"
            "Install it with:\n"
            "py -m pip install PyMuPDF"
        )

    pages: list[tuple[int, str]] = []

    document = fitz.open(pdf_path)

    try:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text") or ""
            pages.append((page_number, text))
    finally:
        document.close()

    return pages


def parse_transaction_line(
    line: str,
    page_number: int,
    statement_year: int,
) -> Optional[Transaction]:
    transaction_date = find_date(line, statement_year)

    if transaction_date is None:
        return None

    amounts = extract_amounts(line)

    if not amounts:
        return None

    amount, transaction_type = classify_amount(line, amounts)

    if amount is None:
        return None

    # Remove date and monetary values to obtain the description.
    description = line

    for pattern in DATE_PATTERNS:
        description = pattern.sub("", description, count=1)
        break

    description = MONEY_ONLY_RE.sub("", description)
    description = clean_text(description)

    # Remove common statement-column artifacts.
    description = re.sub(
        r"\b(?:debit|credit|balance)\b",
        "",
        description,
        flags=re.IGNORECASE,
    )
    description = clean_text(description)

    if len(description) < 2:
        return None

    confidence = "HIGH"

    if len(amounts) > 2:
        confidence = "LOW"
    elif len(description) < 5:
        confidence = "MEDIUM"

    return Transaction(
        transaction_date=transaction_date,
        description=description,
        amount=amount,
        transaction_type=transaction_type,
        source_page=page_number,
        confidence=confidence,
    )


def parse_pdf(pdf_path: Path) -> tuple[list[Transaction], str, int]:
    pages = extract_pdf_pages(pdf_path)

    if not pages:
        raise ValueError("The PDF contains no readable pages.")

    complete_text = "\n".join(text for _, text in pages)
    bank = detect_bank(complete_text)

    statement_year = datetime.now().year

    # Try to infer a year from the document.
    years = re.findall(r"\b(20\d{2})\b", complete_text)
    if years:
        try:
            statement_year = int(years[0])
        except ValueError:
            pass

    transactions: list[Transaction] = []

    for page_number, text in pages:
        lines = [
            clean_text(line)
            for line in text.splitlines()
            if clean_text(line)
        ]

        for line in lines:
            if not looks_like_transaction(line):
                continue

            transaction = parse_transaction_line(
                line,
                page_number,
                statement_year,
            )

            if transaction:
                transactions.append(transaction)

    # Remove exact duplicates.
    unique: dict[str, Transaction] = {}

    for transaction in transactions:
        unique.setdefault(transaction.transaction_id, transaction)

    transactions = list(unique.values())

    transactions.sort(
        key=lambda item: (
            item.transaction_date,
            item.source_page,
            item.description.lower(),
        )
    )

    return transactions, bank, len(pages)


def qbo_escape(value: str) -> str:
    """
    Escape text for the SGML-like format used by QBO/OFX files.
    """
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def qbo_date(value: date) -> str:
    return value.strftime("%Y%m%d000000[-5:EST]")


def transaction_fitid(transaction: Transaction) -> str:
    return transaction.transaction_id.upper()


def build_qbo(
    transactions: list[Transaction],
    bank_id: str,
    account_id: str,
    account_type: str = "CHECKING",
) -> str:
    if not transactions:
        raise ValueError("There are no transactions to export.")

    today = datetime.now().strftime("%Y%m%d%H%M%S")

    start_date = min(t.transaction_date for t in transactions)
    end_date = max(t.transaction_date for t in transactions)

    lines: list[str] = []

    lines.append("OFXHEADER:100")
    lines.append("DATA:OFXSGML")
    lines.append("VERSION:103")
    lines.append("SECURITY:NONE")
    lines.append("ENCODING:USASCII")
    lines.append("CHARSET:1252")
    lines.append("COMPRESSION:NONE")
    lines.append("OLDFILEUID:NONE")
    lines.append("NEWFILEUID:NONE")
    lines.append("")
    lines.append("<OFX>")
    lines.append("<SIGNONMSGSRSV1>")
    lines.append("<SONRS>")
    lines.append("<STATUS>")
    lines.append("<CODE>0")
    lines.append("<SEVERITY>INFO")
    lines.append("</STATUS>")
    lines.append(f"<DTSERVER>{today}")
    lines.append("<LANGUAGE>ENG")
    lines.append("</SONRS>")
    lines.append("</SIGNONMSGSRSV1>")

    lines.append("<BANKMSGSRSV1>")
    lines.append("<STMTTRNRS>")
    lines.append("<TRNUID>0")
    lines.append("<STATUS>")
    lines.append("<CODE>0")
    lines.append("<SEVERITY>INFO")
    lines.append("</STATUS>")
    lines.append("<STMTRS>")
    lines.append("<CURDEF>USD")

    lines.append("<BANKACCTFROM>")
    lines.append(f"<BANKID>{qbo_escape(bank_id)}")
    lines.append(f"<ACCTID>{qbo_escape(account_id)}")
    lines.append(f"<ACCTTYPE>{qbo_escape(account_type)}")
    lines.append("</BANKACCTFROM>")

    lines.append("<BANKTRANLIST>")
    lines.append(f"<DTSTART>{qbo_date(start_date)}")
    lines.append(f"<DTEND>{qbo_date(end_date)}")

    for transaction in transactions:
        lines.append("<STMTTRN>")

        # QBO/OFX convention:
        # positive = credit/deposit
        # negative = debit/withdrawal
        signed_amount = (
            transaction.credit
            if transaction.transaction_type == "CREDIT"
            else -transaction.debit
        )

        lines.append(
            f"<TRNTYPE>{transaction.transaction_type}"
        )
        lines.append(
            f"<DTPOSTED>{qbo_date(transaction.transaction_date)}"
        )
        lines.append(f"<TRNAMT>{signed_amount:.2f}")
        lines.append(f"<FITID>{transaction_fitid(transaction)}")
        lines.append(
            f"<NAME>{qbo_escape(transaction.description[:80])}"
        )
        lines.append(
            f"<MEMO>{qbo_escape(transaction.description)}"
        )

        lines.append("</STMTTRN>")

    lines.append("</BANKTRANLIST>")

    lines.append("<LEDGERBAL>")
    lines.append("<BALAMT>0.00")
    lines.append(f"<DTASOF>{qbo_date(end_date)}")
    lines.append("</LEDGERBAL>")

    lines.append("</STMTRS>")
    lines.append("</STMTTRNRS>")
    lines.append("</BANKMSGSRSV1>")

    lines.append("</OFX>")

    return "\n".join(lines) + "\n"


class ConverterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title(f"{APP_NAME} {VERSION}")
        self.geometry("1250x760")
        self.minsize(1000, 650)

        self.pdf_path: Optional[Path] = None
        self.transactions: list[Transaction] = []
        self.detected_bank = "generic"
        self.page_count = 0

        self.status_var = tk.StringVar(
            value="Select a PDF bank statement to begin."
        )

        self.bank_var = tk.StringVar(value="generic")
        self.account_id_var = tk.StringVar()
        self.account_type_var = tk.StringVar(value="CHECKING")

        self._configure_style()
        self._build_ui()

    def _configure_style(self) -> None:
        style = ttk.Style(self)

        try:
            style.theme_use("vista")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 20, "bold"),
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10),
            foreground="#555555",
        )

        style.configure(
            "Status.TLabel",
            font=("Segoe UI", 9),
        )

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=(20, 18))
        header.pack(fill="x")

        ttk.Label(
            header,
            text="PDF → QBO Converter",
            style="Title.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            header,
            text=(
                "Convert bank-statement PDFs into QuickBooks-compatible "
                "QBO/OFX transaction files."
            ),
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        controls = ttk.Frame(self, padding=(20, 5))
        controls.pack(fill="x")

        ttk.Button(
            controls,
            text="1. Select PDF",
            command=self.select_pdf,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            controls,
            text="2. Analyze PDF",
            command=self.analyze_pdf,
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            controls,
            text="Export QBO",
            command=self.export_qbo,
        ).pack(side="left")

        ttk.Button(
            controls,
            text="Clear",
            command=self.clear_all,
        ).pack(side="right")

        metadata = ttk.LabelFrame(
            self,
            text="Account Information",
            padding=12,
        )
        metadata.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            metadata,
            text="Bank ID:",
        ).grid(row=0, column=0, sticky="w")

        ttk.Entry(
            metadata,
            textvariable=self.bank_var,
            width=28,
        ).grid(row=0, column=1, padx=(5, 20), sticky="w")

        ttk.Label(
            metadata,
            text="Account ID:",
        ).grid(row=0, column=2, sticky="w")

        ttk.Entry(
            metadata,
            textvariable=self.account_id_var,
            width=25,
        ).grid(row=0, column=3, padx=(5, 20), sticky="w")

        ttk.Label(
            metadata,
            text="Type:",
        ).grid(row=0, column=4, sticky="w")

        account_type = ttk.Combobox(
            metadata,
            textvariable=self.account_type_var,
            values=[
                "CHECKING",
                "SAVINGS",
                "MONEYMRKT",
                "CREDITLINE",
            ],
            state="readonly",
            width=15,
        )
        account_type.grid(row=0, column=5, padx=5)

        file_frame = ttk.Frame(self, padding=(20, 0))
        file_frame.pack(fill="x")

        self.file_label = ttk.Label(
            file_frame,
            text="No PDF selected.",
        )
        self.file_label.pack(anchor="w")

        table_frame = ttk.Frame(self, padding=(20, 10))
        table_frame.pack(fill="both", expand=True)

        columns = (
            "date",
            "description",
            "type",
            "amount",
            "confidence",
            "page",
            "reviewed",
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="extended",
        )

        headings = {
            "date": "Date",
            "description": "Description",
            "type": "Type",
            "amount": "Amount",
            "confidence": "Confidence",
            "page": "Page",
            "reviewed": "Reviewed",
        }

        widths = {
            "date": 100,
            "description": 430,
            "type": 90,
            "amount": 110,
            "confidence": 100,
            "page": 60,
            "reviewed": 90,
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column,
                width=widths[column],
                anchor="w",
            )

        scrollbar_y = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )

        scrollbar_x = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
        )

        self.tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.bind(
            "<Double-1>",
            self.edit_selected_transaction,
        )

        footer = ttk.Frame(self, padding=(20, 8))
        footer.pack(fill="x")

        ttk.Label(
            footer,
            textvariable=self.status_var,
            style="Status.TLabel",
        ).pack(side="left")

        ttk.Label(
            footer,
            text="Double-click a transaction to edit it.",
            style="Status.TLabel",
        ).pack(side="right")

    def select_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title="Select bank statement PDF",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*"),
            ],
        )

        if not path:
            return

        self.pdf_path = Path(path)

        self.file_label.config(
            text=f"Selected: {self.pdf_path}"
        )

        self.status_var.set(
            "PDF selected. Click Analyze PDF."
        )

    def analyze_pdf(self) -> None:
        if not self.pdf_path:
            messagebox.showwarning(
                APP_NAME,
                "Select a PDF first.",
            )
            return

        try:
            self.status_var.set("Reading PDF...")
            self.update_idletasks()

            transactions, bank, page_count = parse_pdf(
                self.pdf_path
            )

            self.transactions = transactions
            self.detected_bank = bank
            self.page_count = page_count

            if bank != "generic":
                self.bank_var.set(bank)

            self._refresh_table()

            if not transactions:
                self.status_var.set(
                    "No transactions detected."
                )

                messagebox.showwarning(
                    APP_NAME,
                    (
                        "No transactions were detected.\n\n"
                        "This may be a scanned/image-only PDF or an "
                        "unsupported statement layout.\n\n"
                        "OCR support can be added as a later module."
                    ),
                )
                return

            self.status_var.set(
                f"Detected {len(transactions)} transactions "
                f"across {page_count} pages. "
                f"Detected bank: {bank}."
            )

        except Exception as exc:
            self.status_var.set("PDF analysis failed.")

            messagebox.showerror(
                APP_NAME,
                f"Could not analyze the PDF.\n\n{exc}",
            )

    def _refresh_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, transaction in enumerate(self.transactions):
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    transaction.transaction_date.isoformat(),
                    transaction.description,
                    transaction.transaction_type,
                    f"{transaction.amount:.2f}",
                    transaction.confidence,
                    transaction.source_page,
                    "YES" if transaction.reviewed else "NO",
                ),
            )

    def edit_selected_transaction(self, _event=None) -> None:
        selection = self.tree.selection()

        if len(selection) != 1:
            return

        index = int(selection[0])
        transaction = self.transactions[index]

        dialog = TransactionEditor(
            self,
            transaction,
        )

        self.wait_window(dialog)

        if dialog.result is not None:
            self.transactions[index] = dialog.result
            self._refresh_table()

    def export_qbo(self) -> None:
        if not self.transactions:
            messagebox.showwarning(
                APP_NAME,
                "Analyze a PDF before exporting.",
            )
            return

        unreviewed = [
            transaction
            for transaction in self.transactions
            if not transaction.reviewed
        ]

        low_confidence = [
            transaction
            for transaction in self.transactions
            if transaction.confidence == "LOW"
        ]

        if unreviewed:
            answer = messagebox.askyesno(
                APP_NAME,
                (
                    f"{len(unreviewed)} transaction(s) have not been "
                    "marked as reviewed.\n\n"
                    "Export anyway?"
                ),
            )

            if not answer:
                return

        if low_confidence:
            answer = messagebox.askyesno(
                APP_NAME,
                (
                    f"{len(low_confidence)} transaction(s) have LOW "
                    "confidence.\n\n"
                    "Reviewing them before export is strongly recommended.\n\n"
                    "Continue?"
                ),
            )

            if not answer:
                return

        account_id = self.account_id_var.get().strip()

        if not account_id:
            messagebox.showwarning(
                APP_NAME,
                (
                    "Enter the bank account ID before exporting.\n\n"
                    "Use the account number or another identifier "
                    "appropriate for your QuickBooks import workflow."
                ),
            )
            return

        if not self._validate_transactions():
            return

        output_path = filedialog.asksaveasfilename(
            title="Save QBO file",
            defaultextension=".qbo",
            filetypes=[
                ("QBO files", "*.qbo"),
                ("OFX files", "*.ofx"),
                ("All files", "*.*"),
            ],
            initialfile=(
                f"{self.pdf_path.stem}_converted.qbo"
                if self.pdf_path
                else "converted.qbo"
            ),
        )

        if not output_path:
            return

        try:
            qbo = build_qbo(
                transactions=self.transactions,
                bank_id=self.bank_var.get().strip()
                or "UNKNOWN",
                account_id=account_id,
                account_type=self.account_type_var.get(),
            )

            Path(output_path).write_text(
                qbo,
                encoding="ascii",
                errors="xmlcharrefreplace",
            )

            self.status_var.set(
                f"Exported {len(self.transactions)} transactions."
            )

            messagebox.showinfo(
                APP_NAME,
                (
                    "QBO file created successfully.\n\n"
                    f"{output_path}\n\n"
                    "Review the file in QuickBooks before relying "
                    "on the imported transactions."
                ),
            )

        except Exception as exc:
            messagebox.showerror(
                APP_NAME,
                f"Could not create QBO file.\n\n{exc}",
            )

    def _validate_transactions(self) -> bool:
        errors: list[str] = []

        for index, transaction in enumerate(self.transactions, start=1):
            if not transaction.description.strip():
                errors.append(
                    f"Transaction {index}: missing description."
                )

            if transaction.amount < 0:
                errors.append(
                    f"Transaction {index}: negative absolute amount."
                )

            if transaction.transaction_type not in (
                "DEBIT",
                "CREDIT",
            ):
                errors.append(
                    f"Transaction {index}: invalid transaction type."
                )

        if errors:
            messagebox.showerror(
                APP_NAME,
                "Validation failed:\n\n"
                + "\n".join(errors[:20]),
            )
            return False

        return True

    def clear_all(self) -> None:
        self.pdf_path = None
        self.transactions.clear()
        self.detected_bank = "generic"
        self.page_count = 0

        self.bank_var.set("generic")
        self.account_id_var.set("")
        self.account_type_var.set("CHECKING")

        self.file_label.config(
            text="No PDF selected."
        )

        self._refresh_table()

        self.status_var.set(
            "Select a PDF bank statement to begin."
        )


class TransactionEditor(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        transaction: Transaction,
    ) -> None:
        super().__init__(parent)

        self.result: Optional[Transaction] = None
        self.original = transaction

        self.title("Edit Transaction")
        self.geometry("560x360")
        self.resizable(False, False)

        self.date_var = tk.StringVar(
            value=transaction.transaction_date.isoformat()
        )

        self.description_var = tk.StringVar(
            value=transaction.description
        )

        self.type_var = tk.StringVar(
            value=transaction.transaction_type
        )

        self.amount_var = tk.StringVar(
            value=f"{transaction.amount:.2f}"
        )

        self.reviewed_var = tk.BooleanVar(
            value=True
        )

        self._build()

        self.transient(parent)
        self.grab_set()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Date (YYYY-MM-DD)",
        ).grid(row=0, column=0, sticky="w", pady=8)

        ttk.Entry(
            frame,
            textvariable=self.date_var,
            width=40,
        ).grid(row=0, column=1, sticky="ew", pady=8)

        ttk.Label(
            frame,
            text="Description",
        ).grid(row=1, column=0, sticky="w", pady=8)

        ttk.Entry(
            frame,
            textvariable=self.description_var,
            width=40,
        ).grid(row=1, column=1, sticky="ew", pady=8)

        ttk.Label(
            frame,
            text="Type",
        ).grid(row=2, column=0, sticky="w", pady=8)

        ttk.Combobox(
            frame,
            textvariable=self.type_var,
            values=("DEBIT", "CREDIT"),
            state="readonly",
            width=37,
        ).grid(row=2, column=1, sticky="ew", pady=8)

        ttk.Label(
            frame,
            text="Amount",
        ).grid(row=3, column=0, sticky="w", pady=8)

        ttk.Entry(
            frame,
            textvariable=self.amount_var,
            width=40,
        ).grid(row=3, column=1, sticky="ew", pady=8)

        ttk.Checkbutton(
            frame,
            text="Mark as reviewed",
            variable=self.reviewed_var,
        ).grid(
            row=4,
            column=1,
            sticky="w",
            pady=12,
        )

        ttk.Label(
            frame,
            text=(
                "Source page: "
                f"{self.original.source_page}\n"
                f"Original confidence: {self.original.confidence}"
            ),
        ).grid(
            row=5,
            column=1,
            sticky="w",
            pady=8,
        )

        buttons = ttk.Frame(frame)
        buttons.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="e",
            pady=(20, 0),
        )

        ttk.Button(
            buttons,
            text="Cancel",
            command=self.destroy,
        ).pack(side="right", padx=5)

        ttk.Button(
            buttons,
            text="Save",
            command=self.save,
        ).pack(side="right", padx=5)

        frame.columnconfigure(1, weight=1)

    def save(self) -> None:
        try:
            transaction_date = date.fromisoformat(
                self.date_var.get().strip()
            )
        except ValueError:
            messagebox.showerror(
                "Invalid date",
                "Use YYYY-MM-DD.",
                parent=self,
            )
            return

        description = self.description_var.get().strip()

        if not description:
            messagebox.showerror(
                "Invalid description",
                "Description cannot be empty.",
                parent=self,
            )
            return

        amount = parse_decimal(
            self.amount_var.get()
        )

        if amount is None or amount < 0:
            messagebox.showerror(
                "Invalid amount",
                "Enter a valid non-negative amount.",
                parent=self,
            )
            return

        transaction_type = self.type_var.get()

        self.result = Transaction(
            transaction_date=transaction_date,
            description=description,
            amount=amount,
            transaction_type=transaction_type,
            balance=self.original.balance,
            source_page=self.original.source_page,
            confidence=self.original.confidence,
            reviewed=self.reviewed_var.get(),
        )

        self.destroy()


def show_startup_error(message: str) -> None:
    root = tk.Tk()
    root.withdraw()

    messagebox.showerror(
        APP_NAME,
        message,
    )

    root.destroy()


def main() -> None:
    try:
        app = ConverterApp()
        app.mainloop()
    except Exception:
        error = traceback.format_exc()

        try:
            show_startup_error(
                "The converter could not start.\n\n"
                + error
            )
        except Exception:
            print(error, file=sys.stderr)


if __name__ == "__main__":
    main()
