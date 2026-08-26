"""
Standalone validation for the three patches:
  1. dedupe() only collapses back-to-back repeats
  2. year_for_date() handles statements crossing a year boundary
  3. QBOGenerator.fitid() is content-based (stable + unique)

Stubs out tkinter (not installed in this sandbox / not needed for
these classes) so the target .pyw can be imported without a display.
"""

import sys
import types
import importlib.util
import importlib.machinery

# ---- stub tkinter so the import at the top of the .pyw succeeds ----
fake_tk = types.ModuleType("tkinter")
fake_tk.ttk = types.ModuleType("tkinter.ttk")
fake_tk.filedialog = types.ModuleType("tkinter.filedialog")
fake_tk.messagebox = types.ModuleType("tkinter.messagebox")
sys.modules["tkinter"] = fake_tk
sys.modules["tkinter.ttk"] = fake_tk.ttk
sys.modules["tkinter.filedialog"] = fake_tk.filedialog
sys.modules["tkinter.messagebox"] = fake_tk.messagebox

loader = importlib.machinery.SourceFileLoader(
    "converter", "PDF_to_QBO_Converter.pyw"
)
spec = importlib.util.spec_from_loader("converter", loader)
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)

SectionParser = converter.SectionParser
QBOGenerator = converter.QBOGenerator

failures = []


def check(label, condition):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        failures.append(label)


# ============================================================
# 1. YEAR-BOUNDARY HANDLING
# ============================================================

p = SectionParser()
p.full_text = (
    "TaxPreparerTools Bank\n"
    "Statement Period: 12/15/2025 - 01/14/2026\n"
)
year = p.find_year()

check("cross-year: find_year returns end year", year == "2026")
check("cross-year: start_month/start_year parsed", (p.start_month, p.start_year) == (12, 2025))
check("cross-year: end_month/end_year parsed", (p.end_month, p.end_year) == (1, 2026))
check("cross-year: December date -> start year", p.year_for_date("12/20") == "2025")
check("cross-year: January date -> end year", p.year_for_date("01/05") == "2026")

p2 = SectionParser()
p2.full_text = "Statement Period: 03/01/2026 - 03/31/2026\n"
year2 = p2.find_year()
check("same-year: find_year still works", year2 == "2026")
check("same-year: year_for_date matches single year", p2.year_for_date("03/15") == "2026")

p3 = SectionParser()
p3.full_text = "Some statement text mentioning 2026 somewhere, no period line."
year3 = p3.find_year()
check("no-period fallback: old single-year detection still works", year3 == "2026")
check("no-period fallback: year_for_date falls back to self.year", p3.year_for_date("07/04") == "2026")


# ============================================================
# 2. DEDUPE ADJACENCY BEHAVIOR
# ============================================================

def txn(date, amount, name, source):
    return {"date": date, "amount": amount, "name": name, "source": source, "check_num": None}


# Same content, back-to-back -> extraction artifact -> collapse
adjacent = [
    txn("20260115", -20.00, "VENDING MACHINE", "Debit"),
    txn("20260115", -20.00, "VENDING MACHINE", "Debit"),
]
result_adjacent = p.dedupe(adjacent)
check("dedupe: back-to-back exact repeat collapses to 1", len(result_adjacent) == 1)

# Same content, NOT adjacent (something else between them) -> two genuine transactions
separated = [
    txn("20260115", -20.00, "VENDING MACHINE", "Debit"),
    txn("20260115", -5.00, "COFFEE SHOP", "Debit"),
    txn("20260115", -20.00, "VENDING MACHINE", "Debit"),
]
result_separated = p.dedupe(separated)
check("dedupe: non-adjacent identical transactions both survive", len(result_separated) == 3)

# Three-in-a-row identical -> still just 1 (chain of repeats)
triple = [
    txn("20260115", -20.00, "VENDING MACHINE", "Debit"),
    txn("20260115", -20.00, "VENDING MACHINE", "Debit"),
    txn("20260115", -20.00, "VENDING MACHINE", "Debit"),
]
result_triple = p.dedupe(triple)
check("dedupe: chain of 3 identical repeats collapses to 1", len(result_triple) == 1)


# ============================================================
# 3. FITID: CONTENT-BASED STABILITY + UNIQUENESS
# ============================================================

sample = {"date": "20260115", "amount": -20.00, "name": "VENDING MACHINE", "check_num": None}

gen1 = QBOGenerator("Test Bank", "1234")
fid_run1 = gen1.fitid(sample)

gen2 = QBOGenerator("Test Bank", "1234")  # simulates a completely separate later re-export
fid_run2 = gen2.fitid(sample)

check("fitid: stable across separate export runs", fid_run1 == fid_run2)

gen3 = QBOGenerator("Test Bank", "1234")
txn_a = dict(sample)
txn_b = dict(sample)  # genuinely separate txn, identical content (preserved by the dedupe fix)
fid_a = gen3.fitid(txn_a)
fid_b = gen3.fitid(txn_b)

check("fitid: two genuine duplicates in one export get DIFFERENT fitids", fid_a != fid_b)

gen4 = QBOGenerator("Test Bank", "1234")  # re-running the same pair reproduces the same two fitids
fid_a2 = gen4.fitid(dict(sample))
fid_b2 = gen4.fitid(dict(sample))
check("fitid: re-running the same duplicate pair is stable", (fid_a2, fid_b2) == (fid_a, fid_b))


print()
if failures:
    print(f"{len(failures)} FAILURE(S):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
