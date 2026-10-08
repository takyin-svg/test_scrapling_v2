# src/scraper.py
import hashlib
import logging
import random
import time
from urllib.parse import urljoin
from scrapling.fetchers import DynamicSession, StealthyFetcher

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("ScraperV3")

class ScraperV3:
    def __init__(self, config_list):
        self.configs = config_list
        self.noise_words = ["编辑解读", "添加解读", "查看解读", "\n", "\r"]
        self.discard_words = ["登入", "登錄", "login", "register", "首頁", "下載", "版權所有"]

    def clean_text(self, raw_text: str) -> str:
        if not raw_text: return ""
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
        
        for source_idx, cfg in enumerate(self.configs):
            source_name = cfg["name"]
            pages_to_scrape = cfg.get("pages_to_scrape", 1)
            fetcher_type = cfg.get("fetcher_type", "dynamic")
            
            logger.info(f"🚀 開始抓取: [{source_name}] (模式: {fetcher_type.upper()}, 深度: {pages_to_scrape} 頁)")

            # --- 將翻頁與解析邏輯獨立出來，避免代碼重複 ---
            def _scrape_pages(fetch_func):
                source_news = []
                seen_links = set() # 🚨 已經移到翻頁迴圈外部，確保跨頁去重機制生效！
                
                for page_num in range(1, pages_to_scrape + 1):
                    target_url = cfg["url"].format(page=page_num) if "{page}" in cfg["url"] else cfg["url"]
                    
                    try:
                        logger.info(f"   -> 正在加載第 {page_num} 頁...")
                        page = fetch_func(target_url)
                        elements = page.css(cfg["target_css"])
                        
                        valid_items = []
                        
                        for el in elements:
                            raw_title = el.xpath(".//text()").getall() 
                            title = self.clean_text("".join(raw_title))
                            
                            if not self.is_valid_news(title): continue
                            
                            if cfg.get("is_flash"):
                                content_hash = hashlib.md5(title.encode('utf-8')).hexdigest()[:10]
                                full_url = f"{cfg['url']}#flash_{content_hash}"
                            else:
                                raw_href = el.attrib.get("href", "") if el.attrib else ""
                                if not raw_href or raw_href.startswith("javascript:"): continue
                                full_url = urljoin(cfg["url"], raw_href)
                                
                            if full_url not in seen_links:
                                seen_links.add(full_url)
                                valid_items.append({
                                    "source": source_name,
                                    "title": title,
                                    "link": full_url
                                })
                        
                        source_news.extend(valid_items)
                        
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
                return source_news
            # -----------------------------------------------

            # 🚨 嚴格隔離兩種爬蟲引擎，避免 Event Loop 衝突
            if fetcher_type == "stealth":
                # 狙擊槍模式：在乾淨環境下執行，不啟動 DynamicSession
                all_news.extend(_scrape_pages(lambda url: StealthyFetcher.fetch(url, headless=True)))
            else:
                # 坦克模式：針對動態網站，才在此刻啟動重量級會話
                with DynamicSession(headless=True, stealth=True, timeout=60000) as sess:
                    fetch_kwargs = {}
                    if cfg.get("wait_selector"):
                        fetch_kwargs["wait_selector"] = cfg["wait_selector"]
                        
                    all_news.extend(_scrape_pages(lambda url: sess.fetch(url, **fetch_kwargs)))
            
            # 源頭切換間的禮貌延遲
            if source_idx < len(self.configs) - 1:
                time.sleep(random.uniform(4, 7))
                    
        return all_news
