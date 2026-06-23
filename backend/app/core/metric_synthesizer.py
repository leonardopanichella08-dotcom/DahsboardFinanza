"""
Synthetic metric generation engine.
Scans the parsed sheet for financial primitives and derives standard KPIs
that may not be explicitly modeled in the original spreadsheet.
"""
from dataclasses import dataclass
from typing import Any, Optional
import re

from app.models.simulation import SyntheticMetric


@dataclass
class _Candidate:
    keywords: list[str]
    cell_id: Optional[str] = None
    value: Optional[Any] = None


def _fuzzy_find(
    label_values: dict[str, tuple[str, Any]],
    keywords: list[str],
) -> Optional[tuple[str, Any]]:
    """
    Search label_values (cell_id -> (label, value)) for a cell whose label
    contains any of the keywords (case-insensitive).
    """
    for cid, (label, val) in label_values.items():
        label_lower = label.lower()
        if any(kw in label_lower for kw in keywords):
            return cid, val
    return None


def synthesize_metrics(
    label_values: dict[str, tuple[str, Any]],  # cell_id -> (label, resolved_value)
) -> list[SyntheticMetric]:
    """
    Attempt to derive missing standard KPIs from raw cell data.
    Returns only metrics that could be meaningfully computed.
    """
    metrics: list[SyntheticMetric] = []

    def _num(result: Optional[tuple]) -> Optional[float]:
        if result is None:
            return None
        try:
            return float(result[1])
        except (TypeError, ValueError):
            return None

    def _id(result: Optional[tuple]) -> Optional[str]:
        return result[0] if result else None

    # --- Revenue & Cost primitives ---
    revenue_r   = _fuzzy_find(label_values, ["revenue", "sales", "income", "ricavi"])
    cogs_r      = _fuzzy_find(label_values, ["cogs", "cost of goods", "costo del venduto"])
    total_cost_r = _fuzzy_find(label_values, ["total cost", "costi totali", "expenses", "spese"])
    fixed_cost_r = _fuzzy_find(label_values, ["fixed cost", "costi fissi", "overhead"])
    variable_cost_r = _fuzzy_find(label_values, ["variable cost", "costi variabili"])
    customers_r = _fuzzy_find(label_values, ["customers", "clienti", "users", "utenti"])
    cac_r       = _fuzzy_find(label_values, ["cac", "acquisition cost", "costo acquisizione"])
    ltv_r       = _fuzzy_find(label_values, ["ltv", "lifetime value", "clv"])
    churn_r     = _fuzzy_find(label_values, ["churn", "abbandono", "cancellation"])
    arpu_r      = _fuzzy_find(label_values, ["arpu", "average revenue per user", "revenue per user"])
    cash_r      = _fuzzy_find(label_values, ["cash", "cassa", "liquidity", "liquidità"])
    burn_r      = _fuzzy_find(label_values, ["burn", "monthly burn", "burn rate"])
    margin_r    = _fuzzy_find(label_values, ["gross margin", "margine lordo"])

    revenue = _num(revenue_r)
    cogs    = _num(cogs_r)
    total_cost = _num(total_cost_r)
    fixed_cost = _num(fixed_cost_r)
    variable_cost = _num(variable_cost_r)
    customers  = _num(customers_r)
    cac        = _num(cac_r)
    ltv        = _num(ltv_r)
    churn      = _num(churn_r)
    arpu       = _num(arpu_r)
    cash       = _num(cash_r)
    burn       = _num(burn_r)

    # --- Gross Margin % ---
    if revenue and cogs and revenue != 0:
        gm = (revenue - cogs) / revenue * 100
        metrics.append(SyntheticMetric(
            id="synthetic_gross_margin_pct",
            label="Gross Margin %",
            value=round(gm, 2),
            formula_used="(Revenue - COGS) / Revenue × 100",
            explanation=f"Gross Margin % = ({revenue:,.0f} - {cogs:,.0f}) / {revenue:,.0f} × 100 = {gm:.1f}%",
            why_it_matters="Measures how efficiently you produce your product. Below 40% for SaaS or 20% for retail signals pricing/cost pressure.",
            source_cells=[_id(revenue_r), _id(cogs_r)],
            is_ai_generated=True,
        ))

    # --- LTV/CAC Ratio ---
    if ltv and cac and cac != 0:
        ratio = ltv / cac
        metrics.append(SyntheticMetric(
            id="synthetic_ltv_cac",
            label="LTV / CAC Ratio",
            value=round(ratio, 2),
            formula_used="LTV / CAC",
            explanation=f"LTV/CAC = {ltv:,.0f} / {cac:,.0f} = {ratio:.2f}x",
            why_it_matters="A ratio > 3x indicates healthy unit economics. Below 1x means you lose money on every customer.",
            source_cells=[_id(ltv_r), _id(cac_r)],
        ))
    elif arpu and churn and churn != 0 and cac:
        # Derive LTV from ARPU and churn
        derived_ltv = arpu / churn
        ratio = derived_ltv / cac
        metrics.append(SyntheticMetric(
            id="synthetic_ltv_cac",
            label="LTV / CAC Ratio (derived)",
            value=round(ratio, 2),
            formula_used="(ARPU / Churn Rate) / CAC",
            explanation=f"LTV = {arpu:.0f} / {churn:.3f} = {derived_ltv:,.0f}; LTV/CAC = {ratio:.2f}x",
            why_it_matters="A ratio > 3x indicates healthy unit economics. Below 1x means you lose money on every customer.",
            source_cells=[_id(arpu_r), _id(churn_r), _id(cac_r)],
        ))

    # --- Break-Even Point ---
    if fixed_cost and variable_cost and revenue and customers and customers != 0:
        price_per_unit = revenue / customers
        vc_per_unit = variable_cost / customers
        if (price_per_unit - vc_per_unit) != 0:
            breakeven = fixed_cost / (price_per_unit - vc_per_unit)
            metrics.append(SyntheticMetric(
                id="synthetic_breakeven",
                label="Break-Even Units",
                value=round(breakeven, 0),
                formula_used="Fixed Costs / (Price per Unit − Variable Cost per Unit)",
                explanation=f"BEP = {fixed_cost:,.0f} / ({price_per_unit:,.2f} − {vc_per_unit:,.2f}) = {breakeven:,.0f} units",
                why_it_matters="The minimum sales volume needed to cover all costs. Crossing this threshold means every additional unit is profit.",
                source_cells=[_id(fixed_cost_r), _id(variable_cost_r), _id(revenue_r), _id(customers_r)],
            ))
    elif fixed_cost and revenue and total_cost and revenue != 0:
        # Margin-based break-even
        contrib_margin_ratio = (revenue - (total_cost - (fixed_cost or 0))) / revenue
        if contrib_margin_ratio > 0:
            be_revenue = fixed_cost / contrib_margin_ratio
            metrics.append(SyntheticMetric(
                id="synthetic_breakeven_revenue",
                label="Break-Even Revenue",
                value=round(be_revenue, 2),
                formula_used="Fixed Costs / Contribution Margin Ratio",
                explanation=f"BEP Revenue = {fixed_cost:,.0f} / {contrib_margin_ratio:.2%} = {be_revenue:,.0f}",
                why_it_matters="The minimum revenue needed before the business becomes profitable.",
                source_cells=[_id(fixed_cost_r), _id(revenue_r), _id(total_cost_r)],
            ))

    # --- Cash Runway ---
    if cash and burn and burn != 0:
        runway_months = cash / burn
        metrics.append(SyntheticMetric(
            id="synthetic_runway",
            label="Cash Runway (months)",
            value=round(runway_months, 1),
            formula_used="Cash / Monthly Burn Rate",
            explanation=f"Runway = {cash:,.0f} / {burn:,.0f} = {runway_months:.1f} months",
            why_it_matters="How long the company can operate without new revenue or funding. < 6 months is a critical warning zone.",
            source_cells=[_id(cash_r), _id(burn_r)],
        ))

    # --- Churn-implied Avg Customer Lifetime ---
    if churn and churn != 0:
        lifetime = 1 / churn
        metrics.append(SyntheticMetric(
            id="synthetic_customer_lifetime",
            label="Avg Customer Lifetime (months)",
            value=round(lifetime, 1),
            formula_used="1 / Monthly Churn Rate",
            explanation=f"Lifetime = 1 / {churn:.3f} = {lifetime:.1f} months",
            why_it_matters="Higher churn means shorter customer life, reducing LTV and requiring more CAC spend to maintain revenue.",
            source_cells=[_id(churn_r)],
        ))

    # Filter out metrics with None source cells
    return [
        m for m in metrics
        if all(s is not None for s in m.source_cells)
    ]
