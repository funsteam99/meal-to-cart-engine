# Dashboard SQL Validation

Validation date: 2026-05-18

Production table:

```text
subtle-fulcrum-496004-d5.freshwise_analytics.events
```

The SQL blocks in `docs/analytics-dashboard.md` were validated against production BigQuery events.

## Validated Queries

| Query | Status | Notes |
| --- | --- | --- |
| Session Funnel | Pass | Returned 13 sessions, 12 recipe sessions, 10 checkout sessions, 10 order sessions. |
| Daily Trend | Pass | Returned daily rows for 2026-05-15 and 2026-05-18. |
| Top Recommended Products | Pass | Returned English and Traditional Chinese product exposure rows. |
| Product Mock GMV | Pass | Returned ordered product units and product-level mock GMV. |
| Product Cart Changes | Pass | Returned add/remove events and net quantity delta. |
| Promotion Performance | Pass | Returned `demo-retailer` / `demo-promotion` rows plus null historical rows. |
| Model Performance | Pass | Returned `gemini-2.5-flash` rows plus null historical rows. |
| Top Ingredients | Pass | Returned normalized English and Traditional Chinese ingredients. |
| Meal Value | Pass | Returned generated, selected, and ordered meal rows. |

## Validation Notes

Some older events were emitted before attribution fields were added, so `Promotion Performance` and `Model Performance` include null groups. This is expected historical data, not a query failure.

Product names currently appear in both English and Traditional Chinese because demos have been run in both UI languages. A later production dashboard should group by `catalog_product_id` first and show localized names as labels.

## Recommended Dashboard Decision

The in-app Admin dashboard is enough for the first live demo because it already shows updated PoC metrics directly from BigQuery.

Build Looker Studio when the audience needs a shareable retailer report, multi-page funnel/product views, or persistent stakeholder access outside the app.
