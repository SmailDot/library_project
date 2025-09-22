from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Book, BorrowRecord
from .serializers import BookSerializer, BorrowRecordSerializer
from django.db import transaction

# 定義 Books API 視圖集
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# 定義 Borrow Records API 視圖集
class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all().select_related('book')
    serializer_class = BorrowRecordSerializer

    # 自定義借閱操作
    @action(detail=False, methods=['post'])
    def borrow_book(self, request):
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({'message': '請提供書籍 ID。'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                book = get_object_or_404(Book, pk=book_id)
                if not book.is_available:
                    return Response({'message': '此書已被借出。'}, status=status.HTTP_409_CONFLICT)
                
                # 假設使用者 ID 為 1
                record = BorrowRecord.objects.create(
                    book=book,
                    user_id=1,
                    borrow_date=timezone.now(),
                    due_date=timezone.now() + timezone.timedelta(days=14)
                )
                book.is_available = False
                book.save()
            return Response({'message': 'success', 'record_id': record.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 自定義歸還操作
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        try:
            with transaction.atomic():
                # 關鍵修正: 將 returned_date 改為 return_date
                record = get_object_or_404(BorrowRecord, pk=pk, return_date__isnull=True)
                record.return_date = timezone.now()
                record.save()
                
                book = record.book
                book.is_available = True
                book.save()
            return Response({'message': 'success'}, status=status.HTTP_200_OK)
        except BorrowRecord.DoesNotExist:
            return Response({'message': '此記錄不存在或已歸還。'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)