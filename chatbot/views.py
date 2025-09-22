# chatbot/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import re
from datetime import date, timedelta
from django.utils import timezone
from django.db import transaction

# 導入 LangChain 相關套件
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# 導入你的 Django 模型
from books.models import Book, BorrowRecord

# 載入知識庫並建立 RAG 模型
qa_chain = None

def get_qa_chain():
    """初始化並回傳 RAG 問答鏈"""
    global qa_chain
    if qa_chain is not None:
        return qa_chain
    
    loader = TextLoader("faq.txt", encoding="utf-8")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(
        separator='\n\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    docsearch = FAISS.from_documents(texts, embeddings)
    llm = Ollama(model="gemma3:4b")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
    )
    return qa_chain

# 假設你已經有一個 user_id 來標識當前使用者
CURRENT_USER_ID = 1

def find_book_id_by_title(book_title):
    """根據書籍名稱查詢 ID"""
    try:
        # 使用不區分大小寫且包含的查詢，增加容錯性
        books = Book.objects.filter(title__icontains=book_title)
        if books.exists():
            return books.first().id
        return None
    except Exception:
        return None

def borrow_book_logic(user_question):
    """
    處理借書請求的邏輯。
    可以從問題中解析出書籍 ID 或書名。
    """
    try:
        # 1. 嘗試從問題中解析書籍 ID
        match = re.search(r'ID\s?(\d+)', user_question, re.IGNORECASE)
        if match:
            book_id = int(match.group(1))
        else:
            # 2. 如果沒有 ID，嘗試從問題中解析書名
            prompt = ChatPromptTemplate.from_messages([
                ("system", """請從使用者的問題中提取書籍的名稱。
                如果問題包含「借」、「借閱」、「借出」等動詞，或直接提及書籍名稱，請將其判斷為借書意圖，並返回書名。
                如果找不到書名，請回答'無'。
                例如：
                使用者: '我想借哈利波特'
                書名: '哈利波特'
                使用者: '幫我借出書名是《LAB_Works》的書'
                書名: 'LAB_Works'
                使用者: '借一下童話故事集'
                書名: '童話故事集'
                請僅回覆書名，不要有額外的字詞。
                """),
                ("human", "使用者: {question}")
            ])
            llm = Ollama(model="gemma3:4b")
            chain = prompt | llm
            book_title_response = chain.invoke({"question": user_question})
            book_title = book_title_response.strip().replace("《", "").replace("》", "")
            
            if book_title and book_title != '無':
                book = Book.objects.filter(title__icontains=book_title).first()
                if not book:
                    return {"message": f"找不到書名為 '{book_title}' 的書籍。"}
                book_id = book.id
            else:
                return {"message": "請提供要借閱的書籍 ID 或書名。"}

        # 3. 執行借書邏輯
        with transaction.atomic():
            book = Book.objects.get(pk=book_id)
            if book.is_available:
                due_date = date.today() + timedelta(days=14) 
                
                record = BorrowRecord.objects.create(
                    book=book,
                    user_id=CURRENT_USER_ID,
                    due_date=due_date,
                    borrow_date=timezone.now(),
                )
                book.is_available = False
                book.save()
                return {"message": f"成功借閱書籍：'{book.title}'，到期日為 {due_date.strftime('%Y-%m-%d')}。", "record_id": record.id}
            else:
                return {"message": f"抱歉，書籍：'{book.title}' 已經被借出。"}

    except Book.DoesNotExist:
        return {"message": f"找不到 ID 為 {book_id} 的書籍。"}
    except Exception as e:
        return {"message": f"借書時發生錯誤：{str(e)}"}

def general_qa_logic(user_question):
    """
    處理通用問答邏輯，使用 RAG 問答鏈。
    """
    try:
        qa_chain_instance = get_qa_chain()
        result = qa_chain_instance.invoke({"query": user_question})
        return result['result']
    except Exception as e:
        return {"message": f"回答問題時發生錯誤：{str(e)}"}


class ChatbotAPIView(APIView):
    """
    處理聊天機器人訊息的 API 視圖，使用 LLM 路由器模式。
    """
    def post(self, request, *args, **kwargs):
        user_question = request.data.get('question')
        if not user_question:
            return Response({'error': '請提供一個問題。'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 優先處理歸還請求
            if "歸還" in user_question or "還書" in user_question:
                return Response({'message': "圖書館助理無法直接為您處理歸還書籍的請求。這需要由圖書管理員確認您已將書籍歸還，請您將書籍攜至櫃檯，謝謝。"})

            # 使用 LLM 判斷意圖
            prompt = ChatPromptTemplate.from_messages([
                ("system", """請判斷以下使用者問題的意圖。
                如果使用者想**執行**借閱某本書的動作，問題中通常會包含「借」、「借閱」、「借出」等動詞，或直接提及書名（例如「借哈利波特」、「我要借10萬個為什麼」）。請回答 'BORROW'。
                如果使用者是**詢問**圖書館的通用問題（例如：'如何借書?'、'借閱期限是多久?'），請回答 'QA'。
                如果問題不屬於以上兩者，回答 'OTHER'。
                請僅回覆一個單詞，例如 'BORROW' 或 'QA'。
                """),
                ("human", "問題: {question}")
            ])
            llm = Ollama(model="gemma3:4b")
            chain = prompt | llm
            
            intent = chain.invoke({"question": user_question}).strip()

            if 'BORROW' in intent:
                answer = borrow_book_logic(user_question)
                return Response({'message': answer['message']})
            elif 'QA' in intent:
                answer = general_qa_logic(user_question)
                return Response({'message': answer})
            else:
                # Fallback機制：如果LLM無法判斷意圖，嘗試直接進行書籍借閱，以處理簡單的書籍名稱輸入。
                borrow_response = borrow_book_logic(user_question)
                if '成功' in borrow_response.get('message', ''):
                    return Response({'message': borrow_response['message']})
                else:
                    return Response({'message': "我無法理解你的問題，請明確說明你的意圖。"})

        except Exception as e:
            print("Chatbot API Error:", e)
            return Response({'message': f'發生錯誤：{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)