import requests
import os
import json
import re

# --- 設定 ---
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')
TARGET_URL = "https://marche-yell.com/dst_miyaharaazu"
DB_FILE = "last_stock.json"

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
    last_data = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_data = json.load(f)

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    }
    
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        html = response.text
        
        # 1. HTML内の "__NEXT_DATA__" (JSON) を探し出す
        json_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if not json_match:
            print("データタグが見つかりません。")
            return

        # 2. JSONを解析
        data = json.loads(json_match.group(1))
        # 商品リストが眠っている場所を狙い撃ち
        products = data.get('props', {}).get('pageProps', {}).get('products', [])

        if not products:
            print("現在、出品中の商品は見つかりませんでした。")
            return

        current_data = {}
        for p in products:
            title = p.get('title', '商品')
            limit = p.get('limit_quantity', 0) # これが「全数」
            sold = p.get('sold_quantity', 0)   # これが「売れた数」
            remaining = limit - sold           # これが「残り数」
            p_id = p.get('id')
            p_url = f"https://marche-yell.com/dst_miyaharaazu/products/{p_id}"
            
            current_data[title] = remaining
            last_count = last_data.get(title, -1)

            should_notify = False
            reason = ""

            # 通知判定
            if last_count == -1:
                should_notify = True
                reason = "✨ 新着出品！"
            elif remaining <= 3 and last_count > 3:
                should_notify = True
                reason = "⚠️ 残りわずか！"
            elif remaining > last_count and last_count != -1:
                should_notify = True
                reason = "🔄 在庫復活！"

            if should_notify:
                # LINEメッセージ
                msg = f"\n【{reason}】宮原梓\n{title}\n在庫：残り {remaining} / 全 {limit} 枚\n{p_url}"
                send_line(msg)
                print(f"通知送信: {title} ({remaining}/{limit})")

        # 今回の状態を保存
        with open(DB_FILE, "w") as f:
            json.dump(current_data, f)

    except Exception as e:
        print(f"解析エラー: {e}")

if __name__ == "__main__":
    check_marche()
