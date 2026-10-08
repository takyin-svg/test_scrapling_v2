# src/config.py

SOURCE_CONFIGS = [
    {
        "id": "zhitong_news",
        "name": "智通財經_港股新聞",
        "url": "https://www.zhitongcaijing.com/?index=ganggu&page={page}",
        "wait_selector": None,
        # 覆蓋所有可能的列表標籤
        "target_css": ".list-item a, .article-item a, .recommend-article-list a, div.content-wrap a, div.res-list a, .news-list a",
        "is_flash": False,
        "pages_to_scrape": 2,
        # 🚨 關鍵升級：指定使用輕量級純 HTML 隱匿請求
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
        # 🚨 關鍵升級：指定使用重量級無頭瀏覽器
        "fetcher_type": "dynamic"
    }
]
