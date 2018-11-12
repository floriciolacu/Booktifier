from django import forms
from django.contrib.auth.forms import UserCreationForm
from booktifier.models import Book, Comment
from booktifier.models import Author, BUser
from django.contrib.auth.models import User
from django.core.files.images import get_image_dimensions
from django.conf import settings
from django.template import RequestContext

class BookForm(forms.ModelForm):
    appearance_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')
    #cover = forms.ImageField()
    class Meta:
        model = Book
        fields = ('title', 'appearance_date', 'genre', 'authors', 'description', 'publishing_house', 'cover')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('title', 'content')

class UploadFileForm(forms.Form):
    file = forms.ImageField()

class AuthorForm(forms.ModelForm):
    birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')
    class Meta:
        model = Author
        fields = ('first_name', 'last_name', 'birth_date', 'birth_place', 'description', 'website', 'sign', 'picture')

class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = BUser
        fields = "__all__"

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class BUserForm(forms.ModelForm):
    class Meta:
        model = BUser
        fields = ('birth_date', )

class SignUpForm(UserCreationForm):
    birth_date = forms.DateField(help_text='Required. Format: YYYY-MM-DD')
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'birth_date', )
        help_texts = {
            'last_name': 'Required.',
            'first_name': 'Required'
        }

    def custom_save(self, datas):
        user = User.objects.create_user(datas['username'],
                                     first_name=datas['first_name'],
                                     last_name=datas['last_name'],
                                     email=datas['email'],
                                     password=datas['password1'],
                                     )
        user.buser.birth_date = datas['birth_date']
        user.save()
        return user
