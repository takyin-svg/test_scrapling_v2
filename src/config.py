# src/config.py

SOURCE_CONFIGS = [
    {
        "id": "zhitong_news",
        "name": "智通財經_港股新聞",
        "url": "https://www.zhitongcaijing.com/?index=ganggu&page={page}",
        # 🚨 修正：強制等待新聞區塊出現
        "wait_selector": ".news-item",
        # 🚨 修正：直擊新聞標題與連結所在的 a 標籤
        "target_css": ".news-item .title a",
        "is_flash": False,
        "pages_to_scrape": 2, 
    },
    {
        "id": "zhitong_7x24",
        "name": "智通財經_7x24快訊",
        "url": "https://www.zhitongcaijing.com/immediately.html?type=ganggu",
        "wait_selector": "div.allday-item-content", 
        "target_css": "div.allday-item-content",    
        "is_flash": True,
        "pages_to_scrape": 1,  
    }
]
