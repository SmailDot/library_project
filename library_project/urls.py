# library_project/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import BookViewSet, BorrowRecordViewSet
from django.views.generic import TemplateView

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'borrow-records', BorrowRecordViewSet, basename='borrow-record')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), 
    path('api/', include('chatbot.urls')), # 新增聊天機器人路由
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]