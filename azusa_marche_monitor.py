import requests
import os
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
    # 拒否されにくい最強のiPhoneヘッダー
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja-JP,ja;q=0.9",
        "Connection": "keep-alive",
    }
    
    try:
        # セッションを使ってアクセス
        session = requests.Session()
        response = session.get(TARGET_URL, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"アクセス制限中 (Status: {response.status_code})")
            return

        html = response.text
        
        # HTMLから「商品タイトル」と「残り枚数」を正規表現で引っこ抜く
        # マルシェのHTML構造（product-card内のタイトルと在庫数）を狙い撃ち
        titles = re.findall(r'class="product-card__title">([^<]+)</div>', html)
        stocks = re.findall(r'残り\s*(\d+)\s*枚', html)

        if not titles:
            # ページは開けたが商品がない状態
            print("現在、出品中の商品は見つかりませんでした。出品を待機します。")
            return

        print(f"検知数: {len(titles)}件")

        for i in range(len(titles)):
            title = titles[i].strip()
            # 在庫数が取得できれば数値化、できなければ無視
            try:
                remaining = int(stocks[i])
            except:
                continue
            
            # 【重要】通知条件：在庫が1〜3枚の時だけ送る（完売や大量在庫はスルー）
            if 0 < remaining <= 3:
                msg = f"\n【在庫わずか！】宮原梓\n{title}\n残り {remaining} 枚\n{TARGET_URL}"
                send_line(msg)
                print(f"通知送信: {title}")

    except Exception as e:
        print(f"監視一時エラー（自動再試行されます）: {e}")

if __name__ == "__main__":
    check_marche()
