from django.contrib import admin

# Register your models here.
from .models import Author, Genre, Book, BookInstance, Language

# consider adding save_as to more easily add instance that have similar values
# you could do this for any or all of the below, e.g.
# admin.site.register(Book, save_as=True)
# except mayeb not bookinstance tho

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(BookInstance)
admin.site.register(Language)