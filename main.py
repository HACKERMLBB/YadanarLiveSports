import os
import asyncio
import threading
import requests
import xml.etree.ElementTree as ET
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_IDS = [x.strip() for x in os.getenv("CHANNEL_IDS", "").split(",") if x.strip()]

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Premium Sports Bot Running!"
@app_flask.route('/ping')
def ping():
    return "OK", 200
@app_flask.route('/health')
def health():
    return "Bot is Alive", 200
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False)

# ========== LANGUAGES ==========
USER_LANG = {}
LANGS = {
    "si": {"name": "සිංහල", "welcome": "👋 ආයුබෝවන්! ඔබේ ක්‍රීඩාව තෝරන්න", "choose": "👇 ඔබේ ක්‍රීඩාව තෝරන්න 👇"},
    "ta": {"name": "தமிழ்", "welcome": "👋 வணக்கம்! உங்கள் விளையாட்டை தேர்வு செய்யவும்", "choose": "👇 உங்கள் விளையாட்டை தேர்வு செய்யவும் 👇"},
    "en": {"name": "English", "welcome": "👋 Welcome, Champion!", "choose": "👇 CHOOSE YOUR SPORT BELOW 👇"},
    "hi": {"name": "हिन्दी", "welcome": "👋 नमस्ते! अपना खेल चुनें", "choose": "👇 अपना खेल चुनें 👇"},
    "ur": {"name": "اردو", "welcome": "👋 خوش آمدید! اپنا کھیل منتخب کریں", "choose": "👇 اپنا کھیل منتخب کریں 👇"},
    "bn": {"name": "বাংলা", "welcome": "👋 স্বাগতম! আপনার খেলা বেছে নিন", "choose": "👇 আপনার খেলা বেছে নিন 👇"},
    "ar": {"name": "العربية", "welcome": "👋 مرحبا! اختر رياضتك", "choose": "👇 اختر رياضتك 👇"},
    "es": {"name": "Español", "welcome": "👋 ¡Bienvenido, Campeón!", "choose": "👇 ELIGE TU DEPORTE 👇"},
    "fr": {"name": "Français", "welcome": "👋 Bienvenue, Champion!", "choose": "👇 CHOISISSEZ VOTRE SPORT 👇"},
    "pt": {"name": "Português", "welcome": "👋 Bem-vindo, Campeão!", "choose": "👇 ESCOLHA SEU ESPORTE 👇"},
    "ru": {"name": "Русский", "welcome": "👋 Добро пожаловать, Чемпион!", "choose": "👇 ВЫБЕРИТЕ СВОЙ СПОРТ 👇"},
    "zh": {"name": "中文", "welcome": "👋 欢迎，冠军！", "choose": "👇 选择你的运动 👇"},
    "ja": {"name": "日本語", "welcome": "👋 ようこそ、チャンピオン！", "choose": "👇 スポーツを選んでください 👇"},
    "ko": {"name": "한국어", "welcome": "👋 환영합니다, 챔피언!", "choose": "👇 스포츠를 선택하세요 👇"},
    "de": {"name": "Deutsch", "welcome": "👋 Willkommen, Champion!", "choose": "👇 WÄHLE DEINEN SPORT 👇"},
    "it": {"name": "Italiano", "welcome": "👋 Benvenuto, Campione!", "choose": "👇 SCEGLI IL TUO SPORT 👇"},
    "nl": {"name": "Nederlands", "welcome": "👋 Welkom, Kampioen!", "choose": "👇 KIES JE SPORT 👇"},
    "tr": {"name": "Türkçe", "welcome": "👋 Hoş Geldin, Şampiyon!", "choose": "👇 SPORUNU SEÇ 👇"},
    "fa": {"name": "فارسی", "welcome": "👋 خوش آمدید، قهرمان!", "choose": "👇 ورزش خود را انتخاب کنید 👇"},
    "ms": {"name": "Bahasa Melayu", "welcome": "👋 Selamat Datang, Juara!", "choose": "👇 PILIH SUKAN ANDA 👇"},
    "id": {"name": "Bahasa Indonesia", "welcome": "👋 Selamat Datang, Juara!", "choose": "👇 PILIH OLAHRAGA ANDA 👇"},
    "th": {"name": "ไทย", "welcome": "👋 ยินดีต้อนรับ แชมป์เปี้ยน!", "choose": "👇 เลือกกีฬาของคุณ 👇"},
    "vi": {"name": "Tiếng Việt", "welcome": "👋 Chào mừng, Nhà vô địch!", "choose": "👇 CHỌN MÔN THỂ THAO CỦA BẠN 👇"},
    "tl": {"name": "Filipino", "welcome": "👋 Maligayang Pagdating, Kampeon!", "choose": "👇 PILIIN ANG IYONG SPORT 👇"},
    "ne": {"name": "नेपाली", "welcome": "👋 नमस्ते, च्याम्पियन!", "choose": "👇 आफ्नो खेल छान्नुहोस् 👇"},
    "pa": {"name": "ਪੰਜਾਬੀ", "welcome": "👋 ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ, ਚੈਂਪੀਅਨ!", "choose": "👇 ਆਪਣੀ ਖੇਡ ਚੁਣੋ 👇"},
    "te": {"name": "తెలుగు", "welcome": "👋 స్వాగతం, ఛాంపియన్!", "choose": "👇 మీ క్రీడను ఎంచుకోండి 👇"},
    "ml": {"name": "മലയാളം", "welcome": "👋 സ്വാഗതം, ചാമ്പ്യൻ!", "choose": "👇 നിങ്ങളുടെ കായികം തിരഞ്ഞെടുക്കുക 👇"},
    "kn": {"name": "ಕನ್ನಡ", "welcome": "👋 ಸುಸ್ವಾಗತ, ಚಾಂಪಿಯನ್!", "choose": "👇 ನಿಮ್ಮ ಕ್ರೀಡೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ 👇"},
    "mr": {"name": "मराठी", "welcome": "👋 नमस्कार, चॅम्पियन!", "choose": "👇 तुमचा खेळ निवडा 👇"},
    "gu": {"name": "ગુજરાતી", "welcome": "👋 નમસ્તે, ચેમ્પિયન!", "choose": "👇 તમારી રમત પસંદ કરો 👇"},
    "or": {"name": "ଓଡ଼ିଆ", "welcome": "👋 ନମସ୍କାର, ଚାମ୍ପିଅନ୍!", "choose": "👇 ଆପଣଙ୍କ ଖେଳ ବାଛନ୍ତୁ 👇"},
    "my": {"name": "မြန်မာ", "welcome": "👋 ကြိုဆိုပါတယ်၊ ချန်ပီယံ!", "choose": "👇 သင့်အားကစားကို ရွေးချယ်ပါ 👇"},
    "km": {"name": "ខ្មែរ", "welcome": "👋 សូមស្វាគមន៍ ជើងឯក!", "choose": "👇 ជ្រើសរើសកីឡារបស់អ្នក 👇"},
    "lo": {"name": "ລາວ", "welcome": "👋 ຍິນດີຕ້ອນຮັບ ແຊ້ມ!", "choose": "👇 ເລືອກກິລາຂອງທ່ານ 👇"},
    "sw": {"name": "Kiswahili", "welcome": "👋 Karibu, Bingwa!", "choose": "👇 CHAGUA MICHEZO YAKO 👇"},
    "ha": {"name": "Hausa", "welcome": "👋 Barka da zuwa, Zakara!", "choose": "👇 ZAƁI WASA 👇"},
    "am": {"name": "አማርኛ", "welcome": "👋 እንኳን ደህና መጣህ, ሻምፒዮን!", "choose": "👇 ስፖርትህን ምረጥ 👇"},
    "uk": {"name": "Українська", "welcome": "👋 Ласкаво просимо, Чемпіоне!", "choose": "👇 ОБЕРІТЬ СВІЙ СПОРТ 👇"},
    "pl": {"name": "Polski", "welcome": "👋 Witaj, Mistrzu!", "choose": "👇 WYBIERZ SWÓJ SPORT 👇"},
    "sv": {"name": "Svenska", "welcome": "👋 Välkommen, Mästare!", "choose": "👇 VÄLJ DIN SPORT 👇"},
    "fi": {"name": "Suomi", "welcome": "👋 Tervetuloa, Mestari!", "choose": "👇 VALITSE URHEILUSI 👇"},
    "el": {"name": "Ελληνικά", "welcome": "👋 Καλώς ήρθες, Πρωταθλητή!", "choose": "👇 ΔΙΑΛΕΞΕ ΤΟ ΑΘΛΗΜΑ ΣΟΥ 👇"},
    "he": {"name": "עברית", "welcome": "👋 ברוך הבא, אלוף!", "choose": "👇 בחר את הספורט שלך 👇"},
    "ro": {"name": "Română", "welcome": "👋 Bine ai venit, Campioane!", "choose": "👇 ALEGE SPORTUL TĂU 👇"},
}
def get_text(chat_id, key):
    lang = USER_LANG.get(str(chat_id), "en")
    return LANGS.get(lang, LANGS["en"]).get(key, LANGS["en"][key])

def bar(v1, v2, label):
    try:
        a = float(str(v1).replace('%','')); b = float(str(v2).replace('%','')); tot = a + b
        if tot == 0: return f"{label}\n{a} - {b}\n"
        p = int((a/tot)*12); q = 12 - p
        return f"{label}\n{'🟦'*p}{'⬜'*q} {a:.0f}% - {b:.0f}%\n"
    except: return f"{label}: {v1} - {v2}\n"
def progress_bar(minute):
    try:
        m = int(str(minute).replace("'","").split("+")[0]); p = min(int(m/90*10), 10)
        return f"{'🟩'*p}{'⬜'*(10-p)} {m}'"
    except: return ""
def fetch_board(sport, league):
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
        return requests.get(url, timeout=12).json().get('events', [])
    except: return []
def fetch_summary(sport, league, eid):
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event={eid}"
        return requests.get(url, timeout=12).json()
    except: return None
def fetch_standings(sport, league):
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/standings"
        return requests.get(url, timeout=12).json()
    except: return None

# ========== NEWS + SCORE SYSTEM ==========
ALL_SCORES_CACHE = []  # News එකට Score හොයන්න

def fetch_news():
    news = []
    # 1. ESPN News
    try:
        r = requests.get("https://site.api.espn.com/apis/site/v2/sports/cricket/news?limit=10", timeout=10).json()
        for a in r.get('articles', [])[:5]:
            news.append({"title": a.get('headline',''), "desc": a.get('description','')[:150], "source": "ESPN Cricket", "link": a.get('links',{}).get('web',{}).get('href','')})
    except: pass
    try:
        r = requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/news?limit=10", timeout=10).json()
        for a in r.get('articles', [])[:5]:
            news.append({"title": a.get('headline',''), "desc": a.get('description','')[:150], "source": "ESPN Football", "link": a.get('links',{}).get('web',{}).get('href','')})
    except: pass
    # 2. Google News RSS - U19, Asia Cup වගේ News ඔක්කොම එනවා
    rss_urls = [
        "https://news.google.com/rss/search?q=cricket+live+score&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=U19+Asia+Cup+cricket&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=football+live+score&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=IPL+cricket&hl=en-IN&gl=IN&ceid=IN:en",
    ]
    for url in rss_urls:
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:4]:
                t = item.findtext("title","")
                link = item.findtext("link","")
                news.append({"title": t, "desc": "", "source": "Google News", "link": link})
        except: pass
    # Duplicate අයින් කරනවා
    seen=set(); uniq=[]
    for n in news:
        if n["title"] not in seen:
            seen.add(n["title"]); uniq.append(n)
    return uniq[:12]

def find_score_for_news(title):
    # News Title එකේ තියෙන Team එකට Score එක හොයනවා
    title_low = title.lower()
    for s in ALL_SCORES_CACHE:
        # Score text එකේ Team නම් තියෙනවද බලනවා
        s_low = s.lower()
        # Team නම් 2ක් වත් Match වෙනවද?
        words = [w for w in ["india","pakistan","sri lanka","australia","england","bangladesh","new zealand","south africa","afghanistan","nepal","west indies"] if w in title_low]
        if len(words)>=1:
            for w in words:
                if w in s_low:
                    # Score එක කෙටියෙන් ගන්නවා
                    lines = s.split("\n")
                    short = "\n".join([l for l in lines if "┃" in l or "Won" in l or "Draw" in l][:4])
                    return short
    return ""

def get_lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇱🇰 සිංහල", callback_data="lang_si"), InlineKeyboardButton("🇮🇳 தமிழ்", callback_data="lang_ta")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"), InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="lang_hi")],
        [InlineKeyboardButton("🇵🇰 اردو", callback_data="lang_ur"), InlineKeyboardButton("🇧🇩 বাংলা", callback_data="lang_bn")],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"), InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")],
        [InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr"), InlineKeyboardButton("🇵🇹 Português", callback_data="lang_pt")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"), InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh")],
        [InlineKeyboardButton("🇯🇵 日本語", callback_data="lang_ja"), InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko")],
        [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de"), InlineKeyboardButton("🇮🇹 Italiano", callback_data="lang_it")],
        [InlineKeyboardButton("🇳🇱 Nederlands", callback_data="lang_nl"), InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"), InlineKeyboardButton("🇲🇾 Melayu", callback_data="lang_ms")],
        [InlineKeyboardButton("🇮🇩 Indonesia", callback_data="lang_id"), InlineKeyboardButton("🇹🇭 ไทย", callback_data="lang_th")],
        [InlineKeyboardButton("🇻🇳 Tiếng Việt", callback_data="lang_vi"), InlineKeyboardButton("🇵🇭 Filipino", callback_data="lang_tl")],
        [InlineKeyboardButton("🇳🇵 नेपाली", callback_data="lang_ne"), InlineKeyboardButton("🇮🇳 ਪੰਜਾਬੀ", callback_data="lang_pa")],
        [InlineKeyboardButton("🇮🇳 తెలుగు", callback_data="lang_te"), InlineKeyboardButton("🇮🇳 മലയാളം", callback_data="lang_ml")],
        [InlineKeyboardButton("🇮🇳 ಕನ್ನಡ", callback_data="lang_kn"), InlineKeyboardButton("🇮🇳 मराठी", callback_data="lang_mr")],
        [InlineKeyboardButton("🇮🇳 ગુજરાતી", callback_data="lang_gu"), InlineKeyboardButton("🇮🇳 ଓଡ଼ିଆ", callback_data="lang_or")],
        [InlineKeyboardButton("🇲🇲 မြန်မာ", callback_data="lang_my"), InlineKeyboardButton("🇰🇭 ខ្មែរ", callback_data="lang_km")],
        [InlineKeyboardButton("🇱🇦 ລາວ", callback_data="lang_lo"), InlineKeyboardButton("🇹🇿 Kiswahili", callback_data="lang_sw")],
        [InlineKeyboardButton("🇳🇬 Hausa", callback_data="lang_ha"), InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am")],
        [InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_uk"), InlineKeyboardButton("🇵🇱 Polski", callback_data="lang_pl")],
        [InlineKeyboardButton("🇸🇪 Svenska", callback_data="lang_sv"), InlineKeyboardButton("🇫🇮 Suomi", callback_data="lang_fi")],
        [InlineKeyboardButton("🇬🇷 Ελληνικά", callback_data="lang_el"), InlineKeyboardButton("🇮🇱 עברית", callback_data="lang_he")],
        [InlineKeyboardButton("🇷🇴 Română", callback_data="lang_ro")],
        [InlineKeyboardButton("Back to Menu", callback_data="menu_start")]
    ])

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 YOUR LANGUAGES", callback_data="menu_lang")],
        [InlineKeyboardButton("📰 SPORTS NEWS + SCORE", callback_data="menu_news")],
        [InlineKeyboardButton("Football", callback_data="menu_football"), InlineKeyboardButton("Cricket", callback_data="menu_cricket")],
        [InlineKeyboardButton("IPL LIVE", callback_data="menu_ipl"), InlineKeyboardButton("LPL / SL", callback_data="menu_lpl")],
        [InlineKeyboardButton("Basketball", callback_data="menu_basketball"), InlineKeyboardButton("Tennis", callback_data="menu_tennis")],
        [InlineKeyboardButton("Hockey", callback_data="menu_hockey"), InlineKeyboardButton("Volleyball", callback_data="menu_volleyball")],
        [InlineKeyboardButton("Table Tennis", callback_data="menu_tabletennis"), InlineKeyboardButton("Baseball", callback_data="menu_baseball")],
        [InlineKeyboardButton("NFL", callback_data="menu_nfl"), InlineKeyboardButton("Badminton", callback_data="menu_badminton")],
        [InlineKeyboardButton("F1 Racing", callback_data="menu_f1"), InlineKeyboardButton("Golf", callback_data="menu_golf")],
        [InlineKeyboardButton("UFC / Boxing", callback_data="menu_ufc"), InlineKeyboardButton("Rugby", callback_data="menu_rugby")],
        [InlineKeyboardButton("Kabaddi", callback_data="menu_kabaddi"), InlineKeyboardButton("E-Sports", callback_data="menu_esports")],
        [InlineKeyboardButton("FIFA", callback_data="menu_fifa"), InlineKeyboardButton("LIVE ALL", callback_data="menu_live")],
        [InlineKeyboardButton("RESULTS", callback_data="menu_results"), InlineKeyboardButton("POINTS TABLE", callback_data="menu_table")],
        [InlineKeyboardButton("TOMORROW", callback_data="menu_tomorrow"), InlineKeyboardButton("SEARCH", callback_data="menu_search")],
        [InlineKeyboardButton("Join Channel", url="https://t.me/bigolive_asia")]
    ])
def get_back_keyboard(key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Refresh", callback_data=f"menu_{key}")],
        [InlineKeyboardButton("Back to Menu", callback_data="menu_start")],
        [InlineKeyboardButton("Join Channel", url="https://t.me/bigolive_asia")]
    ])

def format_premium(ev, sport, league):
    try:
        comp = ev['competitions'][0]; competitors = comp['competitors']
        state = ev.get('status', {}).get('type', {}).get('state')
        short = ev.get('status', {}).get('type', {}).get('shortDetail','')
        detail = ev.get('status', {}).get('type', {}).get('detail','')
        eid = ev.get('id')
        venue = comp.get('venue', {}).get('fullName','Unknown Stadium') if comp.get('venue') else 'Unknown Stadium'
        city = comp.get('venue', {}).get('address', {}).get('city','') if comp.get('venue') else ''
        comp_name = ev.get('season', {}).get('slug','').replace('-',' ').upper() if ev.get('season') else league.upper()
        league_emoji = {"ENG.1":"🏴󐁧󐁢󐁥󐁮󐁧󐁿","ESP.1":"🇪🇸","GER.1":"🇩🇪","ITA.1":"🇮🇹","FRA.1":"🇫🇷","UEFA.CHAMPIONS":"⭐","NBA":"🏀","ATP":"🎾","WTA":"🎾","MLB":"⚾","NFL":"🏈","BWF":"🏸","F1":"🏎️","PGA":"⛳","MMA":"🥊","RUGBY":"🏉"}.get(league.upper(),"🏆")
        h = competitors[0]; a = competitors[1] if len(competitors)>1 else None
        h_name = h['team'].get('displayName',''); a_name = a['team'].get('displayName','') if a else ""
        h_short = h['team'].get('abbreviation',''); a_short = a['team'].get('abbreviation','') if a else ""
        h_score = h.get('score','0'); a_score = a.get('score','0') if a else "0"
        h_lines = h.get('linescores', []); a_lines = a.get('linescores', []) if a else []
        h_line_txt = " | ".join([str(x.get('value','')) for x in h_lines]) if h_lines else ""
        a_line_txt = " | ".join([str(x.get('value','')) for x in a_lines]) if a_lines else ""
        winner = ""
        if state == 'post':
            try:
                if float(h_score) > float(a_score): winner = f"👑 {h_name} Won!"
                elif float(a_score) > float(h_score): winner = f"👑 {a_name} Won!"
                else: winner = "🤝 Draw Match"
            except: winner = "✅ Full Time"
        t = ""
        t += "╔══════════════════════╗\n"
        if state == 'in': t += f"║  🔴 <b>LIVE NOW</b>  •  {short}  ║\n"
        elif state == 'post': t += f"║  ✅ <b>FULL TIME</b>  •  {detail}  ║\n"
        else: t += f"║  🕒 <b>UPCOMING</b>  •  {short}  ║\n"
        t += "╚══════════════════════╝\n\n"
        t += f"{league_emoji} <b>{comp_name}</b>\n🏟️ {venue} {city}\n"
        if state == 'in' and sport == "soccer": t += f"⏱️ Match Progress: {progress_bar(short)}\n"
        t += "\n┏━━━━━━━━━━━━━━━━━━━━┓\n"
        if state == 'pre': t += f"┃  <b>{h_name}</b>\n┃         <b>VS</b>\n┃  <b>{a_name}</b>\n"
        else:
            t += f"┃  <b>{h_name}</b>  [{h_short}]\n┃      <b> {h_score}  -  {a_score} </b>\n┃  <b>{a_name}</b>  [{a_short}]\n"
            if h_line_txt: t += f"┃  {h_short}: {h_line_txt}\n"
            if a_line_txt: t += f"┃  {a_short}: {a_line_txt}\n"
        t += "┗━━━━━━━━━━━━━━━━━━━━┛\n"
        if winner: t += f"\n{winner}\n"
        if state == 'pre':
            t += "\n<i>⏳ Match not started yet. Stay tuned!</i>\n━━━━━━━━━━━━━━━━━━━━━━\n"; return t
        if sport == "cricket":
            t += f"\n🏏 <b>CRICKET DETAILS</b>\n──────────────────────\n📍 {detail}\n📊 {h_name}: {h_score}\n📊 {a_name}: {a_score}\n\n━━━━━━━━━━━━━━━━━━━━━━\n💬 <i>Follow for more live updates</i>  •  @bigolive_asia\n"; return t
        dj = fetch_summary(sport, league, eid)
        goals, cards, subs, timeline = [], [], [], []; stats = {}
        if dj:
            for d in dj.get('details', []):
                txt = d.get('type', {}).get('text',''); team = d.get('team', {}).get('shortDisplayName','')
                ath = d['athletesInvolved'][0].get('displayName','') if d.get('athletesInvolved') else ''
                clock = d.get('clock', {}).get('displayValue',''); tl = txt.lower()
                if 'goal' in tl or 'penalty - scored' in tl:
                    is_pen = 'penalty' in tl; goals.append((clock, ath, team, is_pen)); timeline.append(f"  {clock}'  ⚽ {ath} ({team}){' [PEN]' if is_pen else ''}")
                elif 'yellow' in tl: cards.append(f"  {clock}'  🟨 {ath} ({team})"); timeline.append(f"  {clock}'  🟨 {ath}")
                elif 'red' in tl: cards.append(f"  {clock}'  🟥 {ath} ({team})"); timeline.append(f"  {clock}'  🟥 {ath}")
                elif 'substitution' in tl: subs.append(f"  {clock}'  🔄 {ath} ({team})")
                elif 'touchdown' in tl or 'field goal' in tl or 'home run' in tl: timeline.append(f"  {clock}'  🔥 {ath} - {txt} ({team})")
            try:
                teams = dj.get('boxscore', {}).get('teams', [])
                if len(teams) >= 2:
                    for tm in teams:
                        for st in tm.get('statistics', []):
                            n = st.get('name')
                            if n in ['possessionPct','totalShots','shotsOnTarget','wonCorners','fouls','offsides','saves','rebounds','assists']:
                                if n not in stats: stats[n] = []
                                stats[n].append(st.get('displayValue'))
            except: pass
        if timeline:
            t += f"\n📜 <b>MATCH TIMELINE</b>\n──────────────────────\n"
            for line in timeline: t += f"{line}\n"
        if goals:
            t += f"\n⚽ <b>GOAL SCORERS</b>\n──────────────────────\n"
            for clock, ath, team, is_pen in goals:
                pen = " 🎯 PENALTY" if is_pen else ""; t += f"  ⏰ {clock}'  <b>{ath}</b>\n       └ {team}{pen}\n"
        if cards:
            t += f"\n🟨 <b>CARDS</b>\n──────────────────────\n"
            for c in cards: t += f"{c}\n"
        if subs:
            t += f"\n🔄 <b>SUBSTITUTIONS</b>\n──────────────────────\n"
            for s in subs[:5]: t += f"{s}\n"
        if stats:
            t += f"\n📊 <b>MATCH STATISTICS</b>\n──────────────────────\n"
            labels = {'possessionPct': f"⚽ Possession  {h_short} vs {a_short}",'totalShots': f"🥅 Total Shots  {h_short} vs {a_short}",'shotsOnTarget': f"🎯 Shots on Target",'wonCorners': f"🚩 Corners",'fouls': f"🚨 Fouls",'rebounds': f"🏀 Rebounds",'assists': f"🎯 Assists"}
            for k, lab in labels.items():
                if k in stats and len(stats[k])>=2:
                    v1, v2 = stats[k][0], stats[k][1]
                    if k == 'possessionPct': t += bar(v1, v2, lab) + "\n"
                    else:
                        try:
                            a1 = float(v1); b1 = float(v2); tot = a1+b1
                            if tot>0:
                                p = int((a1/tot)*10); t += f"{lab}\n{'🟦'*p}{'🟧'*(10-p)}  {v1} - {v2}\n\n"
                            else: t += f"{lab}: {v1} - {v2}\n"
                        except: t += f"{lab}: {v1} - {v2}\n"
        else:
            if state == 'in': t += f"\n📊 <i>Stats are updating live...</i>\n"
        t += "\n━━━━━━━━━━━━━━━━━━━━━━\n💬 <i>Follow for more live updates</i>  •  @bigolive_asia\n"
        return t
    except Exception as e: return f"Error: {e}\n━━━━━━━━━━━━━━\n"

SPORT_CONFIG = {
    "football": ("⚽ FOOTBALL", [("soccer","eng.1"),("soccer","esp.1"),("soccer","ger.1"),("soccer","ita.1"),("soccer","fra.1"),("soccer","uefa.champions")]),
    "cricket": ("🏏 CRICKET", [("cricket","")]),
    "ipl": ("🔥 IPL - INDIAN PREMIER LEAGUE", [("cricket","")]),
    "lpl": ("🇱🇰 LPL / SRI LANKA", [("cricket","")]),
    "basketball": ("🏀 BASKETBALL", [("basketball","nba")]),
    "tennis": ("🎾 TENNIS", [("tennis","atp"),("tennis","wta")]),
    "hockey": ("🏑 FIELD HOCKEY", [("field-hockey","fih")]),
    "volleyball": ("🏐 VOLLEYBALL", [("volleyball","fivb")]),
    "tabletennis": ("🏓 TABLE TENNIS", [("table-tennis","ittf")]),
    "baseball": ("⚾ BASEBALL", [("baseball","mlb")]),
    "nfl": ("🏈 AMERICAN FOOTBALL", [("football","nfl")]),
    "badminton": ("🏸 BADMINTON", [("badminton","bwf")]),
    "fifa": ("🏆 FIFA", [("soccer","fifa.world"),("soccer","fifa.friendly")]),
    "f1": ("🏎️ FORMULA 1", [("racing","f1")]),
    "golf": ("⛳ GOLF", [("golf","pga")]),
    "ufc": ("🥊 UFC / MMA / BOXING", [("mma","mma"),("boxing","boxing")]),
    "rugby": ("🏉 RUGBY", [("rugby","rugby")]),
    "kabaddi": ("🤼 KABADDI", [("cricket","")]),
    "esports": ("🎮 E-SPORTS", [("soccer","eng.1")]),
}

def get_data(key):
    global ALL_SCORES_CACHE
    title, leagues = SPORT_CONFIG[key]
    live, up, res = [], [], []
    for sport, league in leagues:
        if sport == "cricket":
            events = []
            urls = ["https://site.api.espn.com/apis/site/v2/sports/cricket/scoreboard", "https://site.api.espn.com/apis/site/v2/sports/cricket/scoreboard?limit=100"]
            for u in urls:
                try:
                    r = requests.get(u, headers={"User-Agent":"Mozilla/5.0"}, timeout=12).json()
                    events += r.get('events', [])
                except: pass
            seen=set(); uniq=[]
            for ev in events:
                if ev.get('id') not in seen:
                    seen.add(ev.get('id')); uniq.append(ev)
            events = uniq
            for ev in events:
                name = (ev.get('name','') + " " + ev.get('shortName','')).lower()
                if key == "ipl" and "ipl" not in name and "indian premier" not in name: continue
                if key == "lpl" and "lanka" not in name and "sri lanka" not in name and "lpl" not in name: continue
                if key == "kabaddi": continue
                state = ev.get('status',{}).get('type',{}).get('state')
                txt = format_premium(ev, "cricket", "")
                if state=='in': live.append(txt)
                elif state=='pre': up.append(txt)
                elif state=='post': res.append(txt)
            continue
        events = fetch_board(sport, league)
        for ev in events:
            state = ev.get('status',{}).get('type',{}).get('state')
            txt = format_premium(ev, sport, league)
            if state=='in': live.append(txt)
            elif state=='pre': up.append(txt)
            elif state=='post': res.append(txt)
    if key == "kabaddi": live = ["🤼 <b>PRO KABADDI LEAGUE</b>\n\n📍 Live Score Coming Soon\n🏆 Season Starts Soon - Stay Tuned!\n━━━━━━━━━━━━━━━━━━━━━━\n"]
    if key == "esports": live = ["🎮 <b>E-SPORTS LIVE</b>\n\n🔥 PUBG Mobile - PMPL\n🔥 Free Fire - FFWS\n🔥 Valorant Champions\n\n📍 Live Scores Update Soon\n━━━━━━━━━━━━━━━━━━━━━━\n"]
    ALL_SCORES_CACHE.extend(live + res)
    ALL_SCORES_CACHE = ALL_SCORES_CACHE[-100:]
    return title, live, up, res

def format_full(key):
    title, live, up, res = get_data(key)
    t = f"✨ <b>{title}  •  PREMIUM LIVE</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    t += "🔴 <b>LIVE NOW</b>\n\n"; t += "".join(live[:2]) if live else "😴 No Live Match Right Now\n━━━━━━━━━━━━━━━━━━━━━━\n"
    t += "\n✅ <b>PREVIOUS RESULTS</b>\n\n"; t += "".join(res[:3]) if res else "No Results Yet\n━━━━━━━━━━━━━━━━━━━━━━\n"
    t += "\n🕒 <b>UPCOMING</b>\n\n"; t += "".join(up[:3]) if up else "No Upcoming\n━━━━━━━━━━━━━━━━━━━━━━\n"
    return t

def format_news():
    # Score Cache එක Update කරනවා - News එකට Score හොයන්න
    for k in ["cricket","football","basketball","tennis"]:
        get_data(k)
    news = fetch_news()
    t = "📰 <b>SPORTS NEWS + LIVE SCORE</b> 📰\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for n in news:
        score = find_score_for_news(n["title"])
        t += f"📰 <b>{n['title']}</b>\n"
        if n["desc"]: t += f"{n['desc']}\n"
        if score:
            t += f"\n📊 <b>SCORE:</b>\n{score}\n"
        t += f"🔗 <a href=\"{n['link']}\">Read Full News</a>  •  {n['source']}\n"
        t += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    t += "⚡ <i>Powered by @bigolive_asia</i>"
    return t[:4000]

def get_welcome(chat_id):
    w = get_text(chat_id, "welcome"); c = get_text(chat_id, "choose")
    return ("╔══════════════════════╗\n║  ✨ 🏆 PREMIUM SPORTS 🏆 ✨  ║\n╚══════════════════════╝\n\n    ⚽  🏏  🏀  🎾  🏈  ⚾\n  <b>YADANAR LIVE SPORTS</b>\n  <b>PREMIUM SPORTS</b>\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
    f"{w}\n━━━━━━━━━━━━━━━━━━━━━━\n\n🔴 <b>LIVE SCORES</b>  •  Every 3 Minutes\n⚽ <b>GOAL ALERTS</b>  •  Instant Update\n📰 <b>NEWS + SCORE</b>  •  All Matches\n🏆 <b>IPL • LPL • EPL • FIFA</b>\n🏏 <b>CRICKET • FOOTBALL • TENNIS</b>\n📊 <b>STATS • TABLE • RESULTS</b>\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
    f"{c}\n━━━━━━━━━━━━━━━━━━━━━━\n\n💎 <i>Fastest • Beautiful • Free</i>\n💬 <i>Join Our Family For Daily Live Updates</i>\n\n━━━━━━━━━━━━━━━━━━━━━━\nPOWERD BY @bigolive_asia")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_welcome(update.effective_chat.id), parse_mode="HTML", reply_markup=get_main_keyboard())
async def send_sport_to_chat(chat_id, context, key):
    txt = format_full(key); await context.bot.send_message(chat_id=chat_id, text=txt[:4000], parse_mode="HTML", reply_markup=get_back_keyboard(key))
async def send_news_to_chat(chat_id, context):
    msg = await context.bot.send_message(chat_id=chat_id, text="📰 Loading News + Scores...")
    txt = format_news()
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=txt, parse_mode="HTML", reply_markup=get_back_keyboard("news"))
async def send_live_to_chat(chat_id, context):
    msg = await context.bot.send_message(chat_id=chat_id, text="✨ Loading Premium Live...")
    text = "✨ <b>🔴 TOP LIVE - PREMIUM</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key in SPORT_CONFIG.keys():
        title, live, up, res = get_data(key); text += f"<b>{title}</b>\n"; text += "".join(live[:1]) if live else "😴 No Live Now\n━━━━━━━━━━━━━━━━━━━━━━\n"
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=text[:4000], parse_mode="HTML", reply_markup=get_back_keyboard("live"))
async def send_results_to_chat(chat_id, context):
    msg = await context.bot.send_message(chat_id=chat_id, text="✨ Loading Results...")
    text = "✨ <b>✅ PREVIOUS RESULTS - PREMIUM</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key in SPORT_CONFIG.keys():
        title, live, up, res = get_data(key); text += f"<b>{title}</b>\n"; text += "".join(res[:1]) if res else "No Results\n━━━━━━━━━━━━━━━━━━━━━━\n"
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=text[:4000], parse_mode="HTML", reply_markup=get_back_keyboard("results"))
async def send_table_to_chat(chat_id, context):
    txt = "🏆 <b>PREMIER LEAGUE - POINTS TABLE</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    data = fetch_standings("soccer","eng.1")
    try:
        entries = data['children'][0]['standings']['entries'][:10]
        for i, e in enumerate(entries, 1):
            team = e['team']['displayName']; stats = {s['name']: s['value'] for s in e['stats']}
            txt += f"{i}. <b>{team}</b> - {stats.get('points',0)} Pts | P:{stats.get('gamesPlayed',0)} W:{stats.get('wins',0)} D:{stats.get('ties',0)} L:{stats.get('losses',0)}\n"
    except: txt += "Table Updating... Try Again Later\n"
    txt += "\n━━━━━━━━━━━━━━━━━━━━━━\n💬 @bigolive_asia"
    await context.bot.send_message(chat_id=chat_id, text=txt[:4000], parse_mode="HTML", reply_markup=get_back_keyboard("table"))
async def send_tomorrow_to_chat(chat_id, context):
    txt = "📅 <b>TOMORROW MATCHES</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key in ["football","cricket","basketball","tennis"]:
        title, live, up, res = get_data(key); txt += f"<b>{title}</b>\n"; txt += "".join(up[:2]) if up else "No Matches Tomorrow\n━━━━━━━━━━━━━━━━━━━━━━\n"
    await context.bot.send_message(chat_id=chat_id, text=txt[:4000], parse_mode="HTML", reply_markup=get_back_keyboard("tomorrow"))
async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🔍 Usage: /search Real Madrid\nExample: /search India\nExample: /search Arsenal", parse_mode="HTML"); return
    q = " ".join(context.args).lower(); await update.message.reply_text(f"🔍 Searching for <b>{q}</b>...", parse_mode="HTML")
    found=False
    for key in SPORT_CONFIG.keys():
        title, live, up, res = get_data(key)
        for item in live + up + res:
            if q in item.lower(): await update.message.reply_text(item[:4000], parse_mode="HTML"); found=True; break
        if found: break
    if not found: await update.message.reply_text("😴 No Match Found. Try Another Team Name.", parse_mode="HTML")
async def live_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_live_to_chat(update.effective_chat.id, context)
async def results_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_results_to_chat(update.effective_chat.id, context)
async def table_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_table_to_chat(update.effective_chat.id, context)
async def tomorrow_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_tomorrow_to_chat(update.effective_chat.id, context)
async def news_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_news_to_chat(update.effective_chat.id, context)
async def make_handler(key):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_sport_to_chat(update.effective_chat.id, context, key)
    return handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer("Loading... ⏳"); data = q.data; chat_id = update.effective_chat.id
    if data == "menu_start": await context.bot.send_message(chat_id=chat_id, text=get_welcome(chat_id), parse_mode="HTML", reply_markup=get_main_keyboard())
    elif data == "menu_news": await send_news_to_chat(chat_id, context)
    elif data == "menu_lang": await context.bot.send_message(chat_id=chat_id, text="🌐 <b>CHOOSE YOUR LANGUAGE / YOUR LANGUAGES</b>\n\n🌍 Select Your Language Below 👇", parse_mode="HTML", reply_markup=get_lang_keyboard())
    elif data.startswith("lang_"):
        lang = data.replace("lang_", ""); USER_LANG[str(chat_id)] = lang; name = LANGS.get(lang, LANGS["en"])["name"]; welcome = LANGS.get(lang, LANGS["en"])["welcome"]
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Language Saved: <b>{name}</b>\n\n{welcome}", parse_mode="HTML", reply_markup=get_main_keyboard())
    elif data == "menu_live": await send_live_to_chat(chat_id, context)
    elif data == "menu_results": await send_results_to_chat(chat_id, context)
    elif data == "menu_table": await send_table_to_chat(chat_id, context)
    elif data == "menu_tomorrow": await send_tomorrow_to_chat(chat_id, context)
    elif data == "menu_search": await context.bot.send_message(chat_id=chat_id, text="🔍 <b>SEARCH</b>\n\nType: /search Real Madrid\nType: /search India\nType: /search Arsenal", parse_mode="HTML")
    elif data.startswith("menu_"):
        key = data.replace("menu_", "")
        if key in SPORT_CONFIG: await send_sport_to_chat(chat_id, context, key)

last_sent = {}
async def auto_job(context: ContextTypes.DEFAULT_TYPE):
    global last_sent
    try:
        if not CHANNEL_IDS: return
        # 1. LIVE SCORES - හැම Sport එකම, break නෑ
        for key in SPORT_CONFIG.keys():
            title, live, _, _ = get_data(key)
            if not live: continue
            new_text = live[0][:500]
            if last_sent.get(f"live_{key}") == new_text: continue
            last_sent[f"live_{key}"] = new_text
            text = f"✨ <b>🔴 LIVE UPDATE - {title}</b> ✨\n\n{live[0]}"[:4000]
            for CH in CHANNEL_IDS:
                try: await context.bot.send_message(chat_id=CH, text=text, parse_mode="HTML")
                except: pass
            await asyncio.sleep(1)
        # 2. NEWS + SCORE - පැය 1කට වතාවක් වගේ
        if last_sent.get("news_time", 0) < asyncio.get_event_loop().time() - 1800:
            last_sent["news_time"] = asyncio.get_event_loop().time()
            news_txt = format_news()
            for CH in CHANNEL_IDS:
                try: await context.bot.send_message(chat_id=CH, text=news_txt, parse_mode="HTML")
                except: pass
    except Exception as e: print("Auto Error:", e)

async def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("live", live_cmd)); app.add_handler(CommandHandler("results", results_cmd))
    app.add_handler(CommandHandler("table", table_cmd)); app.add_handler(CommandHandler("tomorrow", tomorrow_cmd))
    app.add_handler(CommandHandler("news", news_cmd)); app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(CommandHandler("lineup", search_cmd))
    for key in SPORT_CONFIG.keys():
        h = await make_handler(key); app.add_handler(CommandHandler(key, h))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.job_queue.run_repeating(auto_job, interval=180, first=10)
    print("Premium Bot Started!")
    await app.initialize(); await app.start(); await app.updater.start_polling(); await asyncio.Event().wait()
if __name__ == "__main__":
    asyncio.run(main())
