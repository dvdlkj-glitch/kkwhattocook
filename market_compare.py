# -*- coding: utf-8 -*-
"""三地市場對比：
亞庇(KK) / 吉隆坡(KL) 取自馬來西亞 PriceCatcher 官方零售價（同幣別 RM）；
台北取自台灣農業部農產品批發行情，並用即時匯率 TWD→RM 換算（批發價，僅供跨國參考）。
"""
import os
import tempfile
import datetime
import urllib.request

import pandas as pd

PC_BASE = "https://storage.data.gov.my/pricecatcher"

# (顯示名稱, PriceCatcher 品項關鍵字, 台灣作物關鍵字或 None)
COMPARE_ITEMS = [
    ("🍗 雞肉 Ayam", ["AYAM STANDARD", "AYAM SUPER", "AYAM BERSIH"], None),
    ("🥚 雞蛋 Telur", ["TELUR AYAM"], None),
    ("🍅 番茄 Tomato", ["TOMATO"], ["番茄"]),
    ("🧅 洋蔥 Bawang", ["BAWANG BESAR"], ["洋蔥"]),
    ("🌶️ 辣椒 Cili", ["CILI"], ["辣椒"]),
    ("🦐 蝦 Udang", ["UDANG"], None),
    ("🐟 甘望魚 Kembung", ["IKAN KEMBUNG"], None),
]


def _read_parquet_url(url):
    fn = os.path.join(tempfile.gettempdir(), os.path.basename(url))
    if not os.path.exists(fn):
        urllib.request.urlretrieve(url, fn)
    return pd.read_parquet(fn)


def _mask_contains(premise, text):
    m = pd.Series(False, index=premise.index)
    for col in ("district", "state", "premise"):
        if col in premise.columns:
            m = m | premise[col].astype(str).str.contains(text, case=False, na=False)
    return m


def fetch_taipei_veg():
    """台北批發行情：回傳 {作物: 平均價 TWD/kg}（取最新交易日、跨品種平均）。"""
    import requests
    import urllib3
    urllib3.disable_warnings()
    r = requests.get("https://data.moa.gov.tw/Service/OpenData/FromM/FarmTransData.aspx",
                     timeout=25, verify=False)
    data = r.json()
    tpe = [d for d in data if "台北" in str(d.get("市場名稱", ""))]

    def dt(s):
        try:
            y, m, dd = str(s).split(".")
            return (int(y), int(m), int(dd))
        except Exception:
            return (0, 0, 0)

    out = {}
    for crop in ("番茄", "洋蔥", "辣椒"):
        rows = [d for d in tpe if crop in str(d.get("作物名稱", ""))]
        if not rows:
            continue
        latest = max(dt(d.get("交易日期", "")) for d in rows)
        vals = [float(d.get("平均價") or 0) for d in rows
                if dt(d.get("交易日期", "")) == latest and d.get("平均價")]
        vals = [v for v in vals if v > 0]
        if vals:
            out[crop] = sum(vals) / len(vals)
    return out


def fetch_twd_myr():
    try:
        import requests
        r = requests.get("https://open.er-api.com/v6/latest/TWD", timeout=10)
        return float(r.json()["rates"]["MYR"])
    except Exception:
        return 0.128


def fetch_compare():
    """回傳 (DataFrame, meta)；價格皆為 RM。"""
    premise = _read_parquet_url(f"{PC_BASE}/lookup_premise.parquet")
    items = _read_parquet_url(f"{PC_BASE}/lookup_item.parquet")
    kk = set(premise.loc[_mask_contains(premise, "Kota Kinabalu"), "premise_code"])
    kl = set(premise.loc[_mask_contains(premise, "Kuala Lumpur"), "premise_code"])

    today = datetime.date.today()
    first = today.replace(day=1)
    months = [today.strftime("%Y-%m"),
              (first - datetime.timedelta(days=1)).strftime("%Y-%m")]
    df = None
    used = None
    for m in months:
        try:
            d = _read_parquet_url(f"{PC_BASE}/pricecatcher_{m}.parquet")
            d = d[d["price"] > 0].merge(items[["item_code", "item", "unit"]],
                                        on="item_code", how="left")
            d["item"] = d["item"].astype(str).str.upper()
            df = d
            used = m
            break
        except Exception:
            continue
    if df is None:
        raise RuntimeError("PriceCatcher 下載失敗")

    def med(premset, kws):
        sub = df[df["premise_code"].isin(premset)]
        s = sub[sub["item"].str.contains("|".join(kws), na=False)]
        unit = s["unit"].mode().iloc[0] if len(s["unit"].mode()) else "1kg"
        return (float(s["price"].median()) if len(s) >= 3 else None), unit

    tpe = fetch_taipei_veg()
    rate = fetch_twd_myr()
    rows = []
    for label, kws, tcrops in COMPARE_ITEMS:
        kkp, unit = med(kk, kws)
        klp, _ = med(kl, kws)
        tp = None
        if tcrops:
            twd = next((tpe[c] for c in tcrops if c in tpe), None)
            if twd:
                tp = round(twd * rate, 2)
        rows.append({"品項": label,
                     "亞庇 KK": round(kkp, 2) if kkp else None,
                     "吉隆坡 KL": round(klp, 2) if klp else None,
                     "台北(批發)": tp,
                     "單位": unit})
    meta = {"month": used, "kk_n": len(kk), "kl_n": len(kl),
            "rate": rate, "tpe_items": len(tpe)}
    return pd.DataFrame(rows), meta
