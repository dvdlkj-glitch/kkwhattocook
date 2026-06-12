# -*- coding: utf-8 -*-
"""
🌸 今天煮什麼？— 亞庇家庭買菜煮飯小幫手
Kota Kinabalu Family Meal Planner (Lido Market + Damai Fresh Market)
Streamlit Dashboard — deploy: streamlit run app.py
RWD: 手機 / 平板 / 折疊機自適應
"""
import os
import base64
import urllib.parse
import functools
import random
from collections import defaultdict

import pandas as pd
import streamlit as st

from recipes_data import (
    RECIPES, MOODS, WEATHERS, CUISINE_STYLES, PROTEIN_PREFS,
    ING_CATEGORIES, SEAFOOD_PRICES, MARKET_TIPS, ELDERLY_TIPS,
)

# ---------------------------------------------------------------- 基本設定
st.set_page_config(
    page_title="今天煮什麼？亞庇買菜煮飯小幫手",
    page_icon="🌸",
    layout="wide",
)

RECIPE_BY_ID = {r["id"]: r for r in RECIPES}
DAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
DAY_EMOJIS = ["🌷", "🌼", "🌺", "🌻", "🌹", "🌸", "💐"]
IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

# ---------------------------------------------------------------- 主題 CSS（玫瑰豆沙粉）
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans TC', sans-serif; }

.stApp {
  background: linear-gradient(180deg, #FDF4F6 0%, #FBEFF2 45%, #F9EAEF 100%);
}

/* 主標題橫幅 */
.hero {
  background: linear-gradient(120deg, #C2698A 0%, #B45A78 55%, #9C4D68 100%);
  border-radius: 24px; padding: 28px 36px; color: #FFF8F9;
  box-shadow: 0 10px 30px rgba(180, 90, 120, 0.25);
  margin-bottom: 6px;
}
.hero h1 { margin: 0; font-size: 1.9rem; font-weight: 900; letter-spacing: 1px; }
.hero p  { margin: 6px 0 0 0; font-size: 0.95rem; opacity: 0.92; }
.hero .gold { color: #F4D9A6; font-weight: 700; }

/* 卡片 */
.card {
  background: #FFFFFF; border-radius: 20px; padding: 18px 20px;
  box-shadow: 0 6px 18px rgba(180, 90, 120, 0.10);
  border: 1px solid #F3DCE3; margin-bottom: 14px;
}
.meal-card {
  background: #FFFDFD; border-radius: 18px; padding: 14px 16px;
  border: 1.5px solid #F0D5DD; box-shadow: 0 4px 12px rgba(180,90,120,.08);
  margin-bottom: 8px; min-height: 150px;
}
.meal-tag {
  display:inline-block; font-size: 0.72rem; font-weight: 700;
  padding: 2px 10px; border-radius: 999px; margin-bottom: 6px;
}
.tag-lunch  { background:#FCEEDF; color:#A6731F; }
.tag-dinner { background:#EFE0F0; color:#7B4E86; }
.meal-name { font-size: 1.02rem; font-weight: 700; color: #6E3B4E; line-height:1.4; }
.cost-badge {
  display:inline-block; background: #FBE9EE; color: #B4456A;
  font-weight: 800; font-size: 0.86rem; border-radius: 10px;
  padding: 3px 10px; margin-top: 6px;
}
.chip {
  display:inline-block; background:#F7F0EA; color:#8A6A52;
  border-radius: 999px; font-size: 0.72rem; padding: 2px 9px; margin: 2px 2px;
}
.note {
  font-size: 0.78rem; color: #9A7C5B; background: #FDF7EC;
  border-left: 3px solid #DDB877; border-radius: 6px;
  padding: 5px 9px; margin-top: 7px;
}
.day-header {
  font-size: 1.12rem; font-weight: 900; color: #8E4560;
  padding: 4px 2px; margin: 6px 0 2px 0;
}
.section-title { font-size: 1.15rem; font-weight: 900; color: #8E4560; margin: 4px 0 10px 0; }

/* 統計小卡 */
.stat {
  background:#FFFFFF; border-radius:18px; text-align:center;
  padding: 14px 8px; border: 1px solid #F3DCE3;
  box-shadow: 0 4px 14px rgba(180,90,120,.10);
}
.stat .v { font-size: 1.35rem; font-weight: 900; color: #B4456A; }
.stat .l { font-size: 0.8rem; color: #A0728B; margin-top: 2px; }

/* 按鈕 */
.stButton > button {
  border-radius: 999px; border: 1.5px solid #E5B9C9;
  color: #8E4560; background: #FFF6F8; font-weight: 700;
}
.stButton > button:hover { border-color:#B4456A; color:#B4456A; background:#FDEDF2; }
div[data-testid="stButton"] > button[kind="primary"] {
  background: linear-gradient(120deg, #C2698A, #A8546F);
  color: #FFF; border: none; font-size: 1.05rem; font-weight: 900;
  padding: 0.6rem 1.4rem; box-shadow: 0 6px 16px rgba(180,90,120,.35);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
  background: #FFF6F8; border-radius: 999px; padding: 6px 16px;
  border: 1px solid #F0D5DD; color: #8E4560; font-weight: 700;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(120deg, #C2698A, #A8546F) !important;
  color: #FFF !important; border: none !important;
}

/* 表格 */
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }

/* ---------- 📱 手機 / 平板 / 折疊機自適應 ---------- */
/* 統計小卡列：自動換行 */
.stats-row { display:flex; flex-wrap:wrap; gap:10px; margin: 4px 0 10px 0; }
.stats-row .stat { flex: 1 1 160px; }

/* Tabs 在窄螢幕可左右滑動，不會擠成兩行 */
.stTabs [data-baseweb="tab-list"] {
  overflow-x: auto; flex-wrap: nowrap; scrollbar-width: none;
  -webkit-overflow-scrolling: touch; padding-bottom: 4px;
}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar { display: none; }
.stTabs [data-baseweb="tab"] { white-space: nowrap; flex-shrink: 0; }

/* 按鈕加大觸控面積（手指好按） */
.stButton > button { min-height: 2.5rem; }

/* 平板 / 折疊機展開（≤1024px）：欄位自動換行，一排最多 2 欄 */
@media (max-width: 1024px) {
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 0.7rem !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex: 1 1 45% !important; min-width: 45% !important; width: auto !important;
  }
}

/* 手機直向（≤640px）：一排一欄、字體與留白縮小 */
@media (max-width: 640px) {
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex: 1 1 100% !important; min-width: 100% !important;
  }
  .block-container { padding: 0.9rem 0.7rem !important; }
  .hero { padding: 18px 20px; border-radius: 18px; }
  .hero h1 { font-size: 1.35rem; }
  .hero p { font-size: 0.8rem; }
  .meal-card { min-height: unset; }
  .day-header { font-size: 1.05rem; }
  .stat .v { font-size: 1.15rem; }
}

/* 一週菜單：一天一卡 */
.day-card {
  background:#FFFFFF; border-radius:20px; border:1.5px solid #F0D5DD;
  box-shadow: 0 5px 16px rgba(180,90,120,.10);
  padding: 14px 14px 10px 14px; margin-bottom: 8px;
}
.day-head {
  display:flex; justify-content:space-between; align-items:center;
  font-weight:900; color:#8E4560; font-size:1.05rem; margin-bottom:8px;
}
.day-cost {
  background:#FBE9EE; color:#B4456A; font-size:.76rem; font-weight:800;
  border-radius:999px; padding:2px 10px; white-space:nowrap;
}
.meal-img {
  width:100%; height:110px; object-fit:cover; border-radius:12px;
  display:block; margin:6px 0;
}
.day-card .meal-name { min-height:2.9em; font-size:.95rem; }
.day-card .emoji-hero { height:110px; display:flex; align-items:center; justify-content:center; margin:6px 0; padding:0; }
.day-divider { border-top:1.5px dashed #F0D5DD; margin:10px 0 8px 0; }

/* emoji 大圖示佔位 */
.emoji-hero {
  font-size: 2.6rem; text-align:center; background:#FBEFF2;
  border-radius: 14px; padding: 10px 0; margin-bottom: 8px;
}
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- 邏輯
def people_factor(n: int) -> float:
    return {2: 0.8, 3: 1.0, 4: 1.15, 5: 1.35, 6: 1.5}.get(n, 1.0)

def scaled_cost(recipe: dict, n: int):
    f = people_factor(n)
    return int(round(recipe["cost"][0] * f)), int(round(recipe["cost"][1] * f))

def candidate_pool(meal: str, opts: dict):
    pool = []
    for r in RECIPES:
        if meal not in r["meal"]:
            continue
        if opts["elderly"] and not r["elderly_ok"]:
            continue
        if opts["kids"] and not r["kid_ok"]:
            continue
        pool.append(r)
    return pool

def score(r: dict, opts: dict, weekend_dinner: bool) -> float:
    s = 0.0
    if opts["mood"] in r["moods"]:
        s += 4
    if opts["weather"] in r["weather"]:
        s += 2
    style = opts["style"]
    if style == "中式家常為主":
        s += 3 if r["cuisine"] == "中式" else -2.5
    elif style == "泰式風味週":
        s += 3 if r["cuisine"] == "泰式" else -2.5
    else:
        s += 1
    pref = opts["protein"]
    if pref == "多肉類" and r["protein"] == "肉":
        s += 3
    elif pref == "多魚 / 海鮮" and r["protein"] in ("魚", "蝦", "海鮮"):
        s += 3
    elif pref == "蛋豆腐輕食" and r["protein"] == "蛋":
        s += 3
    if weekend_dinner and r.get("weekend"):
        s += 4
    if not weekend_dinner and r.get("weekend"):
        s -= 4
    return s

def generate_week(opts: dict, seed=None) -> dict:
    rng = random.Random(seed)
    plan, used = {}, set()
    for i, day in enumerate(DAYS):
        day_plan = {}
        for meal in ("lunch", "dinner"):
            weekend_dinner = (i >= 5 and meal == "dinner")
            pool = candidate_pool(meal, opts)
            fresh = [r for r in pool if r["id"] not in used] or pool
            fresh = sorted(fresh, key=lambda r: score(r, opts, weekend_dinner) + rng.random() * 3,
                           reverse=True)
            pick = fresh[0]
            used.add(pick["id"])
            day_plan[meal] = pick["id"]
        plan[day] = day_plan
    return plan

def swap_recipe(day: str, meal: str):
    """換一道：從符合條件的池子裡挑一道目前不在菜單上的"""
    opts = st.session_state["opts"]
    plan = st.session_state["plan"]
    i = DAYS.index(day)
    current_ids = {p[m] for p in plan.values() for m in p}
    pool = candidate_pool(meal, opts)
    alts = [r for r in pool if r["id"] not in current_ids]
    if not alts:
        alts = [r for r in pool if r["id"] != plan[day][meal]]
    if alts:
        weekend_dinner = (i >= 5 and meal == "dinner")
        alts = sorted(alts, key=lambda r: score(r, opts, weekend_dinner) + random.random() * 3,
                      reverse=True)
        plan[day][meal] = alts[0]["id"]

def aggregate_shopping(plan: dict) -> dict:
    """彙總一週食材 → {分類: [(名稱, 數量, 單位)]}"""
    agg = defaultdict(float)
    meta = {}
    for day_plan in plan.values():
        for rid in day_plan.values():
            for name, amt, unit, cat in RECIPE_BY_ID[rid]["ingredients"]:
                agg[(name, unit)] += amt
                meta[(name, unit)] = cat
    result = defaultdict(list)
    for (name, unit), amt in sorted(agg.items(), key=lambda x: meta[x[0]]):
        cat = meta[(name, unit)]
        if unit == "g" and amt >= 1000:
            qty = f"{amt/1000:.1f} kg".replace(".0 ", " ")
        else:
            qty = f"{int(amt)} {unit}"
        result[cat].append((name, qty))
    return result

def week_cost(plan: dict, n: int):
    lo = sum(scaled_cost(RECIPE_BY_ID[rid], n)[0] for p in plan.values() for rid in p.values())
    hi = sum(scaled_cost(RECIPE_BY_ID[rid], n)[1] for p in plan.values() for rid in p.values())
    return lo, hi

@functools.lru_cache(maxsize=64)
def _img_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def _meal_block(meal: str, rid: str, n: int) -> str:
    r = RECIPE_BY_ID[rid]
    lo, hi = scaled_cost(r, n)
    tag_cls = "tag-lunch" if meal == "lunch" else "tag-dinner"
    tag_txt = "🍱 午餐" if meal == "lunch" else "🌙 晚餐"
    img_path = os.path.join(IMG_DIR, r.get("img", "") or "_none_")
    if os.path.exists(img_path):
        visual = ("<img class='meal-img' src='data:image/jpeg;base64," +
                  _img_b64(img_path) + "'/>")
    else:
        visual = f"<div class='emoji-hero'>{r['emoji']}</div>"
    return (f"<div><span class='meal-tag {tag_cls}'>{tag_txt}</span>"
            f"{visual}"
            f"<div class='meal-name'>{r['name']}</div>"
            f"<span class='cost-badge'>💰 RM {lo} – {hi}</span></div>")

def render_day_card(day: str, n: int, elderly: bool):
    i = DAYS.index(day)
    lrid, drid = plan[day]["lunch"], plan[day]["dinner"]
    llo, lhi = scaled_cost(RECIPE_BY_ID[lrid], n)
    dlo, dhi = scaled_cost(RECIPE_BY_ID[drid], n)
    st.markdown(
        f"<div class='day-card'>"
        f"<div class='day-head'><span>{DAY_EMOJIS[i]} {day}</span>"
        f"<span class='day-cost'>全日 RM {llo + dlo} – {lhi + dhi}</span></div>"
        f"{_meal_block('lunch', lrid, n)}"
        f"<div class='day-divider'></div>"
        f"{_meal_block('dinner', drid, n)}"
        f"</div>",
        unsafe_allow_html=True,
    )
    b1, b2 = st.columns(2)
    b1.button("🔄 換午餐", key=f"swap_{day}_lunch",
              on_click=swap_recipe, args=(day, "lunch"), use_container_width=True)
    b2.button("🔄 換晚餐", key=f"swap_{day}_dinner",
              on_click=swap_recipe, args=(day, "dinner"), use_container_width=True)
    with st.expander("👩‍🍳 食材・做法・影片"):
        for label, rid in (("🍱 午餐", lrid), ("🌙 晚餐", drid)):
            r = RECIPE_BY_ID[rid]
            st.markdown(f"**{label}｜{r['name']}**")
            st.caption("、".join(f"{nm} {amt}{u}" for nm, amt, u, _ in r["ingredients"]))
            for si, step in enumerate(r.get("steps", []), 1):
                st.markdown(f"{si}. {step}")
            if elderly and r.get("elderly_note"):
                st.markdown(f"👵 {r['elderly_note']}")
            _q = urllib.parse.quote(r.get("yt", r["name"] + " 做法"))
            st.link_button(f"📺 {label[2:]}教學影片",
                           f"https://www.youtube.com/results?search_query={_q}",
                           use_container_width=True)

# ---------------------------------------------------------------- 頁首
st.markdown("""
<div class='hero'>
  <h1>🌸 今天煮什麼？</h1>
  <p>亞庇家庭買菜煮飯小幫手 ｜ <span class='gold'>麗都市場 Lido Market</span> ＆
     <span class='gold'>生源 Damai Fresh Market</span> ｜ 一鍵排好一週午晚餐、採買清單與預算 💕</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- 選項區（簡單不囉嗦）
st.markdown("<div class='section-title'>✨ 今天的心情與家裡狀況（選好按一鍵生成就好）</div>",
            unsafe_allow_html=True)

c1, c2, c3 = st.columns([1.3, 1.1, 1.3])
with c1:
    mood_label = st.radio("💗 這週想吃的感覺",
                          [f"{e} {t}" for e, t in MOODS.values()], horizontal=True)
    mood = list(MOODS.keys())[[f"{e} {t}" for e, t in MOODS.values()].index(mood_label)]
with c2:
    weather_label = st.radio("🌤️ 最近的天氣",
                             [f"{e} {t}" for e, t in WEATHERS.values()], horizontal=True)
    weather = list(WEATHERS.keys())[[f"{e} {t}" for e, t in WEATHERS.values()].index(weather_label)]
with c3:
    people = st.slider("👨‍👩‍👧 用餐人數", 2, 6, 4)

c4, c5, c6, c7 = st.columns([1, 1, 1.2, 1.2])
with c4:
    kids = st.toggle("🧒 家有小孩")
with c5:
    elderly = st.toggle("👵 家有年長者")
with c6:
    protein = st.selectbox("🍖 口味偏好", PROTEIN_PREFS)
with c7:
    style = st.selectbox("🥢 本週風味", CUISINE_STYLES)

opts = dict(mood=mood, weather=weather, people=people,
            kids=kids, elderly=elderly, protein=protein, style=style)

gen_col, _ = st.columns([1, 2])
with gen_col:
    if st.button("🪄 一鍵生成本週菜單", type="primary", use_container_width=True):
        st.session_state["opts"] = opts
        st.session_state["plan"] = generate_week(opts, seed=random.randint(0, 99999))
        st.balloons()

# 首次進入先給一份預設菜單，畫面不會空空的
if "plan" not in st.session_state:
    st.session_state["opts"] = opts
    st.session_state["plan"] = generate_week(opts, seed=20)

plan = st.session_state["plan"]
n = st.session_state["opts"]["people"]
sel_elderly = st.session_state["opts"]["elderly"]
sel_kids = st.session_state["opts"]["kids"]

# ---------------------------------------------------------------- 統計列
lo, hi = week_cost(plan, n)
seafood_meals = sum(1 for p in plan.values() for rid in p.values()
                    if RECIPE_BY_ID[rid]["protein"] in ("魚", "蝦", "海鮮"))
st.markdown(f"""
<div class='stats-row'>
  <div class='stat'><div class='v'>RM {lo} – {hi}</div><div class='l'>本週預估買菜費</div></div>
  <div class='stat'><div class='v'>14 餐</div><div class='l'>午餐 7 + 晚餐 7</div></div>
  <div class='stat'><div class='v'>{seafood_meals} 餐</div><div class='l'>有魚 / 海鮮</div></div>
  <div class='stat'><div class='v'>{n} 人</div><div class='l'>用餐人數</div></div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- 分頁
tab_week, tab_shop, tab_budget, tab_market, tab_elderly, tab_tips = st.tabs(
    ["📅 一週菜單", "🛒 採買清單", "💰 花費總覽", "🐟 市場行情", "👵 樂齡專區", "💡 小貼士"])

# ---- 📅 一週菜單
with tab_week:
    _has_photo = any(os.path.exists(os.path.join(IMG_DIR, RECIPE_BY_ID[rid].get("img", "") or "x"))
                     for p in plan.values() for rid in p.values())
    if not _has_photo:
        st.info("📷 尚未偵測到 images/ 資料夾內的菜餚照片，先以可愛圖示顯示。把照片上傳到 GitHub 的 images/ 後重新整理即可。")
    for chunk_start in (0, 4):
        days_chunk = DAYS[chunk_start:chunk_start + 4] if chunk_start == 0 else DAYS[4:]
        cols = st.columns(len(days_chunk))
        for col, day in zip(cols, days_chunk):
            with col:
                render_day_card(day, n, sel_elderly)

# ---- 🛒 採買清單
with tab_shop:
    st.markdown("<div class='section-title'>🛒 本週市場採買清單（已自動加總）</div>",
                unsafe_allow_html=True)
    shopping = aggregate_shopping(plan)
    cat_emojis = {"海鮮": "🐟", "肉類": "🍗", "蛋 / 豆腐": "🥚",
                  "蔬菜": "🥬", "麵 / 主食": "🍜", "辛香料 / 調味": "🧄"}
    cols = st.columns(3)
    lines = [f"🌸 本週採買清單（{n} 人份）", f"預估買菜費：RM {lo} – {hi}", ""]
    for idx, cat in enumerate(ING_CATEGORIES):
        items = shopping.get(cat, [])
        if not items:
            continue
        with cols[idx % 3]:
            items_html = "".join(
                f"<div style='padding:4px 0;border-bottom:1px dashed #F0D5DD;"
                f"display:flex;justify-content:space-between'>"
                f"<span>☐ {nm}</span><b style='color:#B4456A'>{qty}</b></div>"
                for nm, qty in items)
            st.markdown(f"<div class='card'><b style='color:#8E4560'>"
                        f"{cat_emojis.get(cat,'🛍️')} {cat}</b><br>{items_html}</div>",
                        unsafe_allow_html=True)
        lines.append(f"【{cat}】")
        lines += [f"  □ {nm}  {qty}" for nm, qty in items]
        lines.append("")
    lines += ["—" * 20] + MARKET_TIPS
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button("⬇️ 下載採買清單（帶去市場）", "\n".join(lines),
                           file_name="本週採買清單.txt", use_container_width=True)
    with dl2:
        _wa = "\n".join(lines)
        if len(_wa) > 1500:
            _wa = _wa[:1500] + "\n…"
        st.link_button("💬 用 WhatsApp 分享清單",
                       "https://wa.me/?text=" + urllib.parse.quote(_wa),
                       use_container_width=True)

# ---- 💰 花費總覽
with tab_budget:
    st.markdown("<div class='section-title'>💰 每日餐費預估（依人數調整後）</div>",
                unsafe_allow_html=True)
    rows = []
    for day in DAYS:
        l = RECIPE_BY_ID[plan[day]["lunch"]]
        d = RECIPE_BY_ID[plan[day]["dinner"]]
        llo, lhi = scaled_cost(l, n)
        dlo, dhi = scaled_cost(d, n)
        rows.append(dict(星期=day, 午餐=l["name"], 午餐費=f"RM {llo}–{lhi}",
                         晚餐=d["name"], 晚餐費=f"RM {dlo}–{dhi}",
                         當日預估=(llo + dlo + lhi + dhi) / 2))
    df = pd.DataFrame(rows)
    b1, b2 = st.columns([1.2, 1])
    with b1:
        st.dataframe(df[["星期", "午餐", "午餐費", "晚餐", "晚餐費"]],
                     use_container_width=True, hide_index=True)
    with b2:
        chart_df = df.set_index("星期")[["當日預估"]].rename(columns={"當日預估": "RM"})
        st.bar_chart(chart_df, color="#C2698A")
        avg = df["當日預估"].mean()
        st.markdown(f"<div class='card'>📌 平均每天買菜約 <b style='color:#B4456A'>"
                    f"RM {avg:.0f}</b>，一週合計約 <b style='color:#B4456A'>RM {lo} – {hi}</b>"
                    f"（{n} 人份，未含米、油、鹽、醬油等家中常備品）</div>",
                    unsafe_allow_html=True)

# ---- 🐟 市場行情
with tab_market:
    st.markdown("<div class='section-title'>🐟 麗都市場常見海鮮行情（RM / 公斤）</div>",
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

# ---- 👵 樂齡專區
with tab_elderly:
    st.markdown("<div class='section-title'>👵 適合家有年長者的食譜</div>",
                unsafe_allow_html=True)
    elder_recipes = [r for r in RECIPES if r["elderly_ok"]]
    cols = st.columns(3)
    for idx, r in enumerate(elder_recipes):
        lo2, hi2 = scaled_cost(r, n)
        with cols[idx % 3]:
            st.markdown(f"<div class='meal-card'><div class='emoji-hero'>{r['emoji']}</div>"
                        f"<div class='meal-name'>{r['name']}</div>"
                        f"<span class='cost-badge'>💰 RM {lo2} – {hi2}</span>"
                        f"<div class='note'>👵 {r['elderly_note']}</div></div>",
                        unsafe_allow_html=True)
    st.markdown("<div class='card'><b style='color:#8E4560'>🤍 為長輩備餐的小提醒</b><br>" +
                "<br>".join(ELDERLY_TIPS) + "</div>", unsafe_allow_html=True)

# ---- 💡 小貼士
with tab_tips:
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("<div class='card'><b style='color:#8E4560'>🧺 市場採買小貼士</b><br>" +
                    "<br>".join(MARKET_TIPS) + "</div>", unsafe_allow_html=True)
    with t2:
        st.markdown("""<div class='card'><b style='color:#8E4560'>🌸 使用小撇步</b><br>
        ① 先選心情、天氣、人數，按「🪄 一鍵生成」<br>
        ② 哪一餐不喜歡，按「🔄 換一道」就好<br>
        ③ 到「🛒 採買清單」下載清單，帶手機去市場照著買<br>
        ④ 把菜餚照片放進 <code>images/</code> 資料夾，卡片就會顯示照片<br>
        ⑤ 想加新食譜？打開 <code>recipes_data.py</code> 照格式加一筆即可
        </div>""", unsafe_allow_html=True)
        st.markdown("""<div class='card'><b style='color:#8E4560'>📍 之後可以擴充</b><br>
        ・更多地區市場（山打根、斗湖、西馬…）<br>
        ・更多菜系（娘惹、日式、韓式）<br>
        ・節慶菜單（農曆新年、中秋圍爐）<br>
        ・收藏「我家最愛」常用菜單
        </div>""", unsafe_allow_html=True)

st.markdown("<p style='text-align:center;color:#C99AAD;font-size:0.8rem;margin-top:18px'>"
            "🌸 今天煮什麼？ · 為亞庇的妳設計 · 價格為市場常見估算，實際以當日市價為準</p>",
            unsafe_allow_html=True)
