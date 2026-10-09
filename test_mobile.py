# test_mobile.py
import time
from urllib.parse import urljoin
from scrapling.fetchers import StealthyFetcher

def run_mobile_test():
    print("="*60)
    print("📱 開始測試：智通財經【手機版】極速分頁抓取")
    print("="*60)
    
    # 🚨 關鍵：改用 m.zhitongcaijing.com 手機版網址，原生支援 ?page= 參數
    base_url = "https://m.zhitongcaijing.com/market.html?page={}"
    
    all_news = []
    
    # 測試抓取第 1 頁與第 2 頁
    for page_num in range(1, 3):
        url = base_url.format(page_num)
        print(f"\n-> 正在加載第 {page_num} 頁: {url}")
        
        try:
            # 使用最輕量的 StealthyFetcher，不啟動複雜的無頭瀏覽器
            page = StealthyFetcher.fetch(url, headless=True, timeout=45000)
            
            # 手機版的 CSS 結構可能不同，我們放寬選擇器，並用 a 標籤一網打盡
            elements = page.css(".list-item a, .news-list a, .item a, a")
            
            valid_items = []
            seen_titles = set()
            
            for el in elements:
                # 提取純文字標題
                raw_title = el.xpath(".//text()").getall()
                title = "".join(raw_title).strip()
                
                # 過濾長度過短或包含無效字眼的導覽列按鈕
                if len(title) < 15 or "登入" in title or "下載" in title:
                    continue
                    
                # 提取連結
                href = el.attrib.get("href", "") if el.attrib else ""
                if not href or href.startswith("javascript:"):
                    continue
                    
                full_link = urljoin(url, href)
                
                # 去重機制：確保同一頁內沒有重複新聞
                if title not in seen_titles:
                    seen_titles.add(title)
                    valid_items.append({
                        "title": title,
                        "link": full_link
                    })
            
            all_news.extend(valid_items)
            
            print(f"   ✅ 第 {page_num} 頁萃取完成，共 {len(valid_items)} 條有效新聞。")
            if valid_items:
                print("   👀 [資料預覽]:")
                for idx, item in enumerate(valid_items[:3], 1):
                    # 截斷過長的標題以利預覽
                    short_title = item['title'][:45] + "..." if len(item['title']) > 45 else item['title']
                    print(f"      [{idx}] {short_title}")
                    
            # 翻頁之間的禮貌休眠
            if page_num < 2:
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ 第 {page_num} 頁抓取失敗: {e}")
            break

    print("\n" + "="*60)
    print(f"🎉 測試結束！系統跨頁總共抓取到 {len(all_news)} 條新聞。")
    print("="*60)

if __name__ == "__main__":
    run_mobile_test()
