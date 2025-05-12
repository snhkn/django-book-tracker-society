from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserBookForm, EditUserBookForm, NoteForm
from .models import Book, UserBook, Profile
from django.contrib.auth.models import User
from django.utils.timezone import localtime
from calendar import monthrange
from datetime import date
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from itertools import chain
from operator import attrgetter
from .models import Note, Feed

@login_required
def dashboard(request):
    form = NoteForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect("core:dashboard")

    user_profile = request.user.profile
    follows = user_profile.follows.all().order_by("-id")


    activities = []

    for profile in follows:
        for feed in profile.user.feeds.all():
            feed.type = "feed"
            feed.user = profile.user  # manually attach for template
            activities.append(feed)
        for note in profile.user.notes.all():
            note.type = "note"
            note.user = profile.user
            activities.append(note)

    activities.sort(key=lambda x: x.timestamp, reverse=True)

    paginator = Paginator(activities, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/dashboard.html", {
        "form": form,
        "page_obj": page_obj
    })


@login_required
def profile_list(request):
    profiles = Profile.objects.exclude(user=request.user)
    paginator = Paginator(profiles, 10)  # Show 10 profiles per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "core/profile_list.html", {"profiles": profiles, "page_obj": page_obj})

@login_required
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

    WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    today = date.today()
    _, days_in_month = monthrange(today.year, today.month)

    # Gather note + feed timestamps
    note_dates = profile.user.notes.values_list('timestamp', flat=True)

    # Normalize to date (remove time)
    activity_days = set(
        localtime(nd).date() for nd in note_dates
    )

    return render(request, "core/profile.html", {"profile": profile,
                                                 "num_books": num_books,
                                                 "num_to_read": num_to_read,
                                                 "num_reading": num_reading,
                                                 "num_finished": num_finished,
                                                 "weekdays": WEEKDAYS,
                                                 "month_days": [date(today.year, today.month, day) for day in
                                                                range(1, days_in_month + 1)],
                                                 "activity_days": activity_days,
                                                 })
@login_required
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

                # ✅ Create Feed object
                Feed.objects.create(user=request.user, book=book, action='added')

                return redirect('core:my_books')  # redirect after success
            else:
                form.add_error(None, "You already added this book.")
    else:
        form = UserBookForm()

    return render(request, 'core/add_userbook.html', {'form': form})

@login_required
def my_books(request):
    profile = request.user.profile
    user_books = UserBook.objects.filter(user=profile)

    paginator = Paginator(user_books, 5)  # Show 5 books per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/my_books.html', {
        'profile': profile,
        'user_books': user_books,
        'page_obj': page_obj
    })

@login_required
def edit_userbook(request, pk):

    userbook = UserBook.objects.get(pk=pk)

    if request.method == 'POST':
        form = EditUserBookForm(request.POST, instance=userbook)
        if form.is_valid():
            old_status = userbook.status  # before saving
            updated_userbook = form.save(commit=False)

            if old_status != updated_userbook.status:
                # Customize action based on new status
                Feed.objects.create(
                    user=request.user,
                    book=updated_userbook.book,
                    action=f'updated status to {updated_userbook.status}'
                )

            updated_userbook.save()
            return redirect('core:profile', pk=request.user.profile.id)
    else:
        form = EditUserBookForm(instance=userbook)

    return render(request, 'core/edit_userbook.html', {'form': form})

@login_required
def delete_userbook(request, pk):
    userbook = get_object_or_404(UserBook, pk=pk, user=request.user.profile)

    if request.method == 'POST':
        userbook.delete()
        return redirect('core:profile', pk=request.user.profile.pk)

    return render(request, 'core/delete_userbook.html', {'userbook': userbook})

@login_required
def filtered_books(request, status):
    profile = request.user.profile
    user_books = UserBook.objects.filter(user=profile, status=status)

    return render(request, "core/filtered_books.html", {
        "status": status,
        "user_books": user_books,
        "profile": profile,
    })

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None  # Removes help text


def sign_up(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("core:dashboard"))
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/sign_up.html", {"form": form})


from django.db.models import Q

from django.db.models import Q

@login_required
def search_books(request):
    query = request.GET.get("q", "")
    results = []

    if query:
        results = UserBook.objects.filter(
            user=request.user.profile  # use Profile instance
        ).filter(
            Q(book__title__icontains=query) | Q(book__author__icontains=query)
        ).select_related("book")

    return render(request, "core/search_results.html", {
        "results": results,
        "query": query,
    })


