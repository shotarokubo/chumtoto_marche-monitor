import requests
import os

# --- 設定 ---
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')
# API URLを再度利用（ここに直接アクセスするのが最も確実です）
API_URL = "https://marche-yell.com/api/v1/creators/dst_miyaharaazu/products"

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
    # サーバーを騙すための「おまじない」を強化
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://marche-yell.com",
        "Referer": "https://marche-yell.com/dst_miyaharaazu",
        "X-Requested-With": "XMLHttpRequest" # これが重要！ブラウザからの通信だと主張します
    }
    
    try:
        response = requests.get(API_URL, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        # もしこれでも200以外なら、その理由を出力
        if response.status_code != 200:
            print(f"アクセス拒否されました: {response.text[:200]}")
            return

        products = response.json()
        if not products:
            print("現在、商品データが空です。")
            return

        for p in products:
            title = p.get('title', '新着商品')
            limit = p.get('limit_quantity', 0)
            sold = p.get('sold_quantity', 0)
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
