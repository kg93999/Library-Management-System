from django.contrib import admin
from .models import MyUser, Books, BookIssued

# Register your models here.
@admin.register(MyUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'password', 'is_admin', 'create_date', 'is_active']

@admin.register(Books)
class BooksAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'isbn_code']

@admin.register(BookIssued)
class BookIssuedAdmin(admin.ModelAdmin):
    list_display = ['to', 'isbn_code', 'issue_date', 'expiry_date', 'is_borrowed']