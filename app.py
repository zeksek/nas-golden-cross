import yfinance as yf
import pandas as pd
import requests
import time
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- ⚙️ AYARLAR ---
TOKEN = "8349458683:AAEi-AFSYxn0Skds7r4VQIaogVl3Fugftyw"
ID_GUNLUK = "1484256652"          # Günlük sinyaller için eski grup
ID_KANAL = "-1003792245773"       # 15D, 1S ve 4S sinyalleri için yeni kanal

def telegram_gonder(chat_id, mesaj):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": mesaj, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except: pass

# --- 📋 TEMİZLENMİŞ 150 VARLIK LİSTESİ (Hatalılar Çıkarıldı) ---
liste = [
    "BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "XRP-USD", "ADA-USD", "DOT-USD", "LINK-USD", "DOGE-USD",
    "POL-USD", "LTC-USD", "NEAR-USD", "ARB-USD", "OP-USD", "RENDER-USD", "FET-USD", "INJ-USD",
    "THYAO.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "ASELS.IS", "TUPRS.IS", "ISCTR.IS", "AKBNK.IS", "GARAN.IS", "SASA.IS",
    "EKGYO.IS", "YKBNK.IS", "VAKBN.IS", "HALKB.IS", "BIMAS.IS", "ARCLK.IS", "FROTO.IS", "TOASO.IS", "PETKM.IS", "GUBRF.IS",
    "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NFLX", "AMD", "INTC", "PYPL", "TSM", "BABA", "COIN", "MSTR",
    "GC=F", "SI=F", "CL=F", "^GSPC", "^IXIC"
]

def tarama_motoru(periyot_adi, interval, period, sma_ayar, bekleme, hedef_id, hacim_kontrol=True):
    while True:
        for sembol in liste:
            try:
                df = yf.download(sembol, period=period, interval=
