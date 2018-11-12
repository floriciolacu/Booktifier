

from django.contrib import admin

from booktifier.models import Book, Author, BUser, Comment
# Register your models here.

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(BUser)
admin.site.register(Comment)
