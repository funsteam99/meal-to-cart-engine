# Freshwise QA Record

This records what has been verified after Cloud Run revision `freshwise-00008-zmz`.

## Deployment

- Cloud Run service URL: `https://freshwise-539021301650.asia-east1.run.app`
- Previous URL still reachable: `https://freshwise-lyhoyhjnca-de.a.run.app`
- Both URLs returned `200 OK` after deployment.

## Analytics Flow Evidence

Recent BigQuery events confirmed the demo path has data for:

- `ingredients_updated`
- `recipe_generated`
- `product_recommended`
- `product_added_to_cart`
- `product_removed_from_cart`
- `checkout_started`
- `order_line_item`
- `order_completed`

The latest verified session included:

- 1 `recipe_generated`
- 5 `product_recommended`
- 2 `product_added_to_cart`
- 2 `product_removed_from_cart`
- 5 `order_line_item`
- 1 `order_completed`
- mock cart subtotal: `$17.15`

## Admin Metrics Evidence

The same BigQuery logic used by the in-app Admin dashboard returned non-zero metrics:

- event count: `23`
- session count: `1`
- recipe count: `1`
- product recommendation count: `5`
- order count: `1`
- order line item count: `5`
- average mock cart subtotal: `$17.15`

This confirms the Admin dashboard has updated data available after the flow.

## Top Ingredients Normalization

The dashboard normalization logic was verified with:

```text
Eggs
eggs
 EGGS 
```

All three normalize to:

```text
Eggs
```

## Remaining Visual QA

Visual browser confirmation was provided by screenshot for:

- Traditional Chinese UI labels in the main app shell.
- Traditional Chinese cart tab.
- Mock order confirmation card after checkout.
- Confirmation card order metrics: item count, order total, order ID, and line items.

These still require visual browser confirmation:

- Confirm the full flow includes selecting a recipe and returning to Admin.
