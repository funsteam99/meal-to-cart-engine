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
- **Admin**: review BigQuery analytics for sessions, recipe generation, product exposure, cart activity, and mock orders.
- **Settings**: change the retail goal and verify model connection status without cluttering the main flow.

## Features

- English and Traditional Chinese UI language toggle.
- Multimodal ingredient recognition using the same configured model family as recipe generation.
- Initial recipe and cart views start empty until ingredients are entered and recipes are generated.
- Local fallback recipe/demo data appears only when the user selects demo ingredients or when the model call is unavailable.
- Optional BigQuery event logging with an in-app PoC admin dashboard.
- Product-level cart and mock order line-item events for attribution analysis.
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

If recipe generation fails with `403 API_KEY_SERVICE_BLOCKED`, the API key itself is restricted. In Google Cloud Console, open the API key, then under **API restrictions** either allow **Generative Language API** (`generativelanguage.googleapis.com`) or temporarily choose **Don't restrict key** while testing.

## Local Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL in a browser. For mobile camera testing, deploy to Streamlit Community Cloud or expose the local server through a secure mobile-accessible URL.

## Google Cloud Run Deployment

This repo can run on Google Cloud Run with the included `Dockerfile` and `deploy-cloud-run.ps1`.

The app reads model settings from Streamlit secrets first, then falls back to environment variables:

- `GOOGLE_API_KEY`, `GEMINI_API_KEY`, or `API_KEY`
- `MODEL`, `DEFAULT_MODEL`, or `GEMINI_MODEL`
- `BIGQUERY_DATASET` and `BIGQUERY_EVENTS_TABLE` for optional analytics event logging

Create the API key secret once:

```powershell
gcloud config set project YOUR_PROJECT_ID
gcloud services enable secretmanager.googleapis.com
echo YOUR_GOOGLE_API_KEY | gcloud secrets create freshwise-google-api-key --data-file=-
```

Deploy:

```powershell
.\deploy-cloud-run.ps1 -ProjectId YOUR_PROJECT_ID -Region asia-east1
```

For the current GCP project:

```powershell
gcloud auth login
.\deploy-cloud-run.ps1 -ProjectId subtle-fulcrum-496004-d5 -Region asia-east1
```

The script enables the required APIs, creates or updates `freshwise-google-api-key` from `.streamlit/secrets.toml` when that file exists, deploys the service from source, sets `DEFAULT_MODEL`, and maps `GOOGLE_API_KEY` from Secret Manager.

To enable BigQuery analytics during deployment:

```powershell
.\deploy-cloud-run.ps1 -ProjectId subtle-fulcrum-496004-d5 -Region asia-east1 -EnableAnalytics -GrantAnalyticsIam
```

That adds `roles/bigquery.dataEditor` to the Cloud Run runtime service account so the app can create and write the event table. It also sets:

```text
BIGQUERY_DATASET=freshwise_analytics
BIGQUERY_EVENTS_TABLE=events
```

When those values are present, Freshwise logs recipe, product recommendation, cart, checkout, and mock order events to BigQuery. If BigQuery is unavailable, the app keeps running and writes the event payload to Cloud Logging.

The app includes an `Admin` tab that reads the same BigQuery table and shows the last 30 days of PoC metrics:

- sessions and total events
- recipes generated
- product recommendation exposures
- mock orders and average mock cart subtotal
- top ingredients and recommended products
- recent event stream

Current Cloud Run service URL:

```text
https://freshwise-lyhoyhjnca-de.a.run.app
```

## Demo Scope

This is a functional prototype. It does not connect to a real retailer API, payment system, inventory feed, or checkout cart yet. Those screens and data structures are kept intentionally mockable so the app can evolve toward a production/PWA version later.

## Business Model

See [docs/business-model.md](docs/business-model.md) for a Chinese visual revenue strategy covering PoC fees, SaaS tiers, AI usage fees, and cart/GMV commission.

## Analytics Dashboard

See [docs/analytics-dashboard.md](docs/analytics-dashboard.md) for the first retailer-facing PoC dashboard plan, including Looker Studio pages, KPI definitions, and BigQuery SQL for funnel, product exposure, ingredient, and mock GMV metrics.
