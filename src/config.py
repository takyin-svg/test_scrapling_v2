# src/config.py

SOURCE_CONFIGS = [
    {
        "id": "zhitong_news",
        "name": "智通財經_港股新聞",
        "url": "https://www.zhitongcaijing.com/?index=ganggu&page={page}",
        # 🚨 修正 1：還原 V2 成功過的標籤，用逗號隔開 (OR 邏輯)。只要出現其中一種，就解除等待！
        "wait_selector": ".list-item, .article-item, .recommend-article-list, .news-list",
        # 🚨 修正 2：對應的目標 CSS 也用逗號串聯，一網打盡
        "target_css": ".list-item a, .article-item a, .recommend-article-list a, .news-list a",
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
