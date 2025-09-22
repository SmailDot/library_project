// frontend/script.js

// 基礎設定
const API_BASE_URL = 'http://127.0.0.1:8000/api';

/**
 * 取得 CSRF token (跨站請求偽造)
 * Django REST Framework 預設需要此 token 才能進行 POST, PUT 等請求
 */
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * 渲染使用者資訊
 */
async function renderUserInfo() {
    const usernameEl = document.getElementById('username');
    const overdueStatusEl = document.getElementById('overdue-status');

    try {
        const response = await fetch(`${API_BASE_URL}/borrow-records/`);
        const records = await response.json();

        // 檢查是否有任何借閱記錄
        if (records.length > 0) {
            usernameEl.textContent = records[0].user_name;
        } else {
            usernameEl.textContent = `使用者`; // 假設沒有借閱記錄時
        }

        const hasOverdue = records.some(record => {
            const dueDate = new Date(record.due_date);
            return dueDate < new Date() && !record.return_date;
        });
        
        overdueStatusEl.textContent = hasOverdue ? '是' : '否';
        if (hasOverdue) {
            overdueStatusEl.classList.add('overdue');
        } else {
            overdueStatusEl.classList.remove('overdue');
        }

    } catch (error) {
        console.error('載入使用者資訊失敗：', error);
        usernameEl.textContent = '載入失敗';
        overdueStatusEl.textContent = '載入失敗';
    }
}

/**
 * 渲染圖書列表
 */
async function renderBooks() {
    const bookListEl = document.getElementById('book-list');
    bookListEl.innerHTML = '載入中...';

    try {
        const response = await fetch(`${API_BASE_URL}/books/`);
        const books = await response.json();

        bookListEl.innerHTML = '';
        books.forEach(book => {
            const li = document.createElement('li');
            li.className = 'book-item';
            li.innerHTML = `
                <span>${book.title} - ${book.author} (${book.is_available ? '可借閱' : '已借出'})</span>
                ${book.is_available ? `<button onclick="borrowBook(${book.id})">借閱</button>` : ''}
            `;
            bookListEl.appendChild(li);
        });
    } catch (error) {
        console.error('載入圖書列表失敗：', error);
        bookListEl.innerHTML = '載入圖書清單時發生錯誤。';
    }
}

/**
 * 渲染借閱記錄
 */
async function renderBorrowRecords() {
    const borrowListEl = document.getElementById('borrow-records-list');
    borrowListEl.innerHTML = '載入中...';

    try {
        const response = await fetch(`${API_BASE_URL}/borrow-records/`);
        const records = await response.json();

        borrowListEl.innerHTML = '';
        if (records.length === 0) {
            borrowListEl.innerHTML = '<li>您目前沒有任何借閱記錄。</li>';
            return;
        }

        records.forEach(record => {
            const isOverdue = new Date(record.due_date) < new Date() && !record.return_date;
            
            const li = document.createElement('li');
            li.innerHTML = `
                <span>
                    <strong>${record.book_title}</strong>
                    <br>借閱日期：${record.borrow_date}
                    <br>到期日：<span class="${isOverdue ? 'overdue' : ''}">${record.due_date}</span>
                    <br>歸還日期：${record.return_date || '未歸還'}
                </span>
                ${!record.return_date ? `<button onclick="returnBook(${record.id})">歸還</button>` : ''}
            `;
            borrowListEl.appendChild(li);
        });
    } catch (error) {
        console.error('載入借閱記錄失敗：', error);
        borrowListEl.innerHTML = '載入借閱記錄時發生錯誤。';
    }
}

/**
 * 借閱書籍
 */
async function borrowBook(bookId) {
    const csrfToken = getCsrfToken();
    try {
        const response = await fetch(`${API_BASE_URL}/borrow-records/borrow_book/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ book_id: bookId })
        });
        
        if (response.ok) {
            alert('借閱成功！');
            // 重新載入列表
            renderBooks();
            renderBorrowRecords();
            renderUserInfo();
        } else {
            const errorData = await response.json();
            alert(`借閱失敗：${errorData.error}`);
        }
    } catch (error) {
        console.error('借閱書籍失敗：', error);
        alert('借閱書籍時發生錯誤。');
    }
}

/**
 * 歸還書籍
 */
async function returnBook(recordId) {
    const csrfToken = getCsrfToken();
    try {
        const response = await fetch(`${API_BASE_URL}/borrow-records/${recordId}/return_book/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
        
        if (response.ok) {
            alert('歸還成功！');
            // 重新載入列表
            renderBooks();
            renderBorrowRecords();
            renderUserInfo();
        } else {
            const errorData = await response.json();
            alert(`歸還失敗：${errorData.error}`);
        }
    } catch (error) {
        console.error('歸還書籍失敗：', error);
        alert('歸還書籍時發生錯誤。');
    }
}

// 聊天機器人相關功能
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatWindow = document.getElementById('chat-window');

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const question = userInput.value;
    if (question.trim() === '') return;

    appendMessage('user', question);
    userInput.value = '';
    
    sendQuestionToChatbot(question);
});

function appendMessage(sender, text) {
    const messageEl = document.createElement('div');
    messageEl.classList.add('message', `${sender}-message`);

    // 使用 innerHTML 屬性，並將 \n 替換為 <br> 標籤
    messageEl.innerHTML = text.replace(/\n/g, '<br>');

    chatWindow.appendChild(messageEl);
    chatWindow.scrollTop = chatWindow.scrollHeight; // 自動捲動到底部
}

async function sendQuestionToChatbot(question) {
    appendMessage('bot', '正在思考中...'); // 顯示等待訊息

    const csrfToken = getCsrfToken();
    try {
        const response = await fetch(`${API_BASE_URL}/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();
        if (response.ok) {
            // 移除等待訊息
            chatWindow.lastChild.remove();
            appendMessage('bot', data.answer);
        } else {
            // 移除等待訊息並顯示錯誤
            chatWindow.lastChild.remove();
            appendMessage('bot', `抱歉，發生錯誤：${data.error}`);
        }
    } catch (error) {
        console.error('與聊天機器人通訊失敗：', error);
        // 移除等待訊息並顯示錯誤
        chatWindow.lastChild.remove();
        appendMessage('bot', '與伺服器連線失敗。');
    }
}

// 頁面載入時執行
window.onload = () => {
    renderBooks();
    renderBorrowRecords();
    renderUserInfo();
    
    // 在頁面載入完成後，顯示歡迎訊息
    const welcomeMessage = `親愛的使用者您好，我是圖書館的AI助理，歡迎您使用！

您可以詢問以下問題：
1. 如何借閱書籍？
2. 我最多可以借閱多少本書？
3. 借閱期限是多久？
4. 如何歸還圖書？
5. 如果圖書逾期了怎麼辦？
6. 我可以推薦新書嗎？`;

    appendMessage('bot', welcomeMessage);
};