# Freshwise Meal-to-Cart Engine

A Streamlit mobile-first MVP that identifies fridge ingredients, generates a recipe with a multimodal LLM, and turns missing ingredients into a mock grocery cart.

## Positioning

> See it. Cook it. Love it.

Freshwise is currently implemented as a Streamlit app so it can be tested quickly on desktop and mobile. The UI is shaped like an app prototype, with a future path toward PWA packaging after the core flow is stable.

## Current MVP Flow

- **Scan**: take a fridge photo on mobile or upload/capture an image through `st.camera_input`.
- **Recognize**: send the photo to the configured multimodal model and write detected ingredients back into the editable ingredient text box.
- **Edit**: manually correct, remove, or add ingredients before generating a recipe.
- **Generate Recipe**: call the configured model to create a recipe plan, chef note, missing ingredients, recommended products, and cooking steps.
- **Cart**: review mock grocery items, adjust quantities, and place a mock order.
- **Settings**: change the retail goal and verify model connection status without cluttering the main flow.

## Features

- English and Traditional Chinese UI language toggle.
- Multimodal ingredient recognition using the same configured model family as recipe generation.
- Local fallback recipe/demo data for presentations when the model is unavailable.
- Mobile-friendly Streamlit layout with app-style tabs.
- Mock retail catalog and cart totals for meal-to-cart demonstrations.

## Streamlit Secrets

Set these in Streamlit Community Cloud:

```toml
api_key = "YOUR_GOOGLE_API_KEY"
default_model = "models/gemma-4-31b-it"
```

`model` is also supported and takes priority over `default_model`.

For local development, put the same values in `.streamlit/secrets.toml`. The `.streamlit/` directory is intentionally ignored by git, so API keys should not be committed.

## Local Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL in a browser. For mobile camera testing, deploy to Streamlit Community Cloud or expose the local server through a secure mobile-accessible URL.

## Demo Scope

This is a functional prototype. It does not connect to a real retailer API, payment system, inventory feed, or checkout cart yet. Those screens and data structures are kept intentionally mockable so the app can evolve toward a production/PWA version later.
