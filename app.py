import json
import re
from openai import OpenAI
import streamlit as st

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
MODEL_SECRET_KEYS = ("model", "default_model")

PROMO_CATALOG = [
    {"name": "雞胸肉", "category": "肉品", "price": 89, "promo": "高蛋白主打"},
    {"name": "青蔥", "category": "蔬菜", "price": 25, "promo": "新鮮配菜組"},
    {"name": "沙茶醬", "category": "調味", "price": 69, "promo": "台式熱炒常備"},
    {"name": "醬油", "category": "調味", "price": 55, "promo": "日常料理基礎"},
    {"name": "白米", "category": "主食", "price": 199, "promo": "家庭號"},
    {"name": "豆腐", "category": "蛋白質", "price": 29, "promo": "冷藏促銷"},
    {"name": "高麗菜", "category": "蔬菜", "price": 49, "promo": "當季蔬菜"},
    {"name": "雞蛋", "category": "蛋白質", "price": 79, "promo": "早餐與便當組"},
]

PARTNER_SOURCES = [
    {
        "name": "FreshMart",
        "type": "Full-line supermarket",
        "offer": "Fresh dinner bundle",
        "inventory": "184 promoted SKUs",
        "accent": "green",
    },
    {
        "name": "CitySuper Express",
        "type": "Premium urban grocery",
        "offer": "Ready-to-cook chilled sets",
        "inventory": "62 promoted SKUs",
        "accent": "red",
    },
    {
        "name": "PX Market",
        "type": "Neighborhood fresh market",
        "offer": "Value family basket",
        "inventory": "127 promoted SKUs",
        "accent": "yellow",
    },
    {
        "name": "Organic Farm Direct",
        "type": "Farm and produce partner",
        "offer": "Seasonal vegetable add-ons",
        "inventory": "38 promoted SKUs",
        "accent": "blue",
    },
]

SAMPLE_INGREDIENTS = "雞蛋, 豆腐, 高麗菜, 剩飯"

st.set_page_config(
    page_title="AI Meal-to-Cart Engine",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --paper: #f8f2e8;
        --ink: #25211c;
        --muted: #75695e;
        --line: #ded1be;
        --market: #2f6f4e;
        --market-dark: #244f3a;
        --tomato: #b84536;
        --cream: #fffaf1;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {
        background:
            linear-gradient(180deg, rgba(248, 242, 232, 0.98), rgba(243, 235, 222, 0.99)),
            repeating-linear-gradient(90deg, rgba(47, 111, 78, 0.035) 0 1px, transparent 1px 44px);
        color: var(--ink);
    }
    .block-container {
        max-width: 860px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }
    .hero {
        border-bottom: 2px solid var(--ink);
        padding: 0.75rem 0 1.1rem;
        margin-bottom: 1.1rem;
    }
    .kicker {
        color: var(--market);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .title {
        color: var(--ink);
        font-family: Georgia, "Times New Roman", "Noto Serif TC", serif;
        font-size: clamp(2.2rem, 7.4vw, 4.1rem);
        font-weight: 800;
        line-height: 0.98;
        margin: 0;
    }
    .deck {
        color: var(--muted);
        font-size: 1.02rem;
        line-height: 1.55;
        max-width: 42rem;
        margin-top: 0.75rem;
    }
    .section-label {
        align-items: center;
        color: var(--ink);
        display: flex;
        font-size: 0.84rem;
        font-weight: 800;
        gap: 0.65rem;
        letter-spacing: 0.06em;
        margin: 1.35rem 0 0.65rem;
        text-transform: uppercase;
    }
    .section-label:after {
        background: var(--line);
        content: "";
        flex: 1;
        height: 1px;
    }
    .metric-row {
        display: grid;
        gap: 0.75rem;
        grid-template-columns: repeat(3, 1fr);
        margin: 0.5rem 0 1rem;
    }
    .metric {
        background: var(--cream);
        border: 1px solid var(--line);
        padding: 0.8rem;
    }
    .metric b {
        display: block;
        font-size: 1.4rem;
        color: var(--market-dark);
    }
    .metric span {
        color: var(--muted);
        font-size: 0.84rem;
    }
    .commerce-strip {
        background: var(--ink);
        color: var(--cream);
        display: grid;
        gap: 0.9rem;
        grid-template-columns: 1.2fr 1fr auto;
        margin: 1.25rem 0 1.1rem;
        padding: 1rem;
        position: relative;
    }
    .commerce-strip:before {
        background: var(--tomato);
        content: "";
        height: 100%;
        left: 0;
        position: absolute;
        top: 0;
        width: 5px;
    }
    .commerce-kicker {
        color: #e7c96f;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .commerce-title {
        font-family: Georgia, "Times New Roman", "Noto Serif TC", serif;
        font-size: clamp(1.25rem, 3.8vw, 1.85rem);
        font-weight: 800;
        line-height: 1.05;
        margin-top: 0.2rem;
    }
    .commerce-copy {
        color: #d8cdbc;
        font-size: 0.92rem;
        line-height: 1.45;
    }
    .commerce-chip {
        align-self: center;
        border: 1px solid rgba(255, 250, 241, 0.35);
        color: var(--cream);
        font-size: 0.82rem;
        font-weight: 800;
        justify-self: end;
        padding: 0.48rem 0.62rem;
        text-transform: uppercase;
    }
    .source-grid {
        display: grid;
        gap: 0.75rem;
        grid-template-columns: repeat(4, 1fr);
        margin: 0.55rem 0 1.2rem;
    }
    .source-card {
        background: var(--cream);
        border: 1px solid var(--line);
        min-height: 10.5rem;
        padding: 0.78rem;
    }
    .source-card.green { border-top: 5px solid var(--market); }
    .source-card.red { border-top: 5px solid var(--tomato); }
    .source-card.yellow { border-top: 5px solid #d8a51d; }
    .source-card.blue { border-top: 5px solid #3e6d8f; }
    .source-name {
        color: var(--ink);
        font-family: Georgia, "Times New Roman", "Noto Serif TC", serif;
        font-size: 1.02rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .source-type {
        color: var(--muted);
        font-size: 0.78rem;
        line-height: 1.35;
        margin-top: 0.25rem;
        min-height: 2.1rem;
    }
    .source-offer {
        color: var(--ink);
        font-size: 0.86rem;
        font-weight: 700;
        line-height: 1.35;
        margin-top: 0.85rem;
    }
    .source-link {
        color: var(--market-dark);
        display: block;
        font-size: 0.78rem;
        font-weight: 800;
        margin-top: 0.7rem;
        text-decoration: none;
        text-transform: uppercase;
    }
    .impact-panel {
        background: #ecdfcb;
        border: 1px solid #c9b89d;
        display: grid;
        gap: 0.8rem;
        grid-template-columns: 1.1fr repeat(3, 1fr);
        margin: 1.15rem 0 1rem;
        padding: 1rem;
    }
    .impact-lead {
        color: var(--ink);
        font-family: Georgia, "Times New Roman", "Noto Serif TC", serif;
        font-size: 1.25rem;
        font-weight: 800;
        line-height: 1.12;
    }
    .impact-note {
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.4;
        margin-top: 0.35rem;
    }
    .impact-metric {
        background: rgba(255, 250, 241, 0.55);
        border: 1px solid rgba(37, 33, 28, 0.12);
        padding: 0.7rem;
    }
    .impact-metric b {
        color: var(--market-dark);
        display: block;
        font-size: 1.3rem;
        line-height: 1.1;
    }
    .impact-metric span {
        color: var(--muted);
        font-size: 0.76rem;
        line-height: 1.3;
    }
    .stButton>button {
        background: var(--cream);
        border: 1px solid var(--line);
        border-radius: 3px;
        color: var(--ink);
        min-height: 3.1rem;
        height: auto;
        font-weight: 700;
        line-height: 1.25;
        white-space: normal;
        transition: 0.2s;
    }
    .stButton>button:hover {
        border-color: var(--market);
        color: var(--market);
        transform: translateY(-1px);
    }
    .stButton>button[kind="primary"] {
        background: var(--market);
        border-color: var(--market);
        color: #fffaf1;
    }
    .stButton>button[kind="primary"]:hover {
        background: var(--market-dark);
        border-color: var(--market-dark);
        color: #fffaf1;
    }
    .stTextArea textarea {
        background: var(--cream);
        border: 1px solid var(--line);
        border-radius: 3px;
        color: var(--ink);
        font-size: 1rem;
        line-height: 1.45;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--cream);
        border: 1px solid var(--line);
        border-radius: 3px;
        box-shadow: none;
    }
    h2, h3 {
        color: var(--ink);
        font-family: Georgia, "Times New Roman", "Noto Serif TC", serif;
    }
    div[data-testid="stAlert"] { border-radius: 3px; }
    @media (max-width: 640px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 0.5rem; }
        .title { font-size: 2.35rem; }
        .metric-row { grid-template-columns: 1fr; }
        .commerce-strip { grid-template-columns: 1fr; }
        .commerce-chip { justify-self: start; }
        .source-grid { grid-template-columns: 1fr; }
        .impact-panel { grid-template-columns: 1fr; }
        [data-testid="stTextArea"] textarea { min-height: 132px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def read_runtime_config():
    try:
        api_key = st.secrets.get("api_key")
        model = next((st.secrets.get(key) for key in MODEL_SECRET_KEYS if st.secrets.get(key)), None)
    except Exception:
        return {
            "ready": False,
            "api_key": "",
            "model": "",
            "error": "Missing Streamlit secrets. Add api_key and default_model in the app secrets.",
        }

    missing = []
    if not api_key:
        missing.append("api_key")
    if not model:
        missing.append("default_model or model")

    if missing:
        return {
            "ready": False,
            "api_key": "",
            "model": "",
            "error": f"Missing required secrets: {', '.join(missing)}.",
        }

    return {"ready": True, "api_key": api_key, "model": model, "error": ""}


def clean_response(raw):
    raw = re.sub(r"<thought>.*?</thought>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    raw = re.sub(r"```[a-zA-Z]*\n?|```", "", raw)
    return raw.strip()


def catalog_as_prompt():
    return "\n".join(
        f"- {item['name']} / {item['category']} / NT${item['price']} / {item['promo']}"
        for item in PROMO_CATALOG
    )


def render_retail_media_banner():
    st.markdown(
        """
        <div class="commerce-strip">
            <div>
                <div class="commerce-kicker">Sponsored Retail Media Slot</div>
                <div class="commerce-title">High-protein dinner basket</div>
            </div>
            <div class="commerce-copy">
                Simulated brand placement for chicken, eggs, tofu, and chilled meal solutions.
                The banner follows the shopper's meal intent instead of interrupting it.
            </div>
            <div class="commerce-chip">Mock Ad Link</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_partner_sources():
    cards = []
    for source in PARTNER_SOURCES:
        cards.append(
            f"""
            <div class="source-card {source['accent']}">
                <div class="source-name">{source['name']}</div>
                <div class="source-type">{source['type']}</div>
                <div class="source-offer">{source['offer']}</div>
                <div class="source-type">{source['inventory']}</div>
                <a class="source-link" href="#">Simulated checkout link</a>
            </div>
            """
        )

    st.markdown('<div class="section-label">Partner Grocery Sources</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="source-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_business_impact(plan):
    products = plan.get("recommended_products", [])
    cart = plan.get("cart_summary", {})
    estimated_total = cart.get("estimated_total", 0)
    item_count = cart.get("item_count", len(products))
    sponsored_slots = max(1, min(3, len(products)))

    st.markdown(
        f"""
        <div class="impact-panel">
            <div>
                <div class="impact-lead">Commercial impact view</div>
                <div class="impact-note">For retailers, this converts meal intent into promoted-product demand and measurable media inventory.</div>
            </div>
            <div class="impact-metric"><b>{item_count}</b><span>cart-ready promoted items</span></div>
            <div class="impact-metric"><b>NT${estimated_total}</b><span>simulated incremental basket</span></div>
            <div class="impact-metric"><b>{sponsored_slots}</b><span>available sponsored placements</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def generate_plan(api_key, model, owned_ingredients, business_goal):
    system_prompt = f"""
You are a retail meal-to-cart planning engine for a grocery retailer.
Create one practical dinner plan using the user's current ingredients and the retailer promotion catalog.
Prefer promoted products only when they make culinary and commercial sense.
Do not invent product names outside the catalog.

Retail business goal:
{business_goal}

Promotion catalog:
{catalog_as_prompt()}

Return strict JSON with this schema:
{{
  "meal_title": "string",
  "reasoning_summary": "string",
  "owned_ingredients": ["string"],
  "missing_items": ["string"],
  "recommended_products": [
    {{"name": "string", "reason": "string", "estimated_price": 0}}
  ],
  "recipe_steps": ["string"],
  "cart_summary": {{"item_count": 0, "estimated_total": 0}}
}}
"""
    client = OpenAI(api_key=api_key, base_url=DEFAULT_BASE_URL)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User-owned ingredients: {owned_ingredients}"},
        ],
        response_format={"type": "json_object"},
    )
    raw = clean_response(response.choices[0].message.content)
    match = re.search(r"(\{.*\})", raw, re.DOTALL)
    if not match:
        raise ValueError("Model did not return parseable JSON.")
    parsed = json.loads(match.group(1))
    if not isinstance(parsed.get("recommended_products"), list):
        raise ValueError("Model JSON is missing recommended_products.")
    return parsed


def render_plan(plan):
    st.markdown('<div class="section-label">Meal Recommendation</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader(plan.get("meal_title", "Dinner Plan"))
        st.write(plan.get("reasoning_summary", ""))

    owned = plan.get("owned_ingredients", [])
    missing = plan.get("missing_items", [])
    products = plan.get("recommended_products", [])
    cart = plan.get("cart_summary", {})

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric"><b>{len(owned)}</b><span>已有食材</span></div>
            <div class="metric"><b>{len(products)}</b><span>推薦商品</span></div>
            <div class="metric"><b>NT${cart.get('estimated_total', 0)}</b><span>模擬購物車</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-label">Already Have</div>', unsafe_allow_html=True)
        st.write(", ".join(owned) if owned else "No owned ingredients listed.")

        st.markdown('<div class="section-label">Missing Items</div>', unsafe_allow_html=True)
        st.write(", ".join(missing) if missing else "No missing items.")

    with col2:
        st.markdown('<div class="section-label">Add to Cart</div>', unsafe_allow_html=True)
        for product in products:
            with st.container(border=True):
                st.markdown(f"**{product.get('name', 'Product')}**")
                st.caption(f"NT${product.get('estimated_price', 0)}")
                st.write(product.get("reason", ""))

    st.markdown('<div class="section-label">Recipe Steps</div>', unsafe_allow_html=True)
    for index, step in enumerate(plan.get("recipe_steps", []), start=1):
        st.write(f"{index}. {step}")

    render_business_impact(plan)

    c1, c2, c3 = st.columns(3)
    c1.button("Add all to cart", use_container_width=True)
    c2.button("Replace cheaper", use_container_width=True)
    c3.button("Make vegetarian", use_container_width=True)


runtime_config = read_runtime_config()

st.markdown(
    """
    <section class="hero">
        <div class="kicker">Retail Demo / AI Meal-to-Cart Engine</div>
        <div class="title">From Fridge to Cart</div>
        <div class="deck">Convert home ingredients and weekly promotions into a practical dinner plan with a simulated grocery cart.</div>
    </section>
    """,
    unsafe_allow_html=True,
)

if not runtime_config["ready"]:
    st.error(runtime_config["error"])
    st.info("Set api_key and default_model in Streamlit secrets before generating plans.")

with st.sidebar:
    st.title("Demo Settings")
    if runtime_config["ready"]:
        st.success("Secrets loaded")
        st.text_input("Model", value=runtime_config["model"], disabled=True)
    business_goal = st.selectbox(
        "Retail objective",
        [
            "Increase fresh food basket size",
            "Move promoted chilled products",
            "Build a low-cost family dinner cart",
            "Promote high-protein meal solutions",
        ],
    )

st.markdown('<div class="section-label">Current Fridge</div>', unsafe_allow_html=True)
owned_ingredients = st.text_area(
    "What does the shopper already have?",
    value=SAMPLE_INGREDIENTS,
    height=120,
)

render_retail_media_banner()
render_partner_sources()

st.markdown('<div class="section-label">Promotion Catalog</div>', unsafe_allow_html=True)
st.dataframe(PROMO_CATALOG, use_container_width=True, hide_index=True)

st.markdown('<div class="section-label">Generate Plan</div>', unsafe_allow_html=True)
if st.button("Generate meal-to-cart plan", type="primary", use_container_width=True):
    if not runtime_config["ready"]:
        st.error(runtime_config["error"])
    elif not owned_ingredients.strip():
        st.warning("Add at least one owned ingredient.")
    else:
        with st.spinner("Building dinner plan and simulated cart..."):
            try:
                plan = generate_plan(
                    runtime_config["api_key"],
                    runtime_config["model"],
                    owned_ingredients,
                    business_goal,
                )
                st.session_state["last_plan"] = plan
            except Exception as exc:
                st.error(f"Generation failed: {exc}")

if st.session_state.get("last_plan"):
    render_plan(st.session_state["last_plan"])

st.markdown("---")
st.caption("Demo prototype. No real retailer checkout integration yet.")
