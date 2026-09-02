"""
Comprehensive financial metric engine.
Extracts primitive values from any Excel, then derives 100+ KPIs
organised into: growth, unit_economics, profitability, cash, fundraising.
"""
from __future__ import annotations
import math
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Keyword maps  (Italian + English)
# ─────────────────────────────────────────────────────────────────────────────
_KW: dict[str, list[str]] = {
    # Revenue primitives
    "mrr":            ["mrr","monthly recurring revenue","ricavi ricorrenti mensili","ricavo mensile ricorrente"],
    "arr":            ["arr","annual recurring revenue","ricavi ricorrenti annuali","ricavo annuale ricorrente"],
    "revenue":        ["fatturato totale","ricavi totali","total revenue","totale ricavi","entrate totali","revenue totale"],
    "revenue_month":  ["fatturato mensile","ricavi mensili","ricavo mensile","monthly revenue","revenue mensile"],
    "recurring_rev":  ["ricavi ricorrenti","recurring revenue","ricavi abbonamenti","subscription revenue"],
    "onetimetime_rev":["ricavi una tantum","one-time revenue","setup fee","ricavi non ricorrenti"],
    "expansion_rev":  ["expansion revenue","upsell","ricavi espansione","upgrade revenue"],
    "contraction_rev":["contraction","downgrade","ricavi ridotti","downgrade revenue"],
    # Customers
    "customers":      ["clienti attivi","active customers","utenti attivi","active users","clienti totali"],
    "new_customers":  ["nuovi clienti","new customers","nuove acquisizioni","clienti acquisiti"],
    "churned_cust":   ["clienti persi","churned customers","clienti disdetti","abbandoni"],
    "subscribers":    ["abbonamenti","abbonati","subscribers","utenti abbonati"],
    # Churn / retention
    "churn_rate":     ["churn rate","tasso abbandono","tasso di abbandono","churn mensile","monthly churn"],
    "churn_rev":      ["revenue churn","ricavi persi","mrr churn","churn ricavi"],
    "retention_rate": ["retention rate","tasso di retention","tasso ritenzione"],
    "repeat_rate":    ["repeat purchase","riacquisto","frequenza acquisto"],
    # Acquisition / marketing
    "cac":            ["cac","costo acquisizione cliente","customer acquisition cost","costo di acquisizione"],
    "cost_per_lead":  ["cost per lead","costo per lead","cpl"],
    "marketing_spend":["spesa marketing","marketing budget","budget marketing","advertising spend","ads spend"],
    "leads":          ["lead","leads","contatti generati"],
    "trials":         ["trial","prove gratuite","free trial"],
    "conversions":    ["conversioni","conversions","clienti convertiti"],
    "roas":           ["roas","return on ad spend"],
    "roi_marketing":  ["roi marketing","ritorno investimento marketing"],
    # Pricing
    "price":          ["prezzo","price","tariffa","fee mensile","canone mensile","monthly fee","subscription price"],
    "arpu":           ["arpu","arpa","revenue per user","ricavo per utente","revenue per account","avg revenue per user"],
    "avg_order":      ["average order value","aov","valore medio ordine","scontrino medio"],
    # Costs
    "cogs":           ["cogs","cost of goods sold","costo del venduto","costo diretto","costi diretti"],
    "gross_profit":   ["margine lordo","gross profit","utile lordo"],
    "fixed_costs":    ["costi fissi","fixed costs","overhead","costi strutturali","costi operativi fissi"],
    "variable_costs": ["costi variabili","variable costs"],
    "opex":           ["opex","operating expenses","costi operativi","spese operative","totale costi operativi"],
    "total_costs":    ["costi totali","total costs","totale costi","spese totali","totale spese"],
    "salaries":       ["stipendi","salary","personale","costo personale","labor cost"],
    "marketing_cost": ["costi marketing","marketing cost","costo marketing"],
    "rd_cost":        ["r&d","ricerca e sviluppo","research","sviluppo prodotto"],
    # Profitability
    "gross_margin_pct":["gross margin %","margine lordo %","gross margin percentage"],
    "ebitda":         ["ebitda","margine operativo lordo","operating income before"],
    "ebit":           ["ebit","operating income","reddito operativo"],
    "net_profit":     ["utile netto","net profit","net income","profitto netto","risultato netto","reddito netto"],
    "operating_margin":["operating margin","margine operativo %"],
    "contribution":   ["contribution margin","margine di contribuzione","margine contribuzione"],
    # Cash / liquidity
    "cash":           ["cassa","cash","liquidità","disponibilità cassa","cash balance","saldo cassa"],
    "burn_rate":      ["burn rate","cash burn","consumo mensile cassa","tasso consumo cassa"],
    "net_burn":       ["net burn","burn netto"],
    "gross_burn":     ["gross burn","burn lordo"],
    "operating_cf":   ["operating cash flow","flusso di cassa operativo","cash flow operativo","fcf operativo"],
    "capex":          ["capex","capital expenditure","investimenti","immobilizzazioni"],
    "working_cap":    ["working capital","capitale circolante","capitale di lavoro"],
    # Funding / valuation
    "raised":         ["amount raised","raccolta","funding","finanziamento","capitale raccolto","investimento ricevuto"],
    "pre_money":      ["pre-money","pre money valuation","valutazione pre"],
    "post_money":     ["post-money","post money valuation","valutazione post"],
    "irr":            ["irr","internal rate of return","tasso interno rendimento"],
    "npv":            ["npv","net present value","valore attuale netto"],
    "roe":            ["roe","return on equity","ritorno sul capitale"],
    "roa":            ["roa","return on assets"],
    "roic":           ["roic","return on invested capital"],
    # Employees
    "employees":      ["dipendenti","employees","headcount","personale totale","numero dipendenti"],
    # Time
    "months":         ["mesi","months","durata","periodo","n. mesi","numero mesi"],
    "lifespan":       ["vita media cliente","customer lifespan","average lifespan","durata media cliente"],
}

# ─────────────────────────────────────────────────────────────────────────────
# Metric catalogue  (all 100+ metrics we want to show)
# ─────────────────────────────────────────────────────────────────────────────
METRIC_META: dict[str, dict] = {
    # ── GROWTH ───────────────────────────────────────────────────────────────
    "mrr":           {"label":"MRR",                        "cat":"growth",          "unit":"€",    "fmt":"eur"},
    "arr":           {"label":"ARR",                        "cat":"growth",          "unit":"€",    "fmt":"eur"},
    "total_revenue": {"label":"Ricavi Totali",              "cat":"growth",          "unit":"€",    "fmt":"eur"},
    "revenue_mom":   {"label":"Crescita Ricavi MoM",        "cat":"growth",          "unit":"%",    "fmt":"pct"},
    "revenue_yoy":   {"label":"Crescita Ricavi YoY",        "cat":"growth",          "unit":"%",    "fmt":"pct"},
    "cagr_revenue":  {"label":"CAGR Ricavi",                "cat":"growth",          "unit":"%",    "fmt":"pct"},
    "arpu":          {"label":"ARPU / ARPA",                "cat":"growth",          "unit":"€",    "fmt":"eur"},
    "nrr":           {"label":"Net Revenue Retention",      "cat":"growth",          "unit":"%",    "fmt":"pct"},
    "grr":           {"label":"Gross Revenue Retention",    "cat":"growth",          "unit":"%",    "fmt":"pct"},
    "expansion_rev": {"label":"Expansion Revenue",          "cat":"growth",          "unit":"€",    "fmt":"eur"},
    "contraction_rev":{"label":"Contraction Revenue",       "cat":"growth",          "unit":"€",    "fmt":"eur"},
    # ── UNIT ECONOMICS ───────────────────────────────────────────────────────
    "cac":           {"label":"CAC",                        "cat":"unit_economics",  "unit":"€",    "fmt":"eur"},
    "cac_payback":   {"label":"CAC Payback Period",         "cat":"unit_economics",  "unit":"mesi", "fmt":"num"},
    "ltv":           {"label":"LTV",                        "cat":"unit_economics",  "unit":"€",    "fmt":"eur"},
    "ltv_cac":       {"label":"LTV / CAC",                  "cat":"unit_economics",  "unit":"x",    "fmt":"mult"},
    "avg_order":     {"label":"Average Order Value",        "cat":"unit_economics",  "unit":"€",    "fmt":"eur"},
    "gm_per_customer":{"label":"Gross Margin per Cliente",  "cat":"unit_economics",  "unit":"€",    "fmt":"eur"},
    "contrib_per_cust":{"label":"Contribution Margin / Cliente","cat":"unit_economics","unit":"€",  "fmt":"eur"},
    "breakeven_cust":{"label":"Breakeven per Cliente",      "cat":"unit_economics",  "unit":"€",    "fmt":"eur"},
    "payback_cust":  {"label":"Payback Period Cliente",     "cat":"unit_economics",  "unit":"mesi", "fmt":"num"},
    # ── PROFITABILITY ────────────────────────────────────────────────────────
    "gross_margin_pct":{"label":"Gross Margin %",           "cat":"profitability",   "unit":"%",    "fmt":"pct"},
    "gross_profit":  {"label":"Gross Profit",               "cat":"profitability",   "unit":"€",    "fmt":"eur"},
    "ebitda":        {"label":"EBITDA",                     "cat":"profitability",   "unit":"€",    "fmt":"eur"},
    "ebitda_margin": {"label":"EBITDA Margin %",            "cat":"profitability",   "unit":"%",    "fmt":"pct"},
    "ebit":          {"label":"EBIT",                       "cat":"profitability",   "unit":"€",    "fmt":"eur"},
    "net_profit":    {"label":"Net Profit",                 "cat":"profitability",   "unit":"€",    "fmt":"eur"},
    "net_margin":    {"label":"Net Profit Margin %",        "cat":"profitability",   "unit":"%",    "fmt":"pct"},
    "operating_margin":{"label":"Operating Margin %",       "cat":"profitability",   "unit":"%",    "fmt":"pct"},
    "contribution":  {"label":"Contribution Margin",        "cat":"profitability",   "unit":"€",    "fmt":"eur"},
    "cogs":          {"label":"COGS",                       "cat":"profitability",   "unit":"€",    "fmt":"eur"},
    "operating_leverage":{"label":"Operating Leverage",     "cat":"profitability",   "unit":"x",    "fmt":"mult"},
    # ── CASH ─────────────────────────────────────────────────────────────────
    "burn_rate":     {"label":"Burn Rate Mensile",          "cat":"cash",            "unit":"€",    "fmt":"eur"},
    "net_burn":      {"label":"Net Burn",                   "cat":"cash",            "unit":"€",    "fmt":"eur"},
    "gross_burn":    {"label":"Gross Burn",                 "cat":"cash",            "unit":"€",    "fmt":"eur"},
    "cash_runway":   {"label":"Cash Runway",                "cat":"cash",            "unit":"mesi", "fmt":"num"},
    "cash_balance":  {"label":"Cash Balance",               "cat":"cash",            "unit":"€",    "fmt":"eur"},
    "operating_cf":  {"label":"Operating Cash Flow",        "cat":"cash",            "unit":"€",    "fmt":"eur"},
    "free_cf":       {"label":"Free Cash Flow",             "cat":"cash",            "unit":"€",    "fmt":"eur"},
    "working_cap":   {"label":"Working Capital",            "cat":"cash",            "unit":"€",    "fmt":"eur"},
    # ── FUNDRAISING ──────────────────────────────────────────────────────────
    "raised":        {"label":"Amount Raised",              "cat":"fundraising",     "unit":"€",    "fmt":"eur"},
    "pre_money":     {"label":"Pre-money Valuation",        "cat":"fundraising",     "unit":"€",    "fmt":"eur"},
    "post_money":    {"label":"Post-money Valuation",       "cat":"fundraising",     "unit":"€",    "fmt":"eur"},
    "revenue_multiple":{"label":"Revenue Multiple",         "cat":"fundraising",     "unit":"x",    "fmt":"mult"},
    "arr_multiple":  {"label":"ARR Multiple",               "cat":"fundraising",     "unit":"x",    "fmt":"mult"},
    "ebitda_multiple":{"label":"EBITDA Multiple",           "cat":"fundraising",     "unit":"x",    "fmt":"mult"},
    "runway_post_round":{"label":"Runway Post-round",       "cat":"fundraising",     "unit":"mesi", "fmt":"num"},
    "irr":           {"label":"IRR",                        "cat":"fundraising",     "unit":"%",    "fmt":"pct"},
    "npv":           {"label":"NPV",                        "cat":"fundraising",     "unit":"€",    "fmt":"eur"},
    "roe":           {"label":"ROE",                        "cat":"fundraising",     "unit":"%",    "fmt":"pct"},
    "roa":           {"label":"ROA",                        "cat":"fundraising",     "unit":"%",    "fmt":"pct"},
    "roic":          {"label":"ROIC",                       "cat":"fundraising",     "unit":"%",    "fmt":"pct"},
}

CATEGORY_META = {
    "growth":         {"label": "Ricavi & Crescita",           "icon": "📈", "color": "#6366f1"},
    "unit_economics": {"label": "Unit Economics",              "icon": "🎯", "color": "#8b5cf6"},
    "profitability":  {"label": "Redditività & Margini",       "icon": "💰", "color": "#10b981"},
    "cash":           {"label": "Cassa & Sostenibilità",       "icon": "🏦", "color": "#06b6d4"},
    "fundraising":    {"label": "Funding & Valuation",         "icon": "🚀", "color": "#f59e0b"},
}


# ─────────────────────────────────────────────────────────────────────────────
# Primitive finder
# ─────────────────────────────────────────────────────────────────────────────

def _num(v: Any) -> float | None:
    try:
        f = float(v)
        return None if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return None


def _find_primitives(
    cells: list[dict],
    resolved: dict[str, Any],
) -> dict[str, float]:
    """
    Scan all cells and return the best match for each primitive concept.
    Returns {concept: float_value}.
    """
    # Score each cell for each concept
    best: dict[str, tuple[float, float]] = {}   # concept -> (score, value)

    for c in cells:
        if c.get("type") == "label":
            continue
        cid = c.get("id", "")
        raw = resolved.get(cid) if resolved.get(cid) is not None else c.get("value")
        v = _num(raw)
        if v is None:
            continue

        label = (c.get("label") or "").lower()

        for concept, keywords in _KW.items():
            score = 0.0
            for kw in keywords:
                if kw in label:
                    score = max(score, len(kw) / max(len(label), 1) * 100 + len(kw))
            if score > 0:
                prev_score, _ = best.get(concept, (0.0, 0.0))
                if score > prev_score:
                    best[concept] = (score, v)

    return {k: v for k, (_, v) in best.items()}


def _find_revenue_series(
    cells: list[dict],
    resolved: dict[str, Any],
) -> list[float]:
    """
    Find the best monthly revenue time series (row with most columns, matching revenue keywords).
    Returns list of monthly values sorted by column.
    """
    rev_kw = ["fatturato","ricavi","revenue","entrate","incassi","ricavo mensile","fatturato mensile","total revenue","ricavi mensili"]
    row_groups: dict[tuple, list[dict]] = {}
    for c in cells:
        if c.get("type") == "label":
            continue
        key = (c.get("sheet",""), c.get("row",0))
        row_groups.setdefault(key, []).append(c)

    best_series: list[float] = []
    best_score = 0.0

    for (sh, row_idx), row_cells in row_groups.items():
        numeric = sorted(
            [c for c in row_cells if c.get("data_type") in ("number","currency","percentage")],
            key=lambda c: c.get("col", 0)
        )
        if len(numeric) < 3:
            continue

        # Find row label from adjacent label cell
        label = ""
        for c in cells:
            if c.get("sheet") == sh and c.get("row") == row_idx and c.get("type") == "label":
                label = (c.get("label") or c.get("value") or "").lower()
                if label:
                    break

        kw_score = sum(len(kw) for kw in rev_kw if kw in label)
        if kw_score == 0:
            continue

        vals = []
        for c in numeric:
            v = resolved.get(c["id"]) if resolved.get(c["id"]) is not None else c.get("value")
            n = _num(v)
            vals.append(n if n is not None else 0.0)

        # Prefer non-zero, increasing-ish series
        nonzero = sum(1 for v in vals if v != 0)
        series_score = kw_score * nonzero * len(vals)
        if series_score > best_score:
            best_score = series_score
            best_series = vals

    return best_series


def _find_customer_series(cells, resolved) -> list[float]:
    cust_kw = ["clienti","utenti","abbonamenti","subscribers","customers","users"]
    row_groups: dict[tuple, list[dict]] = {}
    for c in cells:
        if c.get("type") == "label":
            continue
        row_groups.setdefault((c.get("sheet",""), c.get("row",0)), []).append(c)

    best: list[float] = []
    best_score = 0.0
    for (sh, row_idx), row_cells in row_groups.items():
        numeric = sorted([c for c in row_cells if c.get("data_type") in ("number","currency","percentage")],
                         key=lambda c: c.get("col",0))
        if len(numeric) < 3:
            continue
        label = ""
        for c in cells:
            if c.get("sheet")==sh and c.get("row")==row_idx and c.get("type")=="label":
                label=(c.get("label") or c.get("value") or "").lower(); break
        kw_score = sum(len(kw) for kw in cust_kw if kw in label)
        if kw_score == 0:
            continue
        vals = [_num(resolved.get(c["id"]) if resolved.get(c["id"]) is not None else c.get("value")) or 0.0
                for c in numeric]
        s = kw_score * sum(1 for v in vals if v>0)
        if s > best_score:
            best_score = s; best = vals
    return best


# ─────────────────────────────────────────────────────────────────────────────
# Metric computation
# ─────────────────────────────────────────────────────────────────────────────

def _compute_all(
    p: dict[str, float],
    rev_series: list[float],
    cust_series: list[float],
) -> dict[str, float]:
    """
    Given primitive values and optional time series, compute all possible metrics.
    """
    m: dict[str, float] = {}

    # Helpers
    def get(*keys):
        for k in keys:
            v = p.get(k) or m.get(k)
            if v is not None:
                return v
        return None

    def safe_div(a, b):
        if a is None or b is None or b == 0:
            return None
        return a / b

    # ── Revenue series stats ──────────────────────────────────────────────────
    rev = [v for v in rev_series if v is not None and v > 0]

    if rev:
        last = rev[-1]
        first = rev[0]
        n = len(rev)

        # MRR = last monthly revenue
        if not p.get("mrr"):
            m["mrr"] = last

        # ARR = MRR * 12
        if not p.get("arr"):
            m["arr"] = (p.get("mrr") or m.get("mrr", last)) * 12

        # Total revenue = sum of series
        if not p.get("revenue") and not p.get("revenue_month"):
            m["total_revenue"] = sum(rev)
        else:
            m["total_revenue"] = p.get("revenue") or p.get("revenue_month") or sum(rev)

        # MoM growth (last vs second-to-last)
        if n >= 2 and rev[-2] > 0:
            m["revenue_mom"] = (rev[-1] - rev[-2]) / rev[-2] * 100

        # YoY growth (last 12 months vs previous 12)
        if n >= 24:
            last12 = sum(rev[-12:])
            prev12 = sum(rev[-24:-12])
            if prev12 > 0:
                m["revenue_yoy"] = (last12 - prev12) / prev12 * 100
        elif n >= 13:
            if rev[-13] > 0:
                m["revenue_yoy"] = (rev[-1] - rev[-13]) / rev[-13] * 100

        # CAGR
        if n >= 2 and first > 0 and last > 0:
            m["cagr_revenue"] = ((last / first) ** (1 / (n - 1)) - 1) * 100

    # ── Pass through found primitives ─────────────────────────────────────────
    for key in ["mrr","arr","arpu","expansion_rev","contraction_rev",
                "cac","ltv","churn_rate","churn_rev","retention_rate",
                "ebitda","ebit","net_profit","gross_profit","gross_margin_pct",
                "cogs","operating_cf","capex","working_cap","operating_margin",
                "contribution","fixed_costs","variable_costs","total_costs","opex",
                "cash","burn_rate","net_burn","gross_burn",
                "raised","pre_money","post_money","irr","npv","roe","roa","roic",
                "employees","avg_order","roas","roi_marketing","lifespan","months"]:
        if p.get(key) is not None and key not in m:
            m[key] = p[key]

    # Alias
    if not m.get("total_revenue"):
        m["total_revenue"] = get("revenue","revenue_month")

    # ── ARPU ──────────────────────────────────────────────────────────────────
    if not m.get("arpu"):
        rev_v = m.get("mrr") or m.get("total_revenue")
        cust_v = get("customers","subscribers")
        if rev_v and cust_v and cust_v > 0:
            m["arpu"] = rev_v / cust_v

    # ── Customer series ──────────────────────────────────────────────────────
    custs = [v for v in cust_series if v is not None and v > 0]
    if custs and not get("customers","subscribers"):
        m["customers"] = custs[-1]

    # ── MRR / ARR fallback ───────────────────────────────────────────────────
    if not m.get("mrr") and m.get("arpu") and get("customers","subscribers"):
        m["mrr"] = m["arpu"] * get("customers","subscribers")
    if not m.get("arr"):
        if m.get("mrr"):
            m["arr"] = m["mrr"] * 12

    # ── Churn / Retention ────────────────────────────────────────────────────
    churn = m.get("churn_rate")
    if churn is None and custs and len(custs) >= 2:
        # Estimate churn from customer series
        churned_periods = [max(0, custs[i] - custs[i+1]) for i in range(len(custs)-1) if custs[i] > 0]
        if churned_periods:
            avg_start = sum(custs[:-1]) / len(custs[:-1])
            churn = sum(churned_periods) / (len(churned_periods) * avg_start) * 100
            m["churn_rate"] = churn

    if churn is not None:
        churn_dec = churn / 100 if churn > 1 else churn
        if not m.get("retention_rate"):
            m["retention_rate"] = (1 - churn_dec) * 100
        if not m.get("lifespan") and churn_dec > 0:
            m["lifespan"] = 1 / churn_dec

        # LTV = ARPU / churn
        if not m.get("ltv") and m.get("arpu") and churn_dec > 0:
            m["ltv"] = m["arpu"] / churn_dec

    # ── NRR / GRR ─────────────────────────────────────────────────────────────
    if not m.get("nrr") and m.get("mrr"):
        start_mrr = rev[0] if rev else m["mrr"]
        exp = m.get("expansion_rev", 0)
        con = m.get("contraction_rev", 0)
        churn_rev = m.get("churn_rev", (m.get("churn_rate",0)/100 * start_mrr) if start_mrr else 0)
        if start_mrr > 0:
            m["nrr"] = min((start_mrr + exp - con - churn_rev) / start_mrr * 100, 200)
            m["grr"] = max((start_mrr - churn_rev - con) / start_mrr * 100, 0)

    # ── Gross profit / margin ─────────────────────────────────────────────────
    rev_v = m.get("total_revenue") or m.get("mrr", 0)
    cogs_v = m.get("cogs")
    if not cogs_v:
        cogs_v = get("variable_costs")

    if rev_v and cogs_v is not None and not m.get("gross_profit"):
        m["gross_profit"] = rev_v - cogs_v
    if rev_v and not m.get("gross_margin_pct"):
        gp = m.get("gross_profit")
        if gp is not None and rev_v > 0:
            m["gross_margin_pct"] = gp / rev_v * 100
    if rev_v and m.get("gross_margin_pct") and not m.get("gross_profit"):
        m["gross_profit"] = rev_v * m["gross_margin_pct"] / 100

    # ── EBITDA ────────────────────────────────────────────────────────────────
    if not m.get("ebitda"):
        gp = m.get("gross_profit")
        opex = get("opex","fixed_costs")
        if gp is not None and opex is not None:
            m["ebitda"] = gp - opex
        elif rev_v and m.get("total_costs"):
            m["ebitda"] = rev_v - m["total_costs"]

    if rev_v and m.get("ebitda") and not m.get("ebitda_margin"):
        m["ebitda_margin"] = m["ebitda"] / rev_v * 100

    # ── Net profit / margins ──────────────────────────────────────────────────
    if not m.get("net_profit") and m.get("ebitda"):
        m["net_profit"] = m["ebitda"]  # simplification if no taxes/depreciation
    if rev_v and m.get("net_profit") and not m.get("net_margin"):
        m["net_margin"] = m["net_profit"] / rev_v * 100
    if rev_v and m.get("ebit") and not m.get("operating_margin"):
        m["operating_margin"] = m["ebit"] / rev_v * 100
    elif rev_v and m.get("ebitda") and not m.get("operating_margin"):
        m["operating_margin"] = m["ebitda"] / rev_v * 100

    # ── Contribution margin ────────────────────────────────────────────────────
    if not m.get("contribution") and rev_v and cogs_v is not None:
        m["contribution"] = rev_v - cogs_v

    # ── LTV / CAC ─────────────────────────────────────────────────────────────
    if not m.get("ltv_cac") and m.get("ltv") and m.get("cac") and m["cac"] > 0:
        m["ltv_cac"] = m["ltv"] / m["cac"]

    # ── CAC payback ───────────────────────────────────────────────────────────
    if not m.get("cac_payback") and m.get("cac") and m.get("arpu"):
        gm_pct = (m.get("gross_margin_pct", 100)) / 100
        denom = m["arpu"] * gm_pct
        if denom > 0:
            m["cac_payback"] = m["cac"] / denom

    # ── Gross margin / contribution per customer ──────────────────────────────
    cust_v = get("customers","subscribers") or (custs[-1] if custs else None)
    if cust_v and cust_v > 0:
        if m.get("gross_profit") and not m.get("gm_per_customer"):
            m["gm_per_customer"] = m["gross_profit"] / cust_v
        if m.get("contribution") and not m.get("contrib_per_cust"):
            m["contrib_per_cust"] = m["contribution"] / cust_v
        if m.get("cac") and m.get("gm_per_customer") and not m.get("payback_cust"):
            if m["gm_per_customer"] > 0:
                m["payback_cust"] = m["cac"] / m["gm_per_customer"]

    # ── Burn rate / net burn ──────────────────────────────────────────────────
    if not m.get("burn_rate"):
        tot = get("total_costs","opex","fixed_costs")
        if tot:
            m["burn_rate"] = tot
    if not m.get("gross_burn"):
        m["gross_burn"] = m.get("burn_rate")
    if not m.get("net_burn") and m.get("burn_rate") and rev_v:
        nb = m["burn_rate"] - rev_v
        if nb > 0:
            m["net_burn"] = nb

    # ── Cash runway ───────────────────────────────────────────────────────────
    if not m.get("cash_runway"):
        cash_v = m.get("cash")
        burn_v = m.get("net_burn") or m.get("burn_rate")
        if cash_v and burn_v and burn_v > 0:
            m["cash_runway"] = cash_v / burn_v

    if not m.get("cash_balance") and m.get("cash"):
        m["cash_balance"] = m["cash"]

    # ── Operating / free cash flow ─────────────────────────────────────────────
    if not m.get("operating_cf") and m.get("ebitda"):
        m["operating_cf"] = m["ebitda"]
    if not m.get("free_cf") and m.get("operating_cf"):
        capex_v = m.get("capex", 0)
        m["free_cf"] = m["operating_cf"] - capex_v

    # ── Working capital ───────────────────────────────────────────────────────
    # Skip if not found directly

    # ── Valuation multiples ───────────────────────────────────────────────────
    val = m.get("pre_money") or m.get("post_money")
    if val and val > 0:
        arr_v = m.get("arr") or (m.get("mrr",0)*12)
        rev_ann = m.get("total_revenue") or arr_v
        ebitda_v = m.get("ebitda")
        if arr_v and arr_v > 0 and not m.get("arr_multiple"):
            m["arr_multiple"] = val / arr_v
        if rev_ann and rev_ann > 0 and not m.get("revenue_multiple"):
            m["revenue_multiple"] = val / rev_ann
        if ebitda_v and ebitda_v > 0 and not m.get("ebitda_multiple"):
            m["ebitda_multiple"] = val / ebitda_v

    # ── Post-money = pre-money + raised ───────────────────────────────────────
    if not m.get("post_money") and m.get("pre_money") and m.get("raised"):
        m["post_money"] = m["pre_money"] + m["raised"]
    if not m.get("runway_post_round") and m.get("post_money") and m.get("burn_rate"):
        if m["burn_rate"] > 0:
            m["runway_post_round"] = m.get("raised", m["post_money"]) / m["burn_rate"]

    # ── Operating leverage ─────────────────────────────────────────────────────
    if m.get("ebitda") and m.get("gross_profit") and m["gross_profit"] != 0:
        m["operating_leverage"] = m["ebitda"] / m["gross_profit"]

    # Filter out nonsensical values
    return {k: v for k, v in m.items() if v is not None and not (isinstance(v, float) and (math.isnan(v) or math.isinf(v)))}


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def extract_business_metrics(
    cells: list[dict],
    resolved_values: dict[str, Any],
) -> list[dict]:
    """Returns all computable metrics as a list, organised by category."""
    primitives = _find_primitives(cells, resolved_values)
    rev_series  = _find_revenue_series(cells, resolved_values)
    cust_series = _find_customer_series(cells, resolved_values)

    computed = _compute_all(primitives, rev_series, cust_series)

    results: list[dict] = []
    for metric_id, meta in METRIC_META.items():
        val = computed.get(metric_id)
        if val is None:
            continue
        try:
            val = float(val)
        except (TypeError, ValueError):
            continue
        if math.isnan(val) or math.isinf(val):
            continue

        results.append({
            "id":       metric_id,
            "label":    meta["label"],
            "value":    val,
            "category": meta["cat"],
            "unit":     meta["unit"],
            "fmt":      meta["fmt"],
            "description": _describe(metric_id, val, computed),
            "cell_id":  None,
        })

    # Attach category metadata for the frontend
    return results


def _describe(mid: str, val: float, m: dict) -> str:
    fv = f"{val:,.1f}"
    descs = {
        "mrr":           f"Ricavo ricorrente mensile: € {val:,.0f}",
        "arr":           f"Proiezione annua ricorrente: € {val:,.0f}",
        "revenue_mom":   f"Il fatturato cresce del {val:.1f}% ogni mese rispetto al mese precedente",
        "revenue_yoy":   f"Crescita annua: {val:.1f}%",
        "cagr_revenue":  f"Tasso di crescita annuo composto (CAGR): {val:.1f}%",
        "arpu":          f"Ogni cliente genera in media € {val:,.2f} al mese",
        "nrr":           f"NRR {val:.1f}% — {'ottimo, cresci senza nuovi clienti' if val>=110 else 'inferiore al 100%, perdi ricavi dalla base esistente' if val<100 else 'stabile'}",
        "grr":           f"Il {val:.1f}% dei ricavi esistenti viene trattenuto (escl. espansione)",
        "cac":           f"Costo medio per acquisire un cliente: € {val:,.0f}",
        "cac_payback":   f"Recuperi il costo di acquisizione in {val:.1f} mesi",
        "ltv":           f"Valore totale generato da un cliente: € {val:,.0f}",
        "ltv_cac":       f"{'Eccellente (>3x)' if val>=3 else 'Attenzione (<3x)'}: per ogni € investito ne recuperi {val:.1f}x",
        "gross_margin_pct": f"Ogni € di ricavo lascia {val:.1f}¢ dopo i costi diretti",
        "ebitda_margin": f"Margine EBITDA: {val:.1f}% del fatturato",
        "net_margin":    f"Utile netto: {val:.1f}% del fatturato",
        "burn_rate":     f"L'azienda consuma € {val:,.0f} al mese",
        "cash_runway":   f"{'⚠️ Critico (<6 mesi)' if val<6 else '✅ Sano (>12 mesi)' if val>=12 else '⚠️ Attenzione (<12 mesi)'}: {val:.0f} mesi di autonomia",
        "revenue_multiple": f"Valutazione = {val:.1f}x i ricavi annuali (benchmark: 5-15x per SaaS early stage)",
        "arr_multiple":  f"Valutazione = {val:.1f}x ARR",
        "ltv_cac": f"Rapporto LTV/CAC = {val:.2f}x — target investitori: ≥3x",
    }
    return descs.get(mid, "")


def extract_time_series(
    cells: list[dict],
    resolved_values: dict[str, Any],
    sheet: str | None = None,
) -> list[dict]:
    rev_kw  = ["fatturato","ricavi","revenue","entrate","incassi","ricavo mensile"]
    cost_kw = ["costi","spese","costs","expenses","uscite","costo"]
    prof_kw = ["utile","profit","margine","ebitda","risultato"]
    user_kw = ["utenti","abbonamenti","clienti","users","subscribers"]
    cf_kw   = ["cash flow","cashflow","flusso","saldo cassa"]

    row_groups: dict[tuple, list[dict]] = {}
    for c in cells:
        if c.get("type") == "label":
            continue
        row_groups.setdefault((c.get("sheet",""), c.get("row",0)), []).append(c)

    out: list[dict] = []
    seen: set[str] = set()
    for (sh, row_idx), row_cells in row_groups.items():
        if sheet and sh != sheet:
            continue
        numeric = sorted([c for c in row_cells if c.get("data_type") in ("number","currency","percentage")],
                         key=lambda c: c.get("col",0))
        if len(numeric) < 3:
            continue
        label = ""
        for c in cells:
            if c.get("sheet")==sh and c.get("row")==row_idx and c.get("type")=="label":
                label = (c.get("label") or c.get("value") or "")
                if label: break
        label_l = label.lower()
        if label_l in seen or not label:
            continue
        seen.add(label_l)
        vals = [_num(resolved_values.get(c["id"]) if resolved_values.get(c["id"]) is not None else c.get("value")) or 0.0
                for c in numeric]
        if len(set(vals)) <= 1 or all(v == 0 for v in vals):
            continue
        cat = "other"
        if any(k in label_l for k in rev_kw): cat="revenue"
        elif any(k in label_l for k in cost_kw): cat="costs"
        elif any(k in label_l for k in prof_kw): cat="profit"
        elif any(k in label_l for k in user_kw): cat="users"
        elif any(k in label_l for k in cf_kw): cat="cashflow"
        out.append({"label":label,"category":cat,"series":vals[:24],"n_periods":min(len(vals),24),"sheet":sh,"row":row_idx})

    order={"revenue":0,"profit":1,"users":2,"costs":3,"cashflow":4,"other":5}
    out.sort(key=lambda s:order.get(s["category"],9))
    return out[:20]


def extract_scenario_params(
    cells: list[dict],
    resolved_values: dict[str, Any],
    dependency_graph: dict[str, list[str]],
) -> list[dict]:
    _PARAM_KW = [
        (["prezzo","price","tariffa","fee mensile","canone mensile","subscription price"], "Prezzo mensile per utente"),
        (["churn","tasso abbandono","abbandono mensile"],                                  "Tasso di churn mensile"),
        (["tasso di crescita","crescita mensile","growth rate"],                           "Tasso di crescita mensile"),
        (["cac","costo acquisizione"],                                                     "CAC – Costo acquisizione cliente"),
        (["utenti iniziali","starting users","utenti mese 1","clienti iniziali"],          "Utenti di partenza"),
        (["costi fissi","fixed cost","overhead"],                                          "Costi fissi mensili"),
        (["stipendi","salary","costo personale"],                                          "Costo personale"),
        (["marketing","pubblicità","ads"],                                                 "Budget marketing mensile"),
        (["canone broker","fee broker","broker fee"],                                      "Fee broker"),
        (["royalt","licenza"],                                                             "Royalty / Licenze"),
        (["cloud","server","hosting","infrastruttura"],                                    "Infrastruttura / Cloud"),
        (["mesi","durata","periodo proiezione"],                                           "Durata proiezione (mesi)"),
    ]

    static_cells = [c for c in cells if c.get("type") == "static"]

    def downstream(cid, graph, depth=0, visited=None):
        if visited is None: visited = set()
        if cid in visited or depth > 5: return 0
        visited.add(cid)
        return sum(1 + downstream(n, graph, depth+1, visited)
                   for n, deps in graph.items() if cid in deps and n not in visited)

    scored = []
    for c in static_cells:
        cid = c["id"]
        raw = resolved_values.get(cid) if resolved_values.get(cid) is not None else c.get("value")
        v = _num(raw)
        if v is None or v == 0: continue
        label = c.get("label", "")
        label_l = label.lower()
        dep_score = downstream(cid, dependency_graph)
        friendly = None
        param_score = 0.0
        for kws, fl in _PARAM_KW:
            if any(k in label_l for k in kws):
                param_score = 15.0; friendly = fl; break
        total = dep_score + param_score
        if total > 0:
            scored.append((total, c, v, friendly))

    scored.sort(key=lambda x: -x[0])
    params, seen_labels = [], set()
    for score, c, val, friendly in scored[:10]:
        label = friendly or c.get("label", c["id"])
        if label in seen_labels: continue
        seen_labels.add(label)
        abs_v = abs(val)
        if abs_v < 1:     step=0.001; lo=0; hi=max(val*5,1.0)
        elif abs_v < 10:  step=0.1;   lo=max(0,val*.1); hi=val*5
        elif abs_v < 1000:step=1;     lo=max(0,val*.1); hi=val*5
        elif abs_v<100000:step=100;   lo=max(0,val*.1); hi=val*5
        else:             step=1000;  lo=max(0,val*.1); hi=val*5
        label_l = label.lower()
        unit = "%" if any(k in label_l for k in ["churn","tasso","rate","%"]) else \
               "mesi" if any(k in label_l for k in ["mesi","months","durata"]) else \
               "€" if c.get("data_type")=="currency" else ""
        params.append({"cell_id":c["id"],"label":label,"value":val,
                        "min":lo,"max":hi,"step":step,"unit":unit,
                        "description":f"Modifica «{label}» per vedere l'impatto su tutti gli indicatori"})
    return params
