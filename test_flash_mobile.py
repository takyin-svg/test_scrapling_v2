# test_flash_mobile.py
import logging
import re
from scrapling.fetchers import DynamicSession

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("FlashFastTest")

def get_40_flash():
    target_url = "https://www.zhitongcaijing.com/immediately.html?type=ganggu"
    target_count = 40
    
    logger.info("=" * 60)
    logger.info("🚀 開始測試：智通財經 7x24 快訊（原生 JS 直取 40 條，免滾動）")
    logger.info("=" * 60)
    
    items = []
    seen_texts = set()

    def fetch_via_page_action(page):
        """
        在 page_action 內部直接持有 page 物件，完成：
        1. 等待節點
        2. 抓取時間戳記
        3. 調用原生 window.GET 抓取第二批資料
        """
        logger.info("⏳ [page_action] 等待首頁節點載入...")
        page.wait_for_selector("div.allday-item-content", timeout=30000)
        
        # 1. 取得時間戳記
        timestamp = page.evaluate("""() => {
            const box = document.querySelector('div.allday-box');
            return box ? box.getAttribute('data-page') : null;
        }""")
        logger.info(f"🔑 [page_action] 瀏覽器內取得時間戳記: {timestamp}")
        
        # 2. 直接執行 window.GET 並直接把結果回傳給 Python
        if timestamp:
            logger.info("⚡ [page_action] 直接執行網頁原生 window.GET 拉取第二批（免滾動等待）...")
            extra_data = page.evaluate(f"""async () => {{
                try {{
                    const res = await window.GET("/immediately/content-list.html?type=ganggu", {{
                        last_update_time: "{timestamp}"
                    }});
                    if (res && res[1] && res[1].list) {{
                        return res[1].list;
                    }}
                }} catch (e) {{
                    return [];
                }}
                return [];
            }}""")
            
            logger.info(f"📦 [page_action] 原生 JS 直取回傳: {len(extra_data)} 條原始資料")
            for item in extra_data:
                raw_content = item.get("content", "")
                clean_content = re.sub(r'<[^>]+>', '', raw_content).strip()
                clean_content = clean_content.replace("编辑解读", "").replace("添加解读", "").strip()
                if len(clean_content) > 15 and clean_content not in seen_texts:
                    seen_texts.add(clean_content)
                    items.append(clean_content)

    with DynamicSession(headless=True, stealth=True, timeout=60000) as sess:
        response = sess.fetch(
            target_url,
            wait_selector="div.allday-item-content",
            page_action=fetch_via_page_action
        )
        
        # 提取首頁原本渲染的 20 條 (SSR)
        elements = response.css("div.allday-item-content")
        for el in elements:
            raw_text = "".join(el.xpath(".//text()").getall()).strip()
            clean_text = raw_text.replace("编辑解读", "").replace("添加解读", "").strip()
            if len(clean_text) > 15 and clean_text not in seen_texts:
                seen_texts.add(clean_text)
                items.append(clean_text)

    logger.info("=" * 60)
    logger.info(f"🎉 抓取成功！去重後總共取得: {len(items)} 條快訊！")
    logger.info("=" * 60)
    logger.info("📋 [新聞清單完整預覽]:")
    for idx, title in enumerate(items[:target_count], 1):
        logger.info(f"[{idx:02d}] {title[:65]}...")

if __name__ == "__main__":
    get_40_flash()
