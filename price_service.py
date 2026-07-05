"""Ambil harga & perubahan 24 jam untuk BTC/ETH/SOL dari CoinGecko."""
import requests
import config


def fetch_prices() -> dict:
    """
    Return: {"bitcoin": {"symbol": "BTC", "usd": 65000.0, "usd_24h_change": 2.3}, ...}
    Raises requests.HTTPError kalau API gagal — biar caller yang decide fallback.
    """
    ids = ",".join(config.COINS.keys())
    params = {
        "ids": ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
    }
    headers = {}
    if config.COINGECKO_API_KEY:
        # Demo API key dikirim via header x-cg-demo-api-key
        headers["x-cg-demo-api-key"] = config.COINGECKO_API_KEY

    resp = requests.get(
        f"{config.COINGECKO_BASE_URL}/simple/price",
        params=params,
        headers=headers,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    result = {}
    for coin_id, symbol in config.COINS.items():
        coin_data = data.get(coin_id, {})
        result[coin_id] = {
            "symbol": symbol,
            "usd": coin_data.get("usd"),
            "usd_24h_change": coin_data.get("usd_24h_change"),
        }
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(fetch_prices(), indent=2))
