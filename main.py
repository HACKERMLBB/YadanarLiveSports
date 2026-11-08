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
    return "Full Detailed Top 10 Sports Bot Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# ============ ESPN HELPERS ============

def fetch_scoreboard(sport, league):
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
        r = requests.get(url, timeout=12).json()
        return r.get('events', [])
    except Exception as e:
        print(f"Scoreboard Error {sport} {league}:", e)
        return []

def fetch_event_details(sport, league, event_id):
    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event={event_id}"
        r = requests.get(url, timeout=12).json()
        return r
    except:
        return None

def parse_details(details_json):
    goals = []
    cards = []
    stats_text = ""
    commentary = []
    if not details_json:
        return goals, cards, stats_text, commentary
    # Details - Goals, Cards
    details = details_json.get('details', [])
    for d in details:
        t = d.get('type', {}).get('text', '')
        team = d.get('team', {}).get('shortDisplayName', '')
        athlete = d.get('athletesInvolved', [{}])[0].get('displayName', '') if d.get('athletesInvolved') else ''
        clock = d.get('clock', {}).get('displayValue', '')
        if 'Goal' in t or 'goal' in t.lower():
            goals.append(f"{athlete} {clock}' ({team})")
        if 'Yellow' in t or 'Red' in t:
            emoji = "🟨" if 'Yellow' in t else "🟥"
            cards.append(f"{emoji} {athlete} {clock}' ({team})")
        if 'Penalty' in t:
            goals.append(f"{athlete} {clock}' PEN ({team})")
    # Stats
    try:
        box = details_json.get('boxscore', {})
        teams = box.get('teams', [])
        if len(teams) >= 2:
            # Try to find possession, shots
            for st in teams[0].get('statistics', []):
                if st.get('name') in ['possessionPct', 'totalShots', 'shotsOnTarget', 'wonCorners']:
                    pass
            stats = {}
            for tm in teams:
                for st in tm.get('statistics', []):
                    if st.get('name') == 'possessionPct':
                        stats['poss'] = stats.get('poss', []) + [st.get('displayValue')]
                    if st.get('name') == 'totalShots':
                        stats['shots'] = stats.get('shots', []) + [st.get('displayValue')]
            if stats.get('poss'):
                stats_text = f"Possession: {' - '.join(stats['poss'])} | Shots: {' - '.join(stats.get('shots', ['-','-']))}"
    except:
        pass
    # Commentary - last 3
    try:
        keyplays = details_json.get('keyPlays', []) or details_json.get('gameInfo', {}).get('venue', {})
        # ESPN commentary is in 'commentary' via different endpoint, keep simple
    except:
        pass
    return goals, cards, stats_text, commentary

def format_event(ev, sport, league, show_detail=True):
    try:
        comp = ev['competitions'][0]
        competitors = comp['competitors']
        state = ev.get('status', {}).get('type', {}).get('state')
        short_detail = ev.get('status', {}).get('type', {}).get('shortDetail', '')
        detail = ev.get('status', {}).get('type', {}).get('detail', '')
        event_id = ev.get('id')
        league_name = ev.get('season', {}).get('slug', '') or league

        if len(competitors) >= 2:
            h = competitors[0]
            a = competitors[1]
            h_name = h['team'].get('shortDisplayName', h['team'].get('displayName',''))
            a_name = a['team'].get('shortDisplayName', a['team'].get('displayName',''))
            h_score = h.get('score', '')
            a_score = a.get('score', '')
            # For cricket, score is different
            if sport == 'cricket':
                h_score = h.get('score', '') or h.get('linescores', [{}])[0].get('displayValue','') if h.get('linescores') else ''
                a_score = a.get('score', '') or a.get('linescores', [{}])[0].get('displayValue','') if a.get('linescores') else ''
        else:
            h_name = ev.get('name','')
            a_name = ""
            h_score = ""
            a_score = ""

        if state == 'in':
            header = f"LIVE - {short_detail}\n{h_name} {h_score} - {a_score} {a_name}"
        elif state == 'post':
            header = f"FT - {detail}\n{h_name} {h_score} - {a_score} {a_name}"
        else:
            header = f"UPCOMING - {short_detail}\n{h_name} vs {a_name}"

        if not show_detail or state == 'pre':
            return header

        # Fetch detailed info for live and finished
        details_json = fetch_event_details(sport, league, event_id)
        goals, cards, stats_text, _ = parse_details(details_json)
        extra = ""
        if goals:
            extra += "\nGoals:\n" + "\n".join([f"  {g}" for g in goals[:8]])
        if cards:
            extra += "\nCards:\n" + "\n".join([f"  {c}" for c in cards[:6]])
        if stats_text:
            extra += f"\nStats: {stats_text}"
        # Cricket innings detail
        if sport == 'cricket' and details_json:
            try:
                # Try to get linescores
                pass
            except:
                pass
        return header + extra
    except Exception as e:
        return f"Error parsing: {e}"

# ============ SPORT DEFINITIONS TOP 10 ============

SPORT_CONFIG = {
    "football": ("FOOTBALL", [("soccer","eng.1"),("soccer","esp.1"),("soccer","ger.1"),("soccer","ita.1"),("soccer","fra.1"),("soccer","uefa.champions")]),
    "cricket": ("CRICKET", [("cricket","")]),
    "basketball": ("BASKETBALL NBA", [("basketball","nba")]),
    "tennis": ("TENNIS", [("tennis","atp"),("tennis","wta")]),
    "hockey": ("FIELD HOCKEY", [("field-hockey","fih")]),
    "volleyball": ("VOLLEYBALL", [("volleyball","fivb")]),
    "tabletennis": ("TABLE TENNIS", [("table-tennis","ittf")]),
    "baseball": ("BASEBALL MLB", [("baseball","mlb")]),
    "nfl": ("AMERICAN FOOTBALL NFL", [("football","nfl")]),
    "badminton": ("BADMINTON", [("badminton","bwf")]),
    "fifa": ("FIFA", [("soccer","fifa.world"),("soccer","fifa.friendly"),("soccer","fifa.world.qual")]),
}

def get_sport_data(key):
    title, leagues = SPORT_CONFIG[key]
    live = []
    upcoming = []
    results = []
    for sport, league in leagues:
        if sport == "cricket" and league == "":
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                r = requests.get("https://site.api.espn.com/apis/site/v2/sports/cricket/scoreboard", headers=headers, timeout=12).json()
                events = r.get('events', [])
            except:
                events = []
            for ev in events:
                state = ev.get('status', {}).get('type', {}).get('state')
                name = ev.get('name','')
                det = ev.get('status', {}).get('type', {}).get('detail','')
                txt = f"{name} | {det}"
                if state == 'in':
                    live.append(txt)
                elif state == 'pre':
                    upcoming.append(txt)
                elif state == 'post':
                    results.append(txt)
            continue

        events = fetch_scoreboard(sport, league)
        for ev in events:
            state = ev.get('status', {}).get('type', {}).get('state')
            formatted = format_event(ev, sport, league, show_detail=(state in ['in','post']))
            if state == 'in':
                live.append(formatted)
            elif state == 'pre':
                upcoming.append(formatted)
            elif state == 'post':
                results.append(formatted)
    return title, live, upcoming, results

def format_full_sport(key):
    title, live, upcoming, results = get_sport_data(key)
    text = f"{title}\n\n"
    text += "=== LIVE ===\n"
    text += "\n\n".join(live[:3]) if live else "No Live Match"
    text += "\n\n=== PREVIOUS RESULTS ===\n"
    text += "\n\n".join(results[:5]) if results else "No Recent Results"
    text += "\n\n=== UPCOMING ===\n"
    text += "\n\n".join(upcoming[:5]) if upcoming else "No Upcoming Matches"
    return text

# ============ BOT HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "TOP 10 LIVE SPORTS HUB - FULL DETAILS\n\n"
        "Commands:\n"
        "/live - All Live + Results\n"
        "/results - All Previous Results\n"
        "/football - Football Full Details\n"
        "/cricket - Cricket Full Details\n"
        "/basketball - Basketball\n"
        "/tennis - Tennis\n"
        "/hockey - Field Hockey\n"
        "/volleyball - Volleyball\n"
        "/tabletennis - Table Tennis\n"
        "/baseball - Baseball\n"
        "/nfl - American Football\n"
        "/badminton - Badminton\n"
        "/fifa - FIFA Matches\n\n"
        "Live = Score + Goals + Cards + Stats\n"
        "Previous = Last Results + Scorers"
    )

async def live_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Getting Full Live Details...")
    text = "TOP 10 LIVE + RESULTS\n\n"
    for key in SPORT_CONFIG.keys():
        title, live, upcoming, results = get_sport_data(key)
        text += f"--- {title} ---\n"
        if live:
            text += "\n".join(live[:2]) + "\n\n"
        else:
            text += "No Live Now\n"
            if results:
                text += f"Last: {results[0][:200]}\n\n"
            else:
                text += "No Results\n\n"
    await msg.edit_text(text[:4000])

async def results_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Getting Previous Results...")
    text = "PREVIOUS RESULTS - TOP 10\n\n"
    for key in SPORT_CONFIG.keys():
        title, live, upcoming, results = get_sport_data(key)
        text += f"--- {title} ---\n"
        if results:
            text += "\n\n".join(results[:2]) + "\n\n"
        else:
            text += "No Results\n\n"
    await msg.edit_text(text[:4000])

async def make_handler(key):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await update.message.reply_text("Getting Full Details...")
        txt = format_full_sport(key)
        await msg.edit_text(txt[:4000])
    return handler

last_scores = set()
async def auto_job(context: ContextTypes.DEFAULT_TYPE):
    global last_scores
    try:
        all_live = []
        for key in SPORT_CONFIG.keys():
            title, live, _, _ = get_sport_data(key)
            for s in live:
                all_live.append(f"{title}:\n{s}")
        current = set(all_live)
        new = current - last_scores
        if last_scores and new and CHANNEL:
            for s in list(new)[:3]:
                await context.bot.send_message(chat_id=CHANNEL, text=f"LIVE UPDATE\n\n{s}"[:4000])
        if current:
            last_scores = current
    except Exception as e:
        print("Auto Job Error:", e)

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
    print("Full Detailed Bot Started!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
