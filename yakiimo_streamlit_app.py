
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="📍 GPS自動入力版", layout="centered")
st.title("📍 GPS取得（自動入力版）")

# 初期化
if 'gps_result' not in st.session_state:
    st.session_state.gps_result = ""

# JavaScriptで取得し、Streamlit側へ postMessage
components.html("""
    <script>
    window.addEventListener("message", (event) => {
        const gpsField = window.parent.document.querySelector('input[data-testid="stTextInput"]');
        if (event.data.startsWith("GPS:") && gpsField) {
            gpsField.value = event.data;
            gpsField.dispatchEvent(new Event("input", { bubbles: true }));
        } else if (event.data.startsWith("ERROR:") && gpsField) {
            gpsField.value = event.data;
            gpsField.dispatchEvent(new Event("input", { bubbles: true }));
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

# GPS値を自動入力する text_input（ユーザーは触れなくてOK）
gps_input = st.text_input("📍 現在地（自動取得）", value=st.session_state.gps_result)
if gps_input.startswith("GPS:"):
    gps_value = gps_input.replace("GPS:", "")
    st.success(f"✅ GPS取得成功: {gps_value}")
    st.session_state.gps_result = gps_input
elif gps_input.startswith("ERROR:"):
    st.error(f"❌ GPS取得エラー: {gps_input.replace('ERROR:', '')}")
    st.session_state.gps_result = gps_input
else:
    st.info("⏳ GPS取得中です...（数秒お待ちください）")

# 入力フォーム
qty = st.number_input("🍠 販売個数", min_value=0)
price = st.number_input("💴 金額", min_value=0)
note = st.text_input("📝 備考")

CSV_FILE = "yakiimo_log.csv"
if st.button("✅ 記録を保存"):
    if not st.session_state.gps_result.startswith("GPS:"):
        st.error("❌ GPSが取得できていません。")
    else:
        gps_data = st.session_state.gps_result.replace("GPS:", "")
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
