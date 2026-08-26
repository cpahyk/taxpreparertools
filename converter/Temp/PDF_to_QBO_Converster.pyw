import os
import re
import html
import hashlib
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from api_client import APIClient, APIError
    from license_manager import LicenseManager
except ImportError:
    APIClient = None
    APIError = Exception
    LicenseManager = None

# ============================================================
# TAXPREPARERTOOLS.COM
# PDF -> QBO CONVERTER
#
# Multi-bank PDF bank statement converter.
#
# Supported parsers:
#   - Auto Detect
#   - Fifth Third Bank
#   - Climate First Bank
#   - Generic Bank Statement
#
# Website:
#   https://www.taxpreparertools.com/
# ============================================================


APP_NAME = "TaxPreparerTools PDF → QBO Converter"
SITE_NAME = "TaxPreparerTools.com"
SITE_URL = "https://www.taxpreparertools.com/"

APP_VERSION = "2.0"
LICENSE_SERVER_URL = os.environ.get("TAXPREPARERTOOLS_LICENSE_API", "http://localhost:8000")


# ============================================================
# DEPENDENCY
# ============================================================

try:
    import pypdf
except ImportError:
    root = tk.Tk()
    root.withdraw()

    messagebox.showerror(
        "Missing Dependency",
        "This program requires pypdf.\n\n"
        "Open Command Prompt / Terminal and run:\n\n"
        "pip install --upgrade pypdf"
    )

    raise SystemExit(1)


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_spaces(text):
    return re.sub(r"\s+", " ", text or "").strip()


def money_value(text):
    """
    Convert common bank statement money formats to float.

    Examples:
        1,234.56
        $1,234.56
        1,234.56-
        (1,234.56)
        $1,234.56-
    """

    if text is None:
        return None

    s = str(text).strip()

    if not s:
        return None

    s = s.replace("$", "")
    s = s.replace(",", "")
    s = s.replace(" ", "")

    negative = False

    if s.endswith("-"):
        negative = True
        s = s[:-1]

    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1]

    try:
        value = float(s)
    except ValueError:
        return None

    if negative:
        value = -value

    return value


def xml_escape(value):
    return html.escape(
        str(value or ""),
        quote=False
    )


def normalize_date(date_text, year):
    """
    Convert MM/DD to YYYYMMDD.
    """

    try:
        month, day = date_text.split("/")

        return (
            f"{int(year):04d}"
            f"{int(month):02d}"
            f"{int(day):02d}"
        )

    except Exception:
        return ""


def display_date(yyyymmdd):
    if len(yyyymmdd) != 8:
        return yyyymmdd

    return (
        f"{yyyymmdd[4:6]}/"
        f"{yyyymmdd[6:8]}/"
        f"{yyyymmdd[:4]}"
    )


def normalize_description(text):
    text = clean_spaces(text)

    text = re.sub(
        r"\bPage\s+\d+\s+of\s+\d+\b",
        "",
        text,
        flags=re.I
    )

    text = re.sub(
        r"\bDaily Balance Summary\b.*$",
        "",
        text,
        flags=re.I
    )

    return clean_spaces(text)


# ============================================================
# REGEX
# ============================================================

DATE_RE = r"\d{1,2}/\d{1,2}"

MONEY_RE = (
    r"(?:"
    r"\$?\(?"
    r"\d{1,3}(?:,\d{3})*"
    r"(?:\.\d{2})"
    r"\)?-?"
    r")"
)

DATE_AMOUNT_RE = re.compile(
    rf"(?P<date>{DATE_RE})\s+"
    rf"(?P<amount>{MONEY_RE})"
)


# ============================================================
# BANK DETECTION
# ============================================================

class BankDetector:

    BANKS = (
        "Auto Detect",
        "Fifth Third Bank",
        "Climate First Bank",
        "Generic Bank Statement",
    )

    @staticmethod
    def detect(text):

        s = text.lower()

        if (
            "fifth third bank" in s
            or "fifth third" in s
            or "53.com" in s
        ):
            return "Fifth Third Bank"

        if (
            "climate first bank" in s
            or "climatefirstbank.com" in s
        ):
            return "Climate First Bank"

        return "Generic Bank Statement"


# ============================================================
# BASE PARSER
# ============================================================

class BaseStatementParser:

    def __init__(self):

        self.pages = []
        self.full_text = ""

        self.year = str(
            datetime.datetime.now().year
        )

        # Populated by find_year() when a "Statement Period"
        # range is found. Used by year_for_date() to assign the
        # correct year to each transaction on statements whose
        # period crosses a year boundary (e.g. 12/15 - 01/14).
        self.start_month = None
        self.start_year = None
        self.end_month = None
        self.end_year = None

        self.summary = {
            "beginning_balance": None,
            "ending_balance": None,

            "checks_count": None,
            "checks_total": None,

            "debits_count": None,
            "debits_total": None,

            "credits_count": None,
            "credits_total": None,
        }

    # --------------------------------------------------------
    # READ PDF
    # --------------------------------------------------------

    def read_pdf(self, filename):

        self.pages = []

        with open(filename, "rb") as f:

            reader = pypdf.PdfReader(f)

            for page_number, page in enumerate(
                reader.pages,
                start=1
            ):

                try:

                    text = page.extract_text(
                        extraction_mode="layout",
                        layout_mode_space_vertically=False
                    )

                except TypeError:

                    try:
                        text = page.extract_text()
                    except Exception:
                        text = ""

                text = text or ""

                self.pages.append({
                    "page": page_number,
                    "text": text
                })

        self.full_text = "\n".join(
            p["text"]
            for p in self.pages
        )

        if not self.full_text.strip():

            raise RuntimeError(
                "No text could be extracted from this PDF.\n\n"
                "This may be a scanned/image-only PDF.\n\n"
                "Try a text-based PDF statement."
            )

        return self.pages

    # --------------------------------------------------------
    # YEAR
    # --------------------------------------------------------

    def find_year(self):

        # Try a full "Statement Period" range first (start date
        # AND end date) so a statement crossing a year boundary,
        # e.g. 12/15/2025 - 01/14/2026, can have each side of the
        # boundary dated correctly. See year_for_date().
        period_patterns = [

            r"Statement\s+Period\s*:?\s*"
            r"(\d{1,2})/\d{1,2}/(\d{4})\s*"
            r"(?:-|to|through)\s*"
            r"(\d{1,2})/\d{1,2}/(\d{4})",

            r"(\d{1,2})/\d{1,2}/(\d{4})\s*"
            r"(?:-|to|through)\s*"
            r"(\d{1,2})/\d{1,2}/(\d{4})",
        ]

        for pattern in period_patterns:

            match = re.search(
                pattern,
                self.full_text,
                flags=re.I | re.S
            )

            if match:

                (
                    start_month,
                    start_year,
                    end_month,
                    end_year,
                ) = match.groups()

                self.start_month = int(start_month)
                self.start_year = int(start_year)
                self.end_month = int(end_month)
                self.end_year = int(end_year)

                self.year = end_year

                return self.year

        patterns = [

            r"Statement\s+Period\s+Date\s*:"
            r"\s*\d{1,2}/\d{1,2}/"
            r"(\d{4})",

            r"Statement\s+Period.*?"
            r"\d{1,2}/\d{1,2}/"
            r"(\d{4})",

            r"\d{1,2}/\d{1,2}/"
            r"(20\d{2})",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                self.full_text,
                flags=re.I | re.S
            )

            if match:

                self.year = match.group(1)

                return self.year

        match = re.search(
            r"\b(20\d{2})\b",
            self.full_text
        )

        if match:
            self.year = match.group(1)

        return self.year

    def year_for_date(self, date_text):
        """
        Pick the correct year for a MM/DD transaction date.

        Most statements only need self.year. But when a "Statement
        Period" range was found and it spans two different years,
        a single blanket year is wrong for one side of the
        boundary -- so pick per-transaction based on its month.
        """

        if (
            self.start_year is None
            or self.end_year is None
            or self.start_year == self.end_year
        ):
            return self.year

        try:
            month = int(date_text.split("/")[0])
        except (ValueError, IndexError):
            return self.year

        if month >= self.start_month:
            return str(self.start_year)

        if month <= self.end_month:
            return str(self.end_year)

        return self.year

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    def parse_summary(self):

        text = clean_spaces(
            self.full_text
        )

        # Beginning balance
        for pattern in (
            r"Beginning\s+Balance\s+\$?([\d,]+\.\d{2})",
            r"Beginning\s+Balance.*?\$?([\d,]+\.\d{2})",
        ):

            m = re.search(
                pattern,
                text,
                re.I
            )

            if m:

                self.summary[
                    "beginning_balance"
                ] = abs(
                    money_value(
                        m.group(1)
                    )
                )

                break

        # Ending balance
        for pattern in (
            r"Ending\s+Balance\s+\$?([\d,]+\.\d{2})",
            r"Ending\s+Balance.*?\$?([\d,]+\.\d{2})",
        ):

            m = re.search(
                pattern,
                text,
                re.I
            )

            if m:

                self.summary[
                    "ending_balance"
                ] = money_value(
                    m.group(1)
                )

                break

        # Fifth Third checks
        m = re.search(
            r"Checks\s+"
            r"(\d+)\s+"
            r"checks?\s+"
            r"totaling\s+"
            r"\$?([\d,]+\.\d{2})",
            text,
            re.I
        )

        if m:

            self.summary[
                "checks_count"
            ] = int(
                m.group(1)
            )

            self.summary[
                "checks_total"
            ] = abs(
                money_value(
                    m.group(2)
                )
            )

        # Withdrawals / Debits
        m = re.search(
            r"Withdrawals\s*/?\s*Debits\s+"
            r"(\d+)\s+"
            r"items?\s+"
            r"totaling\s+"
            r"\$?([\d,]+\.\d{2})",
            text,
            re.I
        )

        if m:

            self.summary[
                "debits_count"
            ] = int(
                m.group(1)
            )

            self.summary[
                "debits_total"
            ] = abs(
                money_value(
                    m.group(2)
                )
            )

        # Deposits / Credits
        m = re.search(
            r"Deposits\s*/?\s*Credits\s+"
            r"(\d+)\s+"
            r"items?\s+"
            r"totaling\s+"
            r"\$?([\d,]+\.\d{2})",
            text,
            re.I
        )

        if m:

            self.summary[
                "credits_count"
            ] = int(
                m.group(1)
            )

            self.summary[
                "credits_total"
            ] = abs(
                money_value(
                    m.group(2)
                )
            )

    # --------------------------------------------------------
    # CREATE TRANSACTION
    # --------------------------------------------------------

    def make_transaction(
        self,
        date_text,
        amount,
        description,
        source,
        year,
        check_number=None
    ):

        date = normalize_date(
            date_text,
            year
        )

        if not date:
            return None

        if amount is None:
            return None

        description = normalize_description(
            description
        )

        if not description:
            description = "Transaction"

        return {
            "date": date,
            "amount": round(
                float(amount),
                2
            ),
            "name": description[:255],
            "check_num": (
                str(check_number)
                if check_number
                else None
            ),
            "source": source,
        }

    # --------------------------------------------------------
    # DEDUPLICATE
    # --------------------------------------------------------

    def dedupe(self, transactions):
        """
        Collapse a transaction only when it is an exact repeat of
        the one immediately before it in extraction order.

        This intentionally does NOT collapse identical-looking
        transactions found elsewhere in the statement (e.g. two
        separate $20 vending-machine charges on the same day) --
        only ones extracted back-to-back, which is the signature of
        a PDF layout artifact (a line repeated across a page break,
        or picked up twice during extraction) rather than two
        genuinely different transactions that happen to match.
        """

        result = []
        previous_key = None

        for txn in transactions:

            if txn.get("check_num"):

                key = (
                    "CHECK",
                    txn["date"],
                    txn["check_num"],
                    round(
                        txn["amount"],
                        2
                    )
                )

            else:

                key = (
                    txn["date"],
                    round(
                        txn["amount"],
                        2
                    ),
                    clean_spaces(
                        txn["name"]
                    ).lower(),
                    txn["source"]
                )

            if key == previous_key:
                continue

            previous_key = key
            result.append(txn)

        result.sort(
            key=lambda x: (
                x["date"],
                x["source"],
                x["name"]
            )
        )

        return result

    # --------------------------------------------------------
    # RECONCILE
    # --------------------------------------------------------

    def reconcile(self, transactions):

        checks = [
            t for t in transactions
            if t["source"] == "Check"
        ]

        debits = [
            t for t in transactions
            if t["source"] == "Debit"
        ]

        credits = [
            t for t in transactions
            if t["source"] == "Credit"
        ]

        return {

            "checks_count": len(checks),

            "checks_total": round(
                sum(
                    abs(t["amount"])
                    for t in checks
                ),
                2
            ),

            "debits_count": len(debits),

            "debits_total": round(
                sum(
                    abs(t["amount"])
                    for t in debits
                ),
                2
            ),

            "credits_count": len(credits),

            "credits_total": round(
                sum(
                    abs(t["amount"])
                    for t in credits
                ),
                2
            ),
        }

    # --------------------------------------------------------
    # PARSE
    # --------------------------------------------------------

    def parse(self, filename):

        self.read_pdf(filename)

        self.find_year()

        self.parse_summary()

        transactions = (
            self.parse_transactions()
        )

        transactions = self.dedupe(
            transactions
        )

        parsed = self.reconcile(
            transactions
        )

        return {
            "transactions": transactions,
            "summary": self.summary,
            "parsed": parsed,
            "year": self.year,
            "text": self.full_text,
        }

    def parse_transactions(self):
        raise NotImplementedError


# ============================================================
# SECTION PARSER
# ============================================================

class SectionParser(BaseStatementParser):

    NONE = "NONE"
    CHECKS = "CHECKS"
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

    def __init__(self):

        super().__init__()

        self.section = self.NONE

    # --------------------------------------------------------
    # SECTION DETECTION
    # --------------------------------------------------------

    def detect_section(self, line):

        s = clean_spaces(
            line
        ).lower()

        # Checks
        if (
            "checks" in s
            and (
                "number" in s
                or "date paid" in s
                or "totaling" in s
            )
        ):

            return self.CHECKS

        # Withdrawals / Debits
        if (
            "withdrawals / debits" in s
            or "withdrawals/debits" in s
            or "withdrawals" in s
            or "debits" in s
        ):

            return self.DEBIT

        # Deposits / Credits
        if (
            "deposits / credits" in s
            or "deposits/credits" in s
            or "deposits" in s
            or "credits" in s
        ):

            return self.CREDIT

        # Stop transaction sections
        if (
            "daily balance" in s
            or "account summary" in s
            or "analysis period" in s
            or "interest rate" in s
            or "service charge" in s
            or "beginning balance" in s
            or "ending balance" in s
        ):

            return self.NONE

        return None

    # --------------------------------------------------------
    # CHECK PARSER
    # --------------------------------------------------------

    def parse_check_line(self, line):

        transactions = []

        pattern = re.compile(
            rf"(?P<number>\d{{3,7}})"
            rf"\s+[is]?\s*"
            rf"(?P<date>{DATE_RE})"
            rf"\s+"
            rf"(?P<amount>{MONEY_RE})",
            re.I
        )

        matches = list(
            pattern.finditer(line)
        )

        for match in matches:

            number = match.group(
                "number"
            )

            date_text = match.group(
                "date"
            )

            amount = money_value(
                match.group("amount")
            )

            if amount is None:
                continue

            txn = self.make_transaction(
                date_text,
                -abs(amount),
                f"Check {number}",
                "Check",
                self.year_for_date(date_text),
                number
            )

            if txn:
                transactions.append(txn)

        return transactions

    # --------------------------------------------------------
    # NORMAL TRANSACTION PARSER
    # --------------------------------------------------------

    def parse_transaction_line(
        self,
        line,
        source
    ):

        transactions = []

        matches = list(
            DATE_AMOUNT_RE.finditer(
                line
            )
        )

        if not matches:
            return transactions

        for index, match in enumerate(
            matches
        ):

            date_text = match.group(
                "date"
            )

            amount_text = match.group(
                "amount"
            )

            amount = money_value(
                amount_text
            )

            if amount is None:
                continue

            start = match.end()

            if index + 1 < len(matches):

                end = matches[
                    index + 1
                ].start()

            else:

                end = len(line)

            description = line[
                start:end
            ]

            description = normalize_description(
                description
            )

            if not description:
                continue

            if source == "Debit":

                final_amount = -abs(
                    amount
                )

            else:

                final_amount = abs(
                    amount
                )

            txn = self.make_transaction(
                date_text,
                final_amount,
                description,
                source,
                self.year_for_date(date_text)
            )

            if txn:
                transactions.append(
                    txn
                )

        return transactions

    # --------------------------------------------------------
    # MAIN SECTION PARSER
    # --------------------------------------------------------

    def parse_transactions(self):

        transactions = []

        pending = None

        for page in self.pages:

            lines = page[
                "text"
            ].splitlines()

            for raw_line in lines:

                line = raw_line.rstrip()

                stripped = clean_spaces(
                    line
                )

                if not stripped:
                    continue

                new_section = (
                    self.detect_section(
                        stripped
                    )
                )

                if new_section is not None:

                    self.section = (
                        new_section
                    )

                    pending = None

                    continue

                # ------------------------------------------------
                # CHECKS
                # ------------------------------------------------

                if self.section == self.CHECKS:

                    found = (
                        self.parse_check_line(
                            stripped
                        )
                    )

                    if found:
                        transactions.extend(
                            found
                        )

                    continue

                # ------------------------------------------------
                # DEBITS / CREDITS
                # ------------------------------------------------

                if self.section in (
                    self.DEBIT,
                    self.CREDIT
                ):

                    source = (
                        "Debit"
                        if self.section
                        == self.DEBIT
                        else "Credit"
                    )

                    found = (
                        self.parse_transaction_line(
                            stripped,
                            source
                        )
                    )

                    if found:

                        transactions.extend(
                            found
                        )

                        pending = found[-1]

                    else:

                        # Description continuation
                        if pending:

                            continuation = (
                                normalize_description(
                                    stripped
                                )
                            )

                            blocked_words = (
                                "page ",
                                "daily balance",
                                "account summary",
                                "beginning balance",
                                "ending balance",
                                "analysis period",
                                "service charge"
                            )

                            if (
                                continuation
                                and not any(
                                    x in
                                    continuation.lower()
                                    for x in
                                    blocked_words
                                )
                            ):

                                pending["name"] = (
                                    pending["name"]
                                    + " "
                                    + continuation
                                )[:255]

        return transactions


# ============================================================
# FIFTH THIRD
# ============================================================

class FifthThirdParser(
    SectionParser
):
    """
    Fifth Third statements generally contain:

        Checks

        Withdrawals / Debits
        Date Amount Description

        Deposits / Credits
        Date Amount Description

    The parser intentionally does NOT rely on one giant regex.
    """

    pass


# ============================================================
# CLIMATE FIRST
# ============================================================

class ClimateFirstParser(
    SectionParser
):

    def detect_section(self, line):

        s = clean_spaces(
            line
        ).lower()

        if (
            "checks paid" in s
            or "checks in number order" in s
            or (
                "checks" in s
                and (
                    "number" in s
                    or "date" in s
                )
            )
        ):

            return self.CHECKS

        if (
            "deposits and additions" in s
            or "deposits" in s
            or "additions" in s
        ):

            return self.CREDIT

        if (
            "checks and withdrawals" in s
            or "withdrawals" in s
            or "debits" in s
        ):

            return self.DEBIT

        if (
            "daily balance" in s
            or "interest rate summary" in s
            or "account summary" in s
        ):

            return self.NONE

        return None

    def parse_check_line(self, line):

        transactions = []

        pattern = re.compile(
            rf"(?P<date>{DATE_RE})"
            rf"\s+"
            rf"(?P<number>\d{{3,7}})\*?"
            rf"\s+"
            rf"(?P<amount>{MONEY_RE})",
            re.I
        )

        for match in pattern.finditer(
            line
        ):

            number = match.group(
                "number"
            )

            date_text = match.group(
                "date"
            )

            amount = money_value(
                match.group("amount")
            )

            if amount is None:
                continue

            txn = self.make_transaction(
                date_text,
                -abs(amount),
                f"Check {number}",
                "Check",
                self.year_for_date(date_text),
                number
            )

            if txn:
                transactions.append(
                    txn
                )

        return transactions


# ============================================================
# GENERIC
# ============================================================

class GenericParser(
    SectionParser
):

    def detect_section(self, line):

        s = clean_spaces(
            line
        ).lower()

        # Check section
        if (
            "checks paid" in s
            or (
                "checks" in s
                and (
                    "date" in s
                    or "number" in s
                )
            )
        ):

            return self.CHECKS

        # Debit section
        if any(
            term in s
            for term in (
                "withdrawals",
                "withdrawal",
                "debits",
                "debit",
                "payments",
                "charges"
            )
        ):

            return self.DEBIT

        # Credit section
        if any(
            term in s
            for term in (
                "deposits",
                "deposit",
                "credits",
                "credit",
                "additions",
                "receipts"
            )
        ):

            return self.CREDIT

        # Stop
        if any(
            term in s
            for term in (
                "daily balance",
                "balance summary",
                "account summary",
                "beginning balance",
                "ending balance",
                "interest rate",
                "service charge",
                "analysis period"
            )
        ):

            return self.NONE

        return None


# ============================================================
# PARSER FACTORY
# ============================================================

def create_parser(bank):

    if bank == "Fifth Third Bank":
        return FifthThirdParser()

    if bank == "Climate First Bank":
        return ClimateFirstParser()

    return GenericParser()


# ============================================================
# QBO GENERATOR
# ============================================================

class QBOGenerator:

    def __init__(
        self,
        bank_name,
        account_number,
        fid="",
        bid=""
    ):

        self.bank_name = clean_spaces(
            bank_name
        )

        self.account_number = (
            account_number.strip()
        )

        self.fid = fid.strip()
        self.bid = bid.strip()

        # Tracks how many times a given transaction's content has
        # been seen so far in this generate() call. See fitid().
        self._fitid_occurrences = {}

    # --------------------------------------------------------
    # FITID
    # --------------------------------------------------------

    def fitid(
        self,
        transaction
    ):
        """
        FITID is content-based, not position-based: hashing the
        transaction's own fields (not its index in the list) means
        re-exporting the same statement -- even with a different
        date range or transaction count around it -- produces the
        same FITID for the same transaction, so QuickBooks
        correctly recognizes it as already-imported instead of
        creating a duplicate.

        Two transactions can have identical content (date, amount,
        name, check number) and still both be genuine -- e.g. two
        separate same-day charges of the same amount. An occurrence
        counter keyed on that content keeps each one's FITID unique
        within this export while remaining stable across runs, as
        long as their relative order doesn't change (it won't: the
        transaction list is always produced in the same sorted
        order for the same input).
        """

        content_key = "|".join([
            transaction["date"],
            f"{transaction['amount']:.2f}",
            transaction["name"],
            str(
                transaction.get(
                    "check_num",
                    ""
                ) or ""
            ),
        ])

        occurrence = (
            self._fitid_occurrences.get(content_key, 0)
            + 1
        )

        self._fitid_occurrences[content_key] = occurrence

        raw = f"{content_key}|{occurrence}"

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()[:32]

    # --------------------------------------------------------
    # GENERATE QBO / OFX
    # --------------------------------------------------------

    def generate(
        self,
        transactions,
        beginning_balance=None,
        ending_balance=None
    ):

        if not transactions:

            raise ValueError(
                "There are no transactions to export."
            )

        dates = [
            t["date"]
            for t in transactions
        ]

        start_date = min(dates)
        end_date = max(dates)

        now = datetime.datetime.now()

        server_time = now.strftime(
            "%Y%m%d%H%M%S"
        )

        lines = [

            "OFXHEADER:100",
            "DATA:OFXSGML",
            "VERSION:103",
            "SECURITY:NONE",
            "ENCODING:USASCII",
            "CHARSET:1252",
            "COMPRESSION:NONE",
            "OLDFILEUID:NONE",
            "NEWFILEUID:NONE",
            "",

            "<OFX>",

            "<SIGNONMSGSRSV1>",
            "<SONRS>",

            "<STATUS>",
            "<CODE>0",
            "<SEVERITY>INFO",
            "</STATUS>",

            f"<DTSERVER>{server_time}",
            "<LANGUAGE>ENG",

        ]

        lines.extend([
            "<FI>",
            f"<ORG>{xml_escape(self.bank_name)}",
            f"<FID>{xml_escape(self.fid or '0')}",
            "</FI>",
        ])

        lines.extend([

            "</SONRS>",
            "</SIGNONMSGSRSV1>",

            "<BANKMSGSRSV1>",
            "<STMTTRNRS>",
            "<TRNUID>0",

            "<STATUS>",
            "<CODE>0",
            "<SEVERITY>INFO",
            "</STATUS>",

            "<STMTRS>",
            "<CURDEF>USD",

            "<BANKACCTFROM>",
        ])

        if self.bid:

            lines.append(
                f"<BANKID>{xml_escape(self.bid)}"
            )

        else:

            lines.append(
                "<BANKID>000000000"
            )

        lines.extend([

            f"<ACCTID>"
            f"{xml_escape(self.account_number)}",

            "<ACCTTYPE>CHECKING",

            "</BANKACCTFROM>",

            "<BANKTRANLIST>",

            f"<DTSTART>{start_date}",
            f"<DTEND>{end_date}",
        ])

        # ----------------------------------------------------
        # TRANSACTIONS
        # ----------------------------------------------------

        for index, transaction in enumerate(
            transactions,
            start=1
        ):

            amount = float(
                transaction["amount"]
            )

            if transaction.get(
                "check_num"
            ):

                trntype = "CHECK"

            elif amount < 0:

                trntype = "DEBIT"

            else:

                trntype = "CREDIT"

            fid = self.fitid(
                transaction,
                index
            )

            lines.extend([

                "<STMTTRN>",

                f"<TRNTYPE>{trntype}",

                f"<DTPOSTED>"
                f"{transaction['date']}",

                f"<TRNAMT>"
                f"{amount:.2f}",

                f"<FITID>{fid}",

                f"<NAME>"
                f"{xml_escape(transaction['name'])}",
            ])

            if transaction.get(
                "check_num"
            ):

                lines.append(
                    f"<CHECKNUM>"
                    f"{xml_escape(transaction['check_num'])}"
                )

            lines.append(
                "</STMTTRN>"
            )

        lines.append(
            "</BANKTRANLIST>"
        )

        # ----------------------------------------------------
        # ENDING BALANCE
        # ----------------------------------------------------

        if ending_balance is None:

            if beginning_balance is not None:

                ending_balance = (
                    beginning_balance
                    + sum(
                        t["amount"]
                        for t in transactions
                    )
                )

            else:

                ending_balance = sum(
                    t["amount"]
                    for t in transactions
                )

        ending_balance = round(
            ending_balance,
            2
        )

        lines.extend([

            "<LEDGERBAL>",

            f"<BALAMT>"
            f"{ending_balance:.2f}",

            f"<DTASOF>{end_date}",

            "</LEDGERBAL>",

            "</STMTRS>",
            "</STMTTRNRS>",
            "</BANKMSGSRSV1>",

            "</OFX>",
        ])

        return (
            "\r\n".join(lines)
            + "\r\n"
        )


# ============================================================
# GUI
# ============================================================

class ConverterApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            APP_NAME
            + " | "
            + SITE_NAME
        )

        self.root.geometry(
            "1280x820"
        )

        self.root.minsize(
            1000,
            650
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        self.pdf_file = None
        self.data = None
        self.transactions = []

        if LicenseManager is None:
            messagebox.showerror(
                "License System Error",
                "The license system could not be loaded.\n\n"
                "Make sure api_client.py and license_manager.py "
                "are in the same folder as this application."
            )
            self.root.destroy()
            return

        self.license_manager = LicenseManager(
            api_client=APIClient(base_url=LICENSE_SERVER_URL),
            version=APP_VERSION,
        )
        self.license_valid = False

        self.build_ui()
        self.root.after(100, self.check_license_on_startup)

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        main = ttk.Frame(
            self.root,
            padding=10
        )

        main.pack(
            fill=tk.BOTH,
            expand=True
        )

        # ----------------------------------------------------
        # BRAND HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            main,
            bg="#17365D",
            height=72
        )

        header.pack(
            fill=tk.X,
            pady=(0, 10)
        )

        header.pack_propagate(
            False
        )

        title = tk.Label(
            header,
            text="TaxPreparerTools.com",
            bg="#17365D",
            fg="white",
            font=(
                "Segoe UI",
                18,
                "bold"
            )
        )

        title.pack(
            side=tk.LEFT,
            padx=18
        )

        subtitle = tk.Label(
            header,
            text=(
                "PDF → QBO Bank Statement Converter"
            ),
            bg="#17365D",
            fg="#D9EAF7",
            font=(
                "Segoe UI",
                11
            )
        )

        subtitle.pack(
            side=tk.LEFT
        )

        website_btn = tk.Button(
            header,
            text="Visit TaxPreparerTools.com",
            command=self.open_website,
            bg="#2E75B6",
            fg="white",
            activebackground="#4F91C9",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            padx=12
        )

        website_btn.pack(
            side=tk.RIGHT,
            padx=15
        )

        # ----------------------------------------------------
        # TOOLBAR
        # ----------------------------------------------------

        top = ttk.Frame(
            main
        )

        top.pack(
            fill=tk.X,
            pady=(0, 8)
        )

        ttk.Button(
            top,
            text="Open PDF",
            command=self.open_pdf
        ).pack(
            side=tk.LEFT
        )

        ttk.Button(
            top,
            text="Save Extracted Text",
            command=self.save_text
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        self.create_button = ttk.Button(
            top,
            text="Create QBO",
            command=self.create_qbo,
            state=tk.DISABLED
        )

        self.create_button.pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            top,
            text="Clear",
            command=self.clear
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            top,
            text="License",
            command=self.manage_license
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        ttk.Button(
            top,
            text="More Tax Tools",
            command=self.open_website
        ).pack(
            side=tk.RIGHT
        )

        self.file_label = ttk.Label(
            top,
            text="No PDF selected."
        )

        self.file_label.pack(
            side=tk.LEFT,
            padx=15
        )

        # ----------------------------------------------------
        # BANK
        # ----------------------------------------------------

        bank_frame = ttk.LabelFrame(
            main,
            text="Bank / Parser",
            padding=8
        )

        bank_frame.pack(
            fill=tk.X,
            pady=(0, 8)
        )

        ttk.Label(
            bank_frame,
            text="Bank:"
        ).pack(
            side=tk.LEFT
        )

        self.bank_var = tk.StringVar(
            value="Auto Detect"
        )

        self.bank_combo = ttk.Combobox(
            bank_frame,
            textvariable=self.bank_var,
            values=[
                "Auto Detect",
                "Fifth Third Bank",
                "Climate First Bank",
                "Generic Bank Statement",
            ],
            state="readonly",
            width=30
        )

        self.bank_combo.pack(
            side=tk.LEFT,
            padx=8
        )

        ttk.Label(
            bank_frame,
            text=(
                "Auto Detect identifies the bank from "
                "the PDF. You can also force a parser."
            )
        ).pack(
            side=tk.LEFT
        )

        # ----------------------------------------------------
        # ACCOUNT INFORMATION
        # ----------------------------------------------------

        account_frame = ttk.Frame(
            main
        )

        account_frame.pack(
            fill=tk.X,
            pady=(0, 8)
        )

        ttk.Label(
            account_frame,
            text="Account ID:"
        ).pack(
            side=tk.LEFT
        )

        self.account_var = tk.StringVar()

        ttk.Entry(
            account_frame,
            textvariable=self.account_var,
            width=28
        ).pack(
            side=tk.LEFT,
            padx=8
        )

        ttk.Label(
            account_frame,
            text="Bank ID / Routing:"
        ).pack(
            side=tk.LEFT,
            padx=(20, 5)
        )

        self.bid_var = tk.StringVar()

        ttk.Entry(
            account_frame,
            textvariable=self.bid_var,
            width=18
        ).pack(
            side=tk.LEFT
        )

        ttk.Label(
            account_frame,
            text="Optional"
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ----------------------------------------------------
        # QBO INFO
        # ----------------------------------------------------

        qbo_frame = ttk.Frame(
            main
        )

        qbo_frame.pack(
            fill=tk.X,
            pady=(0, 8)
        )

        ttk.Label(
            qbo_frame,
            text="Financial Institution:"
        ).pack(
            side=tk.LEFT
        )

        self.fi_var = tk.StringVar()

        ttk.Entry(
            qbo_frame,
            textvariable=self.fi_var,
            width=30
        ).pack(
            side=tk.LEFT,
            padx=8
        )

        ttk.Label(
            qbo_frame,
            text="FID:"
        ).pack(
            side=tk.LEFT,
            padx=(15, 5)
        )

        self.fid_var = tk.StringVar()

        ttk.Entry(
            qbo_frame,
            textvariable=self.fid_var,
            width=15
        ).pack(
            side=tk.LEFT
        )

        ttk.Label(
            qbo_frame,
            text="Optional"
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # ----------------------------------------------------
        # RECONCILIATION
        # ----------------------------------------------------

        recon = ttk.LabelFrame(
            main,
            text="Statement Reconciliation",
            padding=10
        )

        recon.pack(
            fill=tk.X,
            pady=(0, 8)
        )

        self.recon_var = tk.StringVar(
            value="Open a PDF to begin."
        )

        self.recon_label = ttk.Label(
            recon,
            textvariable=self.recon_var,
            justify=tk.LEFT,
            font=(
                "Segoe UI",
                10
            )
        )

        self.recon_label.pack(
            anchor=tk.W
        )

        # ----------------------------------------------------
        # TRANSACTION TABLE
        # ----------------------------------------------------

        table_frame = ttk.Frame(
            main
        )

        table_frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        columns = (
            "date",
            "type",
            "amount",
            "check",
            "description"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "date": "Date",
            "type": "Type",
            "amount": "Amount",
            "check": "Check #",
            "description": "Description"
        }

        widths = {
            "date": 100,
            "type": 100,
            "amount": 120,
            "check": 100,
            "description": 700
        }

        for column in columns:

            self.tree.heading(
                column,
                text=headings[column]
            )

            self.tree.column(
                column,
                width=widths[column],
                anchor=(
                    tk.E
                    if column == "amount"
                    else tk.W
                )
            )

        scroll_y = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scroll_y.set
        )

        self.tree.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scroll_y.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        # ----------------------------------------------------
        # PROMOTIONAL FOOTER
        # ----------------------------------------------------

        promo = tk.Frame(
            main,
            bg="#F2F6FA",
            bd=1,
            relief=tk.SOLID,
            padx=10,
            pady=7
        )

        promo.pack(
            fill=tk.X,
            pady=(8, 0)
        )

        promo_left = tk.Label(
            promo,
            text=(
                "TaxPreparerTools.com  •  "
                "Free tax tools, calculators, "
                "IRS references & professional resources"
            ),
            bg="#F2F6FA",
            fg="#17365D",
            font=(
                "Segoe UI",
                9,
                "bold"
            )
        )

        promo_left.pack(
            side=tk.LEFT
        )

        promo_link = tk.Label(
            promo,
            text="Explore 50+ Tax Tools →",
            bg="#F2F6FA",
            fg="#1769AA",
            cursor="hand2",
            font=(
                "Segoe UI",
                9,
                "underline"
            )
        )

        promo_link.pack(
            side=tk.RIGHT
        )

        promo_link.bind(
            "<Button-1>",
            lambda event: self.open_website()
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status_var = tk.StringVar(
            value=(
                "Ready. "
                "Open a bank statement PDF to begin."
            )
        )

        ttk.Label(
            main,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        ).pack(
            fill=tk.X,
            pady=(8, 0)
        )

    # ========================================================
    # LICENSE
    # ========================================================

    def check_license_on_startup(self):
        key = self.license_manager.get_license_key()

        if not key:
            self.license_valid = False
            self.create_button.config(state=tk.DISABLED)
            self.show_license_dialog()
            return

        try:
            self.license_manager.validate()
            self.license_valid = True
            self.status_var.set("License verified. Ready to convert PDFs.")
        except Exception as exc:
            self.license_valid = False
            self.create_button.config(state=tk.DISABLED)
            answer = messagebox.askyesno(
                "License Validation Failed",
                "Your license could not be validated.\n\n"
                f"{exc}\n\n"
                "Would you like to enter a license key?"
            )
            if answer:
                self.show_license_dialog()
            else:
                self.status_var.set("License required.")

    def show_license_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Activate PDF → QBO Converter")
        win.geometry("520x300")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        frame = ttk.Frame(win, padding=25)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text="Activate Your License",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 8))

        ttk.Label(
            frame,
            text="Enter the license key purchased from TaxPreparerTools.com.",
            wraplength=450,
            justify=tk.CENTER
        ).pack(pady=(0, 15))

        key_var = tk.StringVar(
            value=self.license_manager.get_license_key() or ""
        )

        entry = ttk.Entry(
            frame,
            textvariable=key_var,
            width=48
        )
        entry.pack(pady=5)
        entry.focus_set()

        status = tk.StringVar(value="")
        ttk.Label(
            frame,
            textvariable=status,
            wraplength=450,
            justify=tk.CENTER
        ).pack(pady=8)

        buttons = ttk.Frame(frame)
        buttons.pack(pady=10)

        def activate():
            key = key_var.get().strip()
            if not key:
                status.set("Enter your license key.")
                return

            status.set("Activating license...")
            win.update_idletasks()

            try:
                self.license_manager.activate(key)
                self.license_valid = True
                self.status_var.set("License activated. Ready to convert PDFs.")
                messagebox.showinfo(
                    "License Activated",
                    "Your PDF → QBO Converter license is active on this computer.",
                    parent=win
                )
                win.grab_release()
                win.destroy()
            except Exception as exc:
                self.license_valid = False
                status.set(str(exc))

        ttk.Button(
            buttons,
            text="Activate",
            command=activate
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons,
            text="Buy / Manage License",
            command=self.open_website
        ).pack(side=tk.LEFT, padx=5)

        def close_dialog():
            win.grab_release()
            win.destroy()

        ttk.Button(
            buttons,
            text="Close",
            command=close_dialog
        ).pack(side=tk.LEFT, padx=5)

    def require_valid_license(self):
        if not self.license_valid:
            self.check_license_on_startup()

        if not self.license_valid:
            messagebox.showwarning(
                "License Required",
                "A valid license is required to create QBO files."
            )
            return False

        try:
            self.license_manager.validate()
            return True
        except Exception as exc:
            self.license_valid = False
            self.create_button.config(state=tk.DISABLED)
            messagebox.showerror(
                "License Validation Failed",
                str(exc)
            )
            return False

    def manage_license(self):
        self.show_license_dialog()

    # ========================================================
    # WEBSITE
    # ========================================================

    def open_website(self):

        try:
            webbrowser.open(
                SITE_URL,
                new=2
            )

        except Exception:

            messagebox.showinfo(
                "TaxPreparerTools.com",
                SITE_URL
            )

    # ========================================================
    # ABOUT
    # ========================================================

    def show_about(self):

        win = tk.Toplevel(
            self.root
        )

        win.title(
            "About TaxPreparerTools PDF → QBO"
        )

        win.geometry(
            "560x390"
        )

        win.resizable(
            False,
            False
        )

        frame = ttk.Frame(
            win,
            padding=25
        )

        frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        ttk.Label(
            frame,
            text="TaxPreparerTools.com",
            font=(
                "Segoe UI",
                20,
                "bold"
            )
        ).pack(
            pady=(0, 5)
        )

        ttk.Label(
            frame,
            text=(
                "PDF → QBO Bank Statement Converter"
            ),
            font=(
                "Segoe UI",
                12
            )
        ).pack(
            pady=(0, 15)
        )

        text = (
            "Convert bank statement PDFs into "
            "QuickBooks-compatible QBO files.\n\n"

            "Features:\n"
            "• Multiple bank parsers\n"
            "• Automatic bank detection\n"
            "• Check parsing\n"
            "• Debit and credit parsing\n"
            "• Statement reconciliation\n"
            "• QBO export\n"
            "• PDF text diagnostics\n\n"

            "More free tax tools, calculators, "
            "IRS resources and professional tools:\n\n"

            "TaxPreparerTools.com"
        )

        ttk.Label(
            frame,
            text=text,
            justify=tk.CENTER
        ).pack(
            pady=5
        )

        ttk.Button(
            frame,
            text="Visit TaxPreparerTools.com",
            command=self.open_website
        ).pack(
            pady=15
        )

        ttk.Button(
            frame,
            text="Close",
            command=win.destroy
        ).pack()

    # ========================================================
    # OPEN PDF
    # ========================================================

    def open_pdf(self):

        filename = filedialog.askopenfilename(
            title="Select Bank Statement PDF",
            filetypes=[
                (
                    "PDF files",
                    "*.pdf"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not filename:
            return

        self.status_var.set(
            "Reading PDF..."
        )

        self.root.update_idletasks()

        try:

            # Read first to detect bank.
            detector_parser = (
                BaseStatementParser()
            )

            detector_parser.read_pdf(
                filename
            )

            selected_bank = (
                self.bank_var.get()
            )

            if selected_bank == "Auto Detect":

                selected_bank = (
                    BankDetector.detect(
                        detector_parser.full_text
                    )
                )

                self.bank_var.set(
                    selected_bank
                )

            parser = create_parser(
                selected_bank
            )

            self.status_var.set(
                f"Parsing as "
                f"{selected_bank}..."
            )

            self.root.update_idletasks()

            data = parser.parse(
                filename
            )

            self.pdf_file = filename
            self.data = data
            self.transactions = (
                data["transactions"]
            )

            self.file_label.config(
                text=os.path.basename(
                    filename
                )
            )

            # Auto financial institution
            if not self.fi_var.get().strip():

                self.fi_var.set(
                    selected_bank
                )

            self.populate_table()

            self.update_reconciliation()

            if self.transactions and self.license_valid:

                self.create_button.config(
                    state=tk.NORMAL
                )

            else:

                self.create_button.config(
                    state=tk.DISABLED
                )

            self.status_var.set(
                f"Found "
                f"{len(self.transactions)} "
                f"transactions."
            )

        except Exception as exc:

            self.status_var.set(
                "Error parsing PDF."
            )

            messagebox.showerror(
                "PDF Parsing Error",
                str(exc)
            )

    # ========================================================
    # RECONCILIATION
    # ========================================================

    def update_reconciliation(self):

        if not self.data:
            return

        summary = self.data[
            "summary"
        ]

        parsed = self.data[
            "parsed"
        ]

        lines = []

        # ----------------------------------------------------
        # CHECKS
        # ----------------------------------------------------

        sc = summary[
            "checks_count"
        ]

        st = summary[
            "checks_total"
        ]

        pc = parsed[
            "checks_count"
        ]

        pt = parsed[
            "checks_total"
        ]

        if sc is not None:

            check_line = (
                f"CHECKS: "
                f"{pc} parsed / "
                f"{sc} on statement    "
                f"${pt:,.2f} / "
                f"${st:,.2f}"
            )

        else:

            check_line = (
                f"CHECKS: {pc} parsed"
            )

        lines.append(
            check_line
        )

        # ----------------------------------------------------
        # DEBITS
        # ----------------------------------------------------

        dc = summary[
            "debits_count"
        ]

        dt = summary[
            "debits_total"
        ]

        pdc = parsed[
            "debits_count"
        ]

        pdt = parsed[
            "debits_total"
        ]

        if dc is not None:

            debit_line = (
                f"WITHDRAWALS / DEBITS: "
                f"{pdc} parsed / "
                f"{dc} on statement    "
                f"${pdt:,.2f} / "
                f"${dt:,.2f}"
            )

        else:

            debit_line = (
                f"WITHDRAWALS / DEBITS: "
                f"{pdc} parsed"
            )

        lines.append(
            debit_line
        )

        # ----------------------------------------------------
        # CREDITS
        # ----------------------------------------------------

        cc = summary[
            "credits_count"
        ]

        ct = summary[
            "credits_total"
        ]

        pcc = parsed[
            "credits_count"
        ]

        pct = parsed[
            "credits_total"
        ]

        if cc is not None:

            credit_line = (
                f"DEPOSITS / CREDITS: "
                f"{pcc} parsed / "
                f"{cc} on statement    "
                f"${pct:,.2f} / "
                f"${ct:,.2f}"
            )

        else:

            credit_line = (
                f"DEPOSITS / CREDITS: "
                f"{pcc} parsed"
            )

        lines.append(
            credit_line
        )

        # ----------------------------------------------------
        # RECONCILIATION RESULT
        # ----------------------------------------------------

        checks_ok = True
        debits_ok = True
        credits_ok = True

        if sc is not None:

            checks_ok = (
                pc == sc
                and abs(
                    pt - st
                ) < 0.01
            )

        if dc is not None:

            debits_ok = (
                pdc == dc
                and abs(
                    pdt - dt
                ) < 0.01
            )

        if cc is not None:

            credits_ok = (
                pcc == cc
                and abs(
                    pct - ct
                ) < 0.01
            )

        lines.append("")

        if (
            checks_ok
            and debits_ok
            and credits_ok
        ):

            lines.append(
                "✓ RECONCILED — "
                "all statement transaction totals match."
            )

            self.recon_label.config(
                foreground="#137333"
            )

        else:

            lines.append(
                "⚠ NOT RECONCILED — "
                "review the transaction table before export."
            )

            self.recon_label.config(
                foreground="#B00020"
            )

        self.recon_var.set(
            "\n".join(lines)
        )

    # ========================================================
    # POPULATE TABLE
    # ========================================================

    def populate_table(self):

        for item in (
            self.tree.get_children()
        ):

            self.tree.delete(
                item
            )

        for txn in self.transactions:

            if txn["source"] == "Check":

                txn_type = "CHECK"

            elif txn["amount"] < 0:

                txn_type = "DEBIT"

            else:

                txn_type = "CREDIT"

            self.tree.insert(
                "",
                tk.END,
                values=(
                    display_date(
                        txn["date"]
                    ),
                    txn_type,
                    f"{txn['amount']:,.2f}",
                    txn.get(
                        "check_num",
                        ""
                    ) or "",
                    txn["name"]
                )
            )

    # ========================================================
    # SAVE EXTRACTED TEXT
    # ========================================================

    def save_text(self):

        if not self.data:

            messagebox.showwarning(
                "No PDF",
                "Open a PDF first."
            )

            return

        output = filedialog.asksaveasfilename(
            title="Save Extracted PDF Text",
            defaultextension=".txt",
            filetypes=[
                (
                    "Text files",
                    "*.txt"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not output:
            return

        try:

            with open(
                output,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    self.data["text"]
                )

            messagebox.showinfo(
                "Saved",
                "Extracted PDF text was saved.\n\n"
                "This file is useful for diagnosing "
                "new bank statement layouts."
            )

        except Exception as exc:

            messagebox.showerror(
                "Save Error",
                str(exc)
            )

    # ========================================================
    # CHECK RECONCILIATION BEFORE EXPORT
    # ========================================================

    def get_mismatches(self):

        if not self.data:
            return []

        parsed = self.data[
            "parsed"
        ]

        summary = self.data[
            "summary"
        ]

        mismatches = []

        # Checks
        if (
            summary["checks_count"]
            is not None
        ):

            if (
                parsed["checks_count"]
                !=
                summary["checks_count"]
                or
                abs(
                    parsed["checks_total"]
                    -
                    summary["checks_total"]
                ) >= 0.01
            ):

                mismatches.append(
                    "Checks"
                )

        # Debits
        if (
            summary["debits_count"]
            is not None
        ):

            if (
                parsed["debits_count"]
                !=
                summary["debits_count"]
                or
                abs(
                    parsed["debits_total"]
                    -
                    summary["debits_total"]
                ) >= 0.01
            ):

                mismatches.append(
                    "Withdrawals / Debits"
                )

        # Credits
        if (
            summary["credits_count"]
            is not None
        ):

            if (
                parsed["credits_count"]
                !=
                summary["credits_count"]
                or
                abs(
                    parsed["credits_total"]
                    -
                    summary["credits_total"]
                ) >= 0.01
            ):

                mismatches.append(
                    "Deposits / Credits"
                )

        return mismatches

    # ========================================================
    # CREATE QBO
    # ========================================================

    def create_qbo(self):

        if not self.require_valid_license():
            return

        if not self.transactions:

            messagebox.showwarning(
                "No Transactions",
                "No transactions were found."
            )

            return

        account = (
            self.account_var.get().strip()
        )

        if not account:

            messagebox.showwarning(
                "Account ID Required",
                "Enter the account number/ID "
                "shown on the statement."
            )

            return

        # ----------------------------------------------------
        # RECONCILIATION SAFETY CHECK
        # ----------------------------------------------------

        mismatches = (
            self.get_mismatches()
        )

        if mismatches:

            answer = messagebox.askyesno(
                "Statement Does Not Reconcile",

                "The following sections do not "
                "match the statement totals:\n\n"
                + "\n".join(
                    "• " + x
                    for x in mismatches
                )
                + "\n\n"
                "It is safer to correct the parser "
                "before importing into QuickBooks.\n\n"
                "Do you want to create the QBO anyway?"
            )

            if not answer:
                return

        # ----------------------------------------------------
        # GENERATOR
        # ----------------------------------------------------

        generator = QBOGenerator(
            bank_name=(
                self.fi_var.get().strip()
                or self.bank_var.get()
            ),
            account_number=account,
            fid=self.fid_var.get(),
            bid=self.bid_var.get()
        )

        try:

            qbo = generator.generate(
                self.transactions,

                beginning_balance=(
                    self.data[
                        "summary"
                    ][
                        "beginning_balance"
                    ]
                ),

                ending_balance=(
                    self.data[
                        "summary"
                    ][
                        "ending_balance"
                    ]
                )
            )

        except Exception as exc:

            messagebox.showerror(
                "QBO Generation Error",
                str(exc)
            )

            return

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        base = os.path.splitext(
            os.path.basename(
                self.pdf_file
            )
        )[0]

        output = filedialog.asksaveasfilename(
            title="Save QBO File",
            defaultextension=".qbo",
            initialfile=(
                base + ".qbo"
            ),
            filetypes=[
                (
                    "QuickBooks QBO",
                    "*.qbo"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not output:
            return

        try:

            with open(
                output,
                "w",
                encoding="cp1252",
                newline=""
            ) as f:

                f.write(qbo)

        except Exception as exc:

            messagebox.showerror(
                "QBO Save Error",
                str(exc)
            )

            return

        self.status_var.set(
            "QBO file created successfully."
        )

        # ----------------------------------------------------
        # SUCCESS DIALOG
        # ----------------------------------------------------

        success = tk.Toplevel(
            self.root
        )

        success.title(
            "QBO Created"
        )

        success.geometry(
            "600x430"
        )

        success.resizable(
            False,
            False
        )

        frame = ttk.Frame(
            success,
            padding=25
        )

        frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        ttk.Label(
            frame,
            text="✓ QBO FILE CREATED",
            foreground="#137333",
            font=(
                "Segoe UI",
                18,
                "bold"
            )
        ).pack(
            pady=(0, 15)
        )

        ttk.Label(
            frame,
            text=(
                f"{len(self.transactions)} transactions "
                "were exported."
            ),
            font=(
                "Segoe UI",
                11
            )
        ).pack(
            pady=(0, 8)
        )

        ttk.Label(
            frame,
            text=output,
            wraplength=530,
            justify=tk.CENTER
        ).pack(
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # PROMOTION
        # ----------------------------------------------------

        promo_box = tk.Frame(
            frame,
            bg="#F2F6FA",
            bd=1,
            relief=tk.SOLID,
            padx=15,
            pady=15
        )

        promo_box.pack(
            fill=tk.X,
            pady=5
        )

        tk.Label(
            promo_box,
            text="More tools for tax professionals",
            bg="#F2F6FA",
            fg="#17365D",
            font=(
                "Segoe UI",
                12,
                "bold"
            )
        ).pack(
            pady=(0, 6)
        )

        tk.Label(
            promo_box,
            text=(
                "Explore TaxPreparerTools.com for "
                "tax calculators, IRS references, "
                "deadlines, professional resources "
                "and more."
            ),
            bg="#F2F6FA",
            fg="#333333",
            wraplength=500,
            justify=tk.CENTER
        ).pack(
            pady=(0, 10)
        )

        tk.Button(
            promo_box,
            text="Explore TaxPreparerTools.com",
            command=self.open_website,
            bg="#2E75B6",
            fg="white",
            activebackground="#4F91C9",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=15,
            pady=7,
            font=(
                "Segoe UI",
                10,
                "bold"
            )
        ).pack()

        # ----------------------------------------------------
        # CLOSE
        # ----------------------------------------------------

        ttk.Button(
            frame,
            text="Close",
            command=success.destroy
        ).pack(
            pady=18
        )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(self):

        self.pdf_file = None
        self.data = None
        self.transactions = []

        self.file_label.config(
            text="No PDF selected."
        )

        self.recon_var.set(
            "Open a PDF to begin."
        )

        self.recon_label.config(
            foreground="black"
        )

        self.status_var.set(
            "Ready. "
            "Open a bank statement PDF to begin."
        )

        self.account_var.set("")
        self.bid_var.set("")
        self.fid_var.set("")
        self.fi_var.set("")

        self.bank_var.set(
            "Auto Detect"
        )

        for item in (
            self.tree.get_children()
        ):

            self.tree.delete(
                item
            )

        self.create_button.config(
            state=tk.DISABLED
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def on_close(self):

        answer = messagebox.askyesno(
            "Exit",
            "Close the PDF → QBO Converter?"
        )

        if answer:

            self.root.destroy()


# ============================================================
# MAIN
# ============================================================

def main():

    root = tk.Tk()

    try:

        style = ttk.Style()

        if "vista" in style.theme_names():

            style.theme_use(
                "vista"
            )

        elif "clam" in style.theme_names():

            style.theme_use(
                "clam"
            )

    except Exception:
        pass

    ConverterApp(
        root
    )

    root.mainloop()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
