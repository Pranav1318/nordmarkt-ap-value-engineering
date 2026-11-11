import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

st.set_page_config(page_title="Nordmarkt | AP Value Case", page_icon="🛒", layout="wide")

# Public evidence register: links are shown in the app and in README.
SOURCES = {
    "kingfisher": {
        "label": "Rossum — Kingfisher retail AP case study",
        "url": "https://rossum.ai/customer-stories/kingfisher/",
        "facts": "Kingfisher reports ~5 minutes manual SAP invoice indexing, 25 seconds after automation, 60% touchless data extraction, 21 seconds average annotation time, and 14 FTE redeployed."
    },
    "destatis": {
        "label": "Destatis / Eurostat — 2025 hourly labour costs by sector",
        "url": "https://www.destatis.de/Europa/EN/Topic/Population-Labour-Social-Issues/Labour-market/EU_LabourCostPerHourWorked.html",
        "facts": "Germany's 2025 hourly labour cost for services (NACE G–N) is €43.80. This is a broad services-sector proxy, not a retail-AP wage."
    },
    "idc": {
        "label": "IDC InfoBrief — Digitizing Accounts Payable and Receivable (2022)",
        "url": "https://sipp-content-uk.dystrick.com/wp-content/uploads/2023/10/idc-digitizing-accounts-payable-receivable-to-boost-efficiency-enable-growth-report.pdf",
        "facts": "Page 11 reports 9–24 minutes per incoming invoice and 0.7 AP FTE for medium-sized businesses (n=207). The underlying survey covered UK and US companies, not the EU as a whole."
    },
    "bmd": {
        "label": "German Federal Ministry of Finance — E-invoice FAQ (March 2026)",
        "url": "https://www.bundesfinanzministerium.de/Content/DE/FAQ/e-rechnung.html",
        "facts": "German domestic businesses must be able to receive structured e-invoices from 1 January 2025; transitional rules apply to issuing."
    },
    "vida": {
        "label": "European Commission — VAT in the Digital Age (ViDA)",
        "url": "https://taxation-customs.ec.europa.eu/taxation/vat/vat-digital-age-vida_en",
        "facts": "ViDA was adopted in March 2025; EU cross-border B2B digital reporting requirements start from 1 July 2030."
    }
}

st.title("🛒 Nordmarkt Retail | AP Value Engineering")
st.caption("Fictional German mid-sized retailer · Accounts payable invoice-indexing value case · Public evidence + editable scenario assumptions")

with st.sidebar:
    st.header("Scenario controls")
    st.caption("Blue labels are externally sourced reference points. Editable scenario inputs are assumptions, not market facts.")
    annual_volume = st.number_input("Annual incoming invoices", min_value=1000, max_value=500000, value=24000, step=1000)
    baseline_minutes = st.number_input("Current manual indexing time (min / invoice)", min_value=0.1, max_value=60.0, value=5.0, step=0.5)
    target_minutes = st.number_input("Future average indexing time (min / invoice)", min_value=0.0, max_value=30.0, value=25/60, step=0.05, format="%.2f")
    touchless_rate = st.slider("Touchless data-extraction rate (%)", 0, 100, 60, 5)
    labour_rate = st.number_input("Employer labour-cost proxy (€ / hour)", min_value=0.0, max_value=200.0, value=43.8, step=1.0)
    productive_hours = st.number_input("Productive hours per FTE / year", min_value=500, max_value=2200, value=1720, step=20)
    st.divider()
    st.subheader("Optional cost inputs")
    implementation_cost = st.number_input("One-time implementation (€)", min_value=0, value=0, step=5000)
    annual_platform_cost = st.number_input("Annual platform / operating cost (€)", min_value=0, value=0, step=1000)
    st.caption("Costs default to €0 because no public BLP quote or customer-specific implementation estimate is available. Enter validated quote values to calculate payback.")

st.markdown("### Scenario profile")
c1, c2, c3 = st.columns(3)
c1.metric("Industry", "Grocery & household retail")
c2.metric("Geography", "Germany / EU context")
c3.metric("Company", "Fictional mid-market retailer")
st.info("This is a modelled scenario, not a real Nordmarkt company or BLP customer. Public Kingfisher data is used as a retail reference point; Nordmarkt's annual volume and staffing assumptions are illustrative.")

# Optional customer data upload; otherwise benchmark scenario.
st.markdown("### 1. Baseline")
uploaded = st.file_uploader("Optional: upload AP transaction sample (CSV)", type=["csv"])
use_uploaded = uploaded is not None
if use_uploaded:
    df = pd.read_csv(uploaded)
    required = {"processing_minutes", "hourly_cost_eur"}
    missing = required - set(df.columns)
    if missing:
        st.error("CSV must include: processing_minutes, hourly_cost_eur")
        st.stop()
    df["processing_minutes"] = pd.to_numeric(df["processing_minutes"], errors="coerce")
    df["hourly_cost_eur"] = pd.to_numeric(df["hourly_cost_eur"], errors="coerce")
    df = df.dropna(subset=["processing_minutes", "hourly_cost_eur"])
    df = df[(df.processing_minutes >= 0) & (df.hourly_cost_eur >= 0)]
    if df.empty:
        st.error("No valid rows after validation.")
        st.stop()
    observed_minutes = float(df.processing_minutes.mean())
    observed_rate = float(df.hourly_cost_eur.mean())
    current_minutes = observed_minutes
    current_labour_rate = observed_rate
    st.caption(f"Uploaded dataset: {len(df):,} rows. The model uses the sample mean processing time and hourly cost, extrapolated to the annual volume above.")
else:
    current_minutes = float(baseline_minutes)
    current_labour_rate = float(labour_rate)
    st.caption("No customer file uploaded. The default baseline uses Kingfisher's published manual indexing time (5 minutes), not a claim about all AP processing.")

# Calculations
post_minutes = float(target_minutes)
minutes_saved_per_invoice = max(current_minutes - post_minutes, 0)
annual_minutes_saved = annual_volume * minutes_saved_per_invoice
annual_hours_saved = annual_minutes_saved / 60
fte_released = annual_hours_saved / productive_hours if productive_hours else 0
gross_capacity_value = annual_hours_saved * current_labour_rate
net_annual_capacity_value = gross_capacity_value - annual_platform_cost
first_year_capacity_value = gross_capacity_value - annual_platform_cost - implementation_cost
reduction_pct = (minutes_saved_per_invoice / current_minutes * 100) if current_minutes > 0 else 0
payback_months = (implementation_cost / (gross_capacity_value - annual_platform_cost) * 12
                  if implementation_cost > 0 and gross_capacity_value > annual_platform_cost else None)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Annual invoices", f"{annual_volume:,.0f}")
k2.metric("Current indexing time", f"{current_minutes:.2f} min")
k3.metric("Modelled time reduction", f"{reduction_pct:.1f}%")
k4.metric("Touchless extraction target", f"{touchless_rate}%")

st.markdown("### 2. Automation scenario")
a, b, c, d = st.columns(4)
a.metric("Hours released / year", f"{annual_hours_saved:,.0f} h")
b.metric("FTE capacity equivalent", f"{fte_released:.2f}")
c.metric("Gross capacity value", f"€{gross_capacity_value:,.0f}")
d.metric("First-year value after entered costs", f"€{first_year_capacity_value:,.0f}")

st.caption("Calculation: annual invoices × (current minutes − future minutes) ÷ 60 = annual hours released. Gross capacity value = hours released × employer labour-cost proxy. FTE equivalent = hours released ÷ productive hours per FTE. The touchless-rate slider is a separate operational KPI; it is not multiplied into the time-saved formula because the 25-second Kingfisher figure is already an observed average post-automation indexing time.")

st.markdown("### 3. Transparent value bridge")
bridge = pd.DataFrame([
    ["Annual invoice volume", annual_volume, "Scenario assumption"],
    ["Current indexing effort", current_minutes, "Kingfisher retail case: ~5 min; or uploaded sample mean"],
    ["Future indexing effort", post_minutes, "Kingfisher case: ~25 sec; editable scenario input"],
    ["Annual hours released", annual_hours_saved, "Calculated"],
    ["Employer labour-cost proxy", current_labour_rate, "Germany services NACE G–N, 2025; broad proxy"],
    ["Gross annual capacity value (€)", gross_capacity_value, "Calculated; not automatically cash savings"],
    ["Annual platform / operating cost (€)", annual_platform_cost, "User-entered; €0 until quoted"],
    ["One-time implementation cost (€)", implementation_cost, "User-entered; €0 until quoted"],
    ["First-year capacity value after entered costs (€)", first_year_capacity_value, "Calculated; not a validated ROI"],
], columns=["Metric", "Value", "Evidence / status"])
st.dataframe(bridge, use_container_width=True, hide_index=True)

if payback_months is not None:
    st.success(f"Indicative payback: {payback_months:.1f} months, using user-entered implementation and annual operating costs.")
elif implementation_cost == 0 and annual_platform_cost == 0:
    st.warning("Payback is not calculated: implementation and platform costs have not been supplied. Current output is gross capacity value only.")
else:
    st.warning("Payback is not positive under the entered cost assumptions.")

st.warning("Capacity released is not the same as cash saved. Financial savings require a documented action such as avoided hiring, reduced overtime, lower outsourcing, or redeployment into work that otherwise requires additional spend.")

st.markdown("### 4. Evidence and European operating context")
with st.expander("Retail implementation reference — Kingfisher", expanded=True):
    st.write("Kingfisher is a major European home-improvement retailer. Its published case reports 40,000 invoices per month across six countries, approximately five minutes of manual SAP indexing per invoice, 25 seconds after automation, 60% touchless data extraction, 21 seconds average annotation time, and 14 FTE redeployed.")
    st.markdown(f"[Open source: {SOURCES['kingfisher']['label']}]({SOURCES['kingfisher']['url']})")
    st.caption("Important: Kingfisher is a large retailer. These are a real implementation reference, not a mid-market benchmark or guaranteed Nordmarkt outcome.")
with st.expander("Medium-sized business cross-check — IDC"):
    st.write("IDC's 2022 InfoBrief reports 9–24 minutes spent processing each incoming invoice and 0.7 FTE supporting AP at an average medium-sized firm. The underlying October 2021 survey included 207 medium-sized businesses, but the survey covered the UK and US. Do not present this as EU-wide data.")
    st.markdown(f"[Open source: {SOURCES['idc']['label']}]({SOURCES['idc']['url']})")
with st.expander("Germany e-invoicing requirements"):
    st.write("From 1 January 2025, German domestic businesses must be able to receive structured e-invoices. Transitional rules continue to apply to invoice issuance. The scenario therefore includes structured e-invoice, EDI, PDF/email and paper intake as possible channels; exact supplier and format mix must be discovered.")
    st.markdown(f"[Open source: {SOURCES['bmd']['label']}]({SOURCES['bmd']['url']})")
with st.expander("EU VAT in the Digital Age"):
    st.write("The European Commission says ViDA was adopted in March 2025 and cross-border B2B digital reporting requirements take effect from 1 July 2030.")
    st.markdown(f"[Open source: {SOURCES['vida']['label']}]({SOURCES['vida']['url']})")
with st.expander("Labour-cost proxy"):
    st.write("The default €43.80/hour is Germany's 2025 average hourly labour cost for services (NACE G–N), as reported in Destatis' Eurostat-based comparison. This is not a retail AP employee-specific rate; replace it with Nordmarkt's fully loaded finance/AP cost.")
    st.markdown(f"[Open source: {SOURCES['destatis']['label']}]({SOURCES['destatis']['url']})")

st.markdown("### 5. Recommended discovery questions")
st.markdown("""
- What is the actual annual invoice count by store, supplier and invoice type?
- What proportion is PO-backed versus non-PO, EDI / structured e-invoice versus PDF or paper?
- What is the measured touch time for capture, coding, matching, approvals and exception resolution?
- Which exceptions dominate: missing PO, price / quantity mismatch, duplicate, tax validation or missing master data?
- Which ERP and integration interfaces are in scope, and what is the write-back / audit requirement?
- Who owns released capacity, and how will it translate into avoided cost or additional throughput?
""")

st.markdown("### 6. Export")
summary = f"""# Nordmarkt Retail — AP value case

Fictional German mid-sized retailer. Scenario only; not a real customer or BLP quote.

## Inputs
- Annual invoice volume: {annual_volume:,.0f} (editable scenario assumption)
- Current indexing time: {current_minutes:.2f} minutes / invoice
- Future indexing time: {post_minutes:.2f} minutes / invoice
- Labour-cost proxy: €{current_labour_rate:.2f} / hour
- Touchless extraction target: {touchless_rate}%
- Productive hours per FTE: {productive_hours:,} / year (editable modelling assumption)

## Calculated outputs
- Annual hours released: {annual_hours_saved:,.1f}
- FTE capacity equivalent: {fte_released:.2f}
- Gross annual capacity value: €{gross_capacity_value:,.2f}
- First-year capacity value after entered costs: €{first_year_capacity_value:,.2f}
- Modelled indexing-time reduction: {reduction_pct:.1f}%

## Caveats
- Kingfisher's 5-minute and 25-second figures concern invoice indexing into SAP, not end-to-end AP approval/payment cycle time.
- Kingfisher is a large retailer; its results are not guaranteed for a fictional mid-sized retailer.
- €43.80/hour is a Germany-wide services-sector labour-cost proxy (NACE G–N), not an AP-specific retail rate.
- Annual volume and productive hours are scenario assumptions.
- Capacity released is not cash saved without an operational realization plan.
- No BLP licence, implementation quote, integration estimate, tax/legal opinion or customer data has been supplied.
"""
st.download_button("Download value case (Markdown)", summary, file_name="nordmarkt_ap_value_case.md", mime="text/markdown")

st.caption("Prototype purpose: interview / take-home demonstration. Calculations are deterministic; no LLM is used to calculate financial outputs.")
