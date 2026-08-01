import streamlit as st

# 設定網頁標題
st.set_page_config(page_title="李白詩詞登入系統", page_icon="📜", layout="centered")

# 初始化 Session State 來追蹤登入狀態
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 主標題
st.title("📜 李白詩詞系統")

# 如果尚未登入，顯示登入表單
if not st.session_state.authenticated:
    st.subheader("請輸入密碼以解鎖詩詞")
    
    with st.form("login_form"):
        # 隱藏輸入的密碼
        password = st.text_input("密碼", type="password", placeholder="請輸入系統密碼")
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
        > **君不见，黄河之水天上来，奔流到海不复回。**  
        > **君不见，高堂明镜悲白发，朝如青丝暮成雪。**  
        > **人生得意须尽欢，莫使金樽空对月。**  
        > **天生我材必有用，千金散尽还复来。**  
        > 
        > — *唐·李白*
        """
    )
    
    st.markdown("---")
    
    # 登出按鈕
    if st.button("登出"):
        st.session_state.authenticated = False
        st.rerun()
