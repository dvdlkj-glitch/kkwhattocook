"""
recipe_to_ingredients.py
========================
「今天煮什麼？」Dashboard 的反向管線核心:菜 → 食材 → 購物清單。

流程:
    search_dishes()      搜尋 YouTube 菜餚            (search.list,  100 units/次)
    fetch_description()  抓完整影片描述              (videos.list,    1 unit/次)
    extract_ingredients()  Claude 把描述抽成結構化食材 JSON
    get_or_build_recipe()  Supabase 快取:抽過的菜直接讀,不重燒額度
    build_shopping_list()  跨多道菜聚合成分類購物清單

設計原則(對齊 Market-Sentinel 的習慣):
    - snapshot-first:一道菜抽一次,永久存進 Supabase。
    - 額度省著用:search 100u 很貴,videos.list 只要 1u;LLM 抽取結果一定快取。
    - 模糊份量(適量/少許/一把)不硬做加法,照列就好。
    - 同義詞(蒜/蒜頭/大蒜)用 name_norm 合併。

依賴: requests, anthropic, supabase
    pip install requests anthropic supabase

Supabase 建表 SQL(跑一次):

    create table if not exists recipes (
        video_id      text primary key,
        title         text,
        channel       text,
        thumbnail_url text,
        servings      int,
        ingredients   jsonb,        -- [{name, name_norm, qty, unit, category, is_fuzzy}, ...]
        inferred      boolean default false,  -- 描述沒食材表、由 LLM 從菜名推測
        raw_description text,       -- 留著,抽取邏輯改進可重跑
        extracted_at  timestamptz default now()
    );

    create table if not exists meal_plan (
        id        bigint generated always as identity primary key,
        plan_date date not null,
        slot      text not null,   -- '午' / '晚'
        video_id  text references recipes(video_id),
        unique (plan_date, slot, video_id)
    );
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any

import requests

# 預設用 sonnet:中式描述常常很亂,sonnet 抽取較穩。
# 想省成本可換 "claude-haiku-4-5-20251001"。
DEFAULT_MODEL = "claude-sonnet-4-6"

# 超市動線分類順序(輸出購物清單時照這個排)
CATEGORY_ORDER = ["蔬菜", "肉類", "海鮮", "蛋豆製品", "調味料", "乾貨雜貨", "其他"]

_YT_SEARCH = "https://www.googleapis.com/youtube/v3/search"
_YT_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"


# ──────────────────────────────────────────────────────────────────────────
# 1. 搜尋菜餚  (search.list, 100 units/次 — 盡量讓使用者主動觸發,不要每次 rerun 都打)
# ──────────────────────────────────────────────────────────────────────────
def search_dishes(query: str, api_key: str, max_results: int = 6) -> list[dict]:
    """用菜名搜 YouTube,回傳縮圖卡片清單。"""
    params = {
        "part": "snippet",
        "q": f"{query} 做法 食譜",
        "type": "video",
        "maxResults": max_results,
        "regionCode": "TW",
        "relevanceLanguage": "zh-Hant",
        "key": api_key,
    }
    resp = requests.get(_YT_SEARCH, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json().get("items", [])

    cards = []
    for it in items:
        vid = it["id"]["videoId"]
        sn = it["snippet"]
        thumbs = sn.get("thumbnails", {})
        # 回傳裡 Google 已附好縮圖;maxres 不保證存在,故以 high 保底。
        thumb = (thumbs.get("high") or thumbs.get("medium") or thumbs.get("default") or {}).get("url")
        cards.append(
            {
                "video_id": vid,
                "title": sn.get("title", ""),
                "channel": sn.get("channelTitle", ""),
                "thumbnail_url": thumb,
                "url": f"https://www.youtube.com/watch?v={vid}",
            }
        )
    return cards


# ──────────────────────────────────────────────────────────────────────────
# 2. 抓完整描述  (videos.list, 只要 1 unit — search 的 snippet 是被截斷的,一定要再打這支)
# ──────────────────────────────────────────────────────────────────────────
def fetch_description(video_id: str, api_key: str) -> str:
    """取得影片完整描述(食材表通常藏在這)。"""
    params = {"part": "snippet", "id": video_id, "key": api_key}
    resp = requests.get(_YT_VIDEOS, params=params, timeout=10)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        return ""
    return items[0]["snippet"].get("description", "")


# ──────────────────────────────────────────────────────────────────────────
# 3. Claude 抽取食材  (一次解決:正規化名稱 / 模糊份量 / 超市分類 / 描述為空時的保底)
# ──────────────────────────────────────────────────────────────────────────
_EXTRACTION_PROMPT = """你是食材清單抽取器。根據料理影片的「標題」與「描述」,輸出這道菜的食材清單。

規則:
1. 只輸出 JSON,不要任何說明文字或 markdown 反引號。
2. 若描述裡有明確食材表,以它為準;若描述沒有食材資訊,就依菜名推測一份「家常做法」的典型食材,並把 inferred 設為 true。
3. 每個食材物件欄位:
   - name: 描述中的原始寫法
   - name_norm: 正規化後的標準名(蒜/蒜頭/大蒜 → 蒜頭;蔥/青蔥/蔥花 → 蔥;生抽/醬油 → 醬油),用於跨菜合併
   - qty: 數字(可為小數),沒有明確數字時設 null
   - unit: 單位字串(瓣/根/克/大匙/茶匙/顆/片...),沒有就 null
   - category: 從 [蔬菜, 肉類, 海鮮, 蛋豆製品, 調味料, 乾貨雜貨, 其他] 擇一
   - is_fuzzy: 份量是「適量/少許/一把/隨意」這類無法量化時設 true,否則 false
4. servings: 這份食材對應幾人份(看不出來就填 2)。

輸出格式:
{"servings": 2, "inferred": false, "ingredients": [
  {"name":"蒜頭","name_norm":"蒜頭","qty":3,"unit":"瓣","category":"蔬菜","is_fuzzy":false}
]}

標題: %(title)s

描述:
%(description)s
"""


def extract_ingredients(
    title: str,
    description: str,
    anthropic_client: Any,
    model: str = DEFAULT_MODEL,
) -> dict:
    """呼叫 Claude 把描述抽成結構化食材。回傳 {servings, inferred, ingredients[]}。"""
    prompt = _EXTRACTION_PROMPT % {
        "title": title,
        "description": (description or "(無描述)")[:6000],  # 控制 token
    }
    resp = anthropic_client.messages.create(
        model=model,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    return _safe_json(text)


def _safe_json(text: str) -> dict:
    """容錯解析:去掉可能的 ```json 圍欄,失敗時回安全空殼。"""
    cleaned = re.sub(r"```(?:json)?|```", "", text).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # 退而求其次:抓第一個 {...} 區塊
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        data = json.loads(m.group(0)) if m else {}
    data.setdefault("servings", 2)
    data.setdefault("inferred", False)
    data.setdefault("ingredients", [])
    return data


# ──────────────────────────────────────────────────────────────────────────
# 4. Supabase 快取  (抽過的菜直接讀 — 省 LLM 與 videos.list 額度)
# ──────────────────────────────────────────────────────────────────────────
def get_cached_recipe(supabase: Any, video_id: str) -> dict | None:
    res = supabase.table("recipes").select("*").eq("video_id", video_id).execute()
    rows = res.data or []
    return rows[0] if rows else None


def save_recipe(supabase: Any, record: dict) -> None:
    supabase.table("recipes").upsert(record, on_conflict="video_id").execute()


def get_or_build_recipe(
    card: dict,
    *,
    yt_api_key: str,
    anthropic_client: Any,
    supabase: Any,
    model: str = DEFAULT_MODEL,
) -> dict:
    """
    給一張搜尋卡片,回傳含食材的完整 recipe。
    先查 Supabase;沒有才抓描述 + LLM 抽取,並寫回快取。
    """
    video_id = card["video_id"]

    cached = get_cached_recipe(supabase, video_id)
    if cached:
        return cached

    description = fetch_description(video_id, yt_api_key)   # 1 unit
    extracted = extract_ingredients(card["title"], description, anthropic_client, model)

    record = {
        "video_id": video_id,
        "title": card.get("title"),
        "channel": card.get("channel"),
        "thumbnail_url": card.get("thumbnail_url"),
        "servings": extracted.get("servings", 2),
        "ingredients": extracted.get("ingredients", []),
        "inferred": extracted.get("inferred", False),
        "raw_description": description,
    }
    save_recipe(supabase, record)
    return record


# ──────────────────────────────────────────────────────────────────────────
# 5. 購物清單聚合  (跨多道菜合併、依分類輸出 — 改餐表就重跑這支,不存表)
# ──────────────────────────────────────────────────────────────────────────
def build_shopping_list(recipes: list[dict]) -> dict[str, list[dict]]:
    """
    輸入多道 recipe(各含 ingredients),輸出依超市分類分組的購物清單。

    合併規則:
        - 用 name_norm 分組(蒜頭/大蒜 算同一樣)。
        - 同單位的數字份量 → 相加。
        - 模糊份量(is_fuzzy / 無數字)→ 不硬加,標「適量」。
        - 不同單位 → 並列(例:醬油 2 大匙 + 1 茶匙),不強制換算。

    回傳: {"蔬菜": [{"name","amount","from":[菜名...]}...], ...}
    """
    # name_norm -> 累積桶
    agg: dict[str, dict] = {}

    for r in recipes:
        title = r.get("title", "")
        for ing in r.get("ingredients", []):
            key = ing.get("name_norm") or ing.get("name") or "未命名"
            bucket = agg.setdefault(
                key,
                {
                    "name": ing.get("name_norm") or ing.get("name") or "未命名",
                    "category": ing.get("category", "其他"),
                    "units": defaultdict(float),  # unit -> 累計數量
                    "fuzzy": False,
                    "sources": set(),
                },
            )
            bucket["sources"].add(title)

            qty = ing.get("qty")
            unit = (ing.get("unit") or "").strip()
            if ing.get("is_fuzzy") or qty is None:
                bucket["fuzzy"] = True
            else:
                try:
                    bucket["units"][unit] += float(qty)
                except (TypeError, ValueError):
                    bucket["fuzzy"] = True

    # 組裝顯示字串
    grouped: dict[str, list[dict]] = defaultdict(list)
    for bucket in agg.values():
        parts = []
        for unit, total in bucket["units"].items():
            num = int(total) if float(total).is_integer() else round(total, 2)
            parts.append(f"{num} {unit}".strip())
        if bucket["fuzzy"]:
            parts.append("適量")
        amount = " + ".join(parts) if parts else "適量"

        grouped[bucket["category"]].append(
            {
                "name": bucket["name"],
                "amount": amount,
                "from": sorted(bucket["sources"]),
            }
        )

    # 依超市動線排序分類,類別內依名稱排序
    ordered = {}
    for cat in CATEGORY_ORDER:
        if cat in grouped:
            ordered[cat] = sorted(grouped[cat], key=lambda x: x["name"])
    # 萬一 LLM 給了不在清單裡的分類,補在最後
    for cat, items in grouped.items():
        if cat not in ordered:
            ordered[cat] = sorted(items, key=lambda x: x["name"])
    return ordered


# ──────────────────────────────────────────────────────────────────────────
# 使用範例(Streamlit 端大致長這樣):
#
#     import streamlit as st
#     from anthropic import Anthropic
#     from supabase import create_client
#     import recipe_to_ingredients as R
#
#     yt_key   = st.secrets["YOUTUBE_API_KEY"]
#     claude   = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
#     supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
#
#     # 1) 使用者搜尋(用按鈕觸發,別每次 rerun 都打 100u)
#     cards = R.search_dishes("麻婆豆腐", yt_key)
#
#     # 2) 使用者勾選想煮的幾道 → 各自取得含食材的 recipe(自動走快取)
#     chosen = [R.get_or_build_recipe(c, yt_api_key=yt_key,
#                                     anthropic_client=claude, supabase=supabase)
#               for c in selected_cards]
#
#     # 3) 一鍵生成分類購物清單
#     shopping = R.build_shopping_list(chosen)
#     for category, items in shopping.items():
#         st.subheader(category)
#         for it in items:
#             st.write(f"☐ {it['name']} — {it['amount']}  ·來自 {', '.join(it['from'])}")
# ──────────────────────────────────────────────────────────────────────────
