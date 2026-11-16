"""SEC EDGAR: ticker lookup, filing lists, and reported financials from XBRL company facts. urllib only.

SEC asks automated clients to send a User-Agent with a contact email. Set SEC_CONTACT_EMAIL to use
your own; the default is a placeholder.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from datetime import date
from pathlib import Path

CONTACT = os.environ.get("SEC_CONTACT_EMAIL", "admin@example.com")
UA = f"market-tools personal research {CONTACT}"
CACHE = Path(os.environ.get("MARKET_TOOLS_CACHE",
                            Path(__file__).resolve().parents[2] / "private" / "cache"))

# Each line item tries these us-gaap tags in order; companies tag the same thing differently.
LINE_ITEMS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                "RevenuesNetOfInterestExpense", "RevenueFromContractWithCustomerIncludingAssessedTax"],
    "cost_of_revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "d_and_a": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization",
                "DepreciationAmortizationAndAccretionNet", "Depreciation"],
    "interest_expense": ["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt"],
    "pretax_income": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                      "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "eps_diluted": ["EarningsPerShareDiluted"],
    "diluted_shares": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock"],
    "dividends_paid": ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue",
             "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "total_assets": ["Assets"],
    "long_term_debt": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "current_debt": ["LongTermDebtCurrent", "DebtCurrent", "ShortTermBorrowings"],
    "total_liabilities": ["Liabilities"],
    "shareholders_equity": ["StockholdersEquity",
                            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
}
INSTANT = {"cash", "total_assets", "long_term_debt", "current_debt", "total_liabilities", "shareholders_equity"}


def _get(url: str):
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read())
        except Exception as e:  # SEC allows ~10 requests/sec; back off on 429/503
            last = e
            time.sleep(1 + attempt)
    raise last  # type: ignore[misc]


def cik_for(ticker_or_cik: str) -> tuple:
    """Return (10-digit CIK, company name) for a ticker or CIK. Ticker list is cached for a day."""
    s = str(ticker_or_cik).strip().upper()
    if s.isdigit():
        return s.zfill(10), None
    path = CACHE / "sec-tickers.json"
    if path.exists() and time.time() - path.stat().st_mtime < 86400:
        table = json.loads(path.read_text())
    else:
        table = _get("https://www.sec.gov/files/company_tickers.json")
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(table))
    for row in table.values():
        if row["ticker"].upper() == s.replace(".", "-"):
            return str(row["cik_str"]).zfill(10), row["title"]
    raise ValueError(f"{ticker_or_cik}: not found in SEC's ticker list (foreign or delisted companies may not file here)")


def filings(ticker: str, forms: list | None = None, limit: int = 15) -> dict:
    cik, name = cik_for(ticker)
    sub = _get(f"https://data.sec.gov/submissions/CIK{cik}.json")
    r = sub["filings"]["recent"]
    want = {f.upper() for f in forms} if forms else None
    out = []
    for i, form in enumerate(r["form"]):
        if want and form.upper() not in want:
            continue
        acc = r["accessionNumber"][i]
        folder = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}"
        out.append({
            "form": form, "filed": r["filingDate"][i], "period": r["reportDate"][i] or None,
            "description": r["primaryDocDescription"][i] or None,
            "items": r["items"][i] or None,  # 8-K item numbers, e.g. 2.02 = earnings, 1.01 = material agreement
            "url": f"{folder}/{r['primaryDocument'][i]}" if r["primaryDocument"][i] else folder,
        })
        if len(out) >= limit:
            break
    return {"company": sub.get("name") or name, "cik": cik, "sic": sub.get("sicDescription"),
            "fiscal_year_end": sub.get("fiscalYearEnd"), "filings": out}


def _days(f) -> int:
    if not f.get("start"):
        return 0
    return (date.fromisoformat(f["end"]) - date.fromisoformat(f["start"])).days


def _series(facts: dict, tags: list, instant: bool, period: str) -> tuple:
    """Merge tags in priority order: each period end takes the highest-priority tag that reports it.
    Companies switch tags over time (e.g. Revenues -> RevenueFromContractWithCustomer... after ASC 606)."""
    merged, used = {}, []
    for tag in tags:
        s, t = _one_tag(facts, tag, instant, period)
        new = {k: v for k, v in s.items() if k not in merged}
        if new:
            merged.update(new)
            used.append(t)
    return merged, ", ".join(used) or None


def _one_tag(facts: dict, tag: str, instant: bool, period: str) -> tuple:
    gaap = facts.get("facts", {}).get("us-gaap", {})
    for tag in [tag]:
        units = gaap.get(tag, {}).get("units", {})
        vals = units.get("USD") or units.get("USD/shares") or units.get("shares")
        if not vals:
            continue
        picked = {}
        for f in vals:
            if not f.get("form", "").startswith(("10-K", "10-Q", "20-F", "40-F")):
                continue
            if instant:
                if period == "annual" and f.get("fp") != "FY":
                    continue
            else:
                d = _days(f)
                if period == "annual" and not 350 <= d <= 380:
                    continue
                if period == "quarterly" and not 80 <= d <= 100:
                    continue
            prev = picked.get(f["end"])
            if prev is None or f["filed"] > prev["filed"]:  # latest filing wins (restatements)
                picked[f["end"]] = f
        if picked:
            return {k: v["val"] for k, v in picked.items()}, tag
    return {}, None


def financials(ticker: str, period: str = "annual", count: int = 5, items: list | None = None) -> dict:
    cik, name = cik_for(ticker)
    facts = _get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
    wanted = items or list(LINE_ITEMS)
    table, tags_used = {}, {}
    for item in wanted:
        if item not in LINE_ITEMS:
            continue
        s, tag = _series(facts, LINE_ITEMS[item], item in INSTANT, period)
        table[item], tags_used[item] = s, tag
    # Flow items define the periods; instants are matched to those period ends.
    flow_ends = sorted({e for k, s in table.items() if k not in INSTANT for e in s}, reverse=True)
    ends = (flow_ends or sorted({e for s in table.values() for e in s}, reverse=True))[:count]
    rows = []
    for e in ends:
        row = {"period_end": e}
        for k in wanted:
            if k in table:
                row[k] = table[k].get(e)
        g = row.get
        if g("gross_profit") is None and g("revenue") is not None and g("cost_of_revenue") is not None:
            row["gross_profit"] = g("revenue") - g("cost_of_revenue")
        if g("operating_income") is not None and g("d_and_a") is not None:
            row["ebitda"] = g("operating_income") + g("d_and_a")
        if g("operating_cash_flow") is not None and g("capex") is not None:
            row["free_cash_flow"] = g("operating_cash_flow") - g("capex")
        if any(g(k) is not None for k in ("long_term_debt", "current_debt")):
            row["total_debt"] = (g("long_term_debt") or 0) + (g("current_debt") or 0)
            if g("cash") is not None:
                row["net_debt"] = row["total_debt"] - g("cash")
        rev = g("revenue")
        if rev:
            for k in ("gross_profit", "operating_income", "ebitda", "net_income"):
                if row.get(k) is not None:
                    row[f"{k}_margin_%"] = round(row[k] / rev * 100, 1)
        rows.append(row)
    for a, b in zip(rows, rows[1:]):  # growth vs. the prior period in the list
        if a.get("revenue") and b.get("revenue"):
            a["revenue_growth_%"] = round((a["revenue"] / b["revenue"] - 1) * 100, 1)
    return {
        "company": facts.get("entityName") or name, "cik": cik, "period": period, "units": "USD (EPS in USD/share)",
        "rows": rows,
        "notes": ["EBITDA = operating income + D&A as reported; it is not adjusted EBITDA.",
                  "Quarterly rows come from 10-Qs, so a company's Q4 usually has no quarterly row (it is only in the 10-K).",
                  "Banks and insurers report revenue differently; check tags_used and pull other tags with sec_concept."],
        "tags_used": {k: v for k, v in tags_used.items() if v},
    }


def concept(ticker: str, tag: str, taxonomy: str = "us-gaap", count: int = 12) -> dict:
    cik, name = cik_for(ticker)
    d = _get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/{taxonomy}/{tag}.json")
    out = []
    for unit, vals in d.get("units", {}).items():
        seen = {}
        for f in vals:
            key = (f.get("start"), f["end"])
            if key not in seen or f["filed"] > seen[key]["filed"]:
                seen[key] = f
        for f in seen.values():
            out.append({"start": f.get("start"), "end": f["end"], "value": f["val"], "unit": unit,
                        "form": f.get("form"), "fiscal": f"{f.get('fy')} {f.get('fp')}", "filed": f["filed"]})
    out.sort(key=lambda x: (x["end"], x["filed"]), reverse=True)
    return {"company": d.get("entityName") or name, "tag": tag, "label": d.get("label"),
            "description": d.get("description"), "facts": out[:count]}
