from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserBookForm, EditUserBookForm
from .models import Book, UserBook, Profile


def dashboard(request):
    return render(request, "base.html")


def profile_list(request):
    profiles = Profile.objects.exclude(user=request.user)
    return render(request, "core/profile_list.html", {"profiles": profiles})


def profile(request, pk):
    profile = Profile.objects.get(pk=pk)
    user_books = UserBook.objects.filter(user=profile)
    return render(request, "core/profile.html", {"profile": profile, "user_books": user_books})

def add_userbook(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = UserBookForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            status = form.cleaned_data['status']

            # Case-insensitive book lookup or creation
            book = Book.objects.filter(title__iexact=title, author__iexact=author).first()
            if not book:
                book = Book.objects.create(title=title, author=author)

            # Prevent duplicate UserBook
            if not UserBook.objects.filter(user=profile, book=book).exists():
                UserBook.objects.create(user=profile, book=book, status=status)
                return redirect('my_books')  # redirect after success
            else:
                form.add_error(None, "You already added this book.")
    else:
        form = UserBookForm()

    return render(request, 'core/add_userbook.html', {'form': form})


def my_books(request):
    profile = request.user.profile
    user_books = UserBook.objects.filter(user=profile)
    return render(request, 'core/my_books.html', {
        'profile': profile,
        'user_books': user_books
    })

def edit_userbook(request, pk):
    userbook = UserBook.objects.get(pk=pk)

    if request.method == 'POST':
        form = EditUserBookForm(request.POST, instance=userbook)
        if form.is_valid():
            form.save()
            return redirect('core:profile', pk=request.user.profile.id)
    else:
        form = EditUserBookForm(instance=userbook)

    return render(request, 'core/edit_userbook.html', {'form': form})



def delete_userbook(request, pk):
    userbook = get_object_or_404(UserBook, pk=pk, user=request.user.profile)

    if request.method == 'POST':
        userbook.delete()
        return redirect('core:profile', pk=request.user.profile.pk)

    return render(request, 'core/delete_userbook.html', {'userbook': userbook})
