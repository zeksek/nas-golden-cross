import os
import time
import logging
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Kütüphaneler: pip install binance-futures-connector yfinance pandas numpy requests
from binance.um_futures import UMFutures
import yfinance as yf

# ══════════════════════════════════════════════════════════════
#  ⚙️  YAPILANDIRMA (AYARLAR)
# ══════════════════════════════════════════════════════════════

# 🔑 API BİLGİLERİ (Binance Futures kullanacaksanız buraya ekleyin)
API_KEY    = os.environ.get("BINANCE_API_KEY", "BURAYA_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET", "BURAYA_SECRET_KEY")

# 📢 TELEGRAM BİLGİLERİ
TELEGRAM_TOKEN = "8349458683:AAEi-AFSYxn0Skds7r4VQIaogVl3Fugftyw"
USER_ID = "1484256652"         # Kişisel Chat ID
CHAN_ID = "-1003792245773"     # Kanal ID

# 📊 STRATEJİ PARAMETRELERİ
TIMEFRAME = "1d"               # Günlük grafik (Senin analizlerin için en doğrusu)
RSI_PUSU_ALT = 28              # Bu değerin altına düşerse "Pusu" başlar
RSI_PUSU_UST = 72              # Bu değerin üstüne çıkarsa "Pusu" başlar
RSI_TETIK_LONG = 31            # 28 altından gelip 31'e değerse giriş
RSI_TETIK_SHORT = 69           # 72 üstünden gelip 69'a değerse giriş
TRAILING_STOP_PCT = 0.5        # 20x kaldıraçta tam 100$ (Bakiye 1000$ ise)

# 🌐 VARLIK LİSTELERİ
CRYPTO_SYMBOLS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","AVAXUSDT","TRXUSDT","DOTUSDT",
    "LINKUSDT","MATICUSDT","LTCUSDT","BCHUSDT","NEARUSDT","UNIUSDT","ATOMUSDT","XLMUSDT","ETCUSDT","ALGOUSDT",
    "VETUSDT","FILUSDT","APTUSDT","ARBUSDT","OPUSDT","INJUSDT","SUIUSDT","STXUSDT","RUNEUSDT","SEIUSDT",
    "TIAUSDT","ORDIUSDT","WLDUSDT","FETUSDT","AGIXUSDT","RENDERUSDT","IOTAUSDT","SANDUSDT","MANAUSDT","AXSUSDT",
    "GALAUSDT","ENJUSDT","CHZUSDT","FLOWUSDT","EGLDUSDT","HBARUSDT","QNTUSDT","XTZUSDT","EOSUSDT","NEOUSDT",
    "AAVEUSDT","MKRUSDT","COMPUSDT","CRVUSDT","SNXUSDT","YFIUSDT","SUSHIUSDT","1INCHUSDT","BALUSDT","UMAUSDT",
    "LRCUSDT","SKLUSDT","CELRUSDT","BANDUSDT","KNCUSDT","OCEANUSDT","STORJUSDT","ZILUSDT","ICXUSDT","ONTUSDT",
    "ZECUSDT","DASHUSDT","XMRUSDT","WAVESUSDT","KSMUSDT","ROSEUSDT","CFXUSDT","CKBUSDT","KLAYUSDT","ONEUSDT",
    "ANKRUSDT","CTSIUSDT","CELOUSDT","RVNUSDT","SCUSDT","DGBUSDT","BATUSDT","ZENUSDT","RAYUSDT","SRMUSDT",
    "COTIUSDT","REEFUSDT","TRUUSDT","ACHUSDT","IDEXUSDT","WAXPUSDT","HNTUSDT","MINAUSDT","GMTUSDT","LDOUSDT"
]

STOCK_SYMBOLS = [
    "AAPL","MSFT","GOOGL","AMZN","META","NVDA","TSLA","AVGO","ORCL","CRM","AMD","INTC","QCOM","TXN","MU","AMAT",
    "LRCX","KLAC","MRVL","SNPS","CDNS","ADBE","NOW","INTU","PANW","CRWD","ZS","NET","DDOG","SNOW","JPM","BAC",
    "GS","MS","WFC","C","BLK","SCHW","AXP","V","MA","PYPL","COF","USB","PNC","TFC","BK","STT","MTB","RF","JNJ",
    "UNH","PFE","ABBV","MRK","LLY","TMO","ABT","DHR","BMY","AMGN","GILD","VRTX","REGN","ISRG","XOM","CVX","COP",
    "EOG","SLB","PXD","MPC","VLO","PSX","OXY","WMT","HD","MCD","SBUX","NKE","TGT","COST","LOW","DG","DLTR","BA",
    "CAT","GE","HON","LMT","RTX","UPS","FDX","DE","EMR","NFLX","DIS","CMCSA","T","VZ"
]

# ══════════════════════════════════════════════════════════════
#  🛠️ YARDIMCI FONKSİYONLAR
# ══════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
client = UMFutures(key=API_KEY, secret=API_SECRET)

def tg_notify(msg):
    """Telegram üzerinden bildirim gönderir."""
    for cid in [USER_ID, CHAN_ID]:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            requests.post(url, json={"chat_id": cid, "text": msg, "parse_mode": "HTML"}, timeout=10)
        except Exception as e:
            logging.error(f"Telegram Hatası: {e}")

def compute_indicators(df):
    """RSI ve Heikin Ashi hesaplamalarını yapar."""
    # RSI Hesaplama
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    # Heikin Ashi Hesaplama
    df["ha_close"] = (df["open"] + df["high"] + df["low"] + df["close"]) / 4
    ha_open = [(df["open"].iloc[0] + df["close"].iloc[0]) / 2]
    for i in range(1, len(df)):
        ha_open.append((ha_open[i-1] + df["ha_close"].iloc[i-1]) / 2)
    df["ha_open"] = ha_open
    df["ha_color"] = np.where(df["ha_close"] > df["ha_open"], "green", "red")
    return df

def scan_symbol(market_type, symbol):
    """Tek bir sembol için veriyi çeker ve sinyal kontrolü yapar."""
    try:
        if market_type == "CRYPTO":
            raw = client.klines(symbol=symbol, interval=TIMEFRAME, limit=100)
            df = pd.DataFrame(raw, columns=["t","o","h","l","c","v","ct","qv","tr","tb","tq","i"])
            df = df[["o","h","l","c"]].rename(columns={"o":"open","h":"high","l":"low","c":"close"}).astype(float)
        else:
            df = yf.Ticker(symbol).history(period="1y", interval=TIMEFRAME).rename(columns=str.lower)
            if df.empty: return

        df = compute_indicators(df)
        curr = df.iloc[-2]   # Tamamlanmış son mum
        prev = df.iloc[-3]   # Bir önceki mum
        past = df.iloc[-15:-2] # Son 15 gün pusu kontrolü

        # STRATEJİ KONTROLÜ
        was_oversold = (past["rsi"] < RSI_PUSU_ALT).any()
        was_overbought = (past["rsi"] > RSI_PUSU_UST).any()

        # LONG TETİK
        if was_oversold and curr["rsi"] >= RSI_TETIK_LONG and prev["rsi"] < RSI_TETIK_LONG and curr["ha_color"] == "green":
            send_signal(symbol, "LONG 🟢", curr)
        
        # SHORT TETİK
        elif was_overbought and curr["rsi"] <= RSI_TETIK_SHORT and prev["rsi"] > RSI_TETIK_SHORT and curr["ha_color"] == "red":
            send_signal(symbol, "SHORT 🔴", curr)

    except Exception as e:
        pass # Hatalı sembolleri atla

def send_signal(symbol, direction, data):
    """Sinyal oluştuğunda mesajı hazırlar ve gönderir."""
    price = data["close"]
    rsi_val = data["rsi"]
    # Trading Stop hesaplama ( %0.5)
    stop_price = price * (1 - 0.005) if "LONG" in direction else price * (1 + 0.005)
    
    msg = (f"🚀 <b>YENİ SİNYAL: {direction}</b>\n"
           f"━━━━━━━━━━━━━━━━━━━━\n"
           f"🔖 Sembol: <b>#{symbol}</b>\n"
           f"💵 Giriş Fiyatı: <b>{price:.2f}</b>\n"
           f"📊 RSI Değeri: <b>{rsi_val:.2f}</b>\n"
           f"🛑 100$ İzleyen Stop: <b>{stop_price:.2f}</b>\n"
           f"⚡ Kaldıraç: <b>20x</b>")
    tg_notify(msg)

# ══════════════════════════════════════════════════════════════
#  🔁 ANA DÖNGÜ
# ══════════════════════════════════════════════════════════════

def run_bot():
    # Başlangıç Mesajı
    start_msg = (f"🤖 <b>BOT BAŞLADI</b>\n"
                 f"━━━━━━━━━━━━━━━━━━━━\n"
                 f"🎯 Strateji: RSI {RSI_PUSU_ALT}-{RSI_PUSU_UST} Pusu\n"
                 f"📈 Tetik Seviyesi: {RSI_TETIK_LONG}/{RSI_TETIK_SHORT}\n"
                 f"🛡️ İzleyen Stop: %{TRAILING_STOP_PCT}\n"
                 f"📡 Tarama Listesi: 200 Sembol\n"
                 f"⏰ Zaman: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    tg_notify(start_msg)
    logging.info("Bot Telegram bildirimi ile başlatıldı.")

    while True:
        tasks = [("CRYPTO", s) for s in CRYPTO_SYMBOLS] + [("STOCK", s) for s in STOCK_SYMBOLS]
        
        logging.info(f"Tarama başlatılıyor... ({len(tasks)} sembol)")
        with ThreadPoolExecutor(max_workers=15) as executor:
            for m_type, sym in tasks:
                executor.submit(scan_symbol, m_type, sym)
        
        logging.info("Tarama tamamlandı. 1 saat sonra tekrar denenecek.")
        time.sleep(3600) # Her saat başı bir kez tara

if __name__ == "__main__":
    run_bot()
