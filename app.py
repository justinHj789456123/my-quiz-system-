import streamlit as st
import pandas as pd

# 設定頁面與專業風格
st.set_page_config(page_title="數位考官", layout="centered")
st.title("🎯 數位考官：專屬題庫測驗系統")

# 1) 初始確認與範圍設定
if 'df' not in st.session_state:
    st.info("請上傳自訂題庫 Excel 檔 (.xlsx) 以開始測驗。")
    uploaded_file = st.file_uploader("上傳題庫", type=["xlsx"])
    if uploaded_file:
        st.session_state.df = pd.read_excel(uploaded_file)
        st.rerun()
else:
    df = st.session_state.df
    total_rows = len(df)
    
    with st.sidebar:
        st.header("⚙️ 測驗參數設定")
        start_q = st.number_input("起始題號", 1, total_rows, 1) #
        end_q = st.number_input("結束題號", start_q, total_rows, total_rows) #
        num_draw = st.number_input("抽考總題數", 1, (end_q - start_q + 1), 10) #
        
        mode = st.radio("測驗呈現偏好", ["一次僅顯示一題", "一次性呈現所有題目"]) #
        
        if st.button("確認範圍並開始"):
            # 2) 抽題規範：隨機抽題
            pool = df.iloc[start_q-1 : end_q]
            st.session_state.quiz_data = pool.sample(n=num_draw).to_dict('records')
            st.session_state.current_idx = 0
            st.session_state.user_ans = {}
            st.session_state.active = True
            st.session_state.done = False
            st.rerun()

    # 2) & 3) 測驗執行與流程管理
    if st.session_state.get('active') and not st.session_state.get('done'):
        quiz = st.session_state.quiz_data
        
        if mode == "一次僅顯示一題": #
            idx = st.session_state.current_idx
            q = quiz[idx]
            st.subheader(f"進度：{idx + 1} / {len(quiz)}")
            st.markdown("---")
            # 2c) 嚴格格式呈現
            st.write(f"**題號：** {q.get('題號', 'N/A')}")
            st.write(f"**題目：** {q.get('題目', '')}")
            
            opts = [f"A. {q.get('A','')}", f"B. {q.get('B','')}", f"C. {q.get('C','')}", f"D. {q.get('D','')}"]
            ans = st.radio("選項：", opts, key=f"q_{idx}")
            
            if st.button("下一題"):
                st.session_state.user_ans[idx] = ans[0]
                if idx < len(quiz) - 1:
                    st.session_state.current_idx += 1
                    st.rerun()
                else:
                    st.session_state.done = True
                    st.rerun()
        
        else: # 一次性呈現
            with st.form("quiz_form"):
                for i, q in enumerate(quiz):
                    st.write(f"**題號：** {q.get('題號','')}")
                    st.write(f"**題目：** {q.get('題目','')}")
                    st.radio("選項：", [f"A. {q.get('A','')}", f"B. {q.get('B','')}", f"C. {q.get('C','')}", f"D. {q.get('D','')}"] , key=f"f_{i}")
                if st.form_submit_button("繳卷"):
                    st.session_state.done = True
                    st.rerun()

    # 3b) 正確答案核對
    elif st.session_state.get('done'):
        st.success("測驗結束，請核對正確答案。")
        if st.button("重新開始"):
            st.session_state.active = False
            st.rerun()