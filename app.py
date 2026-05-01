import streamlit as st
import pandas as pd
import random

# 設定網頁標題與布局
st.set_page_config(page_title="數位考官", layout="centered")

@st.cache_data(show_spinner="考官正在準備題庫...")
def load_data():
    """高效讀取並處理大型題庫"""
    try:
        # 直接讀取 Excel 檔案
        df = pd.read_excel("公共工程品質管理訓練班_機電班題庫.xlsx")
        # 排除空行並規範格式
        df = df.dropna(subset=['題目內容', '正確答案'])
        df['序號'] = df['序號'].astype(int)
        df['課程名稱'] = df['課程名稱'].astype(str).str.strip()
        df['正確答案'] = df['正確答案'].astype(str).str.strip().str.upper()
        return df
    except Exception:
        return None

def main():
    df = load_data()
    if df is None:
        st.error("❌ 讀取失敗。請確認題庫檔案名稱正確且已上傳。")
        return

    # --- 初始化 Session State ---
    if 'wrong_pool' not in st.session_state:
        st.session_state.wrong_pool = []  # 累積錯題池
    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = False
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # --- 側邊欄：控制台 ---
    st.sidebar.header("⚙️ 考官控制台")
    
    # 簡化選單：僅保留單元選擇與抽題數
    mode = st.sidebar.radio("測驗模式", ["一般抽測", f"錯題累積重考 ({len(st.session_state.wrong_pool)})"])

    if not st.session_state.quiz_active:
        if mode == "一般抽測":
            all_units = sorted(df['課程名稱'].unique().tolist())
            selected_unit = st.sidebar.selectbox("選擇測驗單元", ["全部單元隨機"] + all_units)
            
            pool = df if selected_unit == "全部單元隨機" else df[df['課程名稱'] == selected_unit]
            
            # 僅保留抽考題數設定，移除起始/結束題號
            max_available = len(pool)
            draw_num = st.sidebar.number_input(f"想要抽考的總題數 (最多 {max_available} 題)", 1, max_available, min(10, max_available))

            if st.sidebar.button("確認並開始測驗", use_container_width=True):
                # 隨機抽取題目並轉換為字典清單儲存
                st.session_state.quiz_set = pool.sample(n=int(draw_num)).to_dict('records')
                st.session_state.user_answers = {}
                st.session_state.quiz_active = True
                st.session_state.submitted = False
                st.rerun()

        else: # 錯題重考
            if not st.session_state.wrong_pool:
                st.sidebar.warning("目前尚無累積錯題。")
            else:
                if st.sidebar.button("開始錯題複習", use_container_width=True):
                    st.session_state.quiz_set = random.sample(st.session_state.wrong_pool, len(st.session_state.wrong_pool))
                    st.session_state.user_answers = {}
                    st.session_state.quiz_active = True
                    st.session_state.submitted = False
                    st.rerun()

    # --- 測驗介面 ---
    if st.session_state.quiz_active:
        st.title("🎓 數位考官")
        
        if not st.session_state.submitted:
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.quiz_set):
                    # 嚴格原文呈現規範
                    st.markdown(f"**題號：{i+1}** (原題庫序號：{q['序號']})")
                    st.write(q['題目內容'])
                    
                    # 使用唯一 Key 防止當機
                    st.session_state.user_answers[i] = st.radio(
                        "選擇答案：", ["A", "B", "C", "D"], 
                        key=f"q_{q['序號']}_{i}", 
                        index=None
                    )
                    st.write("---")
                
                if st.form_submit_button("交卷並核對答案", use_container_width=True):
                    st.session_state.submitted = True
                    st.rerun()
        else:
            # --- 結果核對與累積邏輯 ---
            correct = 0
            wrongs = []
            
            for i, q in enumerate(st.session_state.quiz_set):
                u_ans = st.session_state.user_answers.get(i)
                if str(u_ans) == q['正確答案']:
                    correct += 1
                    # 答對則從錯題池移除
                    st.session_state.wrong_pool = [item for item in st.session_state.wrong_pool if item['序號'] != q['序號']]
                else:
                    wrongs.append({'q': q, 'u_ans': u_ans})
                    # 答錯則加入錯題池
                    if q['序號'] not in [x['序號'] for x in st.session_state.wrong_pool]:
                        st.session_state.wrong_pool.append(q)

            st.success(f"測驗完成！正確率：{(correct/len(st.session_state.quiz_set))*100:.1f}%")

            if wrongs:
                st.subheader("❌ 錯誤複習 (已自動加入累積池)")
                for w in wrongs:
                    with st.expander(f"序號 {w['q']['序號']} 詳細內容"):
                        st.write(f"**題目：** {w['q']['題目內容']}")
                        st.markdown(f"**您的答案：** `{w['u_ans']}` | **正確答案：** `{w['q']['正確答案']}`")
            else:
                st.balloons()
                st.success("完美！全部答對。")

            if st.button("回到設定"):
                st.session_state.quiz_active = False
                st.rerun()

if __name__ == "__main__":
    main()
