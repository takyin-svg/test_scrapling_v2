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
        text = raw_text
        for nw in self.noise_words:
            text = text.replace(nw, "")
        return text.strip()

    def is_valid_news(self, title: str) -> bool:
        if len(title) < 15:
            return False
        if any(w in title.lower() for w in self.discard_words):
            return False
        return True

    def fetch_all(self):
        all_news = []

        with DynamicSession(headless=True, stealth=True, timeout=60000) as sess:
            # sess.page 是底層 Playwright Page，用來做點擊互動
            page = sess.page
            for source_idx, cfg in enumerate(self.configs):
                source_name = cfg["name"]
                pages_to_scrape = cfg.get("pages_to_scrape", 1)
                next_sel = cfg.get("next_page_selector")
                is_pagination_click = bool(next_sel)
                wait_sel = cfg.get("wait_selector")

                logger.info(f"🚀 開始抓取: [{source_name}] (目標深度: {pages_to_scrape} 頁)")

                if is_pagination_click:
                    # ========== 點擊翻頁模式（智通港股列表）==========
                    try:
                        logger.info(f"   -> 載入首頁 {cfg['url']}")
                        page.goto(cfg["url"], timeout=60000)
                        # 等待目標區塊出現
                        if wait_sel:
                            page.wait_for_selector(wait_sel, timeout=60000)

                        for page_num in range(1, pages_to_scrape + 1):
                            logger.info(f"   -> 正在萃取第 {page_num} 頁...")
                            # 取得當前頁面 HTML，交由 Scrapling parse
                            html = page.content()
                            current_page = sess.get_response(html_content=html)

                            elements = current_page.css(cfg["target_css"])
                            valid_items = []
                            seen_links = set()

                            for el in elements:
                                raw_title = el.xpath(".//text()").getall()
                                title = self.clean_text("".join(raw_title))
                                if not self.is_valid_news(title):
                                    continue

                                if cfg.get("is_flash"):
                                    content_hash = hashlib.md5(title.encode('utf-8')).hexdigest()[:10]
                                    full_url = f"{cfg['url']}#flash_{content_hash}"
                                else:
                                    raw_href = el.attrib.get("href", "") if el.attrib else ""
                                    if not raw_href or raw_href.startswith("javascript:"):
                                        continue
                                    full_url = urljoin(cfg["url"], raw_href)

                                if full_url not in seen_links:
                                    seen_links.add(full_url)
                                    valid_items.append({
                                        "source": source_name,
                                        "title": title,
                                        "link": full_url
                                    })

                            all_news.extend(valid_items)
                            logger.info(f"   ✅ 第 {page_num} 頁萃取完成，共 {len(valid_items)} 條有效新聞。")
                            if valid_items:
                                logger.info("   👀 [資料預覽]:")
                                for item in valid_items[:3]:
                                    short_title = item['title'][:45] + "..." if len(item['title']) > 45 else item['title']
                                    logger.info(f"      - [{item['source']}] {short_title}")

                            # 不是最後一頁，點擊下一頁
                            if page_num < pages_to_scrape:
                                logger.info(f"   ⏳ 準備點擊下一頁按鈕 {next_sel}")
                                time.sleep(random.uniform(2, 4))
                                # 使用 playwright page 點擊，不是 response.click
                                page.wait_for_selector(next_sel, timeout=15000)
                                page.click(next_sel)
                                # 點擊後等待新聞區塊重新渲染
                                page.wait_for_selector(wait_sel, timeout=60000)
                                time.sleep(random.uniform(1,2))
                    except Exception as e:
                        logger.error(f"❌ [{source_name}] 翻頁流程異常: {str(e)[:150]}")
                        continue

                else:
                    # ========== 原始 fetch 模式（7x24快訊，不變）==========
                    for page_num in range(1, pages_to_scrape + 1):
                        target_url = cfg["url"].format(page=page_num) if "{page}" in cfg["url"] else cfg["url"]
                        try:
                            logger.info(f"   -> 正在加載第 {page_num} 頁...")
                            fetch_kwargs = {}
                            if cfg.get("wait_selector"):
                                fetch_kwargs["wait_selector"] = cfg["wait_selector"]
                            current_page = sess.fetch(target_url,** fetch_kwargs)

                            elements = current_page.css(cfg["target_css"])
                            valid_items = []
                            seen_links = set()

                            for el in elements:
                                raw_title = el.xpath(".//text()").getall()
                                title = self.clean_text("".join(raw_title))
                                if not self.is_valid_news(title):
                                    continue

                                if cfg.get("is_flash"):
                                    content_hash = hashlib.md5(title.encode('utf-8')).hexdigest()[:10]
                                    full_url = f"{cfg['url']}#flash_{content_hash}"
                                else:
                                    raw_href = el.attrib.get("href", "") if el.attrib else ""
                                    if not raw_href or raw_href.startswith("javascript:"):
                                        continue
                                    full_url = urljoin(cfg["url"], raw_href)

                                if full_url not in seen_links:
                                    seen_links.add(full_url)
                                    valid_items.append({
                                        "source": source_name,
                                        "title": title,
                                        "link": full_url
                                    })

                            all_news.extend(valid_items)
                            logger.info(f"   ✅ 第 {page_num} 頁萃取完成，共 {len(valid_items)} 條有效新聞。")
                            if valid_items:
                                logger.info("   👀 [資料預覽]:")
                                for item in valid_items[:3]:
                                    short_title = item['title'][:45] + "..." if len(item['title']) > 45 else item['title']
                                    logger.info(f"      - [{item['source']}] {short_title}")

                            if page_num < pages_to_scrape:
                                time.sleep(random.uniform(2, 4))
                        except Exception as e:
                            logger.error(f"❌ [{source_name}] 第 {page_num} 頁抓取失敗: {str(e)[:100]}")
                            break

                if source_idx < len(self.configs) - 1:
                    time.sleep(random.uniform(4, 7))

        return all_news
