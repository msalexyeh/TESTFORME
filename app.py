import datetime
import pandas as pd
import streamlit as st

# 設定網頁標題
st.set_page_config(page_title="油價記錄小幫手", page_icon="⛽", layout="centered")

st.title("⛽ 加油記錄與油價查詢系統")
st.markdown("輕鬆記錄每次加油的日期、公升數與單價，追蹤您的油費開銷！")

# 1. 初始化 Session State 用於暫存資料（若正式使用可改接資料庫或 CSV 檔案）
if "fuel_data" not in st.session_state:
  # 建立預設範例資料
  st.session_state.fuel_data = pd.DataFrame(
      {
          "日期": [datetime.date(2026, 5, 1), datetime.date(2026, 5, 15)],
          "公升": [40.5, 38.0],
          "單價": [31.2, 30.8],
          "總金額": [40.5 * 31.2, 38.0 * 30.8],
      }
  )

# 2. 側邊欄：輸入表單
st.sidebar.header("➕ 新增加油記錄")

with st.sidebar.form("fuel_form"):
  input_date = st.date_input("日期", value=datetime.date.today())
  input_liters = st.number_input(
      "公升數 (L)", min_value=0.1, max_value=200.0, value=40.0, step=0.1
  )
  input_price = st.number_input(
      "單價 (元/公升)", min_value=1.0, max_value=100.0, value=31.0, step=0.1
  )

  # 提交按鈕
  submitted = st.form_submit_button("新增記錄")

  if submitted:
    total_cost = round(input_liters * input_price, 2)
    new_data = pd.DataFrame(
        {
            "日期": [input_date],
            "公升": [input_liters],
            "單價": [input_price],
            "總金額": [total_cost],
        }
    )

    # 將新資料加入 Session State
    st.session_state.fuel_data = pd.concat(
        [st.session_state.fuel_data, new_data], ignore_index=True
    )
    st.sidebar.success("成功新增記錄！")

# 3. 主頁面：數據展示與統計
st.subheader("📊 歷史加油記錄清單")

if not st.session_state.fuel_data.empty:
  # 排序資料（依日期新到舊）
  df_display = st.session_state.fuel_data.sort_values(
      by="日期", ascending=False
  ).reset_index(drop=True)

  # 顯示總計數據卡片
  total_spent = df_display["總金額"].sum()
  total_liters = df_display["公升"].sum()
  avg_price = (
      round(total_spent / total_liters, 2) if total_liters > 0 else 0
  )

  col1, col2, col3 = st.columns(3)
  col1.metric("累積總花費", f"$ {total_spent:,.2f}")
  col2.metric("累積總公升數", f"{total_liters:,.2f} L")
  col3.metric("平均油價", f"$ {avg_price} /L")

  st.divider()

  # 顯示表格
  st.dataframe(df_display, use_container_width=True)

  # 4. 簡單圖表分析（油價趨勢）
  st.subheader("📈 油價與總花費趨勢")
  chart_data = df_display.sort_values(by="日期")
  st.line_chart(chart_data.set_index("日期")[["單價"]])

  # 5. 匯出 CSV 功能
  csv = df_display.to_csv(index=False).encode("utf-8-sig")
  st.download_button(
      label="📥 下載記錄 CSV 檔案",
      data=csv,
      file_name="fuel_records.csv",
      mime="text/csv",
  )

else:
  st.info("目前尚無記錄，請從左側欄位新增您的第一筆加油資料。")
