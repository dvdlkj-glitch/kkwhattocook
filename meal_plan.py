"""
meal_plan.py
============
餐表 CRUD,接 Supabase `meal_plan` 表。搭配 recipe_to_ingredients.py 使用。

meal_plan 與 recipes 透過 video_id 外鍵關聯,所以查詢時可以一次內嵌帶出
菜名、縮圖、食材(PostgREST embedded resource)。內嵌失敗時自動退回手動 join。
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

SLOTS = ["午", "晚"]


# ──────────────────────────────────────────────────────────────────────────
# 寫入 / 刪除
# ──────────────────────────────────────────────────────────────────────────
def add_to_plan(supabase: Any, plan_date: date, slot: str, video_id: str) -> None:
    """把一道菜排進某天某餐(同一格重複排同一道會被 unique 擋掉,不會重複)。"""
    supabase.table("meal_plan").upsert(
        {"plan_date": str(plan_date), "slot": slot, "video_id": video_id},
        on_conflict="plan_date,slot,video_id",
    ).execute()


def remove_from_plan(supabase: Any, plan_date: date, slot: str, video_id: str) -> None:
    (
        supabase.table("meal_plan")
        .delete()
        .eq("plan_date", str(plan_date))
        .eq("slot", slot)
        .eq("video_id", video_id)
        .execute()
    )


# ──────────────────────────────────────────────────────────────────────────
# 查詢
# ──────────────────────────────────────────────────────────────────────────
def get_plan(supabase: Any, start_date: date, end_date: date) -> list[dict]:
    """回傳日期區間內的餐表,內嵌 recipes 欄位。"""
    embed = "plan_date, slot, video_id, recipes(title, thumbnail_url, ingredients, inferred)"
    try:
        res = (
            supabase.table("meal_plan")
            .select(embed)
            .gte("plan_date", str(start_date))
            .lte("plan_date", str(end_date))
            .order("plan_date")
            .execute()
        )
        return res.data or []
    except Exception:
        # 內嵌 join 不可用時手動補:先抓 plan,再抓對應 recipes
        plan = (
            supabase.table("meal_plan")
            .select("*")
            .gte("plan_date", str(start_date))
            .lte("plan_date", str(end_date))
            .order("plan_date")
            .execute()
        ).data or []
        vids = list({p["video_id"] for p in plan})
        recipes: dict = {}
        if vids:
            rows = supabase.table("recipes").select("*").in_("video_id", vids).execute().data or []
            recipes = {r["video_id"]: r for r in rows}
        for p in plan:
            r = recipes.get(p["video_id"], {})
            p["recipes"] = {k: r.get(k) for k in ("title", "thumbnail_url", "ingredients", "inferred")}
        return plan


def week_start(d: date) -> date:
    """該日期所在週的週一。"""
    return d - timedelta(days=d.weekday())


def get_week_plan(supabase: Any, any_day: date) -> dict[tuple[str, str], list[dict]]:
    """
    整理成 {(date_str, slot): [dish, ...]},方便 UI 排七天 × 午/晚的格子。
    每個 dish: {video_id, title, thumbnail_url, ingredients, inferred}
    """
    mon = week_start(any_day)
    sun = mon + timedelta(days=6)
    rows = get_plan(supabase, mon, sun)

    grid: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        key = (row["plan_date"], row["slot"])
        rec = row.get("recipes") or {}
        grid.setdefault(key, []).append(
            {
                "video_id": row["video_id"],
                "title": rec.get("title") or "(未抽取)",
                "thumbnail_url": rec.get("thumbnail_url"),
                "ingredients": rec.get("ingredients") or [],
                "inferred": rec.get("inferred", False),
            }
        )
    return grid


def collect_week_recipes(grid: dict[tuple[str, str], list[dict]]) -> list[dict]:
    """
    把整週每一餐攤平成 recipe list 餵給 build_shopping_list。
    注意:含重複 —— 同一道菜排兩餐,食材份量就會加倍(這正是想要的)。
    """
    out: list[dict] = []
    for dishes in grid.values():
        out.extend(dishes)
    return out


def clear_week(supabase: Any, any_day: date) -> None:
    """清空某週（週一~週日）所有已排的菜。"""
    mon = week_start(any_day)
    sun = mon + timedelta(days=6)
    (
        supabase.table("meal_plan")
        .delete()
        .gte("plan_date", str(mon))
        .lte("plan_date", str(sun))
        .execute()
    )

# ──────────────────────────────────────────────────────────────────────────
# 食材庫（pantry）CRUD —— 全家共用、persist 到 Supabase
# ──────────────────────────────────────────────────────────────────────────
def get_pantry(supabase: Any) -> list[dict]:
    """回傳目前食材庫 [{item, category}, ...]（依加入時間）。"""
    try:
        res = (supabase.table("pantry")
               .select("item,category").order("added_at").execute())
        return res.data or []
    except Exception:
        return []


def add_pantry(supabase: Any, item: str, category: str = "") -> None:
    item = (item or "").strip()
    if not item:
        return
    supabase.table("pantry").upsert(
        {"item": item, "category": category}, on_conflict="item").execute()


def remove_pantry(supabase: Any, item: str) -> None:
    supabase.table("pantry").delete().eq("item", item).execute()


def clear_pantry(supabase: Any) -> None:
    supabase.table("pantry").delete().neq("item", "__none__").execute()
