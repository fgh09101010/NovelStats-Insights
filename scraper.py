import cloudscraper
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime

class PenanaPortfolioScraper:
    def __init__(self, target_url):
        self.url = target_url
        self.data_file = 'data.json'
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

    def run(self):
        print(f"🚀 正在存取作品集：{self.url}")
        
        try:
            response = self.scraper.get(self.url)
            if response.status_code != 200:
                print(f"❌ 請求失敗，狀態碼: {response.status_code}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            story_blocks = soup.select('.newXbox.storydata')
            
            if not story_blocks:
                print("⚠️ 找不到任何作品。")
                return

            print(f"🔍 成功找到 {len(story_blocks)} 部作品！")
            
            current_data = []
            for story in story_blocks:
                # 1. 基本資訊
                s_id = story.get('data-id')
                title_tag = story.select_one('.newBookTitle')
                title = title_tag.text.strip() if title_tag else "未知標題"
                
                # 2. 觀看數 (校準版)
                try:
                    views_ele = story.select_one('.newBkwords')
                    views = int(views_ele.text.strip().replace(',', '')) if views_ele else 0
                except:
                    views = 0
                
                # 3. 圖片連結 (從 style="background-image: url('...');" 提取)
                cover_url = ""
                cover_div = story.select_one('.newBookCover')
                if cover_div and cover_div.get('style'):
                    style_str = cover_div.get('style')
                    # 使用正規表達式抓取 url('...') 裡面的內容
                    match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style_str)
                    if match:
                        cover_url = match.group(1)

                # 4. 其他欄位
                category = story.select_one('.story_cat').text.strip() if story.select_one('.story_cat') else "未分類"
                update_info = story.select_one('.time').text.strip() if story.select_one('.time') else "未知"
                tags = [t.text.strip() for t in story.select('.story_tag a')]

                print(f"✅ 抓取成功：[{title}] | 觀看: {views} | 有封面: {'是' if cover_url else '否'}")

                current_data.append({
                    "id": s_id,
                    "title": title,
                    "category": category,
                    "views": views,
                    "cover": cover_url,  # 新增圖片欄位
                    "status": update_info,
                    "tags": tags,
                    "url": f"https://www.penana.com/story/{s_id}"
                })

            if current_data:
                self.save_to_json(current_data)

        except Exception as e:
            print(f"🚨 執行出錯: {e}")

    def save_to_json(self, new_stats):
        history = []
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                try:
                    history = json.load(f)
                except:
                    history = []

        entry = {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "works": new_stats
        }
        history.append(entry)

        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        print(f"✨ 數據與圖片連結已同步至 {self.data_file}")

if __name__ == "__main__":
    target = "https://www.penana.com/user/340930/%E7%84%A1%E9%9C%80%E5%A4%9A%E8%A8%80-%E9%9D%9C%E5%BE%85%E8%8A%B1%E9%96%8B/portfolio"
    bot = PenanaPortfolioScraper(target)
    bot.run()