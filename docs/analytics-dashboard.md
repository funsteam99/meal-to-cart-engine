# Freshwise Analytics Dashboard

This document defines the first retailer-facing PoC dashboard for Freshwise. It is designed for Looker Studio on top of the BigQuery events table populated by the Streamlit MVP.

## Goal

Show whether Freshwise can turn a cooking moment into measurable retail intent:

- users enter or recognize ingredients
- users generate recipe options
- users see missing-item recommendations
- users select a recipe
- users adjust a mock cart
- users place a mock order

The dashboard should answer one commercial question:

> Which recipe and product recommendations create the strongest path from meal intent to cart value?

## Data Source

Default BigQuery table:

```text
subtle-fulcrum-496004-d5.freshwise_analytics.events
```

The table is written by the app when these environment variables are present:

```text
BIGQUERY_PROJECT_ID=subtle-fulcrum-496004-d5
BIGQUERY_DATASET=freshwise_analytics
BIGQUERY_EVENTS_TABLE=events
```

Events include these attribution fields in `properties_json`:

- `retailer_id`
- `promotion_id`
- `model_name`
- `order_id` for checkout, order, and order line item events

## Dashboard Pages

### 1. Executive Summary

Use this page for the top-level PoC story.

Recommended scorecards:

- Sessions
- Recipe generation sessions
- Recipe-to-cart conversion rate
- Mock order conversion rate
- Product recommendation exposures
- Average mock order cart value
- Total mock GMV

Recommended charts:

- Daily sessions and mock orders
- Funnel from session to recipe to checkout to order
- Top recommended products by exposure
- Top generated meals by mock order value

### 2. Funnel

Use this page to show where users drop off.

Funnel steps:

1. Any event
2. `ingredients_updated` or `ingredient_detected`
3. `recipe_generated`
4. `recipe_selected`
5. `checkout_started`
6. `order_completed`

Primary measures:

- sessions per step
- step-to-step conversion
- end-to-end order conversion

### 3. Product Performance

Use this page to show retailer value.

Recommended tables:

- Recommended products by exposure count
- Recommended products by order line item count
- Product exposure to checkout rate
- Product-level mock GMV

Current limitation:

The MVP uses mock product prices and mock checkout, so product GMV is directional PoC evidence rather than retailer-settled revenue.

### 4. Ingredient And Meal Insights

Use this page to show demand signals.

Recommended charts:

- Top entered or detected ingredients
- Top meal titles generated
- Ingredients associated with higher cart value
- Language split
- Retail goal split

## Core SQL

Replace the table name if the environment uses a different project, dataset, or table.

### Session Funnel

```sql
WITH session_events AS (
  SELECT
    session_id,
    MIN(event_timestamp) AS first_seen_at,
    MAX(IF(event_name IN ('ingredients_updated', 'ingredient_detected'), 1, 0)) AS has_ingredients,
    MAX(IF(event_name = 'recipe_generated', 1, 0)) AS has_recipe,
    MAX(IF(event_name = 'recipe_selected', 1, 0)) AS has_recipe_selected,
    MAX(IF(event_name = 'checkout_started', 1, 0)) AS has_checkout,
    MAX(IF(event_name = 'order_completed', 1, 0)) AS has_order,
    MAX(IF(event_name = 'order_completed', cart_subtotal, NULL)) AS mock_order_value
  FROM `subtle-fulcrum-496004-d5.freshwise_analytics.events`
  WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY session_id
)
SELECT
  COUNT(*) AS sessions,
  SUM(has_ingredients) AS ingredient_sessions,
  SUM(has_recipe) AS recipe_sessions,
  SUM(has_recipe_selected) AS selected_recipe_sessions,
  SUM(has_checkout) AS checkout_sessions,
  SUM(has_order) AS order_sessions,
  SAFE_DIVIDE(SUM(has_recipe), COUNT(*)) AS recipe_generation_rate,
  SAFE_DIVIDE(SUM(has_checkout), SUM(has_recipe)) AS recipe_to_checkout_rate,
  SAFE_DIVIDE(SUM(has_order), COUNT(*)) AS mock_order_conversion_rate,
  AVG(IF(has_order = 1, mock_order_value, NULL)) AS average_mock_order_value,
  SUM(IFNULL(mock_order_value, 0)) AS mock_gmv
FROM session_events;
```

### Daily Trend

```sql
SELECT
  DATE(event_timestamp) AS event_date,
  COUNT(DISTINCT session_id) AS sessions,
  COUNTIF(event_name = 'recipe_generated') AS recipes_generated,
  COUNTIF(event_name = 'product_recommended') AS product_exposures,
  COUNTIF(event_name = 'checkout_started') AS checkouts,
  COUNTIF(event_name = 'order_completed') AS mock_orders,
  SUM(IF(event_name = 'order_completed', cart_subtotal, 0)) AS mock_gmv
FROM `subtle-fulcrum-496004-d5.freshwise_analytics.events`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY event_date
ORDER BY event_date;
```

### Top Recommended Products

```sql
SELECT
  JSON_VALUE(properties_json, '$.product_name') AS product_name,
  COUNT(*) AS exposure_count,
  AVG(CAST(JSON_VALUE(properties_json, '$.estimated_price') AS FLOAT64)) AS average_estimated_price
FROM `subtle-fulcrum-496004-d5.freshwise_analytics.events`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND event_name = 'product_recommended'
  AND JSON_VALUE(properties_json, '$.product_name') IS NOT NULL
GROUP BY product_name
ORDER BY exposure_count DESC, product_name
LIMIT 25;
```

### Product Mock GMV

```sql
SELECT
  JSON_VALUE(properties_json, '$.product_name') AS product_name,
  SUM(CAST(JSON_VALUE(properties_json, '$.quantity') AS INT64)) AS ordered_units,
  AVG(CAST(JSON_VALUE(properties_json, '$.estimated_price') AS FLOAT64)) AS average_estimated_price,
  SUM(CAST(JSON_VALUE(properties_json, '$.line_subtotal') AS FLOAT64)) AS product_mock_gmv,
  COUNT(DISTINCT session_id) AS ordering_sessions
FROM `subtle-fulcrum-496004-d5.freshwise_analytics.events`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND event_name = 'order_line_item'
  AND JSON_VALUE(properties_json, '$.product_name') IS NOT NULL
GROUP BY product_name
ORDER BY product_mock_gmv DESC, ordered_units DESC, product_name
LIMIT 25;
```

### Product Cart Changes

```sql
SELECT
  JSON_VALUE(properties_json, '$.product_name') AS product_name,
  COUNTIF(event_name = 'product_added_to_cart') AS add_events,
  COUNTIF(event_name = 'product_removed_from_cart') AS remove_events,
  SUM(CAST(JSON_VALUE(properties_json, '$.quantity_delta') AS INT64)) AS net_quantity_delta
FROM `subtle-fulcrum-496004-d5.freshwise_analytics.events`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND event_name IN ('product_added_to_cart', 'product_removed_from_cart')
  AND JSON_VALUE(properties_json, '$.product_name') IS NOT NULL
GROUP BY product_name
ORDER BY net_quantity_delta DESC, add_events DESC, product_name
LIMIT 25;
```

### Promotion Performance

```sql
WITH session_events AS (
  SELECT
    session_id,
    JSON_VALUE(properties_json, '$.retailer_id') AS retailer_id,
    JSON_VALUE(properties_json, '$.promotion_id') AS promotion_id,
    MAX(IF(event_name = 'recipe_generated', 1, 0)) AS has_recipe,
    MAX(IF(event_name = 'checkout_started', 1, 0)) AS has_checkout,
    MAX(IF(event_name = 'order_completed', 1, 0)) AS has_order,
    MAX(IF(event_name = 'order_completed', cart_subtotal, NULL)) AS mock_order_value
  FROM `subtle-fulcrum-496004-d5.freshwise_analytics.events`
  WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY session_id, retailer_id, promotion_id
)
SELECT
  retailer_id,
  promotion_id,
  COUNT(*) AS sessions,
  SUM(has_recipe) AS recipe_sessions,
  SUM(has_checkout) AS checkout_sessions,
  SUM(has_order) AS order_sessions,
  SAFE_DIVIDE(SUM(has_checkout), SUM(has_recipe)) AS recipe_to_checkout_rate,
  AVG(IF(has_order = 1, mock_order_value, NULL)) AS average_mock_order_value,
  SUM(IFNULL(mock_order_value, 0)) AS mock_gmv
FROM session_events
GROUP BY retailer_id, promotion_id
ORDER BY mock_gmv DESC, order_sessions DESC;
```

### Model Performance

```sql
SELECT
  JSON_VALUE(properties_json, '$.model_name') AS model_name,
  COUNTIF(event_name = 'recipe_generated') AS recipes_generated,
  COUNTIF(event_name = 'ingredient_detected') AS photo_recognitions,
  COUNTIF(event_name = 'order_completed') AS mock_orders,
  AVG(IF(event_name = 'order_completed', cart_subtotal, NULL)) AS average_mock_order_value
FROM `subtle-fulcrum-496004-d5.freshwise_analytics.events`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY model_name
ORDER BY recipes_generated DESC, mock_orders DESC;
```

### Top Ingredients

```sql
WITH normalized_ingredients AS (
  SELECT
    session_id,
    CASE
      WHEN REGEXP_CONTAINS(TRIM(ingredient), r'[A-Za-z]') THEN INITCAP(LOWER(TRIM(ingredient)))
      ELSE TRIM(ingredient)
    END AS normalized_ingredient
  FROM `subtle-fulcrum-496004-d5.freshwise_analytics.events`,
  UNNEST(ingredients) AS ingredient
  WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
    AND TRIM(ingredient) != ''
)
SELECT
  normalized_ingredient AS ingredient,
  COUNT(*) AS event_count,
  COUNT(DISTINCT session_id) AS sessions
FROM normalized_ingredients
GROUP BY normalized_ingredient
ORDER BY sessions DESC, event_count DESC, ingredient
LIMIT 25;
```

### Meal Value

```sql
SELECT
  meal_title,
  COUNTIF(event_name = 'recipe_generated') AS generated_events,
  COUNTIF(event_name = 'recipe_selected') AS selected_events,
  COUNTIF(event_name = 'order_completed') AS mock_orders,
  AVG(IF(event_name = 'order_completed', cart_subtotal, NULL)) AS average_mock_order_value,
  SUM(IF(event_name = 'order_completed', cart_subtotal, 0)) AS mock_gmv
FROM `subtle-fulcrum-496004-d5.freshwise_analytics.events`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  AND meal_title IS NOT NULL
  AND meal_title != ''
GROUP BY meal_title
ORDER BY mock_gmv DESC, mock_orders DESC, meal_title
LIMIT 25;
```

## Looker Studio Setup

1. Create a BigQuery data source using `freshwise_analytics.events`.
2. Add calculated fields for the conversion rates when using raw event rows, or use the SQL above as custom queries.
3. Set the default date range to the last 30 days.
4. Add a filter control for `language`.
5. Add a filter control for `business_goal`.
6. Add a table filter for `meal_title`.

Recommended first page layout:

- top row: scorecards for sessions, recipe sessions, mock orders, average mock cart, mock GMV
- middle left: funnel chart
- middle right: daily trend
- bottom left: top products
- bottom right: top ingredients

## Metrics Definitions

| Metric | Definition |
| --- | --- |
| Sessions | Distinct `session_id` values in the date range |
| Recipe sessions | Sessions with at least one `recipe_generated` event |
| Product exposures | Count of `product_recommended` events |
| Checkout sessions | Sessions with at least one `checkout_started` event |
| Mock orders | Count of `order_completed` events |
| Average mock order value | Average `cart_subtotal` on `order_completed` events |
| Mock GMV | Sum of `cart_subtotal` on `order_completed` events |
| Recipe generation rate | Recipe sessions divided by sessions |
| Recipe-to-checkout rate | Checkout sessions divided by recipe sessions |
| Mock order conversion rate | Order sessions divided by sessions |

## Event Gaps To Close Next

For a stronger retailer PoC, add these events or fields after the first dashboard is live:

- `recipe_generation_latency_ms`: tracks AI performance and cost impact
- `currency`: separates demo markets once non-USD mock prices are introduced
- `tenant_config_version`: tracks which retailer catalog and campaign rules generated recommendations
- `catalog_product_id`: links recommended products to a real retailer SKU once catalog integration starts

## Demo Talk Track

Freshwise starts with a user cooking question, not a shopping search. The dashboard shows how often those cooking moments become recipe engagement, product exposure, checkout intent, and mock cart value. That gives a retailer a measurable reason to fund a PoC before Freshwise connects to real inventory and checkout APIs.
