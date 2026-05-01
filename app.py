import streamlit as st
import pandas as pd
import random

# 設定網頁
st.set_page_config(page_title="數位考官 - 專業測驗系統", layout="centered")

@st.cache_data(show_spinner="正在載入題庫...")
def load_data():
    try:
        df = pd.read_excel("公共工程品質管理訓練班_機電班題庫.xlsx")
        df['序號'] = df['序號'].fillna(0).astype(int)
        df['課程名稱'] = df['課程名稱'].astype(str).strip()
        df['正確答案'] = df['正確答案'].astype(str).str.strip().str.upper()
        return df
    except:
        return None

def main():
    df = load_data()
    if df is None:
        st.error("❌ 檔案讀取失敗，請確認檔案名稱與路徑。")
        return

    # --- 初始化全局狀態 (Behavioral Rule 3) ---
    if 'wrong_pool' not in st.session_state:
        st.session_state.wrong_pool = []  # 累積錯誤題目池
    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = False
    if 'mode' not in st.session_state:
        st.session_state.mode = "normal" # normal 或 review

    # --- 側邊欄：設定與功能選擇 ---
    st.sidebar.header("⚙️ 考官控制台")
    
    menu = st.sidebar.radio("選擇模式", ["一般測驗", f"錯誤複習重考 ({len(st.session_state.wrong_pool)})"])

    if menu == "一般測驗":
        st.session_state.mode = "normal"
        all_units = sorted(df['課程名稱'].unique().tolist())
        selected_unit = st.sidebar.selectbox("1. 選擇測驗單元", ["全部單元隨機"] + all_units)
        
        pool = df if selected_unit == "全部單元隨機" else df[df['課程名稱'] == selected_unit]
        min_id, max_id = int(pool['序號'].min()), int(pool['序號'].max())
        
        start_num = st.sidebar.number_input("起始題號", min_id, max_id, min_id)
        end_num = st.sidebar.number_input("結束題號", start_num, max_id, max_id)
        
        range_pool = pool[(pool['序號'] >= start_num) & (pool['序號'] <= end_num)]
        draw_count = st.sidebar.number_input("抽考題數", 1, len(range_pool), min(10, len(range_pool)))

        if st.sidebar.button("開始一般測驗", use_container_width=True):
            st.session_state.quiz_set = range_pool.sample(n=int(draw_count)).to_dict('records')
            st.session_state.user_answers = {}
            st.session_state.quiz_active = True
            st.session_state.submitted = False
            st.rerun()

    else: # 錯誤複習模式
        st.session_state.mode = "review"
        if len(st.session_state.wrong_pool) == 0:
            st.sidebar.warning("目前尚無累積錯題。")
        else:
            if st.sidebar.button("開始錯題重考", use_container_width=True):
                st.session_state.quiz_set = random.sample(st.session_state.wrong_pool, len(st.session_state.wrong_pool))
                st.session_state.user_answers = {}
                st.session_state.quiz_active = True
                st.session_state.submitted = False
                st.rerun()

    # --- 測驗執行介面 (Behavioral Rule 2) ---
    if st.session_state.quiz_active:
        st.title("🎓 數位考官：正在執行測驗")
        
        if not st.session_state.get('submitted'):
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.quiz_set):
                    st.markdown(f"**測驗第 {i+1} 題** (原序號: {q['序號']})")
                    st.write(q['題目內容'])
                    st.session_state.user_answers[i] = st.radio("選項", ["A", "B", "C", "D"], key=f"q_{i}", index=None)
                    st.write("---")
                
                if st.form_submit_button("交卷並核對答案"):
                    st.session_state.submitted = True
                    st.rerun()
        else:
            # --- 結果統計與錯題累積邏輯 ---
            correct = 0
            current_wrongs = []
            
            # 先計算本次結果
            for i, q in enumerate(st.session_state.quiz_set):
                u_ans = st.session_state.user_answers.get(i)
                if str(u_ans) == q['正確答案']:
                    correct += 1
                    # 如果是從錯題池考對的，從累積池移除
                    st.session_state.wrong_pool = [item for item in st.session_state.wrong_pool if item['序號'] != q['序號']]
                else:
                    current_wrongs.append({'q': q, 'u_ans': u_ans})
                    # 如果累積池裡還沒有這題，則加入
                    if q['序號'] not in [x['序號'] for x in st.session_state.wrong_pool]:
                        st.session_state.wrong_pool.append(q)

            st.metric("本次正確率", f"{(correct/len(st.session_state.quiz_set))*100:.1f}%")
            
            if current_wrongs:
                st.subheader("❌ 錯誤解析 (已自動加入錯題累積池)")
                for w in current_wrongs:
                    with st.expander(f"序號 {w['q']['序號']} 檢視"):
                        st.write(f"**題目：** {w['q']['題目內容']}")
                        st.write(f"**正確答案：** {w['q']['正確答案']} | **您的答案：** {w['u_ans']}")
            else:
                st.balloons()
                st.success("全部答對！")

            if st.button("結束並回到設定"):
                st.session_state.quiz_active = False
                st.rerun()        st.sidebar.header("⚙️ 測驗參數設定")
        
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
