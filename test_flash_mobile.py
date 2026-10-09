# test_api_flash.py
import json
import logging
import re
from urllib.parse import urljoin
from scrapling.fetchers import StealthyFetcher

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("FlashAPI")

def get_40_flash():
    base_url = "https://www.zhitongcaijing.com"
    first_page_url = f"{base_url}/immediately.html?type=ganggu"
    
    logger.info("=" * 60)
    logger.info("🚀 正在抓取智通財經 7x24 快訊（目標：40 條）")
    logger.info("=" * 60)
    
    # 1. 抓取首頁純 HTML（秒開，含前 20 條）
    logger.info("📥 正在獲取第一批快訊（前 20 條）...")
    page = StealthyFetcher.fetch(first_page_url, headless=True)
    
    items = []
    
    # 提取前 20 條
    dom_items = page.css("div.allday-item-content")
    for el in dom_items:
        text = "".join(el.xpath(".//text()").getall()).strip()
        text = text.replace("编辑解读", "").replace("添加解读", "").strip()
        if len(text) > 15:
            items.append(text)
            
    logger.info(f"✅ 第一批成功萃取: {len(items)} 條")
    
    # 2. 從 HTML 中抓取翻頁的時間戳記 data-page
    # <div class="allday-box" ... data-page="1791545266" ...>
    allday_box = page.css("div.allday-box")
    last_timestamp = None
    if allday_box:
        last_timestamp = allday_box[0].attrib.get("data-page")
        
    if not last_timestamp:
        # 正則保底搜尋
        match = re.search(r'data-page="(\d+)"', page.text)
        if match:
            last_timestamp = match.group(1)
            
    logger.info(f"🔑 取得第二頁時間戳記 (last_update_time): {last_timestamp}")
    
    # 3. 呼叫底層 API 取得第 21～40 條
    if last_timestamp:
        api_url = f"{base_url}/immediately/content-list.html?type=ganggu&last_update_time={last_timestamp}"
        logger.info(f"📡 正在請求第二批 API: {api_url}")
        
        api_res = StealthyFetcher.fetch(api_url, headless=True)
        try:
            data = json.loads(api_res.text)
            # 依據 JS 結構：data[1].list
            news_list = []
            if isinstance(data, list) and len(data) > 1 and "list" in data[1]:
                news_list = data[1]["list"]
            elif isinstance(data, dict) and "data" in data:
                news_list = data["data"]
                
            for item in news_list:
                # 移除 HTML 標籤
                content = item.get("content", "")
                clean_content = re.sub(r'<[^>]+>', '', content).strip()
                if clean_content:
                    items.append(clean_content)
                    
            logger.info(f"✅ 第二批 API 成功追加: {len(news_list)} 條")
        except Exception as e:
            logger.error(f"❌ 解析 API 失敗: {e}")
            
    logger.info("=" * 60)
    logger.info(f"🎉 總共抓取到: {len(items)} 條快訊！")
    logger.info("=" * 60)
    logger.info("📋 [新聞清單預覽]:")
    for idx, title in enumerate(items[:40], 1):
        logger.info(f"[{idx:02d}] {title[:60]}...")

if __name__ == "__main__":
    get_40_flash()
