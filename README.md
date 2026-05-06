# AI Meal-to-Cart Engine

A Streamlit B2B demo that turns a user's existing ingredients plus a retailer's promoted products into a shoppable dinner plan.

## Positioning

> Turn fridge leftovers and weekly promotions into a shoppable dinner plan.

This demo is designed for supermarkets, grocery platforms, food brands, and kitchen appliance partners.

## What It Shows

- Current fridge ingredients as meal intent
- Mock retailer promotion catalog
- AI-generated dinner recommendation
- Missing items mapped to promoted products
- Simulated cart value
- Recipe steps for the recommended meal

## Streamlit Secrets

Set these in Streamlit Community Cloud:

```toml
api_key = "YOUR_GOOGLE_API_KEY"
default_model = "models/gemma-4-31b-it"
```

`model` is also supported and takes priority over `default_model`.

## Local Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Demo Scope

This is a sales/demo prototype. It does not connect to a real retailer API, payment system, or checkout cart yet.
