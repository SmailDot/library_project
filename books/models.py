# books/models.py

from django.db import models
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="書名")
    author = models.CharField(max_length=100, verbose_name="作者")
    is_available = models.BooleanField(default=True, verbose_name="是否可借閱")

    def __str__(self):
        return self.title

class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="書籍")
    user_id = models.IntegerField(verbose_name="使用者ID")
    borrow_date = models.DateTimeField(default=timezone.now, verbose_name="借閱日期")
    due_date = models.DateTimeField(verbose_name="應歸還日期")
    return_date = models.DateTimeField(null=True, blank=True, verbose_name="實際歸還日期")
    
    def __str__(self):
        return f"{self.user_id} 借閱 {self.book.title}"

    class Meta:
        verbose_name = "借閱紀錄"
        verbose_name_plural = "借閱紀錄"