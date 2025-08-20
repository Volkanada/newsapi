import feedparser, datetime

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

if __name__ == "__main__":
    news = get_news()
    with open("weekly_blog.md", "w", encoding="utf-8") as f:
        f.write("# Bu Haftanın Haberleri\n\n")
        for n in news[:7]:
            f.write(f"- {n['title']} ({n['link']})\n")
