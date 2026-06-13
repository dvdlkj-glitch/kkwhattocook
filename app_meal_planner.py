# -*- coding: utf-8 -*-
"""
🌸 今天煮什麼？— 亞庇家庭買菜煮飯小幫手（YouTube 反向版）
首頁：官方市場行情月度報告 ｜ YouTube 找菜 ｜ 一週餐表 ｜ 採買清單 ｜ 花費總覽
- 找菜：YouTube 搜尋 → 卡片式結果 → Dashboard 內嵌播放（可全螢幕）→ 排入餐表
- 一週餐表：Supabase meal_plan，粉色日曆卡，🪄 一鍵生成
- 採買清單：YouTube 抽取食材自動加總 + 估價 + WhatsApp 分享
- 估價：以市場行情／海鮮價格做本機推估（標「估」）
"""
import os
import base64
import functools
import urllib.parse
import urllib.request
import tempfile
import datetime
import random
from collections import defaultdict
from datetime import date, timedelta

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from anthropic import Anthropic
from supabase import create_client

from recipes_data import (
    RECIPES, SEAFOOD_PRICES, MARKET_TIPS, ELDERLY_TIPS,
)
import recipe_to_ingredients as R
import meal_plan as MP

st.set_page_config(page_title="今天煮什麼？亞庇買菜煮飯小幫手",
                   page_icon="🌸", layout="wide")

DAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
DAY_EMOJIS = ["🌷", "🌼", "🌺", "🌻", "🌹", "🌸", "💐"]
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")


# ---------------------------------------------------------------- 連線
@st.cache_resource
def _get_clients():
    claude = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    return claude, sb

try:
    claude, supabase = _get_clients()
    YT_KEY = st.secrets["YOUTUBE_API_KEY"]
    CLIENTS_OK = True
except Exception:
    claude = supabase = YT_KEY = None
    CLIENTS_OK = False


# ---------------------------------------------------------------- 主題 CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Plus+Jakarta+Sans:wght@600;800&display=swap');

:root{
  --pink-1:#C2698A; --pink-2:#A8546F; --pink-3:#9C4D68;
  --rose:#B4456A; --plum:#8E4560; --gold:#F4D9A6;
  --bg-1:#FDF4F6; --bg-2:#FBEFF2; --bg-3:#F7E8EE;
  --card:rgba(255,255,255,.72); --line:rgba(180,90,120,.18);
  --shadow:0 8px 28px rgba(180,90,120,.14);
}
*{ -webkit-tap-highlight-color:transparent; }
html, body, [class*="css"]{ font-family:'Noto Sans TC','Plus Jakarta Sans',sans-serif; }
.stApp{
  background:
    radial-gradient(1200px 600px at 80% -10%, #FDE7EE 0%, transparent 60%),
    linear-gradient(180deg,var(--bg-1) 0%,var(--bg-2) 45%,var(--bg-3) 100%);
  background-attachment:fixed;
}
.block-container{ max-width:1180px; padding-top:1rem; }

@keyframes floatUp{ from{opacity:0; transform:translateY(14px)} to{opacity:1; transform:none} }
@keyframes shimmer{ 0%{background-position:0% 50%} 100%{background-position:200% 50%} }

.hero{
  background:linear-gradient(120deg,var(--pink-1),var(--pink-3),var(--pink-2));
  background-size:200% 200%; animation:shimmer 14s ease infinite alternate;
  border-radius:26px; padding:24px 28px; color:#FFF8F9;
  box-shadow:0 18px 40px rgba(156,77,104,.32); position:relative; overflow:hidden;
}
.hero::after{ content:''; position:absolute; inset:0;
  background:radial-gradient(420px 220px at 90% 0%, rgba(255,255,255,.22), transparent 70%); }
.hero h1{ margin:0; font-size:1.7rem; font-weight:900; letter-spacing:.5px; }
.hero p{ margin:8px 0 0; font-size:.9rem; opacity:.95; line-height:1.6; }
.hero .gold{ color:var(--gold); font-weight:800; }

.card,.day-card,.pkg-card,.stat,
div[data-testid="stVerticalBlockBorderWrapper"]{
  background:var(--card); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
  border:1px solid var(--line)!important; border-radius:20px;
  box-shadow:var(--shadow); animation:floatUp .5s ease both;
}
.card{ padding:16px 18px; margin-bottom:14px; }
.pkg-card{ padding:10px 10px 8px; text-align:center;
  transition:transform .18s ease, box-shadow .18s ease; }
.pkg-card:hover{ transform:translateY(-4px); box-shadow:0 16px 34px rgba(180,90,120,.22); }
.day-card{ padding:12px; margin-bottom:8px; }

.section-title{ font-size:1.18rem; font-weight:900; color:var(--plum);
  margin:8px 0 12px; display:flex; align-items:center; gap:8px; }
.section-title::before{ content:''; width:6px; height:20px; border-radius:6px;
  background:linear-gradient(var(--pink-1),var(--pink-2)); display:inline-block; }

.meal-name,.dish-mini{ color:#6E3B4E; font-weight:700; line-height:1.4; }
.dish-mini{ font-size:.84rem; min-height:2.3em; margin-top:4px; }
.pkg-title{ font-weight:800; color:var(--plum); margin-top:8px; font-size:.92rem;
  line-height:1.35; min-height:2.4em; }
.pkg-desc{ font-size:.74rem; color:#A0728B; margin-top:2px; }
.yt-thumb{ width:100%; height:128px; object-fit:cover; border-radius:14px; display:block;
  box-shadow:0 6px 16px rgba(180,90,120,.16); }

.cost-badge{ display:inline-block; background:linear-gradient(120deg,#FBE9EE,#FCE0EA);
  color:var(--rose); font-weight:800; font-size:.84rem; border-radius:10px;
  padding:4px 11px; margin-top:7px; }
.day-head{ display:flex; justify-content:space-between; align-items:center;
  font-weight:900; color:var(--plum); font-size:1rem; margin-bottom:8px; }
.day-cost{ background:#FBE9EE; color:var(--rose); font-size:.74rem; font-weight:800;
  border-radius:999px; padding:2px 10px; }
.slot-label{ font-size:.82rem; font-weight:800; color:var(--pink-2); margin:8px 0 2px; }
.warn-flag{ color:#C77; font-size:.72rem; }
.day-divider{ border-top:1.5px dashed var(--line); margin:10px 0 8px; }
.meal-tag{ display:inline-block; font-size:.72rem; font-weight:700; padding:2px 10px;
  border-radius:999px; margin-bottom:6px; }
.tag-lunch{ background:#FCEEDF; color:#A6731F; } .tag-dinner{ background:#EFE0F0; color:#7B4E86; }
.chip{ display:inline-block; background:#F7F0EA; color:#8A6A52; border-radius:999px;
  font-size:.72rem; padding:2px 9px; margin:2px; }
.note{ font-size:.78rem; color:#9A7C5B; background:#FDF7EC; border-left:3px solid #DDB877;
  border-radius:8px; padding:6px 10px; margin-top:8px; }
.emoji-hero{ font-size:2.4rem; text-align:center; background:#FBEFF2; border-radius:14px;
  padding:10px 0; margin-bottom:8px; }

.stats-row{ display:flex; flex-wrap:wrap; gap:10px; margin:6px 0 12px; }
.stat{ flex:1 1 140px; text-align:center; padding:14px 8px; }
.stat .v{ font-size:1.3rem; font-weight:900; color:var(--rose); }
.stat .l{ font-size:.78rem; color:#A0728B; margin-top:2px; }

.stButton > button{ border-radius:14px; border:1.5px solid #E9C2CF;
  color:var(--plum); background:rgba(255,255,255,.7);
  backdrop-filter:blur(6px); font-weight:800; min-height:2.9rem;
  transition:transform .12s ease, box-shadow .18s ease, background .2s; }
.stButton > button:hover{ border-color:var(--rose); color:var(--rose);
  box-shadow:0 8px 18px rgba(180,90,120,.18); }
.stButton > button:active{ transform:scale(.97); }
div[data-testid="stButton"] > button[kind="primary"]{
  background:linear-gradient(120deg,var(--pink-1),var(--pink-2)); color:#fff; border:none;
  font-size:1.02rem; font-weight:900; box-shadow:0 10px 22px rgba(180,90,120,.34); }
div[data-testid="stButton"] > button[kind="primary"]:active{ transform:scale(.97); }
.stLinkButton > a{ border-radius:14px!important; min-height:2.9rem; font-weight:800!important; }

.stTabs [data-baseweb="tab-list"]{ gap:8px; overflow-x:auto; flex-wrap:nowrap;
  scrollbar-width:none; -webkit-overflow-scrolling:touch; padding:4px 0 10px; }
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar{ display:none; }
.stTabs [data-baseweb="tab"]{ background:rgba(255,255,255,.7); backdrop-filter:blur(6px);
  border-radius:999px; padding:8px 16px; border:1px solid var(--line);
  color:var(--plum); font-weight:800; white-space:nowrap; flex-shrink:0; }
.stTabs [aria-selected="true"]{ background:linear-gradient(120deg,var(--pink-1),var(--pink-2))!important;
  color:#fff!important; border:none!important; box-shadow:0 6px 16px rgba(180,90,120,.3); }

[data-testid="stDataFrame"]{ border-radius:16px; overflow:hidden; box-shadow:var(--shadow); }

/* ---------- 響應式（手機優先） ---------- */
@media (max-width:1024px){
  [data-testid="stHorizontalBlock"]{ flex-wrap:wrap!important; gap:.7rem!important; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
    flex:1 1 48%!important; min-width:48%!important; width:auto!important; }
}
@media (max-width:768px){
  .block-container{ padding:.8rem .7rem 3rem!important; }
  .hero h1{ font-size:1.45rem; } .hero p{ font-size:.82rem; }
  .yt-thumb{ height:150px; }
}
@media (max-width:560px){
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
    flex:1 1 100%!important; min-width:100%!important; }
  .hero{ padding:18px 18px; border-radius:20px; }
  .hero h1{ font-size:1.3rem; }
  .section-title{ font-size:1.06rem; }
  .stButton > button{ min-height:3rem; font-size:1rem; }
  .stat .v{ font-size:1.15rem; }
  .yt-thumb{ height:185px; }
}
@media (max-width:380px){
  .hero h1{ font-size:1.15rem; } .hero p{ font-size:.76rem; }
  .block-container{ padding:.6rem .5rem 3rem!important; }
}
footer{ visibility:hidden; }

.yt-wrap{ position:relative; border-radius:14px; overflow:hidden; height:140px;
  box-shadow:0 6px 16px rgba(180,90,120,.16); }
.yt-wrap .yt-thumb{ height:100%; box-shadow:none; border-radius:0; }
.yt-play{ position:absolute; inset:0; display:flex; align-items:center; justify-content:center;
  font-size:32px; color:#fff; background:rgba(156,77,104,.16); opacity:0; transition:opacity .2s; }
.yt-wrap:hover .yt-play{ opacity:1; background:rgba(156,77,104,.34); }
.yt-card-title{ font-weight:800; color:var(--plum); font-size:.9rem; line-height:1.35;
  margin-top:8px; height:2.45em; display:-webkit-box; -webkit-line-clamp:2;
  -webkit-box-orient:vertical; overflow:hidden; }
.yt-card-chan{ font-size:.74rem; color:#A0728B; margin:5px 0 2px; white-space:nowrap;
  overflow:hidden; text-overflow:ellipsis; }
@media (max-width:560px){ .yt-wrap{ height:190px; } }

.dish-mini{ height:2.3em; min-height:2.3em; display:-webkit-box; -webkit-line-clamp:2;
  -webkit-box-orient:vertical; overflow:hidden; }
.day-card .yt-thumb{ height:84px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- 估價（本機推估）
# 以「每道菜該食材的常見份量價」粗估，避開調味料；標示「估」。
PRICE_PORTIONS = [
    (("蝦", "明蝦", "白蝦", "草蝦"), 14),
    (("蟹", "螃蟹"), 18),
    (("牛",), 16),
    (("鴨",), 13),
    (("豬", "排骨", "五花"), 11),
    (("魚", "馬鮫", "甘望", "石斑", "紅鰽", "鱸", "鯧", "鯛"), 12),
    (("雞",), 9),
    (("香菇", "蘑菇", "金針菇", "杏鮑菇", "草菇", "菇"), 4),
    (("豆腐", "豆干", "豆包", "豆皮"), 3),
    (("蛋",), 2),
    (("番茄", "西紅柿"), 2),
    (("洋蔥",), 2),
    (("馬鈴薯", "土豆", "薯", "蘿蔔"), 2),
    (("青菜", "菜心", "白菜", "芥蘭", "空心菜", "菠菜", "花椰", "西蘭花",
      "高麗", "包菜", "生菜", "莧菜", "油菜", "青江", "豆芽", "長豆"), 3),
    (("麵", "河粉", "米粉", "烏冬", "粄條", "板麵"), 3),
    (("米", "飯", "糯米"), 2),
    (("咖哩", "椰漿", "椰奶"), 3),
    (("辣椒", "紅椒", "青椒", "彩椒", "甜椒"), 2),
    (("蒜", "薑", "蔥", "香菜", "九層塔", "羅勒"), 1),
]
SEASONING_FREE = ("鹽", "糖", "油", "醬油", "胡椒", "醋", "味精", "料酒", "米酒",
                  "水", "太白粉", "澱粉", "蠔油", "魚露", "醬", "酒", "粉")


def estimate_dish_cost(ingredients):
    """回傳 (low, high, matched, counted) 或 None。"""
    total, matched, counted = 0.0, 0, 0
    for ing in ingredients or []:
        name = (ing.get("name_norm") or ing.get("name") or "")
        if any(s in name for s in SEASONING_FREE):
            continue
        counted += 1
        for kws, rm in PRICE_PORTIONS:
            if any(k in name for k in kws):
                total += rm
                matched += 1
                break
    if matched == 0:
        return None
    return int(round(total * 0.9)), int(round(total * 1.1)), matched, counted


def cost_badge(ingredients):
    est = estimate_dish_cost(ingredients)
    if not est:
        return "<span class='cost-badge'>💰 RM —</span>"
    lo, hi, _m, _c = est
    return f"<span class='cost-badge'>💰 估 RM {lo}–{hi}</span>"


def dish_mid_cost(ingredients):
    est = estimate_dish_cost(ingredients)
    if not est:
        return 0
    lo, hi, _m, _c = est
    return (lo + hi) / 2


# ---------------------------------------------------------------- 樂齡用：份量縮放
def people_factor(n):
    return {2: 0.8, 3: 1.0, 4: 1.15, 5: 1.35, 6: 1.5}.get(n, 1.0)

def scaled_cost(recipe, n):
    f = people_factor(n)
    return int(round(recipe["cost"][0] * f)), int(round(recipe["cost"][1] * f))


@functools.lru_cache(maxsize=64)
def _img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ---------------------------------------------------------------- 官方物價 PriceCatcher
PC_BASE = "https://storage.data.gov.my/pricecatcher"

OFFICIAL_ITEMS = [
    ("🐟 甘望魚 Ikan Kembung", ["IKAN KEMBUNG"]),
    ("🐠 馬鮫魚 Ikan Tenggiri", ["IKAN TENGGIRI"]),
    ("🦐 蝦 Udang", ["UDANG"]),
    ("🐡 紅鰽魚 / 石斑", ["IKAN MERAH", "KERAPU"]),
    ("🍗 雞肉 Ayam", ["AYAM STANDARD", "AYAM SUPER", "AYAM BERSIH"]),
    ("🥚 雞蛋 Telur", ["TELUR AYAM"]),
    ("🍅 番茄 Tomato", ["TOMATO"]),
    ("🧅 洋蔥 Bawang", ["BAWANG BESAR"]),
    ("🥬 菜心 / 小白菜 Sawi", ["SAWI"]),
    ("🌶️ 辣椒 Cili", ["CILI"]),
]

def _read_parquet_url(url):
    fn = os.path.join(tempfile.gettempdir(), os.path.basename(url))
    if not os.path.exists(fn):
        urllib.request.urlretrieve(url, fn)
    return pd.read_parquet(fn)

@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def fetch_official_mom():
    premise = _read_parquet_url(f"{PC_BASE}/lookup_premise.parquet")
    items = _read_parquet_url(f"{PC_BASE}/lookup_item.parquet")
    kk = set(premise.loc[
        premise["district"].astype(str).str.contains("Kota Kinabalu", case=False, na=False),
        "premise_code"])

    def prep(m):
        df = _read_parquet_url(f"{PC_BASE}/pricecatcher_{m}.parquet")
        df = df[df["premise_code"].isin(kk)]
        df = df[df["price"] > 0]
        df = df.merge(items[["item_code", "item", "unit"]], on="item_code", how="left")
        df["item"] = df["item"].astype(str).str.upper()
        return df

    today = datetime.date.today()
    first = today.replace(day=1)
    m_now = today.strftime("%Y-%m")
    m_prev = (first - datetime.timedelta(days=1)).strftime("%Y-%m")
    m_prev2 = ((first - datetime.timedelta(days=1)).replace(day=1)
               - datetime.timedelta(days=1)).strftime("%Y-%m")
    pair = None
    for cm, pm in ((m_now, m_prev), (m_prev, m_prev2)):
        try:
            pair = (cm, prep(cm), pm, prep(pm))
            break
        except Exception:
            continue
    if pair is None:
        raise RuntimeError("PriceCatcher 下載失敗")
    cm, cur, pm, prev = pair
    rows = []
    for label, kws in OFFICIAL_ITEMS:
        pat = "|".join(kws)
        c = cur[cur["item"].str.contains(pat, na=False)]
        p = prev[prev["item"].str.contains(pat, na=False)]
        if len(c) < 3 or len(p) < 3:
            continue
        mc, mp = float(c["price"].median()), float(p["price"].median())
        pct = (mc - mp) / mp * 100 if mp else 0.0
        arrow = "🔺" if pct > 0.5 else ("🔻" if pct < -0.5 else "➖")
        unit = c["unit"].mode().iloc[0] if len(c["unit"].mode()) else "-"
        rows.append({"品項": label,
                     f"上月 ({pm})": round(mp, 2),
                     f"本月 ({cm})": round(mc, 2),
                     "變化": f"{arrow} {pct:+.1f}%",
                     "單位": unit})
    return pd.DataFrame(rows), {"cur": cm, "prev": pm, "premises": int(len(kk))}


# ---------------------------------------------------------------- 找菜池（一鍵生成用）
LUNCH_NAMES = [r["name"] for r in RECIPES if "lunch" in r["meal"]]
DINNER_NAMES = [r["name"] for r in RECIPES if "dinner" in r["meal"]]

CUISINES = ["全部", "中式", "台式", "西式", "泰式", "馬來西亞", "印尼"]
CUISINE_KW = {"全部": "", "中式": "中式", "台式": "台式", "西式": "西式",
              "泰式": "泰式", "馬來西亞": "馬來西亞", "印尼": "印尼"}
CUISINE_POOLS = {
    "中式": ["麻婆豆腐", "番茄炒蛋", "宮保雞丁", "糖醋排骨", "清蒸魚", "蒜蓉青菜", "紅燒豆腐", "蔥爆牛肉"],
    "台式": ["滷肉飯", "三杯雞", "菜脯蛋", "客家小炒", "台式炒米粉", "麻油雞", "塔香茄子", "鹹蛋苦瓜"],
    "西式": ["奶油義大利麵", "香煎雞排", "烤時蔬", "蘑菇濃湯", "焗烤馬鈴薯", "凱薩沙拉", "番茄肉醬麵", "煎鮭魚"],
    "泰式": ["打拋豬", "泰式綠咖哩", "泰式炒河粉", "椒麻雞", "泰式青木瓜沙拉", "泰式炒空心菜", "泰式酸辣湯", "鳳梨炒飯"],
    "馬來西亞": ["椰漿飯", "咖哩雞", "炒粿條", "海南雞飯", "叻沙", "馬來風光", "黃薑飯", "參巴江魚仔"],
    "印尼": ["印尼炒飯", "仁當牛肉", "沙嗲雞", "巴東牛肉", "印尼炒麵", "加多加多", "薑黃飯", "參巴空心菜"],
}
CUISINE_POOLS["全部"] = [n for pool in CUISINE_POOLS.values() for n in pool]

SKIN_TRIGGERS = ["蝦", "蟹", "貝", "蛤", "蚌", "魷", "茄子", "筍", "辣", "花生", "芒果"]
SKIN_NOTE = ("💧 皮膚敏感模式：含蝦、蟹、貝、魷、茄子、竹筍、辣等常見發物的菜會標 ⚠。"
             "此為飲食參考，若有確診過敏請以醫生囑咐為準。")

def name_has_trigger(name):
    return any(t in (name or "") for t in SKIN_TRIGGERS)

def ingredients_have_trigger(ingredients):
    for ing in ingredients or []:
        nm = (ing.get("name_norm") or ing.get("name") or "")
        if any(t in nm for t in SKIN_TRIGGERS):
            return True
    return False

def scaled_cost_badge(ingredients, people):
    est = estimate_dish_cost(ingredients)
    if not est:
        return "<span class='cost-badge'>💰 RM —</span>"
    lo, hi, _m, _c = est
    f = people_factor(people)
    return f"<span class='cost-badge'>💰 估 RM {int(round(lo * f))}–{int(round(hi * f))}</span>"



# ---------------------------------------------------------------- 頁首
HERO_HTML = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
 html,body{margin:0;height:100%;overflow:hidden;font-family:'Noto Sans TC',sans-serif;}
 #wrap{position:relative;width:100%;height:200px;border-radius:24px;overflow:hidden;
   background:linear-gradient(120deg,#C2698A,#9C4D68 55%,#A8546F);}
 #c{position:absolute;inset:0;}
 #txt{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;
   padding:0 26px;color:#FFF8F9;z-index:2;}
 #txt h1{margin:0;font-size:30px;font-weight:900;letter-spacing:1px;opacity:0;}
 #txt p{margin:8px 0 0;font-size:14px;opacity:0;line-height:1.5;}
 .gold{color:#F4D9A6;font-weight:800;}
 .badge{display:inline-block;margin-top:10px;background:rgba(255,248,249,.18);
   border:1px solid rgba(244,217,166,.55);color:#F4D9A6;font-size:12px;font-weight:700;
   border-radius:999px;padding:4px 14px;opacity:0;width:fit-content;}
 @media(max-width:560px){#txt h1{font-size:23px}#txt p{font-size:12px}}
</style></head><body>
<div id="wrap"><canvas id="c"></canvas>
 <div id="txt">
  <h1 id="t1">🌸 今天煮什麼？</h1>
  <p id="t2">亞庇家庭買菜煮飯小幫手 · <span class="gold">麗都 &amp; 生源市場</span> · YouTube 找菜・一鍵排餐 💕</p>
  <span class="badge" id="t3">✦ David Lau Cooking Market Project</span>
 </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script>
(function(){
 var wrap=document.getElementById('wrap');
 var W=wrap.clientWidth,H=wrap.clientHeight;
 var renderer=new THREE.WebGLRenderer({canvas:document.getElementById('c'),alpha:true,antialias:true});
 renderer.setSize(W,H);renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
 var scene=new THREE.Scene();
 var camera=new THREE.PerspectiveCamera(60,W/H,0.1,100);camera.position.z=18;
 var cv=document.createElement('canvas');cv.width=cv.height=64;var ctx=cv.getContext('2d');
 var g=ctx.createRadialGradient(32,32,0,32,32,32);
 g.addColorStop(0,'rgba(255,255,255,0.95)');g.addColorStop(0.4,'rgba(255,225,235,0.7)');
 g.addColorStop(1,'rgba(255,200,220,0)');ctx.fillStyle=g;ctx.fillRect(0,0,64,64);
 var tex=new THREE.CanvasTexture(cv);
 var N=70,pos=new Float32Array(N*3),spd=[];
 for(var i=0;i<N;i++){pos[i*3]=(Math.random()-0.5)*44;pos[i*3+1]=(Math.random()-0.5)*26;pos[i*3+2]=(Math.random()-0.5)*10;
  spd.push({x:(Math.random()-0.5)*0.01,y:0.01+Math.random()*0.02});}
 var geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
 var mat=new THREE.PointsMaterial({size:1.7,map:tex,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,opacity:0.85});
 var pts=new THREE.Points(geo,mat);scene.add(pts);
 function animate(){requestAnimationFrame(animate);
  var a=geo.attributes.position.array;
  for(var i=0;i<N;i++){a[i*3]+=spd[i].x;a[i*3+1]+=spd[i].y;if(a[i*3+1]>14){a[i*3+1]=-14;a[i*3]=(Math.random()-0.5)*44;}}
  geo.attributes.position.needsUpdate=true;pts.rotation.z+=0.0004;renderer.render(scene,camera);}
 animate();
 window.addEventListener('resize',function(){W=wrap.clientWidth;H=wrap.clientHeight;renderer.setSize(W,H);camera.aspect=W/H;camera.updateProjectionMatrix();});
 if(window.gsap){gsap.to('#t1',{opacity:1,y:0,duration:0.8,ease:'power3.out',startAt:{y:18}});
  gsap.to('#t2',{opacity:1,duration:0.8,delay:0.25});gsap.to('#t3',{opacity:1,duration:0.8,delay:0.5});}
 else{document.getElementById('t1').style.opacity=1;document.getElementById('t2').style.opacity=1;document.getElementById('t3').style.opacity=1;}
})();
</script></body></html>"""
components.html(HERO_HTML, height=215)

if not CLIENTS_OK:
    st.error("⚠️ 找不到 API 金鑰（ANTHROPIC / SUPABASE / YOUTUBE）。"
             "市場行情與樂齡專區仍可使用，但「找菜／餐表／採買清單」需要設定 Secrets。")

tab_market, tab_find, tab_week, tab_shop, tab_budget, tab_elderly, tab_tips = st.tabs(
    ["📊 市場行情", "🔍 找菜", "📅 一週餐表", "🛒 採買清單",
     "💰 花費總覽", "👵 樂齡專區", "💡 小貼士"])


# ================ 📊 市場行情 ================
with tab_market:
    st.markdown("<div class='section-title'>📊 亞庇官方物價月報（上月 vs 本月）</div>",
                unsafe_allow_html=True)
    try:
        with st.spinner("正在載入官方數據（首次約 20–60 秒，之後全站共用快取）…"):
            otable, ometa = fetch_official_mom()
        if len(otable):
            ups = int(otable["變化"].str.startswith("🔺").sum())
            downs = int(otable["變化"].str.startswith("🔻").sum())
            flat = len(otable) - ups - downs
            st.markdown(f"""
            <div class='stats-row'>
              <div class='stat'><div class='v'>🔺 {ups} 項</div><div class='l'>本月變貴</div></div>
              <div class='stat'><div class='v'>🔻 {downs} 項</div><div class='l'>本月變便宜</div></div>
              <div class='stat'><div class='v'>➖ {flat} 項</div><div class='l'>大致持平</div></div>
              <div class='stat'><div class='v'>{ometa['premises']} 家</div><div class='l'>KK 採價店家</div></div>
            </div>""", unsafe_allow_html=True)
            st.dataframe(otable, use_container_width=True, hide_index=True)
            st.caption(
                f"資料來源：PriceCatcher（馬來西亞 KPDN + DOSM，data.gov.my，CC BY 4.0）｜"
                f"比較月份 {ometa['prev']} → {ometa['cur']}，取 Kota Kinabalu 店家當月中位價。"
                f"官方採價以超市與零售店為主，濕市場價格可能略有差異，僅供參考。")
        else:
            st.info("官方數據已下載，但本期抓不到亞庇的相關品項，請過幾天再看。")
    except Exception:
        st.warning("📡 官方月度數據暫時無法載入（來源網站忙碌），請稍後重新整理頁面。"
                   "下方為麗都市場參考行情。")

    st.markdown("<div class='section-title'>🐟 麗都市場海鮮參考行情（RM / 公斤）</div>",
                unsafe_allow_html=True)
    _mkt = [("market_tenggiri.jpg", "馬鮫魚 Ikan Tenggiri"),
            ("market_kembung.jpg", "甘望魚 Ikan Kembung"),
            ("market_udang.jpg", "本地白蝦 Udang"),
            ("market_merah.jpg", "紅鰽魚 / 石斑")]
    if any(os.path.exists(os.path.join(IMG_DIR, f)) for f, _ in _mkt):
        mcols = st.columns(4)
        for col, (fn, cap) in zip(mcols, _mkt):
            p = os.path.join(IMG_DIR, fn)
            if os.path.exists(p):
                col.image(p, caption=cap, use_container_width=True)
    sf = pd.DataFrame([{"海鮮": f"{e} {zh}", "馬來名稱": my,
                        "價格 (RM/kg)": f"RM {a} – {b}", "特點 / 料理方式": note}
                       for zh, my, e, a, b, note in SEAFOOD_PRICES])
    st.dataframe(sf, use_container_width=True, hide_index=True)
    st.markdown("<div class='card'><b style='color:#8E4560'>🧺 買海鮮小貼士</b><br>" +
                "<br>".join(MARKET_TIPS[:5]) + "</div>", unsafe_allow_html=True)


# ================ 🔍 找菜（YouTube 搜尋 → 卡片 → 內嵌播放 → 排入餐表） ================
with tab_find:
    st.markdown("<div class='section-title'>🔍 想煮什麼？YouTube 上找，找到就排進餐表</div>",
                unsafe_allow_html=True)

    if not CLIENTS_OK:
        st.info("此功能需要 ANTHROPIC / SUPABASE / YOUTUBE 三把金鑰，請先到 Secrets 設定。")
    else:
        ss = st.session_state
        ss.setdefault("find_cards", [])
        ss.setdefault("play_vid", None)
        ss.setdefault("play_title", "")
        ss.setdefault("people", 4)
        ss.setdefault("skin", False)
        ss.setdefault("cuisine", "全部")

        with st.container(border=True):
            st.markdown("<b style='color:#8E4560'>⚙️ 用餐設定</b>", unsafe_allow_html=True)
            sc1, sc2 = st.columns([1.4, 1])
            with sc1:
                ss.people = st.slider("👨‍👩‍👧 用餐人數", 2, 6, ss.people, key="people_slider")
            with sc2:
                ss.skin = st.toggle("💧 皮膚敏感（標示發物）", value=ss.skin, key="skin_toggle")
            try:
                _cz = st.pills("🍽️ 料理大類", CUISINES, default=ss.cuisine, key="cuisine_pills")
                ss.cuisine = _cz or "全部"
            except Exception:
                ss.cuisine = st.radio("🍽️ 料理大類", CUISINES,
                                      index=CUISINES.index(ss.cuisine), horizontal=True,
                                      key="cuisine_radio")
            if ss.skin:
                st.caption(SKIN_NOTE)

        query = st.text_input("輸入菜名", placeholder="例：麻婆豆腐、咖哩雞、番茄炒蛋")
        if st.button("🔍 搜尋", key="find_search", type="primary"):
            if query.strip():
                kw = CUISINE_KW.get(ss.cuisine, "")
                full_q = (kw + " " + query.strip()).strip()
                with st.spinner("搜尋中…"):
                    try:
                        ss.find_cards = R.search_dishes(full_q, YT_KEY)
                        ss.play_vid = None
                    except Exception as e:
                        st.error(f"搜尋失敗：{e}")
                        ss.find_cards = []
            else:
                st.warning("先輸入菜名再搜尋喔 🌸")

        if ss.find_cards:
            cols = st.columns(3)
            for i, card in enumerate(ss.find_cards):
                with cols[i % 3]:
                    with st.container(border=True):
                        thumb = card.get("thumbnail_url")
                        if thumb:
                            visual = (f"<div class='yt-wrap'><img class='yt-thumb' src='{thumb}'/>"
                                      f"<span class='yt-play'>▶</span></div>")
                        else:
                            visual = "<div class='emoji-hero'>🍳</div>"
                        skin_flag = ""
                        if ss.skin and name_has_trigger(card["title"]):
                            skin_flag = "<span class='warn-flag'> ⚠發物</span>"
                        st.markdown(
                            f"{visual}"
                            f"<div class='yt-card-title'>{card['title']}{skin_flag}</div>"
                            f"<div class='yt-card-chan'>📺 {card['channel']}</div>",
                            unsafe_allow_html=True)
                        if st.button("▶️ 播放", key=f"play_{card['video_id']}",
                                     use_container_width=True):
                            ss.play_vid = card["video_id"]
                            ss.play_title = card["title"]
                        with st.popover("➕ 排入餐表", use_container_width=True):
                            d = st.date_input("排到哪一天", value=date.today(),
                                              key=f"d_{card['video_id']}")
                            sl = st.radio("時段", MP.SLOTS, horizontal=True,
                                          key=f"sl_{card['video_id']}")
                            if st.button("✅ 確認排入", key=f"cf_{card['video_id']}",
                                         use_container_width=True):
                                with st.spinner("抽取食材中…"):
                                    try:
                                        rec = R.get_or_build_recipe(
                                            card, yt_api_key=YT_KEY,
                                            anthropic_client=claude, supabase=supabase)
                                        MP.add_to_plan(supabase, d, sl, card["video_id"])
                                        warn = ""
                                        if ss.skin and ingredients_have_trigger(rec.get("ingredients")):
                                            warn = "（⚠ 含發物）"
                                        st.success(f"已排入 {d} {sl}：{rec['title'][:16]}{warn}")
                                    except Exception as e:
                                        st.error(f"排入失敗：{e}")

        st.markdown("<div id='find-player'></div>", unsafe_allow_html=True)
        if ss.play_vid:
            pc1, pc2 = st.columns([3, 1])
            with pc1:
                st.markdown(f"<div class='section-title'>▶️ 正在播放：{ss.play_title[:44]}</div>",
                            unsafe_allow_html=True)
            with pc2:
                if st.button("✕ 關閉影片", key="close_find_player", use_container_width=True):
                    ss.play_vid = None
                    st.rerun()
            st.video(f"https://www.youtube.com/watch?v={ss.play_vid}")
            st.caption("點播放器右下角可全螢幕。")

with tab_week:
    st.markdown("<div class='section-title'>📅 一週餐表</div>", unsafe_allow_html=True)

    if not CLIENTS_OK:
        st.info("此功能需要 Secrets 設定。")
    else:
        ss = st.session_state
        ss.setdefault("week_anchor", date.today())
        ss.setdefault("play_vid_week", None)
        ss.setdefault("play_title_week", "")
        ss.setdefault("scroll_to_player", False)
        ss.setdefault("people", 4)
        ss.setdefault("skin", False)
        ss.setdefault("cuisine", "全部")

        def render_dish(dish, day, slot):
            vid = dish["video_id"]
            thumb = dish.get("thumbnail_url")
            visual = (f"<img class='yt-thumb' src='{thumb}'/>" if thumb else "")
            flag = " <span class='warn-flag'>⚠</span>" if dish.get("inferred") else ""
            if ss.get("skin") and ingredients_have_trigger(dish.get("ingredients")):
                flag += " <span class='warn-flag'>⚠發物</span>"
            st.markdown(
                f"<div class='day-card'>{visual}"
                f"<div class='dish-mini'>{dish['title'][:40]}{flag}</div>"
                f"{scaled_cost_badge(dish.get('ingredients'), ss.get('people', 4))}</div>",
                unsafe_allow_html=True)
            if st.button("▶️ 播放", key=f"playw_{day}_{slot}_{vid}", use_container_width=True):
                ss.play_vid_week = vid
                ss.play_title_week = dish["title"]
                ss.scroll_to_player = True
                st.toast("▶️ 影片已在下方開始播放")
            with st.expander("🥬 食材"):
                if dish.get("inferred"):
                    st.caption("⚠ 由菜名推測，非影片實際食材，請核對")
                _ings = dish.get("ingredients") or []
                if _ings:
                    for _ing in _ings:
                        _q = _ing.get("qty")
                        _u = _ing.get("unit") or ""
                        _amt = "適量" if (_ing.get("is_fuzzy") or _q is None) else f"{_q:g} {_u}".strip()
                        st.markdown(f"- {_ing.get('name', '')} {_amt}")
                else:
                    st.caption("這支影片的描述沒有附食材清單。")
            if st.button("✕ 移除", key=f"rm_{day}_{slot}_{vid}", use_container_width=True):
                MP.remove_from_plan(supabase, day, slot, vid)
                st.rerun()

        with st.container(border=True):
            st.markdown("<b style='color:#8E4560'>🪄 一鍵生成：依你選的料理大類搜 YouTube 填滿餐表</b>",
                        unsafe_allow_html=True)
            st.caption(f"目前料理大類：{ss.get('cuisine', '全部')}　·　可在「🔍 找菜」分頁的設定卡更換")
            g1, g2 = st.columns([1, 1])
            with g1:
                gen_days = st.slider("要排幾天", 1, 7, 3, key="gen_days")
            with g2:
                gen_slots = st.multiselect("時段", MP.SLOTS, default=MP.SLOTS, key="gen_slots")
            st.caption(f"預估耗用 YouTube 額度約 {gen_days * max(1, len(gen_slots)) * 100} units"
                       f"（每道菜 100u，已抽取過的會走快取）。")
            gb1, gb2 = st.columns([1.4, 1])
            with gb1:
                go = st.button("🪄 一鍵生成本週餐表", key="gen_week", type="primary",
                               use_container_width=True)
            with gb2:
                if st.button("🗑️ 清空本週", key="clear_week", use_container_width=True):
                    ss._confirm_clear = True
            if go:
                if not gen_slots:
                    st.warning("至少選一個時段。")
                else:
                    pool = CUISINE_POOLS.get(ss.get("cuisine", "全部"), CUISINE_POOLS["全部"])
                    mon = MP.week_start(ss.week_anchor)
                    prog = st.progress(0.0, text="開始生成…")
                    jobs = [(d, s2) for d in range(gen_days) for s2 in gen_slots]
                    done = 0
                    fails = []
                    added = 0
                    for d, slot in jobs:
                        day = mon + timedelta(days=d)
                        name = random.choice(pool) if pool else "家常菜"
                        if ss.get("skin"):
                            tries = 0
                            while name_has_trigger(name) and tries < 6:
                                name = random.choice(pool)
                                tries += 1
                        prog.progress(done / len(jobs), text=f"搜尋：{name}")
                        try:
                            cards = R.search_dishes(name, YT_KEY, max_results=1)
                            if cards:
                                rec = R.get_or_build_recipe(cards[0], yt_api_key=YT_KEY,
                                                            anthropic_client=claude, supabase=supabase)
                                if ss.get("skin") and ingredients_have_trigger(rec.get("ingredients")):
                                    fails.append(f"{name}：含發物已略過")
                                else:
                                    MP.add_to_plan(supabase, day, slot, cards[0]["video_id"])
                                    added += 1
                        except Exception as e:
                            fails.append(f"{name}：{e}")
                        done += 1
                    prog.progress(1.0, text="完成！")
                    if added:
                        st.success(f"已加入 {added} 道，往下看餐表 👇")
                        st.balloons()
                    if fails:
                        st.warning("有 {} 道沒加成功（顯示前 5 個）：\n\n{}".format(len(fails), "\n".join(fails[:5])))

        if ss.get("_confirm_clear"):
            st.warning("確定要清空本週所有已排的菜嗎？此動作無法復原。")
            cc1, cc2 = st.columns(2)
            if cc1.button("✅ 確定清空", key="clear_yes", type="primary", use_container_width=True):
                MP.clear_week(supabase, ss.week_anchor)
                ss._confirm_clear = False
                ss.play_vid_week = None
                st.rerun()
            if cc2.button("取消", key="clear_no", use_container_width=True):
                ss._confirm_clear = False
                st.rerun()

        nav1, nav2, nav3 = st.columns([1, 2, 1])
        with nav1:
            if st.button("← 上一週", use_container_width=True):
                ss.week_anchor -= timedelta(days=7)
        with nav3:
            if st.button("下一週 →", use_container_width=True):
                ss.week_anchor += timedelta(days=7)
        mon = MP.week_start(ss.week_anchor)
        with nav2:
            st.markdown(f"<div style='text-align:center;font-weight:900;color:#8E4560'>"
                        f"{mon} ～ {mon + timedelta(days=6)}</div>", unsafe_allow_html=True)

        week_names = ["一", "二", "三", "四", "五", "六", "日"]
        view = st.radio("檢視方式", ["📆 單日", "🗓️ 整週"], horizontal=True, key="week_view")

        grid = {}
        try:
            grid = MP.get_week_plan(supabase, ss.week_anchor)
            if view == "📆 單日":
                day_labels = [f"週{week_names[i]}" for i in range(7)]
                default_i = (date.today() - mon).days
                default_i = default_i if 0 <= default_i <= 6 else 0
                sel = st.radio("選一天", day_labels, index=default_i, horizontal=True,
                               key="day_sel", label_visibility="collapsed")
                di = day_labels.index(sel)
                day = mon + timedelta(days=di)
                st.markdown(f"<div class='day-head'><span>{DAY_EMOJIS[di]} 週{week_names[di]}</span>"
                            f"<span class='day-cost'>{day.month}/{day.day}</span></div>",
                            unsafe_allow_html=True)
                for slot in MP.SLOTS:
                    st.markdown(f"<div class='slot-label'>{'🍱 午餐' if slot == '午' else '🌙 晚餐'}</div>",
                                unsafe_allow_html=True)
                    dishes = grid.get((str(day), slot), [])
                    if not dishes:
                        st.markdown("<div class='dish-mini' style='color:#C99AAD'>· 未排</div>",
                                    unsafe_allow_html=True)
                    for dish in dishes:
                        render_dish(dish, day, slot)
            else:
                day_cols = st.columns(7)
                for d in range(7):
                    day = mon + timedelta(days=d)
                    with day_cols[d]:
                        st.markdown(f"<div class='day-head'><span>{DAY_EMOJIS[d]} 週{week_names[d]}</span>"
                                    f"<span class='day-cost'>{day.month}/{day.day}</span></div>",
                                    unsafe_allow_html=True)
                        for slot in MP.SLOTS:
                            st.markdown(f"<div class='slot-label'>{'🍱 午餐' if slot == '午' else '🌙 晚餐'}</div>",
                                        unsafe_allow_html=True)
                            dishes = grid.get((str(day), slot), [])
                            if not dishes:
                                st.markdown("<div class='dish-mini' style='color:#C99AAD'>· 未排</div>",
                                            unsafe_allow_html=True)
                            for dish in dishes:
                                render_dish(dish, day, slot)
        except Exception as e:
            st.error(f"餐表載入錯誤：{e}")
        st.session_state["_grid_cache"] = grid

        st.markdown("<div id='player-anchor'></div>", unsafe_allow_html=True)
        if ss.get("play_vid_week"):
            pc1, pc2 = st.columns([3, 1])
            with pc1:
                st.markdown(f"<div class='section-title'>▶️ 正在播放：{ss.play_title_week[:44]}</div>",
                            unsafe_allow_html=True)
            with pc2:
                if st.button("✕ 關閉影片", key="close_week_player", use_container_width=True):
                    ss.play_vid_week = None
                    ss.scroll_to_player = False
                    st.rerun()
            st.video(f"https://www.youtube.com/watch?v={ss.play_vid_week}")
            st.caption("點播放器右下角可全螢幕。")
            if ss.get("scroll_to_player"):
                components.html(
                    "<script>try{var d=window.parent.document;"
                    "var t=d.getElementById('player-anchor');"
                    "if(t){t.scrollIntoView({behavior:'smooth',block:'center'});}}catch(e){}</script>",
                    height=0)
                ss.scroll_to_player = False

with tab_shop:
    st.markdown("<div class='section-title'>🛒 本週採買清單（YouTube 食材自動加總）</div>",
                unsafe_allow_html=True)
    if not CLIENTS_OK:
        st.info("此功能需要 Secrets 設定。")
    else:
        grid = st.session_state.get("_grid_cache")
        if grid is None:
            try:
                grid = MP.get_week_plan(supabase, st.session_state.get("week_anchor", date.today()))
            except Exception:
                grid = {}
        recipes = MP.collect_week_recipes(grid)
        if not recipes:
            st.info("本週還沒排菜，先去「📅 一週餐表」排幾道吧 🌸")
        else:
            try:
                shopping = R.build_shopping_list(recipes)
                total_lo = sum(estimate_dish_cost(r.get("ingredients"))[0]
                               for r in recipes if estimate_dish_cost(r.get("ingredients")))
                total_hi = sum(estimate_dish_cost(r.get("ingredients"))[1]
                               for r in recipes if estimate_dish_cost(r.get("ingredients")))
                st.markdown(f"<div class='card'>🧮 本週估計買菜費："
                            f"<b style='color:#B4456A'>估 RM {total_lo} – {total_hi}</b>"
                            f"（{len(recipes)} 餐，依市場行情粗估，未含米油鹽等常備品）</div>",
                            unsafe_allow_html=True)
                cat_emojis = {"蔬菜": "🥬", "肉類": "🍗", "海鮮": "🐟", "蛋豆製品": "🥚",
                              "調味料": "🧄", "乾貨雜貨": "🛍️", "其他": "🧺"}
                cols = st.columns(3)
                lines = ["🌸 本週採買清單", f"估計買菜費：RM {total_lo} – {total_hi}", ""]
                idx = 0
                for cat, items in shopping.items():
                    with cols[idx % 3]:
                        items_html = "".join(
                            f"<div style='padding:4px 0;border-bottom:1px dashed #F0D5DD;"
                            f"display:flex;justify-content:space-between'>"
                            f"<span>☐ {it['name']}</span>"
                            f"<b style='color:#B4456A'>{it['amount']}</b></div>"
                            for it in items)
                        st.markdown(f"<div class='card'><b style='color:#8E4560'>"
                                    f"{cat_emojis.get(cat, '🛍️')} {cat}</b><br>{items_html}</div>",
                                    unsafe_allow_html=True)
                    lines.append(f"【{cat}】")
                    lines += [f"  □ {it['name']}  {it['amount']}" for it in items]
                    lines.append("")
                    idx += 1
                lines += ["—" * 18] + MARKET_TIPS[:5]
                text = "\n".join(lines)
                dl1, dl2 = st.columns(2)
                with dl1:
                    st.download_button("⬇️ 下載採買清單（帶去市場）", text,
                                       file_name="本週採買清單.txt", use_container_width=True)
                with dl2:
                    _wa = text if len(text) <= 1500 else text[:1500] + "\n…"
                    st.link_button("💬 用 WhatsApp 分享清單",
                                   "https://wa.me/?text=" + urllib.parse.quote(_wa),
                                   use_container_width=True)
            except Exception as e:
                st.error(f"採買清單錯誤：{e}")


# ================ 💰 花費總覽 ================
with tab_budget:
    st.markdown("<div class='section-title'>💰 本週每日餐費估算（依市場行情粗估）</div>",
                unsafe_allow_html=True)
    if not CLIENTS_OK:
        st.info("此功能需要 Secrets 設定。")
    else:
        grid = st.session_state.get("_grid_cache")
        if grid is None:
            try:
                grid = MP.get_week_plan(supabase, st.session_state.get("week_anchor", date.today()))
            except Exception:
                grid = {}
        if not grid:
            st.info("本週還沒排菜。")
        else:
            mon = MP.week_start(st.session_state.get("week_anchor", date.today()))
            week_names = ["一", "二", "三", "四", "五", "六", "日"]
            rows = []
            for d in range(7):
                day = mon + timedelta(days=d)
                lunch = grid.get((str(day), "午"), [])
                dinner = grid.get((str(day), "晚"), [])
                lc = sum(dish_mid_cost(x.get("ingredients")) for x in lunch)
                dc = sum(dish_mid_cost(x.get("ingredients")) for x in dinner)
                rows.append({"星期": f"週{week_names[d]}",
                             "午餐": "、".join(x["title"][:10] for x in lunch) or "—",
                             "晚餐": "、".join(x["title"][:10] for x in dinner) or "—",
                             "當日估費": round(lc + dc)})
            df = pd.DataFrame(rows)
            b1, b2 = st.columns([1.3, 1])
            with b1:
                st.dataframe(df[["星期", "午餐", "晚餐", "當日估費"]],
                             use_container_width=True, hide_index=True)
            with b2:
                chart_df = df.set_index("星期")[["當日估費"]].rename(columns={"當日估費": "RM"})
                st.bar_chart(chart_df, color="#C2698A")
                wk = int(df["當日估費"].sum())
                avg = df["當日估費"].mean()
                st.markdown(f"<div class='card'>📌 本週估計合計約 <b style='color:#B4456A'>RM {wk}</b>，"
                            f"平均每天約 <b style='color:#B4456A'>RM {avg:.0f}</b>"
                            f"（粗估，未含米油鹽等常備品）</div>", unsafe_allow_html=True)


# ================ 👵 樂齡專區 ================
with tab_elderly:
    st.markdown("<div class='section-title'>👵 適合家有年長者的食譜</div>",
                unsafe_allow_html=True)
    n_eld = st.slider("👨‍👩‍👧 用餐人數", 2, 6, 4, key="elder_people")
    elder_recipes = [r for r in RECIPES if r.get("elderly_ok")]
    cols = st.columns(3)
    for idx, r in enumerate(elder_recipes):
        lo2, hi2 = scaled_cost(r, n_eld)
        with cols[idx % 3]:
            st.markdown(f"<div class='day-card'><div class='emoji-hero'>{r['emoji']}</div>"
                        f"<div class='meal-name'>{r['name']}</div>"
                        f"<span class='cost-badge'>💰 RM {lo2} – {hi2}</span>"
                        f"<div class='note'>👵 {r.get('elderly_note', '')}</div></div>",
                        unsafe_allow_html=True)
    st.markdown("<div class='card'><b style='color:#8E4560'>🤍 為長輩備餐的小提醒</b><br>" +
                "<br>".join(ELDERLY_TIPS) + "</div>", unsafe_allow_html=True)


# ================ 💡 小貼士 ================
with tab_tips:
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("<div class='card'><b style='color:#8E4560'>🧺 市場採買小貼士</b><br>" +
                    "<br>".join(MARKET_TIPS) + "</div>", unsafe_allow_html=True)
    with t2:
        st.markdown("""<div class='card'><b style='color:#8E4560'>🌸 使用小撇步</b><br>
        ① 「📊 市場行情」先看這個月什麼變便宜<br>
        ② 「🔍 找菜」輸入想煮的菜 → 卡片結果可直接播放、排進餐表<br>
        ③ 「📅 一週餐表」可手動排，或按 🪄 一鍵生成填滿一週<br>
        ④ 「🛒 採買清單」自動加總食材＋估價，可下載或 WhatsApp 分享<br>
        ⑤ 「💰 花費總覽」看本週每天大概要花多少
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class='card'><b style='color:#8E4560'>📍 之後可以擴充</b><br>
        ・更精準的估價（接 LLM 依亞庇市價估每道菜）<br>
        ・收藏「我家最愛」常用菜單<br>
        ・節慶菜單（農曆新年、中秋圍爐）
        </div>""", unsafe_allow_html=True)

st.markdown("<p style='text-align:center;color:#C99AAD;font-size:0.8rem;margin-top:18px'>"
            "🌸 今天煮什麼？ · 為亞庇的妳設計 · 估價為市場常見推算，實際以當日市價為準</p>",
            unsafe_allow_html=True)
