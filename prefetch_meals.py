# -*- coding: utf-8 -*-
"""
夜間預抓：把還沒快取的菜，用受控預算搜尋並存進 Supabase（dish_candidates / dish_lookup / recipes）。
由 GitHub Actions 排程執行。金鑰一律從環境變數讀取。
"""
import os
import sys
import time

import anthropic
from supabase import create_client

import recipe_to_ingredients as R
from dishes_catalog import all_dish_names


def main():
    yt = os.environ["YOUTUBE_API_KEY"]
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    budget = int(os.environ.get("PREFETCH_BUDGET", "25"))  # 每晚最多搜幾道（每道一次 search=100u）

    names = all_dish_names()
    spent = 0
    ok = 0
    for n in names:
        if spent >= budget:
            break
        # 已有名稱快取或候選快取 → 跳過，不花額度
        if R.get_cached_video_id(sb, n) or R.get_candidates(sb, n):
            continue
        try:
            rec = R.get_or_build_by_name(
                n, yt_api_key=yt, anthropic_client=claude, supabase=sb, throttle=1.0)
            spent += 1
            if rec:
                ok += 1
                print("prefetched:", n)
            else:
                print("no-result:", n)
        except Exception as e:
            spent += 1
            print("fail:", n, str(e)[:100])
        time.sleep(1.0)

    print(f"DONE prefetched={ok} searched={spent} budget={budget}")


if __name__ == "__main__":
    sys.exit(main())
