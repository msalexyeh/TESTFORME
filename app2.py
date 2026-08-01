import streamlit as st

# 設定網頁標題
st.set_page_config(page_title="登入測試系統", page_icon="📜", layout="centered")

# 初始化 Session State 來追蹤登入狀態
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 主標題
st.title("📜 登入測試")

# 如果尚未登入，顯示登入表單
if not st.session_state.authenticated:
    st.subheader("請輸入密碼")
    
    with st.form("login_form"):
        # 隱藏輸入的密碼
        password = st.text_input("密碼", type="password", placeholder="請輸入系統密碼 *提示h開頭")
        submit_button = st.form_submit_button("登入")
        
        if submit_button:
            # 從 Streamlit Secrets 讀取密碼，程式碼內不出現明文密碼
            if password == st.secrets["PASSWORD"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("密碼錯誤，請重新輸入！")

# 如果已經登入成功，顯示詩詞
else:
    st.success("登入成功！歡迎進入詩詞世界。")
    
    st.markdown("---")
    
    # 顯示李白詩詞
    st.header("《將進酒》")
    st.markdown(
        """
        > **君不見，黄河之水天上來，奔流到海不復回。**  
        > **君不見，高堂明鏡悲白髮，朝如青絲暮成雪。**  
        > **人生得意須盡歡，莫使金樽空對月。**  
        > **天生我材必有用，千金散盡還復來。**  
        > 
        > — *唐·李白*
        """
    )
    
    st.markdown("---")
    
    # 登出按鈕
    if st.button("登出"):
        st.session_state.authenticated = False
        st.rerun()
