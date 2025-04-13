
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from streamlit_js_eval import streamlit_js_eval

CSV_FILE = "yakiimo_log.csv"
st.set_page_config(page_title="🍠 GPS取得強化版", layout="centered")
st.title("📍 GPS取得強化版 + 月別CSV保存")

# 再取得ボタンとステート
if 'gps_refresh' not in st.session_state:
    st.session_state.gps_refresh = 0
if st.button("🔄 位置情報を再取得"):
    st.session_state.gps_refresh += 1

# GPS取得（成功/失敗判定付き）
gps_result = streamlit_js_eval(
    js_expressions="""
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const coords = pos.coords.latitude + ',' + pos.coords.longitude;
                Streamlit.setComponentValue('SUCCESS:' + coords);
            },
            (err) => {
                Streamlit.setComponentValue('ERROR:' + err.code + ':' + err.message);
            }
        );
    """,
    key=f"gps_debug_{st.session_state.gps_refresh}"
)

# 結果表示
gps = ""
if gps_result:
    if gps_result.startswith("SUCCESS:"):
        gps = gps_result.replace("SUCCESS:", "")
        st.success(f"✅ 現在地取得成功: {gps}")
    elif gps_result.startswith("ERROR:"):
        parts = gps_result.split(':')
        code = parts[1] if len(parts) > 1 else 'N/A'
        msg = parts[2] if len(parts) > 2 else '詳細不明'
        st.error(f"❌ GPS取得失敗: {msg}（コード: {code}）")
    else:
        st.warning("⚠️ GPS応答の解析に失敗しました。")
else:
    st.info("🔹 再取得ボタンを押して現在地を取得してください。")

# 入力フォーム
qty = st.number_input("🍠 販売個数", min_value=0)
price = st.number_input("💴 金額", min_value=0)
note = st.text_input("📝 備考")

if st.button("✅ 記録を保存"):
    if not gps:
        st.error("❌ 位置情報が取得できていません。記録は保存できません。")
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
        month_filename = now.strftime("yakiimo_%Y_%m.csv")
        if os.path.exists(month_filename):
            df_month = pd.read_csv(month_filename)
            df_month = pd.concat([df_month, row], ignore_index=True)
        else:
            df_month = row
        df_month.to_csv(month_filename, index=False, encoding="utf-8-sig")
        st.success("✅ 保存しました！")
        st.info(f"🗂 月別ファイルにも保存済: {month_filename}")
