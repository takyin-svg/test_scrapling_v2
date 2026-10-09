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
    seen_texts = set()
    
    # 1. 透過 DynamicSession 載入首頁並取得前 20 條
    with DynamicSession(headless=True, stealth=True, timeout=60000) as sess:
        logger.info("📥 正在透過 DynamicSession 載入首頁...")
        page = sess.fetch(first_page_url, wait_selector="div.allday-item-content")
        
        dom_items = page.css("div.allday-item-content")
        for el in dom_items:
            raw_text = "".join(el.xpath(".//text()").getall()).strip()
            clean_text = raw_text.replace("编辑解读", "").replace("添加解读", "").strip()
            if len(clean_text) > 15 and clean_text not in seen_texts:
                seen_texts.add(clean_text)
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
        
        # 3. 請求第二批資料（直接按 HTML 片段與備用 JSON 解析）
        if last_timestamp:
            api_url = f"{base_url}/immediately/content-list.html?type=ganggu&last_update_time={last_timestamp}"
            logger.info(f"📡 正在請求 API 獲取第 21~40 條: {api_url}")
            
            # 帶上 AJAX 請求標頭
            api_res = sess.fetch(
                api_url,
                headers={"X-Requested-With": "XMLHttpRequest"}
            )
            
            res_text = api_res.text.strip()
            added_count = 0
            
            # 嘗試路徑 A: 回傳純 HTML 片段
            html_elements = api_res.css("div.allday-item-content, .allday-item")
            if html_elements:
                for el in html_elements:
                    raw_text = "".join(el.xpath(".//text()").getall()).strip()
                    clean_text = raw_text.replace("编辑解读", "").replace("添加解读", "").strip()
                    if len(clean_text) > 15 and clean_text not in seen_texts:
                        seen_texts.add(clean_text)
                        items.append(clean_text)
                        added_count += 1
                logger.info(f"✅ 第二批（HTML 片段解析）追加成功: {added_count} 條")
            else:
                # 嘗試路徑 B: 嘗試解析 JSON 結構
                try:
                    data = json.loads(res_text)
                    news_list = []
                    if isinstance(data, list) and len(data) > 1 and "list" in data[1]:
                        news_list = data[1]["list"]
                    elif isinstance(data, dict) and "data" in data:
                        news_list = data["data"]
                        
                    for item in news_list:
                        raw_content = item.get("content", "")
                        clean_content = re.sub(r'<[^>]+>', '', raw_content).strip()
                        clean_content = clean_content.replace("编辑解读", "").replace("添加解读", "").strip()
                        if len(clean_content) > 15 and clean_content not in seen_texts:
                            seen_texts.add(clean_content)
                            items.append(clean_content)
                            added_count += 1
                    logger.info(f"✅ 第二批（JSON 解析）追加成功: {added_count} 條")
                except Exception:
                    logger.warning(f"⚠️ 第二批資料前 200 字元預覽: {res_text[:200]}")

    logger.info("=" * 60)
    logger.info(f"🎉 總共抓取到: {len(items)} 條快訊！")
    logger.info("=" * 60)
    logger.info("📋 [新聞清單完整預覽]:")
    for idx, title in enumerate(items[:40], 1):
        logger.info(f"[{idx:02d}] {title[:65]}...")

if __name__ == "__main__":
    get_40_flash()
