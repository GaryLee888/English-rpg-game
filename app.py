import os
import sys
import subprocess

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
        print(f"🔧 偵測到缺少必要套件 {missing}，正在背景自動安裝 (只需執行一次)...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("✅ 安裝完成！正在重新啟動遊戲...")
            os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", sys.argv[0]])
        except Exception as e:
            print(f"❌ 自動安裝失敗: {e}")
            sys.exit(1)

setup_environment()

import streamlit as st
import json
import csv
import random
import time
import eng_to_ipa as ipa
from datetime import datetime
import pandas as pd

# --- 檔案設定 ---
USERS_FILE = "users_db.json"
VOCAB_FILE = "vocab_list.csv"
REWARD_FILE = "reward_list.csv"
SETTINGS_FILE = "settings.json"

# --- Emoji 圖庫 ---
EMOJI_LIST = ["🎮", "🧸", "🎲", "🧩", "🎯", "🪀", "🪁", "🚂", "🍔", "🍟", "🍕", "🍦", "🍩", "🍫", "🍬", "🍿", "🥤", "🧋", "👑", "🏆", "🥇", "⭐", "💰", "💎", "🐬", "🎬", "🚲", "⚽", "🏀", "🏊", "⛺", "🚀", "📖", "🖍️", "🎨", "🎒"]

# --- 角色進化樹與專屬音效 ---
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

# --- 怪物與 BOSS 庫 ---
BOSS_DATA = [
    (144,"急凍鳥"), (145,"閃電鳥"), (146,"火焰鳥"), (150,"超夢"), (248,"班基拉斯"), (249,"洛奇亞"), (250,"鳳王"), 
    (373,"暴飛龍"), (376,"巨金怪"), (377,"雷吉洛克"), (378,"雷吉艾斯"), (379,"雷吉斯奇魯"), (380,"拉帝亞斯"), (381,"拉帝歐斯"), 
    (382,"蓋歐卡"), (383,"固拉多"), (384,"烈空坐"), (386,"代歐奇希斯"), (445,"烈咬陸鯊"), (466,"電擊魔獸"), (467,"鴨嘴炎獸"), 
    (473,"象牙豬"), (477,"黑夜魔靈"), (483,"帝牙盧卡"), (484,"帕路奇亞"), (485,"席多藍恩"), (486,"雷吉奇卡斯"), (487,"騎拉帝納"), 
    (491,"達克萊伊"), (493,"阿爾宙斯"), (612,"雙斧戰龍"), (635,"三首惡龍"), (638,"勾帕路翁"), (639,"代拉基翁"), (640,"畢力吉翁")
]
BOSSES = [{"name": n, "url": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{i}.gif"} for i, n in BOSS_DATA]

MONSTER_DATA = [
    (10,"綠毛蟲"),(13,"獨角蟲"),(16,"波波"),(19,"小拉達"),(27,"穿山鼠"),(29,"尼多蘭"),(32,"尼多朗"),(35,"皮皮"),(37,"六尾"),(39,"胖丁"),
    (43,"走路草"),(46,"派拉斯"),(48,"毛球"),(50,"地鼠"),(52,"喵喵"),(54,"可達鴨"),(56,"猴怪"),(58,"卡蒂狗"),(60,"蚊香蝌蚪"),(63,"凱西"),
    (66,"腕力"),(69,"喇叭芽"),(72,"瑪瑙水母"),(74,"小拳石"),(77,"小火馬"),(79,"呆呆獸"),(81,"小磁怪"),(83,"大蔥鴨"),(84,"嘟嘟"),(86,"小海獅"),
    (90,"大舌貝"),(95,"大岩蛇"),(98,"大鉗蟹"),(100,"霹靂電球"),(102,"蛋蛋"),(104,"卡拉卡拉"),(108,"大舌頭"),(111,"獨角犀牛"),(114,"蔓藤怪"),(116,"墨海馬"),
    (118,"角金魚"),(120,"海星星"),(128,"肯泰羅"),(129,"鯉魚王"),(132,"百變怪"),(133,"伊布"),(137,"多邊獸"),(143,"卡比獸"),(152,"菊草葉"),(155,"火球鼠"),
    (158,"小鋸鱷"),(161,"尾立"),(163,"咕咕"),(165,"芭瓢蟲"),(167,"圓絲蛛"),(170,"燈籠魚"),(173,"皮寶寶"),(174,"寶寶丁"),(175,"波克比"),(177,"天然雀"),
    (179,"咩利羊"),(183,"瑪力露"),(185,"胡說樹"),(187,"毽子草"),(190,"長尾怪手"),(191,"向日種子"),(193,"陽々瑪"),(194,"烏波"),(198,"黑暗鴉"),(200,"夢妖"),
    (202,"果然翁"),(203,"麒麟奇"),(204,"榛果球"),(206,"土龍弟弟"),(209,"布魯"),(213,"壺壺"),(214,"赫拉克羅斯"),(216,"熊寶寶"),(218,"熔岩蟲"),(220,"小山豬"),
    (222,"太陽珊瑚"),(223,"鐵炮魚"),(225,"信使鳥"),(228,"戴魯比"),(231,"小小象"),(234,"驚角鹿"),(235,"圖圖犬"),(236,"巴爾郎"),(238,"迷唇娃"),(239,"電擊怪"),
    (240,"小鴨嘴龍"),(241,"大奶罐"),(246,"幼基拉斯"),(252,"木守宮"),(255,"火稚雞"),(258,"水躍魚")
]
MONSTERS = [{"name": n, "url": f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{i}.gif"} for i, n in MONSTER_DATA]

# --- 題庫初始化 ---
if not os.path.exists(VOCAB_FILE): 
    pd.DataFrame({
        "en": ["burger", "whale", "run"], 
        "zh": ["漢堡", "鯨魚", "跑步"], 
        "hint": ["速食", "海洋生物", "運動"]
    }).to_csv(VOCAB_FILE, index=False, encoding="utf-8-sig")

if not os.path.exists(REWARD_FILE): pd.DataFrame({"reward": ["週末多玩 30 分鐘 Switch"], "cost_medals": [1], "icon": ["🎮"]}).to_csv(REWARD_FILE, index=False, encoding="utf-8-sig")

# --- 資料存取 ---
def load_json(f, d):
    if os.path.exists(f):
        try:
            with open(f, "r", encoding="utf-8") as file: return json.load(file)
        except: pass
    return d
def save_json(f, d):
    with open(f, "w", encoding="utf-8") as file: json.dump(d, file)
def load_user_data(u): 
    return load_json(f"data_{u}.json", {"exp": 0, "level": 1, "hero_hp": 3, "medals": 0, "combo": 0, "is_boss_fight": False, "boss_hp": 3, "history": [], "total_questions": 0, "difficulty": "簡單", "trophies": [], "monster_dex": [], "death_count": 0})
def save_user_data(u, d): save_json(f"data_{u}.json", d)
def load_csv(f):
    try: 
        return pd.read_csv(f, encoding="utf-8-sig").fillna("").to_dict('records')
    except: return []
def load_error_log(u): return load_json(f"error_{u}.json", [])
def save_error_log(u, l): save_json(f"error_{u}.json", l)
def reset_user_data(u):
    if os.path.exists(f"data_{u}.json"): os.remove(f"data_{u}.json")
    if os.path.exists(f"error_{u}.json"): os.remove(f"error_{u}.json")
def delete_user(u):
    reset_user_data(u)
    users = load_json(USERS_FILE, {})
    if u in users: del users[u]; save_json(USERS_FILE, users)

def pick_next_question(v_list, err_log, total_q):
    if err_log and (total_q >= 20 or random.random() < 0.4):
        w = random.choice(err_log)
        for v in v_list:
            if v['en'] == w: return v
    return random.choice(v_list)

def generate_options(c_v, f_list):
    o = [c_v['zh']]
    w = [v['zh'] for v in f_list if v['zh'] != c_v['zh']]
    o.extend(random.sample(w, min(3, len(w))))
    while len(o) < 4: o.append("錯誤")
    random.shuffle(o)
    return o

# --- 網頁設定與自適應 CSS ---
st.set_page_config(page_title="英文英雄 RPG", page_icon="⚔️", layout="wide")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container { max-width: 900px; padding-top: 1rem; padding-bottom: 2rem; }

.status-bar-container { display: flex; flex-wrap: wrap; justify-content: space-around; align-items: center; background-color: #f8f9fa; border-radius: 12px; padding: 10px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.status-item { text-align: center; flex: 1 1 20%; min-width: 70px; padding: 5px; }
.status-label { font-size: 0.8rem; color: #7f8c8d; margin-bottom: 2px; }
.status-value { font-size: 1.2rem; font-weight: bold; color: #2c3e50; }

.arena-bg { position: relative; display: flex; justify-content: space-between; align-items: flex-end; padding: 5%; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.3); margin: 15px 0; min-height: 250px; overflow: hidden; }
.hero-box, .monster-box { width: 40%; text-align: center; z-index: 5; }
.vs-box { width: 20%; text-align: center; z-index: 5; align-self: center; }
.vs-text { color: #f1c40f; font-size: 3rem; font-style: italic; text-shadow: 2px 2px 0 #000; margin:0; }
.hp-badge { font-size: 1.2rem; margin-bottom: 5px; background: rgba(0,0,0,0.4); border-radius: 20px; padding: 2px 10px; display: inline-block; color: #fff; }
.hp-badge-enemy { color: #ff6b6b; }
.monster-name { color:white; font-weight:bold; margin-top:5px; text-shadow: 1px 1px 2px #000; font-size: 1rem;}

.dex-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); gap: 10px; text-align: center; }
.dex-item img { width: 100%; max-width: 60px; height: auto; }
.dex-name { font-size: 0.7rem; color: #555; margin-top: 3px; word-break: keep-all;}

.vocab-card { text-align:center; padding: 5%; background: #ffffff; border-radius: 12px; border: 3px solid #3498db; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 10px; }
.vocab-word { color:#2980b9; font-size: 3.5rem; margin: 5px 0; font-weight: 800; word-wrap: break-word;}
.vocab-hint-str { color:#34495e; font-size: 2.5rem; margin: 10px 0; font-weight: bold; letter-spacing: 5px; word-wrap: break-word;}

@media screen and (max-width: 600px) {
    .arena-bg { min-height: 160px; padding: 15px 5px; }
    .vs-text { font-size: 1.5rem; }
    .hp-badge { font-size: 0.8rem; padding: 2px 6px; }
    .monster-name { font-size: 0.8rem; }
    .m-fx { font-size: 40px !important; }
    .vocab-word { font-size: 2.5rem; }
    .vocab-hint-str { font-size: 1.8rem; letter-spacing: 3px;}
    .status-value { font-size: 1rem; }
}

@keyframes heroDash { 0% { transform: scaleX(-1) translateX(0px); } 30% { transform: scaleX(-1) translateX(-40px); } 100% { transform: scaleX(-1) translateX(0px); } }
@keyframes shakeHurt { 0% { transform: translateX(0); filter: brightness(1); } 20% { transform: translateX(-10px); filter: brightness(2.5) drop-shadow(0 0 25px red); } 40% { transform: translateX(10px); } 60% { transform: translateX(-10px); } 80% { transform: translateX(10px); } 100% { transform: translateX(0); filter: brightness(1); } }
@keyframes monsterDash { 0% { transform: translateX(0px); } 30% { transform: translateX(-40px); } 100% { transform: translateX(0px); } }
@keyframes heroHurt { 0% { transform: scaleX(-1) translateX(0); filter: brightness(1); } 20% { transform: scaleX(-1) translateX(-8px); filter: brightness(0.4) sepia(1) hue-rotate(-50deg) saturate(6); } 40% { transform: scaleX(-1) translateX(8px); } 60% { transform: scaleX(-1) translateX(-8px); } 80% { transform: scaleX(-1) translateX(8px); } 100% { transform: scaleX(-1) translateX(0); filter: brightness(1); } }
@keyframes mBall { 0% { left: 20%; transform: scale(0.5); opacity: 0; } 30% { opacity: 1; transform: scale(1.5); } 70% { left: 70%; transform: scale(2); opacity: 1; } 100% { left: 80%; transform: scale(0.5); opacity: 0; } }
@keyframes heroDead { 0% { transform: scaleX(-1) rotate(0deg); filter: grayscale(0%); } 100% { transform: scaleX(-1) rotate(90deg) translateY(20px); filter: grayscale(100%); } }
.m-fx { position: absolute; top: 40%; font-size: 60px; animation: mBall 0.7s ease-in-out forwards; z-index: 10; }
</style>
""", unsafe_allow_html=True)

if 'settings' not in st.session_state: st.session_state.settings = load_json(SETTINGS_FILE, {"parent_password": "1234", "volume": 0.8})
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'users' not in st.session_state: st.session_state.users = load_json(USERS_FILE, {})
if 'vk_input' not in st.session_state: st.session_state.vk_input = ""
if 'play_auto_audio' not in st.session_state: st.session_state.play_auto_audio = True

# --- 破解手機靜音機制 ---
st.components.v1.html("""
<script>
const pDoc = window.parent.document;
if (!window.parent.gameAudioCtx) {
    const AudioContext = window.parent.AudioContext || window.parent.webkitAudioContext;
    if (AudioContext) {
        window.parent.gameAudioCtx = new AudioContext();
        const unlockAudio = function() {
            if (window.parent.gameAudioCtx && window.parent.gameAudioCtx.state === 'suspended') {
                window.parent.gameAudioCtx.resume();
            }
        };
        pDoc.addEventListener('click', unlockAudio, true);
        pDoc.addEventListener('touchstart', unlockAudio, true);
    }
}
</script>
""", height=0)

# ==================== 登入大廳 ====================
if st.session_state.page == 'login':
    st.markdown("<h1 style='text-align: center; color: #2c3e50;'>⚔️ 英文英雄 RPG 大廳</h1><hr>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("🔑 英雄登入")
        users = list(st.session_state.users.keys())
        if users:
            sel_u = st.selectbox("選擇英雄", users)
            if st.button("進入遊戲", type="primary", use_container_width=True):
                st.session_state.current_user = sel_u
                st.session_state.game_data = load_user_data(sel_u)
                st.session_state.error_log = load_error_log(sel_u)
                st.session_state.vk_input = ""
                st.session_state.play_auto_audio = True
                st.session_state.page = 'game'; st.rerun()
        else: st.info("無帳號")
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.expander("👨‍👩‍👧 家長控制台"):
            pw = st.text_input("密碼", type="password")
            if st.button("進入", use_container_width=True):
                if pw == st.session_state.settings["parent_password"]: st.session_state.page = 'parent'; st.rerun()
                else: st.error("錯誤")
    with col2:
        st.subheader("🆕 創建英雄")
        n_name = st.text_input("名稱")
        n_char = st.selectbox("選擇守護神 (會隨等級進化喔！)", ["火系 (小火龍)", "水系 (傑尼龜)", "草系 (妙蛙種子)", "電系 (皮丘)", "隨機"])
        if st.button("建立", use_container_width=True):
            if not n_name.strip() or n_name in st.session_state.users: st.error("無效名稱")
            else:
                c = random.choice(list(CHARACTERS.keys())) if n_char == "隨機" else n_char
                st.session_state.users[n_name] = {"character": c, "created_at": str(datetime.now().date())}
                save_json(USERS_FILE, st.session_state.users)
                st.session_state.current_user = n_name
                st.session_state.game_data = load_user_data(n_name)
                st.session_state.error_log = load_error_log(n_name)
                st.session_state.vk_input = ""
                st.session_state.play_auto_audio = True
                st.session_state.page = 'game'; st.rerun()

# ==================== 遊戲主畫面 ====================
elif st.session_state.page == 'game':
    user = st.session_state.current_user
    u_data = st.session_state.game_data
    
    if 'difficulty' not in u_data: u_data['difficulty'] = "簡單"
    diff = u_data['difficulty']
    diff_multi = {"簡單": 1, "中等": 2, "困難": 3}.get(diff, 1)

    if 'total_questions' not in u_data: u_data['total_questions'] = 0
    if 'trophies' not in u_data: u_data['trophies'] = []
    if 'monster_dex' not in u_data: u_data['monster_dex'] = []
    if 'death_count' not in u_data: u_data['death_count'] = 0
    if 'history' not in u_data: u_data['history'] = []
    
    char_d = CHARACTERS[st.session_state.users[user]['character']]
    
    stage_idx = 0 if u_data['level'] < 5 else (1 if u_data['level'] < 10 else 2)
    hero_id, hero_name = char_d["stages"][stage_idx]
    hero_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{hero_id}.gif"

    v_list = load_csv(VOCAB_FILE) or [{"en": "hero", "zh": "英雄", "hint": ""}]
    r_list = load_csv(REWARD_FILE)
    vol = st.session_state.settings.get("volume", 0.8)

    if 'current_monster' not in st.session_state: st.session_state.current_monster = random.choice(MONSTERS)
    if 'action_anim' not in st.session_state: st.session_state.action_anim = None
    if 'current_vocab' not in st.session_state: 
        st.session_state.current_vocab = pick_next_question(v_list, st.session_state.error_log, u_data['total_questions'])
        st.session_state.current_options = generate_options(st.session_state.current_vocab, v_list)
    if 'force_learning' not in st.session_state: st.session_state.force_learning = False
    
    c_w = st.session_state.current_vocab

    def process_ans(s):
        st.session_state.play_auto_audio = True 
        st.session_state.vk_input = ""          
        u_data['total_questions'] += 1 
        if s == c_w['zh']:
            u_data['combo'] += 1
            if c_w['en'] in st.session_state.error_log:
                st.session_state.error_log.remove(c_w['en'])
                save_error_log(user, st.session_state.error_log)
                if not st.session_state.error_log: u_data['total_questions'] = 0
                    
            if u_data.get('is_boss_fight', False):
                u_data['boss_hp'] -= 1
                u_data['exp'] += (10 * diff_multi) 
                if u_data['boss_hp'] <= 0:
                    u_data['medals'] += (1 * diff_multi) 
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
                u_data['hero_hp'] = 3
        else:
            u_data['combo'] = 0 
            if c_w['en'] not in st.session_state.error_log:
                st.session_state.error_log.append(c_w['en'])
                save_error_log(user, st.session_state.error_log)
            u_data['hero_hp'] -= 1
            if u_data['hero_hp'] <= 0:
                u_data['exp'] = int(u_data['exp'] * 0.8)
                u_data['death_count'] = u_data.get('death_count', 0) + 1
                if u_data['death_count'] >= 5:
                    u_data['level'] = max(1, u_data['level'] - 1)
                    u_data['death_count'] = 0
                    st.session_state.level_dropped = True
                else:
                    st.session_state.level_dropped = False
                u_data['hero_hp'] = 3
                if u_data.get('is_boss_fight', False): u_data['boss_hp'] = 3
                st.session_state.action_anim = 'dead'
            else: st.session_state.action_anim = 'hurt'
        save_user_data(user, u_data)

    def vk_add(char): st.session_state.vk_input += char
    def vk_del(): st.session_state.vk_input = st.session_state.vk_input[:-1]
    def vk_submit():
        ans = st.session_state.get("vk_input", "").strip()
        if not ans: return
        if ans.lower() == c_w['en'].lower(): process_ans(c_w['zh'])
        else: process_ans("WRONG_ANSWER")

    # --- 側邊欄 ---
    with st.sidebar:
        new_vol = st.slider("🔊 遊戲與發音音量", min_value=0.0, max_value=1.0, value=vol, step=0.1)
        if new_vol != vol:
            st.session_state.settings["volume"] = new_vol; save_json(SETTINGS_FILE, st.session_state.settings)
        st.markdown("---")
        st.subheader("🏪 公會獎勵兌換")
        for r in r_list:
            if st.button(f"{r['icon']} {r['reward']} (需 {r['cost_medals']} 勳章)", use_container_width=True):
                if u_data['medals'] >= int(r['cost_medals']):
                    u_data['medals'] -= int(r['cost_medals'])
                    u_data['history'].append(f"{datetime.now().strftime('%m-%d %H:%M')} 兌換 {r['reward']}")
                    save_user_data(user, u_data); st.success(f"🎉 兌換成功！"); st.rerun()
                else: st.error("勳章不足！")
                
        st.markdown("---")
        st.subheader("🎁 我的兌換紀錄")
        if u_data.get('history'):
            with st.expander("查看所有紀錄", expanded=False):
                for item in reversed(u_data['history']): st.markdown(f"- {item}")
        else: st.caption("尚未兌換任何獎勵。")

        st.markdown("---")
        if st.button("🚪 登出", use_container_width=True): st.session_state.page = 'login'; st.rerun()

    # --- 頂端狀態列 ---
    st.markdown(f"""
    <div class="status-bar-container">
        <div class="status-item"><div class="status-label">👤 {hero_name}</div><div class="status-value">{user}</div></div>
        <div class="status-item"><div class="status-label">🛡️ 等級</div><div class="status-value">Lv. {u_data['level']}</div></div>
        <div class="status-item"><div class="status-label">🔥 連擊</div><div class="status-value">{u_data['combo']} / 10</div></div>
        <div class="status-item"><div class="status-label">🎖️ 勳章</div><div class="status-value">{u_data['medals']}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # --- 自適應圖鑑區 ---
    with st.expander(f"📖 冒險圖鑑 (一般: {len(u_data.get('monster_dex', []))}/{len(MONSTERS)} | 神獸: {len(u_data.get('trophies', []))}/{len(BOSSES)})"):
        d_tab1, d_tab2 = st.tabs(["🏆 傳說神獸", "👾 一般怪物"])
        with d_tab1:
            if u_data.get('trophies'):
                boss_dict = {b['name']: b['url'] for b in BOSSES}
                html_dex = '<div class="dex-grid">'
                for t_name in u_data['trophies']:
                    if t_name in boss_dict:
                        html_dex += f'<div class="dex-item"><img src="{boss_dict[t_name]}"><div class="dex-name">{t_name}</div></div>'
                html_dex += '</div>'
                st.markdown(html_dex, unsafe_allow_html=True)
            else: st.write("尚未收集到神獸。")
        with d_tab2:
            if u_data.get('monster_dex'):
                mon_dict = {m['name']: m['url'] for m in MONSTERS}
                html_dex = '<div class="dex-grid">'
                for m_name in u_data['monster_dex']:
                    if m_name in mon_dict:
                        html_dex += f'<div class="dex-item"><img src="{mon_dict[m_name]}"><div class="dex-name">{m_name}</div></div>'
                html_dex += '</div>'
                st.markdown(html_dex, unsafe_allow_html=True)
            else: st.write("尚未收集到一般怪物。")
    
    scale_factor = 1 + min(u_data['medals'] * 0.1, 2.0)
    h_width = int(100 * scale_factor)

    anim = st.session_state.action_anim
    h_s = f"width: {h_width}%; max-width: 250px; transform: scaleX(-1); image-rendering: pixelated; transition: width 0.5s;"
    m_s = "width: 100%; max-width: 180px; image-rendering: pixelated;"
    fx_html = ""
    audio_js = ""

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
            gain.gain.setValueAtTime({vol} * 0.25, ctx.currentTime); gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + {char_d["snd_len"]});
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
            gain.gain.setValueAtTime({vol} * 0.25, ctx.currentTime); gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + {h_snd["len"]});
            osc.connect(gain); gain.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime + {h_snd["len"]});
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
            gain.gain.setValueAtTime({vol} * 0.25, ctx.currentTime); gain.gain.linearRampToValueAtTime(0.01, ctx.currentTime + 1.5);
            osc.connect(gain); gain.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime + 1.5);
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
        f'<div class="hp-badge">{"❤️"*h_hp}{"🖤"*(3-h_hp)}</div><br>'
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

    # --- 戰鬥結算動畫 ---
    if anim:
        if anim == 'attack': 
            st.success(f"💥 命中！獲得 {5 * diff_multi} EXP！")
        elif anim == 'hurt': 
            st.error("🩸 遭受攻擊！連擊中斷！")
        elif anim == 'boss_defeat': 
            st.balloons()
            st.success(f"🎊 擊敗傳說寶可夢！獲得 {10 * diff_multi} EXP 與 {1 * diff_multi} 枚勳章！")
        elif anim == 'dead': 
            if st.session_state.get('level_dropped', False):
                st.error("😭 英雄不支倒地... (扣除 20% EXP，累積倒地 5 次，等級下降 1 級！)")
            else:
                st.error(f"😭 英雄不支倒地... (扣除 20% EXP！累積倒地 {u_data.get('death_count', 0)}/5)")
        time.sleep(1.8)
        
        st.session_state.action_anim = None
        st.session_state.level_dropped = False 
        
        if anim == 'hurt' or anim == 'dead':
            st.session_state.force_learning = True
        else:
            st.session_state.current_vocab = pick_next_question(v_list, st.session_state.error_log, u_data['total_questions'])
            st.session_state.current_options = generate_options(st.session_state.current_vocab, v_list)
            st.session_state.play_auto_audio = True
            st.session_state.vk_input = ""
        st.rerun()

    # --- 答題介面 ---
    else:
        opts = st.session_state.current_options
        ipa_txt = ipa.convert(c_w['en'])
        ipa_d = f"[{ipa_txt}]" if ipa_txt and '*' not in ipa_txt else ""
        rev = '<span style="background: #e74c3c; color: white; padding: 2px 8px; border-radius: 10px; font-size: 14px; vertical-align: top;">⚠️ 復仇題</span>' if c_w['en'] in st.session_state.error_log else ''
        
        # ==========================================
        # 答錯的強制學習防跳過模式 (2 秒間隔版)
        # ==========================================
        if st.session_state.force_learning:
            v_html = (
                f'<div class="vocab-card" style="background: #fff5f5; border-color: #e74c3c;">'
                f'<h3 style="margin:0; color:#c0392b; font-size: 1.2rem;">❌ 答錯了！請跟著唸 3 次正確答案！</h3>'
                f'<div class="vocab-word" style="color:#e74c3c;">{c_w["en"]} = {c_w["zh"]}</div>'
                f'<h3 style="color:#e67e22; margin:0 0 15px 0; font-family: monospace; font-size: 1.5rem;">{ipa_d}</h3>'
                f'</div>'
            )
            st.markdown(v_html, unsafe_allow_html=True)
            
            # --- 2秒間隔的智慧排程播放器 ---
            js_force = f"""
            <div style="text-align:center; margin-bottom: 20px;">
                <button id="tts-btn" onclick="window.playForce()" style="background-color: #e74c3c; color: white; border: none; padding: 15px 30px; font-size: 18px; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 90%; max-width: 400px; font-weight: bold; animation: pulse 2s infinite;">
                    🔊 準備播放... (若無聲請手動點擊)
                </button>
            </div>
            <style>@keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.02); }} 100% {{ transform: scale(1); }} }}</style>
            <script>
                // 隱藏繼續冒險按鈕
                setTimeout(() => {{
                    const btns = window.parent.document.querySelectorAll('button');
                    btns.forEach(b => {{
                        if(b.innerText.includes('繼續冒險')) {{
                            b.style.display = 'none';
                            window.parent.continueQuestBtn = b;
                        }}
                    }});
                }}, 100);

                let playCount = 0;
                let isSpeaking = false;
                let timeoutId = null;

                window.playForce = function() {{
                    if (isSpeaking) return; // 防狂點
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
                        if(window.parent.continueQuestBtn) {{
                            window.parent.continueQuestBtn.style.display = 'inline-flex';
                        }}
                        return;
                    }}

                    if (window.speechSynthesis) window.speechSynthesis.cancel();
                    let msg = new SpeechSynthesisUtterance("{c_w['en']}"); 
                    msg.lang = 'en-US'; 
                    msg.rate = 0.85; 
                    msg.volume = {vol};

                    let started = false;
                    let ended = false;

                    msg.onstart = function() {{
                        started = true;
                        isSpeaking = true;
                        btn.innerText = "🔊 播放中，請跟著唸... (" + (playCount + 1) + "/3)";
                        btn.style.animation = "none";
                    }};

                    msg.onend = function() {{
                        if (ended) return; 
                        ended = true;
                        isSpeaking = false;
                        playCount++;
                        if (playCount < 3) {{
                            btn.innerText = "⏳ 停頓 2 秒... (" + playCount + "/3)";
                            timeoutId = setTimeout(speakWord, 2000); // 精準等待 2 秒再唸下一次
                        }} else {{
                            speakWord(); 
                        }}
                    }};

                    // 防禦機制
                    setTimeout(() => {{
                        if (!started && playCount === 0) {{
                            isSpeaking = false;
                            btn.innerText = "👉 手機限制：請點我開始播放";
                            btn.style.animation = "pulse 1.5s infinite";
                        }} else if (started && !ended) {{
                            msg.onend();
                        }}
                    }}, 3500);

                    window.speechSynthesis.speak(msg);
                }}

                // 嘗試自動觸發
                setTimeout(window.playForce, 500);
            </script>
            """
            st.components.v1.html(js_force, height=80)
            
            if st.button("💪 我記住了！繼續冒險！", use_container_width=True, type="primary"):
                st.session_state.force_learning = False
                st.session_state.play_auto_audio = True
                st.session_state.vk_input = ""
                st.session_state.current_vocab = pick_next_question(v_list, st.session_state.error_log, u_data['total_questions'])
                st.session_state.current_options = generate_options(st.session_state.current_vocab, v_list)
                st.rerun()

        # ==========================================
        # 正常答題模式 (出題自動循環，聽 1 次解鎖)
        # ==========================================
        else:
            if u_data['total_questions'] >= 20 and st.session_state.error_log:
                st.warning("🔥 累積滿 20 題！進入強制錯題複習模式！")
                
            v_html = f'<div class="vocab-card"><h3 style="margin:0; color:#7f8c8d; font-size: 1.2rem;">✨ 詠唱單字 ✨ {rev}</h3>'
            
            if diff == '簡單':
                v_html += f'<div class="vocab-word">{c_w["en"]}</div><h3 style="color:#e67e22; margin:0 0 15px 0; font-family: monospace; font-size: 1.5rem;">{ipa_d}</h3>'
                if c_w.get('hint'): v_html += f'<p style="color: #16a085; font-size: 1rem; margin: 0; background: #e8f8f5; padding: 8px; border-radius: 5px; font-weight: bold;">💡 提示：{c_w["hint"]}</p>'
            elif diff == '中等':
                word_en = c_w['en']
                w_len = len(word_en)
                if w_len <= 3: indices = [w_len // 2]
                else:
                    N = (w_len - 1) // 3 + 1
                    indices = [int(i * (w_len - 1) / (N - 1) + 0.5) for i in range(N)]
                hint_chars = [char if (i in indices or char in [' ', '-']) else '_' for i, char in enumerate(word_en)]
                hint_str = " ".join(hint_chars)
                v_html += f'<h1 style="color:#2980b9; font-size: 1.8rem; margin: 10px 0; font-weight: 800;">{c_w["zh"]}</h1>'
                v_html += f'<div class="vocab-hint-str">{hint_str}</div>'
                v_html += '<h3 style="color:#e67e22; margin:0 0 10px 0; font-family: monospace; font-size: 1rem;">請拼出對應的英文單字</h3>'
            elif diff == '困難':
                word_en = c_w['en']
                hint_chars = [char if char in [' ', '-'] else '_' for char in word_en]
                hint_str = " ".join(hint_chars)
                v_html += f'<h1 style="color:#2980b9; font-size: 1.8rem; margin: 10px 0; font-weight: 800;">{c_w["zh"]}</h1>'
                v_html += f'<div class="vocab-hint-str">{hint_str}</div>'
                v_html += '<h3 style="color:#e67e22; margin:0 0 10px 0; font-family: monospace; font-size: 1rem;">請完全拼出對應的英文單字</h3>'
            v_html += '</div>'
            st.markdown(v_html, unsafe_allow_html=True)
            
            # 判斷是否為新進題目，如果是就啟動自動播放
            auto_script = "setTimeout(window.playNormal, 500);" if st.session_state.play_auto_audio else ""
            st.session_state.play_auto_audio = False 
            
            # --- 出題畫面：自動循環 2 秒播一次 + 聽完解鎖作答區 ---
            btn_html = f"""
            <div style="text-align:center; margin-bottom: 20px;">
                <button id="normal-tts-btn" onclick="window.playNormal()" style="background-color: #3498db; color: white; border: none; padding: 10px 25px; font-size: 16px; border-radius: 8px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 80%; max-width: 300px; animation: pulse 2s infinite;">
                    🔊 準備出題... (若無聲請點擊)
                </button>
            </div>
            <style>@keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}</style>
            <script>
                // 隱藏作答區 (A/B/C/D 與 鍵盤)
                setTimeout(() => {{
                    const answerDiv = window.parent.document.getElementById('answer-zone');
                    if (answerDiv) answerDiv.style.opacity = '0.3';
                    if (answerDiv) answerDiv.style.pointerEvents = 'none';
                }}, 100);

                let isSpeaking = false;
                let loopTimeout = null;

                window.playNormal = function() {{ 
                    if (isSpeaking) return;
                    clearTimeout(loopTimeout);
                    if (window.speechSynthesis) window.speechSynthesis.cancel();
                    
                    let msg = new SpeechSynthesisUtterance("{c_w['en']}"); 
                    msg.lang = 'en-US'; 
                    msg.rate = 0.9; 
                    msg.volume = {vol}; 
                    
                    let started = false;
                    let ended = false;

                    msg.onstart = function() {{
                        started = true;
                        isSpeaking = true;
                        document.getElementById('normal-tts-btn').innerText = "🔊 播放中...";
                        document.getElementById('normal-tts-btn').style.animation = "none";
                    }};

                    msg.onend = function() {{
                        if(ended) return;
                        ended = true;
                        isSpeaking = false;
                        document.getElementById('normal-tts-btn').innerText = "🔊 播放 / 重聽單字";
                        
                        // 聽完 1 次後：解鎖作答區
                        const answerDiv = window.parent.document.getElementById('answer-zone');
                        if (answerDiv) {{
                            answerDiv.style.opacity = '1';
                            answerDiv.style.pointerEvents = 'auto';
                        }}
                        
                        // 設定 2 秒後自動重播
                        loopTimeout = setTimeout(window.playNormal, 2000);
                    }};

                    // 防禦機制：若被手機擋下來
                    setTimeout(() => {{
                        if (!started) {{
                            isSpeaking = false;
                            document.getElementById('normal-tts-btn').innerText = "👉 手機限制：請點我聽發音解鎖";
                            document.getElementById('normal-tts-btn').style.animation = "pulse 1.5s infinite";
                        }} else if (started && !ended) {{
                            msg.onend();
                        }}
                    }}, 3500);

                    window.speechSynthesis.speak(msg); 
                }};
                
                {auto_script}
            </script>
            """
            st.components.v1.html(btn_html, height=70)

            # --- 將整個作答區用 div 包覆，讓 JS 控制解鎖 ---
            st.markdown('<div id="answer-zone" style="transition: opacity 0.5s;">', unsafe_allow_html=True)
            
            if diff == '簡單':
                cA, cB = st.columns(2)
                with cA:
                    if st.button(f"A. {opts[0]}", use_container_width=True, key="ans_a"): process_ans(opts[0])
                    if st.button(f"C. {opts[2]}", use_container_width=True, key="ans_c"): process_ans(opts[2])
                with cB:
                    if st.button(f"B. {opts[1]}", use_container_width=True, key="ans_b"): process_ans(opts[1])
                    if st.button(f"D. {opts[3]}", use_container_width=True, key="ans_d"): process_ans(opts[3])
            else:
                st.markdown("<hr style='border: 1px dashed #bdc3c7; margin: 15px 0;'>", unsafe_allow_html=True)
                user_input = st.text_input("✍️ 施展拼寫魔法 (支援實體鍵盤與下方虛擬鍵盤)：", value=st.session_state.vk_input, key="text_input_field", autocomplete="off")
                
                if user_input != st.session_state.vk_input:
                    st.session_state.vk_input = user_input
                    
                st.markdown("<div style='text-align:center; color:#95a5a6; font-size:12px; margin-bottom:10px;'>👇 平板專用虛擬鍵盤 👇</div>", unsafe_allow_html=True)

                k_row1 = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
                k_row2 = ["a", "s", "d", "f", "g", "h", "j", "k", "l"]
                k_row3 = ["z", "x", "c", "v", "b", "n", "m"]

                c1 = st.columns(10)
                for i, k in enumerate(k_row1): c1[i].button(k.upper(), on_click=vk_add, args=(k,), key=f"vk_{k}", use_container_width=True)

                c2 = st.columns([0.5] + [1]*9 + [0.5])
                for i, k in enumerate(k_row2): c2[i+1].button(k.upper(), on_click=vk_add, args=(k,), key=f"vk_{k}", use_container_width=True)

                c3 = st.columns([1.5] + [1]*7 + [1.5])
                for i, k in enumerate(k_row3): c3[i+1].button(k.upper(), on_click=vk_add, args=(k,), key=f"vk_{k}", use_container_width=True)

                c4 = st.columns([2, 1, 1, 2])
                c4[0].button("␣ 空格", on_click=vk_add, args=(" ",), use_container_width=True)
                c4[1].button("- 連字", on_click=vk_add, args=("-",), use_container_width=True)
                c4[2].button("🔙 刪除", on_click=vk_del, use_container_width=True)
                c4[3].button("⚔️ 送出攻擊", type="primary", on_click=vk_submit, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True) # 結束作答區包覆

# ==================== 家長控制台 ====================
elif st.session_state.page == 'parent':
    st.markdown("<h1 style='text-align: center; color:#e67e22;'>👨‍👩‍👧 家長控制台</h1><hr>", unsafe_allow_html=True)
    c_top1, c_top2 = st.columns([1, 1])
    with c_top1:
        if st.button("⬅️ 返回大廳", use_container_width=True): st.session_state.page = 'login'; st.rerun()
    with c_top2:
        with st.expander("🔐 更改密碼"):
            o_pw = st.text_input("舊密碼", type="password")
            n_pw = st.text_input("新密碼", type="password")
            if st.button("確認修改"):
                if o_pw == st.session_state.settings["parent_password"] and n_pw.strip():
                    st.session_state.settings["parent_password"] = n_pw.strip(); save_json(SETTINGS_FILE, st.session_state.settings); st.success("✅ 成功！")
                else: st.error("錯誤")
    st.markdown("---")
    t1, t2, t3, t4 = st.tabs(["📊 學習報告與管理", "🏪 管理獎勵", "📚 題庫管理", "🖼️ 全圖鑑展示"])
    with t1:
        u_list = list(st.session_state.users.keys())
        if not u_list: st.info("無帳號")
        for u in u_list:
            d = load_user_data(u)
            e_log = load_error_log(u)
            c = st.session_state.users[u]['character']
            with st.expander(f"👤 {u} ({c})"):
                st.markdown("#### 📊 數據調整")
                cA, cB, cC, cD, cE = st.columns(5)
                n_lvl = cA.number_input("等級", min_value=1, value=d['level'], key=f"lvl_{u}")
                n_tq = cB.number_input("累積題數", min_value=0, value=d.get('total_questions', 0), key=f"tq_{u}")
                n_mdl = cC.number_input("勳章", min_value=0, value=d['medals'], key=f"mdl_{u}")
                n_dc = cD.number_input("倒地次數", min_value=0, max_value=4, value=d.get('death_count', 0), key=f"dc_{u}")
                new_diff = cE.selectbox("目前難度", ["簡單", "中等", "困難"], index=["簡單", "中等", "困難"].index(d.get("difficulty", "簡單")), key=f"diff_{u}")
                
                if n_lvl != d['level'] or n_tq != d.get('total_questions', 0) or n_mdl != d['medals'] or n_dc != d.get('death_count', 0) or new_diff != d.get("difficulty", "簡單"):
                    d['level'] = n_lvl; d['total_questions'] = n_tq; d['medals'] = n_mdl; d['death_count'] = n_dc; d['difficulty'] = new_diff
                    save_user_data(u, d); st.rerun()

                st.markdown("#### 🔴 錯題本")
                st.write(", ".join(e_log) if e_log else "無錯題！")
                
                st.markdown("#### 🎁 兌換紀錄管理")
                st.caption("💡 若小孩誤按兌換，可在此刪除紀錄，並在上方手動將「勳章」數量加回來。")
                if d.get('history'):
                    for i, item in enumerate(reversed(d['history'])):
                        hA, hB = st.columns([4, 1])
                        hA.text(item)
                        if hB.button("🗑️ 刪除", key=f"del_h_{u}_{i}"):
                            actual_idx = len(d['history']) - 1 - i
                            d['history'].pop(actual_idx); save_user_data(u, d); st.rerun()
                    if st.button("🧹 清空所有兌換紀錄", key=f"clr_h_{u}"):
                        d['history'] = []; save_user_data(u, d); st.rerun()
                else: st.write("無紀錄。")
                    
                st.markdown("#### ⚙️ 帳號管理")
                b1, b2 = st.columns(2)
                with b1:
                    if st.button(f"🔄 清空 {u} 學習資料", key=f"rs_{u}"): reset_user_data(u); st.rerun()
                with b2:
                    if st.button(f"🗑️ 刪除 {u} 帳號", key=f"dl_{u}"): delete_user(u); st.rerun()
    with t2:
        st.subheader("新增獎勵")
        with st.form("add_r"):
            n_r = st.text_input("名稱")
            n_c = st.number_input("勳章數", min_value=1, value=1)
            n_i = st.selectbox("圖示", EMOJI_LIST)
            if st.form_submit_button("➕ 新增"):
                if n_r.strip():
                    df = pd.read_csv(REWARD_FILE) if os.path.exists(REWARD_FILE) else pd.DataFrame(columns=["reward", "cost_medals", "icon"])
                    df = pd.concat([df, pd.DataFrame([{"reward": n_r, "cost_medals": n_c, "icon": n_i}])], ignore_index=True)
                    df.to_csv(REWARD_FILE, index=False, encoding="utf-8-sig"); st.success("✅ 成功！"); st.rerun()
        st.subheader("目前清單")
        c_r = load_csv(REWARD_FILE)
        for idx, r in enumerate(c_r):
            cA, cB = st.columns([4, 1])
            with cA: st.info(f"{r['icon']} {r['reward']} (需 {r['cost_medals']})")
            with cB:
                if st.button("🗑️", key=f"d_r_{idx}"):
                    df = pd.read_csv(REWARD_FILE); df.drop(idx).to_csv(REWARD_FILE, index=False, encoding="utf-8-sig"); st.rerun()
    with t3:
        st.subheader("編輯單字庫 (可直接修改儲存)")
        v_df = pd.read_csv(VOCAB_FILE) if os.path.exists(VOCAB_FILE) else pd.DataFrame(columns=["en", "zh", "hint"])
        edited_df = st.data_editor(v_df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 儲存題庫修改", type="primary"):
            if "sentence" in edited_df.columns:
                edited_df = edited_df.drop(columns=["sentence"])
            edited_df.to_csv(VOCAB_FILE, index=False, encoding="utf-8-sig"); st.success("題庫更新成功！")
    with t4:
        st.subheader("🌟 英雄進化型態展示")
        for h_k, h_v in CHARACTERS.items():
            st.markdown(f"**{h_k} 家族**")
            h_cols = st.columns(min(len(h_v["stages"]), 5))
            for idx, (h_id, h_name) in enumerate(h_v["stages"]):
                h_cols[idx].image(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/{h_id}.gif", caption=f"Lv.{1 if idx==0 else (5 if idx==1 else 10)} {h_name}")
        st.markdown("---")
        st.subheader(f"🏆 傳說 BOSS 圖鑑 ({len(BOSSES)} 種)")
        b_cols = st.columns(8)
        for i, b in enumerate(BOSSES):
            b_cols[i % 8].image(b['url'], caption=b['name'])
        st.markdown("---")
        st.subheader(f"👾 一般怪物圖鑑 ({len(MONSTERS)} 種)")
        m_cols = st.columns(10)
        for i, m in enumerate(MONSTERS):
            m_cols[i % 10].image(m['url'], caption=m['name'])
