# -*- coding: utf-8 -*-
"""
亞庇家庭食譜資料庫
依據 Lido Market（麗都市場）+ Damai Fresh Market 常見食材整理
價格為市場常見估算（RM），基準份量為 2-3 人份
想新增 / 修改食譜，只要照同樣格式加一筆即可。
"""

# 心情選項: easy=輕鬆快手 / rich=豐盛犒賞 / light=清淡養生 / appetite=開胃下飯
# 天氣選項: hot=炎熱 / rain=下雨 / cool=涼爽
# ingredients: (名稱, 數量, 單位, 分類)  單位相同會自動加總到採買清單

MOODS = {
    "easy":     ("😌", "輕鬆快手"),
    "rich":     ("🥰", "豐盛犒賞"),
    "light":    ("🍃", "清淡養生"),
    "appetite": ("🌶️", "開胃下飯"),
}

WEATHERS = {
    "hot":  ("☀️", "炎熱"),
    "rain": ("🌧️", "下雨天"),
    "cool": ("⛅", "涼爽"),
}

CUISINE_STYLES = ["中式家常為主", "中式 + 泰式混搭", "泰式風味週"]

PROTEIN_PREFS = ["均衡搭配", "多肉類", "多魚 / 海鮮", "蛋豆腐輕食"]

ING_CATEGORIES = ["海鮮", "肉類", "蛋 / 豆腐", "蔬菜", "麵 / 主食", "辛香料 / 調味"]

RECIPES = [
    # ---------------- 中式家常（飯餐） ----------------
    dict(id="tomato_egg", yt='番茄炒蛋 家常做法',
         steps=['蛋加少許鹽打散，熱油炒至半熟先盛起', '番茄切塊下鍋炒出湯汁，加少許糖和鹽', '蛋回鍋拌勻即起', '另起鍋蒜末爆香，大火快炒青菜'], name="番茄炒蛋 + 蒜炒青菜", emoji="🍅", cuisine="中式",
         meal=["lunch", "dinner"], cost=(10, 14),
         ingredients=[("番茄", 400, "g", "蔬菜"), ("雞蛋", 4, "顆", "蛋 / 豆腐"),
                      ("菜心 / 小白菜", 500, "g", "蔬菜"), ("蒜頭", 30, "g", "辛香料 / 調味")],
         moods=["easy", "light"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="蛋炒嫩一點、青菜切小段更好咀嚼",
         kid_ok=True, protein="蛋", tip="平日最省家常餐", img="tomato_egg.jpg"),

    dict(id="soy_chicken", yt='醬油雞 家常做法',
         steps=['雞肉汆燙去血水', '爆香薑蒜，雞肉煎至表面微黃', '加醬油、少許糖與水，小火燜 20 分鐘', '收汁撒蔥花；另鍋清炒芥蘭'], name="醬油雞 + 清炒芥蘭", emoji="🍗", cuisine="中式",
         meal=["lunch", "dinner"], cost=(18, 23),
         ingredients=[("雞肉", 800, "g", "肉類"), ("芥蘭", 500, "g", "蔬菜"),
                      ("薑", 50, "g", "辛香料 / 調味"), ("蒜頭", 20, "g", "辛香料 / 調味"),
                      ("青蔥", 2, "根", "辛香料 / 調味")],
         moods=["easy", "rich"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="雞肉多燜 10 分鐘更軟嫩，方便長輩食用",
         kid_ok=True, protein="肉", tip="雞肉容易買到，做法穩定", img="soy_chicken.jpg"),

    dict(id="asam_fish", yt='亞參魚 asam pedas 做法',
         steps=['甘望魚煎至兩面微黃備用', '爆香洋蔥，加亞參膏、番茄與水煮開', '放入魚小火煮 10 分鐘，調味', 'Sambal 辣椒醬大火快炒空心菜'], name="亞參甘望魚 + Sambal 空心菜", emoji="🐟", cuisine="中式",
         meal=["lunch", "dinner"], cost=(20, 26),
         ingredients=[("甘望魚 (Ikan Kembung)", 800, "g", "海鮮"), ("番茄", 300, "g", "蔬菜"),
                      ("洋蔥", 150, "g", "蔬菜"), ("亞參膏 / 羅望子醬", 50, "g", "辛香料 / 調味"),
                      ("空心菜", 500, "g", "蔬菜"), ("辣椒", 30, "g", "辛香料 / 調味")],
         moods=["appetite"], weather=["hot", "rain"], spicy=True,
         elderly_ok=False, elderly_note="甘望魚刺較多，長輩同桌建議改清蒸石斑或馬鮫魚",
         kid_ok=False, protein="魚", tip="在地常見、開胃下飯", img="asam_fish.jpg"),

    dict(id="steam_prawn_tofu", yt='清蒸蝦 蒸水蛋 做法',
         steps=['白蝦排盤鋪薑絲，水滾大火蒸 6–8 分鐘', '蛋液加 1.5 倍溫水打勻過篩，與嫩豆腐同蒸 12 分鐘', '兩道都淋上醬油與熱油提香', '青江菜下蒜片清炒'], name="清蒸白蝦 + 豆腐蛋羹 + 青江菜", emoji="🦐", cuisine="中式",
         meal=["dinner"], cost=(32, 39),
         ingredients=[("本地白蝦", 700, "g", "海鮮"), ("嫩豆腐", 2, "盒", "蛋 / 豆腐"),
                      ("雞蛋", 3, "顆", "蛋 / 豆腐"), ("青江菜", 400, "g", "蔬菜"),
                      ("薑", 30, "g", "辛香料 / 調味"), ("青蔥", 2, "根", "辛香料 / 調味")],
         moods=["light", "rich"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="蒸蛋與豆腐軟嫩，蝦可先去殼方便長輩",
         kid_ok=True, protein="蝦", tip="營養均衡、海鮮鮮甜", img="steam_prawn.jpg"),

    dict(id="fried_mackerel", yt='香煎馬鮫魚 做法',
         steps=['魚片抹鹽醃 10 分鐘後擦乾水分', '中火煎至兩面金黃酥香', '豆腐番茄加水煮滾調味成湯', '蒜末爆香炒長豆'], name="香煎馬鮫魚 + 豆腐番茄湯 + 蒜炒長豆", emoji="🐠", cuisine="中式",
         meal=["dinner"], cost=(30, 36),
         ingredients=[("馬鮫魚 (Ikan Tenggiri)", 700, "g", "海鮮"), ("豆腐", 2, "塊", "蛋 / 豆腐"),
                      ("番茄", 250, "g", "蔬菜"), ("長豆", 500, "g", "蔬菜"),
                      ("蒜頭", 30, "g", "辛香料 / 調味"), ("薑", 30, "g", "辛香料 / 調味")],
         moods=["rich", "appetite"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="馬鮫魚肉厚無細刺，最適合長輩與小孩",
         kid_ok=True, protein="魚", tip="肉厚少刺，家庭接受度高", img="mackerel.jpg"),

    dict(id="steam_grouper", yt='清蒸石斑魚 做法',
         steps=['魚身劃刀、鋪薑絲，水滾後大火蒸 10–12 分鐘', '倒掉蒸出的腥水，鋪上蔥絲', '燒熱油淋上，再淋蒸魚醬油', '豆腐湯煮滾調味；菠菜清炒'], name="清蒸紅鰽魚 / 石斑 + 清炒菠菜 + 豆腐湯", emoji="🐡", cuisine="中式",
         meal=["dinner"], cost=(36, 48),
         ingredients=[("紅鰽魚 / 石斑 (Ikan Merah / Kerapu)", 900, "g", "海鮮"),
                      ("菠菜", 500, "g", "蔬菜"), ("嫩豆腐", 1, "盒", "蛋 / 豆腐"),
                      ("薑絲", 20, "g", "辛香料 / 調味"), ("青蔥", 2, "根", "辛香料 / 調味"),
                      ("蒜頭", 20, "g", "辛香料 / 調味")],
         moods=["light", "rich"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="清蒸最能吃出鮮味，魚肉細嫩好入口",
         kid_ok=True, protein="魚", tip="週末升級版，清蒸最能吃出鮮味", img="grouper.jpg"),

    dict(id="weekend_feast", yt='清蒸魚 奶油蝦 做法',
         steps=['魚清蒸（劃刀鋪薑、大火 10–12 分鐘、淋油與醬油）', '蒜蓉與奶油炒香，下蝦快炒至轉紅', '冬瓜與雞肉加薑燉湯 40 分鐘', '起鍋前調味、撒蔥花'], name="週末加菜：清蒸魚 + 蒜蓉奶油蝦 + 冬瓜雞湯", emoji="🎉", cuisine="中式",
         meal=["dinner"], cost=(54, 70), weekend=True,
         ingredients=[("紅鰽魚 / 石斑", 800, "g", "海鮮"), ("本地白蝦", 600, "g", "海鮮"),
                      ("雞肉", 600, "g", "肉類"), ("冬瓜", 600, "g", "蔬菜"),
                      ("青菜", 600, "g", "蔬菜"), ("蒜頭", 40, "g", "辛香料 / 調味"),
                      ("薑", 30, "g", "辛香料 / 調味"), ("青蔥", 2, "根", "辛香料 / 調味")],
         moods=["rich"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="湯品燉久一點，雞肉軟爛適合長輩",
         kid_ok=True, protein="海鮮", tip="適合家庭聚餐，海鮮與湯品一次到位", img="weekend_feast.jpg"),

    dict(id="pork_tofu", yt='豆腐肉碎 苦瓜湯 做法',
         steps=['肉碎爆香，加豆腐與醬油小火燜煮', '肉片大火快炒青菜', '苦瓜與肉片煮湯 20 分鐘，調味'], name="豆腐肉碎 + 肉片炒青菜 + 苦瓜湯", emoji="🥩", cuisine="中式",
         meal=["dinner"], cost=(30, 42),
         ingredients=[("豬肉", 450, "g", "肉類"), ("豆腐", 2, "塊", "蛋 / 豆腐"),
                      ("青菜", 500, "g", "蔬菜"), ("苦瓜", 300, "g", "蔬菜"),
                      ("蒜頭", 30, "g", "辛香料 / 調味")],
         moods=["rich", "appetite"], weather=["hot", "cool"], spicy=False,
         elderly_ok=True, elderly_note="肉碎軟嫩易咀嚼，苦瓜湯清熱",
         kid_ok=True, protein="肉", tip="有豬肉晚餐的家常組合", img="pork_tofu.jpg"),

    dict(id="curry_chicken", yt='馬來西亞咖哩雞 做法',
         steps=['爆香洋蔥與咖哩醬／咖哩粉', '雞肉與馬鈴薯下鍋翻炒上色', '加水（或椰奶）小火燜 25 分鐘', '另煎蛋、炒青菜'], name="咖哩雞 + 炒青菜 + 煎蛋", emoji="🍛", cuisine="中式",
         meal=["lunch", "dinner"], cost=(22, 32),
         ingredients=[("雞肉", 800, "g", "肉類"), ("馬鈴薯", 300, "g", "蔬菜"),
                      ("青菜", 500, "g", "蔬菜"), ("雞蛋", 3, "顆", "蛋 / 豆腐"),
                      ("咖哩粉 / 咖哩醬", 1, "包", "辛香料 / 調味"), ("洋蔥", 150, "g", "蔬菜")],
         moods=["appetite", "rich"], weather=["rain", "cool"], spicy=True,
         elderly_ok=True, elderly_note="咖哩減辣、馬鈴薯燉軟即可",
         kid_ok=True, protein="肉", tip="下雨天最暖胃的家常咖哩", img="curry_chicken.jpg"),

    dict(id="fried_kembung", yt='炸甘望魚 做法',
         steps=['魚抹鹽與薑黃粉醃 15 分鐘', '熱油煎／炸至兩面金黃酥脆', '蒜末爆香快炒青菜'], name="煎甘望魚 + 炒青菜", emoji="🍳", cuisine="中式",
         meal=["lunch"], cost=(15, 22),
         ingredients=[("甘望魚 (Ikan Kembung)", 600, "g", "海鮮"), ("青菜", 500, "g", "蔬菜"),
                      ("蒜頭", 20, "g", "辛香料 / 調味")],
         moods=["easy"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=False, elderly_note="甘望魚刺較多，長輩建議改吃馬鮫魚",
         kid_ok=True, protein="魚", tip="價格親民的普通午餐", img="fried_kembung.jpg"),

    # ---------------- 湯麵・拉麵・燉湯 ----------------
    dict(id="tomato_egg_noodle", yt='番茄蛋花湯麵 做法',
         steps=['番茄炒軟出汁，加水煮開', '緩緩淋入蛋液成蛋花，調味', '黃麵燙熟入湯', '蒜炒小白菜'], name="番茄蛋花湯麵 + 蒜炒小白菜", emoji="🍜", cuisine="中式",
         meal=["lunch"], cost=(12, 17),
         ingredients=[("新鮮黃麵", 600, "g", "麵 / 主食"), ("番茄", 400, "g", "蔬菜"),
                      ("雞蛋", 4, "顆", "蛋 / 豆腐"), ("小白菜", 500, "g", "蔬菜"),
                      ("蒜頭", 30, "g", "辛香料 / 調味"), ("青蔥", 1, "根", "辛香料 / 調味")],
         moods=["easy", "light"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="麵煮軟一點，湯清爽不油膩",
         kid_ok=True, protein="蛋", tip="清爽快速，適合平日", img="tomato_noodle.jpg"),

    dict(id="chicken_mushroom_ramen", yt='雞絲香菇麵 做法',
         steps=['雞肉、香菇、薑片加水煮湯 20 分鐘', '雞肉撕成絲放回湯中', '拉麵燙熟入碗、淋湯', '黃瓜拍碎加蒜醋涼拌'], name="雞絲香菇拉麵 + 涼拌黃瓜", emoji="🍲", cuisine="中式",
         meal=["lunch"], cost=(18, 24),
         ingredients=[("拉麵", 500, "g", "麵 / 主食"), ("雞腿 / 雞胸", 800, "g", "肉類"),
                      ("鮮香菇 / 杏鮑菇", 300, "g", "蔬菜"), ("青江菜", 300, "g", "蔬菜"),
                      ("黃瓜", 300, "g", "蔬菜"), ("薑", 30, "g", "辛香料 / 調味")],
         moods=["easy", "light"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="雞絲撕細、香菇切薄片更易咀嚼",
         kid_ok=True, protein="肉", tip="雞肉容易買到，湯頭穩定", img="chicken_ramen.jpg"),

    dict(id="asam_fish_noodle", yt='亞參魚湯麵 做法',
         steps=['爆香洋蔥，加亞參膏、番茄與水煮湯底', '甘望魚入湯煮 10 分鐘', '麵燙熟入碗、淋酸辣魚湯', 'Sambal 炒空心菜'], name="亞參甘望魚湯麵 + Sambal 空心菜", emoji="🌶️", cuisine="中式",
         meal=["lunch"], cost=(22, 29),
         ingredients=[("甘望魚 (Ikan Kembung)", 800, "g", "海鮮"), ("新鮮麵", 500, "g", "麵 / 主食"),
                      ("番茄", 300, "g", "蔬菜"), ("洋蔥", 150, "g", "蔬菜"),
                      ("亞參膏 / 羅望子", 40, "g", "辛香料 / 調味"), ("空心菜", 500, "g", "蔬菜"),
                      ("辣椒", 20, "g", "辛香料 / 調味")],
         moods=["appetite"], weather=["hot"], spicy=True,
         elderly_ok=False, elderly_note="酸辣口味與魚刺較不適合長輩",
         kid_ok=False, protein="魚", tip="在地常見，酸辣開胃", img="asam_noodle.jpg"),

    dict(id="prawn_tofu_ramen", yt='鮮蝦湯麵 蒸蛋 做法',
         steps=['蝦頭蝦殼炒香後加水熬出鮮湯', '蝦肉與豆腐入湯煮熟，調味', '拉麵燙熟入碗', '蛋液加溫水蒸 12 分鐘成蒸蛋'], name="白蝦豆腐清湯拉麵 + 蒸蛋", emoji="🥚", cuisine="中式",
         meal=["lunch"], cost=(30, 39),
         ingredients=[("本地白蝦", 600, "g", "海鮮"), ("拉麵", 500, "g", "麵 / 主食"),
                      ("嫩豆腐", 2, "盒", "蛋 / 豆腐"), ("雞蛋", 3, "顆", "蛋 / 豆腐"),
                      ("青江菜", 400, "g", "蔬菜"), ("薑", 20, "g", "辛香料 / 調味")],
         moods=["light", "rich"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="清湯 + 蒸蛋 + 豆腐，是最適合長輩的一餐",
         kid_ok=True, protein="蝦", tip="營養均衡，海鮮鮮甜", img="prawn_ramen.jpg"),

    dict(id="herbal_chicken_soup", yt='藥材雞湯 做法',
         steps=['雞肉汆燙去血水', '與藥材包、老薑加水燉 1 小時', '麵線另鍋快燙撈起', '蒜炒長豆'], name="藥材雞燉湯 + 麵線 + 蒜炒長豆", emoji="🫕", cuisine="中式",
         meal=["lunch", "dinner"], cost=(22, 32),
         ingredients=[("雞肉", 900, "g", "肉類"), ("藥材湯包", 1, "包", "辛香料 / 調味"),
                      ("老薑", 50, "g", "辛香料 / 調味"), ("麵線", 300, "g", "麵 / 主食"),
                      ("長豆", 500, "g", "蔬菜"), ("蒜頭", 20, "g", "辛香料 / 調味")],
         moods=["light", "rich"], weather=["rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="溫補燉湯，雞肉燉到軟爛最適合長輩",
         kid_ok=True, protein="肉", tip="溫補家常，湯頭濃郁", img="herbal_soup.jpg"),

    dict(id="mackerel_tofu_soup", yt='魚頭爐 魚湯 做法',
         steps=['馬鮫魚煎香（湯色更奶白）', '加薑、番茄與熱水煮 15 分鐘', '豆腐入湯，調味', '手工麵燙熟；菠菜清炒'], name="馬鮫魚豆腐湯 + 手工麵 + 清炒菠菜", emoji="🥣", cuisine="中式",
         meal=["lunch", "dinner"], cost=(30, 38),
         ingredients=[("馬鮫魚 (Ikan Tenggiri)", 700, "g", "海鮮"), ("豆腐", 2, "塊", "蛋 / 豆腐"),
                      ("手工麵", 500, "g", "麵 / 主食"), ("菠菜", 500, "g", "蔬菜"),
                      ("薑", 30, "g", "辛香料 / 調味"), ("番茄", 250, "g", "蔬菜")],
         moods=["light", "rich"], weather=["rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="魚肉厚實無細刺，湯麵軟滑易入口",
         kid_ok=True, protein="魚", tip="魚肉厚實，週末升級版", img="mackerel_soup.jpg"),

    dict(id="lotus_pork_soup", yt='蓮藕排骨湯 做法',
         steps=['排骨汆燙去血水', '與蓮藕、薑加水燉 1 小時', '烏冬與白蝦煮成海鮮湯麵', '蒜炒青菜'], name="蓮藕排骨燉湯 + 海鮮烏冬 + 蒜炒青菜", emoji="🍢", cuisine="中式",
         meal=["dinner"], cost=(42, 58), weekend=True,
         ingredients=[("排骨", 700, "g", "肉類"), ("蓮藕", 600, "g", "蔬菜"),
                      ("本地白蝦", 500, "g", "海鮮"), ("烏冬", 600, "g", "麵 / 主食"),
                      ("青菜", 500, "g", "蔬菜"), ("薑", 40, "g", "辛香料 / 調味"),
                      ("蒜頭", 20, "g", "辛香料 / 調味")],
         moods=["rich"], weather=["rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="排骨燉至軟爛、蓮藕粉糯，很適合長輩",
         kid_ok=True, protein="肉", tip="適合家庭聚餐，湯麵一次到位", img="lotus_soup.jpg"),

    # ---------------- 泰式風味 ----------------
    dict(id="pad_krapow", yt='打拋豬 做法',
         steps=['大火炒香蒜末與辣椒', '加豬絞肉炒散至微焦', '加魚露、蠔油、糖調味，關火前拌入九層塔', '配白飯與半熟煎蛋'], name="泰式打拋豬肉飯 + 煎蛋", emoji="🌿", cuisine="泰式",
         meal=["lunch", "dinner"], cost=(18, 25),
         ingredients=[("豬絞肉", 400, "g", "肉類"), ("九層塔", 1, "把", "蔬菜"),
                      ("辣椒", 30, "g", "辛香料 / 調味"), ("蒜頭", 20, "g", "辛香料 / 調味"),
                      ("洋蔥", 75, "g", "蔬菜"), ("雞蛋", 3, "顆", "蛋 / 豆腐"),
                      ("魚露", 1, "瓶", "辛香料 / 調味")],
         moods=["appetite", "easy"], weather=["hot"], spicy=True,
         elderly_ok=False, elderly_note="口味偏辣偏重，長輩同桌建議減辣或另備清淡菜",
         kid_ok=False, protein="肉", tip="泰式經典快手飯", img="pad_krapow.jpg"),

    dict(id="green_curry", yt='泰式綠咖哩雞 做法',
         steps=['熱鍋炒香綠咖哩醬', '加雞肉與椰奶煮熟', '加茄子煮軟，以魚露、糖調味', '起鍋前加九層塔'], name="綠咖哩雞飯", emoji="🍛", cuisine="泰式",
         meal=["lunch", "dinner"], cost=(20, 30),
         ingredients=[("雞腿肉", 500, "g", "肉類"), ("綠咖哩醬", 3, "湯匙", "辛香料 / 調味"),
                      ("椰奶", 400, "ml", "辛香料 / 調味"), ("茄子", 2, "顆", "蔬菜"),
                      ("九層塔", 1, "把", "蔬菜")],
         moods=["rich", "appetite"], weather=["rain", "cool"], spicy=True,
         elderly_ok=False, elderly_note="椰奶咖哩較濃郁，長輩淺嚐即可",
         kid_ok=True, protein="肉", tip="椰香濃郁，配白飯一流", img="green_curry.jpg"),

    dict(id="tom_yum", yt='冬蔭功湯 做法',
         steps=['香茅、南薑、檸檬葉加水煮出香氣', '加蝦、草菇、番茄煮熟', '以魚露、檸檬汁、辣椒醬調味', '試味：要酸、辣、鮮平衡'], name="冬蔭功蝦湯 + 白飯", emoji="🍤", cuisine="泰式",
         meal=["dinner"], cost=(25, 35),
         ingredients=[("大蝦", 500, "g", "海鮮"), ("香茅", 2, "支", "辛香料 / 調味"),
                      ("南薑", 30, "g", "辛香料 / 調味"), ("檸檬葉", 4, "片", "辛香料 / 調味"),
                      ("番茄", 200, "g", "蔬菜"), ("草菇", 100, "g", "蔬菜")],
         moods=["appetite"], weather=["hot", "rain"], spicy=True,
         elderly_ok=False, elderly_note="酸辣湯較刺激，長輩建議另備清湯",
         kid_ok=False, protein="蝦", tip="酸辣鮮香，海鮮控最愛", img="tom_yum.jpg"),

    dict(id="thai_chicken", yt='泰式椒麻雞 做法',
         steps=['雞腿以醬油、魚露、糖醃 20 分鐘', '中火煎至兩面金黃全熟', '切塊配糯米飯', '淋椒麻沾醬（魚露+檸檬汁+辣椒+香菜）'], name="泰式椒麻雞 + 糯米飯", emoji="🍗", cuisine="泰式",
         meal=["lunch", "dinner"], cost=(18, 28),
         ingredients=[("去骨雞腿", 500, "g", "肉類"), ("魚露", 2, "湯匙", "辛香料 / 調味"),
                      ("糯米", 400, "g", "麵 / 主食"), ("蒜頭", 20, "g", "辛香料 / 調味"),
                      ("黃瓜", 200, "g", "蔬菜")],
         moods=["rich"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="沾醬另放，雞肉煎熟切小塊即可",
         kid_ok=True, protein="肉", tip="外酥內嫩，沾醬靈魂", img="thai_chicken.jpg"),

    dict(id="sour_fish_soup", yt='泰式酸辣魚湯 做法',
         steps=['酸子醬加水煮成酸湯底', '加魚片與番茄煮熟', '加秋葵／蘿蔔煮軟，調味', '配米粉上桌'], name="泰式酸辣魚湯 + 米粉", emoji="🐟", cuisine="泰式",
         meal=["lunch", "dinner"], cost=(20, 30),
         ingredients=[("鮮魚片", 500, "g", "海鮮"), ("酸子醬", 2, "湯匙", "辛香料 / 調味"),
                      ("番茄", 200, "g", "蔬菜"), ("秋葵 / 蘿蔔", 300, "g", "蔬菜"),
                      ("米粉", 300, "g", "麵 / 主食"), ("辣椒", 20, "g", "辛香料 / 調味")],
         moods=["appetite", "light"], weather=["hot"], spicy=True,
         elderly_ok=False, elderly_note="酸辣口味重，長輩建議改清湯魚片",
         kid_ok=False, protein="魚", tip="酸辣開胃，天熱必備", img="sour_fish.jpg"),

    dict(id="pad_thai", yt='Pad Thai 泰式炒河粉 做法',
         steps=['熱油炒蛋與蝦', '加泡軟河粉、豆芽、韭菜大火快炒', '以魚露、糖、辣椒粉調味', '起鍋撒花生碎、擠檸檬'], name="泰式炒河粉 (Pad Thai)", emoji="🥡", cuisine="泰式",
         meal=["lunch", "dinner"], cost=(18, 28),
         ingredients=[("河粉", 300, "g", "麵 / 主食"), ("中蝦", 300, "g", "海鮮"),
                      ("豆芽菜", 150, "g", "蔬菜"), ("韭菜", 50, "g", "蔬菜"),
                      ("雞蛋", 2, "顆", "蛋 / 豆腐"), ("花生碎", 50, "g", "辛香料 / 調味")],
         moods=["easy", "rich"], weather=["hot", "rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="河粉軟滑，少放辣椒粉即可",
         kid_ok=True, protein="蝦", tip="一鍋到底，鹹甜涮嘴", img="pad_thai.jpg"),

    dict(id="coconut_chicken_soup", yt='泰式椰奶雞湯 做法',
         steps=['椰奶加黃咖哩粉煮成湯底', '加雞肉煮熟', '加洋蔥、酸菜煮軟調味', '配米粉與檸檬角'], name="椰奶雞湯 + 米粉", emoji="🥥", cuisine="泰式",
         meal=["lunch", "dinner"], cost=(20, 30),
         ingredients=[("雞腿肉", 500, "g", "肉類"), ("椰奶", 400, "ml", "辛香料 / 調味"),
                      ("黃咖哩粉", 2, "湯匙", "辛香料 / 調味"), ("洋蔥", 150, "g", "蔬菜"),
                      ("米粉", 300, "g", "麵 / 主食"), ("酸菜", 100, "g", "蔬菜")],
         moods=["rich", "light"], weather=["rain", "cool"], spicy=False,
         elderly_ok=True, elderly_note="湯頭溫潤不辣，雞肉燉軟適合長輩",
         kid_ok=True, protein="肉", tip="泰北風味，溫潤暖胃", img="coconut_soup.jpg"),
]

# ---------------- 麗都市場海鮮行情（RM / 公斤） ----------------
SEAFOOD_PRICES = [
    ("馬鮫魚", "Ikan Tenggiri (Spanish Mackerel)", "🐠", 28, 36, "肉質厚實、無細刺；煎香、煮湯、釀豆腐魚肉餡"),
    ("甘望魚 / 花池魚", "Ikan Kembung (Indian Mackerel)", "🐟", 12, 18, "產量大、價格親民；亞參煮、油炸、香料烤魚"),
    ("本地白蝦 / 老虎蝦", "Udang", "🦐", 30, 45, "當天捕撈、殼薄肉甜；清蒸、奶油炒、鹽焗"),
    ("紅鰽魚 / 石斑", "Ikan Merah / Kerapu (Grouper)", "🐡", 25, 40, "肉質細嫩鮮美；清蒸、魚頭湯、豆腐湯"),
    ("魷魚", "Sotong", "🦑", 18, 28, "炒、煮咖哩、釀魷魚"),
    ("螃蟹", "Ketam", "🦀", 25, 45, "辣椒蟹、清蒸、粥"),
    ("花蛤", "Lala", "🐚", 12, 18, "炒辣椒、煮湯"),
    ("扇貝", "Scallop", "🥟", 20, 30, "蒜蓉蒸、烤"),
    ("龍蝦", "Lobster", "🦞", 80, 150, "上湯焗、清蒸（節慶加菜）"),
    ("帶子", "Kerang", "🐚", 15, 25, "炒、燒烤"),
]

MARKET_TIPS = [
    "🌅 清晨 6am–9am 到市場，海鮮最新鮮、選擇最多",
    "🔪 可以請攤販幫忙清理魚、去鱗、去內臟、切片",
    "⚖️ 家庭 2–5 人，海鮮買 600g–1kg 最剛好",
    "💬 記得殼價，買多通常有空間可以聊一聊",
    "🧊 海鮮分 2–3 天份量處理並冷藏 / 冷凍",
    "🥬 葉菜類建議一週採買 2 次，更新鮮",
    "🍜 麵條類盡量 2–3 天內使用完",
]

ELDERLY_TIPS = [
    "🍲 優先選擇：清蒸、燉湯、蒸蛋、豆腐類料理",
    "🐟 選無細刺的魚（馬鮫魚、石斑），或先幫長輩挑刺",
    "🧂 少鹽少油，用薑、蔥、香菇提味取代重調味",
    "🥕 食材切小塊、燉軟一點，方便咀嚼吞嚥",
    "🌶️ 避免酸辣重口味，長輩同桌時另備清淡湯品",
]
