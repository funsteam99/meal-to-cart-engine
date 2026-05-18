# Freshwise GCP Deployment Record

This document records the actual GCP deployment work completed for the Freshwise meal-to-cart MVP.

## Current Deployment

- GCP project ID: `subtle-fulcrum-496004-d5`
- GCP project number: `539021301650`
- Region: `asia-east1`
- Cloud Run service: `freshwise`
- Latest verified revision: `freshwise-00007-qgh`
- Public URL: https://freshwise-539021301650.asia-east1.run.app
- Previous public URL: https://freshwise-lyhoyhjnca-de.a.run.app
- Runtime model: `gemini-2.5-flash`
- Analytics dataset: `freshwise_analytics`
- Analytics events table: `events`

The deployed service is the current C-side MVP/demo layer:

- ingredient input
- fridge/photo ingredient recognition path
- AI recipe generation
- missing ingredient recommendation
- mock cart flow

## Deployment Steps Completed

### 1. Confirmed GCP Project

The target project was confirmed with Google Cloud CLI:

```powershell
gcloud projects describe subtle-fulcrum-496004-d5
```

Confirmed values:

- Project ID: `subtle-fulcrum-496004-d5`
- Project number: `539021301650`
- Project name: `My Project 93653`

### 2. Installed and Authenticated Google Cloud CLI

Google Cloud CLI was installed locally and authenticated with:

```powershell
gcloud auth login
gcloud config set project subtle-fulcrum-496004-d5
```

The active authenticated account was:

```text
funsteam99@gmail.com
```

### 3. Enabled Required GCP APIs

The following APIs were enabled:

```powershell
gcloud services enable `
  run.googleapis.com `
  cloudbuild.googleapis.com `
  secretmanager.googleapis.com `
  generativelanguage.googleapis.com
```

Purpose:

- `run.googleapis.com`: Cloud Run hosting
- `cloudbuild.googleapis.com`: source-to-container build
- `secretmanager.googleapis.com`: secure API key storage
- `generativelanguage.googleapis.com`: Gemini API access

### 4. Created Secret Manager Entry

Secret name:

```text
freshwise-google-api-key
```

The secret value was created from local `.streamlit/secrets.toml` using the `api_key` value.

Cloud Run receives the key through this environment variable:

```text
GOOGLE_API_KEY
```

### 5. Granted Cloud Run Secret Access

Cloud Run uses this default compute service account:

```text
539021301650-compute@developer.gserviceaccount.com
```

It was granted:

```text
roles/secretmanager.secretAccessor
```

This allows the Cloud Run revision to read `freshwise-google-api-key`.

### 6. Added Cloud Run Deployment Files

The project now includes:

- `Dockerfile`
- `.dockerignore`
- `.gcloudignore`
- `deploy-cloud-run.ps1`

`Dockerfile` runs Streamlit on Cloud Run port `8080`:

```dockerfile
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
```

### 7. Updated Runtime Configuration

`app.py` now supports both Streamlit secrets and GCP environment variables.

API key lookup:

- `st.secrets["api_key"]`
- `GOOGLE_API_KEY`
- `GEMINI_API_KEY`
- `API_KEY`

Model lookup:

- `st.secrets["model"]`
- `st.secrets["default_model"]`
- `MODEL`
- `DEFAULT_MODEL`
- `GEMINI_MODEL`

### 8. Fixed Gemini Model Calls

The first Cloud Run deployment showed this user-facing fallback message during recipe generation:

```text
Model call unavailable, using local demo fallback. (Connection error.)
```

The original implementation used the OpenAI-compatible Gemini endpoint through the `openai` Python client.

The fix was to call Gemini through the native REST API instead:

```text
https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
```

After this change:

- `openai` was removed from `requirements.txt`
- Gemini calls use the Python standard library `urllib`
- errors are logged with `logging.exception`
- Cloud Run can generate recipes successfully

### 9. Fixed Streamlit Session State Issue

Cloud Run logs showed a Streamlit error when switching language:

```text
st.session_state.manual_text cannot be modified after the widget with key manual_text is instantiated
```

The language switch logic was adjusted to avoid mutating `manual_text` after the widget exists.

### 10. Deployed to Cloud Run

The deployment command used was equivalent to:

```powershell
gcloud run deploy freshwise `
  --source . `
  --region asia-east1 `
  --project subtle-fulcrum-496004-d5 `
  --port 8080 `
  --allow-unauthenticated `
  --set-env-vars DEFAULT_MODEL=gemini-2.5-flash `
  --set-secrets GOOGLE_API_KEY=freshwise-google-api-key:latest
```

The deployed service is public:

```text
allUsers -> roles/run.invoker
```

### 11. Added BigQuery Event Logging

The next GCP work item, basic analytics event logging, was implemented and deployed.

The app now records these user journey events:

- `ingredient_detected`
- `ingredients_updated`
- `recipe_generated`
- `product_recommended`
- `recipe_selected`
- `cart_quantity_changed`
- `cart_cleared`
- `cart_reset`
- `checkout_started`
- `order_completed`

The Cloud Run service now has these analytics environment variables:

```text
BIGQUERY_PROJECT_ID=subtle-fulcrum-496004-d5
BIGQUERY_DATASET=freshwise_analytics
BIGQUERY_EVENTS_TABLE=events
```

The runtime service account was granted BigQuery write access:

```text
539021301650-compute@developer.gserviceaccount.com -> roles/bigquery.dataEditor
```

Deployment command:

```powershell
.\deploy-cloud-run.ps1 -ProjectId subtle-fulcrum-496004-d5 -Region asia-east1 -EnableAnalytics -GrantAnalyticsIam
```

Cloud Run revision:

```text
freshwise-00004-mfb
```

### 12. Added PoC Admin Dashboard

An in-app `Admin` tab was added to read the BigQuery events table and show a lightweight B2B PoC dashboard.

The dashboard covers:

- sessions and total events
- recipes generated
- product recommendation exposures
- mock order count
- average mock cart subtotal
- top ingredients
- top recommended products
- recent event stream

This keeps the first back-office surface close to the MVP while giving retailer-facing PoC metrics without a separate dashboard product.

Cloud Run revision:

```text
freshwise-00005-9zw
```

### 13. Added PoC Attribution Analytics Fields

Product and model analytics were extended with stronger PoC attribution fields in `properties_json`:

- `catalog_product_id`
- `currency`
- `tenant_config_version`
- `recipe_generation_latency_ms`
- `photo_recognition_latency_ms`
- `estimated_request_count`

The deployment command used:

```powershell
.\deploy-cloud-run.ps1 -ProjectId subtle-fulcrum-496004-d5 -Region asia-east1 -EnableAnalytics -GrantAnalyticsIam
```

Cloud Run revision:

```text
freshwise-00007-qgh
```

## Verification

Cloud Run service state:

- latest ready revision: `freshwise-00007-qgh`
- traffic: `100%`
- URL: https://freshwise-539021301650.asia-east1.run.app
- previous URL: https://freshwise-lyhoyhjnca-de.a.run.app

HTTP check:

```text
GET https://freshwise-539021301650.asia-east1.run.app -> 200 OK
GET https://freshwise-lyhoyhjnca-de.a.run.app -> 200 OK
```

Browser test:

1. Opened the deployed Cloud Run URL.
2. Entered ingredients: `tomatoes, eggs, milk`.
3. Clicked `Use Manual Input`.
4. Opened the `Recipe` tab.
5. Clicked `Generate Recipe`.
6. Confirmed the app generated three recipe options.
7. Confirmed status text: `Generated by the configured model.`

## Repeat Deployment

Future deployments can use:

```powershell
.\deploy-cloud-run.ps1 -ProjectId subtle-fulcrum-496004-d5 -Region asia-east1
```

The script handles:

- setting the GCP project
- enabling required APIs
- creating or updating the Secret Manager secret from `.streamlit/secrets.toml`
- granting Cloud Run access to the secret
- deploying the app to Cloud Run

To also enable BigQuery event logging:

```powershell
.\deploy-cloud-run.ps1 -ProjectId subtle-fulcrum-496004-d5 -Region asia-east1 -EnableAnalytics -GrantAnalyticsIam
```

## Git Record

The deployment support and Gemini fix were committed and pushed to GitHub:

```text
1958e2f Add Cloud Run deployment support
```

Remote:

```text
https://github.com/funsteam99/meal-to-cart-engine.git
```

Branch:

```text
main
```

## Next GCP Work

The current deployment covers the C-side MVP/demo and first-pass BigQuery event logging. To match the full Freshwise business plan, the next GCP work should add:

- Build the Looker Studio dashboard from `docs/analytics-dashboard.md`
- Add latency, currency, catalog product ID, and tenant config version fields for richer analytics attribution
- Firestore or Cloud SQL for persistent user/session/cart state
- Cloud Storage abstraction for uploaded fridge photos
- retailer connector service for inventory, cart, and checkout APIs
- optional Vertex AI Embeddings / Vector Search for better product matching
