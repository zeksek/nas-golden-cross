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

# --- 📋 EN STABİL LİSTE ---
liste = [
    "BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "XRP-USD", "ADA-USD", "DOT-USD", "LINK-USD", "DOGE-USD",
    "KAS-USD", "LTC-USD", "NEAR-USD", "ARB-USD", "OP-USD", "FET-USD", "INJ-USD",
    "THYAO.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "ASELS.IS", "TUPRS.IS", "ISCTR.IS", "AKBNK.IS", "GARAN.IS", "SASA.IS",
    "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NFLX", "AMD", "INTC", "PYPL", "COIN", "MSTR",
    "GC=F", "SI=F", "^GSPC", "^IXIC"
]

def tarama_motoru(periyot_adi, interval, period, sma_ayar, bekleme, hedef_id, hacim_kontrol=True):
    while True:
        for sembol in liste:
            try:
                # Veri çekme hatasını (NoneType) engellemek için kontrol eklendi
                veri = yf.Ticker(sembol)
                df = veri.history(period=period, interval=interval)
                
                if df is None or df.empty or len(df) < max(sma_ayar) + 5:
                    continue
                
                sma_kisa = df['Close'].rolling(window=sma_ayar[0]).mean()
                sma_uzun = df['Close'].rolling(window=sma_ayar[1]).mean()
                fiyat = float(df['Close'].iloc[-1])

                if sma_kisa.iloc[-2] <= sma_uzun.iloc[-2] and sma_kisa.iloc[-1] > sma_uzun.iloc[-1]:
                    hacim_notu = ""
                    if hacim_kontrol and 'Volume' in df.columns:
                        avg_vol = df['Volume'].tail(15).mean()
                        cur_vol = df['Volume'].iloc[-1]
                        hacim_notu = " ✅ HACİM ONAYLI" if cur_vol > (avg_vol * 1.1) else " ⚠️ HACİM DÜŞÜK"
                    
                    telegram_gonder(hedef_id, f"🚀 {sembol} {periyot_adi} Golden Cross{hacim_notu}\n💰 Fiyat: {fiyat:.2f}")
                
                elif sma_kisa.iloc[-2] >= sma_uzun.iloc[-2] and sma_kisa.iloc[-1] < sma_uzun.iloc[-1]:
                    telegram_gonder(hedef_id, f"💀 {sembol} {periyot_adi} Dead Cross\n💰 Fiyat: {fiyat:.2f}")
                
                time.sleep(1.5) # Yahoo engelini yememek için bekleme süresi artırıldı
            except Exception as e:
                print(f"Hata: {sembol} - {str(e)}")
                continue
        time.sleep(bekleme)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Engine is Active")

if __name__ == "__main__":
    telegram_gonder(ID_KANAL, "🚀 SİSTEM YENİDEN BAŞLATILDI!\nVeri çekme hataları için güvenlik önlemleri eklendi.")
    
    Thread(target=tarama_motoru, args=("Günlük", "1d", "2y", (20, 140), 1800, ID_GUNLUK, False)).start()
    Thread(target=tarama_motoru, args=("4 Saat", "4h", "100d", (50, 200), 900, ID_KANAL, True)).start()
    Thread(target=tarama_motoru, args=("1 Saat", "1h", "30d", (50, 200), 600, ID_KANAL, True)).start()
    Thread(target=tarama_motoru, args=("15 Dakika", "15m", "7d", (20, 50), 300, ID_KANAL, True)).start()
    
    server = HTTPServer(('0.0.0.0', 10000), HealthHandler)
    server.serve_forever()
