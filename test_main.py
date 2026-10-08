# test_main.py
from src.config import SOURCE_CONFIGS
from src.scraper import ScraperV3

def run_test():
    print("="*60)
    print("🤖 港股量化新聞監控系統 - V3 Scrapling 獨立測試")
    print("="*60)
    
    scraper = ScraperV3(SOURCE_CONFIGS)
    news_data = scraper.fetch_all()
    
    print("\n" + "="*60)
    print(f"🎉 測試結束！系統總共抓取到 {len(news_data)} 條新聞。")
    print("="*60)

if __name__ == "__main__":
    run_test()
