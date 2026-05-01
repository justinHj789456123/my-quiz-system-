<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>工程品質專業測驗系統</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }

        .container {
            background-color: var(--card-bg);
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            width: 100%;
            max-width: 450px;
            padding: 32px;
            border: 1px solid #e2e8f0;
        }

        .header {
            text-align: center;
            margin-bottom: 24px;
        }

        .header h1 {
            color: #1e293b;
            font-size: 24px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #334155;
            font-size: 15px;
        }

        select, input {
            width: 100%;
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
