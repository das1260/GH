from . import views
from django.urls import path

urlpatterns = [
    path("blog",views.blog,name="blog"),
    path("increaselikes/<int:id>",views.increaselikes,name='increaselikes'),
    path("post/<int:id>",views.post,name="post"),
    path("post/comment/<int:id>",views.savecomment,name="savecomment"),
    path("post/comment/delete/<int:id>",views.deletecomment,name="deletecomment"),

]
