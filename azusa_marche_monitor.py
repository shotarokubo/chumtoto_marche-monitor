import requests
import os
import json

# --- 設定 ---
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_USER_ID')

def send_line(text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {"to": USER_ID, "messages": [{"type": "text", "text": text}]}
    res = requests.post(url, headers=headers, json=payload)
    return res

def test_new_product():
    print("LINE疎通・新着表示テストを開始します...")
    
    # ユーザーさんが知りたい「全枚数(limit)」と「残り(limit - sold)」を再現
    title = "【テスト】梓の全力応援マルシェ"
    limit = 20  # 全20枚
    sold = 0    # 売れた数0
    remaining = limit - sold
    p_url = "https://marche-yell.com/dst_miyaharaazu"

    # 通知メッセージを組み立て
    reason = "✨ 新着出品！"
    msg = f"\n【{reason}】宮原梓\n{title}\n在庫：残り {remaining} / 全 {limit} 枚\n{p_url}"
    
    response = send_line(msg)
    
    if response.status_code == 200:
        print("✅ LINEが送信されました！スマホを確認してください。")
    else:
        print(f"❌ 送信失敗: {response.text}")

if __name__ == "__main__":
    test_new_product()
