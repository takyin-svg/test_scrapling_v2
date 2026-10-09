import random
import time
from urllib.parse import urljoin
from curl_cffi import requests
from bs4 import BeautifulSoup

MAX_PAGE = 3
SLEEP_MIN = 0.5
SLEEP_MAX = 1.2

def fetch_zhitong_mobile(page_num: int):
    base_url = f"https://m.zhitongcaijing.com/market.html?page={page_num}"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept-Language": "zh‑CN,zh;q=0.9",
        "Referer": "https://m.zhitongcaijing.com/"
    }
    try:
        resp = requests.get(
            base_url,
            headers=headers,
            impersonate="safari17",
            timeout=20
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        news_list = []
        items = soup.select("ul.news-list li a")
        for item in items:
            title = item.get_text(strip=True)
            href = item.get("href", "")
            if not title or len(title) < 5 or not href:
                continue
            full_link = urljoin(base_url, href)
            news_list.append({
                "title": title,
                "link": full_link,
                "source": "智通財經"
            })
        return news_list
    except Exception as e:
        print(f"[MOBILE] page={page_num} 抓取異常: {str(e)}")
        return []


def scrape_zhitong():
    all_news = []
    seen_links = set()
    print("=== 開始抓取智通財經【手機版】 ===")

    for p in range(1, MAX_PAGE + 1):
        page_data = fetch_zhitong_mobile(p)
        for n in page_data:
            if n["link"] not in seen_links:
                seen_links.add(n["link"])
                all_news.append(n)
        time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))

    print(f"=== 智通抓取完成，總共 {len(all_news)} 條新聞 ===")
    return all_news


if __name__ == "__main__":
    news_result = scrape_zhitong()
    for idx, item in enumerate(news_result[:10], 1):
        print(f"{idx}. {item['title']} -> {item['link']}")
