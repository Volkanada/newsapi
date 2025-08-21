import feedparser, datetime, os, argparse
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CATEGORIES = {
    "oyunculuk": [
        "https://www.beyazperde.com/rss/diziler-haberleri.xml",
        "https://www.ranini.tv/rss"
    ],
    "dizifilm": [
        "https://www.beyazperde.com/rss/diziler-haberleri.xml"
    ],
    "cekim": [
        "https://www.campaigntr.com/feed/",
        "https://mediacat.com/feed/"
    ],
    "influencers": [
        "https://www.marketingturkiye.com.tr/feed/",
        "https://mediacat.com/feed/"
    ],
    "ai": [
        "https://www.webrazzi.com/feed/",
        "https://www.log.com.tr/feed"
    ],
    "reklam": [
        "https://www.campaigntr.com/feed/",
        "https://mediacat.com/feed/",
        "https://www.marketingturkiye.com.tr/feed/"
    ]
}

def get_news(feeds):
    items = []
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = getattr(entry, "published_parsed", None)
            if published:
                pub_date = datetime.datetime(*published[:6])
                if pub_date < one_day_ago:
                    continue
            items.append({"title": entry.title, "link": entry.link})
    return items[:15]

def write_blog(news_items, category):
    headlines = "\n".join([f"- {n['title']} ({n['link']})" for n in news_items])
    prompt = f"""
    Aşağıdaki {category} haber başlıklarını kullanarak Actingo için
    SEO uyumlu günlük blog yazısı hazırla (600-800 kelime).
    Giriş, gelişme ve sonuç bölümleri olsun.
    Başlıklar:
    {headlines}
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", required=True, help="Kategori seç (oyunculuk, dizifilm, cekim, influencers, ai, reklam)")
    args = parser.parse_args()

    feeds = CATEGORIES.get(args.category)
    if not feeds:
        raise ValueError("Geçersiz kategori seçildi!")

    news = get_news(feeds)
    blog_text = write_blog(news[:7], args.category)

    filename = f"daily_{args.category}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(blog_text)
