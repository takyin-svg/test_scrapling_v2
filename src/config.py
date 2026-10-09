CONFIGS = [
    {
        "name": "智通港股新聞",
        "url": "https://www.zhitongcaijing.com/?index=ganggu",
        "wait_selector": ".news-item",
        "target_css": ".news-item .title a",
        "pages_to_scrape": 2,
        "next_selector": ".pagination li.next a",
        "is_flash": False
    },
    {
        "name": "智通7x24快訊",
        "url": "https://www.zhitongcaijing.com/immediately.html",
        "wait_selector": "div.allday-item-content",
        "target_css": "div.allday-item-content",
        "pages_to_scrape": 1,
        "is_flash": True
    }
]
