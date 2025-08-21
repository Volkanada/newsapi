import feedparser, datetime, os, argparse
from openai import OpenAI

# OpenAI client başlat
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Kategorilere göre RSS kaynakları
CATEGORIES = {
    "oyunculuk": [
        "https://www.beyazperde.com/rss/diziler-haberleri.xml",
        "https://www.beyazperde.com/rss/filmler-haberleri.xml",
        "https://www.ranini.tv/rss"
    ],
    "cekim": [
        "https://www.campaigntr.com/feed/",
        "https://mediacat.com/feed/",
        "https://www.marketingturkiye.com.tr/feed/"
    ],
    "reklam": [
        "https://www.campaigntr.com/feed/",
        "https://mediacat.com/feed/",
        "https://www.marketingturkiye.com.tr/feed/"
    ],
    "influencers": [
        "https://sosyalmedyakulubu.com.tr/feed",
        "https://www.marketingturkiye.com.tr/feed/"
    ],
    "ai": [
    "https://openai.com/blog/rss",
    "https://stability.ai/blog/rss",
    "https://research.runwayml.com/feed.xml",
    "https://huggingface.co/blog/feed.xml",
    "https://ai.googleblog.com/feeds/posts/default?alt=rss",
    "https://www.webrazzi.com/feed/"  # Türkiye için tek kalsın
    ],
    "muzik": [
        "https://www.aa.com.tr/tr/rss/kultur-sanat",
        "https://www.ntv.com.tr/sanat.rss",
        "https://bantmag.com/feed/"
    ]
}

def get_news(feeds, days=1, limit=15):
    """RSS feedlerinden haberleri çek"""
    items = []
    since = datetime.datetime.now() - datetime.timedelta(days=days)
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = getattr(entry, "published_parsed", None)
            if published:
                pub_date = datetime.datetime(*published[:6])
                if pub_date < since:
                    continue
            items.append({"title": entry.title, "link": entry.link})
    return items[:limit]

def write_blog(news_items, category):
    headlines = "\n".join([f"- {n['title']} ({n['link']})" for n in news_items])

    # Prompt (özellikle AI kategorisi için özel filtre talimatı var)
    prompt = f"""
Aşağıdaki {category} haber başlıklarını değerlendir. 

- Sadece **yapay zekânın sanat, görsel, video, ses, oyunculuk, müzik, içerik üretimindeki uygulamaları** hakkında olanları seç. 
- Donanım, cihaz, telefon, araba vb. tüketici ürünlerini içeren haberleri dahil etme. 
- Seçilen her haberi haber diliyle 1-2 paragraf halinde yaz. 
- Eğer haberde demo linki veya YouTube linki varsa, onu mutlaka koru ve yazıya ekle. 

Her haberin sonunda kaynağı şu formatta belirt:
(kaynak: link)

Toplam uzunluk 600-800 kelime olsun.

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
    parser.add_argument("--category", required=True, help="Kategori seç (oyunculuk, cekim, reklam, influencers, ai, muzik)")
    args = parser.parse_args()

    feeds = CATEGORIES.get(args.category)
    if not feeds:
        raise ValueError("Geçersiz kategori seçildi!")

    news = get_news(feeds)
    blog_text = write_blog(news[:7], args.category)

    filename = f"daily_{args.category}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(blog_text)
