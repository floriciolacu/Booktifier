from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from booktifier.models import Book, Author, BUser, Comment
from booktifier.forms import BookForm, AuthorForm, UserProfileForm, UserForm, BUserForm
from booktifier.forms import LoginForm, SignUpForm, CommentForm, UploadFileForm
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
import sys
import os
import django
path = os.path.realpath(__file__)
path = path.split('/')
path.pop()
path.pop()
path = '/'.join(path)
sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE']='awp.settings'
django.setup()
from booktifier.models import Book, Author
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import numpy as np
import json
import difflib
from sklearn.svm import SVC
import tempfile
import cv2

# Create your views here
class FrontPageView(ListView):
    template_name = 'home.html'
    model = Book
    context_object_name = 'books'

class BooksListView(ListView):
    template_name = 'booksList.html'
    model = Book
    context_object_name = 'books'

class BookDetailView(LoginRequiredMixin, DetailView):
    template_name = 'book.html'
    model = Book
    context_object_name = 'book'

class AuthorDetailView(DetailView):
    template_name = 'author.html'
    model = Author
    context_object_name = 'author'

class AuthorCreateView(CreateView):
    template_name = 'addAuthor.html'
    form_class = AuthorForm
    model = Author

    def get_success_url(self, *args, **kwargs):
        return reverse('author_detail', kwargs={'pk': self.object.pk})

class BookCreateView(CreateView):
    template_name = 'addBook.html'
    form_class = BookForm
    model = Book

    def get_success_url(self, *args, **kwargs):
        return reverse('book_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(BookCreateView, self).get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        return context

class BookUpdateView(UpdateView):
    template_name = 'editBook.html'
    form_class = BookForm
    model = Book

    def get_success_url(self, *args, **kwargs):
        return reverse('book_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(BookUpdateView, self).get_context_data(**kwargs)
        authors = Author.objects.all()
        for author in authors:
            author.books_pk = [pk for pk in author.Books.values_list('pk', flat=True)]
        context['authors'] = authors
        context['book_pk'] = self.object.pk
        return context

class BookDeleteView(DeleteView):
    template_name = 'deleteBook.html'
    model = Book

    def get_success_url(self, *args, **kwargs):
        return reverse('bookslist')

class SearchPageListView(ListView):
    template_name = 'search.html'
    model = Book
    context_object_name = 'items'
    def get_queryset(self):
        searchInput = self.kwargs['input']
        queryset = Book.objects.filter(title__contains=searchInput).all() | Book.objects.filter(authors__last_name__contains=searchInput).all()
        return queryset

class SearchPageListView1(ListView):
    template_name = 'search1.html'
    model = Book
    context_object_name = 'items'
    def get_queryset(self):
        queryset = Book.objects.all()
        return queryset

def login_view(request):
    context = {}
    if request.method == 'GET':
        form = LoginForm()
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user:
                login(request=request,
                      user=user)
                return redirect('home')
            else:
                context['error_message'] = 'Wrong username or password!'
    context['form'] = form
    return render(request, 'login.html', context)

def logout_view(request):
    if request.method == 'GET':
        logout(request)
        return redirect('login')

def make_dictionary():
    book_list = Book.objects.all()
    author_list = Author.objects.all()

    number_words_books = 0
    number_words_authors = 0

    words_books = []
    words_authors = []

    dictionary = {}

    for book in book_list:
        for word in book.title.split():
            number_words_books = number_words_books + 1

    for author in author_list:
        number_words_authors = number_words_authors + 2

    for book in book_list:
        for word in book.title.split():
            words_books.append(word)

    for author in author_list:
        words_authors.append(author.first_name)
        words_authors.append(author.last_name)


    number_words = number_words_books + number_words_authors

    for key in range(0, number_words_books):
        dictionary[key] = words_books[key]

    for key in range(number_words_books, number_words):
        dictionary[key] = words_authors[key - number_words_books]

    return dictionary

dictionary = make_dictionary()

def get_prediction(file, dict):
    training_data = np.load('booktifier/TrainingData.npy')
    labels = np.load('booktifier/Labels.npy')
    clf = SVC()
    clf.fit(training_data, labels)
    val = np.zeros(len(dict), dtype=int)
    img = cv2.imread('booktifier/media/' + file, cv2.IMREAD_COLOR)
    img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=12)
    img = cv2.erode(img, kernel, iterations=12)
    cv2.imwrite("temp.jpg", img)
    text = pytesseract.image_to_string(Image.open('temp.jpg'), lang = 'ron', config = '--psm 1 --user-words /home/tgr2/words.txt')
    for word in text.split():
        for key in dict:
            if len(word) <= 4:
                if word.lower() == dict[key].lower():
                    val[key] = 1
            else:
                if difflib.SequenceMatcher(None, word.lower(), dict[key].lower()).ratio() > 0.70:
                    val[key] = 1

    prediction = clf.predict([val])
    return prediction

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            image_name = request.FILES['file']
            file_obj = image_name.read()
            media_path = settings.MEDIA_ROOT
            file = os.path.join(media_path, image_name.name)
            with open(file, 'wb+') as f:
                f.write(file_obj)
            request.session['image_name'] = image_name.name
            return redirect('prediction', bname = image_name.name)
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

class FindPageListView(ListView):
    template_name = 'prediction.html'
    model = Book
    context_object_name = 'items'

    def get_queryset(self):
        image_predict = self.kwargs['bname']
        #image_to_predict = self.request.session.get('image_name')
        #image_to_predict = self.request.GET['image_name']
        #print(image_predict)
        predicted_book_name = get_prediction(image_predict, dictionary)[0]
        queryset = Book.objects.filter(title = predicted_book_name).all()
        return queryset

class AddedFavoriteView(View):
     def get(self, request, *args, **kwargs):
        obj = Book.objects.get(pk=kwargs['pk'])
        if obj not in request.user.buser.favourites.all():
            request.user.buser.favourites.add(obj)
            request.user.buser.save()
            return render( request, 'favorite.html', {'response': 'The book was added to your favorites list!'})
        else:
            request.user.buser.favourites.remove(obj)
            request.user.buser.save()
            return render( request, 'favorite.html', {'response': 'The book was removed from your favorites list!'})

class AddedReadView(View):
     def get(self, request, *args, **kwargs):
        obj = Book.objects.get(pk=kwargs['pk'])
        if obj not in request.user.buser.read.all():
            request.user.buser.read.add(obj)
            request.user.buser.save()
            return render( request, 'read.html', {'response': 'The book was added to your read books list!'})
        else:
            request.user.buser.read.remove(obj)
            request.user.buser.save()
            return render( request, 'read.html', {'response': 'The book was removed from your read books list!'})

class AddedScoreView(View):
     def get(self, request, *args, **kwargs):
        obj = Book.objects.get(pk=kwargs['pk'])
        votedScore = float(kwargs['value'])
        if request.user not in obj.votes.all():
            nr = int(obj.votes.count())
            obj.score = str(format((float(obj.score) * nr + votedScore) / (nr + 1), '.2f'))
            obj.votes.add(request.user)
            obj.save()
            return render( request, 'voted.html', {'response': 'Thank you for your vote!'})
        else:
            return render( request, 'voted.html', {'response': 'You have already voted for this book!'})


class UserProfileDetailView(DetailView):
    template_name = 'profile.html'
    model = BUser
    context_object_name = 'buser'

@login_required
def update_profile(request, pk):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        buser_form = BUserForm(request.POST, instance=request.user.buser)
        if user_form.is_valid() and buser_form.is_valid():
            user_form.save()
            buser = BUser.objects.get(pk=pk)
            buser_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            #return render(request, 'profile.html', {'pk': pk})
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        user_form = UserForm(instance=request.user)
        buser_form = BUserForm(instance=request.user.buser)
    return render(request, 'editProfile.html', {
        'user_form': user_form,
        'buser_form': buser_form
    })

class UserCreateView(CreateView):
    template_name = "signup.html"
    form_class = SignUpForm
    model = BUser

    def get_success_url(self, *args, **kwargs):
        return reverse('login')

    def signup(request):
        if request.method == 'POST':
            form = UserCreateForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password')
                user=authenticate(username=username,password=password)
                return redirect('login')
        else:
            form = UserCreateForm()
        return render(request, 'signup.html', {'form': form})

def add_comment_to_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.book = book
            comment.save()
            return redirect('book_detail', pk=book.pk)
    else:
        form = CommentForm()
    return render(request, 'addComment.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.refresh_from_db()  # load the profile instance created by the signal
            user.buser.first_name = form.cleaned_data.get('first_name')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            return redirect('login')           
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
