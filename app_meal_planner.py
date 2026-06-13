"""
app_meal_planner.py
===================
「今天煮什麼?」反向排餐 UI。

流程:① 找菜(搜尋→排入餐表,排入時自動抽食材並快取)
      ② 一週餐表(七天 × 午/晚,可移除、可翻週)
      ③ 一鍵生成分類購物清單(可勾選、可下載)

慣例(沿用 Market-Sentinel):
  - 不使用 nested st.columns
  - 每個 render 區塊包 try/except
  - 按鈕樣式用 .st-key-{key} button

需要的 secrets(本機 .streamlit/secrets.toml + Streamlit Cloud 兩處都要):
    YOUTUBE_API_KEY, ANTHROPIC_API_KEY, SUPABASE_URL, SUPABASE_KEY
"""

from datetime import date, timedelta

import streamlit as st
from anthropic import Anthropic
from supabase import create_client

import recipe_to_ingredients as R
import meal_plan as MP

st.set_page_config(page_title="今天煮什麼?", page_icon="🍳", layout="wide")


# ── 連線(資源快取,不會每次 rerun 重建)──────────────────────────────────
@st.cache_resource
def get_clients():
    claude = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    return claude, sb


claude, supabase = get_clients()
YT_KEY = st.secrets["YOUTUBE_API_KEY"]


# ── 按鈕樣式(.st-key-{key} pattern)──────────────────────────────────────
st.markdown(
    """
    <style>
      .st-key-do_search button   { background:#06b6d4; color:#fff; font-weight:700; }
      .st-key-gen_shopping button { background:#059669; color:#fff; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── session state ────────────────────────────────────────────────────────
ss = st.session_state
ss.setdefault("cards", [])
ss.setdefault("target_date", date.today())
ss.setdefault("target_slot", "晚")
ss.setdefault("week_anchor", date.today())
ss.setdefault("show_shopping", False)


st.title("🍳 今天煮什麼?")
st.caption("從 YouTube 找菜 → 自動抽食材 → 一週排餐 → 分類購物清單")


# ══════════════════════════════════════════════════════════════════════════
# ① 找菜 + 排入餐表
# ══════════════════════════════════════════════════════════════════════════
st.subheader("① 找菜")

c1, c2, c3 = st.columns([2, 1, 3])  # 頂層 columns,非 nested
with c1:
    ss.target_date = st.date_input("排入日期", value=ss.target_date)
with c2:
    ss.target_slot = st.radio(
        "時段", MP.SLOTS, index=MP.SLOTS.index(ss.target_slot), horizontal=True
    )
with c3:
    query = st.text_input("想煮什麼?(輸入菜名)", placeholder="例:麻婆豆腐")

if st.button("🔍 搜尋", key="do_search"):
    if query.strip():
        with st.spinner("搜尋中…(花 100 units)"):
            try:
                ss.cards = R.search_dishes(query.strip(), YT_KEY)
                ss.show_shopping = False
            except Exception as e:
                st.error(f"搜尋失敗:{e}")
                ss.cards = []
    else:
        st.warning("請先輸入菜名。")

# 渲染搜尋結果卡片
if ss.cards:
    try:
        cols = st.columns(3)  # 頂層
        for i, card in enumerate(ss.cards):
            with cols[i % 3]:
                if card.get("thumbnail_url"):
                    st.image(card["thumbnail_url"], use_container_width=True)
                st.markdown(f"**{card['title'][:46]}**")
                st.caption(f"📺 {card['channel']}")
                if st.button("➕ 排入此餐", key=f"add_{card['video_id']}"):
                    with st.spinner("抽取食材中…(首次會打 1 unit + Claude,之後走快取)"):
                        try:
                            recipe = R.get_or_build_recipe(
                                card,
                                yt_api_key=YT_KEY,
                                anthropic_client=claude,
                                supabase=supabase,
                            )
                            MP.add_to_plan(
                                supabase, ss.target_date, ss.target_slot, card["video_id"]
                            )
                            tag = " ⚠由菜名推測,請核對" if recipe.get("inferred") else ""
                            st.success(
                                f"已排入 {ss.target_date} {ss.target_slot}:"
                                f"{recipe['title'][:20]}{tag}"
                            )
                        except Exception as e:
                            st.error(f"排入失敗:{e}")
    except Exception as e:
        st.error(f"卡片渲染錯誤:{e}")

st.divider()


# ══════════════════════════════════════════════════════════════════════════
# ② 一週餐表
# ══════════════════════════════════════════════════════════════════════════
st.subheader("② 一週餐表")

nav1, nav2, nav3 = st.columns([1, 2, 1])  # 頂層
with nav1:
    if st.button("← 上一週"):
        ss.week_anchor -= timedelta(days=7)
with nav3:
    if st.button("下一週 →"):
        ss.week_anchor += timedelta(days=7)
mon = MP.week_start(ss.week_anchor)
with nav2:
    st.markdown(f"**{mon} ～ {mon + timedelta(days=6)}**")

grid = {}
try:
    grid = MP.get_week_plan(supabase, ss.week_anchor)
    day_cols = st.columns(7)  # 頂層
    week_names = ["一", "二", "三", "四", "五", "六", "日"]
    for d in range(7):
        day = mon + timedelta(days=d)
        with day_cols[d]:
            st.markdown(f"**週{week_names[d]}**　{day.month}/{day.day}")
            for slot in MP.SLOTS:
                st.caption(f"— {slot} —")
                dishes = grid.get((str(day), slot), [])
                if not dishes:
                    st.caption("　·")
                for dish in dishes:
                    if dish.get("thumbnail_url"):
                        st.image(dish["thumbnail_url"], use_container_width=True)
                    flag = " ⚠" if dish.get("inferred") else ""
                    st.caption(dish["title"][:22] + flag)
                    if st.button("✕ 移除", key=f"rm_{day}_{slot}_{dish['video_id']}"):
                        MP.remove_from_plan(supabase, day, slot, dish["video_id"])
                        st.rerun()
except Exception as e:
    st.error(f"餐表載入錯誤:{e}")

st.divider()


# ══════════════════════════════════════════════════════════════════════════
# ③ 購物清單
# ══════════════════════════════════════════════════════════════════════════
st.subheader("③ 購物清單")

if st.button("🛒 生成本週購物清單", key="gen_shopping"):
    ss.show_shopping = True

if ss.show_shopping:
    try:
        recipes = MP.collect_week_recipes(grid)
        if not recipes:
            st.info("這週還沒排菜。")
        else:
            shopping = R.build_shopping_list(recipes)
            export_lines = []
            for cat, items in shopping.items():
                st.markdown(f"### {cat}")
                for it in items:
                    label = f"{it['name']} — {it['amount']}"
                    st.checkbox(label, key=f"buy_{cat}_{it['name']}")
                    export_lines.append(f"[ ] {label}　({'、'.join(it['from'])})")
            txt = f"本週購物清單（{mon} ～ {mon + timedelta(days=6)}）\n\n" + "\n".join(export_lines)
            st.download_button("📄 下載清單(.txt)", txt, file_name="shopping_list.txt")
    except Exception as e:
        st.error(f"購物清單錯誤:{e}")
