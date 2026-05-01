import streamlit as st
import pandas as pd

# 設定網頁標題與風格
st.set_page_config(page_title="工程品質專業測驗系統", layout="centered")

@st.cache_data
def load_data():
    """高效讀取 2878 題大型題庫"""
    try:
        df = pd.read_excel("公共工程品質管理訓練班_機電班題庫.xlsx")
        # 確保重要欄位格式正確
        df['序號'] = df['序號'].astype(int)
        df['課程名稱'] = df['課程名稱'].astype(str).strip()
        return df
    except Exception:
        st.error("讀取失敗：請確認檔案『公共工程品質管理訓練班_機電班題庫.xlsx』已上傳至 GitHub 根目錄。")
        return None

def main():
    df = load_data()
    if df is None: return

    # 1. 初始確認與範圍設定 (行為規則 1)
    st.sidebar.header("⚙️ 數位考官參數設定")
    
    # 單元分類選擇 (新增功能)
    all_units = sorted(df['課程名稱'].unique().tolist())
    selected_unit = st.sidebar.selectbox("1. 選擇測驗單元", ["【全部單元隨機抽】"] + all_units)
    
    # 根據單元篩選題池
    pool = df if selected_unit == "【全部單元隨機抽】" else df[df['課程名稱'] == selected_unit]
    
    # 設定範圍
    min_id, max_id = int(pool['序號'].min()), int(pool['序號'].max())
    st.sidebar.write(f"當前單元題號範圍：{min_id} ~ {max_id}")
    
    start_num = st.sidebar.number_input("起始題號", min_id, max_id, min_id)
    end_num = st.sidebar.number_input("結束題號", start_num, max_id, max_id)
    
    # 抽題數量
    range_count = (end_num - start_num) + 1
    total_draw = st.sidebar.number_input("想要抽考的總題數", 1, range_count, min(30, range_count))
    
    # 2. 抽題與呈現規範 (行為規則 2)
    if st.sidebar.button("確認範圍並開始測驗", use_container_width=True):
        target_pool = pool[(pool['序號'] >= start_num) & (pool['序號'] <= end_num)]
        # 使用隨機演算法抽取題目
        st.session_state.quiz_set = target_pool.sample(n=int(total_draw)).to_dict('records')
        st.session_state.user_answers = {}
        st.session_state.quiz_started = True
        st.rerun()

    # 3. 測驗執行介面
    if st.session_state.get('quiz_started'):
        st.title(f"🎓 數位考官：{selected_unit}")
        st.write(f"本次測驗共 {len(st.session_state.quiz_set)} 題")
        st.write("---")

        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_set):
                # 嚴格遵守格式：題號、題目 (包含原題號)、選項
                st.markdown(f"### 測驗題號：{i+1}")
                st.markdown(f"**【原題庫題號：{q['序號']}】**") # 滿足讓您知道原題號的需求
                st.write(f"題目：{q['題目內容']}") # 原文呈現
                
                st.session_state.user_answers[i] = st.radio(
                    f"選擇答案 (Q{i+1})", ["A", "B", "C", "D"], key=f"q_{i}", index=None
                )
                st.write("---")
            
            # 4. 測驗流程管理 (行為規則 3)
            if st.form_submit_button("交卷並核對答案", use_container_width=True):
                correct = 0
                for idx, q in enumerate(st.session_state.quiz_set):
                    u_ans = st.session_state.user_answers.get(idx)
                    if str(u_ans) == str(q['正確答案']).strip().upper():
                        correct += 1
                
                st.success(f"測驗結束！總答對題數：{correct} / {len(st.session_state.quiz_set)}")
                st.metric("正確率", f"{(correct/len(st.session_state.quiz_set))*100:.2f}%")
        
        if st.button("重新設定測驗"):
            st.session_state.quiz_started = False
            st.rerun()

if __name__ == "__main__":
    main()
