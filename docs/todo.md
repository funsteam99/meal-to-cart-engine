# Freshwise Todo

This checklist summarizes the current project status and next work items from the latest development thread.

## Completed

- Cloud Run redeployed to revision `freshwise-00008-zmz`.
- Admin page Traditional Chinese labels added and deployed.
- BigQuery analytics event logging added.
- Product-level analytics events added:
  - `product_recommended`
  - `product_added_to_cart`
  - `product_removed_from_cart`
  - `order_line_item`
- Attribution fields added to analytics events:
  - `retailer_id`
  - `promotion_id`
  - `model_name`
  - `order_id`
- Cart mock order UX improved:
  - persistent confirmation card after placing a mock order
  - item count, total, order ID, and line items shown
  - empty cart checkout disabled
- Top ingredients normalization fixed:
  - `Eggs`, `eggs`, and ` EGGS ` are grouped as one ingredient
- Analytics dashboard plan added in `docs/analytics-dashboard.md`.

## Immediate QA

- [x] Open the deployed Cloud Run app.
- [x] Switch the UI language to Traditional Chinese.
- [x] Open the Admin tab and confirm all labels are localized.
- [x] Run a full demo flow:
  - enter ingredients
  - generate recipes
  - select a recipe
  - adjust cart quantities
  - place a mock order
  - return to Admin
- [x] Confirm the mock order confirmation card appears after checkout.
- [x] Confirm Top ingredients groups duplicate casing correctly.
- [x] Confirm Admin metrics update after the flow.

## Analytics Verification

- [x] Verify `recipe_generated` events.
- [x] Verify `product_recommended` events.
- [x] Verify `product_added_to_cart` events.
- [x] Verify `product_removed_from_cart` events.
- [x] Verify `order_line_item` events.
- [x] Verify `order_completed` events.
- [x] Verify `ingredient_detected` photo events.
- [x] Confirm checkout, line item, and order completed events share the same `order_id`.
- [x] Confirm `properties_json` includes:
  - `retailer_id`
  - `promotion_id`
  - `model_name`
  - `order_id` where relevant
  - `catalog_product_id` where relevant
  - `currency`
  - `tenant_config_version`
  - `recipe_generation_latency_ms`
  - `photo_recognition_latency_ms`
  - `estimated_request_count`
  - `category` where relevant
  - `promotion_label` where relevant

## Demo Readiness

- [x] Prepare a stable demo script.
- [x] Choose fixed demo ingredients.
- [x] Prepare a short retailer-facing talk track.
- [x] Avoid showing PowerShell for Chinese files during demo.
- [x] Use GitHub, VS Code, browser, or Streamlit UI for Chinese content.
- [x] Check whether any non-Admin Chinese UI text still appears garbled.

## Next Product Work

- [x] Add AI latency tracking:
  - recipe generation latency
  - photo recognition latency
  - model success/fallback source
- [x] Add cost visibility fields where possible:
  - model name
  - request source
  - estimated request count
- [x] Add `catalog_product_id` to recommended products.
- [x] Add `currency` to product/order analytics.
- [x] Add `tenant_config_version` for retailer catalog and campaign rules.

## Retailer PoC Prep

- [x] Build a retailer-specific mock catalog with 10-20 SKUs.
- [x] Add SKU categories and promotion labels.
- [x] Map recommended products to mock catalog IDs.
- [x] Define PoC success metrics:
  - recipe generation rate
  - product exposure
  - add-to-cart activity
  - mock order conversion
  - product mock GMV
- [x] Prepare PoC scope and pricing options.

## Dashboard Work

- [ ] Build Looker Studio dashboard from `docs/analytics-dashboard.md`.
- [ ] Add pages:
  - Executive Summary
  - Funnel
  - Product Performance
  - Ingredient and Meal Insights
- [ ] Validate SQL against BigQuery production events.
- [ ] Decide whether in-app Admin remains enough for first demo or Looker Studio is required.

## Future Integration

- [ ] Define retailer inventory API requirements.
- [ ] Define cart API or checkout deep-link requirements.
- [ ] Define product catalog import format.
- [ ] Define promotion campaign mapping.
- [ ] Decide whether persistent app state should use Firestore or Cloud SQL.
- [ ] Add Cloud Storage abstraction for uploaded fridge photos.
