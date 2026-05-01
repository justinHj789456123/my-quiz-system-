import streamlit as st
import pandas as pd
import random

# 設定網頁標題與布局
st.set_page_config(page_title="數位考官 - 專屬測驗系統", layout="centered")

@st.cache_data(show_spinner="正在載入題庫，請稍候...")
def load_data():
    """讀取並預處理 2878 題大型題庫"""
    try:
        df = pd.read_excel("公共工程品質管理訓練班_機電班題庫.xlsx")
        # 數據清洗：確保序號、內容與答案格式正確
        df['序號'] = df['序號'].fillna(0).astype(int)
        df['課程名稱'] = df['課程名稱'].astype(str).str.strip()
        df['題目內容'] = df['題目內容'].astype(str)
        df['正確答案'] = df['正確答案'].astype(str).str.strip().str.upper()
        return df
    except Exception:
        return None

def main():
    df = load_data()
    if df is None:
        st.error("❌ 檔案讀取失敗。請確認題庫檔案已正確上傳至根目錄。")
        return

    # --- 狀態初始化 ---
    if 'wrong_pool' not in st.session_state:
        st.session_state.wrong_pool = []  # 累積錯題池 (儲存字典格式)
    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = False
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # --- 側邊欄：控制台 ---
    st.sidebar.header("⚙️ 考官控制台")
    
    # 功能模式切換
    mode = st.sidebar.radio("請選擇測驗模式", ["一般抽測", f"錯題重考庫 ({len(st.session_state.wrong_pool)})"])

    if not st.session_state.quiz_active:
        if mode == "一般抽測":
            st.sidebar.subheader("範圍設定")
            all_units = sorted(df['課程名稱'].unique().tolist())
            selected_unit = st.sidebar.selectbox("1. 選擇單元", ["全部隨機"] + all_units)
            
            pool = df if selected_unit == "全部隨機" else df[df['課程名稱'] == selected_unit]
            min_id, max_id = int(pool['序號'].min()), int(pool['序號'].max())
            
            st.sidebar.info(f"可用序號範圍：{min_id} ~ {max_id}")
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

        else: # 錯題重考庫
            if len(st.session_state.wrong_pool) == 0:
                st.sidebar.warning("目前尚無累積錯題。")
            else:
                st.sidebar.write(f"目前累積了 {len(st.session_state.wrong_pool)} 道難題。")
                if st.sidebar.button("開始複習重考", use_container_width=True):
                    # 隨機打亂錯題順序
                    st.session_state.quiz_set = random.sample(st.session_state.wrong_pool, len(st.session_state.wrong_pool))
                    st.session_state.quiz_active = True
                    st.session_state.submitted = False
                    st.session_state.user_answers = {}
                    st.rerun()

    # --- 測驗主畫面 ---
    if st.session_state.quiz_active:
        st.title("🎓 數位考官：正在執行測驗")
        
        if not st.session_state.submitted:
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.quiz_set):
                    st.markdown(f"### 題號：{i+1}")
                    st.markdown(f"**（原序號：{q['序號']}）**")
                    st.write(q['題目內容']) # 嚴格原文呈現
                    st.session_state.user_answers[i] = st.radio("選項：", ["A", "B", "C", "D"], key=f"q_{i}", index=None)
                    st.write("---")
                
                if st.form_submit_button("交卷並核對答案", use_container_width=True):
                    st.session_state.submitted = True
                    st.rerun()
        else:
            # --- 統計與錯題邏輯處理 ---
            correct_count = 0
            current_wrongs = []
            
            for i, q in enumerate(st.session_state.quiz_set):
                u_ans = st.session_state.user_answers.get(i)
                if str(u_ans) == q['正確答案']:
                    correct_count += 1
                    # 若答對，從累積錯題池中移除
                    st.session_state.wrong_pool = [item for item in st.session_state.wrong_pool if item['序號'] != q['序號']]
                else:
                    current_wrongs.append({'q': q, 'u_ans': u_ans})
                    # 若答錯且尚未存在於池中，則加入
                    if q['序號'] not in [x['序號'] for x in st.session_state.wrong_pool]:
                        st.session_state.wrong_pool.append(q)

            st.success(f"測驗結束！答對率：{(correct_count/len(st.session_state.quiz_set))*100:.1f}% ({correct_count}/{len(st.session_state.quiz_set)})")

            if current_wrongs:
                st.subheader("❌ 錯誤解析（已自動同步至複習池）")
                for w in current_wrongs:
                    with st.expander(f"原序號：{w['q']['序號']} - 查看解析"):
                        st.write(f"**題目：** {w['q']['題目內容']}")
                        st.write(f"**您的答案：** {w['u_ans']} | **正確答案：** {w['q']['正確答案']}")
            else:
                st.balloons()
                st.success("全部答對！錯題池已清空。")

            if st.button("結束並回到設定"):
                st.session_state.quiz_active = False
                st.rerun()

if __name__ == "__main__":
    main()
