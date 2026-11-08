# 🌍 ŸᗅĐᗅŇᗅᏒ💗 Live Sports

### 🏆 PREMIUM SPORTS - LIVE SCORES BOT

<p align="center">
  <img src="https://img.shields.io/badge/Telegram-Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Online-00C853?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Version-2.0.0-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

<p align="center">
  <b>⚽ Football • 🏏 Cricket • 🏀 Basketball • 🎾 Tennis • 🏎️ F1 • ⛳ Golf • 🏸 Badminton</b><br>
  <b>🔴 LIVE SCORES • Every 3 Minutes • ⚡ GOAL ALERTS • Instant</b>
</p>

<p align="center">
  🤖 <b>Try The Bot:</b> <a href="https://t.me/YadanarLiveSportsBot">@YadanarLiveSportsBot</a><br>
  💬 <b>Support:</b> <a href="https://t.me/bigolive_asia">@bigolive_asia</a><br>
  📢 <b>Channel:</b> <a href="https://t.me/bigolive_asia">Join Channel</a>
</p>

---

## 📑 Table Of Contents

- [✨ Features](#-features)
- [🎮 How To Use](#-how-to-use)
- [⌨️ Commands](#️-commands)
- [🚀 Tech Stack](#-tech-stack)
- [⚙️ Installation](#️-installation)
- [☁️ Deploy To Render](#️-deploy-to-render)
- [🔑 Environment Variables](#-environment-variables)
- [📁 Project Structure](#-project-structure)
- [📸 Preview](#-preview)
- [🌐 Languages](#-languages)
- [🏆 Supported Leagues](#-supported-leagues)
- [🤝 Contributing](#-contributing)
- [🤝 Support](#-support)
- [📄 License](#-license)

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| 🔴 Live Scores | Auto update every 3 minutes |
| ⚽ Goal Alerts | Instant goal notification with scorer name |
| 🏏 Cricket Live | Ball by ball update, live commentary, wickets |
| 📰 News + Score | Sports news + live score together in one place |
| 📊 Match Stats | Possession, shots, corners, lineups, player stats |
| 🏆 All Tournaments | IPL • LPL • EPL • La Liga • Champions League • FIFA • World Cup • Asia Cup |
| 🌐 23 Languages | English • Tamil • Hindi • Spanish • French • Arabic + 17 More |
| ⚡ Super Fast | Beautiful design, fast response, no lag |
| 🔔 Notifications | Get notified when your favourite team scores |
| ⭐ Favourites | Save your favourite teams |
| 💎 100% Free | No premium, no ads, no hidden charges |

---

## 🎮 How To Use

### Step 1 - Start The Bot
Click here 👉 [@YadanarLiveSportsBot](https://t.me/YadanarLiveSportsBot) and press START

Or send: /start

### Step 2 - Choose Your Language
Select your language from the menu. 23 languages available.

### Step 3 - Choose Your Sport
    ⚽ Football
    🏏 Cricket
    🏀 Basketball
    🎾 Tennis
    🏎️ F1
    ⛳ Golf
    🏸 Badminton

### Step 4 - Enjoy Live Updates
- Click on any live match
- Get score, stats, lineups, news
- Turn on alerts for your team

---

## ⌨️ Commands

| Command | What It Does |
| :--- | :--- |
| /start | Start the bot and show welcome message |
| /live | Show all live matches right now |
| /football | Football live scores |
| /cricket | Cricket live scores |
| /basketball | Basketball live scores |
| /tennis | Tennis live scores |
| /news | Latest sports news |
| /favourites | Your saved favourite teams |
| /language | Change language |
| /help | Help menu |
| /about | About this bot |

---

## 🚀 Tech Stack

- Language: Python 3.11
- Framework: python-telegram-bot 20.7
- Hosting: Render.com (Free Tier)
- Web Server: Flask
- API: Live Sports API
- Database: JSON / In-Memory Cache
- Version Control: Git + GitHub

---

## ⚙️ Installation

### 1. Clone Repo
    git clone https://github.com/your-username/yadanar-live-sports-bot.git
    cd yadanar-live-sports-bot

### 2. Install Dependencies
    pip install -r requirements.txt

### 3. Set Environment Variables
Create a .env file in root folder:
    BOT_TOKEN=your_bot_token_here
    SPORTS_API_KEY=your_api_key_here
    CHANNEL_ID=your_channel_id_here

### 4. Run Bot Locally
    python main.py

You will see:
    Bot Started!
    Yadanar Live Sports Bot Running!

### 5. Test On Telegram
Go to [@YadanarLiveSportsBot](https://t.me/YadanarLiveSportsBot) and send /start

---

## ☁️ Deploy To Render

This bot is designed to run 24/7 on Render.com for FREE.

### Step 1 - Push To GitHub
Push all files to GitHub repo.

### Step 2 - Create Web Service
1. Go to [render.com](https://render.com)
2. Click New + -> Web Service
3. Select your GitHub repo
4. Set:
   - Name: yadanar-live-sports-bot
   - Environment: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: python main.py
   - Instance Type: Free

### Step 3 - Add Environment Variables
In Render Dashboard -> Environment:
    BOT_TOKEN = your_bot_token_here
    SPORTS_API_KEY = your_api_key_here
    CHANNEL_ID = your_channel_id_here

### Step 4 - Deploy
Click Create Web Service. Wait 2-3 minutes. Bot will be Online.

Note: Render Free Tier sleeps after 15 min of inactivity. To keep bot always online, use UptimeRobot to ping your Render URL every 5 minutes.

---

## 🔑 Environment Variables

| Variable | Required | Description | Example |
| :--- | :--- | :--- | :--- |
| BOT_TOKEN | Yes | Bot token from @BotFather | 123456:ABC-DEF... |
| SPORTS_API_KEY | Yes | Sports API key | your_api_key |
| CHANNEL_ID | No | Channel ID for auto posts | -1001234567890 |
| PORT | No | Port for Flask server | 10000 |

---

## 📁 Project Structure

    yadanar-live-sports-bot/
    ├── main.py                 # Main bot file - all logic here
    ├── requirements.txt        # Python dependencies
    ├── README.md               # This file - project documentation
    ├── .env                    # Environment variables (DO NOT push to GitHub)
    ├── .gitignore              # Git ignore file
    ├── utils/
    │   ├── api.py              # Sports API functions
    │   ├── keyboards.py        # Inline keyboards / Buttons
    │   ├── messages.py         # All text messages
    │   └── helpers.py          # Helper functions
    └── data/
        ├── languages.json      # 23 languages translations
        └── teams.json          # Teams data

---

## 📸 Preview

### Welcome Message
    ╔══════════════════════════════╗
    ║  ✨ 🏆 PREMIUM SPORTS 🏆 ✨  ║
    ╚══════════════════════════════╝
        ⚽  🏏  🏀  🎾  🏈  ⚾
      Welcome to 🌍 ŸᗅĐᗅŇᗅᏒ💗 Live Sports
    ━━━━━━━━━━━━━━━━━━━━━━
    🔴 LIVE SCORES • Every 3 Minutes
    ⚽ GOAL ALERTS • Instant Update
    🏏 CRICKET • Ball By Ball
    📰 NEWS + SCORE • Together
    🏆 IPL • LPL • EPL • FIFA • World Cup
    ━━━━━━━━━━━━━━━━━━━━━━
    👇 CHOOSE YOUR SPORT BELOW 👇
    ━━━━━━━━━━━━━━━━━━━━━━
    💎 Fastest • Beautiful • Free

### Live Score Example
    🔴 LIVE • 67'
    ⚽ Manchester United 2 - 1 Arsenal
    ⚽ 23' Rashford
    ⚽ 45' Saka
    ⚽ 67' Fernandes (PEN)
    ━━━━━━━━━━━━━━━━━━━━━━
    📊 Stats | 👥 Lineups | 📰 News

### Cricket Score Example
    🔴 LIVE • 2nd Innings
    🏏 Sri Lanka 186/4 (18.2 Ov)
    🏏 India 182/8 (20 Ov)
    Sri Lanka Need  -3 Runs To Win
    🏏 Kusal Mendis 72* (41)
    🏏 Pathum Nissanka 45 (30)
    ━━━━━━━━━━━━━━━━━━━━━━
    📊 Scorecard | 💬 Commentary

---

## 🌐 Languages

We support 23 languages:

| # | Language | # | Language |
| :--- | :--- | :--- | :--- |
| 1 | English | 13 | Portuguese |
| 2 | Tamil | 14 | German |
| 3 | Hindi | 15 | Italian |
| 4 | Spanish | 16 | Russian |
| 5 | French | 17 | Japanese |
| 6 | Arabic | 18 | Korean |
| 7 | Bengali | 19 | Turkish |
| 8 | Urdu | 20 | Dutch |
| 9 | Malayalam | 21 | Thai |
| 10 | Telugu | 22 | Vietnamese |
| 11 | Kannada | 23 | Indonesian |
| 12 | Chinese | - | More Coming Soon |

Change language anytime with /language

---

## 🏆 Supported Leagues

### ⚽ Football
- English Premier League (EPL)
- La Liga
- Serie A
- Bundesliga
- Ligue 1
- UEFA Champions League
- UEFA Europa League
- FIFA World Cup
- Copa America

### 🏏 Cricket
- Indian Premier League (IPL)
- Lanka Premier League (LPL)
- Big Bash League (BBL)
- ICC World Cup
- ICC T20 World Cup
- Asia Cup
- The Ashes
- Pakistan Super League (PSL)

### 🏀 Basketball
- NBA
- EuroLeague
- FIBA World Cup

### 🎾 Tennis
- Wimbledon
- US Open
- French Open
- Australian Open

### 🏎️ Formula 1
- F1 World Championship
- All Grand Prix

---

## 🤝 Contributing

We love contributions!

1. Fork this repo
2. Create your branch: git checkout -b feature/AmazingFeature
3. Commit your changes: git commit -m 'Add AmazingFeature'
4. Push to branch: git push origin feature/AmazingFeature
5. Open a Pull Request

---

## 🐛 Bug Report

Found a bug? Please open an issue:

1. Go to Issues tab
2. Click New Issue
3. Describe the bug with screenshot
4. We will fix it ASAP

---

## 🤝 Support

- 🤖 Bot: [@YadanarLiveSportsBot](https://t.me/YadanarLiveSportsBot)
- 💬 Support: [@bigolive_asia](https://t.me/bigolive_asia)
- 📢 Channel: Join our channel for updates
- 🐛 Issues: Open an issue in this repo

If you like this bot, please give it a ⭐ on GitHub!

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

    MIT License
    Copyright (c) 2026 Yadanar Live Sports
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

---

## 🙏 Credits

- Developer: [@bigolive_asia](https://t.me/bigolive_asia)
- Bot: [@YadanarLiveSportsBot](https://t.me/YadanarLiveSportsBot)
- API: Live Sports API
- Hosting: Render.com

---

<p align="center">
  <b>🌍 ŸᗅĐᗅŇᗅᏒ💗 Live Sports</b><br>
  <b>⚡ Fastest Sports Updates ⚡</b><br><br>
  <a href="https://t.me/YadanarLiveSportsBot">🚀 Try Bot Now</a><br><br>
  Made with ❤️ by <a href="https://t.me/bigolive_asia">@bigolive_asia</a><br>
  ⭐ Star this repo if you like it!
</p>
