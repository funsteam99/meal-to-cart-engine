# Freshwise Mobile MVP Notes

## Current Goal

Build a Streamlit-hosted mobile app prototype that can be demonstrated on a phone through Streamlit Community Cloud. The prototype should feel like an app first, while keeping the implementation simple enough to evolve into a real PWA later.

## Streamlit.app MVP Scope

These features are suitable for the first mobile demo:

- App-like mobile shell with Home, Scan, Recipe, Cart, and success-style screens.
- Manual ingredient entry as the stable primary flow.
- AI-generated recipe plan using configured Streamlit secrets.
- Local fallback plan generation when API secrets are unavailable.
- Detected ingredient display.
- Missing ingredient recommendations.
- Cart quantity controls and total recalculation.
- Mock checkout or order success state.
- Clear labels for prototype-only or future features.

## Future / Prototype-Only Features

These should remain visible in the UI where useful, but should be marked or handled as future work until the project moves beyond Streamlit:

- Native camera capture experience.
- Continuous live camera recognition.
- Barcode scanning.
- Real retailer inventory lookup.
- Real checkout and payment.
- Delivery quote and order tracking.
- Push notifications.
- Offline PWA behavior.

## Recommended Product Flow

1. User opens Home and sees current detected ingredients plus recipe recommendation.
2. User taps Scan Your Fridge.
3. Scan screen offers:
   - Manual ingredient entry for MVP.
   - Photo/camera capture as future or beta.
4. User generates a meal plan.
5. App routes to Recipe and shows:
   - Meal title.
   - Reasoning summary.
   - Ingredients used.
   - Missing ingredients.
   - Recipe steps.
6. User taps missing ingredients to open Cart.
7. User adjusts quantities and sees total update.
8. User taps Place Order and sees a mock success screen.

## Streamlit vs PWA Boundary

Streamlit is enough for the first phone demo, especially for validating the product story and end-to-end flow. It is not ideal for fine-grained mobile interactions, native camera behavior, offline support, push notifications, or production checkout.

When the prototype is ready to become a real app, the suggested path is:

- Frontend: React with Vite or Next.js.
- PWA: manifest, service worker, installable shell.
- Backend: FastAPI or serverless API.
- Vision: photo upload to a model or recognition API.
- Commerce: retailer inventory/cart/order APIs.

## Implementation Notes

- Keep state explicit: ingredients, generated plan, cart quantities, and selected screen.
- Treat each app screen as a separate render function.
- Keep action functions separate from render functions where possible.
- For Streamlit-only HTML buttons, use query params or native Streamlit widgets so actions actually reach Python.
- Avoid silent placeholder buttons; future features should show a clear prototype/future response.
