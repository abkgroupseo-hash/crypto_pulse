"""
Entry point: kirim 1 pesan digest pagi (harga + ringkasan berita).
Dijadwalkan via cron, misal jam 07:00 setiap hari.
"""
from datetime import datetime

import config
import price_service
import news_service
import telegram_service


def format_message(prices: dict, news_bullets: list) -> str:
    tanggal = datetime.now().strftime("%d %B %Y")
    lines = [f"₿ *CRYPTO PULSE* — {tanggal}", ""]

    for coin_id, data in prices.items():
        symbol = data["symbol"]
        usd = data["usd"]
        change = data["usd_24h_change"]
        if usd is None:
            lines.append(f"{symbol}: data tidak tersedia")
            continue
        arrow = "\U0001F7E2" if (change or 0) >= 0 else "\U0001F534"
        lines.append(f"{arrow} {symbol}: ${usd:,.2f} ({change:+.2f}%)")

    lines.append("")
    lines.append("\U0001F4F0 *NEWS DIGEST*")
    if news_bullets:
        for b in news_bullets:
            lines.append(f"- {b}")
    else:
        lines.append("- Tidak ada berita signifikan dalam 24 jam terakhir.")

    lines.append("")
    lines.append(
        "⚠️ Ini informasi, bukan rekomendasi beli/jual. "
        "Keputusan tetap di tangan kamu."
    )
    return "\n".join(lines)


def run(dry_run: bool = False) -> str:
    prices = price_service.fetch_prices()
    news_bullets = news_service.get_news_digest()
    message = format_message(prices, news_bullets)

    if dry_run:
        print(message)
    else:
        telegram_service.send_message(message)
    return message


if __name__ == "__main__":
    import sys
    run(dry_run="--dry-run" in sys.argv)
