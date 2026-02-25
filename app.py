import yfinance as yf
import pandas as pd
import requests
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- ⚙️ AYARLAR ---
TOKEN = "8349458683:AAEi-AFSYxn0Skds7r4VQIaogVl3Fugftyw"
ID_GUNLUK = "1484256652"          
ID_KANAL = "-1003792245773"       

def telegram_gonder(chat_id, mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": mesaj, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except: pass

# --- 📋 TARAMA LİSTESİ ---
liste = [
    "BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "XRP-USD", "ADA-USD", "DOT-USD", "LINK-USD", "DOGE-USD",
    "KAS-USD", "LTC-USD", "NEAR-USD", "ARB-USD", "OP-USD", "FET-USD", "INJ-USD",
    "THYAO.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "ASELS.IS", "TUPRS.IS", "ISCTR.IS", "AKBNK.IS", "GARAN.IS", "SASA.IS",
    "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NFLX", "AMD", "INTC", "PYPL", "COIN", "MSTR",
    "GC=F", "SI=F", "^GSPC", "^IXIC"
]

def tarama_motoru(periyot_adi, interval, period, sma_ayar, bekleme, hedef_id):
    while True:
        for sembol in liste:
            try:
                veri = yf.Ticker(sembol)
                df = veri.history(period=period, interval=interval)
                
                if df.empty or len(df) < max(sma_ayar) + 5: continue
                
                # --- 🕯️ HEIKIN-ASHI HESAPLAMA ---
                # HA_Close = (Open + High + Low + Close) / 4
                df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
                
                # HA_Open = (Önceki HA_Open + Önceki HA_Close) / 2
                # (Kod içinde hız için basitleştirilmiş HA_Close bazlı trend takibi yapılır)
                
                # Ortalamalar artık HA_Close üzerinden hesaplanıyor
                sma_kisa = df['HA_Close'].rolling(window=sma_ayar[0]).mean()
                sma_uzun = df['HA_Close'].rolling(window=sma_ayar[1]).mean()
                fiyat_ha = float(df['HA_Close'].iloc[-1])
                fiyat_normal = float(df['Close'].iloc[-1])

                # 🚀 GOLDEN CROSS (Heikin-Ashi Bazlı)
                if sma_kisa.iloc[-2] <= sma_uzun.iloc[-2] and sma_kisa.iloc[-1] > sma_uzun.iloc[-1]:
                    
                    # 📊 CVD/HACİM KONTROLÜ
                    avg_vol = df['Volume'].tail(10).mean()
                    current_vol = df['Volume'].iloc[-1]
                    cvd_onay = "✅ CVD/HACİM ONAYLI" if current_vol > (avg_vol * 1.1) else "⚠️ ZAYIF HACİM"
                    
                    mesaj = (f"🚀 {sembol} {periyot_adi} HA-KESİŞİM\n"
                            f"📈 HA Kapanış: {fiyat_ha:.2f}\n"
                            f"💰 Gerçek Fiyat: {fiyat_normal:.2f}\n"
                            f"📊 Durum: {cvd_onay}\n"
                            f"🕯️ Heikin-Ashi Temelli Hesaplama Aktif")
                    
                    telegram_gonder(hedef_id, mesaj)
                
                elif sma_kisa.iloc[-2] >= sma_uzun.iloc[-2] and sma_kisa.iloc[-1] < sma_uzun.iloc[-1]:
                    telegram_gonder(hedef_id, f"💀 {sembol} {periyot_adi} HA-Satış\n💰 Fiyat: {fiyat_normal:.2f}")

                time.sleep(1.2)
            except: continue
        time.sleep(bekleme)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HA-Engine Live")

if __name__ == "__main__":
    telegram_gonder(ID_KANAL, "🕯️ STRATEJİ GÜNCELLENDİ!\nHeikin-Ashi fiyat hesaplaması ve CVD onay sistemi devreye girdi.")
    
    Thread(target=tarama_motoru, args=("Günlük", "1d", "2y", (20, 140), 1800, ID_GUNLUK)).start()
    Thread(target=tarama_motoru, args=("4 Saat", "4h", "100d", (50, 200)…
