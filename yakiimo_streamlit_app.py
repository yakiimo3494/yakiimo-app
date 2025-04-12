
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from streamlit_js_eval import streamlit_js_eval

CSV_FILE = "yakiimo_log.csv"
st.set_page_config(page_title="🍠焼き芋販売記録", layout="centered")
st.title("🍠 GPS取得強化版 + 月別CSV保存")

# GPS再取得ボタン付き取得処理
st.subheader("📍 現在地（GPS）")
if 'gps_refresh' not in st.session_state:
    st.session_state.gps_refresh = 0

if st.button("🔄 位置情報を再取得"):
    st.session_state.gps_refresh += 1

gps = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition((loc) => {const pos = loc.coords.latitude + ',' + loc.coords.longitude; Streamlit.setComponentValue(pos);})",
    key=f"gps_{st.session_state.gps_refresh}"
)

# 表示とバリデーション
if gps and gps != "none":
    st.success(f"✅ 現在地取得済: {gps}")
else:
    st.error("⚠️ 現在地が取得できません。Safariで位置情報を許可し、再取得ボタンを2回以上押してください。")

# 入力フォーム
qty = st.number_input("🍠 販売個数", min_value=0)
price = st.number_input("💴 金額", min_value=0)
note = st.text_input("📝 備考")

# 記録ボタン
if st.button("✅ 記録を保存"):
    if not gps or gps == "none":
        st.error("❌ GPSが取得できていません。再取得ボタンを押して現在地を取得してください。")
    else:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        row = pd.DataFrame([[date_str, gps, qty, price, note]],
                           columns=["日時", "GPS座標", "販売数", "金額", "備考"])

        try:
            old = pd.read_csv(CSV_FILE)
            df = pd.concat([old, row], ignore_index=True)
        except:
            df = row
        df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
        st.success("✅ 保存しました！")

        # 月別ファイル保存
        month_filename = now.strftime("yakiimo_%Y_%m.csv")
        if os.path.exists(month_filename):
            df_month = pd.read_csv(month_filename)
            df_month = pd.concat([df_month, row], ignore_index=True)
        else:
            df_month = row
        df_month.to_csv(month_filename, index=False, encoding="utf-8-sig")
        st.info(f"🗂 月別ファイルにも保存済: {month_filename}")
