
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from streamlit_js_eval import streamlit_js_eval
import pydeck as pdk

CSV_FILE = "yakiimo_log.csv"
st.set_page_config(page_title="🍠 GPS取得強化版", layout="centered")
st.title("📍 GPS取得 + 地図履歴プロット（安定版）")

# 再取得ボタンとステート
if 'gps_refresh' not in st.session_state:
    st.session_state.gps_refresh = 0
if st.button("🔄 位置情報を再取得"):
    st.session_state.gps_refresh += 1

# GPS取得（高精度設定）
gps_result = streamlit_js_eval(
    js_expressions="""
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const coords = pos.coords.latitude + ',' + pos.coords.longitude;
                Streamlit.setComponentValue('SUCCESS:' + coords);
            },
            (err) => {
                Streamlit.setComponentValue('ERROR:' + err.code + ':' + err.message);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
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
        try:
            lat, lon = map(float, gps.split(","))
            st.map(pd.DataFrame([[lat, lon]], columns=['lat', 'lon']))
        except:
            st.warning("⚠️ 地図表示に失敗しました。座標フォーマットを確認してください。")
    elif gps_result.startswith("ERROR:"):
        parts = gps_result.split(':')
        code = parts[1] if len(parts) > 1 else 'N/A'
        msg = parts[2] if len(parts) > 2 else '詳細不明'
        st.error(f"❌ GPS取得失敗: {msg}（コード: {code}）")
        if "permission" in msg.lower():
            st.warning("📱 Safariの「設定 ＞ Safari ＞ 位置情報」が「許可」になっているか確認してください。")
    else:
        st.warning("⚠️ GPS応答の解析に失敗しました。")
else:
    st.info("🔹 再取得ボタンを押して現在地を取得してください。")

# 入力フォーム
qty = st.number_input("🍠 販売個数", min_value=0)
price = st.number_input("💴 金額", min_value=0)
note = st.text_input("📝 備考")

# 保存処理
if st.button("✅ 記録を保存", disabled=not bool(gps)):
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

# 履歴プロット（GPS座標の分解エラー対応版）
map_data = None
try:
    df_all = pd.read_csv(CSV_FILE)
    gps_split = df_all["GPS座標"].str.split(",", expand=True)
    gps_split = gps_split[gps_split.shape[1] == 2]
    gps_split.columns = ['lat', 'lon']
    gps_split = gps_split.astype(float)
    df_all = df_all.loc[gps_split.index]
    df_all[['lat', 'lon']] = gps_split
    df_all["金額"] = df_all["金額"].fillna(0)
    map_data = df_all
except Exception as e:
    st.warning(f"📂 地図データの読み込みに失敗しました: {e}")

if map_data is not None and not map_data.empty:
    st.subheader("🗺️ 売上履歴マップ")
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position='[lon, lat]',
        get_radius="金額",
        radius_scale=5,
        get_fill_color="[255, 140, 0, 160]",
        pickable=True
    )
    view_state = pdk.ViewState(
        latitude=map_data["lat"].mean(),
        longitude=map_data["lon"].mean(),
        zoom=12,
        pitch=0
    )
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "¥{金額}"}))
else:
    st.info("📍まだ売上地点の記録がありません。")
