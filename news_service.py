"""Ambil berita relevan dari RSS feed gratis, lalu ringkas pakai Claude."""
from datetime import datetime, timedelta, timezone
from time import mktime

import feedparser
import config

try:
    import anthropic
except ImportError:
    anthropic = None


def _entry_datetime(entry):
    """Ambil published/updated time entry sebagai timezone-aware datetime (UTC).
    Kalau tidak ada timestamp, anggap baru saja (biar tidak ke-filter out)."""
    for key in ("published_parsed", "updated_parsed"):
        val = getattr(entry, key, None)
        if val:
            return datetime.fromtimestamp(mktime(val), tz=timezone.utc)
    return datetime.now(timezone.utc)


def _is_relevant(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in config.NEWS_KEYWORDS)


def fetch_raw_news() -> list:
    """Ambil entry RSS yang baru (<= NEWS_LOOKBACK_HOURS) & relevan (keyword match).
    Feed yang gagal di-parse akan di-skip (tidak bikin seluruh proses crash)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=config.NEWS_LOOKBACK_HOURS)
    items = []

    for url in config.NEWS_FEEDS:
        try:
            parsed = feedparser.parse(url)
            if parsed.bozo and not parsed.entries:
                # feed gagal total di-parse, skip
                continue
            for entry in parsed.entries:
                title = getattr(entry, "title", "")
                summary = getattr(entry, "summary", "")
                pub_dt = _entry_datetime(entry)
                if pub_dt < cutoff:
                    continue
                if not _is_relevant(title + " " + summary):
                    continue
                items.append({
                    "title": title,
                    "summary": summary,
                    "link": getattr(entry, "link", ""),
                    "source": parsed.feed.get("title", url),
                    "published": pub_dt.isoformat(),
                })
        except Exception:
            # Feed URL berubah/down — jangan sampai gagalkan seluruh digest
            continue

    # Urutkan terbaru dulu, batasi jumlah item mentah yang diteruskan ke Claude
    items.sort(key=lambda x: x["published"], reverse=True)
    return items[: config.NEWS_MAX_ITEMS]


def summarize_with_claude(raw_items: list) -> list:
    """Ringkas daftar berita mentah jadi beberapa bullet singkat & relevan.
    Return list of string (masing-masing 1 bullet). Fallback ke headline polos
    kalau ANTHROPIC_API_KEY tidak diset atau library tidak tersedia."""
    if not raw_items:
        return []

    if not config.ANTHROPIC_API_KEY or anthropic is None:
        # Fallback: headline apa adanya, tanpa AI
        return [f"{it['title']} ({it['source']})" for it in raw_items]

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    articles_text = "\n\n".join(
        f"- Judul: {it['title']}\n  Sumber: {it['source']}\n  Ringkasan asli: {it['summary'][:300]}"
        for it in raw_items
    )

    prompt = f"""Kamu membantu menyusun digest berita crypto harian untuk investor jangka panjang (DCA di BTC/ETH/SOL).

Dari daftar berita mentah di bawah, pilih maksimal 3-4 item PALING RELEVAN (dampak ke harga BTC/ETH/SOL atau makro global seperti Fed/regulasi), lalu tulis masing-masing sebagai 1 kalimat ringkas berbahasa Indonesia yang netral dan informatif (bukan clickbait, bukan rekomendasi beli/jual).

Format output: satu bullet per baris, mulai dengan "- ", tanpa embel-embel lain.

Berita mentah:
{articles_text}"""

    response = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    bullets = [line.strip("- ").strip() for line in text.splitlines() if line.strip().startswith("-")]
    return bullets if bullets else [text]


def get_news_digest() -> list:
    raw = fetch_raw_news()
    return summarize_with_claude(raw)


if __name__ == "__main__":
    for b in get_news_digest():
        print("-", b)
