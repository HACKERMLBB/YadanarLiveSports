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
def home(): return "Premium Sports Bot Running!"
@app_flask.route('/ping')
def ping(): return "OK", 200
@app_flask.route('/health')
def health(): return "Bot is Alive", 200
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False)

# ========== TRANSLATION SYSTEM ==========
USER_LANG = {}
T = {
 "en": {"welcome":"👋 Welcome, Champion!","choose":"👇 CHOOSE YOUR SPORT BELOW 👇","lang_btn":"🌐 YOUR LANGUAGES","news_btn":"📰 SPORTS NEWS + SCORE","football":"⚽ Football","cricket":"🏏 Cricket","ipl":"🔥 IPL LIVE","lpl":"🇱🇰 LPL / SL","basketball":"🏀 Basketball","tennis":"🎾 Tennis","hockey":"🏑 Hockey","volleyball":"🏐 Volleyball","tabletennis":"🏓 Table Tennis","baseball":"⚾ Baseball","nfl":"🏈 NFL","badminton":"🏸 Badminton","f1":"🏎️ F1 Racing","golf":"⛳ Golf","ufc":"🥊 UFC / Boxing","rugby":"🏉 Rugby","kabaddi":"🤼 Kabaddi","esports":"🎮 E-Sports","fifa":"🏆 FIFA","live_all":"🔴 LIVE ALL","results":"✅ RESULTS","table":"🏆 POINTS TABLE","tomorrow":"📅 TOMORROW","search":"🔍 SEARCH","back":"⬅ Back to Menu","refresh":"🔄 Refresh","live_now":"🔴 LIVE NOW","full_time":"✅ FULL TIME","upcoming":"🕒 UPCOMING","won":"Won!","draw":"🤝 Draw Match","vs":"VS","stats":"📊 MATCH STATISTICS","goals":"⚽ GOAL SCORERS","cards":"🟨 CARDS","subs":"🔄 SUBSTITUTIONS","timeline":"📜 MATCH TIMELINE","not_started":"⏳ Match not started yet. Stay tuned!","loading":"✨ Loading...","saved":"✅ Language Saved!","choose_lang":"🌐 CHOOSE YOUR LANGUAGE","join":"Join Channel","cricket_details":"🏏 CRICKET DETAILS","news_title":"📰 SPORTS NEWS + LIVE SCORE","score":"📊 SCORE","read_news":"Read Full News"},
 "si": {"welcome":"👋 ආයුබෝවන්! චැම්පියන්!","choose":"👇 ඔබේ ක්‍රීඩාව තෝරන්න 👇","lang_btn":"🌐 ඔබේ භාෂාව","news_btn":"📰 ක්‍රීඩා පුවත් + ලකුණු","football":"⚽ පාපන්දු","cricket":"🏏 ක්‍රිකට්","ipl":"🔥 IPL සජීවී","lpl":"🇱🇰 LPL / ශ්‍රී ලංකා","basketball":"🏀 පැසිපන්දු","tennis":"🎾 ටෙනිස්","hockey":"🏑 හොකී","volleyball":"🏐 වොලිබෝල්","tabletennis":"🏓 ටේබල් ටෙනිස්","baseball":"⚾ බේස්බෝල්","nfl":"🏈 NFL","badminton":"🏸 බැඩ්මින්ටන්","f1":"🏎️ F1 රේසිං","golf":"⛳ ගොල්ෆ්","ufc":"🥊 UFC / බොක්සිං","rugby":"🏉 රග්බි","kabaddi":"🤼 කබඩි","esports":"🎮 ඊ-ස්පෝර්ට්ස්","fifa":"🏆 FIFA","live_all":"🔴 සජීවී සියල්ල","results":"✅ ප්‍රතිඵල","table":"🏆 ලකුණු වගුව","tomorrow":"📅 හෙට","search":"🔍 සොයන්න","back":"⬅ මෙනුවට","refresh":"🔄 නැවත","live_now":"🔴 සජීවී දැන්","full_time":"✅ අවසන්","upcoming":"🕒 ඉදිරියට","won":"දිනුවා!","draw":"🤝 ජය පරාජයෙන් තොරයි","vs":"VS","stats":"📊 තරග සංඛ්‍යාලේඛන","goals":"⚽ ගෝල් ගහපු අය","cards":"🟨 කාඩ්","subs":"🔄 ආදේශක","timeline":"📜 තරග සිදුවීම්","not_started":"⏳ තරගය තවම පටන් ගත්තේ නෑ. රැඳී ඉන්න!","loading":"✨ ලෝඩ් වෙනවා...","saved":"✅ භාෂාව සුරකින ලදී!","choose_lang":"🌐 ඔබේ භාෂාව තෝරන්න","join":"Channel එකට Join වෙන්න","cricket_details":"🏏 ක්‍රිකට් විස්තර","news_title":"📰 ක්‍රීඩා පුවත් + සජීවී ලකුණු","score":"📊 ලකුණු","read_news":"සම්පූර්ණ පුවත කියවන්න"},
 "ta": {"welcome":"👋 வணக்கம்! சாம்பியன்!","choose":"👇 உங்கள் விளையாட்டை தேர்வு செய்யவும் 👇","lang_btn":"🌐 உங்கள் மொழி","news_btn":"📰 விளையாட்டு செய்திகள் + ஸ்கோர்","football":"⚽ கால்பந்து","cricket":"🏏 கிரிக்கெட்","ipl":"🔥 IPL நேரலை","lpl":"🇱🇰 LPL / இலங்கை","basketball":"🏀 கூடைப்பந்து","tennis":"🎾 டென்னிஸ்","hockey":"🏑 ஹாக்கி","volleyball":"🏐 கைப்பந்து","tabletennis":"🏓 டேபிள் டென்னிஸ்","baseball":"⚾ பேஸ்பால்","nfl":"🏈 NFL","badminton":"🏸 பேட்மிண்டன்","f1":"🏎️ F1 பந்தயம்","golf":"⛳ கோல்ஃப்","ufc":"🥊 UFC / குத்துச்சண்டை","rugby":"🏉 ரக்பி","kabaddi":"🤼 கபடி","esports":"🎮 இ-ஸ்போர்ட்ஸ்","fifa":"🏆 FIFA","live_all":"🔴 நேரலை அனைத்தும்","results":"✅ முடிவுகள்","table":"🏆 புள்ளிகள் அட்டவணை","tomorrow":"📅 நாளை","search":"🔍 தேடுக","back":"⬅ மெனுவுக்கு","refresh":"🔄 புதுப்பி","live_now":"🔴 நேரலை இப்போது","full_time":"✅ முடிந்தது","upcoming":"🕒 வரவிருக்கும்","won":"வென்றது!","draw":"🤝 டிரா","vs":"VS","stats":"📊 போட்டி புள்ளிவிவரங்கள்","goals":"⚽ கோல் அடித்தவர்கள்","cards":"🟨 அட்டைகள்","subs":"🔄 மாற்றுகள்","timeline":"📜 போட்டி நிகழ்வுகள்","not_started":"⏳ போட்டி இன்னும் தொடங்கவில்லை!","loading":"✨ ஏற்றுகிறது...","saved":"✅ மொழி சேமிக்கப்பட்டது!","choose_lang":"🌐 உங்கள் மொழியை தேர்வு செய்யவும்","join":"சேனலில் சேரவும்","cricket_details":"🏏 கிரிக்கெட் விவரங்கள்","news_title":"📰 விளையாட்டு செய்திகள் + நேரலை ஸ்கோர்","score":"📊 ஸ்கோர்","read_news":"முழு செய்தியை படிக்கவும்"},
 "hi": {"welcome":"👋 नमस्ते! चैंपियन!","choose":"👇 अपना खेल चुनें 👇","lang_btn":"🌐 आपकी भाषा","news_btn":"📰 खेल समाचार + स्कोर","football":"⚽ फुटबॉल","cricket":"🏏 क्रिकेट","ipl":"🔥 IPL लाइव","lpl":"🇱🇰 LPL / श्रीलंका","basketball":"🏀 बास्केटबॉल","tennis":"🎾 टेनिस","hockey":"🏑 हॉकी","volleyball":"🏐 वॉलीबॉल","tabletennis":"🏓 टेबल टेनिस","baseball":"⚾ बेसबॉल","nfl":"🏈 NFL","badminton":"🏸 बैडमिंटन","f1":"🏎️ F1 रेसिंग","golf":"⛳ गोल्फ","ufc":"🥊 UFC / बॉक्सिंग","rugby":"🏉 रग्बी","kabaddi":"🤼 कबड्डी","esports":"🎮 ई-स्पोर्ट्स","fifa":"🏆 FIFA","live_all":"🔴 लाइव सभी","results":"✅ परिणाम","table":"🏆 अंक तालिका","tomorrow":"📅 कल","search":"🔍 खोजें","back":"⬅ मेनू पर","refresh":"🔄 रिफ्रेश","live_now":"🔴 लाइव अभी","full_time":"✅ समाप्त","upcoming":"🕒 आगामी","won":"जीता!","draw":"🤝 ड्रॉ","vs":"VS","stats":"📊 मैच आंकड़े","goals":"⚽ गोल करने वाले","cards":"🟨 कार्ड","subs":"🔄 बदलाव","timeline":"📜 मैच घटनाएं","not_started":"⏳ मैच अभी शुरू नहीं हुआ!","loading":"✨ लोड हो रहा है...","saved":"✅ भाषा सहेजी गई!","choose_lang":"🌐 अपनी भाषा चुनें","join":"चैनल जॉइन करें","cricket_details":"🏏 क्रिकेट विवरण","news_title":"📰 खेल समाचार + लाइव स्कोर","score":"📊 स्कोर","read_news":"पूरी खबर पढ़ें"},
 "ur": {"welcome":"👋 خوش آمدید! چیمپئن!","choose":"👇 اپنا کھیل منتخب کریں 👇","lang_btn":"🌐 آپ کی زبان","news_btn":"📰 کھیلوں کی خبریں + اسکور","football":"⚽ فٹبال","cricket":"🏏 کرکٹ","ipl":"🔥 IPL لائیو","lpl":"🇱🇰 LPL / سری لنکا","basketball":"🏀 باسکٹ بال","tennis":"🎾 ٹینس","hockey":"🏑 ہاکی","volleyball":"🏐 والی بال","tabletennis":"🏓 ٹیبل ٹینس","baseball":"⚾ بیس بال","nfl":"🏈 NFL","badminton":"🏸 بیڈمنٹن","f1":"🏎️ F1 ریسنگ","golf":"⛳ گولف","ufc":"🥊 UFC / باکسنگ","rugby":"🏉 رگبی","kabaddi":"🤼 کبڈی","esports":"🎮 ای اسپورٹس","fifa":"🏆 FIFA","live_all":"🔴 لائیو سب","results":"✅ نتائج","table":"🏆 پوائنٹس ٹیبل","tomorrow":"📅 کل","search":"🔍 تلاش","back":"⬅ مینو پر","refresh":"🔄 ریفریش","live_now":"🔴 لائیو ابھی","full_time":"✅ ختم","upcoming":"🕒 آنے والا","won":"جیت گیا!","draw":"🤝 ڈرا","vs":"VS","stats":"📊 میچ کے اعداد","goals":"⚽ گول کرنے والے","cards":"🟨 کارڈ","subs":"🔄 تبدیلیاں","timeline":"📜 میچ کی घटनाएं","not_started":"⏳ میچ ابھی شروع نہیں ہوا!","loading":"✨ لوڈ ہو رہا ہے...","saved":"✅ زبان محفوظ ہو گئی!","choose_lang":"🌐 اپنی زبان منتخب کریں","join":"چینل جوائن کریں","cricket_details":"🏏 کرکٹ تفصیلات","news_title":"📰 کھیلوں کی خبریں + لائیو اسکور","score":"📊 اسکور","read_news":"مکمل خبر پڑھیں"},
 "bn": {"welcome":"👋 স্বাগতম! চ্যাম্পিয়ন!","choose":"👇 আপনার খেলা বেছে নিন 👇","lang_btn":"🌐 আপনার ভাষা","news_btn":"📰 খেলার খবর + স্কোর","football":"⚽ ফুটবল","cricket":"🏏 ক্রিকেট","ipl":"🔥 IPL লাইভ","lpl":"🇱🇰 LPL / শ্রীলঙ্কা","basketball":"🏀 বাস্কেটবল","tennis":"🎾 টেনিস","hockey":"🏑 হকি","volleyball":"🏐 ভলিবল","tabletennis":"🏓 টেবিল টেনিস","baseball":"⚾ বেসবল","nfl":"🏈 NFL","badminton":"🏸 ব্যাডমিন্টন","f1":"🏎️ F1 রেসিং","golf":"⛳ গলফ","ufc":"🥊 UFC / বক্সিং","rugby":"🏉 রাগবি","kabaddi":"🤼 কাবাডি","esports":"🎮 ই-স্পোর্টস","fifa":"🏆 FIFA","live_all":"🔴 লাইভ সব","results":"✅ ফলাফল","table":"🏆 পয়েন্ট টেবিল","tomorrow":"📅 আগামীকাল","search":"🔍 খুঁজুন","back":"⬅ মেনুতে","refresh":"🔄 রিফ্রেশ","live_now":"🔴 লাইভ এখন","full_time":"✅ শেষ","upcoming":"🕒 আসন্ন","won":"জিতেছে!","draw":"🤝 ড্র","vs":"VS","stats":"📊 ম্যাচ পরিসংখ্যান","goals":"⚽ গোলদাতা","cards":"🟨 কার্ড","subs":"🔄 বদলি","timeline":"📜 ম্যাচ ঘটনা","not_started":"⏳ ম্যাচ এখনও শুরু হয়নি!","loading":"✨ লোড হচ্ছে...","saved":"✅ ভাষা সংরক্ষিত!","choose_lang":"🌐 আপনার ভাষা বেছে নিন","join":"চ্যানেলে যোগ দিন","cricket_details":"🏏 ক্রিকেট বিবরণ","news_title":"📰 খেলার খবর + লাইভ স্কোর","score":"📊 স্কোর","read_news":"পুরো খবর পড়ুন"},
 "ar": {"welcome":"👋 مرحبا! أيها البطل!","choose":"👇 اختر رياضتك 👇","lang_btn":"🌐 لغتك","news_btn":"📰 أخبار الرياضة + النتيجة","football":"⚽ كرة القدم","cricket":"🏏 كريكيت","ipl":"🔥 IPL مباشر","lpl":"🇱🇰 LPL / سريلانكا","basketball":"🏀 كرة السلة","tennis":"🎾 تنس","hockey":"🏑 هوكي","volleyball":"🏐 كرة طائرة","tabletennis":"🏓 تنس طاولة","baseball":"⚾ بيسبول","nfl":"🏈 NFL","badminton":"🏸 ريشة","f1":"🏎️ سباق F1","golf":"⛳ غولف","ufc":"🥊 UFC / ملاكمة","rugby":"🏉 رغبي","kabaddi":"🤼 كابادي","esports":"🎮 رياضات إلكترونية","fifa":"🏆 FIFA","live_all":"🔴 مباشر الكل","results":"✅ النتائج","table":"🏆 جدول النقاط","tomorrow":"📅 غدا","search":"🔍 بحث","back":"⬅ للقائمة","refresh":"🔄 تحديث","live_now":"🔴 مباشر الآن","full_time":"✅ انتهت","upcoming":"🕒 قادمة","won":"فاز!","draw":"🤝 تعادل","vs":"VS","stats":"📊 إحصائيات المباراة","goals":"⚽ مسجلو الأهداف","cards":"🟨 البطاقات","subs":"🔄 التبديلات","timeline":"📜 أحداث المباراة","not_started":"⏳ لم تبدأ المباراة بعد!","loading":"✨ جاري التحميل...","saved":"✅ تم حفظ اللغة!","choose_lang":"🌐 اختر لغتك","join":"انضم للقناة","cricket_details":"🏏 تفاصيل الكريكيت","news_title":"📰 أخبار الرياضة + النتيجة المباشرة","score":"📊 النتيجة","read_news":"اقرأ الخبر كاملا"},
 "es": {"welcome":"👋 ¡Bienvenido, Campeón!","choose":"👇 ELIGE TU DEPORTE 👇","lang_btn":"🌐 TU IDIOMA","news_btn":"📰 NOTICIAS + MARCADOR","football":"⚽ Fútbol","cricket":"🏏 Cricket","ipl":"🔥 IPL EN VIVO","lpl":"🇱🇰 LPL / Sri Lanka","basketball":"🏀 Baloncesto","tennis":"🎾 Tenis","hockey":"🏑 Hockey","volleyball":"🏐 Voleibol","tabletennis":"🏓 Tenis de Mesa","baseball":"⚾ Béisbol","nfl":"🏈 NFL","badminton":"🏸 Bádminton","f1":"🏎️ F1 Carreras","golf":"⛳ Golf","ufc":"🥊 UFC / Boxeo","rugby":"🏉 Rugby","kabaddi":"🤼 Kabaddi","esports":"🎮 E-Sports","fifa":"🏆 FIFA","live_all":"🔴 EN VIVO TODO","results":"✅ RESULTADOS","table":"🏆 TABLA DE PUNTOS","tomorrow":"📅 MAÑANA","search":"🔍 BUSCAR","back":"⬅ Al Menú","refresh":"🔄 Actualizar","live_now":"🔴 EN VIVO AHORA","full_time":"✅ TIEMPO COMPLETO","upcoming":"🕒 PRÓXIMO","won":"¡Ganó!","draw":"🤝 Empate","vs":"VS","stats":"📊 ESTADÍSTICAS","goals":"⚽ GOLEADORES","cards":"🟨 TARJETAS","subs":"🔄 CAMBIOS","timeline":"📜 EVENTOS","not_started":"⏳ ¡El partido aún no empieza!","loading":"✨ Cargando...","saved":"✅ ¡Idioma Guardado!","choose_lang":"🌐 ELIGE TU IDIOMA","join":"Unirse al Canal","cricket_details":"🏏 DETALLES DE CRICKET","news_title":"📰 NOTICIAS + MARCADOR EN VIVO","score":"📊 MARCADOR","read_news":"Leer Noticia Completa"},
 "fr": {"welcome":"👋 Bienvenue, Champion!","choose":"👇 CHOISISSEZ VOTRE SPORT 👇","lang_btn":"🌐 VOTRE LANGUE","news_btn":"📰 ACTUS + SCORE","football":"⚽ Football","cricket":"🏏 Cricket","ipl":"🔥 IPL EN DIRECT","lpl":"🇱🇰 LPL / Sri Lanka","basketball":"🏀 Basketball","tennis":"🎾 Tennis","hockey":"🏑 Hockey","volleyball":"🏐 Volley","tabletennis":"🏓 Tennis de Table","baseball":"⚾ Baseball","nfl":"🏈 NFL","badminton":"🏸 Badminton","f1":"🏎️ F1 Course","golf":"⛳ Golf","ufc":"🥊 UFC / Boxe","rugby":"🏉 Rugby","kabaddi":"🤼 Kabaddi","esports":"🎮 E-Sports","fifa":"🏆 FIFA","live_all":"🔴 EN DIRECT TOUT","results":"✅ RÉSULTATS","table":"🏆 CLASSEMENT","tomorrow":"📅 DEMAIN","search":"🔍 RECHERCHER","back":"⬅ Au Menu","refresh":"🔄 Actualiser","live_now":"🔴 EN DIRECT","full_time":"✅ TERMINÉ","upcoming":"🕒 À VENIR","won":"A Gagné!","draw":"🤝 Match Nul","vs":"VS","stats":"📊 STATISTIQUES","goals":"⚽ BUTEURS","cards":"🟨 CARTONS","subs":"🔄 REMPLACEMENTS","timeline":"📜 ÉVÉNEMENTS","not_started":"⏳ Le match n'a pas encore commencé!","loading":"✨ Chargement...","saved":"✅ Langue Enregistrée!","choose_lang":"🌐 CHOISISSEZ VOTRE LANGUE","join":"Rejoindre la Chaîne","cricket_details":"🏏 DÉTAILS CRICKET","news_title":"📰 ACTUS + SCORE EN DIRECT","score":"📊 SCORE","read_news":"Lire l'Article"},
 "pt": {"welcome":"👋 Bem-vindo, Campeão!","choose":"👇 ESCOLHA SEU ESPORTE 👇","lang_btn":"🌐 SEU IDIOMA","news_btn":"📰 NOTÍCIAS + PLACAR","football":"⚽ Futebol","cricket":"🏏 Críquete","ipl":"🔥 IPL AO VIVO","lpl":"🇱🇰 LPL / Sri Lanka","basketball":"🏀 Basquete","tennis":"🎾 Tênis","hockey":"🏑 Hóquei","volleyball":"🏐 Vôlei","tabletennis":"🏓 Tênis de Mesa","baseball":"⚾ Beisebol","nfl":"🏈 NFL","badminton":"🏸 Badminton","f1":"🏎️ F1 Corrida","golf":"⛳ Golfe","ufc":"🥊 UFC / Boxe","rugby":"🏉 Rugby","kabaddi":"🤼 Kabaddi","esports":"🎮 E-Sports","fifa":"🏆 FIFA","live_all":"🔴 AO VIVO TUDO","results":"✅ RESULTADOS","table":"🏆 TABELA","tomorrow":"📅 AMANHÃ","search":"🔍 PESQUISAR","back":"⬅ Ao Menu","refresh":"🔄 Atualizar","live_now":"🔴 AO VIVO AGORA","full_time":"✅ FIM","upcoming":"🕒 PRÓXIMO","won":"Ganhou!","draw":"🤝 Empate","vs":"VS","stats":"📊 ESTATÍSTICAS","goals":"⚽ ARTILHEIROS","cards":"🟨 CARTÕES","subs":"🔄 SUBSTITUIÇÕES","timeline":"📜 EVENTOS","not_started":"⏳ O jogo ainda não começou!","loading":"✨ Carregando...","saved":"✅ Idioma Salvo!","choose_lang":"🌐 ESCOLHA SEU IDIOMA","join":"Entrar no Canal","cricket_details":"🏏 DETALHES CRÍQUETE","news_title":"📰 NOTÍCIAS + PLACAR AO VIVO","score":"📊 PLACAR","read_news":"Ler Notícia Completa"},
 "ru": {"welcome":"👋 Добро пожаловать, Чемпион!","choose":"👇 ВЫБЕРИТЕ СВОЙ СПОРТ 👇","lang_btn":"🌐 ВАШ ЯЗЫК","news_btn":"📰 НОВОСТИ + СЧЁТ","football":"⚽ Футбол","cricket":"🏏 Крикет","ipl":"🔥 IPL LIVE","lpl":"🇱🇰 LPL / Шри-Ланка","basketball":"🏀 Баскетбол","tennis":"🎾 Теннис","hockey":"🏑 Хоккей","volleyball":"🏐 Волейбол","tabletennis":"🏓 Настольный Теннис","baseball":"⚾ Бейсбол","nfl":"🏈 NFL","badminton":"🏸 Бадминтон","f1":"🏎️ F1 Гонки","golf":"⛳ Гольф","ufc":"🥊 UFC / Бокс","rugby":"🏉 Регби","kabaddi":"🤼 Кабадди","esports":"🎮 Киберспорт","fifa":"🏆 FIFA","live_all":"🔴 LIVE ВСЕ","results":"✅ РЕЗУЛЬТАТЫ","table":"🏆 ТАБЛИЦА","tomorrow":"📅 ЗАВТРА","search":"🔍 ПОИСК","back":"⬅ В Меню","refresh":"🔄 Обновить","live_now":"🔴 LIVE СЕЙЧАС","full_time":"✅ ФИНАЛ","upcoming":"🕒 СКОРО","won":"Победил!","draw":"🤝 Ничья","vs":"VS","stats":"📊 СТАТИСТИКА","goals":"⚽ БОМБАРДИРЫ","cards":"🟨 КАРТОЧКИ","subs":"🔄 ЗАМЕНЫ","timeline":"📜 СОБЫТИЯ","not_started":"⏳ Матч еще не начался!","loading":"✨ Загрузка...","saved":"✅ Язык Сохранён!","choose_lang":"🌐 ВЫБЕРИТЕ ЯЗЫК","join":"Вступить в Канал","cricket_details":"🏏 ДЕТАЛИ КРИКЕТА","news_title":"📰 НОВОСТИ + СЧЁТ LIVE","score":"📊 СЧЁТ","read_news":"Читать Новость"},
 "zh": {"welcome":"👋 欢迎，冠军！","choose":"👇 选择你的运动 👇","lang_btn":"🌐 你的语言","news_btn":"📰 体育新闻 + 比分","football":"⚽ 足球","cricket":"🏏 板球","ipl":"🔥 IPL 直播","lpl":"🇱🇰 LPL / 斯里兰卡","basketball":"🏀 篮球","tennis":"🎾 网球","hockey":"🏑 曲棍球","volleyball":"🏐 排球","tabletennis":"🏓 乒乓球","baseball":"⚾ 棒球","nfl":"🏈 NFL","badminton":"🏸 羽毛球","f1":"🏎️ F1 赛车","golf":"⛳ 高尔夫","ufc":"🥊 UFC / 拳击","rugby":"🏉 橄榄球","kabaddi":"🤼 卡巴迪","esports":"🎮 电竞","fifa":"🏆 FIFA","live_all":"🔴 全部直播","results":"✅ 成绩","table":"🏆 积分榜","tomorrow":"📅 明天","search":"🔍 搜索","back":"⬅ 回菜单","refresh":"🔄 刷新","live_now":"🔴 正在直播","full_time":"✅ 全场结束","upcoming":"🕒 即将开始","won":"赢了!","draw":"🤝 平局","vs":"VS","stats":"📊 比赛统计","goals":"⚽ 进球者","cards":"🟨 牌","subs":"🔄 换人","timeline":"📜 比赛事件","not_started":"⏳ 比赛还没开始!","loading":"✨ 加载中...","saved":"✅ 语言已保存!","choose_lang":"🌐 选择你的语言","join":"加入频道","cricket_details":"🏏 板球详情","news_title":"📰 体育新闻 + 实时比分","score":"📊 比分","read_news":"阅读全文"},
 "ja": {"welcome":"👋 ようこそ、チャンピオン！","choose":"👇 スポーツを選んでください 👇","lang_btn":"🌐 あなたの言語","news_btn":"📰 スポーツニュース + スコア","football":"⚽ サッカー","cricket":"🏏 クリケット","ipl":"🔥 IPL ライブ","lpl":"🇱🇰 LPL / スリランカ","basketball":"🏀 バスケットボール","tennis":"🎾 テニス","hockey":"🏑 ホッケー","volleyball":"🏐 バレーボール","tabletennis":"🏓 卓球","baseball":"⚾ 野球","nfl":"🏈 NFL","badminton":"🏸 バドミントン","f1":"🏎️ F1 レース","golf":"⛳ ゴルフ","ufc":"🥊 UFC / ボクシング","rugby":"🏉 ラグビー","kabaddi":"🤼 カバディ","esports":"🎮 Eスポーツ","fifa":"🏆 FIFA","live_all":"🔴 ライブ全て","results":"✅ 結果","table":"🏆 順位表","tomorrow":"📅 明日","search":"🔍 検索","back":"⬅ メニューへ","refresh":"🔄 更新","live_now":"🔴 ライブ中","full_time":"✅ 試合終了","upcoming":"🕒 予定","won":"勝ち!","draw":"🤝 引き分け","vs":"VS","stats":"📊 試合統計","goals":"⚽ 得点者","cards":"🟨 カード","subs":"🔄 交代","timeline":"📜 試合イベント","not_started":"⏳ 試合はまだ始まっていません!","loading":"✨ 読み込み中...","saved":"✅ 言語を保存しました!","choose_lang":"🌐 言語を選んでください","join":"チャンネルに参加","cricket_details":"🏏 クリケット詳細","news_title":"📰 スポーツニュース + ライブスコア","score":"📊 スコア","read_news":"全文を読む"},
 "ko": {"welcome":"👋 환영합니다, 챔피언!","choose":"👇 스포츠를 선택하세요 👇","lang_btn":"🌐 당신의 언어","news_btn":"📰 스포츠 뉴스 + 점수","football":"⚽ 축구","cricket":"🏏 크리켓","ipl":"🔥 IPL 라이브","lpl":"🇱🇰 LPL / 스리랑카","basketball":"🏀 농구","tennis":"🎾 테니스","hockey":"🏑 하키","volleyball":"🏐 배구","tabletennis":"🏓 탁구","baseball":"⚾ 야구","nfl":"🏈 NFL","badminton":"🏸 배드민턴","f1":"🏎️ F1 레이싱","golf":"⛳ 골프","ufc":"🥊 UFC / 복싱","rugby":"🏉 럭비","kabaddi":"🤼 카바디","esports":"🎮 E스포츠","fifa":"🏆 FIFA","live_all":"🔴 라이브 전체","results":"✅ 결과","table":"🏆 순위표","tomorrow":"📅 내일","search":"🔍 검색","back":"⬅ 메뉴로","refresh":"🔄 새로고침","live_now":"🔴 라이브 중","full_time":"✅ 종료","upcoming":"🕒 예정","won":"승리!","draw":"🤝 무승부","vs":"VS","stats":"📊 경기 통계","goals":"⚽ 득점자","cards":"🟨 카드","subs":"🔄 교체","timeline":"📜 경기 이벤트","not_started":"⏳ 경기가 아직 시작되지 않았습니다!","loading":"✨ 로딩 중...","saved":"✅ 언어 저장됨!","choose_lang":"🌐 언어 선택","join":"채널 가입","cricket_details":"🏏 크리켓 상세","news_title":"📰 스포츠 뉴스 + 라이브 점수","score":"📊 점수","read_news":"전체 뉴스 읽기"},
 "de": {"welcome":"👋 Willkommen, Champion!","choose":"👇 WÄHLE DEINEN SPORT 👇","lang_btn":"🌐 DEINE SPRACHE","news_btn":"📰 SPORT NEWS + PUNKTSTAND","football":"⚽ Fußball","cricket":"🏏 Cricket","ipl":"🔥 IPL LIVE","lpl":"🇱🇰 LPL / Sri Lanka","basketball":"🏀 Basketball","tennis":"🎾 Tennis","hockey":"🏑 Hockey","volleyball":"🏐 Volleyball","tabletennis":"🏓 Tischtennis","baseball":"⚾ Baseball","nfl":"🏈 NFL","badminton":"🏸 Badminton","f1":"🏎️ F1 Rennen","golf":"⛳ Golf","ufc":"🥊 UFC / Boxen","rugby":"🏉 Rugby","kabaddi":"🤼 Kabaddi","esports":"🎮 E-Sports","fifa":"🏆 FIFA","live_all":"🔴 LIVE ALLE","results":"✅ ERGEBNISSE","table":"🏆 TABELLE","tomorrow":"📅 MORGEN","search":"🔍 SUCHE","back":"⬅ Zum Menü","refresh":"🔄 Aktualisieren","live_now":"🔴 LIVE JETZT","full_time":"✅ ABPFIFF","upcoming":"🕒 DEMNÄCHST","won":"Gewonnen!","draw":"🤝 Unentschieden","vs":"VS","stats":"📊 STATISTIKEN","goals":"⚽ TORSCHÜTZEN","cards":"🟨 KARTEN","subs":"🔄 WECHSEL","timeline":"📜 EREIGNISSE","not_started":"⏳ Spiel hat noch nicht begonnen!","loading":"✨ Laden...","saved":"✅ Sprache Gespeichert!","choose_lang":"🌐 WÄHLE DEINE SPRACHE","join":"Kanal Beitreten","cricket_details":"🏏 CRICKET DETAILS","news_title":"📰 SPORT NEWS + LIVE SCORE","score":"📊 PUNKTSTAND","read_news":"Ganzen Artikel Lesen"},
 "it": {"welcome":"👋 Benvenuto, Campione!","choose":"👇 SCEGLI IL TUO SPORT 👇","lang_btn":"🌐 LA TUA LINGUA","news_btn":"📰 NOTIZIE + PUNTEGGIO","football":"⚽ Calcio","cricket":"🏏 Cricket","ipl":"🔥 IPL LIVE","lpl":"🇱🇰 LPL / Sri Lanka","basketball":"🏀 Basket","tennis":"🎾 Tennis","hockey":"🏑 Hockey","volleyball":"🏐 Pallavolo","tabletennis":"🏓 Tennis Tavolo","baseball":"⚾ Baseball","nfl":"🏈 NFL","badminton":"🏸 Badminton","f1":"🏎️ F1 Corse","golf":"⛳ Golf","ufc":"🥊 UFC / Boxe","rugby":"🏉 Rugby","kabaddi":"🤼 Kabaddi","esports":"🎮 E-Sports","fifa":"🏆 FIFA","live_all":"🔴 LIVE TUTTI","results":"✅ RISULTATI","table":"🏆 CLASSIFICA","tomorrow":"📅 DOMANI","search":"🔍 CERCA","back":"⬅ Al Menu","refresh":"🔄 Aggiorna","live_now":"🔴 LIVE ORA","full_time":"✅ FINE","upcoming":"🕒 IN ARRIVO","won":"Ha Vinto!","draw":"🤝 Pareggio","vs":"VS","stats":"📊 STATISTICHE","goals":"⚽ MARCATORI","cards":"🟨 CARTELLINI","subs":"🔄 SOSTITUZIONI","timeline":"📜 EVENTI","not_started":"⏳ La partita non è ancora iniziata!","loading":"✨ Caricamento...","saved":"✅ Lingua Salvata!","choose_lang":"🌐 SCEGLI LA TUA LINGUA","join":"Unisciti al Canale","cricket_details":"🏏 DETTAGLI CRICKET","news_title":"📰 NOTIZIE + PUNTEGGIO LIVE","score":"📊 PUNTEGGIO","read_news":"Leggi Articolo Completo"},
 "tr": {"welcome":"👋 Hoş Geldin, Şampiyon!","choose":"👇 SPORUNU SEÇ 👇","lang_btn":"🌐 DİLİN","news_btn":"📰 SPOR HABERLERİ + SKOR","football":"⚽ Futbol","cricket":"🏏 Kriket","ipl":"🔥 IPL CANLI","lpl":"🇱🇰 LPL / Sri Lanka","basketball":"🏀 Basketbol","tennis":"🎾 Tenis","hockey":"🏑 Hokey","volleyball":"🏐 Voleybol","tabletennis":"🏓 Masa Tenisi","baseball":"⚾ Beyzbol","nfl":"🏈 NFL","badminton":"🏸 Badminton","f1":"🏎️ F1 Yarışı","golf":"⛳ Golf","ufc":"🥊 UFC / Boks","rugby":"🏉 Rugby","kabaddi":"🤼 Kabaddi","esports":"🎮 E-Spor","fifa":"🏆 FIFA","live_all":"🔴 CANLI TÜMÜ","results":"✅ SONUÇLAR","table":"🏆 PUAN DURUMU","tomorrow":"📅 YARIN","search":"🔍 ARA","back":"⬅ Menüye","refresh":"🔄 Yenile","live_now":"🔴 CANLI ŞİMDİ","full_time":"✅ BİTTİ","upcoming":"🕒 YAKLAŞAN","won":"Kazandı!","draw":"🤝 Berabere","vs":"VS","stats":"📊 MAÇ İSTATİSTİĞİ","goals":"⚽ GOLCÜLER","cards":"🟨 KARTLAR","subs":"🔄 DEĞİŞİKLİKLER","timeline":"📜 MAÇ OLAYLARI","not_started":"⏳ Maç henüz başlamadı!","loading":"✨ Yükleniyor...","saved":"✅ Dil Kaydedildi!","choose_lang":"🌐 DİLİNİ SEÇ","join":"Kanala Katıl","cricket_details":"🏏 KRİKET DETAYLARI","news_title":"📰 SPOR HABERLERİ + CANLI SKOR","score":"📊 SKOR","read_news":"Haberi Oku"},
 "fa": {"welcome":"👋 خوش آمدید، قهرمان!","choose":"👇 ورزش خود را انتخاب کنید 👇","lang_btn":"🌐 زبان شما","news_btn":"📰 اخبار ورزشی + امتیاز","football":"⚽ فوتبال","cricket":"🏏 کریکت","ipl":"🔥 IPL زنده","lpl":"🇱🇰 LPL / سریلانکا","basketball":"🏀 بسکتبال","tennis":"🎾 تنیس","hockey":"🏑 هاکی","volleyball":"🏐 والیبال","tabletennis":"🏓 تنیس روی میز","baseball":"⚾ بیسبال","nfl":"🏈 NFL","badminton":"🏸 بدمینتون","f1":"🏎️ مسابقات F1","golf":"⛳ گلف","ufc":"🥊 UFC / بوکس","rugby":"🏉 راگبی","kabaddi":"🤼 کبدی","esports":"🎮 ورزش الکترونیک","fifa":"🏆 FIFA","live_all":"🔴 زنده همه","results":"✅ نتایج","table":"🏆 جدول امتیاز","tomorrow":"📅 فردا","search":"🔍 جستجو","back":"⬅ به منو","refresh":"🔄 تازه کردن","live_now":"🔴 زنده اکنون","full_time":"✅ پایان","upcoming":"🕒 آینده","won":"برد!","draw":"🤝 مساوی","vs":"VS","stats":"📊 آمار مسابقه","goals":"⚽ گلزنان","cards":"🟨 کارت‌ها","subs":"🔄 تعویض‌ها","timeline":"📜 رویدادهای مسابقه","not_started":"⏳ مسابقه هنوز شروع نشده!","loading":"✨ در حال بارگذاری...","saved":"✅ زبان ذخیره شد!","choose_lang":"🌐 زبان خود را انتخاب کنید","join":"عضویت در کانال","cricket_details":"🏏 جزئیات کریکت","news_title":"📰 اخبار ورزشی + امتیاز زنده","score":"📊 امتیاز","read_news":"خواندن خبر کامل"},
 "ms": {"welcome":"👋 Selamat Datang, Juara!","choose":"👇 PILIH SUKAN ANDA 👇","lang_btn":"🌐 BAHASA ANDA","news_btn":"📰 BERITA SUKAN + SKOR","football":"⚽ Bola Sepak","cricket":"🏏 Kriket","ipl":"🔥 IPL LANGSUNG","lpl":"🇱🇰 LPL / Sri Lanka","basketball":"🏀 Bola Keranjang","tennis":"🎾 Tenis","hockey":"🏑 Hoki","volleyball":"🏐 Bola Tampar","tabletennis":"🏓 Ping Pong","baseball":"⚾ Besbol","nfl":"🏈 NFL","badminton":"🏸 Badminton","f1":"🏎️ F1 Lumba","golf":"⛳ Golf","ufc":"🥊 UFC / Tinju","rugby":"🏉 Ragbi","kabaddi":"🤼 Kabaddi","esports":"🎮 E-Sukan","fifa":"🏆 FIFA","live_all":"🔴 LANGSUNG SEMUA","results":"✅ KEPUTUSAN","table":"🏆 JADUAL MATA","tomorrow":"📅 ESOK","search":"🔍 CARI","back":"⬅ Ke Menu","refresh":"🔄 Muat Semula","live_now":"🔴 LANGSUNG SEKARANG","full_time":"✅ TAMAT","upcoming":"🕒 AKAN DATANG","won":"Menang!","draw":"🤝 Seri","vs":"VS","stats":"📊 STATISTIK","goals":"⚽ PENJARING GOL","cards":"🟨 KAD","subs":"🔄 PERTUKARAN","timeline":"📜 PERISTIWA","not_started":"⏳ Perlawanan belum bermula!","loading":"✨ Memuatkan...","saved":"✅ Bahasa Disimpan!","choose_lang":"🌐 PILIH BAHASA ANDA","join":"Sertai Saluran","cricket_details":"🏏 BUTIRAN KRIKET","news_title":"📰 BERITA SUKAN + SKOR LANGSUNG","score":"📊 SKOR","read_news":"Baca Berita Penuh"},
 "id": {"welcome":"👋 Selamat Datang, Juara!","choose":"👇 PILIH OLAHRAGA ANDA 👇","lang_btn":"🌐 BAHASA ANDA","news_btn":"📰 BERITA OLAHRAGA + SKOR","football":"⚽ Sepak Bola","cricket":"🏏 Kriket","ipl":"🔥 IPL LANGSUNG","lpl":"🇱🇰 LPL / Sri Lanka","basketball":"🏀 Basket","tennis":"🎾 Tenis","hockey":"🏑 Hoki","volleyball":"🏐 Voli","tabletennis":"🏓 Tenis Meja","baseball":"⚾ Bisbol","nfl":"🏈 NFL","badminton":"🏸 Bulu Tangkis","f1":"🏎️ F1 Balap","golf":"⛳ Golf","ufc":"🥊 UFC / Tinju","rugby":"🏉 Rugby","kabaddi":"🤼 Kabaddi","esports":"🎮 E-Sports","fifa":"🏆 FIFA","live_all":"🔴 LANGSUNG SEMUA","results":"✅ HASIL","table":"🏆 KLASEMEN","tomorrow":"📅 BESOK","search":"🔍 CARI","back":"⬅ Ke Menu","refresh":"🔄 Muat Ulang","live_now":"🔴 LANGSUNG SEKARANG","full_time":"✅ SELESAI","upcoming":"🕒 MENDATANG","won":"Menang!","draw":"🤝 Seri","vs":"VS","stats":"📊 STATISTIK","goals":"⚽ PENCETAK GOL","cards":"🟨 KARTU","subs":"🔄 PERGANTIAN","timeline":"📜 PERISTIWA","not_started":"⏳ Pertandingan belum dimulai!","loading":"✨ Memuat...","saved":"✅ Bahasa Disimpan!","choose_lang":"🌐 PILIH BAHASA ANDA","join":"Gabung Saluran","cricket_details":"🏏 DETAIL KRIKET","news_title":"📰 BERITA OLAHRAGA + SKOR LANGSUNG","score":"📊 SKOR","read_news":"Baca Berita Lengkap"},
 "th": {"welcome":"👋 ยินดีต้อนรับ แชมป์เปี้ยน!","choose":"👇 เลือกกีฬาของคุณ 👇","lang_btn":"🌐 ภาษาของคุณ","news_btn":"📰 ข่าวกีฬา + คะแนน","football":"⚽ ฟุตบอล","cricket":"🏏 คริกเก็ต","ipl":"🔥 IPL สด","lpl":"🇱🇰 LPL / ศรีลังกา","basketball":"🏀 บาสเกตบอล","tennis":"🎾 เทนนิส","hockey":"🏑 ฮอกกี้","volleyball":"🏐 วอลเลย์บอล","tabletennis":"🏓 ปิงปอง","baseball":"⚾ เบสบอล","nfl":"🏈 NFL","badminton":"🏸 แบดมินตัน","f1":"🏎️ F1 แข่งรถ","golf":"⛳ กอล์ฟ","ufc":"🥊 UFC / มวย","rugby":"🏉 รักบี้","kabaddi":"🤼 กาบัดดี้","esports":"🎮 อีสปอร์ต","fifa":"🏆 FIFA","live_all":"🔴 สดทั้งหมด","results":"✅ ผลลัพธ์","table":"🏆 ตารางคะแนน","tomorrow":"📅 พรุ่งนี้","search":"🔍 ค้นหา","back":"⬅ กลับเมนู","refresh":"🔄 รีเฟรช","live_now":"🔴 สดตอนนี้","full_time":"✅ จบเกม","upcoming":"🕒 กำลังจะมา","won":"ชนะ!","draw":"🤝 เสมอ","vs":"VS","stats":"📊 สถิติการแข่งขัน","goals":"⚽ ผู้ทำประตู","cards":"🟨 ใบ","subs":"🔄 ตัวสำรอง","timeline":"📜 เหตุการณ์","not_started":"⏳ การแข่งขันยังไม่เริ่ม!","loading":"✨ กำลังโหลด...","saved":"✅ บันทึกภาษาแล้ว!","choose_lang":"🌐 เลือกภาษาของคุณ","join":"เข้าร่วมช่อง","cricket_details":"🏏 รายละเอียดคริกเก็ต","news_title":"📰 ข่าวกีฬา + คะแนนสด","score":"📊 คะแนน","read_news":"อ่านข่าวเต็ม"},
 "vi": {"welcome":"👋 Chào mừng, Nhà vô địch!","choose":"👇 CHỌN MÔN THỂ THAO CỦA BẠN 👇","lang_btn":"🌐 NGÔN NGỮ CỦA BẠN","news_btn":"📰 TIN THỂ THAO + ĐIỂM","football":"⚽ Bóng Đá","cricket":"🏏 Cricket","ipl":"🔥 IPL TRỰC TIẾP","lpl":"🇱🇰 LPL / Sri Lanka","basketball":"🏀 Bóng Rổ","tennis":"🎾 Tennis","hockey":"🏑 Khúc Côn Cầu","volleyball":"🏐 Bóng Chuyền","tabletennis":"🏓 Bóng Bàn","baseball":"⚾ Bóng Chày","nfl":"🏈 NFL","badminton":"🏸 Cầu Lông","f1":"🏎️ Đua F1","golf":"⛳ Golf","ufc":"🥊 UFC / Quyền Anh","rugby":"🏉 Rugby","kabaddi":"🤼 Kabaddi","esports":"🎮 E-Sports","fifa":"🏆 FIFA","live_all":"🔴 TRỰC TIẾP TẤT CẢ","results":"✅ KẾT QUẢ","table":"🏆 BẢNG ĐIỂM","tomorrow":"📅 NGÀY MAI","search":"🔍 TÌM KIẾM","back":"⬅ Về Menu","refresh":"🔄 Làm Mới","live_now":"🔴 TRỰC TIẾP","full_time":"✅ HẾT GIỜ","upcoming":"🕒 SẮP TỚI","won":"Thắng!","draw":"🤝 Hòa","vs":"VS","stats":"📊 THỐNG KÊ","goals":"⚽ NGƯỜI GHI BÀN","cards":"🟨 THẺ","subs":"🔄 THAY NGƯỜI","timeline":"📜 SỰ KIỆN","not_started":"⏳ Trận đấu chưa bắt đầu!","loading":"✨ Đang tải...","saved":"✅ Đã Lưu Ngôn Ngữ!","choose_lang":"🌐 CHỌN NGÔN NGỮ CỦA BẠN","join":"Tham Gia Kênh","cricket_details":"🏏 CHI TIẾT CRICKET","news_title":"📰 TIN THỂ THAO + ĐIỂM TRỰC TIẾP","score":"📊 ĐIỂM","read_news":"Đọc Tin Đầy Đủ"},
 "ne": {"welcome":"👋 नमस्ते, च्याम्पियन!","choose":"👇 आफ्नो खेल छान्नुहोस् 👇","lang_btn":"🌐 तपाईंको भाषा","news_btn":"📰 खेल समाचार + स्कोर","football":"⚽ फुटबल","cricket":"🏏 क्रिकेट","ipl":"🔥 IPL लाइभ","lpl":"🇱🇰 LPL / श्रीलंका","basketball":"🏀 बास्केटबल","tennis":"🎾 टेनिस","hockey":"🏑 हकी","volleyball":"🏐 भलिबल","tabletennis":"🏓 टेबल टेनिस","baseball":"⚾ बेसबल","nfl":"🏈 NFL","badminton":"🏸 ब्याडमिन्टन","f1":"🏎️ F1 रेसिङ","golf":"⛳ गल्फ","ufc":"🥊 UFC / बक्सिङ","rugby":"🏉 रग्बी","kabaddi":"🤼 कबड्डी","esports":"🎮 ई-स्पोर्ट्स","fifa":"🏆 FIFA","live_all":"🔴 लाइभ सबै","results":"✅ नतिजा","table":"🏆 अंक तालिका","tomorrow":"📅 भोलि","search":"🔍 खोज्नुहोस्","back":"⬅ मेनुमा","refresh":"🔄 रिफ्रेस","live_now":"🔴 लाइभ अहिले","full_time":"✅ सकियो","upcoming":"🕒 आउँदै","won":"जित्यो!","draw":"🤝 बराबरी","vs":"VS","stats":"📊 खेल तथ्यांक","goals":"⚽ गोल गर्ने","cards":"🟨 कार्ड","subs":"🔄 परिवर्तन","timeline":"📜 खेल घटना","not_started":"⏳ खेल अझै सुरु भएको छैन!","loading":"✨ लोड हुँदैछ...","saved":"✅ भाषा सेभ भयो!","choose_lang":"🌐 आफ्नो भाषा छान्नुहोस्","join":"च्यानल जोइन गर्नुहोस्","cricket_details":"🏏 क्रिकेट विवरण","news_title":"📰 खेल समाचार + लाइभ स्कोर","score":"📊 स्कोर","read_news":"पुरा समाचार पढ्नुहोस्"},
}
LANG_NAMES = {"si":"සිංහල","ta":"தமிழ்","en":"English","hi":"हिन्दी","ur":"اردو","bn":"বাংলা","ar":"العربية","es":"Español","fr":"Français","pt":"Português","ru":"Русский","zh":"中文","ja":"日本語","ko":"한국어","de":"Deutsch","it":"Italiano","tr":"Türkçe","fa":"فارسی","ms":"Melayu","id":"Indonesia","th":"ไทย","vi":"Tiếng Việt","ne":"नेपाली"}
LANG_FLAGS = {"si":"🇱🇰","ta":"🇮🇳","en":"🇬🇧","hi":"🇮🇳","ur":"🇵🇰","bn":"🇧🇩","ar":"🇸🇦","es":"🇪🇸","fr":"🇫🇷","pt":"🇵🇹","ru":"🇷🇺","zh":"🇨🇳","ja":"🇯🇵","ko":"🇰🇷","de":"🇩🇪","it":"🇮🇹","tr":"🇹🇷","fa":"🇮🇷","ms":"🇲🇾","id":"🇮🇩","th":"🇹🇭","vi":"🇻🇳","ne":"🇳🇵"}
def tr(chat_id, key):
    lang = USER_LANG.get(str(chat_id), "en")
    d = T.get(lang, T["en"])
    return d.get(key, T["en"].get(key, key))

def bar(v1, v2, label):
    try:
        a=float(str(v1).replace('%','')); b=float(str(v2).replace('%','')); tot=a+b
        if tot==0: return f"{label}\n{a} - {b}\n"
        p=int((a/tot)*12); q=12-p
        return f"{label}\n{'🟦'*p}{'⬜'*q} {a:.0f}% - {b:.0f}%\n"
    except: return f"{label}: {v1} - {v2}\n"
def progress_bar(m):
    try:
        mm=int(str(m).replace("'","").split("+")[0]); p=min(int(mm/90*10),10)
        return f"{'🟩'*p}{'⬜'*(10-p)} {mm}'"
    except: return ""
def fetch_board(sport, league):
    try:
        url=f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
        return requests.get(url, timeout=12).json().get('events', [])
    except: return []
def fetch_summary(sport, league, eid):
    try:
        url=f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/summary?event={eid}"
        return requests.get(url, timeout=12).json()
    except: return None
def fetch_standings(sport, league):
    try:
        url=f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/standings"
        return requests.get(url, timeout=12).json()
    except: return None

ALL_SCORES_CACHE=[]
def fetch_news():
    news=[]
    try:
        r=requests.get("https://site.api.espn.com/apis/site/v2/sports/cricket/news?limit=10", timeout=10).json()
        for a in r.get('articles', [])[:5]: news.append({"title":a.get('headline',''),"desc":a.get('description','')[:150],"source":"ESPN Cricket","link":a.get('links',{}).get('web',{}).get('href','')})
    except: pass
    try:
        r=requests.get("https://site.api.espn.com/apis/site/v2/sports/soccer/news?limit=10", timeout=10).json()
        for a in r.get('articles', [])[:5]: news.append({"title":a.get('headline',''),"desc":a.get('description','')[:150],"source":"ESPN Football","link":a.get('links',{}).get('web',{}).get('href','')})
    except: pass
    rss_urls=["https://news.google.com/rss/search?q=cricket+live+score&hl=en-IN&gl=IN&ceid=IN:en","https://news.google.com/rss/search?q=U19+Asia+Cup+cricket&hl=en-IN&gl=IN&ceid=IN:en","https://news.google.com/rss/search?q=football+live+score&hl=en-IN&gl=IN&ceid=IN:en","https://news.google.com/rss/search?q=IPL+cricket&hl=en-IN&gl=IN&ceid=IN:en"]
    for url in rss_urls:
        try:
            r=requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
            root=ET.fromstring(r.content)
            for item in root.findall(".//item")[:4]:
                news.append({"title":item.findtext("title",""),"desc":"","source":"Google News","link":item.findtext("link","")})
        except: pass
    seen=set(); uniq=[]
    for n in news:
        if n["title"] not in seen: seen.add(n["title"]); uniq.append(n)
    return uniq[:12]
def find_score_for_news(title):
    tl=title.lower()
    for s in ALL_SCORES_CACHE:
        sl=s.lower()
        for w in ["india","pakistan","sri lanka","australia","england","bangladesh","new zealand","south africa","afghanistan","nepal","west indies"]:
            if w in tl and w in sl:
                lines=s.split("\n"); short="\n".join([l for l in lines if "┃" in l or "Won" in l or "Draw" in l][:4]); return short
    return ""

def get_lang_keyboard():
    btns=[]; codes=list(LANG_NAMES.keys())
    for i in range(0, len(codes), 2):
        row=[]
        for c in codes[i:i+2]: row.append(InlineKeyboardButton(f"{LANG_FLAGS.get(c,'🌐')} {LANG_NAMES[c]}", callback_data=f"lang_{c}"))
        btns.append(row)
    btns.append([InlineKeyboardButton("⬅ Back", callback_data="menu_start")])
    return InlineKeyboardMarkup(btns)
def get_main_keyboard(chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(chat_id,"lang_btn"), callback_data="menu_lang")],
        [InlineKeyboardButton(tr(chat_id,"news_btn"), callback_data="menu_news")],
        [InlineKeyboardButton(tr(chat_id,"football"), callback_data="menu_football"), InlineKeyboardButton(tr(chat_id,"cricket"), callback_data="menu_cricket")],
        [InlineKeyboardButton(tr(chat_id,"ipl"), callback_data="menu_ipl"), InlineKeyboardButton(tr(chat_id,"lpl"), callback_data="menu_lpl")],
        [InlineKeyboardButton(tr(chat_id,"basketball"), callback_data="menu_basketball"), InlineKeyboardButton(tr(chat_id,"tennis"), callback_data="menu_tennis")],
        [InlineKeyboardButton(tr(chat_id,"hockey"), callback_data="menu_hockey"), InlineKeyboardButton(tr(chat_id,"volleyball"), callback_data="menu_volleyball")],
        [InlineKeyboardButton(tr(chat_id,"tabletennis"), callback_data="menu_tabletennis"), InlineKeyboardButton(tr(chat_id,"baseball"), callback_data="menu_baseball")],
        [InlineKeyboardButton(tr(chat_id,"nfl"), callback_data="menu_nfl"), InlineKeyboardButton(tr(chat_id,"badminton"), callback_data="menu_badminton")],
        [InlineKeyboardButton(tr(chat_id,"f1"), callback_data="menu_f1"), InlineKeyboardButton(tr(chat_id,"golf"), callback_data="menu_golf")],
        [InlineKeyboardButton(tr(chat_id,"ufc"), callback_data="menu_ufc"), InlineKeyboardButton(tr(chat_id,"rugby"), callback_data="menu_rugby")],
        [InlineKeyboardButton(tr(chat_id,"kabaddi"), callback_data="menu_kabaddi"), InlineKeyboardButton(tr(chat_id,"esports"), callback_data="menu_esports")],
        [InlineKeyboardButton(tr(chat_id,"fifa"), callback_data="menu_fifa"), InlineKeyboardButton(tr(chat_id,"live_all"), callback_data="menu_live")],
        [InlineKeyboardButton(tr(chat_id,"results"), callback_data="menu_results"), InlineKeyboardButton(tr(chat_id,"table"), callback_data="menu_table")],
        [InlineKeyboardButton(tr(chat_id,"tomorrow"), callback_data="menu_tomorrow"), InlineKeyboardButton(tr(chat_id,"search"), callback_data="menu_search")],
        [InlineKeyboardButton(tr(chat_id,"join"), url="https://t.me/bigolive_asia")]
    ])
def get_back_keyboard(chat_id, key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tr(chat_id,"refresh"), callback_data=f"menu_{key}")],
        [InlineKeyboardButton(tr(chat_id,"back"), callback_data="menu_start")],
        [InlineKeyboardButton(tr(chat_id,"join"), url="https://t.me/bigolive_asia")]
    ])

# ========== FIXED FORMAT - Tennis / Golf / F1 Error Fix ==========
def format_premium(ev, sport, league, chat_id="0"):
    try:
        # FIX 1: competitions නැති Sports - Tennis, Golf, F1, Racing
        if 'competitions' not in ev:
            name = ev.get('name', f'{sport.upper()} Match')
            short = ev.get('status', {}).get('type', {}).get('shortDetail', '')
            detail = ev.get('status', {}).get('type', {}).get('detail', '')
            state = ev.get('status', {}).get('type', {}).get('state', '')
            emoji = {"tennis":"🎾","golf":"⛳","racing":"🏎️","f1":"🏎️"}.get(sport, "🏆")
            title_map = {"tennis":"TENNIS • PREMIUM LIVE","golf":"GOLF • PREMIUM LIVE","racing":"F1 • PREMIUM LIVE"}
            title = title_map.get(sport, f"{sport.upper()} • PREMIUM LIVE")
            t = f"{emoji} <b>{title}</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            if state == 'in': t += f"🔴 <b>{tr(chat_id,'live_now')}</b> • {short}\n\n"
            elif state == 'post': t += f"✅ <b>{tr(chat_id,'full_time')}</b> • {detail}\n\n"
            else: t += f"🕒 <b>{tr(chat_id,'upcoming')}</b> • {short}\n\n"
            t += f"🏆 <b>{name}</b>\n📍 {detail}\n\n"
            if sport == "golf":
                t += "🏌️ <b>LEADERBOARD</b>\n──────────────────────\n📊 Top Players Updating Live...\n🏆 Tournament in Progress\n\n"
            if sport == "tennis":
                # Tennis එකේ competitors වෙන තැනක තියෙනවා නම් ගන්නවා
                try:
                    comps = ev.get('competitions', [])
                    if comps:
                        pass
                except: pass
            t += "━━━━━━━━━━━━━━━━━━━━━━\n💬 @bigolive_asia\n"
            return t
        comp = ev['competitions'][0]
        # FIX 2: competitors නැත්නම් Error නොදී Return කරනවා
        competitors = comp.get('competitors', [])
        if not competitors or len(competitors) < 1:
            name = ev.get('name', f'{sport.upper()} Match')
            return f"🏆 <b>{name}</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n📍 Score Updating...\n💬 @bigolive_asia\n"
        state = ev.get('status', {}).get('type', {}).get('state')
        short = ev.get('status', {}).get('type', {}).get('shortDetail','')
        detail = ev.get('status', {}).get('type', {}).get('detail','')
        eid = ev.get('id')
        venue = comp.get('venue', {}).get('fullName','Unknown Stadium') if comp.get('venue') else 'Unknown Stadium'
        city = comp.get('venue', {}).get('address', {}).get('city','') if comp.get('venue') else ''
        comp_name = ev.get('season', {}).get('slug','').replace('-',' ').upper() if ev.get('season') else league.upper()
        league_emoji = {"ENG.1":"🏴󐁧󐁢󐁥󐁮󐁧󐁿","ESP.1":"🇪🇸","GER.1":"🇩🇪","ITA.1":"🇮🇹","FRA.1":"🇫🇷","UEFA.CHAMPIONS":"⭐","NBA":"🏀","ATP":"🎾","WTA":"🎾","MLB":"⚾","NFL":"🏈","BWF":"🏸","F1":"🏎️","PGA":"⛳","MMA":"🥊","RUGBY":"🏉"}.get(league.upper(),"🏆")
        h = competitors[0]; a = competitors[1] if len(competitors)>1 else None
        h_name = h['team'].get('displayName','') if h.get('team') else h.get('athlete',{}).get('displayName','')
        a_name = a['team'].get('displayName','') if a and a.get('team') else (a.get('athlete',{}).get('displayName','') if a else "")
        h_short = h['team'].get('abbreviation','') if h.get('team') else h_name[:3].upper()
        a_short = a['team'].get('abbreviation','') if a and a.get('team') else a_name[:3].upper()
        h_score = h.get('score','0'); a_score = a.get('score','0') if a else "0"
        h_lines = h.get('linescores', []); a_lines = a.get('linescores', []) if a else []
        h_line_txt = " | ".join([str(x.get('value','')) for x in h_lines]) if h_lines else ""
        a_line_txt = " | ".join([str(x.get('value','')) for x in a_lines]) if a_lines else ""
        winner = ""
        if state == 'post':
            try:
                if float(h_score) > float(a_score): winner = f"👑 {h_name} {tr(chat_id,'won')}"
                elif float(a_score) > float(h_score): winner = f"👑 {a_name} {tr(chat_id,'won')}"
                else: winner = tr(chat_id,'draw')
            except: winner = tr(chat_id,'full_time')
        t = ""
        t += "╔══════════════════════╗\n"
        if state == 'in': t += f"║  {tr(chat_id,'live_now')}  •  {short}  ║\n"
        elif state == 'post': t += f"║  {tr(chat_id,'full_time')}  •  {detail}  ║\n"
        else: t += f"║  {tr(chat_id,'upcoming')}  •  {short}  ║\n"
        t += "╚══════════════════════╝\n\n"
        t += f"{league_emoji} <b>{comp_name}</b>\n🏟️ {venue} {city}\n"
        if state == 'in' and sport == "soccer": t += f"⏱️ {progress_bar(short)}\n"
        t += "\n┏━━━━━━━━━━━━━━━━━━━━┓\n"
        if state == 'pre': t += f"┃  <b>{h_name}</b>\n┃         <b>{tr(chat_id,'vs')}</b>\n┃  <b>{a_name}</b>\n"
        else:
            t += f"┃  <b>{h_name}</b>  [{h_short}]\n┃      <b> {h_score}  -  {a_score} </b>\n┃  <b>{a_name}</b>  [{a_short}]\n"
            if h_line_txt: t += f"┃  {h_short}: {h_line_txt}\n"
            if a_line_txt: t += f"┃  {a_short}: {a_line_txt}\n"
        t += "┗━━━━━━━━━━━━━━━━━━━━┛\n"
        if winner: t += f"\n{winner}\n"
        if state == 'pre': t += f"\n<i>{tr(chat_id,'not_started')}</i>\n━━━━━━━━━━━━━━━━━━━━━━\n"; return t
        if sport == "cricket":
            t += f"\n{tr(chat_id,'cricket_details')}\n──────────────────────\n📍 {detail}\n📊 {h_name}: {h_score}\n📊 {a_name}: {a_score}\n\n━━━━━━━━━━━━━━━━━━━━━━\n💬 @bigolive_asia\n"; return t
        dj = fetch_summary(sport, league, eid)
        goals, cards, subs, timeline = [], [], [], []; stats = {}
        if dj:
            try:
                for d in dj.get('details', []):
                    txt = d.get('type', {}).get('text',''); team = d.get('team', {}).get('shortDisplayName','')
                    ath = d['athletesInvolved'][0].get('displayName','') if d.get('athletesInvolved') else ''
                    clock = d.get('clock', {}).get('displayValue',''); tl = txt.lower()
                    if 'goal' in tl or 'penalty - scored' in tl:
                        is_pen = 'penalty' in tl; goals.append((clock, ath, team, is_pen)); timeline.append(f"  {clock}'  ⚽ {ath} ({team}){' [PEN]' if is_pen else ''}")
                    elif 'yellow' in tl: cards.append(f"  {clock}'  🟨 {ath} ({team})"); timeline.append(f"  {clock}'  🟨 {ath}")
                    elif 'red' in tl: cards.append(f"  {clock}'  🟥 {ath} ({team})"); timeline.append(f"  {clock}'  🟥 {ath}")
                    elif 'substitution' in tl: subs.append(f"  {clock}'  🔄 {ath} ({team})")
            except: pass
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
            t += f"\n{tr(chat_id,'timeline')}\n──────────────────────\n"
            for line in timeline: t += f"{line}\n"
        if goals:
            t += f"\n{tr(chat_id,'goals')}\n──────────────────────\n"
            for clock, ath, team, is_pen in goals:
                pen = " 🎯 PENALTY" if is_pen else ""; t += f"  ⏰ {clock}'  <b>{ath}</b>\n       └ {team}{pen}\n"
        if cards:
            t += f"\n{tr(chat_id,'cards')}\n──────────────────────\n"
            for c in cards: t += f"{c}\n"
        if subs:
            t += f"\n{tr(chat_id,'subs')}\n──────────────────────\n"
            for s in subs[:5]: t += f"{s}\n"
        if stats:
            t += f"\n{tr(chat_id,'stats')}\n──────────────────────\n"
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
        t += "\n━━━━━━━━━━━━━━━━━━━━━━\n💬 @bigolive_asia\n"
        return t
    except Exception as e:
        # FIX 3: Error කියලා පෙන්නන්නේ නෑ, ලස්සන Message එකක් පෙන්නනවා
        emoji = {"tennis":"🎾","golf":"⛳","racing":"🏎️","f1":"🏎️"}.get(sport, "🏆")
        return f"{emoji} <b>{sport.upper()} MATCH</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n🏆 {ev.get('name','Match')}\n📍 Score Updating...\n━━━━━━━━━━━━━━━━━━━━━━\n💬 @bigolive_asia\n"

SPORT_CONFIG = {
    "football": ("⚽ FOOTBALL", [("soccer","eng.1"),("soccer","esp.1"),("soccer","ger.1"),("soccer","ita.1"),("soccer","fra.1"),("soccer","uefa.champions")]),
    "cricket": ("🏏 CRICKET", [("cricket","")]),
    "ipl": ("🔥 IPL", [("cricket","")]),
    "lpl": ("🇱🇰 LPL / SRI LANKA", [("cricket","")]),
    "basketball": ("🏀 BASKETBALL", [("basketball","nba")]),
    "tennis": ("🎾 TENNIS", [("tennis","atp"),("tennis","wta")]),
    "hockey": ("🏑 HOCKEY", [("field-hockey","fih")]),
    "volleyball": ("🏐 VOLLEYBALL", [("volleyball","fivb")]),
    "tabletennis": ("🏓 TABLE TENNIS", [("table-tennis","ittf")]),
    "baseball": ("⚾ BASEBALL", [("baseball","mlb")]),
    "nfl": ("🏈 NFL", [("football","nfl")]),
    "badminton": ("🏸 BADMINTON", [("badminton","bwf")]),
    "fifa": ("🏆 FIFA", [("soccer","fifa.world"),("soccer","fifa.friendly")]),
    "f1": ("🏎️ F1", [("racing","f1")]),
    "golf": ("⛳ GOLF", [("golf","pga")]),
    "ufc": ("🥊 UFC", [("mma","mma"),("boxing","boxing")]),
    "rugby": ("🏉 RUGBY", [("rugby","rugby")]),
    "kabaddi": ("🤼 KABADDI", [("cricket","")]),
    "esports": ("🎮 E-SPORTS", [("soccer","eng.1")]),
}

def get_data(key, chat_id="0"):
    global ALL_SCORES_CACHE
    title, leagues = SPORT_CONFIG[key]
    live, up, res = [], [], []
    for sport, league in leagues:
        if sport == "cricket":
            events = []
            # FIX: Cricket Limit 100 - U19, Asia Cup ඔක්කොම එනවා
            for u in ["https://site.api.espn.com/apis/site/v2/sports/cricket/scoreboard","https://site.api.espn.com/apis/site/v2/sports/cricket/scoreboard?limit=100"]:
                try:
                    r = requests.get(u, headers={"User-Agent":"Mozilla/5.0"}, timeout=12).json()
                    events += r.get('events', [])
                except: pass
            seen=set(); uniq=[]
            for ev in events:
                if ev.get('id') not in seen: seen.add(ev.get('id')); uniq.append(ev)
            events = uniq
            for ev in events:
                try:
                    name = (ev.get('name','') + " " + ev.get('shortName','')).lower()
                    if key == "ipl" and "ipl" not in name and "indian premier" not in name: continue
                    if key == "lpl" and "lanka" not in name and "sri lanka" not in name and "lpl" not in name: continue
                    if key == "kabaddi": continue
                    state = ev.get('status',{}).get('type',{}).get('state')
                    txt = format_premium(ev, "cricket", "", chat_id)
                    if "Error" in txt: continue
                    if state=='in': live.append(txt)
                    elif state=='pre': up.append(txt)
                    elif state=='post': res.append(txt)
                except: continue
            continue
        # අනිත් Sports - Error ආවොත් Skip කරනවා
        try:
            events = fetch_board(sport, league)
            for ev in events:
                try:
                    state = ev.get('status',{}).get('type',{}).get('state')
                    txt = format_premium(ev, sport, league, chat_id)
                    if "Error" in txt: continue
                    if state=='in': live.append(txt)
                    elif state=='pre': up.append(txt)
                    elif state=='post': res.append(txt)
                except: continue
        except: continue
    if key == "kabaddi": live = ["🤼 <b>PRO KABADDI LEAGUE</b>\n\n📍 Live Score Coming Soon\n🏆 Season Starts Soon - Stay Tuned!\n━━━━━━━━━━━━━━━━━━━━━━\n"]
    if key == "esports": live = ["🎮 <b>E-SPORTS LIVE</b>\n\n🔥 PUBG Mobile - PMPL\n🔥 Free Fire - FFWS\n🔥 Valorant Champions\n\n📍 Live Scores Update Soon\n━━━━━━━━━━━━━━━━━━━━━━\n"]
    # Tennis / Golf Data නැත්නම් ලස්සන Message එකක්
    if key in ["tennis","golf","f1"] and not live and not res and not up:
        em = {"tennis":"🎾","golf":"⛳","f1":"🏎️"}[key]
        live = [f"{em} <b>{key.upper()} LIVE</b>\n\n📍 <i>Live Scores Updating...\nPlease Click Refresh</i>\n━━━━━━━━━━━━━━━━━━━━━━\n💬 @bigolive_asia\n"]
    ALL_SCORES_CACHE.extend(live + res)
    ALL_SCORES_CACHE = ALL_SCORES_CACHE[-100:]
    return title, live, up, res

def format_full(key, chat_id):
    title, live, up, res = get_data(key, chat_id)
    t = f"✨ <b>{title}  •  PREMIUM LIVE</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    t += f"{tr(chat_id,'live_now')}\n\n"; t += "".join(live[:2]) if live else "😴 No Live Match Right Now\n━━━━━━━━━━━━━━━━━━━━━━\n"
    t += f"\n{tr(chat_id,'results')}\n\n"; t += "".join(res[:3]) if res else "No Results Yet\n━━━━━━━━━━━━━━━━━━━━━━\n"
    t += f"\n{tr(chat_id,'upcoming')}\n\n"; t += "".join(up[:3]) if up else "No Upcoming\n━━━━━━━━━━━━━━━━━━━━━━\n"
    return t
def format_news(chat_id):
    for k in ["cricket","football"]: get_data(k, chat_id)
    news = fetch_news()
    t = f"{tr(chat_id,'news_title')}\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for n in news:
        score = find_score_for_news(n["title"])
        t += f"📰 <b>{n['title']}</b>\n"
        if n["desc"]: t += f"{n['desc']}\n"
        if score: t += f"\n{tr(chat_id,'score')}:\n{score}\n"
        t += f"🔗 <a href=\"{n['link']}\">{tr(chat_id,'read_news')}</a>  •  {n['source']}\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    t += "⚡ @bigolive_asia"
    return t[:4000]
def get_welcome(chat_id):
    return ("╔══════════════════════╗\n║  ✨ 🏆 PREMIUM SPORTS 🏆 ✨  ║\n╚══════════════════════╝\n\n    ⚽  🏏  🏀  🎾  🏈  ⚾\n  <b>YADANAR LIVE SPORTS</b>\n  <b>PREMIUM SPORTS</b>\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
    f"{tr(chat_id,'welcome')}\n━━━━━━━━━━━━━━━━━━━━━━\n\n🔴 <b>LIVE SCORES</b>  •  Every 3 Minutes\n⚽ <b>GOAL ALERTS</b>  •  Instant Update\n📰 <b>NEWS + SCORE</b>\n🏆 <b>IPL • LPL • EPL • FIFA</b>\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
    f"{tr(chat_id,'choose')}\n━━━━━━━━━━━━━━━━━━━━━━\n\n💎 <i>Fastest • Beautiful • Free</i>\n\n━━━━━━━━━━━━━━━━━━━━━━\nPOWERD BY @bigolive_asia")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_welcome(update.effective_chat.id), parse_mode="HTML", reply_markup=get_main_keyboard(update.effective_chat.id))
async def send_sport_to_chat(chat_id, context, key):
    txt = format_full(key, chat_id); await context.bot.send_message(chat_id=chat_id, text=txt[:4000], parse_mode="HTML", reply_markup=get_back_keyboard(chat_id, key))
async def send_news_to_chat(chat_id, context):
    msg = await context.bot.send_message(chat_id=chat_id, text=tr(chat_id,"loading")); txt = format_news(chat_id); await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=txt, parse_mode="HTML", reply_markup=get_back_keyboard(chat_id,"news"))
async def send_live_to_chat(chat_id, context):
    msg = await context.bot.send_message(chat_id=chat_id, text=tr(chat_id,"loading")); text = f"✨ <b>{tr(chat_id,'live_all')}</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key in SPORT_CONFIG.keys():
        title, live, up, res = get_data(key, chat_id); text += f"<b>{title}</b>\n"; text += "".join(live[:1]) if live else "😴 No Live\n━━━━━━━━━━━━━━━━━━━━━━\n"
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=text[:4000], parse_mode="HTML", reply_markup=get_back_keyboard(chat_id,"live"))
async def send_results_to_chat(chat_id, context):
    msg = await context.bot.send_message(chat_id=chat_id, text=tr(chat_id,"loading")); text = f"✨ <b>{tr(chat_id,'results')}</b> ✨\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key in SPORT_CONFIG.keys():
        title, live, up, res = get_data(key, chat_id); text += f"<b>{title}</b>\n"; text += "".join(res[:1]) if res else "No Results\n━━━━━━━━━━━━━━━━━━━━━━\n"
    await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=text[:4000], parse_mode="HTML", reply_markup=get_back_keyboard(chat_id,"results"))
async def send_table_to_chat(chat_id, context):
    txt = f"🏆 <b>{tr(chat_id,'table')}</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"; data = fetch_standings("soccer","eng.1")
    try:
        entries = data['children'][0]['standings']['entries'][:10]
        for i, e in enumerate(entries, 1):
            team = e['team']['displayName']; stats = {s['name']: s['value'] for s in e['stats']}
            txt += f"{i}. <b>{team}</b> - {stats.get('points',0)} Pts | P:{stats.get('gamesPlayed',0)} W:{stats.get('wins',0)} D:{stats.get('ties',0)} L:{stats.get('losses',0)}\n"
    except: txt += "Table Updating... Try Again Later\n"
    txt += "\n━━━━━━━━━━━━━━━━━━━━━━\n💬 @bigolive_asia"
    await context.bot.send_message(chat_id=chat_id, text=txt[:4000], parse_mode="HTML", reply_markup=get_back_keyboard(chat_id,"table"))
async def send_tomorrow_to_chat(chat_id, context):
    txt = f"📅 <b>{tr(chat_id,'tomorrow')}</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for key in ["football","cricket","basketball","tennis"]:
        title, live, up, res = get_data(key, chat_id); txt += f"<b>{title}</b>\n"; txt += "".join(up[:2]) if up else "No Matches\n━━━━━━━━━━━━━━━━━━━━━━\n"
    await context.bot.send_message(chat_id=chat_id, text=txt[:4000], parse_mode="HTML", reply_markup=get_back_keyboard(chat_id,"tomorrow"))
async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: await update.message.reply_text("🔍 /search Real Madrid", parse_mode="HTML"); return
    q = " ".join(context.args).lower(); await update.message.reply_text(f"🔍 {q}...", parse_mode="HTML"); found=False
    for key in SPORT_CONFIG.keys():
        title, live, up, res = get_data(key, update.effective_chat.id)
        for item in live + up + res:
            if q in item.lower(): await update.message.reply_text(item[:4000], parse_mode="HTML"); found=True; break
        if found: break
    if not found: await update.message.reply_text("😴 No Match Found", parse_mode="HTML")
async def live_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_live_to_chat(update.effective_chat.id, context)
async def results_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_results_to_chat(update.effective_chat.id, context)
async def table_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_table_to_chat(update.effective_chat.id, context)
async def tomorrow_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_tomorrow_to_chat(update.effective_chat.id, context)
async def news_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_news_to_chat(update.effective_chat.id, context)
async def make_handler(key):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE): await send_sport_to_chat(update.effective_chat.id, context, key)
    return handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer(tr(update.effective_chat.id,"loading")); data = q.data; chat_id = update.effective_chat.id
    if data == "menu_start": await context.bot.send_message(chat_id=chat_id, text=get_welcome(chat_id), parse_mode="HTML", reply_markup=get_main_keyboard(chat_id))
    elif data == "menu_news": await send_news_to_chat(chat_id, context)
    elif data == "menu_lang": await context.bot.send_message(chat_id=chat_id, text=f"🌐 <b>{tr(chat_id,'choose_lang')}</b>", parse_mode="HTML", reply_markup=get_lang_keyboard())
    elif data.startswith("lang_"):
        lang = data.replace("lang_",""); USER_LANG[str(chat_id)] = lang
        await context.bot.send_message(chat_id=chat_id, text=f"{tr(chat_id,'saved')} - {LANG_NAMES.get(lang,lang)}\n\n{tr(chat_id,'welcome')}", parse_mode="HTML", reply_markup=get_main_keyboard(chat_id))
    elif data == "menu_live": await send_live_to_chat(chat_id, context)
    elif data == "menu_results": await send_results_to_chat(chat_id, context)
    elif data == "menu_table": await send_table_to_chat(chat_id, context)
    elif data == "menu_tomorrow": await send_tomorrow_to_chat(chat_id, context)
    elif data == "menu_search": await context.bot.send_message(chat_id=chat_id, text="🔍 /search Real Madrid", parse_mode="HTML")
    elif data.startswith("menu_"):
        key = data.replace("menu_","")
        if key in SPORT_CONFIG: await send_sport_to_chat(chat_id, context, key)

last_sent = {}
async def auto_job(context: ContextTypes.DEFAULT_TYPE):
    global last_sent
    try:
        if not CHANNEL_IDS: return
        # FIX: break එක අයින් කරලා - හැම Sport එකම යනවා, Score වෙනස් වුනොත් විතරක් යනවා
        for key in SPORT_CONFIG.keys():
            title, live, _, _ = get_data(key, "0")
            if not live: continue
            new_text = live[0][:500]
            if last_sent.get(f"live_{key}") == new_text: continue
            last_sent[f"live_{key}"] = new_text
            text = f"✨ <b>🔴 LIVE UPDATE - {title}</b> ✨\n\n{live[0]}"[:4000]
            for CH in CHANNEL_IDS:
                try: await context.bot.send_message(chat_id=CH, text=text, parse_mode="HTML")
                except: pass
            await asyncio.sleep(1)
        if last_sent.get("news_time", 0) < asyncio.get_event_loop().time() - 1800:
            last_sent["news_time"] = asyncio.get_event_loop().time()
            news_txt = format_news("0")
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
    for key in SPORT_CONFIG.keys():
        h = await make_handler(key); app.add_handler(CommandHandler(key, h))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.job_queue.run_repeating(auto_job, interval=180, first=10)
    print("Premium Bot Started!")
    await app.initialize(); await app.start(); await app.updater.start_polling(); await asyncio.Event().wait()
if __name__ == "__main__":
    asyncio.run(main())
