# test_flash_mobile.py
import json
import logging
import re
from scrapling.fetchers import DynamicSession

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("FlashAPI")

def get_40_flash():
    base_url = "https://www.zhitongcaijing.com"
    first_page_url = f"{base_url}/immediately.html?type=ganggu"
    
    logger.info("=" * 60)
    logger.info("🚀 正在抓取智通財經 7x24 快訊（目標：40 條）")
    logger.info("=" * 60)
    
    items = []
    
    # 1. 使用已驗證穩定的 DynamicSession 載入首頁並取得前 20 條
    with DynamicSession(headless=True, stealth=True, timeout=60000) as sess:
        logger.info("📥 正在透過 DynamicSession 載入首頁...")
        page = sess.fetch(first_page_url, wait_selector="div.allday-item-content")
        
        dom_items = page.css("div.allday-item-content")
        for el in dom_items:
            raw_text = "".join(el.xpath(".//text()").getall()).strip()
            clean_text = raw_text.replace("编辑解读", "").replace("添加解读", "").strip()
            if len(clean_text) > 15:
                items.append(clean_text)
                
        logger.info(f"✅ 第一批（首頁 SSR）成功取得: {len(items)} 條")
        
        # 2. 取得第二頁的翻頁時間戳記 (data-page)
        allday_box = page.css("div.allday-box")
        last_timestamp = None
        if allday_box and "data-page" in allday_box[0].attrib:
            last_timestamp = allday_box[0].attrib["data-page"]
            
        if not last_timestamp:
            match = re.search(r'data-page="(\d+)"', page.text)
            if match:
                last_timestamp = match.group(1)
                
        logger.info(f"🔑 取得第二頁時間戳記: {last_timestamp}")
        
        # 3. 沿用同一個 session 請求後續 API（自動帶有 Cookie 與 Session 狀態）
        if last_timestamp:
            api_url = f"{base_url}/immediately/content-list.html?type=ganggu&last_update_time={last_timestamp}"
            logger.info(f"📡 正在請求 API 獲取第 21~40 條: {api_url}")
            
            api_res = sess.fetch(api_url)
            try:
                # 解析 API 回傳的 JSON
                data = json.loads(api_res.text)
                news_list = []
                if isinstance(data, list) and len(data) > 1 and "list" in data[1]:
                    news_list = data[1]["list"]
                elif isinstance(data, dict) and "data" in data:
                    news_list = data["data"]
                    
                for item in news_list:
                    raw_content = item.get("content", "")
                    clean_content = re.sub(r'<[^>]+>', '', raw_content).strip()
                    clean_content = clean_content.replace("编辑解读", "").replace("添加解读", "").strip()
                    if clean_content and len(clean_content) > 15:
                        items.append(clean_content)
                        
                logger.info(f"✅ 第二批（API 請求）追加成功: {len(news_list)} 條")
            except Exception as e:
                logger.error(f"❌ 解析 API 失敗: {e}")

    logger.info("=" * 60)
    logger.info(f"🎉 總共抓取到: {len(items)} 條快訊！")
    logger.info("=" * 60)
    logger.info("📋 [新聞清單完整預覽]:")
    for idx, title in enumerate(items[:40], 1):
        logger.info(f"[{idx:02d}] {title[:65]}...")

if __name__ == "__main__":
    get_40_flash()
