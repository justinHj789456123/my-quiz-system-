import pandas as pd
import random
import os

class QuizMaster:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.quiz_set = []
        
    def load_data(self):
        """讀取 Excel 題庫檔案"""
        try:
            # 讀取指定的 Excel 檔案
            self.df = pd.read_excel(self.file_path)
            print(f"成功載入題庫，目前共有 {len(self.df)} 題。")
            return True
        except Exception as e:
            print(f"錯誤：無法讀取檔案。{e}")
            return False

    def setup_quiz(self):
        """設定測驗範圍與數量"""
        print("\n--- 測驗參數設定 ---")
        try:
            start_num = int(input(f"請輸入起始題號 (1-{len(self.df)}): "))
            end_num = int(input(f"請輸入結束題號 ({start_num}-{len(self.df)}): "))
            total_draw = int(input(f"請輸入欲抽考的總題數: "))
            
            # 根據範圍篩選題目[cite: 1]
            pool = self.df[(self.df['序號'] >= start_num) & (self.df['序號'] <= end_num)]
            
            if len(pool) < total_draw:
                print(f"警告：範圍內題目不足 {total_draw} 題，將改為全數抽測。")
                total_draw = len(pool)
            
            # 隨機抽題並保持原文呈現
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
