from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import Comment,Post
# Create your views here.

def blog(request):
    try:
        posts = Post.objects.filter(user_id=request.user.id).order_by("-id")
        print(posts)
    except Exception as e:
        posts = []

    try:
        top_posts = Post.objects.all().order_by("-likes")
    except Exception as e:
        top_posts = []

    try:
        recent_posts = Post.objects.all().order_by("-id")
    except Exception as e:
        recent_posts = []
    user1=request.user.is_authenticated

    return render(request, "blog.html", {
        'posts': posts,
        'top_posts': top_posts,
        'recent_posts': recent_posts,
        'user': request.user,
        'media_url': settings.MEDIA_URL,
        'user1':user1

    })

    
def increaselikes(request,id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        post.likes += 1
        post.save() 
    return redirect("index")


def post(request,id):
    post = Post.objects.get(id=id)
    
    return render(request,"post-details.html",{
        "user":request.user,
        'post':Post.objects.get(id=id),
        'recent_posts':Post.objects.all().order_by("-id"),
        'media_url':settings.MEDIA_URL,
        'comments':Comment.objects.filter(post_id = post.id),
        'total_comments': len(Comment.objects.filter(post_id = post.id))
    })
    
def savecomment(request,id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        content = request.POST['message']
        Comment(post_id = post.id,user_id = request.user.id, content = content).save()
        return redirect("index")
    
def deletecomment(request,id):
    comment = Comment.objects.get(id=id)
    postid = comment.post.id
    comment.delete()
    return post(request,postid)
    
