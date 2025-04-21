import requests
import datetime
import time
import random
from collections import deque

# بيانات تيليجرام
TELEGRAM_BOT_TOKEN = '7824094172:AAGxf6e83Q-EGI3CoKEbfXwu7XZDaHVPvSY'
TELEGRAM_CHANNEL_ID = '@trrytryrty'

# الأزواج المتاحة في كوتكس - اخترت أشهر الأزواج هنا
SYMBOLS = [
    "BTC-USDT", "ETH-USDT", "SOL-USDT", "LTC-USDT", "XRP-USDT", "BNB-USDT",
    "EUR-USD", "GBP-USD", "AUD-USD", "USD-JPY", "USD-CAD", "USD-CHF",
    "EUR-JPY", "GBP-JPY", "AUD-JPY", "EUR-GBP"
]

# تاريخ الأسعار القصير لكل رمز
price_history = {symbol: deque(maxlen=10) for symbol in SYMBOLS}
last_sent = {}  # لتتبع وقت آخر توصية لكل زوج

# دالة إرسال توصية إلى تيليجرام
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)
        print("📤 تم إرسال التوصية:", response.status_code)
    except Exception as e:
        print("❌ فشل في الإرسال:", e)

# جلب السعر من OKX
def get_price(symbol):
    url = f"https://www.okx.com/api/v5/market/ticker?instId={symbol}"
    try:
        response = requests.get(url)
        data = response.json()
        return float(data['data'][0]['last'])
    except Exception as e:
        print(f"❌ خطأ في جلب السعر لـ {symbol}:", e)
        return None

# مدة الصفقة العشوائية
def get_random_duration():
    durations = ["30 ثانية", "1 دقيقة", "2 دقيقة", "5 دقائق", "15 دقيقة"]
    return random.choice(durations)

# التحقق من تغيير السعر (استراتيجية Price Spike)
def check_price_spike(symbol, current_price):
    history = price_history[symbol]
    if len(history) >= 2:
        previous_price = history[0]
        change = (current_price - previous_price) / previous_price * 100
        if change >= 0.2:
            return "up"
        elif change <= -0.2:
            return "down"
    return None

# توليد التوصية بالصيغة الجديدة
def create_signal(symbol, direction, price, duration):
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S')
    message = f"""صفقه جديده !

📊= اســـم العملة ({symbol})

🕗= مدة الصفقــة ({duration})

✅= توقيت الدخول ({now})   

🔍= اتجـاه الصفقة ({"شراء ⬆️" if direction == "up" else "بيع ⬇️"})  

➔ @ALBASHMO7ASP 👑"""
    print(message)
    send_to_telegram(message)

# تشغيل البوت
if __name__ == "__main__":
    print("🚀 بدأ البوت في المراقبة...")
    while True:
        for symbol in SYMBOLS:
            price = get_price(symbol)
            if price:
                price_history[symbol].append(price)
                signal = check_price_spike(symbol, price)

                # تحقق من وجود إشارة ومنع التكرار خلال آخر 30 ثانية
                last_time = last_sent.get(symbol)
                now = time.time()
                if signal and (not last_time or now - last_time >= 30):
                    duration = get_random_duration()
                    create_signal(symbol, signal, price, duration)
                    last_sent[symbol] = now

        time.sleep(5)
