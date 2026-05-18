# Freshwise Demo Script

Use this script for a stable retailer-facing Freshwise PoC demo.

## Demo URL

```text
https://freshwise-539021301650.asia-east1.run.app
```

Fallback URL:

```text
https://freshwise-lyhoyhjnca-de.a.run.app
```

## Fixed Demo Ingredients

Use this English ingredient set for the most predictable demo:

```text
tomatoes, spinach, eggs, cheese
```

Use this Traditional Chinese ingredient set only when specifically demoing Chinese UI:

```text
番茄、菠菜、雞蛋、起司
```

## Demo Flow

1. Open the deployed app.
2. In `Scan`, enter the fixed demo ingredients or use a fridge photo.
3. Click `Use Manual Input` or `Recognize Photo`.
4. Open `Recipe`.
5. Click `Generate Recipe`.
6. Wait for three recipe options.
7. Select one recipe.
8. Open `Cart`.
9. Increase one product quantity with `+`.
10. Decrease one product quantity with `-`.
11. Click `Place mock order`.
12. Confirm the order confirmation card shows item count, order total, order ID, and line items.
13. Open `Admin`.
14. Refresh the dashboard and confirm metrics update.

## Retailer Talk Track

Freshwise starts from a cooking moment instead of a shopping search. A user shows or enters what they already have, Freshwise turns that into practical dinner options, and the missing ingredients become a measurable mock cart.

For a retailer, the PoC question is simple: can cooking intent become product exposure, add-to-cart activity, and mock order value? The dashboard answers that with recipe generation, product recommendation exposure, cart changes, order line items, mock GMV, and model latency.

The current demo does not claim real checkout integration. It proves the conversion layer and analytics instrumentation before connecting retailer catalog, inventory, and cart APIs.

## Metrics To Point Out

- `recipe_generated`: recipe demand signal
- `product_recommended`: product exposure
- `product_added_to_cart`: add-to-cart intent
- `product_removed_from_cart`: product rejection or quantity correction
- `order_line_item`: product-level mock GMV
- `order_completed`: mock order conversion
- `catalog_product_id`: SKU-level attribution
- `recipe_generation_latency_ms`: AI generation speed
- `photo_recognition_latency_ms`: fridge recognition speed

## Demo Guardrails

- Avoid showing PowerShell when presenting Chinese text; use the browser, GitHub, VS Code, or Streamlit UI.
- Use English ingredients for the most stable model output.
- Use Traditional Chinese UI only after confirming labels render correctly in the browser.
- If the model is slow, frame latency as an instrumented PoC metric now visible in BigQuery.
- If the Admin dashboard lags, refresh once and explain that BigQuery-backed analytics can take a short moment to appear.
