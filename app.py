import streamlit as st
import pandas as pd

# 設定網頁標題與風格
st.set_page_config(page_title="數位考官 - 工程品質測驗", layout="centered")

@st.cache_data
def load_data():
    """讀取 2878 題大型題庫檔案"""
    try:
        # 確保檔案路徑正確，且讀取時不造成系統卡頓
        df = pd.read_excel("公共工程品質管理訓練班_機電班題庫.xlsx")
        # 預處理資料：確保序號為整數，課程名稱不含多餘空格
        df['序號'] = df['序號'].astype(int)
        df['課程名稱'] = df['課程名稱'].astype(str).str.strip()
        return df
    except Exception:
        return None

def main():
    df = load_data()
    
    # 處理讀取失敗的情況，避免 NameError
    if df is None:
        st.error("❌ 讀取失敗：請確認檔案『公共工程品質管理訓練班_機電班題庫.xlsx』已正確上傳至 GitHub 根目錄。")
        return

    # --- 1. 初始確認與範圍設定 ---
    st.sidebar.header("⚙️ 測驗參數設定")
    
    # 自動抓取所有單元分類
    all_units = sorted(df['課程名稱'].unique().tolist())
    selected_unit = st.sidebar.selectbox("1. 選擇測驗單元", ["【全部單元隨機抽】"] + all_units)
    
    # 根據選擇的單元篩選出可用的題池
    pool = df if selected_unit == "【全部單元隨機抽】" else df[df['課程名稱'] == selected_unit]
    
    # 動態獲取該範圍的題號 (解決截圖中的 NameError 問題)
    min_id = int(pool['序號'].min())
    max_id = int(pool['序號'].max())
    
    # 側邊欄顯示可用範圍
    st.sidebar.info(f"當前範圍可用題號：{min_id} ~ {max_id}")
    
    start_num = st.sidebar.number_input("起始題號", min_id, max_id, min_id)
    end_num = st.sidebar.number_input("結束題號", start_num, max_id, max_id)
    
    # 抽題數量邏輯
    max_range_count = (end_num - start_num) + 1
    total_draw = st.sidebar.number_input("想要抽考的總題數", 1, max_range_count, min(10, max_range_count))

    if st.sidebar.button("確認範圍並開始測驗", use_container_width=True):
        # --- 2. 抽題與呈現規範 ---
        # 嚴格過濾使用者選擇的範圍並進行隨機抽取
        target_pool = pool[(pool['序號'] >= start_num) & (pool['序號'] <= end_num)]
        st.session_state.quiz_set = target_pool.sample(n=int(total_draw)).to_dict('records')
        st.session_state.user_answers = {}
        st.session_state.started = True
        st.rerun()

    # --- 3. 測驗執行介面 ---
    if st.session_state.get('started'):
        st.title(f"🎓 數位考官：{selected_unit}")
        st.write(f"本次抽測：{len(st.session_state.quiz_set)} 題")
        
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_set):
                # 滿足需求：顯示原題庫序號
                st.markdown(f"### 測驗第 {i+1} 題")
                st.markdown(f"**【原題庫序號：{q['序號']}】**")
                # 原文呈現：禁止修改文字、專有名詞
                st.write(f"題目：{q['題目內容']}")
                
                st.session_state.user_answers[i] = st.radio(
                    f"選擇答案 (Q{i+1})", ["A", "B", "C", "D"], key=f"q_{i}", index=None
                )
                st.write("---")
            
            # --- 4. 測驗流程管理 ---
            if st.form_submit_button("交卷並核對答案", use_container_width=True):
                correct = 0
                for idx, q in enumerate(st.session_state.quiz_set):
                    u_ans = st.session_state.user_answers.get(idx)
                    # 嚴格比對正確答案
                    if str(u_ans) == str(q['正確答案']).strip().upper():
                        correct += 1
                
                st.success(f"測驗結束！總答對題數：{correct} / {len(st.session_state.quiz_set)}")
                st.metric("正確率", f"{(correct/len(st.session_state.quiz_set))*100:.2f}%")
        
        if st.button("重新設定範圍"):
            st.session_state.started = False
            st.rerun()

if __name__ == "__main__":
    main()
