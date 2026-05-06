import json
import re

import streamlit as st
from openai import OpenAI

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
MODEL_SECRET_KEYS = ("model", "default_model")

PROMO_CATALOG = [
    {"商品": "雞胸肉", "分類": "肉品", "價格": 89, "促銷主題": "高蛋白主打"},
    {"商品": "青蔥", "分類": "蔬菜", "價格": 25, "促銷主題": "新鮮配菜組"},
    {"商品": "沙茶醬", "分類": "調味", "價格": 69, "促銷主題": "台式熱炒常備"},
    {"商品": "醬油", "分類": "調味", "價格": 55, "促銷主題": "日常料理基礎"},
    {"商品": "白米", "分類": "主食", "價格": 199, "促銷主題": "家庭號"},
    {"商品": "豆腐", "分類": "蛋白質", "價格": 29, "促銷主題": "冷藏促銷"},
    {"商品": "高麗菜", "分類": "蔬菜", "價格": 49, "促銷主題": "當季蔬菜"},
    {"商品": "雞蛋", "分類": "蛋白質", "價格": 79, "促銷主題": "早餐與便當組"},
]

PARTNER_SOURCES = [
    {
        "name": "鮮選超市",
        "type": "全品項生鮮量販",
        "offer": "晚餐生鮮組合",
        "inventory": "184 個促銷品項",
        "link": "模擬結帳連結",
        "color": "#2f6f4e",
        "bg": "#eef7f1",
    },
    {
        "name": "城市精品超市",
        "type": "都會高端通路",
        "offer": "冷藏即煮料理包",
        "inventory": "62 個促銷品項",
        "link": "模擬結帳連結",
        "color": "#b84536",
        "bg": "#fff0eb",
    },
    {
        "name": "鄰里平價市場",
        "type": "社區型生鮮通路",
        "offer": "家庭平價菜籃",
        "inventory": "127 個促銷品項",
        "link": "模擬結帳連結",
        "color": "#b88308",
        "bg": "#fff8df",
    },
    {
        "name": "產地直送農場",
        "type": "蔬果與產地合作",
        "offer": "當季蔬菜加購",
        "inventory": "38 個促銷品項",
        "link": "模擬結帳連結",
        "color": "#3e6d8f",
        "bg": "#edf6fb",
    },
]

BUSINESS_GOALS = [
    "提高生鮮購物籃金額",
    "推動冷藏促銷商品銷售",
    "建立低成本家庭晚餐購物車",
    "推廣高蛋白料理方案",
]

SAMPLE_INGREDIENTS = "雞蛋, 豆腐, 高麗菜, 剩飯"

st.set_page_config(
    page_title="AI 食材到購物車引擎",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.html(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f8f2e8 0%, #f3eadb 100%);
    }
    .block-container {
        max-width: 900px;
        padding-top: 4.2rem;
        padding-bottom: 3rem;
    }
    @media (max-width: 640px) {
        .block-container {
            padding-top: 5rem;
        }
    }
    h1, h2, h3 {
        color: #25211c;
    }
    [data-testid="stMetric"] {
        background: #fffaf1;
        border: 1px solid #ded1be;
        padding: 0.75rem;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #fffaf1;
        border-color: #ded1be;
    }
    </style>
    """
)


def color_block(
    title,
    body,
    eyebrow="",
    bg="#fffaf1",
    color="#2f6f4e",
    text_color="#25211c",
    body_color="#65594f",
):
    st.html(
        f"""
        <div style="
            background:{bg};
            border:1px solid rgba(37,33,28,.16);
            border-left:8px solid {color};
            padding:18px 20px;
            margin:10px 0 16px;
            color:{text_color};">
            <div style="
                color:{color};
                font-size:13px;
                font-weight:800;
                letter-spacing:.08em;
                margin-bottom:6px;">{eyebrow}</div>
            <div style="
                color:{text_color};
                font-size:24px;
                font-weight:800;
                line-height:1.18;
                margin-bottom:7px;">{title}</div>
            <div style="
                color:{body_color};
                font-size:15px;
                line-height:1.6;">{body}</div>
        </div>
        """
    )


def source_block(source):
    st.html(
        f"""
        <div style="
            background:{source['bg']};
            border:1px solid rgba(37,33,28,.14);
            border-top:7px solid {source['color']};
            min-height:155px;
            padding:16px;
            margin-bottom:12px;
            color:#25211c;">
            <div style="font-size:20px;font-weight:800;margin-bottom:4px;">{source['name']}</div>
            <div style="color:#75695e;font-size:13px;margin-bottom:16px;">{source['type']}</div>
            <div style="font-size:15px;font-weight:700;margin-bottom:8px;">{source['offer']}</div>
            <div style="color:#75695e;font-size:14px;">{source['inventory']}</div>
            <div style="
                color:{source['color']};
                font-size:13px;
                font-weight:800;
                margin-top:12px;">{source['link']}</div>
        </div>
        """
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
            "error": "尚未設定 Streamlit 密鑰。請加入 api_key 與 default_model。",
        }

    missing = []
    if not api_key:
        missing.append("api_key")
    if not model:
        missing.append("default_model 或 model")

    if missing:
        return {
            "ready": False,
            "api_key": "",
            "model": "",
            "error": f"缺少必要設定：{', '.join(missing)}。",
        }

    return {"ready": True, "api_key": api_key, "model": model, "error": ""}


def clean_response(raw):
    raw = re.sub(r"<thought>.*?</thought>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    raw = re.sub(r"```[a-zA-Z]*\n?|```", "", raw)
    return raw.strip()


def catalog_as_prompt():
    return "\n".join(
        f"- {item['商品']} / {item['分類']} / NT${item['價格']} / {item['促銷主題']}"
        for item in PROMO_CATALOG
    )


def render_retail_media_banner():
    st.subheader("模擬零售媒體版位")
    color_block(
        "本週主推：高蛋白晚餐購物籃",
        "模擬品牌贊助版位：雞胸肉、雞蛋、豆腐與冷藏料理商品。重點是跟著使用者的晚餐需求出現，而不是單純插入廣告。",
        eyebrow="零售媒體版位",
        bg="#25211c",
        color="#e7c96f",
        text_color="#fffaf1",
        body_color="#e9ddcd",
    )


def render_partner_sources():
    st.subheader("模擬多來源生鮮通路")
    cols = st.columns(2)
    for index, source in enumerate(PARTNER_SOURCES):
        with cols[index % 2]:
            source_block(source)


def render_business_impact(plan):
    products = plan.get("recommended_products", [])
    cart = plan.get("cart_summary", {})
    estimated_total = cart.get("estimated_total", 0)
    item_count = cart.get("item_count", len(products))
    sponsored_slots = max(1, min(3, len(products)))

    st.subheader("商業成效模擬")
    color_block(
        "把晚餐意圖轉成可衡量的零售機會",
        "這個區塊讓主管看到：系統不只是生成食譜，而是把消費者需求轉成促銷商品、加購金額與可銷售媒體版位。",
        eyebrow="主管視角",
        bg="#ecdfcb",
        color="#2f6f4e",
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("可加入購物車商品", item_count)
    col2.metric("模擬加購金額", f"NT${estimated_total}")
    col3.metric("可銷售版位", sponsored_slots)


def generate_plan(api_key, model, owned_ingredients, business_goal):
    system_prompt = f"""
你是一個服務零售通路的 AI 食材到購物車規劃引擎。
請根據使用者家中已有食材，以及零售商促銷商品清單，產生一份實用晚餐方案。
只有在料理邏輯與商業目標合理時，才推薦促銷商品。
不可捏造促銷清單以外的商品名稱。
所有輸出內容請使用繁體中文。

零售商業目標：
{business_goal}

促銷商品清單：
{catalog_as_prompt()}

請回傳嚴格 JSON，格式如下：
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
            {"role": "user", "content": f"使用者已有食材：{owned_ingredients}"},
        ],
        response_format={"type": "json_object"},
    )
    raw = clean_response(response.choices[0].message.content)
    match = re.search(r"(\{.*\})", raw, re.DOTALL)
    if not match:
        raise ValueError("模型沒有回傳可解析的 JSON。")
    parsed = json.loads(match.group(1))
    if not isinstance(parsed.get("recommended_products"), list):
        raise ValueError("模型 JSON 缺少 recommended_products。")
    return parsed


def render_plan(plan):
    st.header("AI 晚餐與購物車建議")
    with st.container(border=True):
        st.subheader(plan.get("meal_title", "晚餐方案"))
        st.write(plan.get("reasoning_summary", ""))

    owned = plan.get("owned_ingredients", [])
    missing = plan.get("missing_items", [])
    products = plan.get("recommended_products", [])
    cart = plan.get("cart_summary", {})

    col1, col2, col3 = st.columns(3)
    col1.metric("已有食材", len(owned))
    col2.metric("推薦商品", len(products))
    col3.metric("模擬購物車", f"NT${cart.get('estimated_total', 0)}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("家中已有")
        st.write("、".join(owned) if owned else "尚未列出已有食材。")

        st.subheader("仍需補齊")
        st.write("、".join(missing) if missing else "不需補齊其他食材。")

    with col2:
        st.subheader("建議加入購物車")
        for product in products:
            with st.container(border=True):
                st.markdown(f"**{product.get('name', '商品')}**")
                st.caption(f"NT${product.get('estimated_price', 0)}")
                st.write(product.get("reason", ""))

    st.subheader("料理步驟")
    for index, step in enumerate(plan.get("recipe_steps", []), start=1):
        st.write(f"{index}. {step}")

    render_business_impact(plan)

    c1, c2, c3 = st.columns(3)
    c1.button("全部加入購物車", use_container_width=True)
    c2.button("改用更便宜商品", use_container_width=True)
    c3.button("改成蔬食版本", use_container_width=True)


runtime_config = read_runtime_config()

color_block(
    "AI 食材到購物車引擎",
    "把冰箱現有食材、賣場促銷商品與晚餐需求，轉成可加購、可衡量、可銷售的零售方案。",
    eyebrow="賣場與品牌通路展示原型",
    bg="#fffaf1",
    color="#2f6f4e",
)

if not runtime_config["ready"]:
    st.error(runtime_config["error"])
    st.info("請在 Streamlit Cloud 的應用程式設定裡加入 api_key 與 default_model 後再產生方案。")

with st.sidebar:
    st.title("展示設定")
    if runtime_config["ready"]:
        st.success("密鑰已載入")
        st.text_input("模型", value=runtime_config["model"], disabled=True)
    business_goal = st.selectbox("零售商業目標", BUSINESS_GOALS)

st.header("使用者家中食材")
owned_ingredients = st.text_area(
    "這位消費者目前有什麼食材？",
    value=SAMPLE_INGREDIENTS,
    height=120,
)

render_retail_media_banner()
render_partner_sources()

st.header("模擬促銷商品清單")
st.dataframe(PROMO_CATALOG, use_container_width=True, hide_index=True)

st.header("產生晚餐購物車")
if st.button("產生 AI 晚餐與購物車方案", type="primary", use_container_width=True):
    if not runtime_config["ready"]:
        st.error(runtime_config["error"])
    elif not owned_ingredients.strip():
        st.warning("請至少輸入一項已有食材。")
    else:
        with st.spinner("正在產生晚餐方案與模擬購物車..."):
            try:
                plan = generate_plan(
                    runtime_config["api_key"],
                    runtime_config["model"],
                    owned_ingredients,
                    business_goal,
                )
                st.session_state["last_plan"] = plan
            except Exception as exc:
                st.error(f"產生失敗：{exc}")

if st.session_state.get("last_plan"):
    render_plan(st.session_state["last_plan"])

st.divider()
st.caption("展示原型：目前尚未串接真實賣場 API、付款系統或正式結帳購物車。")
