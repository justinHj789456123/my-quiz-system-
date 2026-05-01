import streamlit as st
import pandas as pd
import random

# 設置頁面標題與風格
st.set_page_config(page_title="數位考官 - 專業測驗系統", layout="centered")

@st.cache_data(show_spinner="數位考官正在準備題庫...")
def load_data():
    """高效讀取並預處理大型題庫"""
    try:
        df = pd.read_excel("公共工程品質管理訓練班_機電班題庫.xlsx")
        # 確保數據乾淨：去除空行、統一轉字串
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
        st.error("❌ 讀取失敗。請確認題庫檔案已正確上傳至根目錄。")
        return

    # --- 初始化 Session State (確保不會在 Rerun 時丟失數據) ---
    if 'wrong_pool' not in st.session_state:
        st.session_state.wrong_pool = []  # 累積錯題池
    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = False
    if 'quiz_set' not in st.session_state:
        st.session_state.quiz_set = []

    # --- 側邊欄：考官控制台 ---
    st.sidebar.header("⚙️ 考官控制台")
    mode = st.sidebar.radio("測驗模式", ["一般抽測", f"錯題累積重考 ({len(st.session_state.wrong_pool)})"])

    # --- 邏輯 A：設定階段 ---
    if not st.session_state.quiz_active:
        if mode == "一般抽測":
            all_units = sorted(df['課程名稱'].unique().tolist())
            selected_unit = st.sidebar.selectbox("1. 選擇單元", ["全部單元隨機"] + all_units)
            
            pool = df if selected_unit == "全部單元隨機" else df[df['課程名稱'] == selected_unit]
            min_id, max_id = int(pool['序號'].min()), int(pool['序號'].max())
            
            st.sidebar.info(f"當前可用序號：{min_id} ~ {max_id}")
            start_num = st.sidebar.number_input("起始序號", min_id, max_id, min_id)
            end_num = st.sidebar.number_input("結束序號", start_num, max_id, max_id)
            
            range_pool = pool[(pool['序號'] >= start_num) & (pool['序號'] <= end_num)]
            draw_num = st.sidebar.number_input("抽考題數", 1, len(range_pool), min(10, len(range_pool)))

            if st.sidebar.button("確認範圍並開始", use_container_width=True):
                st.session_state.quiz_set = range_pool.sample(n=int(draw_num)).to_dict('records')
                st.session_state.quiz_active = True
                st.session_state.submitted = False
                st.session_state.user_answers = {}
                st.rerun()

        else: # 錯題重考模式
            if not st.session_state.wrong_pool:
                st.sidebar.warning("目前尚無累積錯題。")
            else:
                if st.sidebar.button("開始錯題重考", use_container_width=True):
                    # 複製錯題池並打亂順序
                    st.session_state.quiz_set = random.sample(st.session_state.wrong_pool, len(st.session_state.wrong_pool))
                    st.session_state.quiz_active = True
                    st.session_state.submitted = False
                    st.session_state.user_answers = {}
                    st.rerun()

    # --- 邏輯 B：測驗階段 ---
    else:
        st.title("🎓 數位考官：測驗進行中")
        
        if not st.session_state.get('submitted', False):
            # 使用單次 Form 提交，避免大數據量下每次點擊 Radio 都導致整體重整
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.quiz_set):
                    st.markdown(f"**題號：{i+1}** (原序號：{q['序號']})")
                    st.write(q['題目內容']) # 嚴格原文呈現
                    st.session_state.user_answers[i] = st.radio("選項", ["A", "B", "C", "D"], key=f"q_{i}_{q['序號']}", index=None)
                    st.write("---")
                
                if st.form_submit_button("交卷並核對答案", use_container_width=True):
                    st.session_state.submitted = True
                    st.rerun()
        else:
            # --- 邏輯 C：核對答案與累積錯題 ---
            correct = 0
            current_wrongs = []
            
            for i, q in enumerate(st.session_state.quiz_set):
                u_ans = st.session_state.user_answers.get(i)
                if str(u_ans) == q['正確答案']:
                    correct += 1
                    # 答對：從累積池移除該題
                    st.session_state.wrong_pool = [item for item in st.session_state.wrong_pool if item['序號'] != q['序號']]
                else:
                    current_wrongs.append({'q': q, 'u_ans': u_ans})
                    # 答錯：加入累積池 (避免重複)
                    if q['序號'] not in [x['序號'] for x in st.session_state.wrong_pool]:
                        st.session_state.wrong_pool.append(q)

            st.success(f"測驗結束！答對率：{(correct/len(st.session_state.quiz_set))*100:.1f}% ({correct}/{len(st.session_state.quiz_set)})")

            if current_wrongs:
                st.subheader("❌ 錯誤解析（已加入累積池）")
                for w in current_wrongs:
                    with st.expander(f"序號 {w['q']['序號']} 詳細內容"):
                        st.write(f"**題目：** {w['q']['題目內容']}")
                        st.write(f"**您的答案：** {w['u_ans']} | **正確答案：** {w['q']['正確答案']}")
            else:
                st.balloons()
                st.success("全部答對！")

            if st.button("回主畫面"):
                st.session_state.quiz_active = False
                st.rerun()

if __name__ == "__main__":
    main()
