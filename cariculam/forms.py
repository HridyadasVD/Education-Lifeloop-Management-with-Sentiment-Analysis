from django import forms
from .models import *




class Lessonform(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('lesson_id', 'name', 'position', 'difficulty', 'video', 'ppt', 'notes')


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Comment
        fields = ('body',)

        labels = {"body": "Comment:"}

        widgets = {
            'body': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'cols': 70, 'placeholder': "Enter Your Comment"}),
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ('reply_body',)

        widgets = {
            'reply_body': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'cols': 10}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)   