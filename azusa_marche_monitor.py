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
        
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
        if not match:
            print("データタグが見つかりません。")
            return

        full_data = json.loads(match.group(1))
        
        # --- 調査ログ出力 ---
        # どこにデータがあるか探すために、データのキーをすべて表示します
        props = full_data.get('props', {})
        page_props = props.get('pageProps', {})
        print("見つかったキー:", page_props.keys())

        # マルシェの新しい構造に合わせてデータを取得
        # 'products' が無い場合、'creator' の中や別の場所に隠れている可能性があります
        products = page_props.get('products') or page_props.get('creator', {}).get('products', [])

        if not products:
            print("--- デバッグ情報 ---")
            # データの先頭部分だけ表示して構造を確認
            print(json.dumps(page_props, indent=2, ensure_ascii=False)[:1000])
            print("------------------")
            return

        for p in products:
            title = p.get('title', '新着商品')
            # 完売時は limit_quantity と sold_quantity が同じになる
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
