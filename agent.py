import feedparser, datetime, os
from openai import OpenAI

# OpenAI client başlat
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Haber kaynakları
RSS_FEEDS = [
    "https://www.beyazperde.com/rss/diziler-haberleri.xml",
    "https://www.aa.com.tr/tr/teyithatti/rss/news?cat=kultur-sanat",
    "https://www.marketingturkiye.com.tr/feed/",
    "https://mediacat.com/feed/",
    "https://www.webrazzi.com/feed/",
    "https://www.log.com.tr/feed"
]

def get_news():
    items = []
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published = getattr(entry, "published_parsed", None)
            if published:
                pub_date = datetime.datetime(*published[:6])
                if pub_date < one_week_ago:
                    continue
            items.append({"title": entry.title, "link": entry.link})
    return items[:20]

def write_blog(news_items):
    headlines = "\n".join([f"- {n['title']} ({n['link']})" for n in news_items])
    prompt = f"""
    Aşağıdaki haber başlıklarını kullanarak Actingo için SEO uyumlu,
    1 haftalık blog yazısı hazırla (800-1000 kelime). 
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
    news = get_news()
    blog_text = write_blog(news[:7])  # 7 haber seç
    with open("weekly_blog.md", "w", encoding="utf-8") as f:
        f.write(blog_text)
