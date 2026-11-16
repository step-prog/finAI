import json
import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_FILE = 'database.json'

# --- РАБОТА С БАЗОЙ ДАННЫХ (JSON) ---
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"transactions": [], "accounts": []}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- HTML ИНТЕРФЕЙС (ТОЧНАЯ КОПИЯ ВАШЕЙ HTML-ВЕРСИИ) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>FinAI</title>
<style>
:root{
 --bg:#f3f6f4;--panel:#fff;--text:#20342c;--muted:#78877f;
 --green:#168365;--gbg:#e2f3eb;--red:#d65d5d;--rbg:#fff0f0;
 --border:#e3eae6;
}
body.dark{
 --bg:#111b18;--panel:#1c2a24;--text:#e8f1ec;--muted:#a0afa7;
 --green:#4bc395;--gbg:#254438;--red:#ff8585;--rbg:#482c2c;
 --border:#35443c;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{max-width:100%;overflow-x:hidden}
body{margin:0;background:var(--bg);color:var(--text);font-family:Arial,sans-serif;-webkit-text-size-adjust:100%}
button,input,select,textarea{font:inherit;touch-action:manipulation}
button{cursor:pointer;min-height:44px}
input,select,textarea{min-height:44px}
.app{display:flex;min-height:100vh;min-height:100dvh}
.sidebar{
 width:235px;background:var(--panel);border-right:1px solid var(--border);
 padding:24px 15px;flex-shrink:0;display:flex;flex-direction:column
}
.logo{font-size:28px;font-weight:800;color:var(--green);padding:5px 12px 30px}
.logo span{color:var(--text)}
.nav button{
 width:100%;display:block;text-align:left;padding:14px 13px;margin:4px 0;
 border:0;border-radius:12px;background:none;color:var(--muted);font-size:16px
}
.nav button.active,.nav button:hover{background:var(--gbg);color:var(--green)}
.side-note{margin-top:auto;padding:18px 10px;color:var(--muted);font-size:12px;line-height:1.5}
main{width:100%;max-width:1450px;margin:auto;padding:27px 32px;min-width:0}
.top{display:flex;justify-content:space-between;align-items:center;gap:15px;flex-wrap:wrap;margin-bottom:25px}
h1{font-size:27px;margin:0 0 6px}
.subtitle{color:var(--muted);font-size:14px}
.actions{display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.btn{border:0;border-radius:10px;padding:11px 15px;background:var(--green);color:#fff;font-weight:600;min-height:44px}
.btn.secondary{background:var(--panel);border:1px solid var(--border);color:var(--text)}
.btn.danger{background:var(--rbg);color:var(--red)}
.btn:disabled{opacity:.55;cursor:not-allowed}
input,select,textarea{
 background:var(--panel);color:var(--text);border:1px solid var(--border);
 border-radius:9px;padding:11px;max-width:100%
}
input:focus,select:focus,textarea:focus{outline:2px solid var(--green);outline-offset:1px}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-bottom:18px}
.card{background:var(--panel);border:1px solid var(--border);border-radius:16px;padding:19px;margin-bottom:17px}
.stat-label{font-size:13px;color:var(--muted);margin-bottom:12px}
.stat-value{font-size:25px;font-weight:750;overflow-wrap:anywhere}
.green{color:var(--green)}.red-text{color:var(--red)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.card-title{font-weight:700;margin-bottom:16px}
.page{display:none}.page.active{display:block}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;min-width:520px;font-size:14px}
th{text-align:left;color:var(--muted);font-weight:500;border-bottom:1px solid var(--border);padding:11px 9px}
td{padding:13px 9px;border-bottom:1px solid var(--border)}
tr:last-child td{border-bottom:0}
.empty{text-align:center;color:var(--muted);padding:25px}
.delete{border:0;background:none;color:var(--red);font-size:19px;min-height:36px;min-width:36px}
.month-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:17px}
.month-row label{color:var(--muted);font-size:14px}
.donut-wrap{display:flex;align-items:center;gap:22px;flex-wrap:wrap}
.donut{width:165px;height:165px;border-radius:50%;position:relative;flex-shrink:0}
.donut:after{content:"";position:absolute;inset:30px;border-radius:50%;background:var(--panel)}
.legend{display:grid;gap:10px;font-size:13px;color:var(--muted)}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px}
.note{font-size:14px;color:var(--muted);line-height:1.65}
.goal{margin:18px 0;padding-bottom:15px;border-bottom:1px solid var(--border)}
.goal-head{display:flex;justify-content:space-between;gap:10px;margin-bottom:9px;align-items:center}
.progress{height:10px;border-radius:20px;background:var(--bg);overflow:hidden;margin:9px 0}
.progress div{height:100%;background:var(--green);border-radius:20px}
.modal-bg{display:none;position:fixed;inset:0;background:#0008;z-index:10;align-items:center;justify-content:center;padding:15px;overflow-y:auto}
.modal-bg.show{display:flex}
.modal{width:min(470px,100%);background:var(--panel);padding:24px;border-radius:17px;max-height:90vh;overflow:auto}
.modal h2{margin:0 0 18px}
.field{margin:13px 0}
.field label{display:block;color:var(--muted);font-size:13px;margin-bottom:7px}
.field input,.field select{width:100%}
.modal-actions{display:flex;justify-content:flex-end;gap:9px;margin-top:20px;flex-wrap:wrap}
.chat-box{background:var(--bg);padding:12px;border-radius:12px;min-height:160px;max-height:520px;overflow-y:auto;line-height:1.65;margin:15px 0}
.chat-message{padding:13px 15px;border-radius:12px;margin:10px 0;white-space:pre-wrap;line-height:1.65;overflow-wrap:anywhere}
.chat-user{background:var(--gbg);margin-left:12%}
.chat-bot{background:var(--panel);border:1px solid var(--border);margin-right:8%}
.chat-row{display:flex;gap:9px}
.chat-row input{flex:1;min-width:0}
.chat-tools{display:flex;align-items:center;justify-content:space-between;gap:12px;width:100%;margin-top:12px}
.chat-tools .note{flex:1 1 auto;min-width:0}
.chat-tools button{margin-left:auto;flex:0 0 auto}
.quick-questions{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
.quick-questions button{
 border:1px solid var(--border);border-radius:20px;padding:8px 12px;
 color:var(--text);background:var(--panel);font-size:13px;min-height:38px
}
.quick-questions button:hover{border-color:var(--green);color:var(--green)}
.account-card{padding:15px;border:1px solid var(--border);border-radius:12px;margin:12px 0}
.account-balance{font-size:23px;font-weight:700;margin:8px 0;overflow-wrap:anywhere}
.account-meta{font-size:13px;color:var(--muted)}
.account-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.converter-grid{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:end}
.converter-grid .field{margin:0}
.converter-result{background:var(--gbg);border-radius:13px;padding:20px;margin-top:20px}
.converter-result strong{font-size:28px;color:var(--green);display:block;margin-top:7px;overflow-wrap:anywhere}
.converter-status{margin-top:12px;font-size:13px;color:var(--muted);line-height:1.5}
.swap-btn{background:var(--panel);color:var(--green);border:1px solid var(--border);border-radius:10px;padding:12px}
.section-head{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.type-switch{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px}
.type-switch button{flex:1 1 auto;min-height:40px;border-radius:10px;border:1px solid var(--border);background:var(--panel);color:var(--text);font-weight:600}
.type-switch button.active{background:var(--green);color:#fff;border-color:var(--green)}
.account-add-row{display:flex;gap:8px;align-items:stretch}
.account-add-row select{flex:1;min-width:0}
.account-add-row button{flex:0 0 auto;white-space:nowrap}

body.phone-mode .app{display:block}
body.phone-mode .sidebar{width:100%;padding:10px;border-right:0;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:5}
body.phone-mode .logo{padding:2px 8px 8px;font-size:24px}
body.phone-mode .nav{display:flex;overflow-x:auto;gap:4px;padding-bottom:2px;scrollbar-width:thin;-webkit-overflow-scrolling:touch}
body.phone-mode .nav button{white-space:nowrap;width:auto;padding:10px 12px;font-size:14px;margin:0}
body.phone-mode .side-note{display:none}
body.phone-mode main{padding:16px 10px}
body.phone-mode .cards{gap:8px;grid-template-columns:1fr 1fr}
body.phone-mode .card{padding:13px;border-radius:13px}
body.phone-mode .stat-value{font-size:19px}
body.phone-mode .grid{grid-template-columns:1fr}
body.phone-mode .chat-row{flex-direction:column}
body.phone-mode .chat-user{margin-left:4%}
body.phone-mode .chat-bot{margin-right:2%}
body.phone-mode .chat-tools{align-items:stretch;flex-direction:column}
body.phone-mode .chat-tools button{align-self:flex-end;margin-left:0}
body.phone-mode .converter-grid{grid-template-columns:1fr}
body.phone-mode .swap-btn{width:100%}
body.phone-mode .donut-wrap{justify-content:center}
body.phone-mode .modal{padding:18px;border-radius:14px}
body.phone-mode .modal-actions{flex-direction:column-reverse}
body.phone-mode .modal-actions .btn{width:100%}
body.phone-mode h1{font-size:22px}
body.phone-mode .actions{width:100%}
body.phone-mode .actions select,body.phone-mode .actions .btn{flex:1 1 auto}
body.phone-mode table{font-size:13px;min-width:480px}
body.phone-mode td,body.phone-mode th{padding:9px 6px}
body.phone-mode .section-head{flex-direction:column;align-items:stretch}
body.phone-mode .section-head .btn{width:100%}
body.phone-mode .account-add-row{flex-direction:column}
body.phone-mode .top{flex-direction:column;align-items:flex-start}
body.phone-mode .top .actions{justify-content:flex-start}

@media(max-width:768px){
 .app{display:block}
 .sidebar{width:100%;padding:10px;border-right:0;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:5}
 .logo{padding:2px 8px 8px;font-size:24px}
 .nav{display:flex;overflow-x:auto;gap:4px;padding-bottom:2px;scrollbar-width:thin;-webkit-overflow-scrolling:touch}
 .nav button{white-space:nowrap;width:auto;padding:10px 12px;font-size:14px;margin:0}
 .side-note{display:none}
 main{padding:16px 10px}
 .cards{gap:8px;grid-template-columns:1fr 1fr}
 .card{padding:13px;border-radius:13px}
 .stat-value{font-size:19px}
 .grid{grid-template-columns:1fr}
 .chat-row{flex-direction:column}
 .chat-user{margin-left:4%}
 .chat-bot{margin-right:2%}
 .chat-tools{align-items:stretch;flex-direction:column}
 .chat-tools button{align-self:flex-end;margin-left:0}
 .converter-grid{grid-template-columns:1fr}
 .swap-btn{width:100%}
 .donut-wrap{justify-content:center}
 .modal{padding:18px;border-radius:14px}
 .modal-actions{flex-direction:column-reverse}
 .modal-actions .btn{width:100%}
 h1{font-size:22px}
 .actions{width:100%}
 .actions select,.actions .btn{flex:1 1 auto}
 table{font-size:13px;min-width:480px}
 td,th{padding:9px 6px}
 .section-head{flex-direction:column;align-items:stretch}
 .section-head .btn{width:100%}
 .account-add-row{flex-direction:column}
 .top{flex-direction:column;align-items:flex-start}
 .top .actions{justify-content:flex-start}
}
@media(max-width:380px){
 .cards{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="app">
<aside class="sidebar">
 <div class="logo">Fin<span>AI.</span></div>
 <nav class="nav">
  <button class="active" data-page="overview">◈ Обзор</button>
  <button data-page="income">↗ Доходы</button>
  <button data-page="expenses">↘ Расходы</button>
  <button data-page="savings">◎ Накопления</button>
  <button data-page="converter">⇄ Валюты</button>
  <button data-page="assistant">✧ ИИ-помощник</button>
 </nav>
 <div class="side-note">Ваши данные сохраняются на сервере Python.</div>
</aside>

<main>
<header class="top">
 <div>
  <h1 id="pageTitle">Финансовая сводка</h1>
  <div class="subtitle">Все ваши финансы под контролем</div>
 </div>
 <div class="actions">
  <select id="language" aria-label="Language">
   <option value="ru">Русский</option>
   <option value="en">English</option>
  </select>
  <button class="btn secondary" id="themeButton">☾ Тёмная тема</button>
  <button class="btn secondary" id="phoneModeBtn">📱 Режим телефона</button>
 </div>
</header>

<section class="page active" id="overview">
 <div class="month-row">
  <label for="month">Сводка за месяц:</label>
  <input type="month" id="month">
 </div>
 <div class="cards">
  <div class="card"><div class="stat-label">Доходы за месяц</div><div class="stat-value green" id="sumIncome">0 ₽</div></div>
  <div class="card"><div class="stat-label">Расходы за месяц</div><div class="stat-value red-text" id="sumExpenses">0 ₽</div></div>
  <div class="card"><div class="stat-label">Остаток за месяц</div><div class="stat-value" id="sumBalance">0 ₽</div></div>
 </div>
 <div class="grid">
  <div class="card">
   <div class="card-title">Структура расходов</div>
   <div class="donut-wrap"><div class="donut" id="donut"></div><div class="legend" id="legend"></div></div>
  </div>
  <div class="card">
   <div class="card-title">Финансовый анализ</div>
   <div class="note" id="analysis"></div>
  </div>
 </div>
 <div class="card">
  <div class="card-title">Последние операции</div>
  <div class="table-wrap">
   <table>
    <thead><tr>
     <th>Дата</th><th>Описание</th><th>Тип</th><th>Сумма</th>
    </tr></thead>
    <tbody id="recent"></tbody>
   </table>
  </div>
 </div>
</section>

<section class="page" id="income">
 <div class="card">
  <div class="section-head">
   <div class="card-title">Все доходы</div>
   <button class="btn" id="addIncome">＋ Добавить доход</button>
  </div>
  <div class="table-wrap" style="margin-top:18px">
   <table>
    <thead><tr>
     <th>Дата</th><th>Описание</th><th>Категория</th><th>Сумма</th><th></th>
    </tr></thead>
    <tbody id="incomeList"></tbody>
   </table>
  </div>
 </div>
</section>

<section class="page" id="expenses">
 <div class="card">
  <div class="section-head">
   <div class="card-title">Все расходы</div>
   <button class="btn" id="addExpense">＋ Добавить расход</button>
  </div>
  <div class="table-wrap" style="margin-top:18px">
   <table>
    <thead><tr>
     <th>Дата</th><th>Описание</th><th>Категория</th><th>Сумма</th><th></th>
    </tr></thead>
    <tbody id="expenseList"></tbody>
   </table>
  </div>
 </div>
</section>

<section class="page" id="savings">
 <div class="card">
  <div class="section-head">
   <div>
    <div class="card-title">Мои счета</div>
    <div class="note">Создайте отдельный счёт для каждой цели.</div>
   </div>
   <button class="btn" id="addAccount">＋ Создать новый счёт</button>
  </div>
  <div id="accountsList"></div>
 </div>
</section>

<section class="page" id="converter">
 <div class="card">
  <div class="card-title">⇄ Конвертер валют</div>
  <div class="converter-grid">
   <div class="field">
    <label>Сумма</label>
    <input id="currencyAmount" type="number" min="0" step="0.01" value="1000">
   </div>
   <div>
    <button class="swap-btn" id="swapCurrencies">⇄</button>
   </div>
   <div class="field">
    <label>Из валюты</label>
    <select id="currencyFrom">
     <option value="RUB">RUB — ₽</option>
     <option value="USD">USD — $</option>
     <option value="EUR">EUR — €</option>
    </select>
   </div>
  </div>
  <div class="field">
   <label>В валюту</label>
   <select id="currencyTo">
    <option value="EUR">EUR — €</option>
    <option value="RUB">RUB — ₽</option>
    <option value="USD">USD — $</option>
   </select>
  </div>
  <button class="btn" id="convertButton">Конвертировать</button>
  <div class="converter-result">
   <span class="note">Результат</span>
   <strong id="conversionResult">—</strong>
   <div class="converter-status" id="conversionStatus">Введите сумму и нажмите «Конвертировать».</div>
  </div>
 </div>
</section>

<section class="page" id="assistant">
 <div class="card">
  <div class="card-title">✧ Финансовый помощник</div>
  <div class="note">Задайте вопрос — помощник разберёт вашу ситуацию.</div>
  <div class="quick-questions">
   <button type="button" data-question="budget">Составить бюджет</button>
   <button type="button" data-question="expenses">Анализ расходов</button>
   <button type="button" data-question="car">Покупка машины</button>
  </div>
  <div class="chat-box" id="chat">
   <div class="chat-message chat-bot">Здравствуйте! Я FinAI на Python. Задайте вопрос.</div>
  </div>
  <div class="chat-row">
   <input id="question" placeholder="Напишите вопрос...">
   <button class="btn" id="askButton">Спросить</button>
  </div>
 </div>
</section>
</main>
</div>

<!-- Модалки -->
<div class="modal-bg" id="txModal">
 <form class="modal" id="txForm">
  <h2 id="txTitle">Добавить операцию</h2>
  <div class="field"><label>Описание</label><input id="txDesc" required></div>
  <div class="field"><label>Категория</label><select id="txCategory"></select></div>
  <div class="field"><label>Сумма</label><input id="txAmount" type="number" min="0.01" step="0.01" required></div>
  <div class="field"><label>Дата</label><input id="txDate" type="date" required></div>
  <div class="modal-actions">
   <button type="button" class="btn secondary" id="cancelTx">Отмена</button>
   <button type="submit" class="btn">Сохранить</button>
  </div>
 </form>
</div>

<div class="modal-bg" id="accountModal">
 <form class="modal" id="accountForm">
  <h2>Новый счёт</h2>
  <div class="field">
   <label>Тип счёта</label>
   <div class="type-switch">
    <button type="button" class="active" data-account-type="regular">Обычный</button>
    <button type="button" data-account-type="savings">Накопительный</button>
   </div>
  </div>
  <div class="field"><label>Название счёта</label><input id="accountName" placeholder="Например, Основной счёт" required></div>
  <div class="field" id="accountTargetField"><label>Цель накопления</label><input id="accountTarget" type="number" min="0" step="0.01" placeholder="10000"></div>
  <div class="field"><label>Уже есть на счёте</label><input id="accountInitial" type="number" min="0" step="0.01" value="0"></div>
  <div class="modal-actions">
   <button type="button" class="btn secondary" id="cancelAccount">Отмена</button>
   <button type="submit" class="btn">Создать</button>
  </div>
 </form>
</div>

<script>
// Глобальные переменные
let data = { transactions: [], accounts: [] };
let currentPage = "overview";
let formType = "income";
let accountFormType = "regular";

// Загрузка данных с сервера
async function loadData() {
    const res = await fetch('/api/data');
    data = await res.json();
    render();
}

// Сохранение данных на сервер
async function saveData() {
    await fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
}

// Навигация
document.querySelectorAll(".nav button").forEach(b => {
    b.onclick = () => {
        currentPage = b.dataset.page;
        document.querySelectorAll(".page").forEach(el => el.classList.remove("active"));
        document.getElementById(currentPage).classList.add("active");
        document.querySelectorAll(".nav button").forEach(btn => btn.classList.toggle("active", btn === b));
        document.getElementById("pageTitle").textContent = {
            overview: "Финансовая сводка", income: "Доходы", expenses: "Расходы",
            savings: "Накопления", converter: "Конвертер", assistant: "ИИ-помощник"
        }[currentPage];
    };
});

// Рендер всего интерфейса
function render() {
    // Статистика
    const inc = data.transactions.filter(t => t.type === "income").reduce((s, t) => s + t.amount, 0);
    const exp = data.transactions.filter(t => t.type === "expense").reduce((s, t) => s + t.amount, 0);
    document.getElementById("sumIncome").textContent = inc + " ₽";
    document.getElementById("sumExpenses").textContent = exp + " ₽";
    document.getElementById("sumBalance").textContent = (inc - exp) + " ₽";

    // Списки операций
    const recent = document.getElementById("recent");
    const incomeList = document.getElementById("incomeList");
    const expenseList = document.getElementById("expenseList");
    
    recent.innerHTML = ""; incomeList.innerHTML = ""; expenseList.innerHTML = "";

    data.transactions.sort((a, b) => b.date.localeCompare(a.date)).forEach(t => {
        const row = `<tr>
            <td>${t.date}</td><td>${t.description}</td>
            <td class="${t.type === 'income' ? 'green' : 'red-text'}">${t.type === 'income' ? '+' : '-'}${t.amount} ₽</td>
            <td><button class="delete" onclick="deleteTx(${t.id})">×</button></td>
        </tr>`;
        if (t.type === "income") incomeList.innerHTML += row;
        else expenseList.innerHTML += row;
        
        if (recent.children.length < 5) {
            recent.innerHTML += `<tr><td>${t.date}</td><td>${t.description}</td><td>${t.type === 'income' ? 'Доход' : 'Расход'}</td><td>${t.amount} ₽</td></tr>`;
        }
    });

    // График (упрощенно)
    const expByCat = {};
    data.transactions.filter(t => t.type === "expense").forEach(t => expByCat[t.category] = (expByCat[t.category] || 0) + t.amount);
    let legend = "";
    let gradient = [];
    let start = 0;
    Object.entries(expByCat).forEach(([cat, val], i) => {
        const percent = (val / exp) * 100;
        legend += `<div><span class="dot" style="background:#168365"></span>${cat}: ${val} ₽</div>`;
        gradient.push(`#168365 ${start}% ${start + percent}%`);
        start += percent;
    });
    if (gradient.length) {
        document.getElementById("donut").style.background = `conic-gradient(${gradient.join(",")})`;
        document.getElementById("legend").innerHTML = legend;
    }
}

// Удаление
function deleteTx(id) {
    if (!confirm("Удалить?")) return;
    data.transactions = data.transactions.filter(t => t.id !== id);
    saveData().then(loadData);
}

// Добавление операции
document.getElementById("addIncome").onclick = () => openTx("income");
document.getElementById("addExpense").onclick = () => openTx("expense");

function openTx(type) {
    formType = type;
    document.getElementById("txTitle").textContent = type === "income" ? "Добавить доход" : "Добавить расход";
    document.getElementById("txDesc").value = "";
    document.getElementById("txAmount").value = "";
    document.getElementById("txDate").value = new Date().toISOString().slice(0, 10);
    
    const cats = type === "income" ? ["Зарплата", "Подработка", "Подарки"] : ["Продукты", "Транспорт", "Жильё"];
    document.getElementById("txCategory").innerHTML = cats.map(c => `<option value="${c}">${c}</option>`).join("");
    
    document.getElementById("txModal").classList.add("show");
}

document.getElementById("cancelTx").onclick = () => document.getElementById("txModal").classList.remove("show");

document.getElementById("txForm").onsubmit = e => {
    e.preventDefault();
    const tx = {
        id: Date.now(),
        type: formType,
        description: document.getElementById("txDesc").value,
        category: document.getElementById("txCategory").value,
        amount: Number(document.getElementById("txAmount").value),
        date: document.getElementById("txDate").value
    };
    data.transactions.push(tx);
    saveData().then(() => {
        document.getElementById("txModal").classList.remove("show");
        loadData();
    });
};

// Помощник
document.getElementById("askButton").onclick = () => {
    const input = document.getElementById("question");
    const q = input.value.trim();
    if (!q) return;
    addChat("Вы: " + q, "chat-user");
    input.value = "";
    addChat("FinAI: " + makeAnswer(q), "chat-bot");
};

function addChat(text, cls) {
    const chat = document.getElementById("chat");
    chat.innerHTML += `<div class="chat-message ${cls}">${text}</div>`;
    chat.scrollTop = chat.scrollHeight;
}

function makeAnswer(q) {
    q = q.toLowerCase();
    const salaryMatch = q.match(/зарплат[а-яё]*\s*(\d+)/);
    const targetMatch = q.match(/(\d+)\s*(млн|миллион)/);
    
    if (q.includes('машин') || q.includes('авто')) {
        let salary = salaryMatch ? parseInt(salaryMatch[1]) : 50000;
        let target = targetMatch ? parseInt(targetMatch[1]) * 1000000 : 1000000;
        let months = Math.ceil(target / (salary * 0.2));
        return `Давайте посчитаем. Цель: ${target.toLocaleString()} ₽. Зарплата: ${salary.toLocaleString()} ₽. Откладывая 20% (${(salary*0.2).toLocaleString()} ₽), вам потребуется ~${months} месяцев.`;
    }
    if (q.includes('накоп') || q.includes('сбереж')) return "Создайте отдельный счёт и переводите туда 10-20% от зарплаты сразу после получения.";
    if (q.includes('бюджет')) return "Правило 50/30/20: 50% на обязательное, 30% на желания, 20% на сбережения.";
    return "Я понимаю простые вопросы про бюджет, накопления и покупку машины.";
}

// Тема
document.getElementById("themeButton").onclick = () => {
    document.body.classList.toggle("dark");
};
document.getElementById("phoneModeBtn").onclick = () => {
    document.body.classList.toggle("phone-mode");
};

// Инициализация
document.getElementById("month").value = new Date().toISOString().slice(0, 7);
loadData();
</script>
</body>
</html>
"""

# --- МАРШРУТЫ FLASK ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(load_db())

@app.route('/api/save', methods=['POST'])
def save_data():
    db = request.json
    save_db(db)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("\n" + "="*50)
    print(" СЕРВЕР ЗАПУЩЕН!")
    print(" Откройте в браузере: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', debug=True, port=5000)