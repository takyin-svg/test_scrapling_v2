SOURCE_CONFIGS = [
    {
        "id": "zhitong_news",
        "name": "智通財經_港股新聞",
        "url": "https://www.zhitongcaijing.com/?index=ganggu",
        "wait_selector": ".news-item",
        "target_css": ".news-item .title a",
        "is_flash": False,
        "pages_to_scrape": 2, 
        # 新增翻頁按鈕選擇器
        "next_page_selector": ".pagination li.next a",
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
