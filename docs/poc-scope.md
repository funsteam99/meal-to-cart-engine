# Freshwise Retailer PoC Scope

This document defines a practical first PoC package for a grocery retailer, fresh food e-commerce team, or food brand partner.

## PoC Goal

Prove that Freshwise can turn meal intent into measurable retail activity:

- recipe generation from ingredients
- recommended product exposure
- add-to-cart behavior
- mock order conversion
- product-level mock GMV

The PoC is not a production checkout integration. It validates the conversion journey and analytics layer before connecting retailer catalog, inventory, cart, or payment APIs.

## Recommended PoC Duration

4 to 6 weeks.

Use the first week for catalog and campaign setup, two to four weeks for testing and stakeholder demos, and the final week for reporting and next-scope decisions.

## Fixed Success Metrics

| Metric | Definition | PoC Target |
| --- | --- | --- |
| Recipe generation rate | Sessions with `recipe_generated` divided by total sessions | 40%+ |
| Product exposure | Count of `product_recommended` events | 100+ exposures during test window |
| Add-to-cart activity | Count of `product_added_to_cart` events | 20+ add events during test window |
| Mock order conversion | Sessions with `order_completed` divided by total sessions | 10%+ |
| Product mock GMV | Sum of `line_subtotal` from `order_line_item` events | Directional benchmark, target set by traffic |
| SKU attribution coverage | Product events with `catalog_product_id` present | 95%+ |
| Campaign attribution coverage | Product events with `promotion_label` present | 95%+ |
| Recipe latency | `recipe_generation_latency_ms` p50 / p95 | p50 under 15s, p95 under 30s |
| Photo recognition latency | `photo_recognition_latency_ms` p50 / p95 | p50 under 15s, p95 under 30s |

## Event Evidence

The current MVP already emits these BigQuery events:

- `ingredient_detected`
- `ingredients_updated`
- `recipe_generated`
- `product_recommended`
- `product_added_to_cart`
- `product_removed_from_cart`
- `checkout_started`
- `order_line_item`
- `order_completed`

Product events include:

- `catalog_product_id`
- `category`
- `promotion_label`
- `currency`
- `tenant_config_version`
- `retailer_id`
- `promotion_id`

## PoC Package

### Starter PoC

Use when the retailer wants a fast stakeholder demo.

- 10 to 20 mock SKUs
- one campaign or promotion theme
- hosted demo app
- in-app Admin dashboard
- final summary of usage and conversion events

Suggested price:

```text
NT$50k-100k one-time PoC fee
```

### Growth PoC

Use when the retailer wants a more realistic campaign validation.

- 20 to 50 SKUs
- categories and campaign labels
- multiple demo scenarios
- Looker Studio dashboard
- PoC readout with funnel, product performance, and mock GMV

Suggested price:

```text
NT$100k-300k one-time PoC fee
```

### Integration Pilot

Use after the retailer accepts the PoC direction and wants operational validation.

- retailer catalog import
- inventory availability requirements
- checkout deep-link or cart API requirements
- persistent session/cart storage
- production security review

Suggested pricing:

```text
NT$300k+ implementation fee plus monthly SaaS or usage pricing
```

## Out Of Scope For First PoC

- real payment
- real order fulfillment
- live inventory guarantees
- loyalty login
- personalized user history
- production SLA

These belong in the integration pilot after the retailer validates meal-to-cart conversion.
