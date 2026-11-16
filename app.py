import json
import os
import re
import urllib.request
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_FILE = 'database.json'

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
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

# --- HTML + CSS + JS (ПОЛНЫЙ ИНТЕРФЕЙС) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>FinAI</title>
<style>
:root {
    --bg: #f3f6f4; --panel: #fff; --text: #20342c; --muted: #78877f;
    --green: #168365; --gbg: #e2f3eb; --red: #d65d5d; --rbg: #fff0f0; --border: #e3eae6;
}
body.dark {
    --bg: #111b18; --panel: #1c2a24; --text: #e8f1ec; --muted: #a0afa7;
    --green: #4bc395; --gbg: #254438; --red: #ff8585; --rbg: #482c2c; --border: #35443c;
}
* { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: Arial, sans-serif; display: flex; min-height: 100vh; }
.sidebar { width: 235px; background: var(--panel); border-right: 1px solid var(--border); padding: 24px 15px; flex-shrink: 0; display: flex; flex-direction: column; }
.logo { font-size: 28px; font-weight: 800; color: var(--green); padding: 5px 12px 30px; }
.logo span { color: var(--text); }
.nav button { width: 100%; text-align: left; padding: 14px 13px; margin: 4px 0; border: 0; border-radius: 12px; background: none; color: var(--muted); font-size: 16px; cursor: pointer; font-weight: normal; }
.nav button.active, .nav button:hover { background: var(--gbg); color: var(--green); }
main { flex: 1; padding: 27px 32px; max-width: 1450px; margin: 0 auto; min-width: 0; }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; flex-wrap: wrap; gap: 15px; }
h1 { font-size: 27px; margin: 0 0 6px; }
.subtitle { color: var(--muted); font-size: 14px; }
.actions { display: flex; gap: 10px; flex-wrap: wrap; }
.btn { border: 0; border-radius: 10px; padding: 11px 15px; background: var(--green); color: #fff; font-weight: 600; cursor: pointer; min-height: 44px; font-size: 15px; touch-action: manipulation; display: inline-block; text-align: center; }
.btn.secondary { background: var(--panel); border: 1px solid var(--border); color: var(--text); }
.btn.danger { background: var(--rbg); color: var(--red); }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 18px; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 19px; margin-bottom: 17px; }
.stat-label { font-size: 13px; color: var(--muted); margin-bottom: 12px; }
.stat-value { font-size: 25px; font-weight: 750; }
.green { color: var(--green); } .red-text { color: var(--red); }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.card-title { font-weight: 700; margin-bottom: 16px; }
.page { display: none; } .page.active { display: block; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th { text-align: left; color: var(--muted); font-weight: 500; border-bottom: 1px solid var(--border); padding: 11px 9px; }
td { padding: 13px 9px; border-bottom: 1px solid var(--border); }
.donut-wrap { display: flex; align-items: center; gap: 22px; flex-wrap: wrap; }
.donut { width: 165px; height: 165px; border-radius: 50%; position: relative; flex-shrink: 0; }
.donut:after { content: ""; position: absolute; inset: 30px; border-radius: 50%; background: var(--panel); }
.legend { display: grid; gap: 10px; font-size: 13px; color: var(--muted); }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 7px; }
.chat-box { background: var(--bg); padding: 12px; border-radius: 12px; min-height: 160px; max-height: 520px; overflow-y: auto; margin: 15px 0; }
.chat-message { padding: 13px 15px; border-radius: 12px; margin: 10px 0; white-space: pre-wrap; line-height: 1.65; }
.chat-user { background: var(--gbg); margin-left: 12%; }
.chat-bot { background: var(--panel); border: 1px solid var(--border); margin-right: 8%; }
.chat-row { display: flex; gap: 9px; }
.chat-row input { flex: 1; padding: 11px; border: 1px solid var(--border); border-radius: 9px; background: var(--panel); color: var(--text); }
.quick-questions { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
.quick-questions button { border: 1px solid var(--border); border-radius: 20px; padding: 8px 12px; color: var(--text); background: var(--panel); cursor: pointer; }
.modal-bg { display: none; position: fixed; inset: 0; background: #0008; align-items: center; justify-content: center; z-index: 1000; padding: 15px; }
.modal { background: var(--panel); padding: 24px; border-radius: 17px; width: 100%; max-width: 400px; max-height: 90vh; overflow: auto; position: relative; }
.field { margin-bottom: 13px; }
.field label { display: block; font-size: 13px; color: var(--muted); margin-bottom: 7px; }
.field input, .field select { width: 100%; padding: 11px; border: 1px solid var(--border); border-radius: 9px; background: var(--panel); color: var(--text); }
.account-card { padding: 15px; border: 1px solid var(--border); border-radius: 12px; margin: 12px 0; background: var(--panel); }
.section-head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 16px; }
.converter-grid { display: grid; grid-template-columns: 1fr auto 1fr; gap: 12px; align-items: end; }
.converter-result { background: var(--gbg); border-radius: 13px; padding: 20px; margin-top: 20px; }
.converter-result strong { font-size: 28px; color: var(--green); display: block; margin-top: 7px; }

@media(max-width: 768px) {
    body { display: block; }
    .sidebar { width: 100%; border-right: none; border-bottom: 1px solid var(--border); padding: 10px; }
    .logo { padding: 5px; margin-bottom: 10px; font-size: 24px; }
    .nav { display: flex; overflow-x: auto; gap: 5px; }
    .nav button { width: auto; white-space: nowrap; padding: 10px; }
    main { padding: 15px; }
    .cards { grid-template-columns: 1fr; }
    .grid { grid-template-columns: 1fr; }
    .chat-row { flex-direction: column; }
    .section-head { flex-direction: column; align-items: stretch; }
    .converter-grid { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<aside class="sidebar">
    <div class="logo">Fin<span>AI.</span></div>
    <nav class="nav">
        <button class="active" onclick="showPage('overview', this)">◈ <span data-i18n="navOverview">Обзор</span></button>
        <button onclick="showPage('income', this)">↗ <span data-i18n="navIncome">Доходы</span></button>
        <button onclick="showPage('expenses', this)">↘ <span data-i18n="navExpenses">Расходы</span></button>
        <button onclick="showPage('savings', this)">◎ <span data-i18n="navSavings">Накопления</span></button>
        <button onclick="showPage('converter', this)">⇄ <span data-i18n="navConverter">Валюты</span></button>
        <button onclick="showPage('assistant', this)">✧ <span data-i18n="navAssistant">ИИ-помощник</span></button>
    </nav>
</aside>

<main>
    <header>
        <div>
            <h1 id="pageTitle" data-i18n="overviewTitle">Финансовая сводка</h1>
            <div class="subtitle" data-i18n="subtitle">Все ваши финансы под контролем</div>
        </div>
        <div class="actions">
            <select id="langSelect" onchange="changeLang(this.value)" style="padding:10px; border-radius:10px; border:1px solid var(--border); background:var(--panel); color:var(--text);">
                <option value="ru">Русский</option>
                <option value="en">English</option>
            </select>
            <button class="btn secondary" onclick="toggleTheme()">☾ <span data-i18n="theme">Тема</span></button>
        </div>
    </header>

    <section class="page active" id="overview">
        <div class="cards">
            <div class="card"><div class="stat-label" data-i18n="monthIncome">Доходы</div><div class="stat-value green" id="sumIncome">0 ₽</div></div>
            <div class="card"><div class="stat-label" data-i18n="monthExpenses">Расходы</div><div class="stat-value red-text" id="sumExpenses">0 ₽</div></div>
            <div class="card"><div class="stat-label" data-i18n="monthBalance">Остаток</div><div class="stat-value" id="sumBalance">0 ₽</div></div>
        </div>
        <div class="grid">
            <div class="card">
                <div class="card-title" data-i18n="chartTitle">Структура расходов</div>
                <div class="donut-wrap"><div class="donut" id="donut"></div><div class="legend" id="legend"></div></div>
            </div>
            <div class="card">
                <div class="card-title" data-i18n="recentTitle">Последние операции</div>
                <table><tbody id="recentList"></tbody></table>
            </div>
        </div>
    </section>

    <section class="page" id="income">
        <div class="card">
            <div class="section-head">
                <div class="card-title" data-i18n="allIncome">Все доходы</div>
                <button class="btn" onclick="openTx('income')" data-i18n="addIncome">＋ Добавить доход</button>
            </div>
            <table>
                <thead><tr><th data-i18n="date">Дата</th><th data-i18n="description">Описание</th><th data-i18n="amount">Сумма</th><th></th></tr></thead>
                <tbody id="incomeList"></tbody>
            </table>
        </div>
    </section>

    <section class="page" id="expenses">
        <div class="card">
            <div class="section-head">
                <div class="card-title" data-i18n="allExpenses">Все расходы</div>
                <button class="btn" onclick="openTx('expense')" data-i18n="addExpense">＋ Добавить расход</button>
            </div>
            <table>
                <thead><tr><th data-i18n="date">Дата</th><th data-i18n="description">Описание</th><th data-i18n="amount">Сумма</th><th></th></tr></thead>
                <tbody id="expenseList"></tbody>
            </table>
        </div>
    </section>

    <section class="page" id="savings">
        <div class="card">
            <div class="section-head">
                <div class="card-title" data-i18n="savingsAccounts">Мои счета</div>
                <button class="btn" onclick="openAccountForm()" data-i18n="newAccount">＋ Создать счёт</button>
            </div>
            <div id="accountsList"></div>
        </div>
    </section>

    <section class="page" id="converter">
        <div class="card">
            <div class="card-title" data-i18n="converterTitle">⇄ Конвертер валют</div>
            <div class="converter-grid">
                <div class="field">
                    <label data-i18n="amount">Сумма</label>
                    <input id="currencyAmount" type="number" value="1000">
                </div>
                <div>
                    <button class="btn secondary" onclick="swapCurrencies()" style="padding:12px;">⇄</button>
                </div>
                <div class="field">
                    <label data-i18n="fromCurrency">Из валюты</label>
                    <select id="currencyFrom">
                        <option value="RUB">RUB — ₽</option>
                        <option value="USD">USD — $</option>
                        <option value="EUR">EUR — €</option>
                    </select>
                </div>
            </div>
            <div class="field" style="margin-top:15px;">
                <label data-i18n="toCurrency">В валюту</label>
                <select id="currencyTo">
                    <option value="EUR">EUR — €</option>
                    <option value="RUB">RUB — ₽</option>
                    <option value="USD">USD — $</option>
                </select>
            </div>
            <button class="btn" onclick="convertCurrency()" data-i18n="convertButton">Конвертировать</button>
            <div class="converter-result">
                <span data-i18n="convertedAmount">Результат</span>
                <strong id="conversionResult">—</strong>
                <div id="conversionStatus" style="font-size:13px; color:var(--muted); margin-top:10px;"></div>
            </div>
        </div>
    </section>

    <section class="page" id="assistant">
        <div class="card">
            <div class="card-title" data-i18n="assistantTitle">✧ Финансовый помощник</div>
            <div class="quick-questions">
                <button onclick="askQuick('budget')" data-i18n="quickBudget">Бюджет</button>
                <button onclick="askQuick('car')" data-i18n="quickCar">Покупка машины</button>
                <button onclick="askQuick('save')" data-i18n="quickSave">Экономия</button>
            </div>
            <div class="chat-box" id="chat">
                <div class="chat-message chat-bot" data-i18n="welcome">Здравствуйте! Я FinAI. Спросите меня о бюджете, накоплениях или покупках.</div>
            </div>
            <div class="chat-row">
                <input id="question" placeholder="Задайте вопрос..." data-i18n-placeholder="questionPlaceholder" onkeydown="if(event.key==='Enter') askAI()">
                <button class="btn" onclick="askAI()" data-i18n="ask">Спросить</button>
            </div>
        </div>
    </section>
</main>

<!-- Модалка добавления операции -->
<div class="modal-bg" id="txModal">
    <div class="modal">
        <h2 id="txTitle" style="margin-top:0;">Добавить</h2>
        <div class="field"><label data-i18n="description">Описание</label><input id="txDesc" placeholder="Продукты"></div>
        <div class="field"><label data-i18n="amount">Сумма</label><input id="txAmount" type="number" placeholder="1000"></div>
        <div class="field"><label data-i18n="date">Дата</label><input id="txDate" type="date"></div>
        <div style="display:flex; gap:10px; margin-top:20px;">
            <button class="btn secondary" style="flex:1;" onclick="closeModal('txModal')" data-i18n="cancel">Отмена</button>
            <button class="btn" style="flex:1;" onclick="saveTx()" data-i18n="save">Сохранить</button>
        </div>
    </div>
</div>

<!-- Модалка создания счёта -->
<div class="modal-bg" id="accModal">
    <div class="modal">
        <h2 style="margin-top:0;" data-i18n="newAccountTitle">Новый счёт</h2>
        <div class="field"><label data-i18n="accountName">Название счёта</label><input id="accName" placeholder="Например, Отпуск"></div>
        <div class="field"><label data-i18n="accountTarget">Цель (если есть)</label><input id="accTarget" type="number" placeholder="10000"></div>
        <div class="field"><label data-i18n="initialBalance">Начальный баланс</label><input id="accInitial" type="number" value="0"></div>
        <div style="display:flex; gap:10px; margin-top:20px;">
            <button class="btn secondary" style="flex:1;" onclick="closeModal('accModal')" data-i18n="cancel">Отмена</button>
            <button class="btn" style="flex:1;" onclick="saveAcc()" data-i18n="create">Создать</button>
        </div>
    </div>
</div>

<script>
// --- СЛОВАРИ ПЕРЕВОДА ---
const I18N = {
    ru: {
        navOverview: "Обзор", navIncome: "Доходы", navExpenses: "Расходы", navSavings: "Накопления", navConverter: "Валюты", navAssistant: "ИИ-помощник",
        overviewTitle: "Финансовая сводка", subtitle: "Все ваши финансы под контролем", theme: "Тема",
        monthIncome: "Доходы", monthExpenses: "Расходы", monthBalance: "Остаток", chartTitle: "Структура расходов", recentTitle: "Последние операции",
        allIncome: "Все доходы", allExpenses: "Все расходы", addIncome: "＋ Добавить доход", addExpense: "＋ Добавить расход",
        date: "Дата", description: "Описание", amount: "Сумма",
        savingsAccounts: "Мои счета", newAccount: "＋ Создать счёт",
        converterTitle: "⇄ Конвертер валют", fromCurrency: "Из валюты", toCurrency: "В валюту", convertButton: "Конвертировать", convertedAmount: "Результат",
        assistantTitle: "✧ Финансовый помощник", quickBudget: "Бюджет", quickCar: "Покупка машины", quickSave: "Экономия",
        welcome: "Здравствуйте! Я FinAI. Спросите меня о бюджете, накоплениях или покупках.", questionPlaceholder: "Задайте вопрос...", ask: "Спросить",
        cancel: "Отмена", save: "Сохранить", create: "Создать", newAccountTitle: "Новый счёт", accountName: "Название счёта", accountTarget: "Цель (если есть)", initialBalance: "Начальный баланс"
    },
    en: {
        navOverview: "Overview", navIncome: "Income", navExpenses: "Expenses", navSavings: "Savings", navConverter: "Currency", navAssistant: "AI Assistant",
        overviewTitle: "Financial Overview", subtitle: "All your finances under control", theme: "Theme",
        monthIncome: "Income", monthExpenses: "Expenses", monthBalance: "Balance", chartTitle: "Expense Structure", recentTitle: "Recent Transactions",
        allIncome: "All Income", allExpenses: "All Expenses", addIncome: "＋ Add Income", addExpense: "＋ Add Expense",
        date: "Date", description: "Description", amount: "Amount",
        savingsAccounts: "My Accounts", newAccount: "＋ Create Account",
        converterTitle: "⇄ Currency Converter", fromCurrency: "From", toCurrency: "To", convertButton: "Convert", convertedAmount: "Result",
        assistantTitle: "✧ Financial Assistant", quickBudget: "Budget", quickCar: "Buy a car", quickSave: "Save money",
        welcome: "Hello! I am FinAI. Ask me about budget, savings or purchases.", questionPlaceholder: "Ask a question...", ask: "Ask",
        cancel: "Cancel", save: "Save", create: "Create", newAccountTitle: "New Account", accountName: "Account Name", accountTarget: "Target (optional)", initialBalance: "Initial Balance"
    }
};

let currentLang = "ru";

function changeLang(lang) {
    currentLang = lang;
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (I18N[lang][key]) el.textContent = I18N[lang][key];
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        const key = el.getAttribute("data-i18n-placeholder");
        if (I18N[lang][key]) el.placeholder = I18N[lang][key];
    });
    
    // Обновляем заголовки модалок и кнопок
    const txTitle = document.getElementById('txTitle');
    if(txTitle) {
        if(currentTxType === 'income') txTitle.textContent = lang === 'ru' ? 'Добавить доход' : 'Add Income';
        else txTitle.textContent = lang === 'ru' ? 'Добавить расход' : 'Add Expense';
    }
    
    // Перерисовываем списки, чтобы обновить тексты (например, "Нет данных")
    render();
}

// --- ДАННЫЕ ---
let appData = { transactions: [], accounts: [] };
let currentTxType = 'income';

function loadData() {
    fetch('/api/data')
        .then(res => res.json())
        .then(data => {
            appData = data;
            render();
        });
}

function saveData() {
    fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(appData)
    }).then(() => loadData());
}

// --- НАВИГАЦИЯ ---
function showPage(pageId, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    // Меняем заголовок страницы
    const titles = {
        overview: "overviewTitle", income: "allIncome", expenses: "allExpenses", savings: "savingsAccounts", converter: "converterTitle", assistant: "assistantTitle"
    };
    const titleKey = titles[pageId];
    if (titleKey && I18N[currentLang][titleKey]) {
        document.getElementById('pageTitle').textContent = I18N[currentLang][titleKey];
    }
}

// --- ОТРИСОВКА ---
function render() {
    const inc = appData.transactions.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0);
    const exp = appData.transactions.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0);
    
    document.getElementById('sumIncome').textContent = inc.toLocaleString() + ' ₽';
    document.getElementById('sumExpenses').textContent = exp.toLocaleString() + ' ₽';
    document.getElementById('sumBalance').textContent = (inc - exp).toLocaleString() + ' ₽';

    const recentList = document.getElementById('recentList');
    const incomeList = document.getElementById('incomeList');
    const expenseList = document.getElementById('expenseList');
    
    recentList.innerHTML = ''; incomeList.innerHTML = ''; expenseList.innerHTML = '';

    appData.transactions.sort((a, b) => b.date.localeCompare(a.date)).forEach(t => {
        const row = `<tr>
            <td>${t.date}</td>
            <td>${t.description}</td>
            <td class="${t.type === 'income' ? 'green' : 'red-text'}">${t.amount.toLocaleString()} ₽</td>
            <td><button class="btn danger" style="padding:5px 10px; min-height:30px;" onclick="deleteTx(${t.id})">×</button></td>
        </tr>`;
        if (t.type === 'income') incomeList.innerHTML += row;
        else expenseList.innerHTML += row;

        if (recentList.children.length < 5) {
            recentList.innerHTML += `<tr><td>${t.date}</td><td>${t.description}</td><td class="${t.type === 'income' ? 'green' : 'red-text'}">${t.amount} ₽</td></tr>`;
        }
    });

    // График
    const expByCat = {};
    appData.transactions.filter(t => t.type === 'expense').forEach(t => expByCat['Расходы'] = (expByCat['Расходы'] || 0) + t.amount);
    let legend = ''; let grad = []; let start = 0;
    Object.entries(expByCat).forEach(([cat, val]) => {
        const p = (val / exp) * 100;
        legend += `<div><span class="dot" style="background:var(--green)"></span>${cat}: ${val} ₽ (${Math.round(p)}%)</div>`;
        grad.push(`var(--green) ${start}% ${start + p}%`);
        start += p;
    });
    const donut = document.getElementById('donut');
    const legendEl = document.getElementById('legend');
    if (grad.length) {
        donut.style.background = `conic-gradient(${grad.join(',')})`;
        legendEl.innerHTML = legend;
    } else {
        donut.style.background = 'var(--bg)';
        legendEl.innerHTML = currentLang === 'ru' ? 'Нет данных' : 'No data';
    }

    // Счета
    const accList = document.getElementById('accountsList');
    accList.innerHTML = appData.accounts.length ? '' : `<p>${currentLang === 'ru' ? 'Пока нет счетов' : 'No accounts yet'}</p>`;
    appData.accounts.forEach(a => {
        accList.innerHTML += `<div class="account-card">
            <div style="font-weight:bold; font-size:18px;">${a.name}</div>
            <div style="color:var(--muted); font-size:13px; margin:5px 0;">${currentLang === 'ru' ? 'Цель' : 'Target'}: ${a.target ? a.target.toLocaleString() + ' ₽' : '—'}</div>
            <div style="font-size:24px; font-weight:bold; color:var(--green);">${a.openingBalance.toLocaleString()} ₽</div>
            <button class="btn danger" style="margin-top:10px; padding:5px 10px;" onclick="deleteAcc(${a.id})">${currentLang === 'ru' ? 'Удалить' : 'Delete'}</button>
        </div>`;
    });
}

// --- МОДАЛКИ ---
function openTx(type) {
    currentTxType = type;
    document.getElementById('txTitle').textContent = type === 'income' 
        ? (currentLang === 'ru' ? 'Добавить доход' : 'Add Income')
        : (currentLang === 'ru' ? 'Добавить расход' : 'Add Expense');
    
    document.getElementById('txDesc').value = '';
    document.getElementById('txAmount').value = '';
    
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    document.getElementById('txDate').value = `${yyyy}-${mm}-${dd}`;
    
    document.getElementById('txModal').style.display = 'flex';
}

function saveTx() {
    const desc = document.getElementById('txDesc').value;
    const amount = Number(document.getElementById('txAmount').value);
    const date = document.getElementById('txDate').value;
    
    if (!desc || amount <= 0 || !date) return alert(currentLang === 'ru' ? 'Заполните все поля' : 'Fill all fields');
    
    appData.transactions.push({
        id: Date.now(),
        type: currentTxType,
        description: desc,
        amount: amount,
        date: date
    });
    
    closeModal('txModal');
    saveData();
}

function deleteTx(id) {
    if (!confirm(currentLang === 'ru' ? 'Удалить?' : 'Delete?')) return;
    appData.transactions = appData.transactions.filter(t => t.id !== id);
    saveData();
}

function openAccountForm() {
    document.getElementById('accName').value = '';
    document.getElementById('accTarget').value = '';
    document.getElementById('accInitial').value = '0';
    document.getElementById('accModal').style.display = 'flex';
}

function saveAcc() {
    const name = document.getElementById('accName').value;
    if (!name) return alert(currentLang === 'ru' ? 'Введите название' : 'Enter name');
    
    appData.accounts.push({
        id: Date.now(),
        name: name,
        target: Number(document.getElementById('accTarget').value) || 0,
        openingBalance: Number(document.getElementById('accInitial').value) || 0
    });
    
    closeModal('accModal');
    saveData();
}

function deleteAcc(id) {
    if (!confirm(currentLang === 'ru' ? 'Удалить счёт?' : 'Delete account?')) return;
    appData.accounts = appData.accounts.filter(a => a.id !== id);
    saveData();
}

function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}

function toggleTheme() {
    document.body.classList.toggle('dark');
}

// --- КОНВЕРТЕР ---
function swapCurrencies() {
    const from = document.getElementById('currencyFrom');
    const to = document.getElementById('currencyTo');
    const temp = from.value;
    from.value = to.value;
    to.value = temp;
    convertCurrency();
}

function convertCurrency() {
    const amount = Number(document.getElementById('currencyAmount').value);
    const from = document.getElementById('currencyFrom').value;
    const to = document.getElementById('currencyTo').value;
    const resultEl = document.getElementById('conversionResult');
    const statusEl = document.getElementById('conversionStatus');

    if (amount <= 0) {
        statusEl.textContent = currentLang === 'ru' ? 'Введите сумму' : 'Enter amount';
        return;
    }

    if (from === to) {
        resultEl.textContent = amount + ' ' + to;
        statusEl.textContent = currentLang === 'ru' ? 'Одинаковая валюта' : 'Same currency';
        return;
    }

    statusEl.textContent = currentLang === 'ru' ? 'Загрузка курса...' : 'Loading rate...';
    
    fetch(`https://api.frankfurter.dev/v2/rate/${from.toLowerCase()}/${to.toLowerCase()}`)
        .then(res => {
            if (!res.ok) throw new Error();
            return res.json();
        })
        .then(data => {
            const rate = Number(data.rate);
            resultEl.textContent = (amount * rate).toFixed(2) + ' ' + to;
            statusEl.textContent = `1 ${from} = ${rate} ${to} (${data.date})`;
        })
        .catch(() => {
            resultEl.textContent = '—';
            statusEl.textContent = currentLang === 'ru' ? 'Ошибка курса (нет интернета)' : 'Rate error (offline)';
        });
}

// --- ИИ-ПОМОЩНИК ---
function askQuick(type) {
    const map = {
        budget: currentLang === 'ru' ? 'Как составить бюджет?' : 'How to make a budget?',
        car: currentLang === 'ru' ? 'Как накопить на машину 1 миллион с зарплатой 50000?' : 'How to save for a 1 million car with 50000 salary?',
        save: currentLang === 'ru' ? 'Как сэкономить?' : 'How to save money?'
    };
    document.getElementById('question').value = map[type];
    askAI();
}

function askAI() {
    const input = document.getElementById('question');
    const q = input.value.trim();
    if (!q) return;
    
    addMsg((currentLang === 'ru' ? 'Вы: ' : 'You: ') + q, 'chat-user');
    input.value = '';
    
    setTimeout(() => {
        addMsg('FinAI: ' + makeAnswer(q), 'chat-bot');
    }, 300);
}

function addMsg(text, cls) {
    const chat = document.getElementById('chat');
    chat.innerHTML += `<div class="chat-message ${cls}">${text}</div>`;
    chat.scrollTop = chat.scrollHeight;
}

function makeAnswer(q) {
    q = q.toLowerCase();
    const salaryMatch = q.match(/зарплат[а-яё]*\s*(\d+)/);
    const targetMatch = q.match(/(\d+)\s*(млн|миллион)/);
    const isRu = currentLang === 'ru';

    // Машина / Крупная покупка
    if (q.includes('машин') || q.includes('авто') || q.includes('car')) {
        let salary = salaryMatch ? parseInt(salaryMatch[1]) : 50000;
        let target = targetMatch ? parseInt(targetMatch[1]) * 1000000 : 1000000;
        let monthly = Math.round(salary * 0.2);
        let months = Math.ceil(target / monthly);
        
        return isRu 
            ? `Давайте посчитаем.\nЦель: ${target.toLocaleString()} ₽.\nЗарплата: ${salary.toLocaleString()} ₽.\nОткладывая 20% (${monthly.toLocaleString()} ₽), вы накопите за ${months} месяцев.\n\nСовет: создайте отдельный счёт в разделе «Накопления».`
            : `Let's calculate.\nTarget: ${target}.\nSalary: ${salary}.\nSaving 20% (${monthly}), it will take ${months} months.\n\nTip: create a separate account in "Savings".`;
    }
    
    // Бюджет
    if (q.includes('бюджет') || q.includes('budget')) {
        return isRu
            ? `Правило 50/30/20:\n• 50% — обязательное (жильё, еда)\n• 30% — желания\n• 20% — сбережения.\n\nЕсли зарплата 50 000 ₽, то это: 25 000 на обязательное, 15 000 на желания и 10 000 на накопления.`
            : `50/30/20 Rule:\n• 50% — essentials (housing, food)\n• 30% — wants\n• 20% — savings.\n\nIf salary is 50,000, it's 25,000 for essentials, 15,000 for wants, and 10,000 for savings.`;
    }
    
    // Накопления
    if (q.includes('накоп') || q.includes('сбереж') || q.includes('save') || q.includes('saving')) {
        const numMatch = q.match(/(\d+)/);
        let target = numMatch ? parseInt(numMatch[1]) : 100000;
        return isRu
            ? `Для накопления ${target.toLocaleString()} ₽ создайте отдельный счёт и переводите туда фиксированную сумму (10-20% от дохода) сразу после зарплаты. Это лучший способ не тратить лишнего.`
            : `To save ${target}, create a separate account and transfer a fixed amount (10-20% of income) right after payday. This is the best way to avoid overspending.`;
    }

    // Кредиты
    if (q.includes('кредит') || q.includes('долг') || q.includes('loan') || q.includes('debt')) {
        return isRu
            ? `Перед взятием кредита: 1) Сравните полную стоимость (проценты + страховки). 2) Убедитесь, что платеж не превышает 30-40% от дохода. 3) Создайте резерв на 3-6 месяцев жизни до оформления кредита.`
            : `Before taking a loan: 1) Compare the total cost (interest + insurance). 2) Ensure the payment does not exceed 30-40% of income. 3) Build an emergency fund for 3-6 months before applying.`;
    }

    // Инвестиции
    if (q.includes('инвест') || q.includes('акци') || q.includes('invest')) {
        return isRu
            ? `Инвестиции — это риск. Сначала создайте финансовую подушку (3-6 месяцев расходов). Инвестируйте только те деньги, которые готовы заморозить на 3+ года.`
            : `Investing involves risk. First, build an emergency fund (3-6 months of expenses). Only invest money you are ready to lock away for 3+ years.`;
    }

    return isRu 
        ? `Я не совсем понял вопрос. Я могу помочь с бюджетом, накоплениями, кредитами и покупкой машины. Спросите, например: "Как накопить на машину 1 миллион?"`
        : `I didn't quite understand. I can help with budget, savings, loans, and car purchases. Try asking: "How to save for a 1 million car?"`;
}

// --- ЗАПУСК ---
loadData();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(load_db())

@app.route('/api/save', methods=['POST'])
def save_data():
    save_db(request.json)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)