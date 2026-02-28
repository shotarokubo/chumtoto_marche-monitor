import requests
import os
import json

# --- 設定 ---
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')
DB_FILE = "last_stock.json"

TARGET_CREATORS = [
    {"name": "宮原梓", "id": "dst_miyaharaazu"},
    {"name": "江本夏渚", "id": "dst_emotonana"},
    {"name": "柏葉れん", "id": "dst_kashiwabare"},
    {"name": "瀬﨑くるみ", "id": "dst_sezakikurum"},
    {"name": "詩之宮かこ", "id": "chum_shinomiyak"},
    {"name": "ChumToto", "id": "chumtoto"},
]

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
        try:
            with open(DB_FILE, "r") as f:
                last_data = json.load(f)
        except:
            last_data = {}

    # マルシェのフロントエンドが実際に使用しているヘッダーセット
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Origin": "https://marche-yell.com",
        "Referer": "https://marche-yell.com/",
        "X-Requested-With": "XMLHttpRequest"
    }

    current_all_data = {}

    for creator in TARGET_CREATORS:
        name = creator["name"]
        cid = creator["id"]
        
        # 修正ポイント: 実際のブラウザ通信に基づいた正確なエンドポイントに変更
        api_url = f"https://marche-yell.com/api/creators/{cid}/products?limit=24&offset=0"
        
        print(f"チェック中: {name} ({cid})...")
        
        try:
            response = requests.get(api_url, headers=headers, timeout=15)
            
            # 403/404エラーが出た場合のログを強化
            if response.status_code != 200:
                print(f"  -> スキップ: アクセス拒否 ({response.status_code})")
                continue

            data = response.json()
            
            # APIのレスポンス形式に合わせて取得
            # products または data 配下にあるケース両方に対応
            products = data.get('products') or data.get('data', {}).get('products', [])

            current_all_data[cid] = {}

            if not products:
                print(f"  -> 商品が見つかりませんでした（0件）")
                continue

            print(f"  -> {len(products)}件の商品を検出しました")

            for p in products:
                title = p.get('title', '商品')
                limit = p.get('limit_quantity', 0)
                sold = p.get('sold_quantity', 0)
                remaining = limit - sold
                p_id = p.get('id')
                p_url = f"https://marche-yell.com/{cid}/products/{p_id}"
                
                current_all_data[cid][title] = remaining
                last_count = last_data.get(cid, {}).get(title, -1)

                should_notify = False
                reason = ""

                if last_count == -1:
                    should_notify = True
                    reason = "✨ 新着出品！"
                elif remaining > 0 and (last_count <= 0):
                    should_notify = True
                    reason = "🔄 在庫復活！"
                elif remaining <= 3 and last_count > 3:
                    should_notify = True
                    reason = "⚠️ 残りわずか！"

                if should_notify and remaining > 0:
                    msg = f"\n【{reason}】{name}\n{title}\n在庫：残り {remaining} / 全 {limit} 枚\n{p_url}"
                    send_line(msg)
                    print(f"  -> 通知送信: {title}")

        except Exception as e:
            print(f"  -> {name}のチェック中にエラー: {e}")

    with open(DB_FILE, "w") as f:
        json.dump(current_all_data, f)

if __name__ == "__main__":
    check_marche()
