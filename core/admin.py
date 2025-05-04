from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Profile, UserBook, Book


class UserBookInline(admin.TabularInline):
    model = UserBook


class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ["user", "bio"]
    inlines = [UserBookInline]


class ProfileInline(admin.StackedInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Book)
