# src/config.py

SOURCE_CONFIGS = [
    {
        "id": "zhitong_news",
        "name": "智通財經_港股新聞",
        # 🚨 修正：拿掉無效的分頁參數
        "url": "https://www.zhitongcaijing.com/?index=ganggu",
        "wait_selector": None,
        "target_css": ".list-item a, .article-item a, .recommend-article-list a, div.content-wrap a, div.res-list a, .news-list a",
        "is_flash": False,
        "pages_to_scrape": 1,  # 🚨 修正：1 頁就有 33 條，對高頻監控已足夠
        "fetcher_type": "stealth" 
    },
    {
        "id": "zhitong_7x24",
        "name": "智通財經_7x24快訊",
        "url": "https://www.zhitongcaijing.com/immediately.html?type=ganggu",
        "wait_selector": "div.allday-item-content", 
        "target_css": "div.allday-item-content",    
        "is_flash": True,
        "pages_to_scrape": 1,  
        "fetcher_type": "dynamic"
    }
]
