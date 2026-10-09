# test_flash_mobile.py
import json
import logging
import re
from scrapling.fetchers import DynamicSession

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("FlashFastTest")

def fetch_extra_via_js(page):
    """
    自訂 page_action:
    完全不滾動！直接調用智通財經網頁自帶的 window.GET 函式，
    由瀏覽器核心在內部發起請求，秒級獲取後續 20 條資料並注入全域變數中。
    """
    logger.info("⏳ [page_action] 等待首頁節點載入...")
    page.wait_for_selector("div.allday-item-content", timeout=30000)
    
    # 1. 取得翻頁時間戳記
    timestamp = page.evaluate("""() => {
        const box = document.querySelector('div.allday-box');
        return box ? box.getAttribute('data-page') : null;
    }""")
    logger.info(f"🔑 [page_action] 瀏覽器內取得時間戳記: {timestamp}")
    
    # 2. 如果拿到時間戳記，直接調用原生的 window.GET 請求第二批資料
    if timestamp:
        logger.info("⚡ [page_action] 直接執行網頁原生 window.GET 拉取第二批（免滾動等待）...")
        page.evaluate(f"""async () => {{
            window.__EXTRA_NEWS__ = [];
            try {{
                const res = await window.GET("/immediately/content-list.html?type=ganggu", {{
                    last_update_time: "{timestamp}"
                }});
                if (res && res[1] && res[1].list) {{
                    window.__EXTRA_NEWS__ = res[1].list;
                }}
            }} catch (e) {{
                console.error("fetch error", e);
            }}
        }}""")

def get_40_flash():
    target_url = "https://www.zhitongcaijing.com/immediately.html?type=ganggu"
    target_count = 40
    
    logger.info("=" * 60)
    logger.info(f"🚀 開始測試：智通財經 7x24 快訊（原生 JS 直取 40 條，免滾動）")
    logger.info("=" * 60)
    
    items = []
    seen_texts = set()
    
    with DynamicSession(headless=True, stealth=True, timeout=60000) as sess:
        response = sess.fetch(
            target_url,
            wait_selector="div.allday-item-content",
            page_action=fetch_extra_via_js
        )
        
        # 1. 提取首頁原本的 20 條 (SSR)
        elements = response.css("div.allday-item-content")
        for el in elements:
            raw_text = "".join(el.xpath(".//text()").getall()).strip()
            clean_text = raw_text.replace("编辑解读", "").replace("添加解读", "").strip()
            if len(clean_text) > 15 and clean_text not in seen_texts:
                seen_texts.add(clean_text)
                items.append(clean_text)
                
        logger.info(f"✅ 第一批（首頁原生）取得: {len(items)} 條")
        
        # 2. 直接從瀏覽器取出剛才 JS 拉回來的第二批資料 (API)
        extra_list = sess.page.evaluate("() => window.__EXTRA_NEWS__ || []")
        logger.info(f"📦 第二批（原生 JS 直取）回傳: {len(extra_list)} 條原始資料")
        
        for item in extra_list:
            raw_content = item.get("content", "")
            # 去除 HTML tag
            clean_content = re.sub(r'<[^>]+>', '', raw_content).strip()
            clean_content = clean_content.replace("编辑解读", "").replace("添加解读", "").strip()
            if len(clean_content) > 15 and clean_content not in seen_texts:
                seen_texts.add(clean_content)
                items.append(clean_content)
                
            if len(items) >= target_count:
                break

    logger.info("=" * 60)
    logger.info(f"🎉 抓取成功！去重後總共取得: {len(items)} 條快訊！")
    logger.info("=" * 60)
    logger.info("📋 [新聞清單完整預覽]:")
    for idx, title in enumerate(items[:40], 1):
        logger.info(f"[{idx:02d}] {title[:65]}...")

if __name__ == "__main__":
    get_40_flash()
