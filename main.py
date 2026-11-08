import os
import asyncio
import threading
import requests
import io
from PIL import Image, ImageDraw, ImageFont
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = os.getenv("CHANNEL_ID")

app_flask = Flask(__name__)
@app_flask.route('/')
def home():
    return "Ultra Premium Photo Card Bot Running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# ============ IMAGE CARD GENERATOR - SUPER BEAUTIFUL ============

def create_match_card(h_name, a_name, h_score, a_score, league, status, venue, goals_text=""):
    # 1080 x 640 Premium Card
    W, H = 1080, 640
    img = Image.new('RGB', (W, H), color=(10, 15, 35))
    draw = ImageDraw.Draw(img)

    # Gradient background - dark blue to purple
    for y in range(H):
        r = int(10 + (y/H)*30)
        g = int(15 + (y/H)*10)
        b = int(35 + (y/H)*60)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Top gold line
    draw.rectangle([0, 0, W, 8], fill=(255, 215, 0))
    draw.rectangle([0, H-8, W, H], fill=(255, 215, 0))

    # Fonts - try default
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
        font_team = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_league = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except:
        font_big = ImageFont.load_default()
        font_team = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_league = ImageFont.load_default()

    # League Badge
    draw.rounded_rectangle([340, 30, 740, 90], radius=30, fill=(255, 215, 0))
    draw.text((540, 60), league.upper()[:22], font=font_league, fill=(0,0,0), anchor="mm")

    # Status
    status_color = (255, 60, 60) if "LIVE" in status else (0, 255, 150) if "FULL" in status else (255, 200, 0)
    draw.ellipse([460, 115, 490, 145], fill=status_color)
    draw.text((540, 130), status, font=font_small, fill=(255,255,255), anchor="mm")

    # Teams
    # Home left, Away right
    draw.text((270, 280), h_name[:12].upper(), font=font_team, fill=(255,255,255), anchor="mm")
    draw.text((810, 280), a_name[:12].upper(), font=font_team, fill=(255,255,255), anchor="mm")

    # Score Center - Big
    draw.rounded_rectangle([400, 210, 680, 360], radius=25, fill=(255,255,255))
    draw.text((540, 285), f"{h_score} - {a_score}", font=font_big, fill=(10,15,35), anchor="mm")

    # VS line
    draw.text((540, 400), "VS", font=font_small, fill=(255,215,0), anchor="mm")

    # Venue
    draw.text((540, 450), f"🏟️ {venue[:35]}", font=font_small, fill=(200,200,200), anchor="mm")

    # Goals
    if goals_text:
        draw.text((540, 510), goals_text[:60], font=font_small, fill=(255,255,255), anchor="mm")

    # Footer
    draw.text((540, 580), "✨ BIGO LIVE ASIA  •  @bigolive_asia ✨", font=font_small, fill=(255,215,0), anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# ============ ESPN ============

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

def get_goals_text(dj):
    goals = []
    if dj:
        for d in dj.get('details', []):
            txt = d.get('type', {}).get('text','')
            if 'goal' in txt.lower():
                ath = d['athletesInvolved'][0].get('displayName','') if d.get('athletesInvolved') else ''
                clock = d.get('clock', {}).get('displayValue','')
                goals.append(f"{ath} {clock}'")
    return "  •  ".join(goals[:3])

SPORT_CONFIG = {
    "football": ("FOOTBALL", "soccer", ["eng.1","esp.1","ger.1","ita.1","fra.1","uefa.champions"], "⚽"),
    "cricket": ("CRICKET", "cricket", [""], "🏏"),
    "basketball": ("BASKETBALL", "basketball", ["nba"], "🏀"),
    "tennis": ("TENNIS", "tennis", ["atp","wta"], "🎾"),
    "hockey": ("HOCKEY", "field-hockey", ["fih"], "🏑"),
    "volleyball": ("VOLLEYBALL", "volleyball", ["fivb"], "🏐"),
    "tabletennis": ("TABLE TENNIS", "table-tennis", ["ittf"], "🏓"),
    "baseball": ("BASEBALL", "baseball", ["mlb"], "⚾"),
    "nfl": ("NFL", "football", ["nfl"], "🏈"),
    "badminton": ("BADMINTON", "badminton", ["bwf"], "🏸"),
    "fifa": ("FIFA", "soccer", ["fifa.world"], "🏆"),
}

def build_caption(ev, sport, league, emoji):
    comp = ev['competitions'][0]
    competitors = comp['competitors']
    state = ev.get('status', {}).get('type', {}).get('state')
    short = ev.get('status', {}).get('type', {}).get('shortDetail','')
    detail = ev.get('status', {}).get('type', {}).get('detail','')
    venue = comp.get('venue', {}).get('fullName','Stadium') if comp.get('venue') else 'Stadium'
    h = competitors[0]
    a = competitors[1] if len(competitors)>1 else None
    h_name = h['team'].get('displayName','')
    a_name = a['team'].get('displayName','') if a else ""
    h_score = h.get('score','0')
    a_score = a.get('score','0') if a else "0"
    league_name = ev.get('season', {}).get('slug','').replace('-',' ').upper() if ev.get('season') else league.upper()

    if state == 'in':
        status = f"🔴 LIVE • {short}"
    elif state == 'post':
        status = f"✅ FULL TIME"
    else:
        status = f"🕒 {short}"

    dj = fetch_summary(sport, league, ev.get('id')) if state in ['in','post'] else None
    goals_text = get_goals_text(dj)

    caption = f"✨ <b>{emoji} {league_name} {emoji}</b> ✨\n"
    caption += "━━━━━━━━━━━━━━━━━━\n\n"
    caption += f"<b>{h_name}</b>\n"
    caption += f"<b>     {h_score}  -  {a_score}     </b>\n"
    caption += f"<b>{a_name}</b>\n\n"
    caption += f"{status}\n"
    caption += f"🏟️ {venue}\n"
    if goals_text:
        caption += f"\n⚽ <b>GOALS:</b>\n{goals_text}\n"
    if dj:
        # Stats
        try:
            teams = dj.get('boxscore', {}).get('teams', [])
            if len(teams)>=2:
                for tm in teams:
                    for st in tm.get('statistics', []):
                        if st.get('name')=='possessionPct':
                            caption += f"\n📊 Possession: {st.get('displayValue')}\n"
                            break
        except:
            pass
    caption += "\n━━━━━━━━━━━━━━━━━━\n"
    caption += "📢 <b>@bigolive_asia</b>  •  Follow for More!"
    return caption, h_name, a_name, h_score, a_score, venue, league_name, status

async def send_premium_match(update, ev, sport, league, emoji, key):
    caption, h_name, a_name, h_score, a_score, venue, league_name, status = build_caption(ev, sport, league, emoji)
    # Create image
    img_buf = create_match_card(h_name, a_name, h_score, a_score, league_name, status, venue, goals_text="")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh Score", callback_data=f"refresh_{key}"),
         InlineKeyboardButton("📊 Stats", callback_data=f"stats_{key}")],
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/bigolive_asia")]
    ])
    if update.message:
        await update.message.reply_photo(photo=img_buf, caption=caption, parse_mode="HTML", reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.message.reply_photo(photo=img_buf, caption=caption, parse_mode="HTML", reply_markup=keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚽ Football", callback_data="menu_football"), InlineKeyboardButton("🏏 Cricket", callback_data="menu_cricket")],
        [InlineKeyboardButton("🏀 Basketball", callback_data="menu_basketball"), InlineKeyboardButton("🎾 Tennis", callback_data="menu_tennis")],
        [InlineKeyboardButton("🏆 FIFA", callback_data="menu_fifa"), InlineKeyboardButton("🔴 LIVE ALL", callback_data="menu_live")],
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/bigolive_asia")]
    ])
    await update.message.reply_text(
        "✨ <b>🏆 BIGO LIVE ASIA - ULTRA PREMIUM 🏆</b> ✨\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "👋 Welcome!\n"
        "Now with <b>Beautiful Photo Cards!</b>\n\n"
        "Tap a button below 👇",
        parse_mode="HTML", reply_markup=keyboard
    )

async def sport_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, key):
    title, sport, leagues, emoji = SPORT_CONFIG[key]
    msg = await update.message.reply_text(f"✨ Loading {emoji} {title} Photo Cards...")
    sent = 0
    for league in leagues:
        if sport == "cricket":
            try:
                r = requests.get("https://site.api.espn.com/apis/site/v2/sports/cricket/scoreboard", headers={"User-Agent":"Mozilla/5.0"}, timeout=12).json()
                events = r.get('events', [])
            except:
                events = []
            for ev in events[:2]:
                await update.message.reply_text(f"🏏 <b>{ev.get('name','')}</b>\n{ev.get('status',{}).get('type',{}).get('detail','')}", parse_mode="HTML")
                sent += 1
            continue
        events = fetch_board(sport, league)
        for ev in events[:2]:
            await send_premium_match(update, ev, sport, league, emoji, key)
            sent += 1
            if sent >= 2:
                break
        if sent >= 2:
            break
    await msg.delete()

async def make_handler(key):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await sport_cmd(update, context, key)
    return handler

async def live_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("✨ Loading All Live Photo Cards...")
    for key in SPORT_CONFIG.keys():
        title, sport, leagues, emoji = SPORT_CONFIG[key]
        for league in leagues:
            if sport == "cricket":
                continue
            events = fetch_board(sport, league)
            for ev in events:
                state = ev.get('status', {}).get('type', {}).get('state')
                if state == 'in':
                    await send_premium_match(update, ev, sport, league, emoji, key)
                    break
            break
    await msg.delete()

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data.startswith("menu_"):
        key = data.replace("menu_", "")
        if key == "live":
            await live_cmd(update, context)
        elif key in SPORT_CONFIG:
            # Fake update for sport
            await sport_cmd(update, context, key)
    elif data.startswith("refresh_"):
        await q.message.reply_text("🔄 Refreshing... Send /live again for latest photo card!")

last = set()
async def auto_job(context: ContextTypes.DEFAULT_TYPE):
    global last
    try:
        for key in SPORT_CONFIG.keys():
            title, sport, leagues, emoji = SPORT_CONFIG[key]
            for league in leagues:
                if sport == "cricket":
                    continue
                events = fetch_board(sport, league)
                for ev in events:
                    state = ev.get('status', {}).get('type', {}).get('state')
                    if state == 'in':
                        # Send photo card to channel
                        comp = ev['competitions'][0]
                        h = comp['competitors'][0]
                        a = comp['competitors'][1] if len(comp['competitors'])>1 else None
                        h_name = h['team'].get('displayName','')
                        a_name = a['team'].get('displayName','') if a else ""
                        h_score = h.get('score','0')
                        a_score = a.get('score','0') if a else "0"
                        key_id = f"{h_name}{a_name}{h_score}{a_score}"
                        if key_id not in last:
                            last.add(key_id)
                            caption, hn, an, hs, as_, venue, league_name, status = build_caption(ev, sport, league, emoji)
                            img = create_match_card(hn, an, hs, as_, league_name, status, venue)
                            if CHANNEL:
                                await context.bot.send_photo(chat_id=CHANNEL, photo=img, caption=caption, parse_mode="HTML")
                        break
                break
    except Exception as e:
        print("Auto Error:", e)

async def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("live", live_cmd))
    for key in SPORT_CONFIG.keys():
        h = await make_handler(key)
        app.add_handler(CommandHandler(key, h))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.job_queue.run_repeating(auto_job, interval=120, first=10)
    print("Ultra Premium Photo Bot Started!")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
