# test_flash_mobile.py
import hashlib
import logging
import time
from scrapling.fetchers import StealthyFetcher

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("MobileFlashTest")

def scroll_mobile_page(page):
    """
    手機版專用滾動：
    模擬手機螢幕向下滑動，觸發動態加載更多快訊
    """
    logger.info("⏳ [page_action] 等待首頁內容加載...")
    page.wait_for_timeout(2500)
    
    # 第一次向下滑動
    logger.info("📜 [page_action] 第一次滾動觸發加載...")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2500)
    
    # 第二次向下滑動，確保拉取到 40 條以上
    logger.info("📜 [page_action] 第二次滾動確保獲取 40 條...")
    page.evaluate("window.scrollBy(0, -200)")
    page.wait_for_timeout(400)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(3000)

def run_test():
    # 🚨 明確使用 m.zhitongcaijing.com 手機版網址
    target_url = "https://m.zhitongcaijing.com/immediately.html?type=ganggu"
    target_count = 40
    noise_words = ["编辑解读", "添加解读", "查看解读", "\n", "\r", "\t"]
    
    logger.info("=" * 60)
    logger.info("📱 開始測試：智通財經【手機版 7x24 快訊】")
    logger.info(f"🎯 目標 URL: {target_url}")
    logger.info(f"🎯 目標擷取條數: {target_count} 條")
    logger.info("=" * 60)

    try:
        # 使用手機版專屬的 StealthyFetcher
        response = StealthyFetcher.fetch(
            target_url,
            headless=True,
            timeout=45000,
            page_action=scroll_mobile_page
        )
        
        # 手機版快訊常見的節點選擇器
        elements = response.css(".content-text, .allday-item-content, .item-content, .news-list p")
        logger.info(f"🔍 匹配到的 DOM 節點數量: {len(elements)}")
        
        valid_items = []
        seen_hashes = set()
        
        for el in elements:
            raw_text_list = el.xpath(".//text()").getall()
            text = "".join(raw_text_list).strip()
            
            for nw in noise_words:
                text = text.replace(nw, "")
            text = text.strip()
            
            # 過濾過短字串或導航雜訊
            if len(text) < 15 or "下載APP" in text or "點擊查看" in text:
                continue
                
            content_hash = hashlib.md5(text.encode('utf-8')).hexdigest()[:10]
            if content_hash in seen_hashes:
                continue
                
            seen_hashes.add(content_hash)
            valid_items.append({
                "id": content_hash,
                "title": text,
                "link": f"{target_url}#flash_{content_hash}"
            })
            
            if len(valid_items) >= target_count:
                break
                
        logger.info("=" * 60)
        logger.info(f"🎉 萃取完成！手機版共取得 {len(valid_items)} 條快訊。")
        logger.info("=" * 60)
        logger.info("📋 [抓取內容全清單預覽]:")
        
        for idx, item in enumerate(valid_items, 1):
            logger.info(f"[{idx:02d}] {item['title']}")
            
    except Exception as e:
        logger.error(f"❌ 手機版快訊測試失敗: {e}", exc_info=True)

if __name__ == "__main__":
    run_test()
