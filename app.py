import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# Google Sheets 認證
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1RR0Y817VsMVpmpQ4Y5ugvG4JH__tGzytRB-8b8l90KE").sheet1

# Streamlit 頁面選擇
page = st.sidebar.selectbox(
    "選擇功能",
    ["📢 發布公告", "📋 查看公告", "🗑️ 刪除公告"],
    key="page_selector"
)

if page == "📢 發布公告":
    st.title("📢 公告發布系統")

    title = st.text_input("公告標題", key="input_title")
    content = st.text_area("公告內容", key="input_content")
    sender = st.text_input("發布人", key="input_sender")
    submit = st.button("發布公告", key="submit_button")

    if submit:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = [now, title, content, sender]
        sheet.append_row(new_row)
        st.success("✅ 公告已成功發布！")

elif page == "📋 查看公告":
    st.title("📋 公告列表")

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if not df.empty:
        for index, row in df[::-1].iterrows():
            st.subheader(f"📌 {row['標題']}")
            st.markdown(row['內容'])  # 展開顯示長訊息
            st.caption(f"🕒 {row['時間']}　✏️ {row['發布人']}")
            st.divider()
    else:
        st.info("目前沒有任何公告。")

        
elif page == "🗑️ 刪除公告":
    st.title("🗑️ 刪除公告")

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        st.info("目前沒有任何公告可刪除。")
    else:
        # 反轉資料順序（與查看公告一致）
        reversed_df = df[::-1].reset_index(drop=True)

        for i, row in reversed_df.iterrows():
            with st.expander(f"📌 {row['標題']}　🕒 {row['時間']}　✏️ {row['發布人']}"):
                st.markdown(row["內容"])
                with st.form(key=f"delete_form_{i}"):
                    password = st.text_input("輸入管理密碼以刪除此公告", type="password", key=f"password_{i}")
                    submit = st.form_submit_button("刪除公告")

                    if submit:
                        if password == "DELETE":
                            # 計算實際在 Google Sheet 中的列號
                            actual_row_index = len(df) - i + 1  # 包含表頭，所以 +1
                            sheet.delete_rows(actual_row_index)
                            st.success("✅ 公告已刪除！請重新整理頁面查看最新列表。")
                            st.stop()
                        else:
                            st.error("❌ 密碼錯誤，無法刪除。")
