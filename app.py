from datetime import datetime
import os
import pandas as pd
import streamlit as st

# --- 1. 設定 CSV 檔案路徑 ---
CSV_FILE = "fuel_records.csv"


def load_data():
  """載入 CSV 檔案，如果不存在則建立一個空的 DataFrame"""
  if os.path.exists(CSV_FILE):
    try:
      df = pd.read_csv(CSV_FILE)
      return df
    except Exception as e:
      st.error(f"讀取 CSV 檔案失敗: {e}")
      return pd.DataFrame()
  else:
    # 建立空的 DataFrame 結構
    return pd.DataFrame(
        columns=[
            "日期",
            "駕駛人",
            "單價",
            "公升數",
            "總價",
            "目前公里數",
            "行駛里程",
            "平均油耗",
        ]
    )


def save_data(df):
  """將 DataFrame 儲存至 CSV 檔案"""
  df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")


# --- 2. 介面設計 ---
st.set_page_config(page_title="行車油耗記錄系統", page_icon="⛽", layout="wide")

st.title("⛽ 駕駛油耗與加油記錄系統 (CSV 本機版)")
st.write("記錄每次加油的詳細資訊，資料將直接儲存並可隨時匯出為 CSV。")

# 載入現有資料
df_existing = load_data()

# 找出上一筆的公里數（如果有的話）
last_km = 0
if not df_existing.empty and "目前公里數" in df_existing.columns:
  try:
    last_km = int(df_existing["目前公里數"].iloc[-1])
  except:
    last_km = 0

# --- 3. 加油表單輸入 ---
with st.form("fuel_form"):
  st.subheader("📝 輸入本次加油資訊")

  col1, col2 = st.columns(2)
  with col1:
    fuel_date = st.date_input("加油日期", datetime.now())
    driver = st.text_input("駕駛人姓名", value="", placeholder="例如：王小明")
    unit_price = st.number_input(
        "油價單價 (元/公升)", min_value=0.0, format="%.2f", value=30.0
    )

  with col2:
    liters = st.number_input(
        "公升數 (L)", min_value=0.0, format="%.2f", value=40.0
    )
    current_km = st.number_input(
        "目前總公里數 (km)",
        min_value=last_km,
        value=last_km,
        help=f"上一筆記錄的公里數為: {last_km} km",
    )

  # 提交按鈕
  submitted = st.form_submit_button("送出並儲存記錄")

  if submitted:
    # 計算總價
    total_price = round(unit_price * liters, 2)
  if not driver.strip():
      st.warning("⚠️ 請輸入駕駛人姓名！")

    # 計算行駛里程與平均油耗
    if last_km > 0 and current_km > last_km:
      trip_distance = current_km - last_km
      # 平均油耗計算 (km/L)
      avg_consumption = round(trip_distance / liters, 2)
    else:
      trip_distance = 0
      avg_consumption = 0.0

    # 準備新資料行
    new_row = pd.DataFrame(
        [
            {
                "日期": str(fuel_date),
                "駕駛人": driver,
                "單價": unit_price,
                "公升數": liters,
                "總價": total_price,
                "目前公里數": current_km,
                "行駛里程": trip_distance,
                "平均油耗": avg_consumption,
            }
        ]
    )

    # 將新資料加入現有 DataFrame
    df_existing = pd.concat([df_existing, new_row], ignore_index=True)

    # 儲存回 CSV
    save_data(df_existing)
    st.success("✅ 記錄成功已儲存至 CSV 檔案！")
    st.balloons()
    # 重新整理頁面以更新資料與欄位
    st.rerun()

# --- 4. 顯示歷史記錄與數據分析 ---
st.markdown("---")
st.subheader("📊 歷史加油記錄")

if not df_existing.empty:
  st.dataframe(df_existing, use_container_width=True)

  # 下載 CSV 按鈕
  csv_data = df_existing.to_csv(index=False, encoding="utf-8-sig").encode(
      "utf-8-sig"
  )
  st.download_button(
      label="📥 下載完整 CSV 記錄檔",
      data=csv_data,
      file_name="fuel_records.csv",
      mime="text/csv",
  )

  # 簡單統計數據
  col_a, col_b, col_c = st.columns(3)
  with col_a:
    total_spent = (
        df_existing["總價"].sum() if "總價" in df_existing.columns else 0
    )
    st.metric(label="總加油花費", value=f"$ {total_spent:,.2f}")
  with col_b:
    total_liters = (
        df_existing["公升數"].sum() if "公升數" in df_existing.columns else 0
    )
    st.metric(label="總加油公升數", value=f"{total_liters:,.2f} L")
  with col_c:
    valid_oil = df_existing[df_existing["平均油耗"] > 0]
    if not valid_oil.empty:
      avg_eff = valid_oil["平均油耗"].mean()
      st.metric(label="平均油耗 (km/L)", value=f"{avg_eff:.2f} km/L")
    else:
      st.metric(label="平均油耗 (km/L)", value="0.00 km/L")
else:
  st.info("目前尚無歷史記錄，請在上方填寫第一筆資料。")
