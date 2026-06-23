"""
Prompt templates for Claude API calls.
All prompts are designed to be concise, structured, and return JSON.
"""

SYSTEM_PROMPT = """You are a senior financial analyst and business advisor embedded in a financial simulation dashboard.
Your role is to explain financial metrics, formulas, and KPIs in plain English to founders, operators, and investors.
Always be precise, actionable, and concise. When asked for JSON, return ONLY valid JSON with no markdown fences."""


def explain_metric_prompt(label: str, value: str, data_type: str, context: str) -> str:
    return f"""Explain this financial metric from a business plan spreadsheet.

Metric: {label}
Current Value: {value}
Data Type: {data_type}
Context (nearby cells): {context}

Return a JSON object with exactly these fields:
{{
  "what_it_means": "1-2 sentence plain-English definition of this metric",
  "business_impact": "1-2 sentences on how this metric affects business health and decision-making",
  "sensitivity": "1-2 sentences on what happens if this number increases or decreases significantly"
}}"""


def missing_metrics_prompt(available_labels: list[str]) -> str:
    labels_str = ", ".join(available_labels[:40])
    return f"""A financial spreadsheet contains these labeled values: {labels_str}

Identify which standard financial KPIs from this list are MISSING but could be derived from the available data:
- Gross Margin %, Net Margin %, EBITDA, LTV/CAC Ratio, Break-Even Point, Cash Runway,
- Payback Period, MoM Growth Rate, Annual Recurring Revenue (ARR), Burn Multiple

For each missing metric that CAN be derived, return a JSON array:
[
  {{
    "metric": "metric name",
    "can_derive": true,
    "ingredients_needed": ["label1", "label2"],
    "formula": "plain formula description"
  }}
]
Return an empty array [] if nothing is missing."""


def formula_explanation_prompt(formula: str, label: str, dependencies: list[str]) -> str:
    deps_str = ", ".join(dependencies) if dependencies else "none"
    return f"""Explain this Excel formula from a financial model.

Cell: {label}
Excel Formula: {formula}
Depends on: {deps_str}

Return JSON:
{{
  "plain_english": "What this formula calculates in one sentence",
  "step_by_step": "Brief explanation of each component",
  "common_pitfalls": "One sentence on what could go wrong or what to watch for"
}}"""
