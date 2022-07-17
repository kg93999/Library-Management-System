from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import BookIssuedSerializer, BooksSerializer, UserSerializer, UserChangePasswordSerializer #, SendPasswordResetEmailSerializer, UserPasswordResetSerializer
from .models import *
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(['GET'])
def api_overview(request):
    urls = {
        'register                         ' :   '      library/register/',
        'login                            ' :   '      library/login/',
        'user                             ' :   '      library/user/',
        'logout                           ' :   '      library/logout/',
        'change password                  ' :   '      library/changepassword/',
        'view and add book                ' :   '      library/librarian_book/',
        'update or delete book            ' :   '      library/librarian_book/<str:isbn_code>/',
        'view and add member              ' :   '      library/member/',
        'update or remove member          ' :   '      library/member/<str:username>/',
        'get available books              ' :   '      library/get_books/',
        'borrow or return book            ' :   '      library/borrow_or_issue_book/<str:isbn_code>/',
        'delete account by member         ' :   '      library/delete/'
    }
    return Response(urls, status = status.HTTP_200_OK)

class RegisterView(APIView):
    def post(self, request):
        user = MyUser.objects.filter(username = request.data["username"]).first()
        if user is not None:    # Means the user existed before, but he/she deleted his/her
            # account, and now is re-creating it again 
            user.is_active = True
            user.set_password(request.data["password"])
            user.save()
            return Response("User created", status = status.HTTP_201_CREATED)
        else:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = MyUser.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        if not user.is_active:
            # Means user has deleted his/her account previously
            raise AuthenticationFailed('User does not exist. Register a new account first')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect username or password!')
        payload = {
            'username': user.username,
            'is_admin': user.is_admin,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm = 'HS256') #.decode('utf-8')
        token_decode=jwt.decode(token,'secret',algorithms = ['HS256'])
        response = Response()
        response.set_cookie(key = 'jwt', value = token)   # You can do expires = datetime.utcnow() + timedelta(days = 2)
        response.data = {
            'jwt': token,
            'data':token_decode
        }
        return response

class UserView(APIView):    # To view user details
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token validity expired. Login again!!')
        user = MyUser.objects.filter(username = payload['username'])#.first()
        serializer = UserSerializer(user[0])
        # There are 3 ways of doing this-----  
        # user = MyUser.objects.filter(id=payload['id']).first()
        # user = MyUser.objects.get(id=payload['id'])
        # user = MyUser.objects.filter(id=payload['id']).first()  and then user[0]
        # filter() is returning a queryset of objects
        return Response(serializer.data, status = status.HTTP_202_ACCEPTED)

class LogoutView(APIView):
    def get(self, request):
        response = Response()
        token = request.COOKIES.get('jwt')
        if token is None:
            response.data = "User has already logged out"
        else:
            response.delete_cookie('jwt')
            response.data = "Logged out successfully"
        return response

class UserChangePasswordView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed('You are not logged in!')
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token validity expired. Login again!!')
        user = MyUser.objects.filter(username = payload['username'])
        serializer = UserChangePasswordSerializer(data = request.data, context = {'user':user[0]})
        serializer.is_valid(raise_exception = True)
        
        # Logout when password is changed
        response = Response()
        response.delete_cookie('jwt')
        response.data = "Password changed successfully and logged out"
        return response



# Only librarian is authorised to do
@api_view(['GET', 'POST'])
def view_and_add_book(request):   # Only librarian i.e user with is_admin = True, can add books
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('You are not logged in!')
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token validity expired. Login again!!')
    user = MyUser.objects.filter(username = payload['username']).first()
    if not user.is_admin:   # means not a librarian
        return Response("You are not authorised to add, update or delete any book", status = status.HTTP_401_UNAUTHORIZED)
    else:
        if request.method == 'GET':
            book = Books.objects.values()
            available_books = []
            for i in book:
                if i['available']:
                    available_books.append(i)
            return Response(available_books, status = status.HTTP_200_OK)

        if request.method == 'POST':
            book = Books.objects.filter(isbn_code = request.data['isbn_code']).first()
            if book is not None:   # means book was present before, deleted afterwards and then is added again
                book.available = True
                book.save()
                return Response("Book successfully added", status = status.HTTP_201_CREATED)
            
            # create new book, if not present before
            serializer = BooksSerializer(data = request.data)
            serializer.is_valid(raise_exception = True)
            serializer.save()
            return Response("Book successfully addeddd", status = status.HTTP_201_CREATED)

# Only librarian is authorised to do
@api_view(['PATCH', 'DELETE'])
def update_or_delete_book(request, isbn_code):   # Only librarian i.e user with is_admin = True, can add books
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('You are not logged in!')
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token validity expired. Login again!!')
    user = MyUser.objects.filter(username = payload['username']).first()
    if not user.is_admin:   # means not a librarian
        return Response("You are not authorised to update or delete any book", status = status.HTTP_401_UNAUTHORIZED)
    else:
        if request.method == 'PATCH':
            book = Books.objects.get(isbn_code = isbn_code)
            serializer = BooksSerializer(book, data = request.data, partial = True)
            serializer.is_valid(raise_exception = True)
            serializer.save()
            return Response("Book successfully updated", status = status.HTTP_200_OK)

        elif request.method == 'DELETE':
            book = Books.objects.filter(isbn_code = isbn_code).first()
            if book is not None:
                book.available = False
                book.save()
                return Response("Book successfully deleted", status = status.HTTP_200_OK)

            return Response("Book is not present in database", status = status.HTTP_400_BAD_REQUEST)

# Only librarian is authorised to do
@api_view(['GET', 'POST'])
def view_add_member(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('You are not logged in!')
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token validity expired. Login again!!')
    user = MyUser.objects.filter(username = payload['username']).first()
    if not user.is_admin:   # means not a librarian
        return Response("You are not authorised to add, update, view or remove any member", status = status.HTTP_401_UNAUTHORIZED)
    else:
        if request.method == 'GET':
            members = MyUser.objects.values()    # cannot view other librarians
            if members is None:
                return Response("No members in database", status = status.HTTP_200_OK)
            a = []
            for i in members:
                if i['is_active']:
                    if i['is_admin'] == False:
                        del i['last_login']
                        del i['is_superuser']
                        del i['first_name']
                        del i['last_name']
                        del i['email']
                        del i['date_joined']
                        a.append(i)
            return Response(a, status = status.HTTP_200_OK)

        elif request.method == 'POST':
            member = MyUser.objects.filter(username = request.data['username']).first()
            if member is not None:
                member.is_active = True
                member.save()
                return Response("member has become active again", status = status.HTTP_201_CREATED)
            serializer = UserSerializer(data = request.data)
            serializer.is_valid(raise_exception = True)
            serializer.save()
            return Response("Member successfully added", status = status.HTTP_201_CREATED)

# Only librarian is authorised to do
@api_view(['PATCH', 'DELETE'])
def update_remove_member(request, username):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('You are not logged in!')
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token validity expired. Login again!!')
    user = MyUser.objects.filter(username = payload['username']).first()
    if not user.is_admin:   # means not a librarian
        return Response("You are not authorised to add, update, view or remove any member", status = status.HTTP_401_UNAUTHORIZED)
    else:
        if request.method == 'PATCH':
            member = MyUser.objects.filter(username = username).first()
            if member is None:
                return Response("No such member exist", status = status.HTTP_400_BAD_REQUEST)
            else:
                serializer = UserSerializer(member, data = request.data, partial = True)
                serializer.is_valid(raise_exception = True)
                serializer.save()
                return Response("Member successfully updated", status = status.HTTP_200_OK)

        elif request.method == 'DELETE':
            member = MyUser.objects.filter(username = username).first()
            if member is not None:
                member.is_active = False
                member.save()
                return Response("Member successfully deleted", status = status.HTTP_200_OK)

            return Response("Member is not present in database", status = status.HTTP_400_BAD_REQUEST)


# For member
@api_view(['GET'])     # Member can view books
def get_member_books(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('You are not logged in!')
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token validity expired. Login again!!')
    user = MyUser.objects.filter(username = payload['username']).first()
    if user.is_admin:   # means not a member
        return Response("Please log in as member to view books", status = status.HTTP_401_UNAUTHORIZED)
    else:
        book = Books.objects.values()
        available_books = []
        for i in book:
            if i['available']:
                available_books.append(i)
        return Response(available_books, status = status.HTTP_200_OK)


# For member
# borrow or return books
@api_view(['PATCH'])     # Member can borrow or return books
def member_books(request, isbn_code):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('You are not logged in!')
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token validity expired. Login again!!')
    user = MyUser.objects.filter(username = payload['username']).first()
    if user.is_admin:   # means not a member
        return Response("Please log in as member to borrow/return books", status = status.HTTP_401_UNAUTHORIZED)
    else:
        # NOTE: each api hit will change borrow status of only one book 
        # issue = BookIssued.objects.filter(isbn_code = isbn_code).first()
        try:
            issue = BookIssued.objects.get(isbn_code = isbn_code)
            if issue.to == user.username:
                # Means if book to be borrowed or already borrowed by current logged in user
                if issue.is_borrowed:
                    # Means if the book is already borrowed by the logged in member
                    # Then return the book i.e change the status of is_borrowed to False
                    issue.is_borrowed = False
                    issue.save()
                    return Response("Book returned successfully", status = status.HTTP_200_OK)
                else:
                    # Otherwise issue this book
                    issue.is_borrowed = True
                    issue.save()
                    return Response("Book issued successfully", status = status.HTTP_200_OK)
            else:
                # Book is issued to some other member
                if issue.is_borrowed:
                    return Response("The book is issued to some other member, hence you cannot borrow it now", status = status.HTTP_403_FORBIDDEN)
                else:
                    # The book is available for issue
                    issue.to = user.username
                    issue.is_borrowed = True
                    issue.save()
                    return Response("Book issued successfully", status = status.HTTP_200_OK)
            
        except:
            # Means the book has never been issued to any member is the past or present
            # First check if book is available in library
            b = Books.objects.filter(isbn_code = isbn_code).filter()
            if b == None:
                return Response("Book is not available. Choose other book", status = status.HTTP_400_BAD_REQUEST)
            new_issue = BookIssued.objects.create(to = user.username, isbn_code = isbn_code, is_borrowed = True)
            new_issue.save()
            return Response("Book issued successfully", status = status.HTTP_200_OK)

@api_view(['DELETE'])   # 'Get' method because i am not deleting member from database, I am only making the member non-active 
def delete_account_member(request):     # Soft delete the account
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('You are not logged in!')
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token validity expired. Login again!!')
    user = MyUser.objects.filter(username = payload['username']).first()
    if user is None:
        return Response("Please login first!!!", status = status.HTTP_400_BAD_REQUEST)
    if user.is_admin:   # means not a member
        return Response("Please log in as member to delete your account", status = status.HTTP_403_FORBIDDEN)
    else:
        user.is_active = False
        user.save()
        return Response("Account successfully deleted!!", status = status.HTTP_200_OK)