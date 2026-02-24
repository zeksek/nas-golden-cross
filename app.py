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
        return r.status_code
    except:
        return None

def analiz_dongusu():
    print(">>> CIFT YONLU TARAMA BASLADI!")
    telegram_gonder("🔔 Bot Güncellendi!\n📈 Golden Cross (Yükseliş)\n📉 Dead Cross (Düşüş)\n\n250+ Varlık taranıyor...")

    takip_listesi = [
        # KRİPTO
        "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD", "AVAX-USD", "DOT-USD", "TRX-USD", "LINK-USD",
        "MATIC-USD", "SHIB-USD", "LTC-USD", "BCH-USD", "ATOM-USD", "XLM-USD", "KAS-USD", "ALGO-USD", "NEAR-USD", "ICP-USD",
        "INJ-USD", "OP-USD", "ARB-USD", "TIA-USD", "SUI-USD", "SEI-USD", "FET-USD", "RNDR-USD", "STX-USD", "FIL-USD",
        # BIST 100
        "THYAO.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS", "FROTO.IS", "DOAS.IS", "TTRAK.IS", "KCHOL.IS", "SAHOL.IS", "ASELS.IS",
        "AKBNK.IS", "GARAN.IS", "ISCTR.IS", "YKBNK.IS", "BIMAS.IS", "SASA.IS", "HEKTS.IS", "PGSUS.IS", "ARCLK.IS", "PETKM.IS",
        "KARDM.IS", "TOASO.IS", "ENKAI.IS", "TCELL.IS", "TTKOM.IS", "KONTR.IS", "SMRTG.IS", "EUPWR.IS", "YEOTK.IS", "ASTOR.IS",
        # NASDAQ & ABD
        "NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "AMD", "NFLX", "INTC", "PYPL", "ADBE", "CSCO", "PEP", "COST",
        "AVGO", "QCOM", "TXN", "MU", "AMAT", "LRCX", "PANW", "SNPS", "CDNS", "MAR", "ORCL", "IBM", "UBER", "ABNB", "COIN",
        # EMTİA
        "GC=F", "SI=F", "CL=F", "PA=F", "PL=F", "HG=F", "NG=F"
    ]

    while True:
        for sembol in takip_listesi:
            try:
                df = yf.download(sembol, period="2y", interval="1d", progress=False)
                if len(df) < 145: continue
                
                sma20 = df['Close'].rolling(window=20).mean()
                sma140 = df['Close'].rolling(window=140).mean()
                
                fiyat = float(df['Close'].iloc[-1])

                # 🚀 GOLDEN CROSS KONTROLÜ
                if sma20.iloc[-2] <= sma140.iloc[-2] and sma20.iloc[-1] > sma140.iloc[-1]:
                    telegram_gonder(f"🚀 GOLDEN CROSS (Yükseliş Sinyali!)\n\n💎 Varlık: {sembol}\n💰 Fiyat: {fiyat:.2f}\n✅ Trend yukarı dönüyor olabilir.")

                # 💀 DEAD CROSS KONTROLÜ
                elif sma20.iloc[-2] >= sma140.iloc[-2] and sma20.iloc[-1] < sma140.iloc[-1]:
                    telegram_gonder(f"💀 DEAD CROSS (Düşüş Sinyali!)\n\n💎 Varlık: {sembol}\n💰 Fiyat: {fiyat:.2f}\n⚠️ Trend aşağı dönüyor olabilir.")
                
                time.sleep(1.2)
            except:
                continue
        
        time.sleep(900)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Aktif")

if __name__ == "__main__":
    Thread(target=analiz_dongusu).start()
    server = HTTPServer(('0.0.0.0', 10000), HealthHandler)
    server.serve_forever()
