from DrissionPage import ChromiumPage, ChromiumOptions
import requests
import os
import time

class AvatarFetcher:
    def __init__(self):
        # 準備存放圖片的資料夾
        self.save_dir = "assets"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        # 各大平台連結字典
        self.platforms = {
            "penana": "https://www.penana.com/user/340930",
            "cxc": "https://cxc.today/zh/@bloom_in_silence",
            "kado": "https://www.kadokado.com.tw/user/283023",
            "popo": "https://www.popo.tw/users/fgh09101010",
            "threads": "https://www.threads.net/@fgh09202020"
        }

        # 設定瀏覽器
        self.co = ChromiumOptions()
        # self.co.set_argument('--headless') # 測試時建議不要開啟 headless，看看畫面有沒有出來
        self.co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

    def download_image(self, url, filename):
        """ 下載圖片並存檔 """
        try:
            # 有些網站會檢查 User-Agent 才給下載
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            if response.status_code == 200:
                file_path = os.path.join(self.save_dir, f"{filename}.jpg")
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"📥 成功下載: {filename}.jpg")
                return True
            else:
                print(f"⚠️ 下載失敗，狀態碼: {response.status_code}")
                return False
        except Exception as e:
            print(f"🚨 下載發生錯誤: {e}")
            return False

    def run(self):
        page = ChromiumPage(self.co)
        print("🚀 啟動全平台頭像抓取任務...")

        for name, url in self.platforms.items():
            print(f"\n🔍 正在前往 [{name.upper()}] : {url}")
            try:
                page.get(url)
                time.sleep(3) # 給網頁一點時間渲染 Javascript
                
                img_url = None

                # 策略 1：尋找網頁標準的 og:image (最穩定，通常是最高畫質頭像或封面)
                meta_og = page.ele('x://meta[@property="og:image"]')
                if meta_og:
                    img_url = meta_og.attr('content')
                    print(f"✅ 找到 og:image 網址")

                # 如果 Threads 剛好抓不到 og:image，我們加上備用策略
                if not img_url and name == "threads":
                    print("🔄 嘗試 Threads 備用策略...")
                    # 尋找 Threads 頭像的特徵 (通常是一個圓形圖片)
                    img_tag = page.ele('tag:img')
                    if img_tag: img_url = img_tag.attr('src')

                # 開始下載
                if img_url:
                    # 修復有些 og:image 網址沒有 http 開頭的問題
                    if img_url.startswith('//'):
                        img_url = "https:" + img_url
                        
                    self.download_image(img_url, name)
                else:
                    print(f"❌ 找不到 {name} 的圖片網址。")

            except Exception as e:
                print(f"🚨 抓取 {name} 時發生異常: {e}")

        page.quit()
        print(f"\n✨ 任務完成！所有抓到的圖片已存入 {self.save_dir}/ 資料夾中。")

if __name__ == "__main__":
    fetcher = AvatarFetcher()
    fetcher.run()