# Crypto Pulse Bot — Fase 1 (MVP)

Bot Telegram harian: harga BTC/ETH/SOL + ringkasan berita relevan (AI-summarized), plus alert real-time kalau harga melewati threshold. Bot ini memberi informasi, **bukan sinyal beli/jual**.

## Struktur

```
crypto_pulse/
├── .github/workflows/
│   ├── daily-digest.yml    # jadwal GitHub Actions: digest pagi
│   └── threshold-check.yml # jadwal GitHub Actions: alert tiap jam
├── config.py           # semua setting (baca dari .env / secrets)
├── price_service.py     # fetch harga dari CoinGecko
├── news_service.py       # fetch RSS + ringkas pakai Claude
├── telegram_service.py   # kirim pesan ke Telegram
├── state.py              # dedupe alert (cooldown)
├── daily_digest.py        # ENTRY POINT 1: digest pagi
├── threshold_check.py     # ENTRY POINT 2: alert real-time
├── requirements.txt
├── .gitignore
└── .env.example
```

## Status riset (sudah diverifikasi)

- **CoinGecko**: pakai Demo API key (gratis, daftar di https://www.coingecko.com/en/developers/dashboard) → 100 req/menit, 10.000 req/bulan, plus akses data historis untuk Fase 2.
- **Berita**: NewsAPI.org **tidak dipakai** — free tier-nya cuma untuk localhost & melarang penggunaan produksi. Pakai RSS gratis tanpa batas: CoinDesk, CoinTelegraph, dan Fed press releases untuk konteks makro.
- **Ringkasan berita**: pakai Claude API (`claude-haiku-4-5`) untuk merangkas headline RSS jadi 1-2 kalimat relevan. Kalau `ANTHROPIC_API_KEY` tidak diset, otomatis fallback ke headline polos (tidak crash).
- **Threshold alert**: cek terpisah tiap jam (bukan cuma di digest pagi), dengan cooldown 6 jam supaya tidak spam untuk breach yang sama.
- Semua request eksternal (CoinGecko, RSS, Telegram) belum bisa dites langsung dari sandbox riset ini (network sandbox di-allowlist ketat). Logika inti (format pesan, filter berita, threshold, dedupe) sudah dites lewat mock data — hasilnya benar. **Test end-to-end dengan API key asli perlu dilakukan di mesin/servermu sendiri.**

## Setup

### 1. Install dependencies
```bash
cd crypto_pulse
pip install -r requirements.txt
```

### 2. Buat bot Telegram (BotFather)
1. Chat `@BotFather` di Telegram → `/newbot` → ikuti instruksi → catat token.
2. Chat bot barumu sekali (apa saja), lalu buka `https://api.telegram.org/bot<TOKEN>/getUpdates` di browser untuk menemukan `chat_id`-mu.

### 3. Daftar CoinGecko Demo API key (gratis)
https://www.coingecko.com/en/developers/dashboard → generate Demo API key.

### 4. Siapkan .env
```bash
cp .env.example .env
# isi TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, COINGECKO_API_KEY, ANTHROPIC_API_KEY
```

### 5. Test dry-run (tanpa kirim ke Telegram, cuma print ke terminal)
```bash
python3 daily_digest.py --dry-run
python3 threshold_check.py --dry-run
```

### 6. Test kirim sungguhan
```bash
python3 daily_digest.py
```

### 7. Jadwalkan via GitHub Actions (gratis, tanpa server)

1. Buat repo baru di GitHub (rekomendasi: **private**, cukup dari kuota gratis 2.000 menit/bulan — kebutuhan kita ~400 menit/bulan). Kalau nanti kuota kurang, tinggal ubah ke public dari Settings repo.
2. Push isi folder `crypto_pulse/` ke repo itu (jangan sampai `.env` ikut ke-push — sudah di-`.gitignore`, tapi cek lagi).
   ```bash
   git init
   git add .
   git commit -m "init crypto pulse bot"
   git branch -M main
   git remote add origin https://github.com/<username>/<repo>.git
   git push -u origin main
   ```
3. Di GitHub: repo → Settings → Secrets and variables → Actions → New repository secret. Tambahkan 3 secret ini (value sama seperti di `.env` lokal):
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `COINGECKO_API_KEY`
4. Buka tab **Actions** di repo → kamu akan lihat 2 workflow: "Crypto Pulse - Daily Digest" dan "Crypto Pulse - Threshold Check". Klik salah satu → "Run workflow" (tombol manual trigger) buat test tanpa nunggu jadwal.
5. Cek Telegram — pesan harus masuk. Kalau gagal, klik run yang merah di tab Actions buat lihat log error-nya.
6. Kalau test manual sukses, biarkan saja — jadwal otomatis (`cron` di file `.yml`) akan jalan sendiri tiap hari jam 07:00 WIB (digest) dan tiap jam (threshold check), tanpa laptop/PC kamu perlu nyala.

Ca