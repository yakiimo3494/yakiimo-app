
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="📍 GPS取得 (components版)", layout="centered")
st.title("📍 st.components.v1.html を使ったGPS取得")

# 初期化
if 'gps' not in st.session_state:
    st.session_state.gps = ""

# JavaScript埋め込み
components.html("""
    <script>
    window.addEventListener("message", (event) => {
        if (event.data.startsWith("GPS:") || event.data.startsWith("ERROR:")) {
            const streamlitEvent = new Event("streamlit:message");
            streamlitEvent.data = event.data;
            window.parent.postMessage(streamlitEvent.data, "*");
        }
    });

    navigator.geolocation.getCurrentPosition(
        function(pos) {
            const coords = pos.coords.latitude + ',' + pos.coords.longitude;
            window.parent.postMessage("GPS:" + coords, "*");
        },
        function(err) {
            window.parent.postMessage("ERROR:" + err.message, "*");
        }
    );
    </script>
""", height=0)

# Streamlit側で受信された値を仮に手動入力（ユーザーがコピーして貼る場合を想定）
gps_input = st.text_input("📍 現在地（JSが取得した値を貼り付けてください）", value=st.session_state.gps)
if gps_input.startswith("GPS:"):
    gps_value = gps_input.replace("GPS:", "")
    st.success(f"✅ GPS取得成功: {gps_value}")
    st.session_state.gps = gps_value
elif gps_input.startswith("ERROR:"):
    st.error(f"❌ GPS取得エラー: {gps_input.replace('ERROR:', '')}")
else:
    st.info("⏳ GPS値を待機中、または手動貼付けをお願いします")

# 入力フォーム
qty = st.number_input("🍠 販売個数", min_value=0)
price = st.number_input("💴 金額", min_value=0)
note = st.text_input("📝 備考")

CSV_FILE = "yakiimo_log.csv"
if st.button("✅ 記録を保存"):
    if not st.session_state.gps.startswith("GPS:") and gps_input == "":
        st.error("❌ GPSが取得できていません。")
    else:
        gps_data = gps_input.replace("GPS:", "")
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        row = pd.DataFrame([[date_str, gps_data, qty, price, note]],
                           columns=["日時", "GPS座標", "販売数", "金額", "備考"])
        try:
            old = pd.read_csv(CSV_FILE)
            df = pd.concat([old, row], ignore_index=True)
        except:
            df = row
        df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
        month_filename = now.strftime("yakiimo_%Y_%m.csv")
        if os.path.exists(month_filename):
            df_month = pd.read_csv(month_filename)
            df_month = pd.concat([df_month, row], ignore_index=True)
        else:
            df_month = row
        df_month.to_csv(month_filename, index=False, encoding="utf-8-sig")
        st.success("✅ 保存しました！")
        st.info(f"🗂 月別ファイルにも保存済: {month_filename}")
