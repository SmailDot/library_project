# books/serializers.py

from rest_framework import serializers
from .models import Book, BorrowRecord
from django.utils import timezone

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class BorrowRecordSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = BorrowRecord
        fields = ['id', 'book_title', 'user_id', 'borrow_date', 'due_date', 'return_date', 'is_overdue']

    def get_is_overdue(self, obj):
        if obj.return_date is None:
            return obj.due_date < timezone.now()
        return False