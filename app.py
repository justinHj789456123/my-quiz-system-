import streamlit as st
import pandas as pd
import random

# 設定網頁標題與風格
st.set_page_config(page_title="工程品質專業測驗", layout="centered")

def load_data():
    """讀取 Excel 題庫檔案"""
    try:
        df = pd.read_excel("公共工程品質管理訓練班_機電班題庫.xlsx")
        return df
    except Exception as e:
        st.error(f"找不到題庫檔案，請確保檔案名稱正確：{e}")
        return None

def main():
    df = load_data()
    if df is None:
        return

    # 側邊欄：測驗參數設定
    st.sidebar.header("⚙️ 測驗參數設定")
    
    # 單元選擇
    units = ["【全部題目隨機抽】"] + df['課程名稱'].unique().tolist()
    selected_unit = st.sidebar.selectbox("1. 選擇單元範圍", units)
    
    # 題號範圍 (根據單元過濾)
    if selected_unit == "【全部題目隨機抽】":
        pool = df
    else:
        pool = df[df['課程名稱'] == selected_unit]
    
    min_idx = int(pool['序號'].min())
    max_idx = int(pool['序號'].max())
    
    start_num, end_num = st.sidebar.slider(
        "設定題號區間", 
        min_idx, max_idx, (min_idx, max_idx)
    )
    
    # 抽題數量
    max_draw = (end_num - start_num) + 1
    total_draw = st.sidebar.number_input("2. 抽考總題數", min_value=1, max_value=max_draw, value=min(10, max_draw))
    
    # 呈現偏好
    display_mode = st.sidebar.radio("測驗呈現偏好", ["一次僅顯示一題", "一次性呈現所有題目"])

    st.title("🎓 工程品質專業測驗")
    st.write("---")

    # 初始化測驗狀態
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False

    if not st.session_state.quiz_started:
        if st.button("開始測驗", use_container_width=True):
            # 隨機抽取題目
            final_pool = pool[(pool['序號'] >= start_num) & (pool['序號'] <= end_num)]
            st.session_state.questions = final_pool.sample(n=total_draw).to_dict('records')
            st.session_state.quiz_started = True
            st.session_state.user_answers = {}
            st.rerun()
    else:
        # 執行測驗流程
        questions = st.session_state.questions
        
        if display_mode == "一次性呈現所有題目":
            for i, q in enumerate(questions):
                st.subheader(f"題號：{i+1}")
                st.write(f"**題目：** {q['題目內容']}") # 原文呈現
                st.session_state.user_answers[i] = st.radio(
                    "選項：", ["A", "B", "C", "D"], key=f"q_{i}", index=None
                )
                st.write("---")
            
            if st.button("交卷並核對答案"):
                calculate_score(questions)
        
        if st.button("重新設定"):
            st.session_state.quiz_started = False
            st.rerun()

def calculate_score(questions):
    correct = 0
    for i, q in enumerate(questions):
        ans = st.session_state.user_answers.get(i)
        if str(ans) == str(q['正確答案']).strip().upper():
            correct += 1
    
    st.success(f"測驗結束！您的得分：{correct} / {len(questions)}")
    st.info(f"正確率：{(correct/len(questions))*100:.2f}%")

if __name__ == "__main__":
    main()            # 隨機抽題並保持原文呈現
            self.quiz_set = pool.sample(n=total_draw).to_dict('records')
            
            print(f"\n確認測驗範圍：第 {start_num} 題至第 {end_num} 題")
            print(f"確認抽題數量：{total_draw} 題")
            input("確認無誤請按 Enter 開始測驗...")
            return True
        except ValueError:
            print("錯誤：請輸入正確的數字格式。")
            return False

    def run_quiz(self):
        """執行測驗流程"""
        correct_count = 0
        results = []

        for i, q in enumerate(self.quiz_set, 1):
            print("\n" + "="*30)
            print(f"題號：{i}")
            print(f"題目：{q['題目內容']}")  # 原文呈現[cite: 1]
            print("選項：(A) (B) (C) (D)") # 根據題庫結構提供選項
            
            user_ans = input("您的回答 (A/B/C/D): ").strip().upper()
            
            # 核對正確答案[cite: 1]
            if user_ans == str(q['正確答案']).strip().upper():
                print("結果：正確")
                correct_count += 1
            else:
                print(f"結果：錯誤 (正確答案為 {q['正確答案']})")
            
            results.append({
                '題目': q['題目內容'],
                '您的答案': user_ans,
                '正確答案': q['正確答案']
            })

        self.show_final_report(correct_count, len(self.quiz_set))

    def show_final_report(self, correct, total):
        """統計測驗結果"""
        print("\n" + "="*30)
        print("測驗結束")
        print(f"總答對題數：{correct} / {total}")
        print(f"答對率：{(correct/total)*100:.2f}%")
        print("="*30)

# 執行程式
if __name__ == "__main__":
    file_name = "公共工程品質管理訓練班_機電班題庫.xlsx"
    if os.path.exists(file_name):
        master = QuizMaster(file_name)
        if master.load_data():
            if master.setup_quiz():
                master.run_quiz()
    else:
        print(f"找不到檔案：{file_name}，請確認檔案放置於同一目錄下。")            width: 100%;
            padding: 12px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
            background-color: white;
        }

        .btn-start {
            width: 100%;
            padding: 14px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
            margin-top: 10px;
        }

        .btn-start:hover {
            background-color: #1d4ed8;
        }

        #quiz-area { display: none; }
        .question-card { margin-bottom: 30px; border-bottom: 1px solid #f1f5f9; padding-bottom: 20px; }
        .options-label { display: block; padding: 8px 0; cursor: pointer; }
    </style>
</head>
<body>

<div class="container" id="setup-area">
    <div class="header">
        <h1>🎓 工程品質專業測驗</h1>
    </div>

    <div class="form-group">
        <label>1. 選擇單元範圍</label>
        <select id="unit-select">
            <option value="all">【全部題目隨機抽】</option>
            <option value="unit2_3">單元二：第三章品質分析方法與應用</option>
        </select>
    </div>

    <div class="form-group">
        <label>2. 選擇抽題數量</label>
        <select id="count-select">
            <option value="10">隨機抽 10 題</option>
            <option value="30">隨機抽 30 題</option>
            <option value="50">隨機抽 50 題</option>
            <option value="all">抽全部題目</option>
        </select>
    </div>

    <button class="btn-start" onclick="startQuiz()">開始測驗</button>
</div>

<div class="container" id="quiz-area">
    <div id="questions-container"></div>
    <button class="btn-start" onclick="submitQuiz()">交卷並核對答案</button>
</div>

<script>
    // 模擬題庫數據 (對應您提供之 xlsx 內容)
    const rawBank = [
        { id: 1, unit: "單元二:第三章品質分析方法與應用", content: "現代的品管作業基本觀念已進入(A)全面品質管制(B)品質查證(C)統計流程管制(D)全面品質管理的時代。", ans: "D" },
        { id: 2, unit: "單元二:第三章品質分析方法與應用", content: "新QC七大手法為充實何種階段的重要工具?(A)Do(B)Plan(C)Check(D)Action。", ans: "B" },
        { id: 3, unit: "單元二:第三章品質分析方法與應用", content: "傳統的七大手法比較偏向於何種階段?(A)Action(B)Do(C)Check(D)Plan。", ans: "C" },
        { id: 4, unit: "單元二:第三章品質分析方法與應用", content: "訂定品質改善目標可參考下列何者項目?(A)必要性(B)挑戰性(C)可行性(D)以上皆是。", ans: "D" },
        { id: 5, unit: "單元二:第三章品質分析方法與應用", content: "廣義的工程品質問題包含下列何者?(A)成本(B)安全(C)工期(D)以上皆是。", ans: "D" }
        // 更多題目可由此延伸...
    ];

    let currentQuizSet = [];

    function startQuiz() {
        const unit = document.getElementById('unit-select').value;
        const count = document.getElementById('count-select').value;
        
        // 過濾單元
        let filtered = unit === 'all' ? [...rawBank] : rawBank.filter(q => q.unit.includes("第三章"));
        
        // 隨機排序並抽題
        filtered.sort(() => Math.random() - 0.5);
        const limit = count === 'all' ? filtered.length : parseInt(count);
        currentQuizSet = filtered.slice(0, limit);

        renderQuiz();
    }

    function renderQuiz() {
        document.getElementById('setup-area').style.display = 'none';
        document.getElementById('quiz-area').style.display = 'block';
        
        const container = document.getElementById('questions-container');
        container.innerHTML = currentQuizSet.map((q, index) => `
            <div class="question-card">
                <p><strong>題號：${index + 1}</strong> (原題庫序號: ${q.id})</p>
                <p>題目：${q.content}</p>
                <div class="form-group">
                    <label class="options-label"><input type="radio" name="q${index}" value="A"> A</label>
                    <label class="options-label"><input type="radio" name="q${index}" value="B"> B</label>
                    <label class="options-label"><input type="radio" name="q${index}" value="C"> C</label>
                    <label class="options-label"><input type="radio" name="q${index}" value="D"> D</label>
                </div>
            </div>
        `).join('');
    }

    function submitQuiz() {
        let score = 0;
        currentQuizSet.forEach((q, index) => {
            const selected = document.querySelector(`input[name="q${index}"]:checked`);
            if (selected && selected.value === q.ans) {
                score++;
            }
        });
        alert(`測驗結束！\n您的得分：${score} / ${currentQuizSet.length}\n正確率：${((score/currentQuizSet.length)*100).toFixed(1)}%`);
        location.reload(); // 重新開始
    }
</script>

</body>
</html>
