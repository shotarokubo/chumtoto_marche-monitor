import requests
import os
import json
import re

# --- 設定 ---
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')
TARGET_URL = "https://marche-yell.com/dst_miyaharaazu"

def send_line(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": text}]}
    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
    except Exception as e:
        print(f"LINE送信エラー: {e}")

def check_marche():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers)
        html_content = response.text
        
        # HTML内に埋め込まれているデータ（__NEXT_DATA__）を探す
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
        
        if not match:
            print("データが見つかりませんでした。サイトの構造が大幅に変更された可能性があります。")
            return

        # データの塊を解析
        data = json.loads(match.group(1))
        # 商品リストが格納されている深い階層を指定
        products = data.get('props', {}).get('pageProps', {}).get('products', [])

        if not products:
            print("現在、販売中の商品は見つかりませんでした。")
            return

        for p in products:
            title = p.get('title', '新着商品')
            sold = p.get('sold_quantity', 0)
            limit = p.get('limit_quantity', 0)
            remaining = limit - sold
            p_id = p.get('id')
            p_url = f"https://marche-yell.com/dst_miyaharaazu/products/{p_id}"

            # テスト用：常に通知
            if True: 
                msg = f"\n【在庫チェック】宮原梓\n{title}\n残り {remaining} 枚\n{p_url}"
                send_line(msg)
                print(f"通知送信: {title}")

    except Exception as e:
        print(f"エラー発生: {e}")

if __name__ == "__main__":
    check_marche()
