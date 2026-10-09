import hashlib
import logging
import random
import time
from urllib.parse import urljoin
from scrapling.fetchers import DynamicSession

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("ScraperV3")


class ScraperV3:
    def __init__(self, config_list):
        self.configs = config_list
        self.noise_words = ["编辑解读", "添加解读", "查看解读", "\n", "\r"]
        self.discard_words = ["登入", "登錄", "login", "register", "首頁", "下載", "版權所有"]

    def clean_text(self, raw_text: str) -> str:
        if not raw_text:
            return ""
        txt = raw_text
        for w in self.noise_words:
            txt = txt.replace(w, "")
        return txt.strip()

    def is_valid_title(self, title: str) -> bool:
        if len(title) < 15:
            return False
        for w in self.discard_words:
            if w in title.lower():
                return False
        return True

    def parse_response(self, resp, source_name, base_url, is_flash, target_css):
        items = []
        seen = set()
        elements = resp.css(target_css)
        for el in elements:
            raw_title = "".join(el.xpath(".//text()").getall())
            title = self.clean_text(raw_title)
            if not self.is_valid_title(title):
                continue

            if is_flash:
                uid = hashlib.md5(title.encode("utf-8")).hexdigest()[:10]
                link = f"{base_url}#flash_{uid}"
            else:
                href = el.attrib.get("href", "")
                if not href or href.startswith("javascript:"):
                    continue
                link = urljoin(base_url, href)

            if link not in seen:
                seen.add(link)
                items.append({
                    "source": source_name,
                    "title": title,
                    "url": link
                })
        return items

    def fetch_all(self):
        all_news = []
        with DynamicSession(headless=True, timeout=60000) as sess:
            for cfg in self.configs:
                name = cfg["name"]
                url_tpl = cfg["url_template"]
                wait_sel = cfg["wait_selector"]
                target_sel = cfg["target_css"]
                pages_total = cfg.get("pages_to_scrape", 1)
                is_flash = cfg.get("is_flash", False)

                logger.info(f"🚀 開始抓取：{name}，計劃抓取 {pages_total} 頁")

                for page_num in range(1, pages_total + 1):
                    try:
                        # 替換page參數
                        if "{page}" in url_tpl:
                            target_url = url_tpl.format(page=page_num)
                        else:
                            target_url = url_tpl

                        logger.info(f"   -> 訪問: {target_url}")
                        resp = sess.fetch(target_url, wait_selector=wait_sel)
                        news = self.parse_response(resp, name, target_url, is_flash, target_sel)
                        all_news.extend(news)
                        logger.info(f"✅ {name} 第 {page_num} 頁，撈到 {len(news)} 條新聞")
                        if news:
                            for item in news[:3]:
                                logger.info(f"    - {item['title']}")

                        if page_num < pages_total:
                            time.sleep(random.uniform(2, 4))
                    except Exception as e:
                        logger.error(f"❌ {name} 第 {page_num} 頁失敗：{str(e)[:120]}")
                        break
        return all_news
