from django.contrib import admin

# Register your models here.
from .models import Author, Genre, Book, BookAuthor, BookInstance, Language

# consider adding save_as to more easily add instance that have similar values
# you could do this for any or all of the below, e.g.
# admin.site.register(Book, save_as=True)
# except mayeb not bookinstance tho

admin.site.register(Genre)
admin.site.register(Language)

class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookAuthorInline]


admin.site.register(Author, AuthorAdmin)

class BookInstanceInline(admin.TabularInline):
    model = BookInstance


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_genre')
    inlines = [BookInstanceInline, BookAuthorInline]


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back', 'id')


@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ('book', 'author', 'author_order')