import streamlit as st
import requests

# ページの設定
st.set_page_config(page_title="お迎えルート比較", page_icon="🚗", layout="centered")

# === 設定項目 ===
# 取得したGoogle Routes APIキー
API_KEY = "AIzaSyAfEHdBoGgIIiQ8AsSEvOwU-05I8A7qEEA"

# 出発地と目的地（正確に認識させるため市町村名を付与しています）
ORIGIN = "東京薬科大学, 八王子市"
DESTINATION = "ひよこハウス豊田, 日野市"

# ルートA（直線ルート）の経由地
ROUTE_A_WAYPOINTS = [
    (35.638140, 139.388616),
    (35.655021, 139.378821)
]

# ルートB（南陽台ルート）の経由地
ROUTE_B_WAYPOINTS = [
    (35.633740, 139.374954),
    (35.642243, 139.376011),
    (35.650988, 139.375014)
]

def get_route_time(waypoints):
    """Google Routes APIにリクエストを送り、渋滞を加味した所要時間(分)を取得する"""
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    
    # APIに要求するデータ（ここでは「所要時間」だけを要求して通信を軽くします）
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "routes.duration"
    }
    
    # 経由地のデータをAPIの形式に変換（via=True にすることで「通過点」として扱い、停車時間をなくします）
    intermediates = [
        {
            "location": {"latLng": {"latitude": lat, "longitude": lng}},
            "via": True
        }
        for lat, lng in waypoints
    ]
    
    # リクエストの中身
    payload = {
        "origin": {"address": ORIGIN},
        "destination": {"address": DESTINATION},
        "intermediates": intermediates,
        "travelMode": "DRIVE",               # 自動車
        "routingPreference": "TRAFFIC_AWARE" # 現在のリアルタイム渋滞を加味する
    }
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    try:
        # APIからは "900s" のように秒数で返ってくるので、数値にして60で割り「分」にする
        duration_str = data["routes"][0]["duration"]
        minutes = int(duration_str.replace("s", "")) // 60
        return minutes
    except (KeyError, IndexError):
        # 万が一エラーが起きた場合
        st.error("ルート情報の取得に失敗しました。経由地やAPIキーの設定を確認してください。")
        return None

# === アプリの画面設計 ===
st.title("🚗 お迎えルート比較")
st.write("東京薬科大学 ➔ ひよこハウス豊田")

# ボタンを押した時の処理
if st.button("🔄 現在の所要時間をチェック", type="primary", use_container_width=True):
    with st.spinner("渋滞情報を取得中..."):
        time_a = get_route_time(ROUTE_A_WAYPOINTS)
        time_b = get_route_time(ROUTE_B_WAYPOINTS)
        
        if time_a is not None and time_b is not None:
            st.divider()
            
            # 結果を比較して表示
            if time_a < time_b:
                st.success(f"✨ 今は **ルートA（直線ルート）** が {time_b - time_a}分 早いです！")
            elif time_b < time_a:
                st.success(f"✨ 今は **ルートB（南陽台ルート）** が {time_a - time_b}分 早いです！")
            else:
                st.info("どちらのルートも到着時間は同じです。")
            
            # 並べて大きく表示
            col1, col2 = st.columns(2)
            with col1:
                st.metric("ルートA (直線)", f"{time_a} 分")
            with col2:
                st.metric("ルートB (南陽台)", f"{time_b} 分")