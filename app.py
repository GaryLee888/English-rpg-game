import os
import sys
import subprocess
import json
import csv
import random
import time
from datetime import datetime
import pandas as pd
import eng_to_ipa as ipa

# --- 自動環境檢查與安裝模組 ---
def setup_environment():
    required_packages = {
        "streamlit": "streamlit",
        "pandas": "pandas",
        "eng-to-ipa": "eng_to_ipa"
    }
    missing = []
    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
            
    if missing:
        print(f"🔧 偵測到缺少必要套件 {missing}，正在背景自動安裝...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("✅ 安裝完成！正在重新啟動遊戲...")
            os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", sys.argv[0]])
        except Exception as e:
            print(f"❌ 自動安裝失敗: {e}")
            sys.exit(1)

setup_environment()
import streamlit as st

# --- 檔案設定與常數 ---
ADMIN_FILE = "admin_settings.json"
PARENTS_FILE = "parents_db.json"
USERS_FILE = "users_db.json"
SHARE_FILE = "share_codes.json"
FEEDBACK_FILE = "feedbacks.json"
VOCAB_FILES = {
    "國小": "vocab_elementary.csv",
    "國中": "vocab_junior.csv",
    "多益": "vocab_toeic.csv"
}
EMOJI_LIST = ["🎮", "🧸", "🎲", "🧩", "🎯", "🪀", "🪁", "🚂", "🍔", "🍟", "🍕", "🍦", "🍩", "🍫", "🍬", "🍿", "🥤", "🧋", "👑", "🏆", "🥇", "⭐", "💰", "💎", "🐬", "🎬", "🚲", "⚽", "🏀", "🏊", "⛺", "🚀", "📖", "🖍️", "🎨", "🎒"]

CHARACTERS = {
    "電系 (皮丘)": {"stages": [(172, "皮丘"), (25, "皮卡丘"), (26, "雷丘")], "fx": "⚡", "snd_type": "square", "snd_freq": 1200, "snd_drop": 200, "snd_len": 0.15},
    "火系 (小火龍)": {"stages": [(4, "小火龍"), (5, "火恐龍"), (6, "噴火龍")], "fx": "🔥", "snd_type": "sawtooth", "snd_freq": 300, "snd_drop": 50, "snd_len": 0.4},
    "水系 (傑尼龜)": {"stages": [(7, "傑尼龜"), (8, "卡咪龜"), (9, "水箭龜")], "fx": "💦", "snd_type": "sine", "snd_freq": 600, "snd_drop": 100, "snd_len": 0.25},
    "草系 (妙蛙種子)": {"stages": [(1, "妙蛙種子"), (2, "妙蛙草"), (3, "妙蛙花")], "fx": "🍃", "snd_type": "triangle", "snd_freq": 900, "snd_drop": 400, "snd_len": 0.1}
}

HURT_SOUNDS = [
    {"type": "sawtooth", "f1": 150, "f2": 40, "len": 0.3},
    {"type": "square", "f1": 200, "f2": 80, "len": 0.2},
    {"type": "triangle", "f1": 100, "f2": 20, "len": 0.4}
]

BOSS_DATA = [
    (144,"急凍鳥"), (145,"閃電鳥"), (146,"火焰鳥"), (149,"快龍"), (150,"超夢"), (151,"夢幻"),
    (243,"雷公"), (244,"炎帝"), (245,"水君"), (248,"班基拉斯"), (249,"洛奇亞"), (250,"鳳王"), (251,"時拉比"),
    (373,"暴飛龍"), (376,"巨金怪"), (377,"雷吉洛克"), (378,"雷吉艾斯"), (379,"雷吉斯奇魯"),
    (380,"拉帝亞斯"), (381,"拉帝歐斯"), (382,"蓋歐卡"), (383,"固拉多"), (384,"烈空坐"),
    (385,"基拉祈"), (386,"代歐奇希斯"), (445,"烈咬陸鯊"), (480,"由克希"), (481,"艾姆利多"), (482,"亞克諾姆"),
    (483,"帝牙盧卡"), (484,"帕路奇亞"), (485,"席多藍恩"), (486,"雷吉奇卡斯"),
    (487,"騎拉帝納"), (488,"克雷色利亞"), (491,"達克萊伊"), (493,"阿爾宙斯"),
    (494,"比克提尼"), (635,"三首惡龍"), (638,"勾帕路翁"), (639,"代拉基翁"), (640,"畢力吉翁"),
    (641,"龍捲雲"), (642,"雷電雲"), (643,"萊希拉姆"), (644,"捷克羅姆"), (645,"土地雲"), (646,"酋雷姆")
]
BOSSES = [{"name": n, "url": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{i}.gif"} for i, n in BOSS_DATA]

MONSTER_DATA = [
    (10,"綠毛蟲"),(11,"鐵甲蛹"),(12,"巴大蝶"), (13,"獨角蟲"),(14,"鐵殼蛹"),(15,"大針蜂"),
    (16,"波波"),(17,"比比鳥"),(18,"大比鳥"), (19,"小拉達"),(20,"拉達"), (21,"烈雀"),(22,"大嘴雀"),
    (23,"阿柏蛇"),(24,"阿柏怪"), (27,"穿山鼠"),(28,"穿山王"),
    (29,"尼多蘭"),(30,"尼多娜"),(31,"尼多后"), (32,"尼多朗"),(33,"尼多力諾"),(34,"尼多王"),
    (35,"皮皮"),(36,"皮可西"), (37,"六尾"),(38,"九尾"), (39,"胖丁"),(40,"胖可丁"),
    (41,"超音蝠"),(42,"大嘴蝠"),(169,"叉字蝠"),
    (43,"走路草"),(44,"臭臭花"),(45,"霸王花"),(182,"美麗花"),
    (46,"派拉斯"),(47,"派拉斯特"), (48,"毛球"),(49,"摩魯蛾"),
    (50,"地鼠"),(51,"三地鼠"), (52,"喵喵"),(53,"貓老大"),
    (54,"可達鴨"),(55,"哥達鴨"), (56,"猴怪"),(57,"火爆猴"), (58,"卡蒂狗"),(59,"風速狗"),
    (60,"蚊香蝌蚪"),(61,"蚊香君"),(62,"蚊香泳士"),(186,"蚊香蛙皇"),
    (63,"凱西"),(64,"勇基拉"),(65,"胡地"), (66,"腕力"),(67,"豪力"),(68,"怪力"),
    (69,"喇叭芽"),(70,"口呆花"),(71,"大食花"), (72,"瑪瑙水母"),(73,"毒刺水母"),
    (74,"小拳石"),(75,"隆隆石"),(76,"隆隆岩"), (77,"小火馬"),(78,"烈焰馬"),
    (79,"呆呆獸"),(80,"呆殼獸"),(199,"呆呆王"), (81,"小磁怪"),(82,"三合一磁怪"),
    (83,"大蔥鴨"), (84,"嘟嘟"),(85,"嘟嘟利"), (86,"小海獅"),(87,"白海獅"),
    (88,"臭泥"),(89,"臭臭泥"), (90,"大舌貝"),(91,"刺甲貝"),
    (92,"鬼斯"),(93,"鬼斯通"),(94,"耿鬼"), (95,"大岩蛇"),(208,"大鋼蛇"),
    (96,"催眠貘"),(97,"引夢貘人"), (98,"大鉗蟹"),(99,"巨鉗蟹"),
    (100,"霹靂電球"),(101,"頑皮雷彈"), (102,"蛋蛋"),(103,"椰蛋樹"),
    (104,"卡拉卡拉"),(105,"嘎啦嘎啦"), (108,"大舌頭"),
    (109,"瓦斯彈"),(110,"雙彈瓦斯"), (111,"獨角犀牛"),(112,"鑽角犀獸"), (114,"蔓藤怪"),
    (116,"墨海馬"),(117,"海刺龍"),(230,"刺龍王"), (118,"角金魚"),(119,"金魚王"),
    (120,"海星星"),(121,"寶石海星"), (127,"凱羅斯"), (128,"肯泰羅"),
    (129,"鯉魚王"),(130,"暴鯉龍"), (131,"拉普拉斯"), (132,"百變怪"),
    (133,"伊布"),(134,"水伊布"),(135,"雷伊布"),(136,"火伊布"),(196,"太陽伊布"),(197,"月亮伊布"),
    (137,"多邊獸"),(233,"多邊獸Ⅱ"), (143,"卡比獸"),
    (147,"迷你龍"),(148,"哈克龍"),
    (161,"尾立"),(162,"大尾立"), (163,"咕咕"),(164,"貓頭夜鷹"),
    (165,"芭瓢蟲"),(166,"安瓢蟲"), (167,"圓絲蛛"),(168,"阿利多斯"),
    (170,"燈籠魚"),(171,"電燈怪"), (175,"波克比"),(176,"波克基古"),
    (177,"天然雀"),(178,"天然鳥"), (179,"咩利羊"),(180,"茸茸羊"),(181,"電龍"),
    (183,"瑪力露"),(184,"瑪力露麗"), (185,"胡說樹"),
    (187,"毽子草"),(188,"毽子花"),(189,"毽子棉"), (190,"長尾怪手"),
    (191,"向日種子"),(192,"向日花怪"), (193,"陽々瑪"),
    (194,"烏波"),(195,"沼王"), (198,"黑暗鴉"), (200,"夢妖"), (202,"果然翁"),
    (204,"榛果球"),(205,"佛烈托斯"), (206,"土龍弟弟"), (209,"布魯"),(210,"布魯皇"),
    (213,"壺壺"), (214,"赫拉克羅斯"), (216,"熊寶寶"),(217,"圈圈熊"),
    (218,"熔岩蟲"),(219,"熔岩蝸牛"), (220,"小山豬"),(221,"長毛豬"),
    (222,"太陽珊瑚"), (223,"鐵炮魚"),(224,"章魚桶"), (225,"信使鳥"),
    (228,"戴魯比"),(229,"黑魯加"), (231,"小小象"),(232,"頓甲"),
    (235,"圖圖犬"), (236,"巴爾郎"),(237,"戰舞郎"), (241,"大奶罐"),
    (246,"幼基拉斯"),(247,"沙基拉斯")
]
MONSTERS = [{"name": n, "url": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{i}.gif"} for i, n in MONSTER_DATA]

# --- 系統初始化 ---
def load_json(f, default):
    if os.path.exists(f):
        try:
            with open(f, "r", encoding="utf-8") as file: return json.load(file)
        except: pass
    return default

def save_json(f, d):
    with open(f, "w", encoding="utf-8") as file: json.dump(d, file, ensure_ascii=False, indent=2)

def init_system():
    if not os.path.exists(ADMIN_FILE): save_json(ADMIN_FILE, {"password": "1234", "default_hero_limit": 3, "default_bank_limit": 3})
    if not os.path.exists(PARENTS_FILE): save_json(PARENTS_FILE, {})
    if not os.path.exists(USERS_FILE): save_json(USERS_FILE, {})
    if not os.path.exists(SHARE_FILE): save_json(SHARE_FILE, {})
    if not os.path.exists(FEEDBACK_FILE): save_json(FEEDBACK_FILE, [])
    if not os.path.exists(VOCAB_FILES["國小"]): pd.DataFrame({"en": ["apple", "cat", "dog"], "zh": ["蘋果", "貓", "狗"], "hint": ["水果", "動物", "動物"]}).to_csv(VOCAB_FILES["國小"], index=False, encoding="utf-8-sig")
    if not os.path.exists(VOCAB_FILES["國中"]): pd.DataFrame({"en": ["environment", "develop"], "zh": ["環境", "發展"], "hint": ["大自然", "進步"]}).to_csv(VOCAB_FILES["國中"], index=False, encoding="utf-8-sig")
    if not os.path.exists(VOCAB_FILES["多益"]): pd.DataFrame({"en": ["implement", "revenue"], "zh": ["實施", "收入"], "hint": ["執行", "金錢"]}).to_csv(VOCAB_FILES["多益"], index=False, encoding="utf-8-sig")

init_system()

def get_max_hp(level): return min(10, 3 + (level // 5)) 
def get_title(level):
    if level < 3: return "🌱 新手訓練家"
    if level < 7: return "⚔️ 道館挑戰者"
    if level < 12: return "🌟 菁英訓練家"
    if level < 20: return "🔥 四天王候補"
    return "👑 寶可夢大師"

def get_admin(): return load_json(ADMIN_FILE, {})
def save_admin(d): save_json(ADMIN_FILE, d)
def get_parents(): return load_json(PARENTS_FILE, {})
def save_parents(d): save_json(PARENTS_FILE, d)
def get_users(): return load_json(USERS_FILE, {})
def save_users(d): save_json(USERS_FILE, d)
def get_shares(): return load_json(SHARE_FILE, {})
def save_shares(d): save_json(SHARE_FILE, d)

def load_user_data(u_key): 
    d = load_json(f"data_{u_key}.json", {
        "exp": 0, "level": 1, "hero_hp": 3, "medals": 0, "combo": 0, "is_boss_fight": False, "boss_hp": 3, 
        "history": [], "total_questions": 0, "difficulty": "簡單", "trophies": [], "monster_dex": [], 
        "vocab_bank": "國小", "word_stats": {}, "gold": 0, "shield_active": False,
        "last_login_date": "", "login_streak": 0
    })
    if "vocab_bank" not in d or d["vocab_bank"] == "家長自訂": d["vocab_bank"] = "custom_1"
    if "word_stats" not in d: d["word_stats"] = {}
    if "gold" not in d: d["gold"] = 0
    if "shield_active" not in d: d["shield_active"] = False
    if "last_login_date" not in d: d["last_login_date"] = ""
    if "login_streak" not in d: d["login_streak"] = 0
    if "death_count" in d: del d["death_count"]
    if "inventory" not in d: d["inventory"] = {"potion": 0, "shield": 0, "magnifier": 0}
    return d

def save_user_data(u_key, d): save_json(f"data_{u_key}.json", d)
def load_error_log(u_key): return load_json(f"error_{u_key}.json", [])
def save_error_log(u_key, l): save_json(f"error_{u_key}.json", l)
def delete_user(u_key):
    if os.path.exists(f"data_{u_key}.json"): os.remove(f"data_{u_key}.json")
    if os.path.exists(f"error_{u_key}.json"): os.remove(f"error_{u_key}.json")
    users = get_users()
    if u_key in users: del users[u_key]; save_users(users)

def load_csv(f):
    try: return pd.read_csv(f, encoding="utf-8-sig").fillna("").to_dict('records')
    except: return []

EBBINGHAUS_INTERVALS = [0, 60, 600, 86400, 86400*3, 86400*7, 86400*15]

def pick_next_question(v_list, err_log, total_q, word_stats):
    now = time.time()
    valid_err = [w for w in err_log if any(v['en'] == w for v in v_list)]
    if valid_err and (total_q >= 15 or random.random() < 0.3):
        w = random.choice(valid_err)
        for v in v_list:
            if v['en'] == w: return v

    due_words = []
    new_words = []
    
    for v in v_list:
        w = v['en']
        if w not in word_stats: new_words.append(v)
        elif word_stats[w].get("next_review", 0) <= now: due_words.append(v)
            
    if due_words: return random.choice(due_words)
    if new_words: return random.choice(new_words)
    return random.choice(v_list)

def generate_options(c_v, f_list):
    o = [c_v['zh']]
    w = [v['zh'] for v in f_list if v['zh'] != c_v['zh']]
    o.extend(random.sample(w, min(3, max(0, len(w)))))
    while len(o) < 4: o.append("錯誤選項")
    random.shuffle(o)
    return o

# --- 網頁設定與寶可夢主題 CSS ---
st.set_page_config(page_title="寶可夢英文挑戰", page_icon="⚡", layout="wide")

st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.block-container { max-width: 900px; padding-top: 1rem; padding-bottom: 2rem; }
.poke-title-box { background-color: #ffcb05; padding: 20px; border-radius: 15px; border: 5px solid #3c5aa6; text-align: center; margin-bottom: 25px; box-shadow: 0 6px 15px rgba(0,0,0,0.2); }
.poke-title { color: #3c5aa6; margin: 0; font-size: 3.2rem; font-weight: 900; letter-spacing: 2px; text-shadow: 2px 2px 0px #fff, -2px -2px 0px #fff, 2px -2px 0px #fff, -2px 2px 0px #fff; }
.poke-subtitle { color: #e74c3c; font-weight: bold; font-size: 1.2rem; margin-top: 10px; background: white; display: inline-block; padding: 5px 20px; border-radius: 20px; border: 2px solid #e74c3c;}
.status-bar-container { display: flex; flex-wrap: wrap; justify-content: space-around; align-items: center; background-color: #f8f9fa; border-radius: 12px; padding: 10px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.status-item { text-align: center; flex: 1 1 15%; min-width: 60px; padding: 5px; }
.status-label { font-size: 0.8rem; color: #7f8c8d; margin-bottom: 2px; }
.status-value { font-size: 1.2rem; font-weight: bold; color: #2c3e50; }
.arena-bg { position: relative; display: flex; justify-content: space-between; align-items: flex-end; padding: 5%; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.3); margin: 15px 0; min-height: 250px; overflow: hidden; }
.hero-box, .monster-box { width: 40%; text-align: center; z-index: 5; }
.vs-box { width: 20%; text-align: center; z-index: 5; align-self: center; }
.vs-text { color: #f1c40f; font-size: 3rem; font-style: italic; text-shadow: 2px 2px 0 #000; margin:0; }
.hp-badge { font-size: 1.2rem; margin-bottom: 5px; background: rgba(0,0,0,0.4); border-radius: 20px; padding: 2px 10px; display: inline-block; color: #fff; white-space: nowrap; }
.hp-badge-enemy { color: #ff6b6b; }
.monster-name { color:white; font-weight:bold; margin-top:5px; text-shadow: 1px 1px 2px #000; font-size: 1rem;}
.vocab-card { text-align:center; padding: 5%; background: #ffffff; border-radius: 12px; border: 3px solid #3498db; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 10px; }
.vocab-word { color:#2980b9; font-size: 3.5rem; margin: 5px 0; font-weight: 800; word-wrap: break-word;}
.vocab-hint-str { color:#34495e; font-size: 2.5rem; margin: 10px 0; font-weight: bold; letter-spacing: 5px; word-wrap: break-word;}
.dex-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(70px, 1fr)); gap: 12px; text-align: center; padding: 10px 0; }
.dex-item img { width: 100%; max-width: 60px; height: auto; transition: transform 0.2s; }
.dex-item img:hover { transform: scale(1.2); }
.dex-name { font-size: 0.75rem; color: #555; margin-top: 5px; font-weight: bold; }
@media screen and (max-width: 600px) {
    .poke-title { font-size: 2rem; }
    .poke-subtitle { font-size: 0.9rem; }
    .arena-bg { min-height: 160px; padding: 15px 5px; }
    .vs-text { font-size: 1.5rem; }
    .hp-badge { font-size: 0.8rem; padding: 2px 6px; }
    .monster-name { font-size: 0.8rem; }
    .m-fx { font-size: 40px !important; }
    .vocab-word { font-size: 2.5rem; }
    .vocab-hint-str { font-size: 1.8rem; letter-spacing: 3px;}
    .status-value { font-size: 1rem; }
    .dex-grid { grid-template-columns: repeat(auto-fill, minmax(50px, 1fr)); gap: 8px;}
    .dex-name { font-size: 0.6rem; }
}
@keyframes heroDash { 0% { transform: scaleX(-1) translateX(0px); } 30% { transform: scaleX(-1) translateX(-40px); } 100% { transform: scaleX(-1) translateX(0px); } }
@keyframes shakeHurt { 0% { transform: translateX(0); filter: brightness(1); } 20% { transform: translateX(-10px); filter: brightness(2.5) drop-shadow(0 0 25px red); } 40% { transform: translateX(10px); } 60% { transform: translateX(-10px); } 80% { transform: translateX(10px); } 100% { transform: translateX(0); filter: brightness(1); } }
@keyframes monsterDash { 0% { transform: translateX(0px); } 30% { transform: translateX(-40px); } 100% { transform: translateX(0px); } }
@keyframes heroHurt { 0% { transform: scaleX(-1) translateX(0); filter: brightness(1); } 20% { transform: scaleX(-1) translateX(-8px); filter: brightness(0.4) sepia(1) hue-rotate(-50deg) saturate(6); } 40% { transform: scaleX(-1) translateX(8px); } 60% { transform: scaleX(-1) translateX(-8px); } 80% { transform: scaleX(-1) translateX(8px); } 100% { transform: scaleX(-1) translateX(0); filter: brightness(1); } }
@keyframes mBall { 0% { left: 20%; transform: scale(0.5); opacity: 0; } 30% { opacity: 1; transform: scale(1.5); } 70% { left: 70%; transform: scale(2); opacity: 1; } 100% { left: 80%; transform: scale(0.5); opacity: 0; } }
@keyframes heroDead { 0% { transform: scaleX(-1) rotate(0deg); filter: grayscale(0%); } 100% { transform: scaleX(-1) rotate(90deg) translateY(20px); filter: grayscale(100%); } }
@keyframes healFx { 0% { filter: brightness(1) drop-shadow(0 0 0px #2ecc71); } 50% { filter: brightness(1.5) drop-shadow(0 0 20px #2ecc71); } 100% { filter: brightness(1) drop-shadow(0 0 0px #2ecc71); } }
.m-fx { position: absolute; top: 40%; font-size: 60px; animation: mBall 0.7s ease-in-out forwards; z-index: 10; }
</style>
""", unsafe_allow_html=True)

st.components.v1.html("""<script>
if (!window.parent.gameAudioCtx) {
    const AudioContext = window.parent.AudioContext || window.parent.webkitAudioContext;
    if (AudioContext) { window.parent.gameAudioCtx = new AudioContext(); }
}
const unlockAudio = function() { if (window.parent.gameAudioCtx && window.parent.gameAudioCtx.state === 'suspended') window.parent.gameAudioCtx.resume(); };
document.addEventListener('click', unlockAudio, true); document.addEventListener('touchstart', unlockAudio, true);
if(window.parent && window.parent.document) { window.parent.document.addEventListener('click', unlockAudio, true); window.parent.document.addEventListener('touchstart', unlockAudio, true); }
</script>""", height=0)

if 'page' not in st.session_state: st.session_state.page = 'login'
if 'text_input_field' not in st.session_state: st.session_state.text_input_field = ""
if 'play_auto_audio' not in st.session_state: st.session_state.play_auto_audio = True
if 'magnifier_active' not in st.session_state: st.session_state.magnifier_active = False

# ==================== 登入大廳 ====================
if st.session_state.page == 'login':
    st.markdown("""
    <div class="poke-title-box">
        <h1 class="poke-title">⚡ 寶可夢英文挑戰 ⚡</h1>
        <div class="poke-subtitle">打怪、進化、抓寶！成為英文大師！</div>
    </div>
    """, unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🎒 訓練家遊玩登入", "👨‍👩‍👧 家長控制台", "👑 GM 管理中心"])
    
    with t1:
        st.subheader("選擇您的家庭與訓練家")
        parents = get_parents()
        if not parents: st.info("目前還沒有家庭建立帳號喔！請先請家長到「家長控制台」註冊。")
        else:
            family_input = st.text_input("1️⃣ 請輸入您的家長 (家庭) 帳號", placeholder="輸入後按下 Enter 鍵確認...")
            if family_input:
                if family_input in parents:
                    users = get_users()
                    family_heroes = {k: v for k, v in users.items() if v.get("parent") == family_input}
                    
                    if not family_heroes: st.warning("這個家庭還沒有建立訓練家帳號，請家長先登入控制台建立喔！")
                    else:
                        hero_display = {k: v["name"] for k, v in family_heroes.items()}
                        sel_hero_key = st.selectbox("2️⃣ 選擇你的訓練家", list(hero_display.keys()), format_func=lambda x: hero_display[x])
                        hero_pin = st.text_input("3️⃣ 輸入專屬密碼 (PIN)", type="password", placeholder="預設為 0000")
                        
                        if st.button("🚀 出發冒險！", type="primary", use_container_width=True):
                            if hero_pin == users[sel_hero_key].get("pin", "0000"):
                                init_data = load_user_data(sel_hero_key)
                                today_str = str(datetime.now().date())
                                last_date = init_data.get("last_login_date", "")
                                if last_date != today_str:
                                    try:
                                        delta = (datetime.strptime(today_str, "%Y-%m-%d") - datetime.strptime(last_date, "%Y-%m-%d")).days
                                        if delta == 1: init_data["login_streak"] = init_data.get("login_streak", 0) + 1
                                        else: init_data["login_streak"] = 1
                                    except: init_data["login_streak"] = 1
                                    
                                    bonus_gold = min(50, init_data["login_streak"] * 5)
                                    init_data["gold"] = init_data.get("gold", 0) + bonus_gold
                                    init_data["last_login_date"] = today_str
                                    init_data["history"].append(f"{datetime.now().strftime('%m-%d %H:%M')} 連續登入 {init_data['login_streak']} 天！獲得 {bonus_gold} G")
                                    save_user_data(sel_hero_key, init_data)
                                    st.session_state.show_streak = f"🔥 連續冒險 {init_data['login_streak']} 天！獲得 {bonus_gold} 枚金幣！"
                                
                                st.session_state.current_user_key = sel_hero_key
                                st.session_state.current_parent = family_input
                                st.session_state.game_data = init_data
                                st.session_state.error_log = load_error_log(sel_hero_key)
                                st.session_state.text_input_field = ""
                                st.session_state.play_auto_audio = True
                                st.session_state.page = 'game'; st.rerun()
                            else: st.error("❌ 密碼錯誤！請確認密碼是否正確。")
                else: st.error("找不到這個家庭帳號，請確認輸入是否正確。")

    with t2:
        colA, colB = st.columns(2)
        with colA:
            st.subheader("家長登入")
            l_acc = st.text_input("家長帳號", key="l_acc")
            l_pwd = st.text_input("密碼", type="password", key="l_pwd")
            if st.button("登入", use_container_width=True):
                p_db = get_parents()
                if l_acc in p_db and p_db[l_acc]["password"] == l_pwd:
                    st.session_state.current_parent = l_acc
                    st.session_state.page = 'parent'; st.rerun()
                else: st.error("帳號或密碼錯誤！")
        with colB:
            st.subheader("註冊新家長帳號")
            r_acc = st.text_input("設定帳號 (不可更改)", key="r_acc")
            r_pwd = st.text_input("設定密碼", type="password", key="r_pwd")
            if st.button("註冊", use_container_width=True):
                p_db = get_parents()
                if not r_acc.strip() or not r_pwd.strip(): st.error("帳號密碼不能為空！")
                elif r_acc in p_db: st.error("帳號已存在！")
                else:
                    p_db[r_acc] = {
                        "password": r_pwd, "hero_limit": None, "bank_limit": None,
                        "rewards": [{"reward": "週末多玩 30 分鐘 Switch", "cost_medals": 1, "icon": "🎮"}],
                        "store_prices": {"potion": 50, "shield": 100, "magnifier": 30},
                        "custom_banks": [{"id": "1", "name": "預設自建字庫"}]
                    }
                    save_parents(p_db)
                    st.success("註冊成功！請由左側登入。")

    with t3:
        st.subheader("系統管理員登入")
        admin_db = get_admin()
        gm_pwd = st.text_input("輸入 GM 密碼", type="password", key="gm_pwd")
        if st.button("GM 登入", use_container_width=True):
            if gm_pwd == admin_db["password"]: st.session_state.page = 'admin'; st.rerun()
            else: st.error("密碼錯誤！")

# ==================== 遊戲主畫面 ====================
elif st.session_state.page == 'game':
    u_key = st.session_state.current_user_key
    u_data = st.session_state.game_data
    parent_id = st.session_state.current_parent
    p_db = get_parents()
    
    if 'show_streak' in st.session_state:
        st.toast(st.session_state.show_streak, icon="🔥")
        del st.session_state.show_streak
    
    diff = u_data.get('difficulty', "簡單")
    diff_multi = {"簡單": 1, "中等": 2, "困難": 3}.get(diff, 1)

    users = get_users()
    hero_name = users[u_key]["name"]
    char_d = CHARACTERS[users[u_key]['character']]
    
    stage_idx = 0 if u_data['level'] < 5 else (1 if u_data['level'] < 10 else 2)
    hero_img_id, hero_img_name = char_d["stages"][stage_idx]
    hero_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{hero_img_id}.gif"

    bank_id = u_data.get('vocab_bank', '國小')
    bank_name = bank_id
    if bank_id.startswith("custom_"):
        cb_id = bank_id.split("_")[1]
        v_file = f"vocab_custom_{parent_id}_{cb_id}.csv"
        if not os.path.exists(v_file): v_list = [{"en": "apple", "zh": "蘋果 (請家長至控制台新增單字)", "hint": "預設單字"}]
        else: v_list = load_csv(v_file)
        bank_name = next((b["name"] for b in p_db[parent_id].get("custom_banks", []) if b["id"] == cb_id), "自訂字庫")
    else:
        v_file = VOCAB_FILES.get(bank_id, VOCAB_FILES["國小"])
        v_list = load_csv(v_file) or [{"en": "hero", "zh": "英雄", "hint": ""}]
    
    r_list = p_db.get(parent_id, {}).get("rewards", [])
    store_prices = p_db.get(parent_id, {}).get("store_prices", {"potion": 50, "shield": 100, "magnifier": 30})
    vol = 0.8

    if 'current_monster' not in st.session_state: st.session_state.current_monster = random.choice(MONSTERS)
    if 'action_anim' not in st.session_state: st.session_state.action_anim = None
    if 'current_vocab' not in st.session_state: 
        st.session_state.current_vocab = pick_next_question(v_list, st.session_state.error_log, u_data['total_questions'], u_data['word_stats'])
        st.session_state.current_options = generate_options(st.session_state.current_vocab, v_list)
    if 'force_learning' not in st.session_state: st.session_state.force_learning = False
    
    c_w = st.session_state.current_vocab
    max_hp = get_max_hp(u_data['level'])

    def process_ans(s):
        st.session_state.play_auto_audio = True 
        st.session_state.text_input_field = ""
        st.session_state.magnifier_active = False 
        u_data['total_questions'] += 1 
        word = c_w['en']
        
        if s == c_w['zh']:
            stats = u_data['word_stats'].setdefault(word, {"level": 0, "next_review": 0})
            stats["level"] = min(len(EBBINGHAUS_INTERVALS)-1, stats["level"] + 1)
            stats["next_review"] = time.time() + EBBINGHAUS_INTERVALS[stats["level"]]
            
            u_data['combo'] += 1
            u_data['gold'] += 10 
            
            if word in st.session_state.error_log:
                st.session_state.error_log.remove(word)
                save_error_log(u_key, st.session_state.error_log)
                if not st.session_state.error_log: u_data['total_questions'] = 0
                    
            if u_data.get('is_boss_fight', False):
                u_data['boss_hp'] -= 1
                u_data['exp'] += (10 * diff_multi) 
                if u_data['boss_hp'] <= 0:
                    u_data['medals'] += (1 * diff_multi) 
                    u_data['gold'] += 50 
                    u_data['is_boss_fight'] = False
                    u_data['combo'] = 0 
                    if st.session_state.current_boss['name'] not in u_data.get('trophies', []): u_data['trophies'].append(st.session_state.current_boss['name'])
                    if 'current_boss' in st.session_state: del st.session_state.current_boss
                    st.session_state.action_anim = 'boss_defeat'
                else: st.session_state.action_anim = 'attack'
            else:
                u_data['exp'] += (5 * diff_multi) 
                if st.session_state.current_monster['name'] not in u_data.get('monster_dex', []): u_data.setdefault('monster_dex', []).append(st.session_state.current_monster['name'])
                st.session_state.action_anim = 'attack'
                st.session_state.current_monster = random.choice(MONSTERS)
                if u_data['combo'] >= 10 and not u_data.get('is_boss_fight', False):
                    u_data['is_boss_fight'] = True
                    u_data['boss_hp'] = 3
            
            if (u_data['exp'] // 100) + 1 > u_data['level']:
                u_data['level'] = (u_data['exp'] // 100) + 1
                u_data['hero_hp'] = get_max_hp(u_data['level']) 
        else:
            stats = u_data['word_stats'].setdefault(word, {"level": 0, "next_review": 0})
            stats["level"] = max(0, stats["level"] - 1)
            stats["next_review"] = time.time()
            
            u_data['combo'] = 0 
            if word not in st.session_state.error_log:
                st.session_state.error_log.append(word)
                save_error_log(u_key, st.session_state.error_log)
                
            if u_data.get('shield_active', False):
                u_data['shield_active'] = False
                st.session_state.action_anim = 'shield_block'
            else:
                u_data['hero_hp'] -= 1
                if u_data['hero_hp'] <= 0:
                    if u_data['level'] > 1:
                        u_data['level'] -= 1
                        st.session_state.level_dropped = True
                    else:
                        st.session_state.level_dropped = False
                        
                    u_data['exp'] = (u_data['level'] - 1) * 100
                    u_data['hero_hp'] = get_max_hp(u_data['level'])
                    if u_data.get('is_boss_fight', False): u_data['boss_hp'] = 3
                    st.session_state.action_anim = 'dead'
                else: st.session_state.action_anim = 'hurt'
        save_user_data(u_key, u_data)

    def vk_submit():
        ans = st.session_state.get("text_input_field", "").strip()
        if not ans: return
        if ans.lower() == c_w['en'].lower(): process_ans(c_w['zh'])
        else: process_ans("WRONG_ANSWER")

    st.button("隱藏送出按鈕", on_click=vk_submit, key="hidden_submit_btn")

    # --- 側邊欄 ---
    with st.sidebar:
        st.subheader("🏪 家族獎勵兌換")
        for r in r_list:
            if st.button(f"{r['icon']} {r['reward']} (需 {r['cost_medals']} 勳章)", use_container_width=True):
                if u_data['medals'] >= int(r['cost_medals']):
                    u_data['medals'] -= int(r['cost_medals'])
                    u_data['history'].append(f"{datetime.now().strftime('%m-%d %H:%M')} 兌換 {r['reward']}")
                    save_user_data(u_key, u_data); st.success(f"🎉 兌換成功！"); st.rerun()
                else: st.error("勳章不足！")
                
        st.markdown("---")
        st.subheader("🎁 我的兌換紀錄")
        if u_data.get('history'):
            with st.expander("查看所有紀錄", expanded=False):
                for item in reversed(u_data['history']): st.markdown(f"- {item}")
        else: st.caption("尚未兌換任何獎勵。")

        st.markdown("---")
        if st.button("🚪 返回大廳", use_container_width=True): st.session_state.page = 'login'; st.rerun()

    # --- 頂端狀態列 ---
    hero_title = get_title(u_data['level'])
    st.markdown(f"""
    <div class="status-bar-container">
        <div class="status-item"><div class="status-label">{hero_title}</div><div class="status-value">{hero_name}</div></div>
        <div class="status-item"><div class="status-label">🛡️ 等級</div><div class="status-value">Lv. {u_data['level']}</div></div>
        <div class="status-item"><div class="status-label">🔥 連擊</div><div class="status-value">{u_data['combo']} / 10</div></div>
        <div class="status-item"><div class="status-label">🎖️ 勳章</div><div class="status-value">{u_data['medals']}</div></div>
        <div class="status-item"><div class="status-label">💰 金幣</div><div class="status-value">{u_data['gold']}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # --- 🏪 道具商店「一鍵買＆用」 ---
    st.markdown("<hr style='margin: 5px 0;'><div style='text-align:center; font-weight:bold; color:#7f8c8d; margin-bottom:10px;'>🏪 道具商店 (點擊扣除金幣立即發動)</div>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    
    if c_btn1.button(f"🧪 藥水 ({store_prices['potion']}G)", use_container_width=True, disabled=u_data['hero_hp']>=max_hp):
        if u_data['gold'] >= store_prices['potion']:
            u_data['gold'] -= store_prices['potion']
            u_data['hero_hp'] = min(max_hp, u_data['hero_hp'] + 1)
            st.session_state.action_anim = 'heal'
            save_user_data(u_key, u_data); st.rerun()
        else: st.error("金幣不足！")
            
    if c_btn2.button(f"🛡️ 護盾 ({store_prices['shield']}G)", use_container_width=True, disabled=u_data.get('shield_active', False)):
        if u_data['gold'] >= store_prices['shield']:
            u_data['gold'] -= store_prices['shield']
            u_data['shield_active'] = True
            save_user_data(u_key, u_data); st.rerun()
        else: st.error("金幣不足！")
            
    if c_btn3.button(f"🔍 放大鏡 ({store_prices['magnifier']}G)", use_container_width=True, disabled=st.session_state.magnifier_active):
        if u_data['gold'] >= store_prices['magnifier']:
            u_data['gold'] -= store_prices['magnifier']
            st.session_state.magnifier_active = True
            if diff == '簡單':
                correct_ans = c_w['zh']
                wrong_indices = [i for i, opt in enumerate(st.session_state.current_options) if opt != correct_ans and opt != "❌"]
                if len(wrong_indices) >= 2:
                    to_remove = random.sample(wrong_indices, 2)
                    for i in to_remove: st.session_state.current_options[i] = "❌"
            save_user_data(u_key, u_data); st.rerun()
        else: st.error("金幣不足！")

    # --- 冒險圖鑑 ---
    with st.expander(f"📖 寶可夢圖鑑 (題庫: {bank_name} | 收集: {len(u_data.get('monster_dex', []))}/{len(MONSTERS)} | 傳說: {len(u_data.get('trophies', []))}/{len(BOSSES)})"):
        d_tab1, d_tab2 = st.tabs(["🏆 傳說神獸", "👾 已收集寶可夢"])
        with d_tab1:
            if u_data.get('trophies'):
                boss_dict = {b['name']: b['url'] for b in BOSSES}
                html_dex = '<div class="dex-grid">'
                for t_name in u_data['trophies']:
                    if t_name in boss_dict: html_dex += f'<div class="dex-item"><img src="{boss_dict[t_name]}"><div class="dex-name">{t_name}</div></div>'
                html_dex += '</div>'; st.markdown(html_dex, unsafe_allow_html=True)
            else: st.write("尚未收集到神獸。")
        with d_tab2:
            if u_data.get('monster_dex'):
                mon_dict = {m['name']: m['url'] for m in MONSTERS}
                html_dex = '<div class="dex-grid">'
                for m_name in u_data['monster_dex']:
                    if m_name in mon_dict: html_dex += f'<div class="dex-item"><img src="{mon_dict[m_name]}"><div class="dex-name">{m_name}</div></div>'
                html_dex += '</div>'; st.markdown(html_dex, unsafe_allow_html=True)
            else: st.write("尚未收集到寶可夢。")
    
    scale_factor = 1 + min(u_data['medals'] * 0.1, 2.0)
    h_width = int(100 * scale_factor)

    anim = st.session_state.action_anim
    h_s = f"width: {h_width}%; max-width: 250px; transform: scaleX(-1); image-rendering: pixelated; transition: width 0.5s;"
    
    if u_data.get('shield_active', False): h_s += " filter: drop-shadow(0 0 15px #3498db) brightness(1.2);"
    
    m_s = "width: 100%; max-width: 180px; image-rendering: pixelated;"
    fx_html = ""
    audio_js = ""

    # --- 戰鬥與道具特效/音效處理 ---
    if anim == 'attack':
        h_s += " animation: heroDash 0.7s ease-in-out;"
        m_s += " animation: shakeHurt 0.7s ease-in-out 0.2s;"
        fx_html = f'<div class="m-fx">{char_d["fx"]}</div>'
        audio_js = f"""<script>
        let ctx = window.parent.gameAudioCtx;
        if(ctx) {{
            if(ctx.state === 'suspended') ctx.resume();
            let osc = ctx.createOscillator(); let gain = ctx.createGain();
            osc.type = '{char_d["snd_type"]}'; osc.frequency.setValueAtTime({char_d["snd_freq"]}, ctx.currentTime); osc.frequency.exponentialRampToValueAtTime({char_d["snd_drop"]}, ctx.currentTime + {char_d["snd_len"]});
            gain.gain.setValueAtTime(0.8 * 0.25, ctx.currentTime); gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + {char_d["snd_len"]});
            osc.connect(gain); gain.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime + {char_d["snd_len"]});
        }}
        </script>"""
    elif anim == 'hurt':
        m_s += " animation: monsterDash 0.7s ease-in-out;"
        h_s += " animation: heroHurt 0.7s ease-in-out 0.2s;"
        h_snd = random.choice(HURT_SOUNDS)
        audio_js = f"""<script>
        let ctx = window.parent.gameAudioCtx;
        if(ctx) {{
            if(ctx.state === 'suspended') ctx.resume();
            let osc = ctx.createOscillator(); let gain = ctx.createGain();
            osc.type = '{h_snd["type"]}'; osc.frequency.setValueAtTime({h_snd["f1"]}, ctx.currentTime); osc.frequency.exponentialRampToValueAtTime({h_snd["f2"]}, ctx.currentTime + {h_snd["len"]});
            gain.gain.setValueAtTime(0.8 * 0.25, ctx.currentTime); gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + {h_snd["len"]});
            osc.connect(gain); gain.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime + {h_snd["len"]});
        }}
        </script>"""
    elif anim == 'shield_block':
        m_s += " animation: monsterDash 0.7s ease-in-out;"
        h_s += " animation: heroDash 0.5s ease-in-out 0.2s;"
        audio_js = f"""<script>
        let ctx = window.parent.gameAudioCtx;
        if(ctx) {{
            if(ctx.state === 'suspended') ctx.resume();
            let osc = ctx.createOscillator(); let gain = ctx.createGain();
            osc.type = 'sine'; osc.frequency.setValueAtTime(800, ctx.currentTime); osc.frequency.linearRampToValueAtTime(1200, ctx.currentTime + 0.3);
            gain.gain.setValueAtTime(0.8 * 0.25, ctx.currentTime); gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
            osc.connect(gain); gain.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime + 0.3);
        }}
        </script>"""
    elif anim == 'dead':
        h_s += " animation: heroDead 1s forwards;"
        audio_js = f"""<script>
        let ctx = window.parent.gameAudioCtx;
        if(ctx) {{
            if(ctx.state === 'suspended') ctx.resume();
            let osc = ctx.createOscillator(); let gain = ctx.createGain();
            osc.type = 'sawtooth'; osc.frequency.setValueAtTime(300, ctx.currentTime); osc.frequency.linearRampToValueAtTime(50, ctx.currentTime + 1.5);
            gain.gain.setValueAtTime(0.8 * 0.25, ctx.currentTime); gain.gain.linearRampToValueAtTime(0.01, ctx.currentTime + 1.5);
            osc.connect(gain); gain.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime + 1.5);
        }}
        </script>"""
    elif anim == 'heal':
        h_s += " animation: healFx 1s ease-in-out;"
        audio_js = f"""<script>
        let ctx = window.parent.gameAudioCtx;
        if(ctx) {{
            if(ctx.state === 'suspended') ctx.resume();
            let osc = ctx.createOscillator(); let gain = ctx.createGain();
            osc.type = 'sine'; osc.frequency.setValueAtTime(400, ctx.currentTime); osc.frequency.exponentialRampToValueAtTime(800, ctx.currentTime + 0.5);
            gain.gain.setValueAtTime(0, ctx.currentTime); gain.gain.linearRampToValueAtTime(0.4, ctx.currentTime + 0.1); gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
            osc.connect(gain); gain.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime + 0.5);
        }}
        </script>"""

    is_boss = u_data.get('is_boss_fight', False)
    h_hp = u_data['hero_hp']

    if is_boss:
        if 'current_boss' not in st.session_state: st.session_state.current_boss = random.choice(BOSSES)
        e_n = st.session_state.current_boss['name']
        e_u = st.session_state.current_boss['url']
        e_hp = u_data.get('boss_hp', 3)
        m_hp = 3
        bg_s = "background: linear-gradient(135deg, #2b0b0f 0%, #4a0911 100%); border: 4px solid #ff4500;"
        m_s = m_s.replace("180px", "260px")
    else:
        enemy = st.session_state.current_monster
        e_n = enemy['name']
        e_u = enemy['url']
        e_hp = 1
        m_hp = 1
        bg_s = "background: linear-gradient(135deg, #2980b9 0%, #6dd5fa 100%); border: 4px solid #fff;"

    arena_html = (
        f'<div class="arena-bg" style="{bg_s}">'
        f'{fx_html}'
        f'<div class="hero-box">'
        f'<div class="hp-badge">{"❤️"*h_hp}{"🖤"*(max_hp-h_hp)}</div><br>'
        f'<img src="{hero_url}" style="{h_s}">'
        f'</div>'
        f'<div class="vs-box"><h1 class="vs-text">VS</h1></div>'
        f'<div class="monster-box">'
        f'<div class="hp-badge hp-badge-enemy">{"🩸"*e_hp}{"🖤"*(m_hp-e_hp)}</div><br>'
        f'<img src="{e_u}" style="{m_s}">'
        f'<div class="monster-name">{e_n}</div>'
        f'</div></div>'
    )
    
    st.markdown(arena_html, unsafe_allow_html=True)
    if audio_js: st.components.v1.html(audio_js, height=0)

    if anim:
        if anim == 'attack': st.success(f"💥 命中！獲得 {5 * diff_multi} EXP 與 10 G！")
        elif anim == 'heal': st.success("🧪 喝下生命藥水，生命值恢復了！")
        elif anim == 'shield_block': st.info("🛡️ 神聖護盾為你擋下了一次致命傷害！")
        elif anim == 'hurt': st.error("🩸 遭受攻擊！連擊中斷！")
        elif anim == 'boss_defeat': st.balloons(); st.success(f"🎊 擊敗傳說寶可夢！獲得 {10 * diff_multi} EXP、50 G 與 {1 * diff_multi} 枚勳章！")
        elif anim == 'dead': 
            if st.session_state.get('level_dropped', False): st.error("😭 夥伴寶可夢不支倒地... (等級下降 1 級，經驗值重置！)")
            else: st.error("😭 夥伴寶可夢不支倒地... (已經是最低等級 Lv.1 囉！)")
        time.sleep(1.8)
        
        st.session_state.action_anim = None
        st.session_state.level_dropped = False 
        if anim == 'hurt' or anim == 'dead': st.session_state.force_learning = True
        else:
            st.session_state.current_vocab = pick_next_question(v_list, st.session_state.error_log, u_data['total_questions'], u_data['word_stats'])
            st.session_state.current_options = generate_options(st.session_state.current_vocab, v_list)
            st.session_state.play_auto_audio = True
            st.session_state.text_input_field = ""
            st.session_state.magnifier_active = False 
        st.rerun()

    else:
        opts = st.session_state.current_options
        ipa_txt = ipa.convert(c_w['en'])
        ipa_d = f"[{ipa_txt}]" if ipa_txt and '*' not in ipa_txt else ""
        rev = '<span style="background: #e74c3c; color: white; padding: 2px 8px; border-radius: 10px; font-size: 14px; vertical-align: top;">⚠️ 復仇題</span>' if c_w['en'] in st.session_state.error_log else ''
        
        # --- 答錯模式 ---
        if st.session_state.force_learning:
            v_html = (
                f'<div class="vocab-card" style="background: #fff5f5; border-color: #e74c3c;">'
                f'<h3 style="margin:0; color:#c0392b; font-size: 1.2rem;">❌ 答錯了！請跟著唸 3 次正確答案！</h3>'
                f'<div class="vocab-word" style="color:#e74c3c;">{c_w["en"]} = {c_w["zh"]}</div>'
                f'<h3 style="color:#e67e22; margin:0 0 15px 0; font-family: monospace; font-size: 1.5rem;">{ipa_d}</h3>'
                f'</div>'
            )
            st.markdown(v_html, unsafe_allow_html=True)
            
            js_force = f"""
            <div style="text-align:center; margin-bottom: 20px;">
                <button id="tts-btn" onclick="window.playForce()" style="background-color: #e74c3c; color: white; border: none; padding: 15px 30px; font-size: 18px; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 90%; max-width: 400px; font-weight: bold; animation: pulse 2s infinite;">
                    🔊 準備播放... (若無聲請手動點擊)
                </button>
            </div>
            <style>@keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.02); }} 100% {{ transform: scale(1); }} }}</style>
            <script>
                setTimeout(() => {{
                    const btns = window.parent.document.querySelectorAll('button');
                    btns.forEach(b => {{ if(b.innerText.includes('繼續冒險')) {{ b.style.display = 'none'; window.parent.continueQuestBtn = b; }} }});
                }}, 100);

                let playCount = 0;
                let isSpeaking = false;
                let timeoutId = null;

                window.playForce = function() {{
                    if (isSpeaking) return;
                    playCount = 0;
                    clearTimeout(timeoutId);
                    speakWord();
                }};

                function speakWord() {{
                    let btn = document.getElementById('tts-btn');
                    if (!btn) return;
                    
                    if (playCount >= 3) {{
                        btn.innerText = "✅ 已完成 3 次！請點下方按鈕繼續";
                        btn.style.backgroundColor = "#27ae60";
                        btn.style.animation = "none";
                        if(window.parent.continueQuestBtn) window.parent.continueQuestBtn.style.display = 'inline-flex';
                        return;
                    }}

                    if (window.speechSynthesis) window.speechSynthesis.cancel();
                    let msg = new SpeechSynthesisUtterance("{c_w['en']}"); 
                    msg.lang = 'en-US'; msg.rate = 0.85; msg.volume = 0.8;

                    let started = false; let ended = false;
                    msg.onstart = function() {{ started = true; isSpeaking = true; btn.innerText = "🔊 播放中，請跟著唸... (" + (playCount + 1) + "/3)"; btn.style.animation = "none"; }};
                    msg.onend = function() {{
                        if (ended) return; 
                        ended = true; isSpeaking = false; playCount++;
                        if (playCount < 3) {{
                            btn.innerText = "⏳ 停頓 2 秒... (" + playCount + "/3)";
                            timeoutId = setTimeout(speakWord, 2000); 
                        }} else speakWord(); 
                    }};

                    setTimeout(() => {{
                        if (!started && playCount === 0) {{
                            isSpeaking = false; btn.innerText = "👉 手機限制：請點我開始播放"; btn.style.animation = "pulse 1.5s infinite";
                        }} else if (started && !ended) msg.onend();
                    }}, 3500);

                    window.speechSynthesis.speak(msg);
                }}
                setTimeout(window.playForce, 500);
            </script>
            """
            st.components.v1.html(js_force, height=80)
            
            if st.button("💪 我記住了！繼續冒險！", use_container_width=True, type="primary"):
                st.session_state.force_learning = False
                st.session_state.play_auto_audio = True
                st.session_state.text_input_field = ""
                st.session_state.current_vocab = pick_next_question(v_list, st.session_state.error_log, u_data['total_questions'], u_data['word_stats'])
                st.session_state.current_options = generate_options(st.session_state.current_vocab, v_list)
                st.rerun()

        # --- 正常出題模式 ---
        else:
            if u_data['total_questions'] >= 20 and st.session_state.error_log: st.warning("🔥 累積滿 20 題！進入強制錯題複習模式！")
                
            v_html = f'<div class="vocab-card"><h3 style="margin:0; color:#7f8c8d; font-size: 1.2rem;">✨ 詠唱單字 ✨ {rev}</h3>'
            if diff == '簡單':
                v_html += f'<div class="vocab-word">{c_w["en"]}</div><h3 style="color:#e67e22; margin:0 0 15px 0; font-family: monospace; font-size: 1.5rem;">{ipa_d}</h3>'
                if c_w.get('hint'): v_html += f'<p style="color: #16a085; font-size: 1rem; margin: 0; background: #e8f8f5; padding: 8px; border-radius: 5px; font-weight: bold;">💡 提示：{c_w["hint"]}</p>'
            elif diff == '中等' or diff == '困難':
                word_en = c_w['en']
                w_len = len(word_en)
                
                if st.session_state.magnifier_active:
                    reveal_count = 1
                    r = random.Random(word_en)
                    indices = sorted(r.sample(range(w_len), reveal_count))
                else:
                    if diff == '中等':
                        if w_len <= 3: indices = [w_len // 2]
                        else:
                            N = (w_len - 1) // 3 + 1
                            indices = [int(i * (w_len - 1) / (N - 1) + 0.5) for i in range(N)]
                    else:
                        indices = []
                        
                hint_chars = [char if (i in indices or char in [' ', '-']) else '_' for i, char in enumerate(word_en)]
                hint_str = " ".join(hint_chars)
                v_html += f'<h1 style="color:#2980b9; font-size: 1.8rem; margin: 10px 0; font-weight: 800;">{c_w["zh"]}</h1>'
                v_html += f'<div class="vocab-hint-str">{hint_str}</div><h3 style="color:#e67e22; margin:0 0 10px 0; font-family: monospace; font-size: 1rem;">請拼出對應的英文單字</h3>'
            
            v_html += '</div>'
            st.markdown(v_html, unsafe_allow_html=True)
            
            auto_script = "setTimeout(window.playNormal, 500);" if st.session_state.play_auto_audio else ""
            st.session_state.play_auto_audio = False 
            
            btn_html = f"""
            <div style="text-align:center; margin-bottom: 20px;">
                <button id="normal-tts-btn" onclick="window.playNormal()" style="background-color: #3498db; color: white; border: none; padding: 10px 25px; font-size: 16px; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 80%; max-width: 300px; animation: pulse 2s infinite;">
                    🔊 準備出題... (若無聲請點擊解鎖)
                </button>
            </div>
            <style>@keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}</style>
            <script>
                setTimeout(() => {{
                    const answerDiv = window.parent.document.getElementById('answer-zone');
                    if (answerDiv) {{ answerDiv.style.opacity = '0.3'; answerDiv.style.pointerEvents = 'none'; }}
                }}, 100);

                let isSpeaking = false;
                let loopTimeout = null;

                window.playNormal = function() {{ 
                    if (isSpeaking) return;
                    clearTimeout(loopTimeout);
                    if (window.speechSynthesis) window.speechSynthesis.cancel();
                    
                    let msg = new SpeechSynthesisUtterance("{c_w['en']}"); 
                    msg.lang = 'en-US'; msg.rate = 0.9; msg.volume = 0.8; 
                    
                    let started = false; let ended = false;

                    msg.onstart = function() {{
                        started = true; isSpeaking = true;
                        document.getElementById('normal-tts-btn').innerText = "🔊 播放中...";
                        document.getElementById('normal-tts-btn').style.animation = "none";
                    }};

                    msg.onend = function() {{
                        if(ended) return;
                        ended = true; isSpeaking = false;
                        document.getElementById('normal-tts-btn').innerText = "🔊 播放 / 重聽單字";
                        
                        const answerDiv = window.parent.document.getElementById('answer-zone');
                        if (answerDiv) {{ answerDiv.style.opacity = '1'; answerDiv.style.pointerEvents = 'auto'; }}
                        
                        loopTimeout = setTimeout(window.playNormal, 2000);
                    }};

                    setTimeout(() => {{
                        if (!started) {{
                            isSpeaking = false;
                            document.getElementById('normal-tts-btn').innerText = "👉 手機限制：請點我聽發音解鎖";
                            document.getElementById('normal-tts-btn').style.animation = "pulse 1.5s infinite";
                        }} else if (started && !ended) msg.onend();
                    }}, 3500);

                    window.speechSynthesis.speak(msg); 
                }};
                {auto_script}
            </script>
            """
            st.components.v1.html(btn_html, height=70)

            st.markdown('<div id="answer-zone" style="transition: opacity 0.5s;">', unsafe_allow_html=True)
            
            if diff == '簡單':
                cA, cB = st.columns(2)
                with cA:
                    if opts[0] != "❌":
                        if st.button(f"A. {opts[0]}", use_container_width=True, key="ans_a"): process_ans(opts[0])
                    else: st.button("❌", disabled=True, use_container_width=True, key="ans_a_del")
                    
                    if opts[2] != "❌":
                        if st.button(f"C. {opts[2]}", use_container_width=True, key="ans_c"): process_ans(opts[2])
                    else: st.button("❌", disabled=True, use_container_width=True, key="ans_c_del")
                with cB:
                    if opts[1] != "❌":
                        if st.button(f"B. {opts[1]}", use_container_width=True, key="ans_b"): process_ans(opts[1])
                    else: st.button("❌", disabled=True, use_container_width=True, key="ans_b_del")
                    
                    if opts[3] != "❌":
                        if st.button(f"D. {opts[3]}", use_container_width=True, key="ans_d"): process_ans(opts[3])
                    else: st.button("❌", disabled=True, use_container_width=True, key="ans_d_del")
            else:
                st.markdown("<hr style='border: 1px dashed #bdc3c7; margin: 15px 0;'>", unsafe_allow_html=True)
                st.text_input("✍️ 施展拼寫魔法 (支援實體鍵盤與下方虛擬鍵盤)：", key="text_input_field", autocomplete="off")
                
                # --- 📱 電競級原生手機虛擬鍵盤 ---
                kb_html = """
                <style>
                .kb-container { background-color: #d1d5db; padding: 8px 4px; border-radius: 8px; width: 100%; max-width: 500px; margin: 0 auto; user-select: none; }
                .kb-row { display: flex; justify-content: center; margin-bottom: 6px; gap: 4px; }
                .kb-key { flex: 1; height: 45px; background: #ffffff; border-radius: 5px; border: none; font-size: 1.2rem; font-weight: bold; color: #111827; box-shadow: 0 1px 2px rgba(0,0,0,0.3); cursor: pointer; display: flex; align-items: center; justify-content: center; touch-action: manipulation; }
                .kb-key:active { background: #9ca3af; transform: translateY(1px); }
                .kb-row-2 { padding: 0 5%; }
                .kb-key-wide { flex: 1.5; font-size: 1rem;}
                .kb-key-space { flex: 3; font-size: 1rem; }
                .kb-submit { background-color: #e74c3c; color: #fff; flex: 3; font-size: 1.1rem; }
                .kb-submit:active { background-color: #c0392b; }
                </style>
                <div class="kb-container">
                    <div class="kb-row">
                        <button class="kb-key" onclick="tk('Q')">Q</button><button class="kb-key" onclick="tk('W')">W</button><button class="kb-key" onclick="tk('E')">E</button><button class="kb-key" onclick="tk('R')">R</button><button class="kb-key" onclick="tk('T')">T</button><button class="kb-key" onclick="tk('Y')">Y</button><button class="kb-key" onclick="tk('U')">U</button><button class="kb-key" onclick="tk('I')">I</button><button class="kb-key" onclick="tk('O')">O</button><button class="kb-key" onclick="tk('P')">P</button>
                    </div>
                    <div class="kb-row kb-row-2">
                        <button class="kb-key" onclick="tk('A')">A</button><button class="kb-key" onclick="tk('S')">S</button><button class="kb-key" onclick="tk('D')">D</button><button class="kb-key" onclick="tk('F')">F</button><button class="kb-key" onclick="tk('G')">G</button><button class="kb-key" onclick="tk('H')">H</button><button class="kb-key" onclick="tk('J')">J</button><button class="kb-key" onclick="tk('K')">K</button><button class="kb-key" onclick="tk('L')">L</button>
                    </div>
                    <div class="kb-row">
                        <button class="kb-key kb-key-wide" onclick="tk('-')">-</button><button class="kb-key" onclick="tk('Z')">Z</button><button class="kb-key" onclick="tk('X')">X</button><button class="kb-key" onclick="tk('C')">C</button><button class="kb-key" onclick="tk('V')">V</button><button class="kb-key" onclick="tk('B')">B</button><button class="kb-key" onclick="tk('N')">N</button><button class="kb-key" onclick="tk('M')">M</button><button class="kb-key kb-key-wide" onclick="bk()">⌫</button>
                    </div>
                    <div class="kb-row">
                        <button class="kb-key kb-key-space" onclick="tk(' ')">空白 (Space)</button>
                        <button class="kb-key kb-submit" onclick="sm()">⚔️ 送出攻擊</button>
                    </div>
                </div>
                <script>
                    let p = window.parent.document;
                    
                    function hideBtn() {
                        p.querySelectorAll('button').forEach(b => {
                            if(b.innerText.includes('隱藏送出按鈕')) {
                                b.style.display = 'none';
                                if(b.parentElement) b.parentElement.style.display = 'none';
                            }
                        });
                    }
                    hideBtn();
                    setInterval(hideBtn, 500);

                    function tk(char) {
                        let input = p.querySelector('input[data-testid="stTextInput"] input') || p.querySelector('input[type="text"]');
                        if(input) {
                            let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                            nativeSetter.call(input, input.value + char);
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }
                    
                    function bk() {
                        let input = p.querySelector('input[data-testid="stTextInput"] input') || p.querySelector('input[type="text"]');
                        if(input && input.value.length > 0) {
                            let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                            nativeSetter.call(input, input.value.slice(0, -1));
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                        }
                    }
                    
                    function sm() {
                        let input = p.querySelector('input[data-testid="stTextInput"] input') || p.querySelector('input[type="text"]');
                        if(input) {
                            input.focus();
                            input.blur(); 
                        }
                        setTimeout(() => {
                            p.querySelectorAll('button').forEach(b => {
                                if(b.innerText.includes('隱藏送出按鈕')) b.click();
                            });
                        }, 150);
                    }

                    if(!window.parent.enterListenerAdded) {
                        p.addEventListener('keydown', function(e) {
                            if(e.key === 'Enter') {
                                let activeEl = p.activeElement;
                                if(activeEl && activeEl.tagName === 'INPUT' && activeEl.type === 'text') {
                                    e.preventDefault();
                                    activeEl.blur();
                                    setTimeout(() => {
                                        p.querySelectorAll('button').forEach(b => {
                                            if(b.innerText.includes('隱藏送出按鈕')) b.click();
                                        });
                                    }, 150);
                                }
                            }
                        });
                        window.parent.enterListenerAdded = true;
                    }
                </script>
                """
                st.components.v1.html(kb_html, height=250)
            
            st.markdown('</div>', unsafe_allow_html=True)

# ==================== 家長控制台 ====================
elif st.session_state.page == 'parent':
    p_id = st.session_state.current_parent
    p_db = get_parents()
    p_data = p_db[p_id]
    
    if "custom_banks" not in p_data:
        p_data["custom_banks"] = [{"id": "1", "name": "預設自建字庫"}]
        save_parents(p_db)
        old_file = f"vocab_custom_{p_id}.csv"
        if os.path.exists(old_file): os.rename(old_file, f"vocab_custom_{p_id}_1.csv")

    st.markdown("<h1 style='text-align: center; color:#e67e22;'>👨‍👩‍👧 家長專區</h1><hr>", unsafe_allow_html=True)
    c_top1, c_top2 = st.columns([1, 1])
    with c_top1:
        if st.button("⬅️ 登出並返回大廳", use_container_width=True): st.session_state.page = 'login'; st.rerun()
    with c_top2:
        with st.expander("🔐 更改密碼"):
            o_pw = st.text_input("舊密碼", type="password")
            n_pw = st.text_input("新密碼", type="password")
            if st.button("確認修改"):
                if o_pw == p_data["password"] and n_pw.strip():
                    p_db[p_id]["password"] = n_pw.strip(); save_parents(p_db); st.success("✅ 成功！")
                else: st.error("錯誤")
    st.markdown("---")
    
    t1, t2, t3, t4, t5 = st.tabs(["🎒 訓練家管理", "🏪 商店獎勵", "📚 自建字庫", "🖼️ 目標圖鑑", "📝 官方糾錯回饋"])
    
    with t1:
        admin_cfg = get_admin()
        limit = p_data.get("hero_limit")
        if limit is None: limit = admin_cfg.get("default_hero_limit", 3)
        
        users = get_users()
        my_heroes = {k: v for k, v in users.items() if v.get("parent") == p_id}
        
        global_banks = ["國小", "國中", "多益"]
        custom_bank_options = [f"custom_{b['id']}" for b in p_data["custom_banks"]]
        all_banks = global_banks + custom_bank_options
        def format_bank(b):
            if b in global_banks: return b
            cb_id = b.split("_")[1]
            cb_name = next((cb["name"] for cb in p_data["custom_banks"] if cb["id"] == cb_id), "未知字庫")
            return f"📂 {cb_name}"

        st.info(f"🎒 目前已建立帳號：{len(my_heroes)} / {limit}")
        
        if len(my_heroes) < limit:
            with st.expander("➕ 建立新訓練家帳號", expanded=False):
                n_name = st.text_input("訓練家名稱 (小孩的名字或暱稱)")
                n_pin = st.text_input("設定登入密碼 (建議設定 4 位數字)", value="0000")
                n_char = st.selectbox("選擇夥伴寶可夢", ["火系 (小火龍)", "水系 (傑尼龜)", "草系 (妙蛙種子)", "電系 (皮丘)", "隨機"])
                n_bank = st.selectbox("選擇預設學習題庫", all_banks, format_func=format_bank)
                if st.button("確認建立"):
                    if not n_name.strip() or not n_pin.strip(): st.error("名稱與密碼不可為空")
                    else:
                        u_key = f"{p_id}_{n_name}"
                        if u_key in users: st.error("這個名稱已經存在於您的家庭中了！")
                        else:
                            c = random.choice(list(CHARACTERS.keys())) if n_char == "隨機" else n_char
                            users[u_key] = {"name": n_name.strip(), "parent": p_id, "character": c, "created_at": str(datetime.now().date()), "pin": n_pin.strip()}
                            save_users(users)
                            
                            init_data = load_user_data(u_key)
                            init_data["vocab_bank"] = n_bank
                            save_user_data(u_key, init_data)
                            st.success("✅ 建立成功！"); st.rerun()
        
        st.markdown("#### 訓練家列表")
        for u_key, u_info in my_heroes.items():
            d = load_user_data(u_key)
            e_log = load_error_log(u_key)
            with st.expander(f"👤 {u_info['name']} ({u_info['character']})"):
                st.markdown("#### 📊 數據調整")
                cA, cB, cC, cD, cE = st.columns(5)
                n_lvl = cA.number_input("等級", min_value=1, value=d['level'], key=f"lvl_{u_key}")
                n_tq = cB.number_input("累積題數", min_value=0, value=d.get('total_questions', 0), key=f"tq_{u_key}")
                n_mdl = cC.number_input("勳章", min_value=0, value=d['medals'], key=f"mdl_{u_key}")
                n_dc = cD.number_input("倒地次數", min_value=0, max_value=4, value=d.get('death_count', 0), key=f"dc_{u_key}")
                new_diff = cE.selectbox("難度", ["簡單", "中等", "困難"], index=["簡單", "中等", "困難"].index(d.get("difficulty", "簡單")), key=f"diff_{u_key}")
                
                col_r2 = st.columns([1, 1, 1, 2])
                curr_bank = d.get("vocab_bank", "國小")
                if curr_bank == "家長自訂": curr_bank = "custom_1" 
                if curr_bank not in all_banks: curr_bank = "國小"
                
                new_bank = col_r2[0].selectbox("學習題庫", all_banks, index=all_banks.index(curr_bank), format_func=format_bank, key=f"bank_{u_key}")
                new_pin = col_r2[1].text_input("修改密碼 (PIN)", value=u_info.get("pin", "0000"), key=f"pin_{u_key}")
                n_gld = col_r2[2].number_input("金幣", min_value=0, value=d.get('gold', 0), key=f"gld_{u_key}")
                
                if new_pin != u_info.get("pin", "0000"):
                    users[u_key]["pin"] = new_pin
                    save_users(users)
                    st.success("密碼已更新！")
                
                if n_lvl != d['level'] or n_tq != d.get('total_questions', 0) or n_mdl != d['medals'] or n_dc != d.get('death_count', 0) or new_diff != d.get("difficulty", "簡單") or new_bank != curr_bank or n_gld != d.get('gold', 0):
                    d['level'] = n_lvl; d['total_questions'] = n_tq; d['medals'] = n_mdl; d['death_count'] = n_dc; d['difficulty'] = new_diff; d['vocab_bank'] = new_bank; d['gold'] = n_gld
                    save_user_data(u_key, d); st.rerun()

                st.write("**🔴 錯題本：**", ", ".join(e_log) if e_log else "無錯題！")
                
                st.markdown("**🎁 兌換紀錄**")
                if d.get('history'):
                    for i, item in enumerate(reversed(d['history'])):
                        hA, hB = st.columns([4, 1])
                        hA.text(item)
                        if hB.button("🗑️ 退回", key=f"del_h_{u_key}_{i}"):
                            actual_idx = len(d['history']) - 1 - i
                            d['history'].pop(actual_idx); save_user_data(u_key, d); st.rerun()
                else: st.caption("無紀錄。")
                    
                b1, b2 = st.columns(2)
                with b1:
                    if st.button(f"🔄 清空訓練家學習資料", key=f"rs_{u_key}"): reset_user_data(u_key); st.rerun()
                with b2:
                    if st.button(f"🗑️ 永久刪除此帳號", key=f"dl_{u_key}"): delete_user(u_key); st.rerun()

    with t2:
        st.subheader("🛒 道具販售價格設定")
        prices = p_data.get("store_prices", {"potion": 50, "shield": 100, "magnifier": 30})
        c1, c2, c3 = st.columns(3)
        new_p = c1.number_input("🧪 藥水價格 (G)", min_value=1, value=prices["potion"])
        new_s = c2.number_input("🛡️ 護盾價格 (G)", min_value=1, value=prices["shield"])
        new_m = c3.number_input("🔍 放大鏡價格 (G)", min_value=1, value=prices["magnifier"])
        if st.button("💾 儲存道具價格", type="primary"):
            p_db[p_id]["store_prices"] = {"potion": new_p, "shield": new_s, "magnifier": new_m}
            save_parents(p_db)
            st.success("✅ 道具物價已更新！")
            
        st.markdown("---")
        st.subheader("🎁 新增家庭專屬勳章獎勵")
        with st.form("add_r"):
            n_r = st.text_input("名稱")
            n_c = st.number_input("需要勳章", min_value=1, value=1)
            n_i = st.selectbox("圖示", EMOJI_LIST)
            if st.form_submit_button("➕ 新增獎勵"):
                if n_r.strip():
                    if "rewards" not in p_db[p_id]: p_db[p_id]["rewards"] = []
                    p_db[p_id]["rewards"].append({"reward": n_r, "cost_medals": n_c, "icon": n_i})
                    save_parents(p_db); st.success("✅ 成功！"); st.rerun()
        
        st.subheader("目前可兌換清單")
        r_list = p_db.get(p_id, {}).get("rewards", [])
        if not r_list: st.info("目前沒有設定任何獎勵。")
        for idx, r in enumerate(r_list):
            cA, cB = st.columns([4, 1])
            with cA: st.info(f"{r['icon']} {r['reward']} (需 {r['cost_medals']} 勳章)")
            with cB:
                if st.button("🗑️", key=f"d_r_{idx}"):
                    p_db[p_id]["rewards"].pop(idx)
                    save_parents(p_db); st.rerun()
                    
    with t3:
        admin_cfg = get_admin()
        bank_limit = p_data.get("bank_limit")
        if bank_limit is None: bank_limit = admin_cfg.get("default_bank_limit", 3)
        
        st.info(f"📂 目前已建立字庫：{len(p_data['custom_banks'])} / {bank_limit}")
        
        if len(p_data['custom_banks']) < bank_limit:
            with st.expander("➕ 新增自建字庫", expanded=False):
                n_bank_name = st.text_input("字庫名稱 (例如：康軒第三課)")
                if st.button("確認新增字庫"):
                    if n_bank_name.strip():
                        new_id = str(int(time.time()))
                        p_data['custom_banks'].append({"id": new_id, "name": n_bank_name.strip()})
                        save_parents(p_db)
                        st.success("✅ 字庫建立成功！"); st.rerun()
                    else: st.error("名稱不可為空")

        if p_data['custom_banks']:
            sel_bank_id = st.selectbox("選擇要管理/編輯的字庫", [b["id"] for b in p_data["custom_banks"]], format_func=lambda x: next(b["name"] for b in p_data["custom_banks"] if b["id"]==x))
            c_file = f"vocab_custom_{p_id}_{sel_bank_id}.csv"
            
            # --- 字庫更名與一鍵清空功能 ---
            st.markdown("---")
            st.subheader("⚙️ 字庫設定")
            col_set1, col_set2 = st.columns(2)
            with col_set1:
                current_name = next(b["name"] for b in p_data["custom_banks"] if b["id"]==sel_bank_id)
                new_name = st.text_input("修改字庫名稱", value=current_name)
                if st.button("💾 儲存新名稱"):
                    if new_name.strip():
                        for b in p_data["custom_banks"]:
                            if b["id"] == sel_bank_id:
                                b["name"] = new_name.strip()
                        save_parents(p_db)
                        st.success("✅ 名稱已更新！")
                        st.rerun()
                    else: st.error("名稱不能為空！")
            with col_set2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🧹 一鍵清空此字庫內容", type="secondary"):
                    empty_df = pd.DataFrame(columns=["en", "zh", "hint"])
                    empty_df.to_csv(c_file, index=False, encoding="utf-8-sig")
                    st.success("✅ 字庫內容已清空！")
                    st.rerun()
            
            st.markdown("---")
            st.subheader("🤝 題庫分享與匯入 (Share & Import)")
            colA, colB = st.columns(2)
            with colA:
                st.markdown("**📤 分享目前選取的題庫**")
                shares = get_shares()
                my_code = None
                for k, v in shares.items():
                    if isinstance(v, dict) and v.get("p_id") == p_id and v.get("bank_id") == sel_bank_id: my_code = k
                    elif isinstance(v, str) and v == p_id and sel_bank_id == "1": my_code = k 
                
                if my_code:
                    st.success(f"專屬分享碼：**{my_code}**")
                    st.caption("將此代碼傳給其他家長，即可匯入您的單字庫！")
                else:
                    if st.button("產生專屬分享碼"):
                        new_code = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=5))
                        shares[new_code] = {"p_id": p_id, "bank_id": sel_bank_id}
                        save_shares(shares); st.rerun()
            with colB:
                st.markdown("**📥 匯入他人題庫**")
                import_code = st.text_input("輸入分享碼 (將附加至目前選取的字庫)")
                if st.button("確認匯入"):
                    import_code = import_code.strip().upper()
                    shares = get_shares()
                    if import_code in shares:
                        share_data = shares[import_code]
                        if isinstance(share_data, str): source_p_id, source_bank_id = share_data, "1"
                        else: source_p_id, source_bank_id = share_data["p_id"], share_data["bank_id"]

                        source_file = f"vocab_custom_{source_p_id}_{source_bank_id}.csv"
                        if os.path.exists(source_file):
                            src_df = pd.read_csv(source_file)
                            if os.path.exists(c_file):
                                curr_df = pd.read_csv(c_file)
                                merged_df = pd.concat([curr_df, src_df]).drop_duplicates(subset=['en'], keep='last')
                            else: merged_df = src_df
                            merged_df.to_csv(c_file, index=False, encoding="utf-8-sig")
                            st.success("✅ 匯入成功！已將對方的單字加入您的題庫中。"); st.rerun()
                        else: st.error("對方的題庫目前是空的喔！")
                    else: st.error("❌ 無效的分享碼")

            st.markdown("---")
            v_df = pd.read_csv(c_file) if os.path.exists(c_file) else pd.DataFrame(columns=["en", "zh", "hint"])
            edited_df = st.data_editor(v_df, num_rows="dynamic", use_container_width=True)
            if st.button("💾 儲存自訂單字庫", type="primary"):
                if "sentence" in edited_df.columns: edited_df = edited_df.drop(columns=["sentence"])
                edited_df.to_csv(c_file, index=False, encoding="utf-8-sig"); st.success("您的自訂題庫已更新成功！")
            
    with t4:
        st.subheader("🌟 夥伴寶可夢進化路線")
        st.info("孩子達到指定等級後，夥伴寶可夢就會自動進化！可以拿這個當作他們的目標。")
        for h_k, h_v in CHARACTERS.items():
            st.markdown(f"**{h_k} 家族**")
            h_cols = st.columns(min(len(h_v["stages"]), 5))
            for idx, (h_id, h_name) in enumerate(h_v["stages"]):
                lvl_req = 1 if idx==0 else (5 if idx==1 else 10)
                h_cols[idx].image(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{h_id}.gif", caption=f"Lv.{lvl_req} {h_name}")
        
        st.markdown("---")
        st.subheader(f"🏆 傳說 BOSS 挑戰圖鑑 (共 {len(BOSSES)} 隻)")
        html_boss = '<div class="dex-grid">'
        for b in BOSSES:
            html_boss += f'<div class="dex-item"><img src="{b["url"]}"><div class="dex-name">{b["name"]}</div></div>'
        html_boss += '</div>'
        st.markdown(html_boss, unsafe_allow_html=True)
            
        st.markdown("---")
        st.subheader(f"👾 一般野生寶可夢圖鑑 (共 {len(MONSTERS)} 隻)")
        html_monster = '<div class="dex-grid">'
        for m in MONSTERS:
            html_monster += f'<div class="dex-item"><img src="{m["url"]}"><div class="dex-name">{m["name"]}</div></div>'
        html_monster += '</div>'
        st.markdown(html_monster, unsafe_allow_html=True)

    with t5:
        st.subheader("📝 官方字庫糾錯回饋")
        st.info("若您發現官方字庫 (國小/國中/多益) 中有翻譯不精準或錯誤的地方，請填寫此表單。審核通過後，該單字將會全球同步更新！")
        with st.form("feedback_form"):
            fb_bank = st.selectbox("回報目標字庫", ["國小", "國中", "多益"])
            fb_en = st.text_input("英文單字 (En)")
            fb_zh = st.text_input("正確中文 (Zh)")
            fb_hint = st.text_input("正確提示 (Hint)")
            if st.form_submit_button("送出審核"):
                if fb_en.strip() and fb_zh.strip():
                    fbs = load_json(FEEDBACK_FILE, [])
                    fbs.append({
                        "id": str(int(time.time()*1000)), "p_id": p_id, "bank": fb_bank,
                        "en": fb_en.strip(), "zh": fb_zh.strip(), "hint": fb_hint.strip(),
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    save_json(FEEDBACK_FILE, fbs)
                    st.success("✅ 回報已送出！非常感謝您的協助！")
                else: st.error("英文與中文欄位不可為空！")

# ==================== GM 控制台 ====================
elif st.session_state.page == 'admin':
    st.markdown("<h1 style='text-align: center; color:#c0392b;'>👑 系統最高管理員中心</h1><hr>", unsafe_allow_html=True)
    if st.button("⬅️ 登出並返回大廳"): st.session_state.page = 'login'; st.rerun()
    st.markdown("---")
    
    t1, t2, t3, t4 = st.tabs(["👨‍👩‍👧 租戶 (家長) 與訓練家管理", "📋 回饋審核", "📚 題庫增訂", "⚙️ 系統設定"])
    
    with t1:
        p_db = get_parents()
        u_db = get_users()
        if not p_db: st.info("目前沒有任何家長註冊。")
        for p_id, p_info in p_db.items():
            with st.expander(f"🏠 家族帳號：{p_id}"):
                c1, c2, c3 = st.columns(3)
                new_pwd = c1.text_input("修改密碼", value=p_info['password'], key=f"apwd_{p_id}")
                
                admin_cfg = get_admin()
                h_limit_val = p_info.get('hero_limit')
                if h_limit_val is None: h_limit_val = admin_cfg.get("default_hero_limit", 3)
                
                b_limit_val = p_info.get('bank_limit')
                if b_limit_val is None: b_limit_val = admin_cfg.get("default_bank_limit", 3)
                    
                new_h_limit = c2.number_input("設定帳號上限", min_value=1, value=h_limit_val, key=f"hlim_{p_id}")
                new_b_limit = c3.number_input("設定字庫上限", min_value=1, value=b_limit_val, key=f"blim_{p_id}")
                
                if new_pwd != p_info['password'] or new_h_limit != p_info.get('hero_limit') or new_b_limit != p_info.get('bank_limit'):
                    p_db[p_id]['password'] = new_pwd
                    p_db[p_id]['hero_limit'] = new_h_limit
                    p_db[p_id]['bank_limit'] = new_b_limit
                    save_parents(p_db); st.rerun()
                
                heroes = {k: v for k, v in u_db.items() if v.get("parent") == p_id}
                st.markdown(f"**旗下訓練家 ({len(heroes)})：**")
                for u_key, u_info in heroes.items():
                    d = load_user_data(u_key)
                    cols = st.columns([1, 1, 1, 1, 2])
                    cols[0].write(u_info['name'])
                    cols[1].write(f"Lv.{d['level']}")
                    cols[2].write(f"勳章: {d['medals']}")
                    cols[3].write(d['difficulty'])
                    if cols[4].button("🗑️ 刪除", key=f"gm_d_{u_key}"):
                        delete_user(u_key); st.rerun()
                        
                st.markdown("---")
                if st.button(f"🚨 刪除此家族 (包含底下所有帳號)", key=f"gm_dp_{p_id}", type="primary"):
                    for u_key in heroes: delete_user(u_key)
                    del p_db[p_id]
                    save_parents(p_db); st.rerun()

    with t2:
        st.subheader("📋 官方字庫回饋審核")
        fbs = load_json(FEEDBACK_FILE, [])
        if not fbs: st.info("目前沒有待審核的回饋單。")
        for fb in fbs:
            with st.container():
                cols = st.columns([1, 1, 1, 1, 1, 2])
                cols[0].write(f"**[{fb['bank']}]**")
                cols[1].write(fb['en'])
                cols[2].write(fb['zh'])
                cols[3].write(fb['hint'])
                cols[4].caption(f"By {fb['p_id']}")
                c_btn1, c_btn2 = cols[5].columns(2)
                if c_btn1.button("✅ 核准", key=f"fb_app_{fb['id']}"):
                    v_file = VOCAB_FILES[fb['bank']]
                    df = pd.read_csv(v_file)
                    if fb['en'] in df['en'].values:
                        idx = df.index[df['en'] == fb['en']].tolist()[0]
                        df.at[idx, 'zh'] = fb['zh']
                        df.at[idx, 'hint'] = fb['hint']
                    else:
                        new_row = pd.DataFrame([{"en": fb['en'], "zh": fb['zh'], "hint": fb['hint']}])
                        df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(v_file, index=False, encoding="utf-8-sig")
                    
                    fbs = [f for f in fbs if f['id'] != fb['id']]
                    save_json(FEEDBACK_FILE, fbs)
                    st.success("✅ 審核通過，官方字庫已更新！")
                    st.rerun()
                if c_btn2.button("❌ 拒絕", key=f"fb_rej_{fb['id']}"):
                    fbs = [f for f in fbs if f['id'] != fb['id']]
                    save_json(FEEDBACK_FILE, fbs)
                    st.rerun()

    with t3:
        st.subheader("編輯全域單字庫")
        edit_bank = st.radio("選擇要編輯的題庫", ["國小", "國中", "多益"], horizontal=True)
        edit_file = VOCAB_FILES[edit_bank]
        v_df = pd.read_csv(edit_file) if os.path.exists(edit_file) else pd.DataFrame(columns=["en", "zh", "hint"])
        edited_df = st.data_editor(v_df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 儲存題庫修改", type="primary"):
            if "sentence" in edited_df.columns: edited_df = edited_df.drop(columns=["sentence"])
            edited_df.to_csv(edit_file, index=False, encoding="utf-8-sig"); st.success(f"【{edit_bank}】題庫更新成功！")
            
    with t4:
        st.subheader("系統安全設定")
        admin_cfg = get_admin()
        with st.form("admin_settings"):
            new_a_pwd = st.text_input("GM 密碼", value=admin_cfg.get("password", "1234"), type="password")
            new_h_limit = st.number_input("全域預設帳號上限", min_value=1, value=admin_cfg.get("default_hero_limit", 3))
            new_b_limit = st.number_input("全域預設字庫上限", min_value=1, value=admin_cfg.get("default_bank_limit", 3))
            if st.form_submit_button("儲存系統設定"):
                admin_cfg["password"] = new_a_pwd
                admin_cfg["default_hero_limit"] = new_h_limit
                admin_cfg["default_bank_limit"] = new_b_limit
                save_admin(admin_cfg); st.success("系統設定已儲存！"); st.rerun()
