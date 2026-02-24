import yfinance as yf
import pandas as pd
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# --- AYARLAR ---
TOKEN = "8349458683:AAEi-AFSYxn0Skds7r4VQIaogVl3Fugftyw"
CHAT_ID = "1484256652"

def telegram_gonder(mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mesaj}
        r = requests.post(url, json=payload, timeout=10)
        print(f">>> Telegram Log: {r.status_code}")
        return r.status_code
    except Exception as e:
        print(f">>> Mesaj Hatasi: {e}")
        return None

def analiz_dongusu():
    # Bot baslar baslamaz selam verir
    print(">>> ANALIZ DONGUSU BASLADI!")
    telegram_gonder("💰 Zengin Golden Cross Botu Render Üzerinde Aktif! 🚀")

    # Takip edilecek semboller
    takip_listesi = ["BTC-USD", "ETH-USD", "SOL-USD", "KAS-USD", "NVDA", "TSLA", "THYAO.IS"]

    while True:
        print(f">>> Tarama yapiliyor: {time.ctime()}")
        for sembol in takip_listesi:
            try:
                df = yf.download(sembol, period="2y", interval="1d", progress=False)
                if len(df) < 145: continue
                
                # SMA Hesaplama
                sma20 = df['Close'].rolling(window=20).mean()
                sma140 = df['Close'].rolling(window=140).mean()
                
                # Golden Cross Kontrolü (Dünkü kapanıs ve bugünkü durum)
                if sma20.iloc[-2] <= sma140.iloc[-2] and sma20.iloc[-1] > sma140.iloc[-1]:
                    fiyat = float(df['Close'].iloc[-1])
                    telegram_gonder(f"🚀 GOLDEN CROSS YAKALANDI!\n💎 Sembol: {sembol}\n💰 Fiyat: {fiyat:.2f}")
                
                time.sleep(3) # Limitlere takilmamak icin
            except: continue
        
        time.sleep(600) # 10 dakikada bir tarar

# Render'in botu "canli" gormesi icin gereken sunucu
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Aktif")

if __name__ == "__main__":
    # Analizi arka planda baslat
    Thread(target=analiz_dongusu).start()
    # Sunucuyu baslat (Render 10000 veya 8080 portunu bekleyebilir ama genelde otomatik algilar)
    server = HTTPServer(('0.0.0.0', 10000), HealthHandler)
    server.serve_forever()
