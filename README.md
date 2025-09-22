智慧圖書館管理系統
這是一個整合 AI 助理的現代化圖書館管理系統，旨在提供使用者直觀、高效的圖書借閱與管理體驗。本專案的核心亮點在於其 AI 助理功能，能透過自然語言處理使用者的借書請求，大幅簡化傳統的借書流程。

核心功能
圖書目錄瀏覽：即時查看所有可借閱的書籍清單。

AI 助理：使用者能透過聊天介面，用自然語言（例如：「幫我借哈利波特」）與系統互動，完成借閱或查詢等操作。

借閱紀錄追蹤：即時顯示使用者當前的借閱紀錄，並能直接歸還書籍。

管理後台：圖書管理員可以透過 Django 後台，方便地進行圖書資訊的增、刪、改、查。

技術棧
後端框架：Python, Django, Django REST Framework

AI/NLP：

LLM 框架：LangChain

大型語言模型：Gemma 3B (使用 Ollama)

向量資料庫：FAISS

嵌入模型：all-MiniLM-L6-v2

前端：HTML, CSS, JavaScript (原生)

資料庫：SQLite3 (輕量級、適合開發與測試)

使用教學
請遵循以下步驟來啟動並使用此專案。

步驟一：環境準備
安裝 Python：確保你的電腦已安裝 Python 3.8 或更高版本。

安裝 Git：前往 Git 官網 下載並安裝。

安裝 Ollama：前往 Ollama 官網 下載並安裝，然後在命令提示字元中運行以下指令以下載模型：

Bash

ollama run gemma3:4b
步驟二：專案啟動
複製專案：使用 git clone 指令將專案從 GitHub 複製到本地。

Bash

git clone https://github.com/SmailDot/library_project.git
cd library_project
建立虛擬環境：

Bash

python -m venv myenv
# Windows
myenv\Scripts\activate
安裝依賴套件：

Bash

pip install -r requirements.txt
（如果沒有 requirements.txt，請先執行 pip freeze > requirements.txt，然後再執行安裝指令）

執行資料庫遷移：

Bash

python manage.py makemigrations
python manage.py migrate
創建管理員帳號：

Bash

python manage.py createsuperuser
根據提示設定帳號、電子郵件和密碼。

啟動伺服器：

Bash

python manage.py runserver
步驟三：操作指南
管理後台：

打開瀏覽器，前往 http://127.0.0.1:8000/admin。

使用你創建的管理員帳號登入，即可在後台管理書籍資訊。

前端應用：

前往 http://127.0.0.1:8000。

在「客戶端聊天室」中輸入你的借書請求，例如：「幫我借哈利波特」或「我想借出 LAB_Works」。

系統會根據你的指令完成借閱，並在「圖書目錄」和「我的借閱記錄」中即時更新狀態。

注意事項

db.sqlite3 和 myenv/ 目錄已被  .gitignore 忽略，不會被上傳到 GitHub，這是為了確保專案輕量化。

如果專案啟動時出現錯誤，請檢查是否已成功安裝並運行 Ollama，並確保 gemma3:4b 模型已下載完成。
