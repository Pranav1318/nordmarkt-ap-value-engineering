# Nordmarkt Retail — AP Value Engineering Demo

A Streamlit prototype for a fictional German mid-sized grocery and household retailer. It adapts the user's original BLP Value Engineering Agent concept: upload AP transactions, analyse baseline effort, model automation, calculate released capacity, and export a CFO-facing value case.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy publicly (no localhost link)
1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `sample_invoices.csv`.
2. Sign in to https://share.streamlit.io/ with GitHub.
3. Select the repository, branch, and `app.py` as the main file.
4. Deploy. Streamlit Community Cloud will provide a public `*.streamlit.app` URL that anyone with the link can open.
5. Confirm the app is set to public and test the URL in a private/incognito browser window.

The project is deployment-ready, but no public URL is created until the repository is connected and deployed under an account. Do not represent a localhost address as a public link.

## Evidence register and how each number is used

| Number / claim | Source | Use and limitation |
|---|---|---|
| ~5 min manual invoice indexing; ~25 sec after automation; 60% touchless extraction; 21 sec annotation; 14 FTE redeployed | [Rossum Kingfisher case](https://rossum.ai/customer-stories/kingfisher/) | Retail implementation reference from a large European retailer. Indexing only, not end-to-end AP processing. |
| €43.80 / hour | [Destatis / Eurostat-based 2025 labour-cost comparison](https://www.destatis.de/Europa/EN/Topic/Population-Labour-Social-Issues/Labour-market/EU_LabourCostPerHourWorked.html) | Germany services NACE G–N proxy; not AP-specific retail labour cost. Editable in app. |
| 9–24 minutes per incoming invoice; 0.7 FTE supporting AP at an average medium-sized firm | [IDC InfoBrief, p.11](https://sipp-content-uk.dystrick.com/wp-content/uploads/2023/10/idc-digitizing-accounts-payable-receivable-to-boost-efficiency-enable-growth-report.pdf) | Contextual cross-check only. Underlying survey covers UK and US; not EU-wide. |
| Germany B2B structured e-invoice receiving requirement from 1 Jan 2025; transitional issuance rules | [German Federal Ministry of Finance FAQ](https://www.bundesfinanzministerium.de/Content/DE/FAQ/e-rechnung.html) | German operating context. Check current official guidance for legal implementation. |
| ViDA adopted March 2025; cross-border B2B digital reporting from 1 July 2030 | [European Commission — ViDA](https://taxation-customs.ec.europa.eu/taxation/vat/vat-digital-age-vida_en) | EU regulatory context. |

## Explicit modelling assumptions (not public facts)
- Nordmarkt is fictional.
- 24,000 annual invoices is a scenario input, not a sourced retail average.
- 1,720 productive hours per FTE per year is an editable planning assumption.
- The model uses Kingfisher's indexing benchmark as an illustrative reference, not a promise of the same outcome.
- Implementation and annual platform costs default to zero because no BLP/customer quote is available. Enter validated costs before calculating payback.
- Capacity value is not automatically cash savings; realization requires a credible operational plan.

## CSV upload schema
Minimum required columns: `processing_minutes`, `hourly_cost_eur`.
Optional fields from the original prototype are preserved in the sample: `invoice_id`, `supplier`, `is_manual`, `is_exception`, `invoice_amount_eur`, `invoice_type`, `channel`, `country`.

All sample invoice rows are synthetic and must not be presented as real customer data.
