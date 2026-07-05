"""
Entry point: cek perubahan 24h tiap coin, kirim alert Telegram INSTAN kalau
melewati THRESHOLD_PCT. Terpisah dari digest pagi.
Dijadwalkan via cron lebih sering, misal tiap 1 jam:
    0 * * * * /path/to/venv/bin/python /path/to/threshold_check.py
"""
import config
import price_service
import telegram_service
import state


def format_alert(coin_id: str, data: dict) -> str:
    symbol = data["symbol"]
    usd = data["usd"]
    change = data["usd_24h_change"]
    arrow = "\U0001F680" if change >= 0 else "\U0001F4C9"
    return (
        f"{arrow} *ALERT: {symbol} bergerak {change:+.2f}% dalam 24 jam*\n"
        f"Harga sekarang: ${usd:,.2f}\n\n"
        "⚠️ Ini informasi, bukan rekomendasi beli/jual."
    )


def run(dry_run: bool = False) -> list:
    prices = price_service.fetch_prices()
    sent = []

    for coin_id, data in prices.items():
        change = data.get("usd_24h_change")
        if change is None:
            continue
        if abs(change) < config.THRESHOLD_PCT:
            continue

        direction = "up" if change >= 0 else "down"
        if not state.should_alert(coin_id, direction):
            continue

        message = format_alert(coin_id, data)
        if dry_run:
            print(message)
            print("---")
        else:
            telegram_service.send_message(message)
            state.mark_alerted(coin_id, direction)
        sent.append(message)

    if dry_run and not sent:
        print(f"Tidak ada coin yang melewati threshold ±{config.THRESHOLD_PCT}% saat ini.")
    return sent


if __name__ == "__main__":
    import sys
    run(dry_run="--dry-run" in sys.argv)
