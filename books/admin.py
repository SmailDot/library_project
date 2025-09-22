# books/admin.py

from django.contrib import admin
from .models import Book, BorrowRecord

# 註冊 Book 模型
admin.site.register(Book)

# 註冊 BorrowRecord 模型
admin.site.register(BorrowRecord)