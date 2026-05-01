import streamlit as st
import pandas as pd
import random

# 設定網頁標題
st.set_page_config(page_title="工程品質專業測驗", layout="centered")

def load_data():
    """讀取 Excel 題庫檔案"""
    try:
        df = pd.read_excel("公共工程品質管理訓練班_機電班題庫.xlsx")
        return df
    except Exception:
        st.error("找不到題庫檔案，請確保『公共工程品質管理訓練班_機電班題庫.xlsx』已上傳至 GitHub。")
        return None

def main():
    df = load_data()
    if df is None:
        return

    # 1. 初始確認與範圍設定
    st.sidebar.header("⚙️ 測驗參數設定")
    
    # 選擇單元
    unit_options = ["【全部題目隨機抽】"] + df['課程名稱'].unique().tolist()
    selected_unit = st.sidebar.selectbox("1. 選擇單元範圍", unit_options)
    
    if selected_unit == "【全部題目隨機抽】":
        pool = df
    else:
        pool = df[df['課程名稱'] == selected_unit]
    
    # 2. 設定題號區間
    min_idx = int(pool['序號'].min())
    max_idx = int(pool['序號'].max())
    
    start_num, end_num = st.sidebar.slider(
        "設定題號區間", 
        min_idx, max_idx, (min_idx, max_idx)
    )
    
    # 3. 抽題數量
    max_draw = (end_num - start_num) + 1
    total_draw = st.sidebar.number_input("2. 抽考總題數", min_value=1, max_value=max_draw, value=min(10, max_draw))
    
    # 呈現偏好
    display_mode = st.sidebar.radio("測驗呈現偏好", ["一次性呈現所有題目", "一次僅顯示一題"])

    st.title("🎓 工程品質專業測驗")
    st.write("---")

    # 初始化狀態
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False

    if not st.session_state.quiz_started:
        st.write(f"**測驗範圍：** 第 {start_num} 題至第 {end_num} 題")
        st.write(f"**抽取題數：** {total_draw} 題")
        if st.button("確認範圍並開始測驗", use_container_width=True):
            # 抽題規範：原文呈現[cite: 1]
            final_pool = pool[(pool['序號'] >= start_num) & (pool['序號'] <= end_num)]
            st.session_state.questions = final_pool.sample(n=int(total_draw)).to_dict('records')
            st.session_state.user_answers = {}
            st.session_state.quiz_started = True
            st.rerun()
    else:
        # 執行測驗流程
        questions = st.session_state.questions
        
        with st.form("quiz_form"):
            for i, q in enumerate(questions):
                # 嚴格遵守呈現格式
                st.subheader(f"題號：{i+1}")
                st.write(f"**題目：** {q['題目內容']}") # 原文呈現[cite: 1]
                st.session_state.user_answers[i] = st.radio(
                    "選項：", ["A", "B", "C", "D"], key=f"q_{i}", index=None
                )
                st.write("---")
            
            if st.form_submit_button("交卷並核對答案"):
                correct = 0
                for i, q in enumerate(questions):
                    ans = st.session_state.user_answers.get(i)
                    if str(ans) == str(q['正確答案']).strip().upper():
                        correct += 1
                
                st.success(f"測驗結束！您的得分：{correct} / {len(questions)}")
                st.info(f"正確率：{(correct/len(questions))*100:.2f}%")

        if st.button("重新設定範圍"):
            st.session_state.quiz_started = False
            st.rerun()

if __name__ == "__main__":
    main()
