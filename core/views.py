from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserBookForm, EditUserBookForm, NoteForm
from .models import Book, UserBook, Profile


def dashboard(request):
    form = NoteForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect("core:dashboard")
    return render(request, "core/dashboard.html", {"form": form})


def profile_list(request):
    profiles = Profile.objects.exclude(user=request.user)
    return render(request, "core/profile_list.html", {"profiles": profiles})


def profile(request, pk):
    if not hasattr(request.user, 'profile'):
        missing_profile = Profile(user=request.user)
        missing_profile.save()

    profile = Profile.objects.get(pk=pk)

    if request.method == "POST":
        current_user_profile = request.user.profile
        data = request.POST
        action = data.get("follow")
        if action == "follow":
            current_user_profile.follows.add(profile)
        elif action == "unfollow":
            current_user_profile.follows.remove(profile)
        current_user_profile.save()

    num_books = UserBook.objects.filter(user=profile).count()
    num_to_read = UserBook.objects.filter(user=profile, status="to_read").count()
    num_reading = UserBook.objects.filter(user=profile, status="reading").count()
    num_finished = UserBook.objects.filter(user=profile, status="finished").count()

    return render(request, "core/profile.html", {"profile": profile,
                                                 "num_books": num_books,
                                                 "num_to_read": num_to_read,
                                                 "num_reading": num_reading,
                                                 "num_finished": num_finished,
                                                 })

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
                return redirect('core:my_books')  # redirect after success
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


def filtered_books(request, status):
    profile = request.user.profile
    user_books = UserBook.objects.filter(user=profile, status=status)

    return render(request, "core/filtered_books.html", {
        "status": status,
        "user_books": user_books,
        "profile": profile,
    })