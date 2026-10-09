import random
import time
from urllib.parse import urljoin
from curl_cffi import requests
from bs4 import BeautifulSoup
from scrapling.fetchers import StealthyFetcher

# -------------------------- 配置 --------------------------
MAX_PAGE = 3
SLEEP_MIN = 0.5
SLEEP_MAX = 1.2

def fetch_zhitong_mobile(page_num: int):
    """手機版 curl_cffi 抓取"""
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


def trigger_page_2(page):
    """Scrapling PC版 page_action 模擬加載更多"""
    page.wait_for_timeout(2500)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)
    load_more = page.locator("text='加载更多'")
    if load_more.count() > 0 and load_more.first.is_visible():
        print("[PC page_action] 點擊加載更多")
        load_more.first.click()
        page.wait_for_timeout(3500)
    else:
        print("[PC page_action] 二次滾動觸發")
        page.evaluate("window.scrollBy(0, -300)")
        page.wait_for_timeout(500)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)


def fetch_zhitong_pc_fallback():
    """Fallback：PC版 Scrapling 抓取（含加載更多）"""
    target_url = "https://www.zhitongcaijing.com/?index=ganggu"
    try:
        response = StealthyFetcher.fetch(
            target_url,
            page_action=trigger_page_2,
            timeout=45000,
            headless=True
        )
        selectors = [
            "div.res-list a",
            ".news-item a",
            "div.content-box a",
            ".item-title a",
        ]
        all_news = []
        for sel in selectors:
            elements = response.css(sel)
            for el in elements:
                title = el.css("::text").get() or ""
                title = title.strip()
                href = el.css("::attr(href)").get() or ""
                href = href.strip()
                if len(title) < 5 or not href or href.startswith("javascript:"):
                    continue
                full_link = urljoin(target_url, href)
                all_news.append({
                    "title": title,
                    "link": full_link,
                    "source": "智通財經"
                })
            if len(all_news) >= 15:
                break
        return all_news
    except Exception as e:
        print(f"[PC FALLBACK] 抓取失敗: {str(e)}")
        return []


def scrape_zhitong():
    """主入口：優先手機版，失敗回退PC版"""
    all_news = []
    seen_links = set()
    print("=== 開始抓取智通財經【優先手機版】 ===")

    for p in range(1, MAX_PAGE + 1):
        page_data = fetch_zhitong_mobile(p)
        for n in page_data:
            if n["link"] not in seen_links:
                seen_links.add(n["link"])
                all_news.append(n)
        time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))

    # 如果手機版返回太少，觸發 fallback PC版
    if len(all_news) < 5:
        print(f"[WARN] 手機版獲取新聞過少({len(all_news)}條)，切換PC版fallback")
        pc_data = fetch_zhitong_pc_fallback()
        for n in pc_data:
            if n["link"] not in seen_links:
                seen_links.add(n["link"])
                all_news.append(n)

    print(f"=== 智通抓取完成，總共 {len(all_news)} 條新聞 ===")
    return all_news


if __name__ == "__main__":
    news_result = scrape_zhitong()
    for idx, item in enumerate(news_result[:10], 1):
        print(f"{idx}. {item['title']} -> {item['link']}")
