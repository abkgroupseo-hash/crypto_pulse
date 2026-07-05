"""
Konfigurasi Crypto Pulse Bot.
Semua nilai sensitif diambil dari environment variables (.env) — jangan hardcode secret di sini.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# --- CoinGecko ---
# Demo API key (gratis, daftar di https://www.coingecko.com/en/developers/dashboard)
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# --- Claude (untuk ringkasan berita) ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

# --- Coin yang dipantau ---
# key = CoinGecko id, value = simbol tampilan
COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
}

# --- Sumber berita RSS (gratis, tanpa API key) ---
NEWS_FEEDS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://www.federalreserve.gov/feeds/press_all.xml",  # verifikasi saat live run, ganti jika broken
]

# Kata kunci untuk filter relevansi berita (case-insensitive)
NEWS_KEYWORDS = [
    "bitcoin", "btc", "ethereum", "eth", "solana", "sol",
    "crypto", "cryptocurrency", "sec", "fed", "federal reserve",
    "interest rate", "regulation", "etf", "stablecoin",
]

# Berapa lama ke belakang berita masih dianggap "baru" (jam)
NEWS_LOOKBACK_HOURS = 24
NEWS_MAX_ITEMS = 6  # jumlah item mentah yang dikirim ke Claude untuk diringkas

# --- Threshold Alert (real-time, terpisah dari digest pagi) ---
# Persentase perubahan 24h yang memicu alert instan
THRESHOLD_PCT = float(os.getenv("THRESHOLD_PCT", "5.0"))
# Cooldown (jam) — jangan kirim alert berulang untuk breach yang sama dalam window ini
ALERT_COOLDOWN_HOURS = float(os.getenv("ALERT_COOLDOWN_HOURS", "6"))

# --- File state (menyimpan histori alert supaya tidak spam) ---
STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")
