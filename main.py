import os
import asyncio
import threading
import requests
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")

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

def bar(v1, v2, label):
    try:
        a = float(str(v1).replace('%',''))
        b = float(str(v2).replace('%',''))
        tot = a + b
        if tot == 0:
            return f"{label}\n{a} - {b}\n"
        p = int((a/tot)*12)
        q = 12 - p
        return f"{label}\n{'🟦'*p}{'⬜'*q} {a:.0f}% - {b:.0f}%\n"
    except:
        return f"{label}: {v1} - {v2}\n"

def progress_bar(minute):
    try:
        m = int(str(minute).replace("'","").split("+")[0])
        p = min(int(m/90*10), 10)
        return f"{'🟩'*p}{'⬜'*(10-p)} {m}'"
    except:
        return ""

def fetch_board(sport, league):
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
        return requests.get(url, timeout=12).json().get('events', [])
    except:
        return []

def fetch_summary(sport, league, eid):
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event={eid}"
        return requests.get(url, timeout=12).json()
    except:
        return None

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Football", callback_data="menu_football"), InlineKeyboardButton("Cricket", callback_data="menu_cricket")],
        [InlineKeyboardButton("Basketball", callback_data="menu_basketball"), InlineKeyboardButton("Tennis", callback_data="menu_tennis")],
        [InlineKeyboardButton("Hockey", callback_data="menu_hockey"), InlineKeyboardButton("Volleyball", callback_data="menu_volleyball")],
        [InlineKeyboardButton("Table Tennis", callback_data="menu_tabletennis"), InlineKeyboardButton("Baseball", callback_data="menu_baseball")],
        [InlineKeyboardButton("NFL", callback_data="menu_nfl"), InlineKeyboardButton("Badminton", callback_data="menu_badminton")],
        [InlineKeyboardButton("FIFA", callback_data="menu_fifa"), InlineKeyboardButton("LIVE ALL", callback_data="menu_live")],
        [InlineKeyboardButton("RESULTS", callback_data="menu_results")],
        [InlineKeyboardButton("Join Channel", url="https://t.me/bigolive_asia")]
    ])

def get_back_keyboard(key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Refresh", callback_data=f"menu_{key}")],
        [InlineKeyboardButton("Back to Menu", callback_data="menu_start")],
        [InlineKeyboardButton("Join Channel", url="https://t.me/bigolive_asia")]
    ])

# ============ UNIVERSAL FORMATTER FOR ALL 10 SPORTS ============
def format_premium(ev, sport, league):
    try:
        comp = ev['competitions'][0]
        competitors = comp['competitors']
        state = ev.get('status', {}).get('type', {}).get('state')
        short = ev.get('status', {}).get('type', {}).get('shortDetail','')
        detail = ev.get('status', {}).get('type', {}).get('detail','')
        eid = ev.get('id')
        venue = comp.get('venue', {}).get('fullName','Unknown Stadium') if comp.get('venue') else 'Unknown Stadium'
        city = comp.get('venue', {}).get('address', {}).get('city','') if comp.get('venue') else ''
        comp_name = ev.get('season', {}).get('slug','').replace('-',' ').upper() if ev.get('season') else league.upper()
        league_emoji = {"ENG.1":"🏴󐁧󐁢󐁥󐁮󐁧󐁿","ESP.1":"🇪🇸","GER.1":"🇩🇪","ITA.1":"🇮🇹","FRA.1":"🇫🇷","UEFA.CHAMPIONS":"⭐","NBA":"🏀","ATP":"🎾","WTA":"🎾","MLB":"⚾","NFL":"🏈","BWF":"🏸"}.get(league.upper(),"🏆")

        h = competitors[0]
        a = competitors[1] if len(competitors)>1 else None
        h_name = h['team'].get('displayName','')
        a_name = a['team'].get('displayName','') if a else ""
        h_short = h['team'].get('abbreviation','')
        a_short = a['team'].get('abbreviation','') if a else ""
        h_score = h.get('score','0')
        a_score = a.get('score','0') if a else "0"

        # Cricket special score lines - ex: 180/4 (20 Overs)
        h_lines = h.get('linescores', [])
        a_lines = a.get('linescores', []) if a else []
        h_line_txt = " | ".join([str(x.get('value','')) for x in h_lines]) if h_lines else ""
        a_line_txt = " | ".join([str(x.get('value','')) for x in a_lines]) if a_lines else ""

        winner = ""
        if state == 'post':
            try:
                if float(h_score) > float(a_score):
                    winner = f"👑 {h_name} Won!"
                elif float(a_score) > float(h_score):
                    winner = f"👑 {a_name} Won!"
                else:
                    winner = "🤝 Draw Match"
            except:
                winner = f"✅ Full Time"

        t = ""
        t += "╔══════════════════════╗\n"
        if state == 'in':
            t += f"║  🔴 <b>LIVE NOW</b>  •  {short}  ║\n"
        elif state == 'post':
            t += f"║  ✅ <b>FULL TIME</b>  •  {detail}  ║\n"
        else:
            t += f"║  🕒 <b>UPCOMING</b>  •  {short}  ║\n"
        t += "╚══════════════════════╝\n\n"
        t += f"{league_emoji} <b>{comp_name}</b>\n"
        t += f"🏟️ {venue} {city}\n"
        if state == 'in' and sport == "soccer":
            t += f"⏱️ Match Progress: {progress_bar(short)}\n"
        t += "\n"
        t += "┏━━━━━━━━━━━━━━━━━━━━┓\n"
        if state == 'pre':
            t += f"┃  <b>{h_name}</b>\n"
            t += f"┃         <b>VS</b>\n"
            t += f"┃  <b>{a_name}</b>\n"
        else:
            t += f"┃  <b>{h_name}</b>  [{h_short}]\n"
            t += f"┃      <b> {h_score}  -  {a_score} </b>\n"
            t += f"┃  <b>{a_name}</b>  [{a_short}]\n"
            if h_line_txt:
                t += f"┃  {h_short}: {h_line_txt}\n"
            if a_line_txt:
                t += f"┃  {a_short}: {a_line_txt}\n"
        t += "┗━━━━━━━━━━━━━━━━━━━━┛\n"
        if winner:
            t += f"\n{winner}\n"
        if state == 'pre':
            t += "\n<i>⏳ Match not started yet. Stay tuned!</i>\n"
            t += "━━━━━━━━━━━━━━━━━━━━━━\n"
            return t

        # Cricket Extra Details
        if sport == "cricket":
            t += f"\n🏏 <b>CRICKET DETAILS</b>\n"
            t += "──────────────────────\n"
            t += f"📍 {detail}\n"
            t += f"📊 {h_name}: {h_score}\n"
            t += f"📊 {a_name}: {a_score}\n"
            t += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
            t += "💬 <i>Follow for more live updates</i>  •  @bigolive_asia\n"
            return t

        # Football / Others Details
        dj = fetch_summary(sport, league, eid)
        goals, cards, subs, timeline = [], [], [], []
        stats = {}
        if dj:
            for d in dj.get('details', []):
                txt = d.get('type', {}).get('text','')
                team = d.get('team', {}).get('shortDisplayName','')
                ath = d['athletesInvolved'][0].get('displayName','') if d.get('athletesInvolved') else ''
                clock = d.get('clock', {}).get('displayValue','')
                tl = txt.lower()
                if 'goal' in tl or 'penalty - scored' in tl:
                    is_pen = 'penalty' in tl
                    goals.append((clock, ath, team, is_pen))
                    timeline.append(f"  {clock}'  ⚽ {ath} ({team}){' [PEN]' if is_pen else ''}")
                elif 'yellow' in tl:
                    cards.append(f"  {clock}'  🟨 {ath} ({team})")
                    timeline.append(f"  {clock}'  🟨 {ath}")
                elif 'red' in tl:
                    cards.append(f"  {clock}'  🟥 {ath} ({team})")
                    timeline.append(f"  {clock}'  🟥 {ath}")
                elif 'substitution' in tl:
                    subs.append(f"  {clock}'  🔄 {ath} ({team})")
                elif 'touchdown' in tl or 'field goal' in tl or 'home run' in tl or 'three point' in tl:
                    timeline.append(f"  {clock}'  🔥 {ath} - {txt} ({team})")
            try:
                teams = dj.get('boxscore', {}).get('teams', [])
                if len(teams) >= 2:
                    for tm in teams:
                        for st in tm.get('statistics', []):
                            n = st.get('name')
                            if n in ['possessionPct','totalShots','shotsOnTarget','wonCorners','fouls','offsides','saves','fieldGoalsMade','threePointFieldGoalsMade','rebounds','assists']:
                                if n not in stats:
                                    stats[n] = []
                                stats[n].append(st.get('displayValue'))
            except:
                pass

        if timeline:
            t += f"\n📜 <b>MATCH TIMELINE</b>\n"
            t += "──────────────────────\n"
            for line in timeline:
                t += f"{line}\n"
        if goals:
            t += f"\n⚽ <b>GOAL SCORERS</b>\n"
            t += "──────────────────────\n"
            for clock, ath, team, is_pen in goals:
                pen = " 🎯 PENALTY" if is_pen else ""
                t += f"  ⏰ {clock}'  <b>{ath}</b>\n"
                t += f"       └ {team}{pen}\n"
        if cards:
            t += f"\n🟨 <b>CARDS</b>\n"
            t += "──────────────────────\n"
            for c in cards:
                t += f"{c}\n"
        if subs:
            t += f"\n🔄 <b>SUBSTITUTIONS</b>\n"
            t += "──────────────────────\n"
            for s in subs[:5]:
                t += f"{s}\n"
        if stats:
            t += f"\n📊 <b>MATCH STATISTICS</b>\n"
            t += "──────────────────────\n"
            labels = {
                'possessionPct': f"⚽ Possession  {h_short} vs {a_short}",
                'totalShots': f"🥅 Total Shots  {h_short} vs {a_short}",
                'shotsOnTarget': f"🎯 Shots on Target",
                'wonCorners': f"🚩 Corners",
                'fouls': f"🚨 Fouls",
                'rebounds': f"🏀 Rebounds",
                'assists': f"🎯 Assists",
            }
            for k, lab in labels.items():
                if k in stats and len(stats[k])>=2:
                    v1, v2 = stats[k][0], stats[k][1]
                    if k == 'possessionPct':
                        t += bar(v1, v2, lab) + "\n"
                    else:
                        try:
                            a1 = float(v1); b1 = float(v2)
                            tot = a1+b1
                            if tot>0:
                                p = int((a1/tot)*10)
                                t += f"{lab}\n{'🟦'*p}{'🟧'*(10-p)}  {v1} - {v2}\n\n"
                            else:
                                t += f"{lab}: {v1} - {v2}\n"
                        except:
                            t += f"{lab}: {v1} - {v2}\n"
        else:
            if state == 'in':
                t += f"\n📊 <i>Stats are updating live...</i>\n"
        t += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        t += "💬 <i>Follow for more live updates</i>  •  @bigolive_asia\n"
        return t
    except Exception as e:
        return f"Error: {e}\n━━━━━━━━━━━━━━\n"

SPORT_CONFIG = {
    "football": ("⚽ FOOTBALL", [("soccer","eng.1"),("soccer","esp.1"),("soccer","ger.1"),("soccer","ita.1"),("soccer","fra.1"),("soccer","uefa.champions")]),
    "cricket": ("🏏 CRICKET", [("cricket","")]),
    "basketball": ("🏀 BASKETBALL", [("basketball","nba")]),
    "tennis": ("🎾 TENNIS", [("tennis","atp"),("tennis","wta")]),
    "hockey": ("🏑 FIELD HOCKEY", [("field-hockey","fih")]),
    "volleyball": ("🏐 VOLLEYBALL", [("volleyball","fivb")]),
    "tabletennis": ("🏓 TABLE TENNIS", [("table-tennis","ittf")]),
    "baseball": ("⚾ BASEBALL", [("baseball","mlb")]),
    "nfl": ("🏈 AMERICAN FOOTBALL", [("football","nfl")]),
    "badminton": ("🏸 BADMINTON", [("badminton","bwf")]),
    "fifa": ("🏆 FIFA", [("soccer","fifa.world"),("soccer","fifa.friendly")]),
}

def get_data(key):
    title, leagues = SPORT_CONFIG[key]
    live, up, res = [], [], []
    for sport, league in leagues:
        if sport == "cricket":
            try:
                r = requests.get("https://site.api.espn.com/apis/site/v2/sports/cricket/scoreboard", headers={"User-Agent":"Mozilla/5.0"}, timeout=12).json()
                events = r.get('events', [])
            except:
                events = []
            for ev in events:
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
    return title, live, up, res

def format_full(key):
    title, live, up, res = get_data(key)
    t = f"✨ <b>{title}  •  PREMIUM LIVE</b> ✨\n"
    t += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    t += "🔴 <b>LIVE NOW</b>\n\n"
    t += "".join(live[:2]) if live else "😴 No Live Match Right Now\n━━━━━━━━━━━━━━━━━━━━━━\n"
    t += "\n✅ <b>PREVIOUS RESULTS</b>\n\n"
    t += "".join(res[:3]) if res else "No Results Yet\n━━━━━━━━━━━━━━━━━━━━━━\n"
    t += "\n🕒 <b>UPCOMING</b>\n\n"
    t += "".join(up[:3]) if up else "No Upcoming\n━━━━━━━━━━━━━━━━━━━━━━\n"
    return t

WELCOME_TEXT = (
    "✨ 🏆 YADANAR LIVE SPORTS - PREMIUM SPORTS 🏆 ✨\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "👋 Welcome to the Most Beautiful Live Sports Bot!\n\n"
    "POWERD BY @t.me/bigolive_asia:"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode="HTML", reply_markup=get_main_keyboard())

async def send_sport_to_chat(chat_id, context, key):
    txt = format_full(key)
    await context.bot.send_message(chat_id=chat_id, text=txt[:4000], parse_mode="HTML", reply_markup=get_back_keyboard(key))

async def send_live_to_chat(chat_id, context):
    msg = await context.bot.send_message(chat_id=chat_id, text="✨ Loading Premium Live...")
    text = "✨ <b>🔴 TOP 10 LIVE - PREMIUM</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key in SPORT_CONFIG.keys():
        title, live, up, res = get_data(key)
        text += f"<b>{title}</b>\n"
        if live:
            text += "".join(live[:1])
        else:
            text += "😴 No Live Now\n━━━━━━━━━━━━━━━━━━━━━━\n"
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=text[:4000], parse_mode="HTML", reply_markup=get_back_keyboard("live"))

async def send_results_to_chat(chat_id, context):
    msg = await context.bot.send_message(chat_id=chat_id, text="✨ Loading Results...")
    text = "✨ <b>✅ PREVIOUS RESULTS - PREMIUM</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key in SPORT_CONFIG.keys():
        title, live, up, res = get_data(key)
        text += f"<b>{title}</b>\n"
        text += "".join(res[:1]) if res else "No Results\n━━━━━━━━━━━━━━━━━━━━━━\n"
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=text[:4000], parse_mode="HTML", reply_markup=get_back_keyboard("results"))

async def live_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_live_to_chat(update.effective_chat.id, context)
async def results_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_results_to_chat(update.effective_chat.id, context)
async def make_handler(key):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await send_sport_to_chat(update.effective_chat.id, context, key)
    return handler

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("Loading... ⏳")
    data = q.data
    print(f"Button Clicked: {data}")
    chat_id = update.effective_chat.id
    if data == "menu_start":
        await context.bot.send_message(chat_id=chat_id, text=WELCOME_TEXT, parse_mode="HTML", reply_markup=get_main_keyboard())
    elif data == "menu_live":
        await send_live_to_chat(chat_id, context)
    elif data == "menu_results":
        await send_results_to_chat(chat_id, context)
    elif data.startswith("menu_"):
        key = data.replace("menu_", "")
        if key in SPORT_CONFIG:
            await send_sport_to_chat(chat_id, context, key)

async def auto_job(context: ContextTypes.DEFAULT_TYPE):
    try:
        if not CHANNEL:
            return
        for key in SPORT_CONFIG.keys():
            title, live, _, _ = get_data(key)
            if live:
                text = f"✨ <b>🔴 LIVE UPDATE - {title}</b> ✨\n\n{live[0]}"[:4000]
                await context.bot.send_message(chat_id=CHANNEL, text=text, parse_mode="HTML")
                break
    except Exception as e:
        print("Auto Error:", e)

async def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("live", live_cmd))
    app.add_handler(CommandHandler("results", results_cmd))
    for key in SPORT_CONFIG.keys():
        h = await make_handler(key)
        app.add_handler(CommandHandler(key, h))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.job_queue.run_repeating(auto_job, interval=180, first=10)
    print("Premium Bot Started!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
