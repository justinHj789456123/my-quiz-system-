import streamlit as st
import pandas as pd

# 設置網頁
st.set_page_config(page_title="數位考官 - 工程品質測驗", layout="centered")

@st.cache_data(show_spinner="正在載入 2878 題題庫，請稍候...")
def load_data():
    """高效讀取大型題庫，並處理空值與格式"""
    try:
        # 讀取 Excel
        df = pd.read_excel("公共工程品質管理訓練班_機電班題庫.xlsx")
        # 確保必要欄位存在且無空值
        df['序號'] = df['序號'].fillna(0).astype(int)
        df['課程名稱'] = df['課程名稱'].astype(str).str.strip()
        df['題目內容'] = df['題目內容'].astype(str)
        df['正確答案'] = df['正確答案'].astype(str).str.strip().str.upper()
        return df
    except Exception as e:
        return None

def main():
    df = load_data()
    
    if df is None:
        st.error("❌ 無法載入檔案。請確認『公共工程品質管理訓練班_機電班題庫.xlsx』已位於 GitHub 根目錄。")
        return

    # 初始化狀態
    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = False
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # --- 1. 初始確認與範圍設定 ---
    if not st.session_state.quiz_active:
        st.sidebar.header("⚙️ 測驗參數設定")
        
        all_units = sorted(df['課程名稱'].unique().tolist())
        selected_unit = st.sidebar.selectbox("1. 選擇測驗單元", ["【全部單元隨機抽】"] + all_units)
        
        pool = df if selected_unit == "【全部單元隨機抽】" else df[df['課程名稱'] == selected_unit]
        min_id, max_id = int(pool['序號'].min()), int(pool['序號'].max())
        
        st.sidebar.info(f"當前範圍可用題號：{min_id} ~ {max_id}")
        start_num = st.sidebar.number_input("起始題號", min_id, max_id, min_id)
        end_num = st.sidebar.number_input("結束題號", start_num, max_id, max_id)
        
        range_count = (end_num - start_num) + 1
        total_draw = st.sidebar.number_input("想要抽考的總題數", 1, range_count, min(10, range_count))

        if st.sidebar.button("確認範圍並開始測驗", use_container_width=True):
            target_pool = pool[(pool['序號'] >= start_num) & (pool['序號'] <= end_num)]
            st.session_state.quiz_set = target_pool.sample(n=int(total_draw)).to_dict('records')
            st.session_state.user_answers = {}
            st.session_state.quiz_active = True
            st.session_state.submitted = False
            st.rerun()

    # --- 2. 測驗執行與原文呈現 ---
    else:
        st.title(f"🎓 數位考官：{selected_unit if 'selected_unit' in locals() else ''}")
        
        if not st.session_state.submitted:
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.quiz_set):
                    st.markdown(f"### 測驗題號：{i+1}")
                    st.markdown(f"**【原題庫序號：{q['序號']}】**")
                    st.write(q['題目內容']) # 嚴格原文呈現
                    
                    st.session_state.user_answers[i] = st.radio(
                        "選擇答案：", ["A", "B", "C", "D"], key=f"q_{i}", index=None
                    )
                    st.write("---")
                
                if st.form_submit_button("交卷並核對答案", use_container_width=True):
                    st.session_state.submitted = True
                    st.rerun()
        else:
            # --- 3. 錯誤複習與統計 ---
            correct = 0
            wrongs = []
            for i, q in enumerate(st.session_state.quiz_set):
                u_ans = st.session_state.user_answers.get(i)
                if str(u_ans) == q['正確答案']:
                    correct += 1
                else:
                    wrongs.append({'q': q, 'u_ans': u_ans})

            st.success(f"測驗結束！正確率：{(correct/len(st.session_state.quiz_set))*100:.2f}% ({correct}/{len(st.session_state.quiz_set)})")

            if wrongs:
                st.subheader("❌ 錯誤複習專區")
                for w in wrongs:
                    with st.expander(f"原序號 {w['q']['序號']} - 點擊檢視內容"):
                        st.write(f"**題目：** {w['q']['題目內容']}")
                        st.write(f"**您的答案：** {w['u_ans']} | **正確答案：** {w['q']['正確答案']}")
            else:
                st.balloons()
                st.success("完美！全部答對。")

            if st.button("回主畫面重新設定"):
                st.session_state.quiz_active = False
                st.session_state.submitted = False
                st.rerun()

if __name__ == "__main__":
    main()
