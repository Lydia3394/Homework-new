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

view_mode = st.radio("選擇檢視方式", ["逐筆顯示", "表格顯示"])

if view_mode == "表格顯示":
    st.dataframe(df[::-1])
else:
    for index, row in df[::-1].iterrows():
        st.subheader(f"📌 {row['標題']}")
        st.markdown(row['內容'])
        st.caption(f"🕒 {row['時間']}　✏️ {row['發布人']}")
        st.divider()

        
elif page == "🗑️ 刪除公告":  # 這一段也要頂格
    st.title("🗑️ 刪除公告")

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        st.info("目前沒有任何公告可刪除。")
    else:
        df["顯示"] = df["標題"] + " | " + df["發布人"] + " | " + df["時間"]
        selected = st.selectbox("選擇要刪除的公告", df["顯示"], key="delete_selectbox")
        password = st.text_input("請輸入管理密碼以確認刪除", type="password", key="delete_password")
        delete = st.button("確認刪除", key="delete_button")

        if delete:
            if password == "DELETE":
                row_index = int(df[df["顯示"] == selected].index[0]) + 2
                sheet.delete_rows(row_index)
                st.success("✅ 公告已刪除！請重新整理頁面查看最新列表。")
            else:
                st.error("❌ 密碼錯誤，無法刪除。")
