
# 🍠 GPS取得強化版 + 地図履歴プロットアプリ

## 概要
- スマホで現在地を取得
- 販売記録を保存
- 履歴を地図にプロット（金額に応じて円の大きさ変化）

## 使い方
1. GitHubにこのコードをアップ
2. [Streamlit Cloud](https://streamlit.io/cloud) で新規アプリ作成
3. `yakiimo_streamlit_app.py` を指定すればスマホ単体で動作！

## 必要なライブラリ
- streamlit
- pandas
- streamlit-js-eval
- pydeck

## 注意
- iPhoneでは Safari の「位置情報の許可」が必要
- 初回は「🔄位置情報を再取得」ボタンを押してください
