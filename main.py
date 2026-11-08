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
    return "Live Score Bot Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# --- FOOTBALL - ESPN Free API ---
def get_football_live():
    try:
        leagues = ["eng.1", "esp.1", "ger.1", "ita.1", "fra.1", "uefa.champions"]
        results = []
        for lg in leagues:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lg}/scoreboard"
            r = requests.get(url, timeout=10).json()
            for ev in r.get('events', []):
                if ev.get('status', {}).get('type', {}).get('state') == 'in':
                    comp = ev['competitions'][0]
                    home = comp['competitors'][0]
                    away = comp['competitors'][1]
                    score = f"{home['team']['shortDisplayName']} {home.get('score','0')} - {away.get('score','0')} {away['team']['shortDisplayName']}"
                    status = ev['status'].get('displayClock', '') + " " + ev['status'].get('type', {}).get('shortDetail','')
                    results.append(f"Football: {score}\nTime: {status} | {ev.get('name','')}")
        return results
    except Exception as e:
        print("Football Error:", e)
        return []

# --- CRICKET ---
def get_cricket_live():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://site.api.espn.com/apis/site/v2/sports/cricket/scoreboard", headers=headers, timeout=10).json()
        results = []
        for ev in r.get('events', []):
            comp = ev['competitions'][0]
            home = comp['competitors'][0]
            away = comp['competitors'][1]
            txt = f"Cricket: {ev.get('name','')}\n{home['team']['displayName']} vs {away['team']['displayName']}\nStatus: {ev['status'].get('type',{}).get('detail','')}"
            results.append(txt)
        return results
    except Exception as e:
        print("Cricket Error:", e)
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "LIVE SCORE HUB\n\n"
        "Commands:\n"
        "/live - All Live Matches\n"
        "/football - Football Live\n"
        "/cricket - Cricket Live\n\n"
        f"Channel: {CHANNEL}"
    )

async def live_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Getting Live Scores...")
    foot = get_football_live()
    cric = get_cricket_live()
    text = "LIVE NOW\n\n"
    if foot:
        text += "FOOTBALL\n" + "\n\n".join(foot) + "\n\n"
    else:
        text += "FOOTBALL: No Live Match Right Now\n\n"
    if cric:
        text += "CRICKET\n" + "\n\n".join(cric)
    else:
        text += "CRICKET: No Live Match Right Now"
    await msg.edit_text(text[:4000])

async def football_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    foot = get_football_live()
    if not foot:
        await update.message.reply_text("No Live Football Match Right Now.")
        return
    await update.message.reply_text("FOOTBALL LIVE\n\n" + "\n\n".join(foot))

async def cricket_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cric = get_cricket_live()
    if not cric:
        await update.message.reply_text("No Live Cricket Match Right Now.")
        return
    await update.message.reply_text("CRICKET LIVE\n\n" + "\n\n".join(cric))

# --- AUTO POST TO CHANNEL ---
last_scores = set()
async def auto_job(context: ContextTypes.DEFAULT_TYPE):
    global last_scores
    try:
        foot = get_football_live()
        cric = get_cricket_live()
        all_scores = set(foot + cric)
        new_scores = all_scores - last_scores
        if last_scores and new_scores and CHANNEL:
            for s in new_scores:
                await context.bot.send_message(chat_id=CHANNEL, text=f"LIVE UPDATE\n\n{s}\n\nJoin for more Live Scores")
        if all_scores:
            last_scores = all_scores
    except Exception as e:
        print("Auto Job Error:", e)

async def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("live", live_cmd))
    app.add_handler(CommandHandler("football", football_cmd))
    app.add_handler(CommandHandler("cricket", cricket_cmd))
    app.job_queue.run_repeating(auto_job, interval=120, first=10)
    print("Live Score Bot Started!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
