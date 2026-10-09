from src.scraper import ScraperV3
from config import CONFIGS

def run_test():
    print("=" * 60)
    print("🤖 港股量化新聞監控系統 - V3 Scrapling 獨立測試")
    print("=" * 60)
    scraper = ScraperV3(CONFIGS)
    news_data = scraper.fetch_all()
    print(f"\n✅ 全部完成，總共撈到 {len(news_data)} 條新聞")

if __name__ == "__main__":
    run_test()
