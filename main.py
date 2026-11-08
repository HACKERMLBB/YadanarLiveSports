import os
import asyncio
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Premium Sports Bot Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# ============ PREMIUM DESIGN HELPERS ============

def bar(v1, v2, label):
    try:
        a = float(str(v1).replace('%',''))
        b = float(str(v2).replace('%',''))
        tot = a + b
        if tot == 0:
            return f"{label}\n{a} - {b}\n"
        p = int((a/tot)*12)
        q = 12 - p
        # Beautiful bar
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
        # Competition logo name mapping
        league_emoji = {"ENG.1":"🏴󐁧󐁢󐁥󐁮󐁧󐁿","ESP.1":"🇪🇸","GER.1":"🇩🇪","ITA.1":"🇮🇹","FRA.1":"🇫🇷","UEFA.CHAMPIONS":"⭐"}.get(league.upper(),"🏆")

        h = competitors[0]
        a = competitors[1] if len(competitors)>1 else None
        h_name = h['team'].get('displayName','')
        a_name = a['team'].get('displayName','') if a else ""
        h_short = h['team'].get('abbreviation','')
        a_short = a['team'].get('abbreviation','') if a else ""
        h_score = h.get('score','0')
        a_score = a.get('score','0') if a else "0"
        h_color = h['team'].get('color','1a1a1a')
        # Winner highlight
        winner = ""
        if state == 'post':
            if h_score > a_score:
                winner = f"👑 {h_name} Won!"
            elif a_score > h_score:
                winner = f"👑 {a_name} Won!"
            else:
                winner = "🤝 Draw Match"

        # ===== HEADER =====
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
        if state == 'in':
            t += f"⏱️ Match Progress: {progress_bar(short)}\n"
        t += "\n"

        # ===== SCOREBOARD =====
        t += "┏━━━━━━━━━━━━━━━━━━━━┓\n"
        if state == 'pre':
            t += f"┃  <b>{h_name}</b>\n"
            t += f"┃         <b>VS</b>\n"
            t += f"┃  <b>{a_name}</b>\n"
        else:
            # Show score big
            t += f"┃  <b>{h_name}</b>  [{h_short}]\n"
            t += f"┃      <b> {h_score}  -  {a_score} </b>\n"
            t += f"┃  <b>{a_name}</b>  [{a_short}]\n"
        t += "┗━━━━━━━━━━━━━━━━━━━━┛\n"
        if winner:
            t += f"\n{winner}\n"

        if state == 'pre':
            t += "\n<i>⏳ Match not started yet. Stay tuned!</i>\n"
            t += "━━━━━━━━━━━━━━━━━━━━━━\n"
            return t

        # ===== DETAILS =====
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

            try:
                teams = dj.get('boxscore', {}).get('teams', [])
                if len(teams) >= 2:
                    for tm in teams:
                        for st in tm.get('statistics', []):
                            n = st.get('name')
                            if n in ['possessionPct','totalShots','shotsOnTarget','wonCorners','fouls','offsides','saves']:
                                if n not in stats:
                                    stats[n] = []
                                stats[n].append(st.get('displayValue'))
            except:
                pass

        # Timeline
        if timeline:
            t += f"\n📜 <b>MATCH TIMELINE</b>\n"
            t += "──────────────────────\n"
            for line in timeline:
                t += f"{line}\n"

        # Goals separate beautiful
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

        # Stats Premium
        if stats:
            t += f"\n📊 <b>MATCH STATISTICS</b>\n"
            t += "──────────────────────\n"
            labels = {
                'possessionPct': f"⚽ Possession  {h_short} vs {a_short}",
                'totalShots': f"🥅 Total Shots  {h_short} vs {a_short}",
                'shotsOnTarget': f"🎯 Shots on Target",
                'wonCorners': f"🚩 Corners",
                'fouls': f"🚨 Fouls",
            }
            for k, lab in labels.items():
                if k in stats and len(stats[k])>=2:
                    v1, v2 = stats[k][0], stats[k][1]
                    if k == 'possessionPct':
                        t += bar(v1, v2, lab) + "\n"
                    else:
                        # Visual bar for shots etc
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

# ============ SPORTS ============

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
                txt = f"🏏 <b>{ev.get('name','')}</b>\n📍 {ev.get('status',{}).get('type',{}).get('detail','')}\n━━━━━━━━━━━━━━━━━━━━━━\n"
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ <b>🏆 BIGO LIVE ASIA - PREMIUM SPORTS 🏆</b> ✨\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👋 Welcome to the Most Beautiful Live Sports Bot!\n\n"
        "📱 <b>COMMANDS:</b>\n"
        "🔴 /live - All Live Matches\n"
        "✅ /results - Previous Results\n"
        "⚽ /football - Football\n"
        "🏏 /cricket - Cricket\n"
        "🏀 /basketball - Basketball\n"
        "🎾 /tennis - Tennis\n"
        "🏑 /hockey - Hockey\n"
        "🏐 /volleyball - Volleyball\n"
        "🏓 /tabletennis - Table Tennis\n"
        "⚾ /baseball - Baseball\n"
        "🏈 /nfl - NFL\n"
        "🏸 /badminton - Badminton\n"
        "🏆 /fifa - FIFA\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📢 Channel: @bigolive_asia",
        parse_mode="HTML"
    )

async def live_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("✨ Loading Premium Live...")
    text = "✨ <b>🔴 TOP 10 LIVE - PREMIUM</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key in SPORT_CONFIG.keys():
        title, live, up, res = get_data(key)
        text += f"<b>{title}</b>\n"
        if live:
            text += "".join(live[:1])
        else:
            text += "😴 No Live Now\n━━━━━━━━━━━━━━━━━━━━━━\n"
    await msg.edit_text(text[:4000], parse_mode="HTML")

async def results_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("✨ Loading Results...")
    text = "✨ <b>✅ PREVIOUS RESULTS - PREMIUM</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key in SPORT_CONFIG.keys():
        title, live, up, res = get_data(key)
        text += f"<b>{title}</b>\n"
        text += "".join(res[:1]) if res else "No Results\n━━━━━━━━━━━━━━━━━━━━━━\n"
    await msg.edit_text(text[:4000], parse_mode="HTML")

async def make_handler(key):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await update.message.reply_text("✨ Loading Premium Details...")
        txt = format_full(key)
        await msg.edit_text(txt[:4000], parse_mode="HTML")
    return handler

last = set()
async def auto_job(context: ContextTypes.DEFAULT_TYPE):
    global last
    try:
        all_live=[]
        for key in SPORT_CONFIG.keys():
            title, live, _, _ = get_data(key)
            for s in live:
                all_live.append(f"{title}\n{s}")
        cur=set(all_live)
        new=cur-last
        if last and new and CHANNEL:
            for s in list(new)[:2]:
                await context.bot.send_message(chat_id=CHANNEL, text=f"✨ <b>🔴 LIVE UPDATE</b> ✨\n\n{s}"[:4000], parse_mode="HTML")
        if cur:
            last=cur
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
    app.job_queue.run_repeating(auto_job, interval=120, first=10)
    print("Premium Bot Started!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
