# -*- coding: utf-8 -*-
"""
今天煮什麼?  ·  What to cook today?
亞庇家庭晚餐規劃儀表板 — 全新「暖食」UI（Streamlit 版）

反向流程：選菜 → 抽食材 → 一週餐表 → 採買清單 + 花費；首頁可比較亞庇/吉隆坡/台北物價。
本檔已將全新 UI 設計落地為 Streamlit。功能維持不變；資料管線（YouTube / Claude / Supabase）
的接點以註解標出 —— 把對應呼叫接回去即可（見 § HOOKS）。

執行：  streamlit run app_meal_planner.py
"""

import os
import base64
import random
import urllib.parse

import streamlit as st

# ----------------------------------------------------------------------------
# § HOOKS — 既有後端（若存在則可接回；缺檔時用內建目錄，App 仍可獨立運作）
# ----------------------------------------------------------------------------
# from recipe_to_ingredients import get_or_build_by_name, build_shopping_list
# from meal_plan import add_to_plan, get_week_plan, collect_week_recipes
# from market_compare import fetch_compare
# from dishes_catalog import CUISINE_DISHES, all_dish_names

# ============================================================================
# 1. 頁面設定 + 主題 CSS（暖食風）
# ============================================================================
st.set_page_config(page_title="今天煮什麼?", page_icon="🍲", layout="wide",
                   initial_sidebar_state="collapsed")

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@500;700;900&family=Noto+Sans+TC:wght@400;500;700&display=swap');

:root{
  --bg:#f6efe4; --surface:#fffdf8; --ink:#2b211a; --muted:#9b8b76;
  --line:#ebe0cd; --clay:#c0492b; --herb:#5c7a4a; --gold:#e7b04a;
}
html, body, [class*="css"]{ font-family:'Noto Sans TC',system-ui,sans-serif; }
.stApp{
  background:var(--bg);
  background-image:radial-gradient(circle at 12% -5%, #f4e7d2 0%, transparent 40%),
                   radial-gradient(circle at 90% 0%, #f0e3cf 0%, transparent 35%);
  color:var(--ink);
}
#MainMenu, header[data-testid="stHeader"], footer{ visibility:hidden; height:0; }
.block-container{ padding-top:1.2rem; padding-bottom:4rem; max-width:1200px; }

/* serif headings */
.serif{ font-family:'Noto Serif TC',serif; }

/* brand */
.brand-wrap{ display:flex; align-items:center; gap:11px; }
.brand-mark{ width:36px;height:36px;border-radius:11px;background:var(--clay);color:#fff;
  display:grid;place-items:center;font-family:'Noto Serif TC',serif;font-weight:900;font-size:20px;}
.brand-title{ font-family:'Noto Serif TC',serif;font-weight:900;font-size:22px;line-height:1; }
.brand-sub{ font-size:11px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;margin-top:4px; }

/* hero */
.hero{ position:relative;border-radius:22px;overflow:hidden;border:1px solid var(--line);
  margin:6px 0 26px; min-height:300px; display:flex; align-items:center;
  background-size:cover; background-position:center; }
.hero-overlay{ position:absolute;inset:0;
  background:linear-gradient(100deg,rgba(43,33,26,.88) 0%,rgba(43,33,26,.55) 45%,rgba(43,33,26,.12) 100%); }
.hero-inner{ position:relative;padding:38px 34px;max-width:560px;color:#fff; }
.hero-tag{ display:inline-block;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.25);
  font-size:11px;letter-spacing:1.5px;text-transform:uppercase;padding:5px 12px;border-radius:999px;margin-bottom:16px; }
.hero h1{ font-family:'Noto Serif TC',serif;font-weight:900;font-size:34px;line-height:1.2;margin:0 0 12px; }
.hero p{ color:rgba(255,255,255,.82);font-size:15px;line-height:1.65;margin:0 0 20px; }
.hero-steps{ display:flex;gap:18px;flex-wrap:wrap; }
.hero-step{ display:flex;align-items:center;gap:10px;font-size:13px;font-weight:500; }
.hero-step .n{ width:30px;height:30px;border-radius:50%;background:#fff;color:var(--clay);
  display:grid;place-items:center;font-weight:900;font-family:'Noto Serif TC',serif; }
.hero-visits{ margin-top:20px;font-size:12px;color:rgba(255,255,255,.6); }

/* section heads */
.sec-title{ font-family:'Noto Serif TC',serif;font-weight:900;font-size:27px;margin:0; }
.sec-sub{ color:var(--muted);font-size:13px;margin:6px 0 0; }

/* dish card */
.dish-card{ background:var(--surface);border:1px solid var(--line);border-radius:18px;overflow:hidden;
  box-shadow:0 4px 18px rgba(120,90,50,.06); }
.dish-img{ height:150px;background:#f1e7d6;background-size:cover;background-position:center;position:relative; }
.tag-cat{ position:absolute;top:10px;left:10px;background:rgba(43,33,26,.78);color:#fff;
  font-size:11px;font-weight:600;padding:4px 9px;border-radius:999px; }
.tag-skin{ position:absolute;top:10px;right:10px;background:var(--gold);color:#3a2a14;
  font-size:10px;font-weight:700;padding:4px 8px;border-radius:999px; }
.dish-body{ padding:13px 15px 6px; }
.dish-name{ font-family:'Noto Serif TC',serif;font-weight:700;font-size:17px;line-height:1.2; }
.dish-sub{ font-size:12px;color:#a2917b;margin-top:3px; }
.dish-cost{ font-size:13px;font-weight:700;color:var(--clay);margin-top:10px; }

/* generic surface card */
.card{ background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:18px 20px; }
.tip-card{ background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--clay);
  border-radius:18px;padding:22px; }
.tip-title{ font-family:'Noto Serif TC',serif;font-weight:900;font-size:19px; }
.tip-sub{ font-size:12px;color:#b39a6e;letter-spacing:1px;text-transform:uppercase;margin:4px 0 12px; }
.tip-body{ font-size:14px;line-height:1.7;color:#5f5141; }

/* market table */
.mkt{ width:100%;border-collapse:collapse;background:var(--surface);
  border:1px solid var(--line);border-radius:18px;overflow:hidden; }
.mkt th{ background:#fbf5ea;color:var(--muted);font-size:11px;letter-spacing:1px;text-transform:uppercase;
  font-weight:700;text-align:right;padding:13px 18px;border-bottom:1px solid #f0e7d8; }
.mkt th:first-child{ text-align:left; }
.mkt td{ padding:14px 18px;border-bottom:1px solid #f4ecdd;text-align:right;font-size:14px;color:#7a6a55; }
.mkt td:first-child{ text-align:left; }
.mkt .nm{ font-family:'Noto Serif TC',serif;font-weight:700;font-size:15px;color:var(--ink); }
.mkt .kk{ font-weight:700;color:var(--ink); }
.pill-up{ background:#f7e3e0;color:var(--clay);font-size:12px;font-weight:700;padding:3px 8px;border-radius:999px; }
.pill-dn{ background:#e3eddc;color:var(--herb);font-size:12px;font-weight:700;padding:3px 8px;border-radius:999px; }

/* cost summary */
.cost-box{ background:var(--ink);color:#fff;border-radius:20px;padding:24px; }
.cost-total{ font-family:'Noto Serif TC',serif;font-weight:900;font-size:40px;margin:6px 0 2px; }
.bar{ height:6px;border-radius:999px;background:rgba(255,255,255,.12);overflow:hidden;margin-top:5px; }
.bar > div{ height:100%;background:linear-gradient(90deg,var(--gold),var(--clay));border-radius:999px; }

/* senior */
.sr-card{ background:var(--surface);border:1px solid var(--line);border-radius:22px;overflow:hidden;
  display:flex;align-items:center;gap:20px; }
.sr-img{ width:170px;height:140px;background-size:cover;background-position:center;flex:none; }
.sr-slot{ font-size:16px;color:var(--clay);font-weight:700;letter-spacing:2px; }
.sr-name{ font-family:'Noto Serif TC',serif;font-weight:900;font-size:30px;line-height:1.1;margin-top:6px; }
.sr-sub{ font-size:16px;color:#a2917b;margin-top:6px; }

/* plan cells */
.plan-day{ font-family:'Noto Serif TC',serif;font-weight:700;font-size:17px; }
.plan-day small{ display:block;font-size:11px;color:#a2917b;letter-spacing:1px;text-transform:uppercase;font-family:'Noto Sans TC'; }
.cell{ background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:9px;display:flex;gap:11px;align-items:center; }
.cell-img{ width:56px;height:56px;border-radius:11px;background-size:cover;background-position:center;flex:none; }
.cell-slot{ font-size:10px;color:#b39a6e;font-weight:700;letter-spacing:1px;text-transform:uppercase; }
.cell-name{ font-family:'Noto Serif TC',serif;font-weight:700;font-size:15px;line-height:1.15;margin-top:2px; }
.cell-cost{ font-size:12px;color:var(--clay);font-weight:700;margin-top:2px; }

/* buttons */
.stButton > button{ border-radius:999px;border:1px solid var(--line);font-weight:700;font-size:13px; }
div[data-testid="stButton"] button[kind="primary"]{ background:var(--ink);border-color:var(--ink);color:#fff; }
.stLinkButton > a{ border-radius:999px;font-weight:700;font-size:13px; }

/* nav radio as tabs */
div[role="radiogroup"]{ gap:6px; }
div[role="radiogroup"] label{ background:transparent;border-radius:13px;padding:8px 16px;margin:0;color:#6f5f4c; }
div[role="radiogroup"] label:has(input:checked){ background:var(--ink);color:#fff; }
div[role="radiogroup"] label > div:first-child{ display:none; }   /* hide the dot */
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ============================================================================
# 2. 資料（雙語）
# ============================================================================
DAYS = [("週一", "Mon"), ("週二", "Tue"), ("週三", "Wed"), ("週四", "Thu"),
        ("週五", "Fri"), ("週六", "Sat"), ("週日", "Sun")]
SLOTS = [("lunch", "午餐", "Lunch"), ("dinner", "晚餐", "Dinner")]
CATS = [("all", "全部", "All"), ("seafood", "海鮮", "Seafood"), ("chinese", "中式", "Chinese"),
        ("thai", "泰式", "Thai"), ("soup", "湯品", "Soup"), ("noodle", "麵食", "Noodle"),
        ("quick", "快手", "Quick")]

# id, 中文, English, 圖片, 類別, 估價(RM/4人), 發物, 食材[(中,英,量,單位,分組)]
DISHES = [
    ("asam_fish", "亞參魚", "Asam Fish", "asam_fish.jpg", "seafood", 18, True,
     [("馬鮫魚", "Mackerel", 1, "條", "meat"), ("番茄", "Tomato", 3, "顆", "veg"),
      ("洋蔥", "Onion", 1, "顆", "veg"), ("亞參膏", "Asam paste", 2, "匙", "pantry")]),
    ("mackerel_soup", "番茄馬鮫魚湯", "Mackerel Tomato Soup", "mackerel_soup.jpg", "soup", 14, False,
     [("馬鮫魚", "Mackerel", 1, "條", "meat"), ("番茄", "Tomato", 2, "顆", "veg"),
      ("豆腐", "Tofu", 1, "塊", "pantry"), ("薑", "Ginger", 1, "塊", "veg")]),
    ("curry_chicken", "咖哩雞", "Curry Chicken", "curry_chicken.jpg", "chinese", 16, False,
     [("雞腿", "Chicken thigh", 4, "塊", "meat"), ("馬鈴薯", "Potato", 2, "顆", "veg"),
      ("咖哩粉", "Curry powder", 3, "匙", "pantry"), ("椰漿", "Coconut milk", 200, "毫升", "pantry")]),
    ("green_curry", "綠咖哩雞", "Green Curry Chicken", "green_curry.jpg", "thai", 17, False,
     [("雞胸", "Chicken breast", 300, "克", "meat"), ("綠咖哩醬", "Green curry paste", 2, "匙", "pantry"),
      ("椰漿", "Coconut milk", 250, "毫升", "pantry"), ("茄子", "Eggplant", 1, "條", "veg")]),
    ("tom_yum", "冬蔭功湯", "Tom Yum Soup", "tom_yum.jpg", "thai", 16, True,
     [("鮮蝦", "Prawn", 8, "尾", "meat"), ("香茅", "Lemongrass", 2, "根", "veg"),
      ("辣椒", "Chili", 3, "根", "veg"), ("南薑", "Galangal", 1, "塊", "veg")]),
    ("pad_thai", "泰式炒河粉", "Pad Thai", "pad_thai.jpg", "thai", 14, True,
     [("河粉", "Rice noodle", 2, "包", "pantry"), ("鮮蝦", "Prawn", 6, "尾", "meat"),
      ("雞蛋", "Egg", 2, "顆", "pantry"), ("豆芽", "Bean sprout", 100, "克", "veg")]),
    ("pad_krapow", "打拋豬", "Pad Krapow", "pad_krapow.jpg", "thai", 13, False,
     [("豬絞肉", "Minced pork", 300, "克", "meat"), ("打拋葉", "Holy basil", 1, "把", "veg"),
      ("辣椒", "Chili", 4, "根", "veg"), ("雞蛋", "Egg", 2, "顆", "pantry")]),
    ("soy_chicken", "醬油雞", "Soy Sauce Chicken", "soy_chicken.jpg", "chinese", 15, False,
     [("雞腿", "Chicken thigh", 4, "塊", "meat"), ("醬油", "Soy sauce", 4, "匙", "pantry"),
      ("薑", "Ginger", 1, "塊", "veg"), ("青蔥", "Spring onion", 2, "根", "veg")]),
    ("steam_prawn", "蒜蓉蒸蝦", "Steamed Garlic Prawns", "steam_prawn.jpg", "seafood", 22, True,
     [("鮮蝦", "Prawn", 12, "尾", "meat"), ("蒜頭", "Garlic", 1, "球", "veg"),
      ("粉絲", "Glass noodle", 1, "包", "pantry"), ("青蔥", "Spring onion", 2, "根", "veg")]),
    ("herbal_soup", "藥材雞湯", "Herbal Chicken Soup", "herbal_soup.jpg", "soup", 20, False,
     [("雞", "Chicken", 1, "隻", "meat"), ("枸杞", "Goji berry", 2, "匙", "pantry"),
      ("紅棗", "Red date", 8, "顆", "pantry"), ("當歸", "Dang gui", 1, "片", "pantry")]),
    ("lotus_soup", "蓮藕排骨湯", "Lotus Root Pork Rib Soup", "lotus_soup.jpg", "soup", 18, False,
     [("排骨", "Pork rib", 500, "克", "meat"), ("蓮藕", "Lotus root", 1, "節", "veg"),
      ("紅棗", "Red date", 6, "顆", "pantry"), ("薑", "Ginger", 1, "塊", "veg")]),
    ("tomato_egg", "番茄炒蛋", "Tomato & Egg", "tomato_egg.jpg", "quick", 8, False,
     [("番茄", "Tomato", 3, "顆", "veg"), ("雞蛋", "Egg", 4, "顆", "pantry"),
      ("青蔥", "Spring onion", 1, "根", "veg")]),
    ("tomato_noodle", "番茄蛋麵", "Tomato Egg Noodles", "tomato_noodle.jpg", "noodle", 10, False,
     [("番茄", "Tomato", 2, "顆", "veg"), ("雞蛋", "Egg", 2, "顆", "pantry"),
      ("拉麵", "Ramen noodle", 2, "包", "pantry"), ("青菜", "Greens", 1, "把", "veg")]),
    ("pork_tofu", "豆腐燜肉", "Braised Pork & Tofu", "pork_tofu.jpg", "chinese", 12, False,
     [("五花肉", "Pork belly", 300, "克", "meat"), ("豆腐", "Tofu", 2, "塊", "pantry"),
      ("醬油", "Soy sauce", 3, "匙", "pantry"), ("蒜頭", "Garlic", 3, "瓣", "veg")]),
    ("sour_fish", "酸菜魚", "Sour Vegetable Fish", "sour_fish.jpg", "seafood", 19, True,
     [("草魚", "Grass carp", 1, "條", "meat"), ("酸菜", "Pickled greens", 150, "克", "veg"),
      ("辣椒", "Chili", 3, "根", "veg"), ("花椒", "Sichuan pepper", 1, "匙", "pantry")]),
    ("prawn_ramen", "鮮蝦拉麵", "Prawn Ramen", "prawn_ramen.jpg", "noodle", 16, True,
     [("鮮蝦", "Prawn", 8, "尾", "meat"), ("拉麵", "Ramen noodle", 2, "包", "pantry"),
      ("豆腐", "Tofu", 1, "塊", "pantry"), ("青菜", "Greens", 1, "把", "veg")]),
    ("chicken_ramen", "雞肉拉麵", "Chicken Ramen", "chicken_ramen.jpg", "noodle", 14, False,
     [("雞胸", "Chicken breast", 250, "克", "meat"), ("拉麵", "Ramen noodle", 2, "包", "pantry"),
      ("香菇", "Shiitake", 6, "朵", "veg"), ("青菜", "Greens", 1, "把", "veg")]),
    ("grouper", "清蒸石斑", "Steamed Grouper", "grouper.jpg", "seafood", 28, True,
     [("石斑魚", "Grouper", 1, "條", "meat"), ("薑", "Ginger", 1, "塊", "veg"),
      ("青蔥", "Spring onion", 3, "根", "veg"), ("醬油", "Soy sauce", 3, "匙", "pantry")]),
    ("coconut_soup", "椰汁咖哩雞", "Coconut Curry Chicken", "coconut_soup.jpg", "thai", 17, False,
     [("雞腿", "Chicken thigh", 4, "塊", "meat"), ("椰漿", "Coconut milk", 300, "毫升", "pantry"),
      ("咖哩葉", "Curry leaf", 1, "把", "veg"), ("青檸", "Lime", 2, "顆", "veg")]),
    ("weekend_feast", "週末海鮮餐", "Weekend Seafood Feast", "weekend_feast.jpg", "seafood", 35, True,
     [("鮮蝦", "Prawn", 12, "尾", "meat"), ("石斑魚", "Grouper", 1, "條", "meat"),
      ("青菜", "Greens", 2, "把", "veg"), ("冬瓜", "Winter melon", 1, "塊", "veg")]),
]
DISH_BY_ID = {d[0]: d for d in DISHES}

# 三地物價對比 (RM/kg)：中, 英, 亞庇, 吉隆坡, 台北, MoM%
MARKET = [
    ("番茄", "Tomato", 4.20, 4.80, 5.10, -3),
    ("洋蔥", "Onion", 3.60, 3.90, 4.40, 2),
    ("辣椒", "Chili", 9.50, 10.20, 12.00, 5),
    ("蒜頭", "Garlic", 11.00, 11.50, 9.80, -1),
    ("生薑", "Ginger", 8.00, 8.60, 7.50, 4),
]
SEAFOOD = [
    ("甘望魚", "Kembung", "market_kembung.jpg", 12),
    ("紅魚", "Red Snapper", "market_merah.jpg", 28),
    ("馬鮫魚", "Tenggiri", "market_tenggiri.jpg", 32),
    ("鮮蝦", "Prawns", "market_udang.jpg", 35),
]
TIPS = [
    ("鮮魚挑選", "Picking Fresh Fish", "魚眼清澈、魚鰓鮮紅、按壓魚身能迅速回彈，就是新鮮的好魚。",
     "Clear eyes, bright red gills and flesh that springs back means the fish is fresh."),
    ("控制預算", "Stay on Budget", "一週以一到兩道海鮮為主、其餘搭配雞肉與蔬菜，花費最均衡。",
     "Anchor the week with one or two seafood dishes; fill the rest with chicken and veg."),
    ("皮膚敏感", "Sensitive Skin", "開啟「皮膚敏感」會自動略過蝦蟹等易過敏食材。",
     "Turn on 'skin sensitive' to skip prawns, crab and other common allergens."),
    ("備料省時", "Prep Ahead", "週末把薑蒜辣椒切好分裝冷藏，平日下廚可省一半時間。",
     "Chop ginger, garlic and chili on the weekend to halve weekday cooking time."),
]

# ============================================================================
# 3. session state
# ============================================================================
ss = st.session_state
ss.setdefault("lang", "zh")
ss.setdefault("people", 4)
ss.setdefault("cat", "all")
ss.setdefault("skin", False)
ss.setdefault("plan", {})          # key "day-slot" -> dish id
ss.setdefault("tab", "discover")
ss.setdefault("senior_day", 0)
ss.setdefault("seed", 3)

# ============================================================================
# 4. helpers
# ============================================================================
def L(zh, en):
    return zh if ss.lang == "zh" else en

def fmt(n):
    n = round(n, 2)
    return "RM " + (str(int(n)) if n == int(n) else f"{n:.2f}")

def factor():
    return ss.people / 4

def cat_label(c):
    for x in CATS:
        if x[0] == c:
            return L(x[1], x[2])
    return c

# § HOOKS: 圖片可改由 Supabase thumbnail_url 提供；此處讀本機 images/
@st.cache_data(show_spinner=False)
def img_b64(name):
    here = os.path.dirname(os.path.abspath(__file__))
    for d in [os.path.join(here, "images"), os.path.join(here, "uploads", "images"),
              "images", "uploads/images"]:
        p = os.path.join(d, name)
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

def img_src(name):
    b = img_b64(name)
    return f"data:image/jpeg;base64,{b}" if b else ""

def eligible():
    out = []
    for d in DISHES:
        if ss.cat != "all" and d[4] != ss.cat:
            continue
        if ss.skin and d[6]:
            continue
        out.append(d)
    return out

def add_to_plan(dish_id):
    for day in range(7):
        for s in SLOTS:
            key = f"{day}-{s[0]}"
            if key not in ss.plan:
                ss.plan[key] = dish_id
                return
    # § HOOKS: 同步寫入 meal_plan.add_to_plan(plan_date, slot, video_id)

def remove_from_plan(key):
    ss.plan.pop(key, None)

def clear_week():
    ss.plan = {}

def auto_fill():
    used = set(ss.plan.values())
    pool = [d for d in DISHES if not (ss.skin and d[6])]
    random.Random(ss.seed).shuffle(pool)
    pi = 0
    for day in range(7):
        for s in SLOTS:
            key = f"{day}-{s[0]}"
            if key in ss.plan:
                continue
            guard = 0
            while guard < len(pool) and pool[pi % len(pool)][0] in used:
                pi += 1
                guard += 1
            pick = pool[pi % len(pool)]
            pi += 1
            ss.plan[key] = pick[0]
            used.add(pick[0])

def planned_dishes():
    return [DISH_BY_ID[i] for i in ss.plan.values() if i in DISH_BY_ID]

def shopping_groups():
    f = factor()
    agg = {}
    for d in planned_dishes():
        for (zh, en, qty, unit, grp) in d[7]:
            k = (zh, unit)
            if k not in agg:
                agg[k] = {"zh": zh, "en": en, "qty": 0, "unit": unit, "grp": grp}
            agg[k]["qty"] += qty * f
    order = [("veg", "蔬果", "Produce"), ("meat", "肉類海鮮", "Meat & Seafood"),
             ("pantry", "雜貨調味", "Pantry")]
    groups = []
    for g, zh, en in order:
        items = []
        for m in agg.values():
            if m["grp"] != g:
                continue
            q = round(m["qty"], 1)
            qs = str(int(q)) if q == int(q) else f"{q:.1f}"
            items.append({"name": L(m["zh"], m["en"]), "sub": m["en"] if ss.lang == "zh" else m["zh"],
                          "qty": f"{qs} {m['unit']}"})
        if items:
            groups.append({"label": L(zh, en), "items": items})
    return groups

def cost_data():
    f = factor()
    dishes = planned_dishes()
    total = sum(d[5] * f for d in dishes)
    by_cat = {}
    for d in dishes:
        by_cat[d[4]] = by_cat.get(d[4], 0) + d[5] * f
    rows = []
    for c, v in sorted(by_cat.items(), key=lambda x: -x[1]):
        rows.append({"label": cat_label(c), "value": fmt(v),
                     "pct": round(v / total * 100) if total else 0})
    return {"total": fmt(total), "rows": rows, "count": len(dishes),
            "per_meal": fmt(total / len(dishes)) if dishes else fmt(0)}

def youtube_url(d):
    q = (d[1] if ss.lang == "zh" else d[2]) + " " + L("做法 食譜", "recipe how to cook")
    return "https://www.youtube.com/results?search_query=" + urllib.parse.quote(q)
    # § HOOKS: 改用 get_or_build_by_name(name) 取得實際 video_id，嵌入 st.video / iframe

# ============================================================================
# 5. 頂部列：品牌 · 人數 · 語言
# ============================================================================
hl, hp, hg = st.columns([6, 3, 2])
with hl:
    st.markdown(
        '<div class="brand-wrap"><div class="brand-mark">煮</div>'
        '<div><div class="brand-title">今天煮什麼?</div>'
        '<div class="brand-sub">What to cook today · 亞庇 Kota Kinabalu</div></div></div>',
        unsafe_allow_html=True)
with hp:
    c1, c2, c3 = st.columns([1, 2, 1])
    c1.button("−", key="pm", on_click=lambda: ss.update(people=max(1, ss.people - 1)))
    c2.markdown(f"<div style='text-align:center;font-weight:700;padding-top:6px'>{ss.people} {L('人','ppl')}</div>",
                unsafe_allow_html=True)
    c3.button("＋", key="pp", on_click=lambda: ss.update(people=min(12, ss.people + 1)))
with hg:
    g1, g2 = st.columns(2)
    g1.button("中", key="lzh", type=("primary" if ss.lang == "zh" else "secondary"),
              on_click=lambda: ss.update(lang="zh"))
    g2.button("EN", key="len", type=("primary" if ss.lang == "en" else "secondary"),
              on_click=lambda: ss.update(lang="en"))

# ----- nav -----
NAV = [("discover", "探索", "Discover"), ("plan", "餐表", "Plan"), ("shop", "採買", "Shop"),
       ("market", "行情", "Market"), ("senior", "樂齡", "Senior"), ("tips", "小貼士", "Tips")]
nav_labels = [f"{L(z, e)}" for _, z, e in NAV]
nav_ids = [n[0] for n in NAV]
cur = ss.tab if ss.tab in nav_ids else "discover"
choice = st.radio("nav", nav_labels, index=nav_ids.index(cur),
                  horizontal=True, label_visibility="collapsed")
ss.tab = nav_ids[nav_labels.index(choice)]
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ============================================================================
# 6. 各分頁
# ============================================================================

def render_dish_card(d):
    skin_tag = f'<div class="tag-skin">{L("發物","trigger")}</div>' if d[6] else ""
    st.markdown(
        f'<div class="dish-card"><div class="dish-img" style="background-image:url({img_src(d[3])})">'
        f'<div class="tag-cat">{cat_label(d[4])}</div>{skin_tag}</div>'
        f'<div class="dish-body"><div class="dish-name">{L(d[1], d[2])}</div>'
        f'<div class="dish-sub">{d[2] if ss.lang == "zh" else d[1]}</div>'
        f'<div class="dish-cost">≈ {fmt(d[5])}</div></div></div>',
        unsafe_allow_html=True)
    a, b = st.columns(2)
    a.link_button("▶ " + L("看做法", "Watch"), youtube_url(d), use_container_width=True)
    b.button("＋ " + L("排入", "Add"), key="add_" + d[0], type="primary",
             use_container_width=True, on_click=add_to_plan, args=(d[0],))


def view_discover():
    # hero
    st.markdown(
        f'<div class="hero" style="background-image:url({img_src("weekend_feast.jpg")})">'
        f'<div class="hero-overlay"></div><div class="hero-inner">'
        f'<div class="hero-tag">{L("反向流程 · 選菜就好", "Reverse flow · just pick")}</div>'
        f'<h1>{L("先選想吃的菜，採買清單自動生成", "Pick what you crave — we build the shopping list")}</h1>'
        f'<p>{L("選菜 → 抽食材 → 一週餐表與花費。專為亞庇家庭晚餐而設，對比三地物價、貼心避開敏感食材。", "Choose dishes, extract ingredients, plan the week and track cost — built for Kota Kinabalu family dinners.")}</p>'
        f'<div class="hero-steps">'
        f'<div class="hero-step"><span class="n">1</span>{L("選菜", "Pick dishes")}</div>'
        f'<div class="hero-step"><span class="n">2</span>{L("抽食材", "Get ingredients")}</div>'
        f'<div class="hero-step"><span class="n">3</span>{L("採買 + 花費", "Shop + cost")}</div></div>'
        f'<div class="hero-visits">👀 {L("累計造訪 12,480 次 · 今日 96", "12,480 visits · 96 today")}</div>'
        f'</div></div>', unsafe_allow_html=True)

    t, r = st.columns([5, 2])
    t.markdown(f'<div class="sec-title serif">{L("今晚的推薦", "Tonight\u2019s picks")}</div>'
               f'<div class="sec-sub">{L("依用餐人數估價，一鍵排入餐表", "Priced for your party — add to the week in one tap")}</div>',
               unsafe_allow_html=True)
    with r:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        st.button("↻ " + L("換一批", "Shuffle"), use_container_width=True,
                  on_click=lambda: ss.update(seed=ss.seed + 7))

    # filters
    fcols = st.columns(len(CATS) + 1)
    for i, (cid, z, e) in enumerate(CATS):
        fcols[i].button(L(z, e), key="cat_" + cid,
                        type=("primary" if ss.cat == cid else "secondary"),
                        use_container_width=True, on_click=lambda c=cid: ss.update(cat=c))
    fcols[-1].toggle(L("皮膚敏感", "Skin sensitive"), key="skin")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    pool = eligible()[:]
    random.Random(ss.seed).shuffle(pool)
    pool = pool[:8]
    cols = st.columns(4)
    for i, d in enumerate(pool):
        with cols[i % 4]:
            render_dish_card(d)
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)


def view_plan():
    t, b = st.columns([5, 3])
    t.markdown(f'<div class="sec-title serif">{L("一週餐表", "Weekly Plan")}</div>'
               f'<div class="sec-sub">{L("午餐與晚餐 · 點空格新增，或一鍵生成", "Lunch & dinner — tap a slot or auto-fill the week")}</div>',
               unsafe_allow_html=True)
    with b:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        x, y = st.columns(2)
        x.button("✦ " + L("一鍵生成", "Auto-fill"), type="primary", use_container_width=True, on_click=auto_fill)
        y.button(L("清空", "Clear"), use_container_width=True, on_click=clear_week)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    for di, (dz, de) in enumerate(DAYS):
        c0, c1, c2 = st.columns([1, 3, 3])
        c0.markdown(f'<div class="plan-day">{dz}<small>{de}</small></div>', unsafe_allow_html=True)
        for col, s in zip([c1, c2], SLOTS):
            key = f"{di}-{s[0]}"
            with col:
                if key in ss.plan:
                    d = DISH_BY_ID[ss.plan[key]]
                    inner, btn = st.columns([6, 1])
                    inner.markdown(
                        f'<div class="cell"><div class="cell-img" style="background-image:url({img_src(d[3])})"></div>'
                        f'<div><div class="cell-slot">{L(s[1], s[2])}</div>'
                        f'<div class="cell-name">{L(d[1], d[2])}</div>'
                        f'<div class="cell-cost">{fmt(d[5])}</div></div></div>', unsafe_allow_html=True)
                    btn.button("✕", key="rm_" + key, on_click=remove_from_plan, args=(key,))
                else:
                    st.button("＋ " + L(s[1], s[2]), key="empty_" + key, use_container_width=True,
                              on_click=lambda: ss.update(tab="discover"))
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


def view_shop():
    st.markdown(f'<div class="sec-title serif">{L("採買清單", "Shopping List")}</div>'
                f'<div class="sec-sub">{L("依餐表自動聚合食材，並估算總花費", "Aggregated from your plan, with an estimated total")}</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    groups = shopping_groups()
    if not groups:
        st.markdown(f'<div class="card" style="text-align:center;color:#a2917b;padding:40px">'
                    f'{L("餐表還是空的，先去選幾道菜吧。", "Your week is empty — pick a few dishes first.")}</div>',
                    unsafe_allow_html=True)
        st.button(L("去選菜", "Pick dishes"), type="primary", on_click=lambda: ss.update(tab="discover"))
        return

    left, right = st.columns([5, 3])
    with left:
        for g in groups:
            rows = "".join(
                f'<div style="display:flex;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid #f4ecdd">'
                f'<span style="width:18px;height:18px;border-radius:5px;border:1.5px solid #d8cab2;flex:none"></span>'
                f'<div style="flex:1"><b>{it["name"]}</b>'
                f'<span style="font-size:12px;color:#b39a6e;margin-left:8px">{it["sub"]}</span></div>'
                f'<div style="font-weight:700;color:#7a5a3f">{it["qty"]}</div></div>'
                for it in g["items"])
            st.markdown(
                f'<div class="card" style="padding:0;margin-bottom:16px;overflow:hidden">'
                f'<div style="display:flex;justify-content:space-between;padding:14px 18px;background:#fbf5ea;'
                f'border-bottom:1px solid #f0e7d8"><b class="serif" style="font-size:16px">{g["label"]}</b>'
                f'<span style="font-size:12px;color:#a2917b">{len(g["items"])} {L("項","items")}</span></div>'
                f'<div style="padding:4px 18px 10px">{rows}</div></div>', unsafe_allow_html=True)
    with right:
        c = cost_data()
        note = L(f"{ss.people} 人份 · {c['count']} 餐", f"{c['count']} meals · for {ss.people}")
        bars = "".join(
            f'<div style="margin-bottom:13px"><div style="display:flex;justify-content:space-between;'
            f'font-size:13px;margin-bottom:5px"><span style="color:rgba(255,255,255,.85)">{r["label"]}</span>'
            f'<b>{r["value"]}</b></div><div class="bar"><div style="width:{r["pct"]}%"></div></div></div>'
            for r in c["rows"])
        st.markdown(
            f'<div class="cost-box"><div style="font-size:12px;letter-spacing:2px;text-transform:uppercase;'
            f'color:rgba(255,255,255,.55)">{L("預估總花費", "Estimated Total")}</div>'
            f'<div class="cost-total">{c["total"]}</div>'
            f'<div style="font-size:12px;color:rgba(255,255,255,.6);margin-bottom:18px">'
            f'{note}</div>'
            f'{bars}<div style="margin-top:16px;padding-top:14px;border-top:1px solid rgba(255,255,255,.14);'
            f'display:flex;justify-content:space-between;font-size:13px"><span style="color:rgba(255,255,255,.7)">'
            f'{L("每餐平均", "Avg / meal")}</span><b>{c["per_meal"]}</b></div></div>', unsafe_allow_html=True)


def view_market():
    st.markdown(f'<div class="sec-title serif">{L("三地市場行情", "Market Prices")}</div>'
                f'<div class="sec-sub">{L("亞庇 · 吉隆坡 · 台北 物價對比（RM / kg）", "Kota Kinabalu · Kuala Lumpur · Taipei (RM / kg)")}</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    # § HOOKS: df, meta = fetch_compare()  → 取代下方 MARKET 靜態值
    rows = ""
    for (zh, en, kk, kl, tpe, mom) in MARKET:
        pill = (f'<span class="pill-up">+{mom}%</span>' if mom > 0
                else f'<span class="pill-dn">{mom}%</span>')
        rows += (f'<tr><td><span class="nm">{L(zh, en)}</span>'
                 f'<span style="font-size:12px;color:#b39a6e;margin-left:7px">{en if ss.lang=="zh" else zh}</span></td>'
                 f'<td class="kk">{kk:.2f}</td><td>{kl:.2f}</td><td>{tpe:.2f}</td><td>{pill}</td></tr>')
    st.markdown(
        f'<table class="mkt"><tr><th>{L("品項", "Item")}</th><th>亞庇 KK</th><th>吉隆坡 KL</th>'
        f'<th>台北 TPE</th><th>MoM</th></tr>{rows}</table>', unsafe_allow_html=True)

    st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin:26px 0 12px">'
                f'<b class="serif" style="font-size:20px">{L("亞庇海鮮參考", "KK Seafood Reference")}</b>'
                f'<span style="font-size:12px;color:#a2917b">{L("來源：麗都 · 生源市場", "Source: Lido & Sang Yuan markets")}</span></div>',
                unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (zh, en, img, p) in enumerate(SEAFOOD):
        cols[i].markdown(
            f'<div class="dish-card"><div class="dish-img" style="height:108px;background-image:url({img_src(img)})"></div>'
            f'<div class="dish-body" style="display:flex;justify-content:space-between;align-items:center;padding-bottom:14px">'
            f'<div><div class="dish-name" style="font-size:15px">{L(zh, en)}</div>'
            f'<div class="dish-sub" style="font-size:11px">{en if ss.lang=="zh" else zh}</div></div>'
            f'<div style="text-align:right"><div class="dish-cost" style="margin:0">{fmt(p)}</div>'
            f'<div style="font-size:10px;color:#b39a6e">/ kg</div></div></div></div>', unsafe_allow_html=True)


def view_senior():
    st.markdown(f'<div style="text-align:center;margin-bottom:18px">'
                f'<div style="font-size:14px;letter-spacing:3px;text-transform:uppercase;color:#b39a6e">'
                f'{L("樂齡模式", "Senior Mode")}</div>'
                f'<div class="serif" style="font-weight:900;font-size:32px;margin-top:6px">'
                f'{L("今天吃這些", "Today\u2019s Meals")}</div></div>', unsafe_allow_html=True)
    p, m, n = st.columns([1, 2, 1])
    p.button("‹", key="sprev", use_container_width=True,
             on_click=lambda: ss.update(senior_day=(ss.senior_day + 6) % 7))
    sd = ss.senior_day
    m.markdown(f'<div style="text-align:center"><div class="serif" style="font-weight:900;font-size:24px">'
               f'{DAYS[sd][0]}</div><div style="color:#a2917b">{DAYS[sd][1]}</div></div>', unsafe_allow_html=True)
    n.button("›", key="snext", use_container_width=True,
             on_click=lambda: ss.update(senior_day=(ss.senior_day + 1) % 7))
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    for s in SLOTS:
        key = f"{sd}-{s[0]}"
        if key in ss.plan:
            d = DISH_BY_ID[ss.plan[key]]
            st.markdown(
                f'<div class="sr-card"><div class="sr-img" style="background-image:url({img_src(d[3])})"></div>'
                f'<div style="padding:16px 6px"><div class="sr-slot">{L(s[1], s[2])}</div>'
                f'<div class="sr-name">{L(d[1], d[2])}</div>'
                f'<div class="sr-sub">{d[2] if ss.lang=="zh" else d[1]}</div></div></div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="card" style="display:flex;gap:16px;align-items:center;color:#b39a6e">'
                f'<div class="sr-slot" style="min-width:70px">{L(s[1], s[2])}</div>'
                f'<div style="font-size:18px">{L("尚未安排", "Not planned yet")}</div></div>', unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)


def view_tips():
    st.markdown(f'<div class="sec-title serif">{L("小貼士", "Kitchen Tips")}</div>'
                f'<div class="sec-sub">{L("讓下廚更輕鬆的實用建議", "Practical advice to make cooking easier")}</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (zh, en, bz, be) in enumerate(TIPS):
        cols[i % 4].markdown(
            f'<div class="tip-card"><div class="tip-title">{L(zh, en)}</div>'
            f'<div class="tip-sub">{en}</div><div class="tip-body">{L(bz, be)}</div></div>',
            unsafe_allow_html=True)


VIEWS = {"discover": view_discover, "plan": view_plan, "shop": view_shop,
         "market": view_market, "senior": view_senior, "tips": view_tips}
VIEWS.get(ss.tab, view_discover)()
