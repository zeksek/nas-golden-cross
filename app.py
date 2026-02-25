import yfinance as yf
import pandas as pd
import requests
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- AYARLAR ---
TOKEN = "8349458683:AAEi-AFSYxn0Skds7r4VQIaogVl3Fugftyw"
ID_GUNLUK = "1484256652"          
ID_KANAL = "-1003792245773"    

def telegram_gonder(chat_id, mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": mesaj, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except: pass

# --- TARAMA LİSTESİ (150 Varlık) ---
liste = [
    "BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "XRP-USD", "ADA-USD", "DOT-USD", "LINK-USD", "DOGE-USD", "SHIB-USD",
    "MATIC-USD", "LTC-USD", "NEAR-USD", "ARB-USD", "OP-USD", "PEPE-USD", "RNDR-USD", "FET-USD", "STX-USD", "INJ-USD",
    "THYAO.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "ASELS.IS", "TUPRS.IS", "ISCTR.IS", "AKBNK.IS", "GARAN.IS", "SASA.IS",
    "EKGYO.IS", "YKBNK.IS", "VAKBN.IS", "HALKB.IS", "BIMAS.IS", "ARCLK.IS", "FROTO.IS", "TOASO.IS", "PETKM.IS", "GUBRF.IS",
    "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NFLX", "AMD", "INTC", "PYPL", "TSM", "BABA", "COIN", "MSTR",
    "GC=F", "SI=F", "CL=F", "^GSPC", "^IXIC"
]

def tarama_motoru(periyot_adi, interval, period, sma_ayar, bekleme, hedef_id, hacim_kontrol=True):
    while True:
        for sembol in liste:
            try:
                df = yf.download(sembol, period=period, interval=interval, progress=False)
                if len(df) < max(sma_ayar) + 2: continue
                
                sma_kisa = df['Close'].rolling(window=sma_ayar[0]).mean()
                sma_uzun = df['Close'].rolling(window=sma_ayar[1]).mean()
                fiyat = float(df['Close'].iloc[-1])

                # Golden Cross
                if sma_kisa.iloc[-2] <= sma_uzun.iloc[-2] and sma_kisa.iloc[-1] > sma_uzun.iloc[-1]:
                    hacim_durumu = ""
                    if hacim_kontrol:
                        avg_vol = df['Volume'].tail(10).mean() # Son 10 barın ortalaması
                        cur_vol = df['Volume'].iloc[-1]
                        hacim_durumu = " ✅ HACİM ONAYLI" if cur_vol > (avg_vol * 1.1) else " ⚠️ HACİM ONAYSIZ"
                    
                    mesaj = f"🚀 {sembol} {periyot_adi} Golden Cross{hacim_durumu}\n💰 Fiyat: {fiyat:.2f}"
                    telegram_gonder(hedef_id, mesaj)
                
                # Dead Cross
                elif sma_kisa.iloc[-2] >= sma_uzun.iloc[-2] and sma_kisa.iloc[-1] < sma_uzun.iloc[-1]:
                    telegram_gonder(hedef_id, f"💀 {sembol} {periyot_adi} Dead Cross\n💰 Fiyat: {fiyat:.2f}")
                
                time.sleep(0.3) # Starter hızında tarama
            except: continue
        time.sleep(bekleme)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"4-Engine Pro Terminal Active")

if __name__ == "__main__":
    # 1. GÜNLÜK (20/140) -> Eski Grup
    Thread(target=tarama_motoru, args=("Günlük", "1d", "2y", (20, 140), 1800, ID_GUNLUK, False)).start()
    
    # 2. 4 SAATLİK (50/200) -> Yeni Kanal
    Thread(target=tarama_motoru, args=("4 Saat", "4h", "100d", (50, 200), 900, ID_KANAL, True)).start()
    
    # 3. 1 SAATLİK (50/200) -> Yeni Kanal
    Thread(target=tarama_motoru, args=("1 Saat", "1h", "30d", (50, 200), 600, ID_KANAL, True)).start()
    
    # 4. 15 DAKİKALIK (20/50) -> Yeni Kanal (Hızlı sinyal için 20/50 daha iyidir)
    Thread(target=tarama_motoru, args=("15 Dakika", "15m", "7d", (20, 50), 300, ID_KANAL, True)).start()
    
    server = HTTPServer(('0.0.0.0', 10000), HealthHandler)
    server.serve_forever()
