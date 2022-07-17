from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('change-password/', UserChangePasswordView.as_view()),
    path('librarian/book/', view_and_add_book),
    path('librarian/book/<str:isbn_code>/', update_or_delete_book),
    path('member/', view_add_member), 
    path('member/<str:username>/', update_remove_member),
    path('member/books/', get_member_books),
    path('member/books/<str:isbn_code>/', member_books),
    path('delete/', delete_account_member)
]