from django import forms
from ckeditor.widgets import CKEditorWidget


class PostCreateForm(forms.Form):
    title = forms.CharField(label='Заголовок', required=True, max_length=100)
    image = forms.ImageField(required=False)
    content = forms.CharField(label='Содержание', required=True, widget=CKEditorWidget)
