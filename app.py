import html
import json
import re
import base64
from urllib.parse import quote

import streamlit as st
from openai import OpenAI

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
MODEL_SECRET_KEYS = ("model", "default_model")

PROMO_CATALOG = [
    {
        "name": "Heavy Cream",
        "category": "Dairy",
        "price": 2.49,
        "reason": "Makes tomato sauce smooth and rich.",
        "tone": "cream",
    },
    {
        "name": "Parmesan Cheese",
        "category": "Dairy",
        "price": 2.99,
        "reason": "Adds a nutty, salty finish.",
        "tone": "cheese",
    },
    {
        "name": "Fresh Basil",
        "category": "Herbs",
        "price": 1.79,
        "reason": "Brings a fresh green lift.",
        "tone": "basil",
    },
    {
        "name": "Garlic",
        "category": "Produce",
        "price": 0.89,
        "reason": "Builds the savory base.",
        "tone": "garlic",
    },
    {
        "name": "Pasta",
        "category": "Pantry",
        "price": 1.99,
        "reason": "Turns fridge odds and ends into dinner.",
        "tone": "pasta",
    },
    {
        "name": "Cherry Tomatoes",
        "category": "Produce",
        "price": 3.49,
        "reason": "Cooks down into a sweet quick sauce.",
        "tone": "tomato",
    },
]

BUSINESS_GOALS = [
    "Maximize basket value with relevant missing ingredients",
    "Prioritize fresh produce and dairy promotions",
    "Build a quick weeknight dinner plan",
    "Create a sponsored recipe placement",
]

SAMPLE_INGREDIENTS = "tomatoes, spinach, eggs, cheese"

FALLBACK_PLAN = {
    "meal_title": "Creamy Tomato Pasta",
    "reasoning_summary": (
        "A comforting, creamy pasta packed with juicy tomatoes, fresh spinach, "
        "parmesan, and basil."
    ),
    "owned_ingredients": ["Tomatoes", "Spinach", "Cheese", "Eggs"],
    "missing_items": ["Heavy Cream", "Parmesan Cheese", "Fresh Basil"],
    "recommended_products": [
        {"name": "Heavy Cream", "reason": "Makes the sauce smooth.", "estimated_price": 2.49},
        {"name": "Parmesan Cheese", "reason": "Adds salty depth.", "estimated_price": 2.99},
        {"name": "Fresh Basil", "reason": "Finishes the dish fresh.", "estimated_price": 1.79},
    ],
    "recipe_steps": [
        "Boil pasta until al dente.",
        "Simmer tomatoes with garlic and a splash of cream.",
        "Fold in spinach, pasta, parmesan, and torn basil.",
    ],
    "cart_summary": {"item_count": 3, "estimated_total": 7.27},
}

st.set_page_config(
    page_title="Freshwise",
    page_icon="FW",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def inject_theme():
    st.html(
        """
        <style>
        :root {
            --cream: #fffaf0;
            --paper: #fffdf7;
            --mint: #edf7df;
            --leaf: #2f7b3f;
            --leaf-dark: #0e3f2a;
            --lime: #a9c977;
            --orange: #ff6746;
            --gold: #f2bd58;
            --ink: #123624;
            --muted: #6f796b;
            --line: rgba(22, 63, 39, .12);
            --shadow: 0 18px 42px rgba(34, 68, 38, .14);
        }

        html,
        body,
        .stApp {
            min-height: 100%;
            background:
                radial-gradient(circle at 16% 4%, rgba(201, 226, 143, .46), transparent 280px),
                radial-gradient(circle at 88% 8%, rgba(245, 196, 97, .26), transparent 250px),
                linear-gradient(135deg, #fffdf7 0%, #f4efdd 100%);
            color: var(--ink);
        }

        header,
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] {
            display: none;
        }

        .block-container {
            max-width: 474px;
            padding: 12px 12px 32px;
        }

        h1, h2, h3, p {
            color: var(--ink);
            letter-spacing: 0;
        }

        .phone-shell {
            position: relative;
            overflow: visible;
            min-height: auto;
            border: 1px solid var(--line);
            border-radius: 32px;
            background: var(--paper);
            box-shadow: 0 18px 42px rgba(18, 42, 26, .12);
        }

        .phone-shell::before {
            display: none;
        }

        .status-bar {
            position: relative;
            z-index: 6;
            display: flex;
            justify-content: space-between;
            padding: 16px 22px 4px;
            color: #101a12;
            font-size: 14px;
            font-weight: 800;
        }

        .app-screen {
            min-height: auto;
            padding: 16px 18px 22px;
        }

        .top-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 14px;
        }

        .brand {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: var(--leaf);
            font-size: 23px;
            font-weight: 900;
        }

        .leaf-mark {
            position: relative;
            width: 26px;
            height: 26px;
        }

        .leaf-mark::before,
        .leaf-mark::after {
            content: "";
            position: absolute;
            border-radius: 22px 22px 4px 22px;
            background: linear-gradient(135deg, #83bf54, #2f7b3f);
            transform: rotate(-38deg);
        }

        .leaf-mark::before {
            width: 18px;
            height: 24px;
            left: 8px;
        }

        .leaf-mark::after {
            width: 14px;
            height: 20px;
            left: 0;
            top: 7px;
            opacity: .75;
            transform: rotate(34deg);
        }

        .icon-button {
            display: grid;
            place-items: center;
            width: 42px;
            height: 42px;
            border-radius: 999px;
            background: rgba(255, 255, 255, .82);
            border: 1px solid var(--line);
            box-shadow: 0 10px 24px rgba(32, 58, 32, .11);
            color: var(--leaf-dark);
            font-weight: 900;
        }

        .tap-link {
            color: inherit;
            text-decoration: none;
        }

        .tap-link:visited {
            color: inherit;
        }

        .title {
            margin: 20px 0 5px;
            font-size: 24px;
            line-height: 1.08;
            font-weight: 900;
        }

        .muted {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.45;
        }

        .scan-card {
            display: grid;
            grid-template-columns: 52px 1fr 42px;
            gap: 14px;
            align-items: center;
            margin: 18px 0 22px;
            padding: 18px;
            border-radius: 20px;
            color: white;
            background: linear-gradient(135deg, #65ad58 0%, #25743d 100%);
            box-shadow: 0 18px 34px rgba(37, 116, 61, .28);
        }

        .scan-symbol {
            display: grid;
            place-items: center;
            width: 52px;
            height: 52px;
            border: 2px dashed rgba(255, 255, 255, .78);
            border-radius: 18px;
            font-size: 22px;
            font-weight: 900;
        }

        .round-arrow {
            display: grid;
            place-items: center;
            width: 42px;
            height: 42px;
            border-radius: 999px;
            background: rgba(255, 255, 255, .92);
            color: var(--leaf);
            font-size: 24px;
            font-weight: 900;
        }

        .section-line {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 18px 0 10px;
            font-size: 15px;
            font-weight: 900;
        }

        .section-line span:last-child {
            color: var(--leaf);
            font-size: 12px;
            font-weight: 800;
        }

        .ingredient-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
        }

        .ingredient-card,
        .recipe-card,
        .metric-pill,
        .product-card,
        .step-card,
        .note-row {
            border: 1px solid var(--line);
            background: rgba(255, 253, 247, .92);
            box-shadow: 0 10px 26px rgba(42, 70, 39, .08);
        }

        .ingredient-card {
            position: relative;
            min-height: 86px;
            padding: 10px 7px;
            border-radius: 16px;
            text-align: center;
        }

        .count-badge {
            position: absolute;
            top: 8px;
            right: 8px;
            width: 18px;
            height: 18px;
            border-radius: 999px;
            background: #dff0bd;
            color: var(--leaf-dark);
            font-size: 10px;
            font-weight: 900;
            line-height: 18px;
        }

        .food-art {
            position: relative;
            width: 42px;
            height: 42px;
            margin: 3px auto 7px;
        }

        .food-art::before,
        .food-art::after {
            content: "";
            position: absolute;
            border-radius: 999px;
        }

        .food-art.tomato::before {
            inset: 9px 5px 4px;
            background: radial-gradient(circle at 34% 30%, #ff9571 0 16%, #e74e31 17% 100%);
        }

        .food-art.tomato::after {
            width: 18px;
            height: 12px;
            left: 13px;
            top: 3px;
            border-radius: 70% 10% 70% 10%;
            background: #5b9f3b;
            transform: rotate(-20deg);
        }

        .food-art.leaf::before,
        .food-art.basil::before {
            width: 28px;
            height: 34px;
            left: 7px;
            top: 4px;
            border-radius: 28px 28px 4px 28px;
            background: linear-gradient(135deg, #98cc66, #3b8c42);
            transform: rotate(-28deg);
        }

        .food-art.leaf::after,
        .food-art.basil::after {
            width: 21px;
            height: 26px;
            right: 3px;
            top: 11px;
            border-radius: 24px 24px 4px 24px;
            background: linear-gradient(135deg, #b8db7b, #58a045);
            transform: rotate(28deg);
        }

        .food-art.egg::before {
            inset: 4px 8px;
            background: linear-gradient(145deg, #fff5d5, #e8c99b);
            box-shadow: inset -5px -7px 10px rgba(172, 122, 56, .13);
        }

        .food-art.cheese::before {
            width: 35px;
            height: 29px;
            left: 4px;
            top: 8px;
            border-radius: 7px 14px 7px 7px;
            background: #f2bd58;
            clip-path: polygon(0 40%, 100% 0, 100% 100%, 0 100%);
        }

        .food-art.cheese::after {
            width: 7px;
            height: 7px;
            left: 20px;
            top: 20px;
            background: #d89a30;
            box-shadow: 10px 5px 0 #d89a30;
        }

        .food-art.cream::before {
            width: 24px;
            height: 34px;
            left: 9px;
            top: 5px;
            border-radius: 8px;
            background: linear-gradient(#fff8dc, #e8d4a8);
            border: 2px solid rgba(150, 116, 70, .18);
        }

        .food-art.garlic::before {
            inset: 8px 7px 3px;
            background: linear-gradient(#fff4dc, #e9cfa9);
            border-radius: 52% 52% 45% 45%;
        }

        .food-art.pasta::before {
            inset: 10px 4px;
            border: 5px solid #f2bd58;
            background: transparent;
            box-shadow: 9px 1px 0 -1px #f2bd58, -8px 2px 0 -1px #f2bd58;
        }

        .ingredient-card strong {
            display: block;
            overflow: hidden;
            color: var(--ink);
            font-size: 11px;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .recipe-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .recipe-card {
            overflow: hidden;
            border-radius: 18px;
        }

        .recipe-image,
        .hero-food {
            position: relative;
            display: grid;
            place-items: center;
            background:
                radial-gradient(circle at 50% 48%, #fff8df 0 28%, transparent 29%),
                radial-gradient(circle at 44% 45%, #ec5134 0 4%, transparent 5%),
                radial-gradient(circle at 57% 53%, #438f45 0 5%, transparent 6%),
                linear-gradient(135deg, #f7df9e, #9ecb71);
        }

        .recipe-image {
            height: 92px;
        }

        .plate {
            position: relative;
            width: 82px;
            height: 58px;
            border-radius: 50%;
            background: #fff9df;
            box-shadow: inset 0 0 0 7px #fffdf8, 0 8px 18px rgba(101, 80, 30, .18);
        }

        .plate::before {
            content: "";
            position: absolute;
            inset: 18px 12px;
            border-top: 5px solid #efbe57;
            border-bottom: 5px solid #efbe57;
            border-radius: 50%;
            transform: rotate(-10deg);
        }

        .plate::after {
            content: "";
            position: absolute;
            width: 10px;
            height: 10px;
            left: 24px;
            top: 18px;
            border-radius: 999px;
            background: #e85235;
            box-shadow: 22px 9px 0 #e85235, 13px -2px 0 #4d9747;
        }

        .recipe-body {
            padding: 11px;
        }

        .recipe-body strong {
            display: block;
            min-height: 32px;
            font-size: 13px;
            line-height: 1.2;
        }

        .recipe-meta {
            display: flex;
            justify-content: space-between;
            margin-top: 9px;
            color: var(--muted);
            font-size: 11px;
        }

        .promo-callout {
            display: grid;
            grid-template-columns: 50px 1fr 38px;
            gap: 12px;
            align-items: center;
            margin-top: 20px;
            padding: 14px;
            border-radius: 20px;
            background: linear-gradient(135deg, #ffe5d2, #fff0b8);
        }

        .basket-icon {
            position: relative;
            width: 42px;
            height: 42px;
            border-radius: 13px;
            background: #f3ae34;
        }

        .basket-icon::before {
            content: "";
            position: absolute;
            width: 18px;
            height: 12px;
            left: 10px;
            top: -2px;
            border: 3px solid #fff1c5;
            border-bottom: 0;
            border-radius: 12px 12px 0 0;
        }

        .hero-food {
            height: 292px;
            margin: -18px -22px 0;
            border-bottom-left-radius: 30px;
            border-bottom-right-radius: 30px;
        }

        .hero-food .plate {
            width: 210px;
            height: 148px;
        }

        .hero-food .plate::before {
            inset: 43px 28px;
            border-top-width: 11px;
            border-bottom-width: 11px;
        }

        .hero-food .plate::after {
            width: 20px;
            height: 20px;
            left: 60px;
            top: 47px;
            box-shadow: 54px 22px 0 #e85235, 34px -10px 0 #4d9747, 72px -3px 0 #4d9747;
        }

        .floating-actions {
            position: absolute;
            top: 86px;
            right: 22px;
            display: flex;
            gap: 10px;
        }

        .detail-sheet {
            position: relative;
            margin-top: -22px;
            padding: 22px 4px 0;
            border-radius: 28px 28px 0 0;
            background: var(--paper);
        }

        .detail-sheet h1,
        .cart-title {
            margin: 0 0 8px;
            font-size: 27px;
            line-height: 1.08;
            font-weight: 900;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin: 18px 0;
        }

        .metric-pill {
            border-radius: 15px;
            padding: 11px 8px;
            text-align: center;
        }

        .metric-pill strong {
            display: block;
            font-size: 13px;
        }

        .metric-pill span {
            color: var(--muted);
            font-size: 10px;
        }

        .missing-strip {
            display: grid;
            grid-template-columns: 44px 1fr auto;
            gap: 12px;
            align-items: center;
            margin-top: 18px;
            padding: 14px;
            border-radius: 18px;
            background: linear-gradient(135deg, #fff0b8, #ffe4c9);
        }

        .mini-button {
            padding: 10px 13px;
            border-radius: 12px;
            color: white;
            background: var(--orange);
            font-size: 12px;
            font-weight: 900;
        }

        .delivery {
            display: grid;
            grid-template-columns: 42px 1fr;
            gap: 12px;
            align-items: center;
            margin: 18px 0 10px;
            padding: 13px;
            border-radius: 18px;
            background: var(--mint);
        }

        .product-card {
            display: grid;
            grid-template-columns: 48px 1fr auto;
            gap: 12px;
            align-items: center;
            margin: 10px 0;
            padding: 12px;
            border-radius: 18px;
        }

        .product-card strong {
            display: block;
            font-size: 14px;
        }

        .price {
            margin-top: 6px;
            color: var(--ink);
            font-weight: 900;
        }

        .qty {
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--leaf);
            font-weight: 900;
        }

        .note-row {
            display: flex;
            justify-content: space-between;
            margin-top: 14px;
            padding: 14px;
            border-radius: 15px;
            color: var(--muted);
            font-size: 13px;
        }

        .ingredient-list {
            display: grid;
            gap: 10px;
            margin-top: 16px;
        }

        .ingredient-row-card {
            display: grid;
            grid-template-columns: 48px 1fr 34px;
            gap: 12px;
            align-items: center;
            padding: 12px;
            border: 1px solid var(--line);
            border-radius: 18px;
            background: rgba(255, 253, 247, .92);
            box-shadow: 0 10px 26px rgba(42, 70, 39, .08);
        }

        .confidence {
            display: inline-block;
            margin-top: 5px;
            padding: 4px 8px;
            border-radius: 999px;
            color: var(--leaf);
            background: var(--mint);
            font-size: 11px;
            font-weight: 900;
        }

        .future-card {
            display: grid;
            grid-template-columns: 48px 1fr auto;
            gap: 12px;
            align-items: center;
            margin-top: 14px;
            padding: 14px;
            border: 1px dashed rgba(47, 123, 63, .34);
            border-radius: 18px;
            background: rgba(237, 247, 223, .58);
        }

        .success-burst {
            position: relative;
            display: grid;
            place-items: center;
            width: 128px;
            height: 128px;
            margin: 48px auto 24px;
            border-radius: 999px;
            background: linear-gradient(135deg, #8fc95c, #2f7b3f);
            box-shadow: 0 22px 42px rgba(47, 123, 63, .26);
            color: white;
            font-size: 58px;
            font-weight: 900;
        }

        .success-card {
            padding: 20px;
            border: 1px solid var(--line);
            border-radius: 24px;
            background: rgba(255, 253, 247, .94);
            box-shadow: var(--shadow);
            text-align: center;
        }

        .total-box {
            margin-top: 14px;
            padding: 14px;
            border-radius: 17px;
            background: linear-gradient(135deg, #f5f9df, #e6f1d2);
        }

        .total-row {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 13px;
        }

        .total-row.big {
            margin-top: 12px;
            font-size: 22px;
            font-weight: 900;
            color: var(--leaf);
        }

        .order-button,
        .cook-button {
            display: grid;
            place-items: center;
            min-height: 54px;
            margin-top: 14px;
            border-radius: 999px;
            color: white;
            font-weight: 900;
        }

        .order-button {
            background: linear-gradient(135deg, #ff7850, #ff563d);
            box-shadow: 0 16px 26px rgba(255, 91, 62, .26);
        }

        .cook-button {
            background: linear-gradient(135deg, #3f9a4c, #28753d);
            box-shadow: 0 16px 26px rgba(47, 123, 63, .24);
        }

        .step-list {
            display: grid;
            gap: 10px;
            margin-top: 14px;
        }

        .step-card {
            display: grid;
            grid-template-columns: 32px 1fr;
            gap: 10px;
            padding: 13px;
            border-radius: 16px;
        }

        .step-card b {
            display: grid;
            place-items: center;
            width: 30px;
            height: 30px;
            border-radius: 999px;
            background: var(--mint);
            color: var(--leaf);
        }

        .scan-input-card {
            padding: 18px;
            border-radius: 24px;
            background: var(--paper);
            border: 1px solid var(--line);
            box-shadow: var(--shadow);
        }

        .scan-illustration {
            position: relative;
            height: 190px;
            margin-bottom: 18px;
            border-radius: 28px;
            background:
                linear-gradient(90deg, rgba(47, 123, 63, .10) 0 1px, transparent 1px 42px),
                linear-gradient(#ecf6df, #fff5d8);
            overflow: hidden;
        }

        .fridge {
            position: absolute;
            left: 92px;
            top: 24px;
            width: 136px;
            height: 145px;
            border: 7px solid rgba(70, 125, 92, .55);
            border-radius: 28px;
            background: rgba(226, 246, 222, .62);
            box-shadow: inset 0 0 0 3px rgba(255,255,255,.8);
        }

        .fridge::before,
        .fridge::after {
            content: "";
            position: absolute;
            left: 16px;
            right: 16px;
            height: 3px;
            background: rgba(70, 125, 92, .34);
        }

        .fridge::before { top: 48px; }
        .fridge::after { top: 94px; }

        .produce-bowl {
            position: absolute;
            left: 32px;
            bottom: 20px;
            width: 88px;
            height: 42px;
            border-radius: 10px 10px 44px 44px;
            background: #d89a44;
        }

        .produce-bowl::before {
            content: "";
            position: absolute;
            left: 15px;
            top: -22px;
            width: 22px;
            height: 22px;
            border-radius: 999px;
            background: #e85235;
            box-shadow: 28px 2px 0 #efbe57, 42px -14px 0 #5ba246;
        }

        div[data-testid="stTextArea"] textarea {
            min-height: 110px !important;
            border-radius: 18px;
            border-color: var(--line);
            background: rgba(255, 253, 247, .96);
            color: var(--ink);
            font-size: 16px;
        }

        div[data-testid="stRadio"] {
            margin-top: 12px;
            padding: 0;
        }

        div[data-testid="stRadio"] > label {
            display: none;
        }

        div[data-testid="stRadio"] [role="radiogroup"] {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 6px;
            padding: 10px;
            border: 1px solid var(--line);
            border-radius: 24px;
            background: rgba(255, 253, 247, .94);
            box-shadow: 0 12px 28px rgba(42, 70, 39, .08);
            backdrop-filter: blur(14px);
        }

        div[data-testid="stRadio"] [role="radio"] {
            justify-content: center;
            min-height: 48px;
            padding: 0 4px;
            border-radius: 16px;
            color: #596654;
            font-size: 12px;
            font-weight: 800;
        }

        div[data-testid="stRadio"] [aria-checked="true"] {
            background: var(--mint);
            color: var(--leaf);
        }

        div[data-testid="stRadio"] [role="radio"] > div:first-child {
            display: none;
        }

        .action-panel {
            margin: 12px 0 0;
            padding: 14px;
            border: 1px solid var(--line);
            border-radius: 24px;
            background: rgba(255, 253, 247, .94);
            box-shadow: 0 14px 32px rgba(42, 70, 39, .10);
        }

        .action-panel h3 {
            margin: 0 0 8px;
            font-size: 15px;
        }

        .action-panel p {
            margin: 0 0 12px;
            color: var(--muted);
            font-size: 12px;
        }

        .stButton > button {
            min-height: 54px;
            border: 0;
            border-radius: 999px;
            color: #fffdf7;
            background: linear-gradient(135deg, #3f9a4c, #28753d);
            box-shadow: 0 16px 26px rgba(47, 123, 63, .24);
            font-weight: 900;
        }

        @media (max-width: 520px) {
            .block-container {
                max-width: none;
                padding: 0 10px 24px;
            }

            .phone-shell {
                min-height: auto;
                border: 0;
                border-radius: 0 0 28px 28px;
                box-shadow: none;
            }

            .phone-shell::before {
                display: none;
            }

            .status-bar {
                padding-top: 16px;
            }

            .app-screen {
                min-height: auto;
            }

            div[data-testid="stRadio"] {
                margin-top: 12px;
            }

            .action-panel {
                margin-left: 14px;
                margin-right: 14px;
            }
        }
        </style>
        """
    )


def money(value):
    try:
        return f"${float(value):.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def esc(value):
    return html.escape(str(value), quote=True)


def app_href(screen, **params):
    query = {"screen": screen, **{key: value for key, value in params.items() if value is not None}}
    return "?" + "&".join(f"{quote(str(key))}={quote(str(value))}" for key, value in query.items())


def tone_for(name):
    lower = name.lower()
    if "tomato" in lower:
        return "tomato"
    if "spinach" in lower or "basil" in lower or "leaf" in lower:
        return "leaf"
    if "egg" in lower:
        return "egg"
    if "cheese" in lower or "parmesan" in lower:
        return "cheese"
    if "cream" in lower or "milk" in lower:
        return "cream"
    if "garlic" in lower:
        return "garlic"
    if "pasta" in lower:
        return "pasta"
    return "leaf"


def read_runtime_config():
    try:
        api_key = st.secrets.get("api_key")
        model = next((st.secrets.get(key) for key in MODEL_SECRET_KEYS if st.secrets.get(key)), None)
    except Exception:
        return {"ready": False, "api_key": "", "model": "", "error": "Add api_key and default_model in Streamlit secrets."}

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
            "error": f"Missing Streamlit secret: {', '.join(missing)}.",
        }

    return {"ready": True, "api_key": api_key, "model": model, "error": ""}


def parse_ingredients(value):
    parts = re.split(r"[,，\n]+", value or "")
    return [part.strip().title() for part in parts if part.strip()]


def local_plan_from_ingredients(ingredients):
    owned = ingredients or parse_ingredients(SAMPLE_INGREDIENTS)
    plan = dict(FALLBACK_PLAN)
    plan["owned_ingredients"] = owned
    lower_owned = " ".join(owned).lower()
    recommended = []
    for item in PROMO_CATALOG:
        name = item["name"]
        if name.lower() not in lower_owned and len(recommended) < 3:
            recommended.append(
                {
                    "name": name,
                    "reason": item["reason"],
                    "estimated_price": item["price"],
                }
            )

    if not recommended:
        recommended = FALLBACK_PLAN["recommended_products"]

    plan["recommended_products"] = recommended
    plan["missing_items"] = [product["name"] for product in recommended]
    plan["cart_summary"] = {
        "item_count": len(recommended),
        "estimated_total": round(sum(product["estimated_price"] for product in recommended), 2),
    }
    return plan


def current_ingredients():
    return st.session_state.setdefault("detected_ingredients", parse_ingredients(SAMPLE_INGREDIENTS))


def clean_response(raw):
    raw = re.sub(r"<thought>.*?</thought>", "", raw, flags=re.DOTALL | re.IGNORECASE)
    raw = re.sub(r"```[a-zA-Z]*\n?|```", "", raw)
    return raw.strip()


def catalog_as_prompt():
    return "\n".join(
        f"- {item['name']} / {item['category']} / ${item['price']:.2f} / {item['reason']}"
        for item in PROMO_CATALOG
    )


def generate_plan(api_key, model, owned_ingredients, business_goal):
    system_prompt = f"""
You are Freshwise, a meal-to-cart engine for a mobile grocery app.
Create one dinner recommendation from the user's existing ingredients and the retailer promotion catalog.
Business goal: {business_goal}

Promotion catalog:
{catalog_as_prompt()}

Return only valid JSON with this shape:
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
            {"role": "user", "content": f"Ingredients in my fridge: {owned_ingredients}"},
        ],
        response_format={"type": "json_object"},
    )
    raw = clean_response(response.choices[0].message.content)
    match = re.search(r"(\{.*\})", raw, re.DOTALL)
    if not match:
        raise ValueError("The model did not return JSON.")
    parsed = json.loads(match.group(1))
    if not isinstance(parsed.get("recommended_products"), list):
        raise ValueError("The JSON is missing recommended_products.")
    return parsed


def recognize_ingredients_from_image(api_key, model, image_bytes):
    encoded = base64.b64encode(image_bytes).decode("ascii")
    client = OpenAI(api_key=api_key, base_url=DEFAULT_BASE_URL)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Freshwise's fridge image recognition engine. "
                    "Identify visible food ingredients from the image. "
                    "Return only valid JSON like {\"ingredients\":[\"Tomatoes\",\"Spinach\"]}. "
                    "Use common grocery names and do not include non-food objects."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Identify ingredients visible in this fridge or food photo."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                    },
                ],
            },
        ],
        response_format={"type": "json_object"},
    )
    raw = clean_response(response.choices[0].message.content)
    match = re.search(r"(\{.*\})", raw, re.DOTALL)
    if not match:
        raise ValueError("The model did not return ingredient JSON.")
    parsed = json.loads(match.group(1))
    ingredients = parsed.get("ingredients", [])
    if not isinstance(ingredients, list):
        raise ValueError("The JSON is missing an ingredients list.")
    return [str(item).strip().title() for item in ingredients if str(item).strip()]


def generate_recipe_from_current_ingredients(runtime_config, business_goal):
    ingredients = current_ingredients()
    ingredient_text = ", ".join(ingredients)
    if runtime_config["ready"]:
        try:
            plan = generate_plan(
                runtime_config["api_key"],
                runtime_config["model"],
                ingredient_text,
                business_goal,
            )
            st.session_state["last_plan"] = plan
            st.session_state["generation_notice"] = "Generated with the configured multimodal model."
            return plan
        except Exception as exc:
            st.session_state["generation_notice"] = f"Model generation failed; using demo fallback. ({exc})"
    else:
        st.session_state["generation_notice"] = "API secrets are missing; using demo fallback."

    plan = local_plan_from_ingredients(ingredients)
    st.session_state["last_plan"] = plan
    return plan


def recognize_photo_into_ingredients(runtime_config, image_bytes):
    if runtime_config["ready"]:
        try:
            ingredients = recognize_ingredients_from_image(
                runtime_config["api_key"],
                runtime_config["model"],
                image_bytes,
            )
            st.session_state["detected_ingredients"] = ingredients
            st.session_state["last_plan"] = local_plan_from_ingredients(ingredients)
            st.session_state["generation_notice"] = "Photo recognized with the configured multimodal model."
            return ingredients
        except Exception as exc:
            st.session_state["generation_notice"] = f"Image recognition failed; please confirm manually. ({exc})"
            return []

    st.session_state["generation_notice"] = "API secrets are missing; photo recognition needs the multimodal model."
    return []


def normalize_plan(plan):
    merged = FALLBACK_PLAN | (plan or {})
    merged["owned_ingredients"] = merged.get("owned_ingredients") or FALLBACK_PLAN["owned_ingredients"]
    merged["missing_items"] = merged.get("missing_items") or FALLBACK_PLAN["missing_items"]
    merged["recommended_products"] = merged.get("recommended_products") or FALLBACK_PLAN["recommended_products"]
    merged["recipe_steps"] = merged.get("recipe_steps") or FALLBACK_PLAN["recipe_steps"]

    total = sum(float(product.get("estimated_price", 0) or 0) for product in merged["recommended_products"])
    cart = merged.get("cart_summary") or {}
    cart["item_count"] = cart.get("item_count") or len(merged["recommended_products"])
    cart["estimated_total"] = cart.get("estimated_total") or round(total, 2)
    merged["cart_summary"] = cart
    return merged


def sync_cart(plan):
    quantities = st.session_state.setdefault("cart_quantities", {})
    product_names = [product.get("name", "Ingredient") for product in plan["recommended_products"]]
    for name in product_names:
        quantities.setdefault(name, 1)
    for name in list(quantities):
        if name not in product_names:
            del quantities[name]


def cart_subtotal(plan):
    quantities = st.session_state.get("cart_quantities", {})
    total = 0.0
    count = 0
    for product in plan["recommended_products"]:
        name = product.get("name", "Ingredient")
        qty = int(quantities.get(name, 1))
        total += float(product.get("estimated_price", 0) or 0) * qty
        count += qty
    return round(total, 2), count


def handle_query_actions():
    params = st.query_params
    requested_screen = params.get("screen")
    action = params.get("cart_action")
    item = params.get("item")
    future = params.get("future")
    remove_ingredient = params.get("remove_ingredient")
    order = params.get("order")
    generate_recipe = params.get("generate_recipe")

    valid_screens = {"Home", "Ingredients", "Recipe", "Cart", "Scan", "OrderSuccess"}

    if generate_recipe:
        generate_recipe_from_current_ingredients(st.session_state["runtime_config"], st.session_state["business_goal"])
        st.session_state["screen_picker"] = "Recipe"
        st.query_params.clear()
        st.rerun()

    if future:
        st.session_state["future_notice"] = f"{future.replace('_', ' ').title()} is reserved for the PWA version."
        if requested_screen in valid_screens:
            st.session_state["screen_picker"] = requested_screen
        st.query_params.clear()
        st.rerun()

    if remove_ingredient:
        ingredients = [name for name in current_ingredients() if name != remove_ingredient]
        st.session_state["detected_ingredients"] = ingredients
        if requested_screen in valid_screens:
            st.session_state["screen_picker"] = requested_screen
        st.query_params.clear()
        st.rerun()

    if order == "place":
        subtotal, item_count = cart_subtotal(normalize_plan(st.session_state.get("last_plan", FALLBACK_PLAN)))
        st.session_state["last_order"] = {"subtotal": subtotal, "item_count": item_count}
        st.session_state["screen_picker"] = "OrderSuccess"
        st.query_params.clear()
        st.rerun()

    if action and item:
        if requested_screen in valid_screens:
            st.session_state["screen_picker"] = requested_screen
        quantities = st.session_state.setdefault("cart_quantities", {})
        current = int(quantities.get(item, 1))
        if action == "inc":
            quantities[item] = current + 1
        elif action == "dec":
            quantities[item] = max(0, current - 1)
        st.query_params.clear()
        st.rerun()

    if requested_screen in valid_screens:
        st.session_state["screen_picker"] = requested_screen
        st.query_params.clear()
        st.rerun()


def ingredient_cards(names, limit=4):
    cards = []
    for index, name in enumerate(names[:limit], start=1):
        tone = tone_for(name)
        cards.append(
            f"""
            <div class="ingredient-card">
                <div class="count-badge">{index}</div>
                <div class="food-art {tone}"></div>
                <strong>{esc(name)}</strong>
            </div>
            """
        )
    return "".join(cards)


def phone_frame(content):
    return f"""
    <div class="phone-shell">
        <div class="status-bar"><span>9:41</span><span>5G  100%</span></div>
        {content}
    </div>
    """


def render_home(plan):
    owned = list(current_ingredients()[:4])
    while len(owned) < 4:
        owned.append(["Tomatoes", "Eggs", "Spinach", "Cheese"][len(owned)])
    st.html(
        phone_frame(
            f"""
        <div class="app-screen">
            <div class="top-row">
                <div class="icon-button">=</div>
                <div class="brand"><span class="leaf-mark"></span><span>Freshwise</span></div>
                <div class="icon-button">!</div>
            </div>
            <h1 class="title">Good morning, Alex!</h1>
            <div class="muted">Let's turn your ingredients into something amazing.</div>

            <a class="tap-link scan-card" href="{app_href("Scan")}" target="_self">
                <div class="scan-symbol">[]</div>
                <div>
                    <strong>Scan Your Fridge</strong>
                    <div style="font-size:12px;opacity:.9;margin-top:4px;">Identify ingredients in seconds</div>
                </div>
                <div class="round-arrow">&gt;</div>
            </a>

            <div class="section-line"><span>Detected Ingredients</span><a class="tap-link" href="{app_href("Ingredients")}" target="_self">View all</a></div>
            <div class="ingredient-grid">{ingredient_cards(owned, 4)}</div>

            <div class="section-line"><span>Recommended Recipes</span><span>View all</span></div>
            <div class="recipe-grid">
                <a class="tap-link recipe-card" href="{app_href("Recipe")}" target="_self">
                    <div class="recipe-image"><div class="plate"></div></div>
                    <div class="recipe-body">
                        <strong>{esc(plan["meal_title"])}</strong>
                        <div class="recipe-meta"><span>25 min</span><span>Easy</span></div>
                    </div>
                </a>
                <a class="tap-link recipe-card" href="{app_href("Recipe")}" target="_self">
                    <div class="recipe-image"><div class="plate"></div></div>
                    <div class="recipe-body">
                        <strong>Veggie & Cheese Omelette</strong>
                        <div class="recipe-meta"><span>15 min</span><span>Easy</span></div>
                    </div>
                </a>
            </div>

            <a class="tap-link promo-callout" href="{app_href("Cart")}" target="_self">
                <div class="basket-icon"></div>
                <div>
                    <strong>Missing something?</strong>
                    <div class="muted">Order fresh ingredients delivered to you.</div>
                </div>
                <div class="round-arrow">&gt;</div>
            </a>
        </div>
        """
        )
    )


def render_recipe(plan):
    ingredients = (plan["owned_ingredients"] + plan["missing_items"])[:4]
    st.html(
        phone_frame(
            f"""
        <div class="app-screen">
            <div class="top-row">
                <a class="tap-link icon-button" href="{app_href("Home")}" target="_self">&lt;</a>
                <div></div>
                <div style="display:flex;gap:10px;">
                    <a class="tap-link icon-button" href="{app_href("Recipe", future="save_recipe")}" target="_self">H</a>
                    <a class="tap-link icon-button" href="{app_href("Recipe", future="share_recipe")}" target="_self">S</a>
                </div>
            </div>
            <div class="hero-food"><div class="plate"></div></div>
            <div class="detail-sheet">
                <h1>{esc(plan["meal_title"])}</h1>
                <div class="muted">{esc(plan["reasoning_summary"])}</div>
                <div class="metrics-grid">
                    <div class="metric-pill"><strong>25 min</strong><span>Prep Time</span></div>
                    <div class="metric-pill"><strong>Easy</strong><span>Difficulty</span></div>
                    <div class="metric-pill"><strong>420</strong><span>Calories</span></div>
                </div>
                <div class="section-line"><span>Uses These Ingredients</span><span></span></div>
                <div class="ingredient-grid">{ingredient_cards(ingredients, 4)}</div>
                <a class="tap-link missing-strip" href="{app_href("Cart")}" target="_self">
                    <div class="basket-icon"></div>
                    <div><strong>{len(plan["missing_items"])} ingredients missing</strong><div class="muted">Add them to your order</div></div>
                    <div class="mini-button">View</div>
                </a>
                <div class="section-line"><span>Steps</span><span></span></div>
                <div class="step-list">
                    {''.join(
                        f'<div class="step-card"><b>{index}</b><div>{esc(step)}</div></div>'
                        for index, step in enumerate(plan["recipe_steps"], start=1)
                    )}
                </div>
                <a class="tap-link cook-button" href="{app_href("Recipe", generate_recipe="1")}" target="_self">Cook Now</a>
            </div>
        </div>
        """
        )
    )


def render_cart(plan):
    products = plan["recommended_products"]
    subtotal, item_count = cart_subtotal(plan)
    delivery = 1.99
    total = subtotal + delivery
    st.html(
        phone_frame(
            f"""
        <div class="app-screen">
            <div class="top-row">
                <a class="tap-link icon-button" href="{app_href("Recipe")}" target="_self">&lt;</a>
                <div></div>
                <div class="icon-button">3</div>
            </div>
            <h1 class="cart-title">Missing Ingredients</h1>
            <div class="muted">For {esc(plan["meal_title"])}</div>
            <div class="delivery">
                <div class="basket-icon"></div>
                <div><strong>Fast delivery</strong><div class="muted">Fresh to your door in as little as 60 mins.</div></div>
            </div>
            {''.join(
                f'<div class="product-card"><div class="food-art {tone_for(product.get("name", ""))}"></div>'
                f'<div><strong>{esc(product.get("name", "Ingredient"))}</strong><div class="muted">{esc(product.get("reason", ""))}</div>'
                f'<div class="price">{money(product.get("estimated_price", 0))}</div></div>'
                f'<div class="qty"><a class="tap-link" href="{app_href("Cart", cart_action="dec", item=product.get("name", "Ingredient"))}" target="_self">-</a> '
                f'<span>{int(st.session_state.get("cart_quantities", {}).get(product.get("name", "Ingredient"), 1))}</span> '
                f'<a class="tap-link" href="{app_href("Cart", cart_action="inc", item=product.get("name", "Ingredient"))}" target="_self">+</a></div></div>'
                for product in products
            )}
            <a class="tap-link note-row" href="{app_href("Cart", future="shopper_note")}" target="_self"><span>Add a note for your shopper</span><span>&gt;</span></a>
            <div class="total-box">
                <div class="total-row"><span>Subtotal ({item_count} items)</span><span>{money(subtotal)}</span></div>
                <div class="total-row"><span>Delivery Fee</span><span>{money(delivery)}</span></div>
                <div class="total-row big"><span>Total</span><span>{money(total)}</span></div>
            </div>
            <a class="tap-link order-button" href="{app_href("OrderSuccess", order="place")}" target="_self">Place Order - {money(total)}</a>
            <div style="text-align:center;margin-top:10px;color:var(--leaf);font-size:12px;font-weight:800;">Secure checkout</div>
        </div>
        """
        )
    )


def render_scan(plan, runtime_config, business_goal):
    st.html(
        phone_frame(
            f"""
        <div class="app-screen">
            <div class="top-row">
                <a class="tap-link icon-button" href="{app_href("Home")}" target="_self">&lt;</a>
                <div class="brand"><span class="leaf-mark"></span><span>Freshwise</span></div>
                <a class="tap-link icon-button" href="{app_href("Scan", future="scan_help")}" target="_self">?</a>
            </div>
            <h1 class="title">Scan Your Fridge</h1>
            <div class="muted">For the Streamlit prototype, type or paste ingredients here. This screen becomes camera capture when the PWA is built.</div>
            <div class="scan-illustration">
                <div class="fridge"></div>
                <div class="produce-bowl"></div>
            </div>
        </div>
        """
        )
    )


def render_ingredients(plan):
    ingredients = current_ingredients()
    rows = []
    for ingredient in ingredients:
        rows.append(
            f"""
            <div class="ingredient-row-card">
                <div class="food-art {tone_for(ingredient)}"></div>
                <div>
                    <strong>{esc(ingredient)}</strong>
                    <div class="confidence">Detected</div>
                </div>
                <a class="tap-link icon-button" href="{app_href("Ingredients", remove_ingredient=ingredient)}" target="_self">x</a>
            </div>
            """
        )
    empty = '<div class="muted">No ingredients yet. Add some below or scan your fridge.</div>' if not rows else ""
    st.html(
        phone_frame(
            f"""
        <div class="app-screen">
            <div class="top-row">
                <a class="tap-link icon-button" href="{app_href("Home")}" target="_self">&lt;</a>
                <div class="brand"><span class="leaf-mark"></span><span>Freshwise</span></div>
                <a class="tap-link icon-button" href="{app_href("Scan")}" target="_self">+</a>
            </div>
            <h1 class="title">Detected Ingredients</h1>
            <div class="muted">Confirm what Freshwise found before generating a recipe.</div>
            <div class="ingredient-list">{''.join(rows)}{empty}</div>
            <a class="tap-link cook-button" href="{app_href("Recipe", generate_recipe="1")}" target="_self">Generate Recipe</a>
        </div>
        """
        )
    )


def render_order_success(plan):
    order = st.session_state.get("last_order", {})
    total = float(order.get("subtotal", cart_subtotal(plan)[0])) + 1.99
    item_count = int(order.get("item_count", cart_subtotal(plan)[1]))
    st.html(
        phone_frame(
            f"""
        <div class="app-screen">
            <div class="top-row">
                <a class="tap-link icon-button" href="{app_href("Home")}" target="_self">&lt;</a>
                <div class="brand"><span class="leaf-mark"></span><span>Freshwise</span></div>
                <div></div>
            </div>
            <div class="success-burst">✓</div>
            <div class="success-card">
                <h1 class="cart-title">Order placed</h1>
                <div class="muted">Mock checkout complete for the Streamlit mobile demo.</div>
                <div class="total-box">
                    <div class="total-row"><span>Items</span><span>{item_count}</span></div>
                    <div class="total-row big"><span>Total</span><span>{money(total)}</span></div>
                </div>
                <a class="tap-link cook-button" href="{app_href("Home")}" target="_self">Back Home</a>
            </div>
        </div>
        """
        )
    )


def render_scan_controls(runtime_config, business_goal):
    st.html(
        """
        <div class="action-panel">
            <h3>Camera / Manual Input</h3>
            <p>On mobile, the camera field opens the device camera. Vision recognition is next; manual input remains the reliable MVP path.</p>
        </div>
        """
    )
    fridge_photo = st.camera_input(
        "Take a fridge photo",
        key="fridge_photo",
        help="On Streamlit Cloud mobile, this opens the phone camera or photo picker.",
    )
    if fridge_photo is not None:
        if st.session_state.get("recognized_photo_id") != fridge_photo.file_id:
            with st.spinner("Freshwise is recognizing ingredients with the multimodal model..."):
                ingredients = recognize_photo_into_ingredients(runtime_config, fridge_photo.getvalue())
            st.session_state["recognized_photo_id"] = fridge_photo.file_id
            if ingredients:
                st.session_state["ingredient_input"] = ", ".join(ingredients)
                st.session_state["screen_picker"] = "Ingredients"
                st.rerun()
        st.info(st.session_state.get("generation_notice", "Photo captured. Confirm ingredients below."))

    owned_ingredients = st.text_area(
        "Ingredients",
        key="ingredient_input",
        label_visibility="collapsed",
        placeholder="tomatoes, spinach, eggs, cheese",
    )
    col1, col2 = st.columns(2)
    with col1:
        generate = st.button("Generate Plan", type="primary", use_container_width=True)
    with col2:
        demo = st.button("Use Demo", use_container_width=True)

    if demo:
        st.session_state["ingredient_input"] = SAMPLE_INGREDIENTS
        ingredients = parse_ingredients(SAMPLE_INGREDIENTS)
        st.session_state["detected_ingredients"] = ingredients
        generate_recipe_from_current_ingredients(runtime_config, business_goal)
        st.session_state["screen_picker"] = "Ingredients"
        st.rerun()

    if generate:
        ingredients = parse_ingredients(owned_ingredients)
        if not ingredients:
            st.warning("Add at least one ingredient first.")
        else:
            st.session_state["detected_ingredients"] = ingredients
            with st.spinner("Freshwise is building a meal and cart with the multimodal model..."):
                generate_recipe_from_current_ingredients(runtime_config, business_goal)
            st.session_state["screen_picker"] = "Recipe"
            st.rerun()


def render_home_controls():
    col1, col2 = st.columns(2)
    if col1.button("Scan / Input", type="primary", use_container_width=True):
        st.session_state["screen_picker"] = "Scan"
        st.rerun()
    if col2.button("View Recipe", use_container_width=True):
        st.session_state["screen_picker"] = "Recipe"
        st.rerun()


def render_recipe_controls(runtime_config, business_goal):
    col1, col2 = st.columns(2)
    if col1.button("Cook Steps", type="primary", use_container_width=True):
        st.session_state["screen_picker"] = "Recipe"
        st.info("Recipe steps are shown above. Timer mode is reserved for the PWA version.")
    if col2.button("Missing Items", use_container_width=True):
        st.session_state["screen_picker"] = "Cart"
        st.rerun()

    if st.button("Regenerate Recipe", use_container_width=True):
        with st.spinner("Freshwise is generating a recipe with the multimodal model..."):
            generate_recipe_from_current_ingredients(runtime_config, business_goal)
        st.session_state["screen_picker"] = "Recipe"
        st.rerun()


def render_ingredients_controls(runtime_config, business_goal):
    st.html(
        """
        <div class="action-panel">
            <h3>Ingredient Editor</h3>
            <p>Add an item manually, then regenerate the meal plan from the confirmed ingredients.</p>
        </div>
        """
    )
    new_item = st.text_input("Add ingredient", key="new_ingredient", label_visibility="collapsed", placeholder="Add ingredient")
    col1, col2 = st.columns(2)
    if col1.button("Add Item", use_container_width=True):
        item = new_item.strip().title()
        if item:
            ingredients = current_ingredients()
            if item not in ingredients:
                ingredients.append(item)
            st.session_state["detected_ingredients"] = ingredients
            st.session_state["last_plan"] = local_plan_from_ingredients(ingredients)
            st.rerun()
    if col2.button("Generate Recipe", type="primary", use_container_width=True):
        with st.spinner("Freshwise is building a meal and cart with the multimodal model..."):
            generate_recipe_from_current_ingredients(runtime_config, business_goal)
        st.session_state["screen_picker"] = "Recipe"
        st.rerun()


def render_cart_controls(plan):
    st.html(
        """
        <div class="action-panel">
            <h3>Cart Controls</h3>
            <p>These controls update the prototype cart state and recalculate the in-app total.</p>
        </div>
        """
    )
    for product in plan["recommended_products"]:
        name = product.get("name", "Ingredient")
        qty = int(st.session_state["cart_quantities"].get(name, 1))
        label_col, minus_col, qty_col, plus_col = st.columns([2.4, .8, .7, .8])
        label_col.write(f"**{name}**")
        if minus_col.button("-", key=f"minus_{name}", use_container_width=True, disabled=qty <= 0):
            st.session_state["cart_quantities"][name] = max(0, qty - 1)
            st.rerun()
        qty_col.write(str(qty))
        if plus_col.button("+", key=f"plus_{name}", use_container_width=True):
            st.session_state["cart_quantities"][name] = qty + 1
            st.rerun()

    col1, col2 = st.columns(2)
    if col1.button("Clear Cart", use_container_width=True):
        for name in st.session_state["cart_quantities"]:
            st.session_state["cart_quantities"][name] = 0
        st.rerun()
    if col2.button("Reset Qty", use_container_width=True):
        for name in st.session_state["cart_quantities"]:
            st.session_state["cart_quantities"][name] = 1
        st.rerun()


inject_theme()
runtime_config = read_runtime_config()
st.session_state["runtime_config"] = runtime_config

if "last_plan" not in st.session_state:
    st.session_state["last_plan"] = FALLBACK_PLAN
if "ingredient_input" not in st.session_state:
    st.session_state["ingredient_input"] = SAMPLE_INGREDIENTS
if "detected_ingredients" not in st.session_state:
    st.session_state["detected_ingredients"] = list(FALLBACK_PLAN["owned_ingredients"])
if "new_ingredient" not in st.session_state:
    st.session_state["new_ingredient"] = ""
if "business_goal" not in st.session_state:
    st.session_state["business_goal"] = BUSINESS_GOALS[0]

handle_query_actions()

with st.sidebar:
    st.title("Freshwise Settings")
    if runtime_config["ready"]:
        st.success("AI model connected")
        st.text_input("Model", value=runtime_config["model"], disabled=True)
    else:
        st.warning(runtime_config["error"])
    business_goal = st.selectbox("Retail goal", BUSINESS_GOALS)
st.session_state["business_goal"] = business_goal

plan = normalize_plan(st.session_state["last_plan"])
sync_cart(plan)
nav_options = ["Home", "Ingredients", "Recipe", "Cart", "Scan"]
screen = st.session_state.get("screen_picker", "Home")

if screen == "Home":
    render_home(plan)
elif screen == "Ingredients":
    render_ingredients(plan)
elif screen == "Recipe":
    render_recipe(plan)
elif screen == "Cart":
    render_cart(plan)
elif screen == "OrderSuccess":
    render_order_success(plan)
else:
    render_scan(plan, runtime_config, business_goal)

if screen == "Scan":
    render_scan_controls(runtime_config, business_goal)
elif screen == "Home":
    render_home_controls()
elif screen == "Recipe":
    render_recipe_controls(runtime_config, business_goal)
elif screen == "Ingredients":
    render_ingredients_controls(runtime_config, business_goal)
elif screen == "Cart":
    render_cart_controls(plan)

if st.session_state.get("future_notice"):
    st.info(st.session_state.pop("future_notice"))
if st.session_state.get("generation_notice"):
    st.info(st.session_state.pop("generation_notice"))

if screen in nav_options:
    selected_screen = st.radio(
        "App screen",
        nav_options,
        index=nav_options.index(screen),
        horizontal=True,
        label_visibility="collapsed",
    )
    if selected_screen != screen:
        st.session_state["screen_picker"] = selected_screen
        st.rerun()
