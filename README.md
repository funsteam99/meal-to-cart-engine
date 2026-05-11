# Freshwise Meal-to-Cart Engine

A Streamlit mobile-first MVP that identifies fridge ingredients, generates a recipe with a multimodal LLM, and turns missing ingredients into a mock grocery cart.

## Positioning

> See it. Cook it. Love it.

Freshwise is currently implemented as a Streamlit app so it can be tested quickly on desktop and mobile. The UI is shaped like an app prototype, with a future path toward PWA packaging after the core flow is stable.

## Current MVP Flow

- **Scan**: take a fridge photo on mobile or upload/capture an image through `st.camera_input`.
- **Recognize**: send the photo to the configured multimodal model and write detected ingredients back into the editable ingredient text box.
- **Edit**: manually correct, remove, or add ingredients before generating a recipe.
- **Generate Recipes**: call the configured model to create three recipe options, each with a chef note, missing ingredients, recommended products, and cooking steps.
- **Choose**: select one of the three recipe options as the current meal.
- **Cart**: review mock grocery items for the selected recipe, adjust quantities, and place a mock order.
- **Settings**: change the retail goal and verify model connection status without cluttering the main flow.

## Features

- English and Traditional Chinese UI language toggle.
- Multimodal ingredient recognition using the same configured model family as recipe generation.
- Initial recipe and cart views start empty until ingredients are entered and recipes are generated.
- Local fallback recipe/demo data appears only when the user selects demo ingredients or when the model call is unavailable.
- Mobile-friendly Streamlit layout with app-style tabs.
- Mock retail catalog and cart totals for meal-to-cart demonstrations.

## Streamlit Secrets

Set these in Streamlit Community Cloud:

```toml
api_key = "YOUR_GOOGLE_API_KEY"
default_model = "gemini-2.5-flash"
```

`model` is also supported and takes priority over `default_model`.

For local development, put the same values in `.streamlit/secrets.toml`. The `.streamlit/` directory is intentionally ignored by git, so API keys should not be committed.

If recipe generation fails with `403 SERVICE_DISABLED`, enable the Gemini API for the Google Cloud project behind that API key:

https://console.developers.google.com/apis/api/generativelanguage.googleapis.com/overview

After enabling it, wait a few minutes for Google Cloud propagation and retry.

## Local Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL in a browser. For mobile camera testing, deploy to Streamlit Community Cloud or expose the local server through a secure mobile-accessible URL.

## Demo Scope

This is a functional prototype. It does not connect to a real retailer API, payment system, inventory feed, or checkout cart yet. Those screens and data structures are kept intentionally mockable so the app can evolve toward a production/PWA version later.

## Business Model

See [docs/business-model.md](docs/business-model.md) for a Chinese visual revenue strategy covering PoC fees, SaaS tiers, AI usage fees, and cart/GMV commission.
