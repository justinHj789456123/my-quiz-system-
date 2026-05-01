import streamlit as st
import pandas as pd

# 設定網頁標題
st.set_page_config(page_title="數位考官 - 工程品質測驗", layout="centered")

@st.cache_data
def load_data():
    """讀取 2878 題大型題庫檔案"""
    try:
        df = pd.read_excel("公共工程品質管理訓練班_機電班題庫.xlsx")
        df['序號'] = df['序號'].astype(int)
        df['課程名稱'] = df['課程名稱'].astype(str).str.strip()
        return df
    except Exception:
        return None

def main():
    df = load_data()
    
    # 嚴格檢查數據載入
    if df is None:
        st.error("❌ 讀取失敗：請確認檔案『公共工程品質管理訓練班_機電班題庫.xlsx』已上傳。")
        return

    # 初始化狀態管理
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # --- 1. 初始確認與範圍設定 (行為與規則 1) ---
    if not st.session_state.quiz_started:
        st.sidebar.header("⚙️ 測驗參數設定")
        
        # 課程單元分類
        all_units = sorted(df['課程名稱'].unique().tolist())
        selected_unit = st.sidebar.selectbox("1. 選擇測驗單元", ["【全部單元隨機抽】"] + all_units)
        
        # 確保 pool 在此範圍內始終有效
        pool = df if selected_unit == "【全部單元隨機抽】" else df[df['課程名稱'] == selected_unit]
        
        min_id = int(pool['序號'].min())
        max_id = int(pool['序號'].max())
        
        st.sidebar.info(f"可用題號範圍：{min_id} ~ {max_id}")
        start_num = st.sidebar.number_input("起始題號", min_id, max_id, min_id)
        end_num = st.sidebar.number_input("結束題號", start_num, max_id, max_id)
        
        max_range_count = (end_num - start_num) + 1
        total_draw = st.sidebar.number_input("想要抽考的總題數", 1, max_range_count, min(10, max_range_count))

        if st.sidebar.button("確認範圍並開始測驗", use_container_width=True):
            # --- 2. 抽題與呈現規範 (行為與規則 2) ---
            target_pool = pool[(pool['序號'] >= start_num) & (pool['序號'] <= end_num)]
            # 隨機抽取並存入 Session
            st.session_state.quiz_set = target_pool.sample(n=int(total_draw)).to_dict('records')
            st.session_state.user_answers = {}
            st.session_state.quiz_started = True
            st.session_state.submitted = False
            st.rerun()

    # --- 3. 測驗執行介面 ---
    else:
        st.title("🎓 數位考官")
        
        if not st.session_state.submitted:
            # 測驗模式
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.quiz_set):
                    st.markdown(f"### 題號：{i+1}")
                    st.markdown(f"**題目（原序號 {q['序號']}）：**")
                    st.write(q['題目內容']) # 嚴格原文呈現
                    
                    st.session_state.user_answers[i] = st.radio(
                        "選項：", ["A", "B", "C", "D"], key=f"q_{i}", index=None
                    )
                    st.write("---")
                
                if st.form_submit_button("交卷並核對答案", use_container_width=True):
                    st.session_state.submitted = True
                    st.rerun()
        else:
            # --- 4. 錯誤複習與統計 (行為與規則 3) ---
            correct_count = 0
            wrong_questions = []

            for i, q in enumerate(st.session_state.quiz_set):
                u_ans = st.session_state.user_answers.get(i)
                correct_ans = str(q['正確答案']).strip().upper()
                if str(u_ans) == correct_ans:
                    correct_count += 1
                else:
                    wrong_questions.append({'q': q, 'u_ans': u_ans})

            st.success(f"測驗結束！答對率：{(correct_count/len(st.session_state.quiz_set))*100:.2f}% ({correct_count}/{len(st.session_state.quiz_set)})")

            # 錯誤複習區塊
            if wrong_questions:
                st.subheader("❌ 錯誤複習專區")
                for item in wrong_questions:
                    with st.expander(f"原序號：{item['q']['序號']} - 點擊查看詳情", expanded=True):
                        st.write(f"**題目：** {item['q']['題目內容']}")
                        st.markdown(f"**您的答案：** `{item['u_ans']}` | **正確答案：** `{item['q']['正確答案']}`")
            else:
                st.balloons()
                st.success("完美！全部答對。")

            if st.button("回主畫面重新設定"):
                # 清除所有測驗狀態以重啟
                st.session_state.quiz_started = False
                st.session_state.submitted = False
                st.session_state.pop('quiz_set', None)
                st.rerun()
