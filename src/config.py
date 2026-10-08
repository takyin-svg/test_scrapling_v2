# src/config.py

SOURCE_CONFIGS = [
    {
        "id": "zhitong_news",
        "name": "智通財經_港股新聞",
        "url": "https://www.zhitongcaijing.com/?index=ganggu&page={page}",
        # 🚨 移除嚴格的 wait_selector，讓 Scrapling 自動判斷網頁載入
        "wait_selector": None,
        # 🚨 給它所有可能的候選名單，讓 adaptive 演算法自動命中
        "target_css": ".list-item a, .article-item a, .recommend-article-list a, div.res-list a, .news-list a",
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
