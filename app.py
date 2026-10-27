import streamlit as st
import requests
import urllib.parse
from datetime import datetime, timezone, timedelta

# ページの設定
st.set_page_config(page_title="お迎えルート", layout="centered")

# === 画面上部が隠れないよう、上部パディングを広げたCSS ===
st.markdown("""
<style>
    /* 上部に十分な余白をとることでメニューバーへの隠れを防止 */
    .block-container { padding-top: 3.5rem !important; padding-bottom: 1rem !important; }
    
    .title-text { font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 0px; }
    .sub-text { font-size: 12px; color: gray; text-align: center; margin-bottom: 12px; }
    
    /* 勝敗結果のバッジ */
    .win-badge { background-color: #e6f4ea; color: #1e8e3e; padding: 8px; border-radius: 6px; text-align: center; font-weight: bold; margin-bottom: 12px; font-size: 14px;}
    .tie-badge { background-color: #e8f0fe; color: #1967d2; padding: 8px; border-radius: 6px; text-align: center; font-weight: bold; margin-bottom: 12px; font-size: 14px;}
    
    /* ルート情報カード */
    .route-card { background: #fff; border-radius: 8px; padding: 12px; text-align: center; border: 2px solid #f0f2f6; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .r-name { font-size: 13px; font-weight: bold; color: #555; }
    .r-time { font-size: 36px; font-weight: bold; color: #000; margin: -2px 0; }
    .r-sub { font-size: 12px; margin-bottom: 12px; color: #666; }
    .d-red { color: #d32f2f; font-weight: bold; }
    .d-green { color: #2e7d32; }
    
    /* ナビ起動ボタン */
    .nav-btn { display: block; background-color: #1a73e8; color: white !important; padding: 8px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# === 設定項目 ===
API_KEY = "AIzaSyAfEHdBoGgIIiQ8AsSEvOwU-05I8A7qEEA"
ORIGIN = "東京薬科大学, 八王子市"
DESTINATION = "ひよこハウス豊田, 日野市"
JST = timezone(timedelta(hours=+9), 'JST')

ROUTE_A = [(35.638140, 139.388616), (35.655021, 139.378821)]
ROUTE_B = [(35.633740, 139.374954), (35.642243, 139.376011), (35.650988, 139.375014)]

def get_route_info(waypoints):
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.staticDuration"
    }
    intermediates = [{"location": {"latLng": {"latitude": lat, "longitude": lng}}, "via": True} for lat, lng in waypoints]
    payload = {
        "origin": {"address": ORIGIN}, "destination": {"address": DESTINATION},
        "intermediates": intermediates, "travelMode": "DRIVE", "routingPreference": "TRAFFIC_AWARE"
    }
    
    res = requests.post(url, headers=headers, json=payload).json()
    try:
        dur_str = res["routes"][0]["duration"]
        stat_str = res["routes"][0].get("staticDuration", dur_str)
        time_m = int(dur_str.replace("s", "")) // 60
        stat_m = int(stat_str.replace("s", "")) // 60
        return time_m, max(0, time_m - stat_m)
    except:
        return None, None

def get_gmaps_url(waypoints):
    org = urllib.parse.quote(ORIGIN)
    dst = urllib.parse.quote(DESTINATION)
    wps = "|".join([f"{lat},{lng}" for lat, lng in waypoints])
    return f"https://www.google.com/maps/dir/?api=1&origin={org}&destination={dst}&waypoints={wps}&travelmode=driving"

def draw_card(name, time, delay, url):
    eta = (datetime.now(JST) + timedelta(minutes=time)).strftime("%H:%M")
    delay_html = f"<span class='d-red'>+{delay}分渋滞</span>" if delay > 0 else "<span class='d-green'>渋滞なし</span>"
    
    html = f"""
    <div class="route-card">
        <div class="r-name">{name}</div>
        <div class="r-time">{time}<span style="font-size:16px; font-weight:normal;">分</span></div>
        <div class="r-sub">{eta} 着 ({delay_html})</div>
        <a href="{url}" class="nav-btn" target="_blank">📱 ナビ開始</a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# === 画面レイアウト ===
st.markdown("<div class='title-text'>🚗 お迎えルート比較</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>東京薬科大学 ➔ ひよこハウス豊田</div>", unsafe_allow_html=True)

if st.button("🔄 現在の状況をチェック", type="primary", use_container_width=True):
    with st.spinner("渋滞情報を取得中..."):
        time_a, delay_a = get_route_info(ROUTE_A)
        time_b, delay_b = get_route_info(ROUTE_B)
        
        if time_a is not None and time_b is not None:
            if time_a < time_b:
                st.markdown(f"<div class='win-badge'>✨ ルートA（直線）が {time_b - time_a}分 早い！</div>", unsafe_allow_html=True)
            elif time_b < time_a:
                st.markdown(f"<div class='win-badge'>✨ ルートB（南陽台）が {time_a - time_b}分 早い！</div>", unsafe_allow_html=Type)
            else:
                st.markdown("<div class='tie-badge'>どちらも到着時間は同じです</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                draw_card("ルートA (直線)", time_a, delay_a, get_gmaps_url(ROUTE_A))
            with col2:
                draw_card("ルートB (南陽台)", time_b, delay_b, get_gmaps_url(ROUTE_B))
