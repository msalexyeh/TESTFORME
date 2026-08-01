from datetime import datetime
import os
import pandas as pd
import streamlit as st

# --- 1. 設定檔案路徑與資料夾 ---
CSV_FILE = "fuel_records.csv"
UPLOAD_FOLDER = "uploads"

# 確保上傳照片的資料夾存在
if not os.path.exists(UPLOAD_FOLDER):
  os.makedirs(UPLOAD_FOLDER)


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
    # 建立空的 DataFrame 結構（新增「照片檔名」欄位）
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
            "照片檔名",
        ]
    )


def save_data(df):
  """將 DataFrame 儲存至 CSV 檔案"""
  df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")


# --- 2. 介面設計 ---
st.set_page_config(page_title="行車油耗記錄系統", page_icon="⛽", layout="wide")

st.title("⛽ 駕駛油耗與加油記錄系統 (含照片上傳)")
st.write(
    "記錄每次加油的詳細資訊、自由輸入駕駛人，並可上傳加油發票或里程表照片。"
)

# 載入現有資料
df_existing = load_data()

# 確保 DataFrame 包含「照片檔名」欄位（防範舊 CSV 缺少該欄位）
if "照片檔名" not in df_existing.columns:
  df_existing["照片檔名"] = ""

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

  # 照片上傳欄位（注意：Streamlit 的 file_uploader 在 form 內支援把檔案物件傳遞出來）
  uploaded_file = st.file_uploader(
      "上傳加油發票 / 里程表照片 (選填)", type=["jpg", "jpeg", "png"]
  )

  # 提交按鈕
  submitted = st.form_submit_button("送出並儲存記錄")

  if submitted:
    # 檢查是否填寫駕駛人
    if not driver.strip():
      st.warning("⚠️ 請輸入駕駛人姓名！")
    else:
      # 處理照片儲存
      photo_filename = ""
      if uploaded_file is not None:
        # 為了避免檔名重複，加上時間戳記
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        photo_filename = f"{timestamp_str}_{uploaded_file.name}"
        file_path = os.path.join(UPLOAD_FOLDER, photo_filename)

        # 儲存照片到 uploads/ 資料夾
        with open(file_path, "wb") as f:
          f.write(uploaded_file.getbuffer())

      # 計算總價
      total_price = round(unit_price * liters, 2)

      # 計算行駛里程與平均油耗
      if last_km > 0 and current_km > last_km:
        trip_distance = current_km - last_km
        avg_consumption = round(trip_distance / liters, 2)
      else:
        trip_distance = 0
        avg_consumption = 0.0

      # 準備新資料行
      new_row = pd.DataFrame(
          [
              {
                  "日期": str(fuel_date),
                  "駕駛人": driver.strip(),
                  "單價": unit_price,
                  "公升數": liters,
                  "總價": total_price,
                  "目前公里數": current_km,
                  "行駛里程": trip_distance,
                  "平均油耗": avg_consumption,
                  "照片檔名": photo_filename,
              }
          ]
      )

      # 將新資料加入現有 DataFrame
      df_existing = pd.concat([df_existing, new_row], ignore_index=True)

      # 儲存回 CSV
      save_data(df_existing)
      st.success("✅ 記錄成功，照片與資料已儲存！")
      st.balloons()
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

  # 照片檢視區塊
  st.markdown("### 🖼️ 加油照片檢視")
  # 篩選出有上傳照片的記錄
  records_with_photo = df_existing[
      df_existing["照片檔名"].notna() & (df_existing["照片檔名"] != "")
  ]

  if not records_with_photo.empty:
    # 讓使用者選擇要檢視哪一筆記錄的照片
    selected_record = st.selectbox(
        "選擇要檢視照片的記錄（依日期與駕駛人）",
        options=records_with_photo.index,
        format_func=lambda x: (
            f"日期: {records_with_photo.loc[x, '日期']} |"
            f" 駕駛: {records_with_photo.loc[x, '駕駛人']} |"
            f" 總價: {records_with_photo.loc[x, '總價']}元"
        ),
    )

    if selected_record is not None:
      p_name = records_with_photo.loc[selected_record, "照片檔名"]
      p_path = os.path.join(UPLOAD_FOLDER, str(p_name))
      if os.path.exists(p_path):
        st.image(p_path, caption=f"上傳的照片: {p_name}", width=400)
      else:
        st.warning("⚠️ 找不到對應的照片檔案（可能已被刪除）。")
  else:
    st.info("目前尚無上傳任何照片記錄。")

  # 簡單統計數據
  st.markdown("---")
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
