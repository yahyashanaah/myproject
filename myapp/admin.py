from django import forms
from django.contrib import admin
from django.shortcuts import render
from .models import Post

admin.site.register(Post)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']


def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})