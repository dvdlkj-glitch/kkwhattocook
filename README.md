# 🌸 今天煮什麼？— 亞庇家庭買菜煮飯小幫手

依據麗都市場（Lido Market）＋ 生源市場（Damai Fresh Market）常見食材，
一鍵生成一週午餐＋晚餐、自動加總採買清單、預估每餐花費。

## 檔案結構

```
├── app.py             # Streamlit 主程式（介面 + 邏輯）
├── recipes_data.py    # 食譜資料庫（要加菜就改這裡）
├── requirements.txt
└── images/            # 菜餚照片（選用）
```

## 本機執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 部署到 Streamlit Cloud（透過 GitHub）

1. 在 GitHub 建一個新 repository，把這幾個檔案（含 `images/` 資料夾）上傳。
2. 到 https://share.streamlit.io 用 GitHub 帳號登入。
3. 按「New app」→ 選你的 repo → Main file path 填 `app.py` → Deploy。
4. 完成！會得到一個公開網址，手機也能開。

## 放入菜餚照片

把照片放進 `images/` 資料夾，檔名對應 `recipes_data.py` 每道菜的 `img` 欄位
（例如 `images/tomato_egg.jpg`）。沒有照片時卡片會自動顯示可愛 emoji。
建議尺寸：寬 800px 左右、jpg 格式，載入較快。

## 新增 / 修改食譜

打開 `recipes_data.py`，照現有格式複製一筆 `dict(...)` 修改即可：
菜名、食材分量、價格範圍、適合的心情 / 天氣、是否適合長輩與小孩。
存檔後重新整理網頁就生效。

## 之後擴充方向

- 更多地區（山打根、斗湖、西馬各州市場價格）
- 更多菜系（娘惹、日式、韓式）
- 節慶菜單、收藏「我家最愛」
