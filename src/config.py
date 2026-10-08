# src/config.py

SOURCE_CONFIGS = [
    {
        "id": "zhitong_news",
        "name": "智通財經_港股新聞",
        # 🚨 URL 改為模板格式，加入 {page} 讓爬蟲可以翻頁
        "url": "https://www.zhitongcaijing.com/?index=ganggu&page={page}",
        "wait_selector": ".list-item a, .news-list a",
        "target_css": ".list-item a, .news-list a",
        "is_flash": False,
        "pages_to_scrape": 2,  # 🚨 設定抓取深度：例如抓取前 2 頁，防止資料缺失
    },
    {
        "id": "zhitong_7x24",
        "name": "智通財經_7x24快訊",
        # 7x24 頁面不支援 URL 翻頁，所以 {page} 參數在這邊不會影響，設定只抓 1 頁
        "url": "https://www.zhitongcaijing.com/immediately.html?type=ganggu",
        "wait_selector": "div.allday-item-content", 
        "target_css": "div.allday-item-content",    
        "is_flash": True,
        "pages_to_scrape": 1,  
    }
]
