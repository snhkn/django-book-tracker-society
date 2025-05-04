from django import forms
from .models import UserBook

class UserBookForm(forms.Form):
    title = forms.CharField(max_length=255)
    author = forms.CharField(max_length=255)
    status = forms.ChoiceField(choices=UserBook.STATUS_CHOICES)

    def clean_title(self):
        return self.cleaned_data['title'].strip().title()

    def clean_author(self):
        return self.cleaned_data['author'].strip().title()

class EditUserBookForm(forms.ModelForm):
    class Meta:
        model = UserBook
        fields = ['status']